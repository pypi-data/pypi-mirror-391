# sf_veritas/patches/network_libraries/http_client.py
import os
import time
import traceback
from typing import List, Optional, Tuple

try:
    import wrapt

    HAS_WRAPT = True
except ImportError:
    HAS_WRAPT = False

from ... import _sffastnetworkrequest as _fast  # native module
from ...constants import SAILFISH_TRACING_HEADER, PARENT_SESSION_ID_HEADER
from ...env_vars import SF_DEBUG
from ...thread_local import is_network_recording_suppressed, trace_id_ctx
from .utils import init_fast_header_check, inject_headers_ultrafast, record_network_request, init_fast_network_tracking, is_ssl_socket_active, has_sailfish_header

# JSON serialization - try fast orjson first, fallback to stdlib json
try:
    import orjson

    HAS_ORJSON = True
except ImportError:
    import json

    HAS_ORJSON = False

TRACE_HEADER_LOWER = SAILFISH_TRACING_HEADER.lower()
PARENT_HEADER_LOWER = PARENT_SESSION_ID_HEADER.lower()
# --- Native fast path (C) readiness probe -------------------------
_FAST = None


def _install_putheader_debug(_hc):
    """Instrument http.client putheader to trace Sailfish headers when SF_DEBUG is on."""
    if not SF_DEBUG:
        return
    putheader = getattr(_hc.HTTPConnection, "putheader", None)
    if not putheader or getattr(putheader, "_sf_debug_wrapped", False):
        return

    original_putheader = putheader

    def debug_putheader(self, header, *values):
        header_text = header
        if isinstance(header_text, bytes):
            header_text = header_text.decode("latin-1", "ignore")
        header_lower = header_text.lower() if isinstance(header_text, str) else None
        if header_lower in (TRACE_HEADER_LOWER, PARENT_HEADER_LOWER):
            try:
                value_preview = [
                    v.decode("latin-1", "ignore") if isinstance(v, (bytes, bytearray)) else str(v)
                    for v in values
                ]
                print(
                    "[http.client.putheader] method="
                    f"{getattr(self, '_method', '?')} header={header_text} values={value_preview}",
                    log=False,
                )
                stack = "".join(traceback.format_stack(limit=4))
                print(f"[http.client.putheader] stack:\n{stack}", log=False)
            except Exception as exc:
                print(f"[http.client.putheader] debug log failed: {exc}", log=False)
        return original_putheader(self, header, *values)

    debug_putheader._sf_debug_wrapped = True  # type: ignore[attr-defined]
    _hc.HTTPConnection.putheader = debug_putheader


def _fast_ready() -> bool:
    global _FAST
    if _FAST is None:
        try:
            _FAST = _fast

            if SF_DEBUG:
                try:
                    print(
                        "[http_client] _sffastnetworkrequest loaded successfully",
                        log=False,
                    )
                except TypeError:
                    print("[http_client] _sffastnetworkrequest loaded successfully")
        except Exception as e:
            _FAST = False

            if SF_DEBUG:
                try:
                    print(
                        f"[http_client] _sffastnetworkrequest NOT available: {e}",
                        log=False,
                    )
                except TypeError:
                    print(f"[http_client] _sffastnetworkrequest NOT available: {e}")
    if _FAST is False:
        return False
    try:
        ready = bool(_FAST.is_ready())

        if SF_DEBUG:
            try:
                print(
                    f"[http_client] _sffastnetworkrequest.is_ready() = {ready}",
                    log=False,
                )
            except TypeError:
                print(f"[http_client] _sffastnetworkrequest.is_ready() = {ready}")
        return ready
    except Exception as e:
        if SF_DEBUG:
            try:
                print(f"[http_client] is_ready() check failed: {e}", log=False)
            except TypeError:
                print(f"[http_client] is_ready() check failed: {e}")
        return False


