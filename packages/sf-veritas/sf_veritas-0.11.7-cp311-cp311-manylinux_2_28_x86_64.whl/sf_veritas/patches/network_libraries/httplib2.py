import os
import time
from typing import List, Optional

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

from ...constants import SAILFISH_TRACING_HEADER, PARENT_SESSION_ID_HEADER
from ...env_vars import SF_DEBUG
from ...thread_local import trace_id_ctx
from .utils import (
    init_fast_header_check,
    inject_headers_ultrafast,
    record_network_request,
    is_ssl_socket_active,
    has_sailfish_header,
)

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False


def _tee_preload_active() -> bool:
    """Detect if LD_PRELOAD tee is active (same logic as http_client.py)."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def patch_httplib2(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    Monkey-patch httplib2.Http.request so that:
    1. We skip header injection for configured domains.
    2. We inject SAILFISH_TRACING_HEADER + FUNCSPAN_OVERRIDE_HEADER (fast: <20ns).
    3. We call NetworkRequestTransmitter().do_send via record_network_request() UNLESS LD_PRELOAD active.
    4. All HTTP methods (GET, POST, etc.) continue to work as before.

    When LD_PRELOAD is active: ULTRA-FAST path with <10ns overhead (header injection only).
    When LD_PRELOAD is NOT active: Full capture path with body/header recording.

    CRITICAL: If http.client is already patched, httplib2 only does header injection
    to avoid double-capture (httplib2 uses http.client.HTTPConnection underneath).
    """
    TRACE_HEADER_LOWER = SAILFISH_TRACING_HEADER.lower()
    PARENT_HEADER_LOWER = PARENT_SESSION_ID_HEADER.lower()

    def _log_headers(stage: str, hdrs: Optional[dict]) -> None:
        if not (SF_DEBUG and hdrs):
            return
        try:
            snapshot = {}
            for key, value in hdrs.items():
                if not isinstance(key, str):
                    continue
                key_lower = key.lower()
                if key_lower in (TRACE_HEADER_LOWER, PARENT_HEADER_LOWER):
                    snapshot[key] = value
            print(f"[httplib2.patch] {stage} headers={snapshot}", log=False)
        except Exception as exc:  # pragma: no cover - debug logging only
            print(f"[httplib2.patch] {stage} header log failed: {exc}", log=False)

    try:
        import httplib2
    except ImportError:
        return

    original_conn_request = getattr(httplib2.Http, "_conn_request", None)
    if (
        original_conn_request
        and not getattr(original_conn_request, "_sf_debug_logged", False)
        and SF_DEBUG
    ):
        def _logged_conn_request(self, conn, request_uri, method, body, headers):
            _log_headers(
                f"conn_request:{method}:{request_uri}",
                headers or {},
            )
            return original_conn_request(self, conn, request_uri, method, body, headers)

        _logged_conn_request._sf_debug_logged = True  # type: ignore[attr-defined]
        httplib2.Http._conn_request = _logged_conn_request

    skip = domains_to_not_propagate_headers_to or []
    preload_active = _tee_preload_active()

    # CRITICAL: Check if http.client is already patched (handles capture for us)
    # httplib2 uses http.client.HTTPConnection underneath, so if http_client patch
    # is active, we should ONLY do header injection to avoid double-capture
    http_client_patched = False
    try:
        import http.client as _hc
        # Check if request method has been wrapped (indicates http_client patch is active)
        http_client_patched = hasattr(_hc.HTTPConnection.request, '__wrapped__') or \
                             getattr(_hc.HTTPConnection.request, '__name__', '') == 'patched_request'
    except Exception:
        pass

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active or http_client_patched:
        init_fast_header_check(skip)

    # Store original for both fast and slow paths
    original_request = httplib2.Http.request

    # Use fast path (header injection only) if LD_PRELOAD is active OR http.client is already patched
    use_fast_path = preload_active or http_client_patched

    if use_fast_path:
        # ========== ULTRA-FAST PATH: Header injection only ==========
        # Used when: LD_PRELOAD is active OR http.client is already patched
        # This avoids double-capture since http.client handles it for us
        if HAS_WRAPT:
            # FASTEST: Use wrapt directly (OTEL-style for minimal overhead)
            def instrumented_request(wrapped, instance, args, kwargs):
                """Ultra-fast header injection using inject_headers_ultrafast() via wrapt."""
                # args = (uri, method, ...), kwargs = {body, headers, ...}
                uri = args[0] if len(args) > 0 else kwargs.get("uri", "")

                # Ensure headers dict exists
                headers = kwargs.get("headers")
                if not headers:
                    headers = {}
                elif not isinstance(headers, dict):
                    headers = dict(headers)

                if SF_DEBUG:
                    _log_headers("pre-inject", headers)

                # Check if headers are already injected (avoid double-injection with http.client)
                # Fast O(1) check for common cases, fallback to O(n) for rare mixed-case variants
                if not has_sailfish_header(headers):
                    # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                    inject_headers_ultrafast(headers, uri, skip)
                    if SF_DEBUG:
                        _log_headers("post-inject", headers)
                elif SF_DEBUG:
                    dup_snapshot = {
                        k: headers[k]
                        for k in headers
                        if isinstance(k, str) and k.lower() == TRACE_HEADER_LOWER
                    }
                    print(f"[httplib2.patch] Skip inject (wrapt) - existing headers={dup_snapshot}", log=False)

                kwargs["headers"] = headers

                # Immediately call original and return - NO timing, NO capture!
                return wrapped(*args, **kwargs)

            wrapt.wrap_function_wrapper(
                "httplib2", "Http.request", instrumented_request
            )
        else:
            # Fallback: Direct patching if wrapt not available
            def patched_request(
                self, uri, method="GET", body=None, headers=None, **kwargs
            ):
                # Ensure headers dict exists
                if not headers:
                    headers = {}
                elif not isinstance(headers, dict):
                    headers = dict(headers)

                if SF_DEBUG:
                    _log_headers("pre-inject", headers)

                # Check if headers are already injected (avoid double-injection with http.client)
                # Fast O(1) check for common cases, fallback to O(n) for rare mixed-case variants
                if not has_sailfish_header(headers):
                    # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                    inject_headers_ultrafast(headers, uri, skip)
                    if SF_DEBUG:
                        _log_headers("post-inject", headers)
                elif SF_DEBUG:
                    dup_snapshot = {
                        k: headers[k]
                        for k in headers
                        if isinstance(k, str) and k.lower() == TRACE_HEADER_LOWER
                    }
                    print(f"[httplib2.patch] Skip inject (fallback) - existing headers={dup_snapshot}", log=False)

                # Immediately call original and return - NO timing, NO capture!
                return original_request(
                    self, uri, method, body=body, headers=headers, **kwargs
                )

            httplib2.Http.request = patched_request

    else:
        # ========== FULL CAPTURE PATH: When neither LD_PRELOAD nor http.client patch is active ==========
        # Only used when httplib2 needs to handle capture itself (rare case)
        def patched_request(self, uri, method="GET", body=None, headers=None, **kwargs):
            start_ts = int(time.time() * 1_000)

            # Ensure headers dict exists
            if not headers:
                headers = {}
            elif not isinstance(headers, dict):
                headers = dict(headers)

            if SF_DEBUG:
                _log_headers("pre-inject-full", headers)

            # Check if headers are already injected (avoid double-injection with http.client)
            # Fast O(1) check for common cases, fallback to O(n) for rare mixed-case variants
            if not has_sailfish_header(headers):
                # ULTRA-FAST: inject_headers_ultrafast does domain filtering + header injection (~100ns)
                inject_headers_ultrafast(headers, uri, skip)
                if SF_DEBUG:
                    _log_headers("post-inject-full", headers)
            elif SF_DEBUG:
                dup_snapshot = {
                    k: headers[k]
                    for k in headers
                    if isinstance(k, str) and k.lower() == TRACE_HEADER_LOWER
                }
                print(f"[httplib2.patch] Skip inject (full path) - existing headers={dup_snapshot}", log=False)

            # Skip capture for HTTPS when ssl_socket.py is active (avoids double-capture)
            # ssl_socket.py captures ALL SSL traffic at socket layer when enabled
            is_https = uri.startswith("https://")
            if is_https and is_ssl_socket_active():
                # ssl_socket.py will handle capture, just make the request
                return original_request(self, uri, method, body=body, headers=headers, **kwargs)

            # Get trace_id for capture
            trace_id = trace_id_ctx.get(None) or ""

            # Capture request data
            req_data = b""
            req_headers = b""
            try:
                if body:
                    if isinstance(body, bytes):
                        req_data = body
                    elif isinstance(body, str):
                        req_data = body.encode("utf-8")

                # Capture request headers
                if HAS_ORJSON:
                    req_headers = orjson.dumps({str(k): str(v) for k, v in headers.items()})
                else:
                    req_headers = json.dumps({str(k): str(v) for k, v in headers.items()}).encode("utf-8")
            except Exception:  # noqa: BLE001
                pass

            try:
                # perform the actual HTTP call
                response, content = original_request(
                    self, uri, method, body=body, headers=headers, **kwargs
                )
                status_code = getattr(response, "status", None) or getattr(
                    response, "status_code", None
                )
                success = isinstance(status_code, int) and 200 <= status_code < 400

                # Capture response data and headers
                resp_data = b""
                resp_headers = b""

                # content is already the response body in httplib2
                resp_data = content if isinstance(content, bytes) else b""
                # Capture response headers
                if HAS_ORJSON:
                    resp_headers = orjson.dumps({str(k): str(v) for k, v in response.items()})
                else:
                    resp_headers = json.dumps({str(k): str(v) for k, v in response.items()}).encode("utf-8")

                # record success (only when LD_PRELOAD is NOT active)
                record_network_request(
                    trace_id,
                    uri,
                    method,
                    status_code,
                    success,
                    timestamp_start=start_ts,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    response_data=resp_data,
                    request_headers=req_headers,
                    response_headers=resp_headers,
                )

                return response, content

            except Exception as e:
                # record failures (only when LD_PRELOAD is NOT active)
                record_network_request(
                    trace_id,
                    uri,
                    method,
                    0,
                    False,
                    error=str(e)[:255],
                    timestamp_start=start_ts,
                    timestamp_end=int(time.time() * 1_000),
                    request_data=req_data,
                    request_headers=req_headers,
                )
                raise

        # apply our patch (only if not using wrapt in fast path)
        if not (use_fast_path and HAS_WRAPT):
            httplib2.Http.request = patched_request