def _split_headers_and_body_from_send_chunk(
    chunk: memoryview, state
) -> Tuple[Optional[bytes], Optional[bytes]]:
    if state["seen_hdr_end"]:
        return None, bytes(chunk)

    mv = chunk
    pos = mv.tobytes().find(b"\r\n\r\n")
    if pos == -1:
        state["hdr_buf"].append(bytes(mv))
        return None, None

    hdr_part = bytes(mv[: pos + 4])
    body_part = bytes(mv[pos + 4 :])
    state["hdr_buf"].append(hdr_part)
    state["seen_hdr_end"] = True
    return b"".join(state["hdr_buf"]), body_part if body_part else None


def _parse_request_headers_from_block(block: bytes) -> dict:
    headers = {}
    lines = block.split(b"\r\n")
    for raw in lines[1:]:
        if not raw:
            break
        i = raw.find(b":")
        if i <= 0:
            continue
        k = raw[:i].decode("latin1", "replace").strip()
        v = raw[i + 1 :].decode("latin1", "replace").strip()
        headers[k] = v
    return headers


def _tee_preload_active() -> bool:
    """Detect if the LD_PRELOAD tee is active; if so, skip Python-level patch."""
    if os.getenv("SF_TEE_PRELOAD_ONLY", "0") == "1":
        return True
    ld = os.getenv("LD_PRELOAD", "")
    # match our shipped name
    return "libsfnettee.so" in ld or "_sfteepreload" in ld


def patch_http_client(domains_to_not_propagate_headers_to: Optional[List[str]] = None):
    """
    ALWAYS patch for header injection (trace_id + funcspan_override).
    Skip capture/emission if LD_PRELOAD tee is active (socket layer already captures).

    This ensures headers propagate correctly regardless of capture mechanism.
    """
    preload_active = _tee_preload_active()

    # Initialize C extension for ultra-fast header checking (if available)
    if preload_active:
        init_fast_header_check(domains_to_not_propagate_headers_to or [])
        if SF_DEBUG:
            try:
                print(
                    "[http_client] LD_PRELOAD tee active; patching for headers only (no capture)",
                    log=False,
                )
            except TypeError:
                print(
                    "[http_client] LD_PRELOAD tee active; patching for headers only (no capture)"
                )

    # Initialize fast network tracking (collectNetworkRequest mutation sender)
    # This must be called to set up the C extension that sends network requests
    if not preload_active:
        init_fast_network_tracking()
        if SF_DEBUG:
            try:
                print("[http_client] Initialized fast network tracking for collectNetworkRequest", log=False)
            except TypeError:
                print("[http_client] Initialized fast network tracking for collectNetworkRequest")

    # Check if C extension is available for capture (not required for header injection)
    fast_available = False
    if not preload_active:
        fast_available = _fast_ready()
        if not fast_available and SF_DEBUG:
            try:
                print(
                    "[http_client] C extension not ready - will patch for headers only (no capture)",
                    log=False,
                )
            except TypeError:
                print(
                    "[http_client] C extension not ready - will patch for headers only (no capture)"
                )

    _fast = _FAST if (not preload_active and fast_available) else None  # type: ignore[assignment]
    if domains_to_not_propagate_headers_to is None:
        domains_to_not_propagate_headers_to = []

    if SF_DEBUG:
        mode = "headers only" if preload_active else "full capture"
        try:
            print(
                f"[http_client] Patching http.client ({mode})",
                log=False,
            )
        except TypeError:
            print(f"[http_client] Patching http.client ({mode})")

    try:
        import http.client as _hc
    except ImportError:
        if SF_DEBUG:
            try:
                print("[http_client] http.client not available to patch", log=False)
            except TypeError:
                print("[http_client] http.client not available to patch")
        return

    _install_putheader_debug(_hc)

    # Body size limits (only needed if NOT using preload)
    if not preload_active:
        try:
            SFF_MAX_REQ_BODY = getattr(_fast, "SFF_MAX_REQ_BODY", 8192)
            SFF_MAX_RESP_BODY = getattr(_fast, "SFF_MAX_RESP_BODY", 8192)
        except Exception:
            SFF_MAX_REQ_BODY = 8192
            SFF_MAX_RESP_BODY = 8192
    else:
        SFF_MAX_REQ_BODY = 0
        SFF_MAX_RESP_BODY = 0

    if SF_DEBUG:
        print("SFF_MAX_REQ_BODY=", SFF_MAX_REQ_BODY, log=False)
        print("SFF_MAX_RESP_BODY=", SFF_MAX_RESP_BODY, log=False)

    original_request = _hc.HTTPConnection.request
    original_send = _hc.HTTPConnection.send
    original_getresponse = _hc.HTTPConnection.getresponse
    original_close = _hc.HTTPConnection.close
    original_response_read = _hc.HTTPResponse.read

    def patched_request(
        self, method, url, body=None, headers=None, *, encode_chunked=False
    ):
        # CRITICAL: Clean any stale capture state from connection reuse
        # httplib2 pools connections and reuses them across requests, which can
        # leave stale _sf_req_capture state that corrupts subsequent requests
        if hasattr(self, "_sf_req_capture"):
            delattr(self, "_sf_req_capture")
        if hasattr(self, "_sf_response_processed"):
            delattr(self, "_sf_response_processed")

        # Build full URL for domain checking (http.client uses relative paths)
        full_url = url
        if not url.startswith(("http://", "https://")):
            # Relative path - build full URL from connection
            scheme = "https" if isinstance(self, _hc.HTTPSConnection) else "http"
            full_url = (
                f"{scheme}://{self.host}:{self.port}{url}"
                if self.port not in (80, 443)
                else f"{scheme}://{self.host}{url}"
            )

        # ULTRA-FAST header injection using inject_headers_ultrafast() (~100ns)
        # Create dict for injection, then check if we actually added anything
        hdrs_dict = dict(headers) if headers else {}
        original_keys = set(hdrs_dict.keys())

        # Check if headers are already injected (avoid double-injection with httplib2/requests)
        # Fast O(1) check for common cases, fallback to O(n) for rare mixed-case variants
        has_trace = has_sailfish_header(hdrs_dict)
        if SF_DEBUG:
            print(f"[http_client dedup check] headers_keys={list(hdrs_dict.keys())}, has_trace={has_trace}", log=False)

        if not has_trace:
            inject_headers_ultrafast(
                hdrs_dict, full_url, domains_to_not_propagate_headers_to
            )
        elif SF_DEBUG:
            print(f"[http_client] SKIPPED injection - headers already present!", log=False)

        # Only use dict if we added headers OR original had headers (preserve None if nothing to add)
        if headers or set(hdrs_dict.keys()) != original_keys:
            hdrs_out = hdrs_dict
        else:
            hdrs_out = None  # Preserve None if no headers were originally provided and none were injected

        # Only capture state if NOT using LD_PRELOAD (preload captures at socket layer)
        # ALSO skip capture for HTTPS when ssl_socket.py is active (avoids double-capture)
        is_https = isinstance(self, _hc.HTTPSConnection)
        skip_capture = preload_active or (is_https and is_ssl_socket_active())

        if not skip_capture:
            # Get trace_id for capture (already injected in headers)
            trace_id = trace_id_ctx.get(None) or ""

            start_ts = int(time.time() * 1_000)
            # Store state as list [start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, seen_end]
            # Lists are mutable so patched_send can append to buffers
            self._sf_req_capture = [
                start_ts,
                trace_id,
                url,
                method,
                bytearray(),
                bytearray(),
                False,
            ]

        if SF_DEBUG:
            trace_headers = {k: v for k, v in (hdrs_out or {}).items() if isinstance(k, str) and k.lower() in (TRACE_HEADER_LOWER, PARENT_HEADER_LOWER)}
            print(f"[http_client] CALLING original_request with headers={trace_headers}", log=False)

        return original_request(
            self,
            method,
            url,
            body=body,
            headers=hdrs_out,
            encode_chunked=encode_chunked,
        )

    def patched_send(self, data):
        state = getattr(self, "_sf_req_capture", None)
        # DEFENSIVE: Ensure state is valid and not from a previous request (httplib2 connection reuse)
        if state is not None and isinstance(state, list) and len(state) == 7:
            # FAST: Capture headers and body without parsing
            # state = [start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, seen_end]
            hdr_buf, body_buf, seen_end = state[4], state[5], state[6]

            if not seen_end:
                # Look for \r\n\r\n to split headers from body
                pos = data.find(b"\r\n\r\n")
                if pos >= 0:
                    hdr_buf.extend(data[: pos + 4])
                    if len(data) > pos + 4:
                        cap = SFF_MAX_REQ_BODY - len(body_buf)
                        if cap > 0:
                            body_buf.extend(data[pos + 4 : pos + 4 + cap])
                    state[6] = True  # Mark seen_end
                else:
                    hdr_buf.extend(data)
            else:
                # Already saw headers, just capture body
                cap = SFF_MAX_REQ_BODY - len(body_buf)
                if cap > 0:
                    body_buf.extend(data[:cap])

        return original_send(self, data)

    def patched_getresponse(self):
        response = original_getresponse(self)

        state = getattr(self, "_sf_req_capture", None)
        if not state:
            return response

        # CRITICAL: Prevent double-processing from httplib2 connection reuse
        # If this connection was already processed, clean up and return early
        if getattr(self, "_sf_response_processed", False):
            if hasattr(self, "_sf_req_capture"):
                delattr(self, "_sf_req_capture")
            if hasattr(self, "_sf_response_processed"):
                delattr(self, "_sf_response_processed")
            return response

        # Check if network recording is suppressed (e.g., by @skip_network_tracing decorator)
        if is_network_recording_suppressed():
            delattr(self, "_sf_req_capture")
            return response

        # Mark as processed BEFORE attempting capture (prevents re-entry if getresponse called again)
        self._sf_response_processed = True

        # CRITICAL: Set up response body capture buffer (httplib2 compatibility)
        # Instead of peek() which hangs with SSL, we'll capture body in patched_response_read()
        # when httplib2 calls response.read() to consume the body
        self._sf_response_body_buf = bytearray() if SFF_MAX_RESP_BODY > 0 else None
        # Store reference to connection so patched_response_read can find the buffer
        response._orig_conn = self
        # Mark that we haven't emitted capture yet (will emit after body is read or on close)
        self._sf_capture_emitted = False

        # ULTRA-FAST: Prepare captured data for later emission (after body is read)
        try:
            # state = [start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, seen_end]
            start_ts, trace_id, url, method, req_hdr_buf, req_body_buf, _ = state
            delattr(self, "_sf_req_capture")

            status = int(getattr(response, "status", 0))
            ok = 1 if status < 400 else 0
            end_ts = int(time.time() * 1_000)

            # FAST: Parse request headers from buffer
            req_headers_json = "{}"
            hdr_dict = {}
            if req_hdr_buf:
                try:
                    hdr_dict = _parse_request_headers_from_block(bytes(req_hdr_buf))
                except Exception:
                    pass

                if HAS_ORJSON:
                    req_headers_json = orjson.dumps(hdr_dict).decode("utf-8")
                else:
                    req_headers_json = json.dumps(hdr_dict).decode("utf-8")

            # FAST: Get response headers
            resp_headers_json = "{}"
            if HAS_ORJSON:
                resp_headers_json = orjson.dumps(
                    {str(k): str(v) for k, v in response.getheaders()}
                ).decode("utf-8")
            else:
                resp_headers_json = json.dumps(
                    {str(k): str(v) for k, v in response.getheaders()}
                ).decode("utf-8")

            # Store capture data on connection for later emission (after body is read)
            # This deferred emission allows httplib2 to call response.read() and fill
            # _sf_response_body_buf via patched_response_read()
            self._sf_pending_capture = {
                "trace_id": trace_id,
                "url": url,
                "method": method,
                "status": status,
                "ok": ok,
                "timestamp_start": start_ts,
                "timestamp_end": end_ts,
                "request_body": bytes(req_body_buf) if req_body_buf else b"",
                "request_headers_json": req_headers_json,
                "response_headers_json": resp_headers_json,
            }
        except Exception:
            pass

        return response

    def patched_response_read(self, amt=None):
        """
        Capture response body as httplib2 reads it (solves peek() hang issue).

        Instead of peeking in getresponse() (which interferes with SSL socket state),
        we capture the body when httplib2 calls response.read() to consume it.
        This is non-invasive and works perfectly with connection pooling.
        """
        # Call original read() first
        data = original_response_read(self, amt)

        # If this response belongs to a connection being captured, store the body
        conn = getattr(self, "_orig_conn", None)
        if conn:
            # Capture body if buffer exists
            if (
                hasattr(conn, "_sf_response_body_buf")
                and conn._sf_response_body_buf is not None
                and data
            ):
                buf = conn._sf_response_body_buf
                # Only capture up to limit
                remaining = SFF_MAX_RESP_BODY - len(buf)
                if remaining > 0:
                    buf.extend(data[:remaining])

            # Emit capture after first read (httplib2 typically reads entire body in one call)
            # or when no more data (empty read signals EOF)
            if hasattr(conn, "_sf_pending_capture") and not getattr(
                conn, "_sf_capture_emitted", False
            ):
                # Check if we should emit now (either got data or EOF)
                should_emit = (data is not None) and (
                    len(data) == 0 or amt is None or (amt and len(data) > 0)
                )

                if should_emit or not data:  # Emit on first read or EOF
                    try:
                        capture = conn._sf_pending_capture
                        resp_body = (
                            bytes(conn._sf_response_body_buf)
                            if conn._sf_response_body_buf
                            else b""
                        )

                        # Emit mutation collectNetworkRequest (not collectNetworkHop!)
                        record_network_request(
                            trace_id=capture["trace_id"],
                            url=capture["url"],
                            method=capture["method"],
                            status_code=capture["status"],
                            success=capture["ok"],
                            timestamp_start=capture["timestamp_start"],
                            timestamp_end=capture["timestamp_end"],
                            request_data=capture["request_body"],
                            response_data=resp_body,
                            request_headers=capture["request_headers_json"].encode('utf-8') if capture["request_headers_json"] else b"",
                            response_headers=capture["response_headers_json"].encode('utf-8') if capture["response_headers_json"] else b"",
                        )

                        conn._sf_capture_emitted = True
                        delattr(conn, "_sf_pending_capture")
                    except Exception:
                        pass

        return data

    def patched_close(self):
        """Clean up capture state when connection is closed (httplib2 connection pooling)."""
        # CRITICAL: Emit any pending capture before closing (if body wasn't read)
        if hasattr(self, "_sf_pending_capture") and not getattr(
            self, "_sf_capture_emitted", False
        ):
            try:
                capture = self._sf_pending_capture
                resp_body = (
                    bytes(self._sf_response_body_buf)
                    if hasattr(self, "_sf_response_body_buf")
                    and self._sf_response_body_buf
                    else b""
                )

                # Emit mutation collectNetworkRequest (not collectNetworkHop!)
                record_network_request(
                    trace_id=capture["trace_id"],
                    url=capture["url"],
                    method=capture["method"],
                    status_code=capture["status"],
                    success=capture["ok"],
                    timestamp_start=capture["timestamp_start"],
                    timestamp_end=capture["timestamp_end"],
                    request_data=capture["request_body"],
                    response_data=resp_body,
                    request_headers=capture["request_headers_json"].encode('utf-8') if capture["request_headers_json"] else b"",
                    response_headers=capture["response_headers_json"].encode('utf-8') if capture["response_headers_json"] else b"",
                )
            except Exception:
                pass

        # Clean capture state before closing to prevent memory leaks
        # and ensure proper SSL shutdown (prevents TimeoutError: SSL shutdown timed out)
        if hasattr(self, "_sf_req_capture"):
            delattr(self, "_sf_req_capture")
        if hasattr(self, "_sf_response_processed"):
            delattr(self, "_sf_response_processed")
        if hasattr(self, "_sf_response_body_buf"):
            delattr(self, "_sf_response_body_buf")
        if hasattr(self, "_sf_pending_capture"):
            delattr(self, "_sf_pending_capture")
        if hasattr(self, "_sf_capture_emitted"):
            delattr(self, "_sf_capture_emitted")

        # Call original close() to perform actual connection teardown
        return original_close(self)

    # ALWAYS patch request() for header injection (even with LD_PRELOAD or no C extension)
    if HAS_WRAPT:

        def instrumented_request(wrapped, instance, args, kwargs):
            """Ultra-fast header injection using wrapt."""
            method = args[0] if len(args) > 0 else kwargs.get("method", "GET")
            url = args[1] if len(args) > 1 else kwargs.get("url", "")
            body = args[2] if len(args) > 2 else kwargs.get("body", None)
            headers = args[3] if len(args) > 3 else kwargs.get("headers", None)
            encode_chunked = kwargs.get("encode_chunked", False)
            return patched_request(
                instance, method, url, body, headers, encode_chunked=encode_chunked
            )

        wrapt.wrap_function_wrapper(_hc.HTTPConnection, "request", instrumented_request)
    else:
        _hc.HTTPConnection.request = patched_request

    # ONLY patch send/getresponse if NOT using LD_PRELOAD AND C extension is available (for capture/emission)
    if not preload_active and fast_available:
        if HAS_WRAPT:

            def instrumented_send(wrapped, instance, args, kwargs):
                """Ultra-fast send wrapper using wrapt."""
                data = args[0] if len(args) > 0 else kwargs.get("data", b"")
                return patched_send(instance, data)

            def instrumented_getresponse(wrapped, instance, args, kwargs):
                """Ultra-fast getresponse wrapper using wrapt."""
                return patched_getresponse(instance)

            wrapt.wrap_function_wrapper(_hc.HTTPConnection, "send", instrumented_send)
            wrapt.wrap_function_wrapper(
                _hc.HTTPConnection, "getresponse", instrumented_getresponse
            )
        else:
            _hc.HTTPConnection.send = patched_send
            _hc.HTTPConnection.getresponse = patched_getresponse

        if SF_DEBUG:
            try:
                print("[http_client] Patched send/getresponse for capture", log=False)
            except TypeError:
                print("[http_client] Patched send/getresponse for capture")
    else:
        reason = (
            "LD_PRELOAD handles capture"
            if preload_active
            else "C extension not available"
        )
        if SF_DEBUG:
            try:
                print(
                    f"[http_client] Skipped send/getresponse patches ({reason})",
                    log=False,
                )
            except TypeError:
                print(f"[http_client] Skipped send/getresponse patches ({reason})")

    # ALWAYS patch close() to clean up capture state (critical for httplib2 connection pooling)
    # This prevents SSL shutdown timeouts when connections are reused
    if HAS_WRAPT:

        def instrumented_close(wrapped, instance, args, kwargs):
            """Ultra-fast close wrapper using wrapt."""
            return patched_close(instance)

        wrapt.wrap_function_wrapper(_hc.HTTPConnection, "close", instrumented_close)
    else:
        _hc.HTTPConnection.close = patched_close

    # ALWAYS patch HTTPResponse.read() to capture response body (httplib2 compatibility)
    # This allows us to capture body as httplib2 reads it, avoiding peek() hang issue
    if HAS_WRAPT:

        def instrumented_response_read(wrapped, instance, args, kwargs):
            """Ultra-fast response read wrapper using wrapt."""
            amt = args[0] if len(args) > 0 else kwargs.get("amt", None)
            return patched_response_read(instance, amt)

        wrapt.wrap_function_wrapper(
            _hc.HTTPResponse, "read", instrumented_response_read
        )
    else:
        _hc.HTTPResponse.read = patched_response_read

    if SF_DEBUG:
        try:
            print(
                "[http_client] Patched close() and HTTPResponse.read() for httplib2 compatibility",
                log=False,
            )
        except TypeError:
            print(
                "[http_client] Patched close() and HTTPResponse.read() for httplib2 compatibility"
            )
def _install_putheader_debug(_hc):
    """Instrument http.client putheader to trace Sailfish headers when SF_DEBUG is on."""
    if not (SF_DEBUG and getattr(_hc.HTTPConnection.putheader, "_sf_debug_wrapped", False) is False):
        return
