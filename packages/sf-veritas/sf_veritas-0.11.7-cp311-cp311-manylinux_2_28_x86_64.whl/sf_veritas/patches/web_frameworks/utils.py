import fnmatch
import inspect
import os
import sysconfig
from typing import Any, Callable, List, Optional, Set

try:
    from ... import _sffastlog
    from ... import app_config
    from ...custom_output_wrapper import _ensure_fast_print_initialized
    from ...interceptors import _COLLECT_LOGS_MUTATION
    import sf_veritas.custom_output_wrapper as output_wrapper
    from ...env_vars import PRINT_CONFIGURATION_STATUSES, SF_DEBUG

    _SFFASTLOG_OK = True
except ImportError:
    _sffastlog = None
    _SFFASTLOG_OK = False

_stdlib = sysconfig.get_paths()["stdlib"]


_ATTR_CANDIDATES = (
    "resolver",
    "func",
    "python_func",
    "_resolver",
    "wrapped_func",
    "__func",
)


def _is_user_code(path: Optional[str] = None) -> bool:
    return (
        bool(path)
        and not path.startswith(_stdlib)
        and "site-packages" not in path
        and "dist-packages" not in path
        and not path.startswith("<")
    )


def _unwrap_user_func(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Unwrap decorators & closures until we find your user function."""
    seen: Set[int] = set()
    queue = [fn]
    while queue:
        current = queue.pop()
        if id(current) in seen:
            continue
        seen.add(id(current))

        if inspect.isfunction(current) and _is_user_code(current.__code__.co_filename):
            return current

        inner = getattr(current, "__wrapped__", None)
        if inner:
            queue.append(inner)

        for attr in _ATTR_CANDIDATES:
            attr_val = getattr(current, attr, None)
            if inspect.isfunction(attr_val):
                queue.append(attr_val)

        for cell in getattr(current, "__closure__", []) or []:
            cc = cell.cell_contents
            if inspect.isfunction(cc):
                queue.append(cc)

    return fn  # fallback


def should_skip_route(route_pattern: str, routes_to_skip: List[str]) -> bool:
    """
    Check if route should be skipped based on wildcard patterns.

    Supports Unix shell-style wildcards:
    - Exact match: "/healthz" matches "/healthz"
    - Wildcard *: "/he*" matches "/health", "/healthz", "/healthz/foo"
    - Wildcard ?: "/health?" matches "/healthz" but not "/health"
    - Character sets: "/health[z12]" matches "/healthz", "/health1", "/health2"

    Examples:
        - "/he*" → matches "/health", "/healthz", "/healthz/foo"
        - "/metrics*" → matches "/metrics", "/metrics/detailed"
        - "/api/internal/*" → matches "/api/internal/status", "/api/internal/debug"
        - "*/admin" → matches "/foo/admin", "/bar/admin"

    Args:
        route_pattern: Route pattern to check (e.g., "/healthz", "/log/{n}")
        routes_to_skip: List of patterns to skip (can contain wildcards)

    Returns:
        True if route should be skipped, False otherwise
    """
    if not routes_to_skip or not route_pattern:
        return False

    for skip_pattern in routes_to_skip:
        # Use fnmatch for Unix shell-style wildcards
        # This supports * (matches anything) and ? (matches single char)
        if fnmatch.fnmatch(route_pattern, skip_pattern):
            return True

    return False


def reinitialize_log_print_capture_for_worker() -> None:
    """
    Reinitialize log/print capture for worker processes.

    CRITICAL: When web servers fork workers (e.g., Supervisor with numprocs=2, Gunicorn),
    daemon threads don't survive the fork but global flags do. This function:
    1. Resets global initialization flags
    2. Creates new daemon threads for log/print capture in each worker

    Called by web framework middleware __init__ methods to ensure each worker
    has its own sender threads.
    """
    if not _SFFASTLOG_OK or not _sffastlog:
        if SF_DEBUG or PRINT_CONFIGURATION_STATUSES:
            print(f"[WebFramework] Worker PID={os.getpid()} _sffastlog not available", log=False)
        return

    try:
        if SF_DEBUG or PRINT_CONFIGURATION_STATUSES:
            print(f"[WebFramework] Worker PID={os.getpid()} startup - reinitializing log/print capture", log=False)

        # Force reset of global flags to trigger re-initialization
        output_wrapper._FAST_PRINT_READY = False

        # Reinitialize print capture (creates new daemon threads for this worker)
        print_ok = _ensure_fast_print_initialized()

        # Reinitialize log capture (creates new daemon threads for this worker)
        endpoint = getattr(app_config, "_sailfish_graphql_endpoint", None)
        api_key = getattr(app_config, "_sailfish_api_key", None)
        service_uuid = getattr(app_config, "_service_uuid", None)
        library = getattr(app_config, "library", "sailfish-python")
        version = getattr(app_config, "version", "0.0.0")
        http2 = 1 if os.getenv("SF_NBPOST_HTTP2", "0") == "1" else 0

        if endpoint and api_key and service_uuid:
            log_ok = _sffastlog.init(
                url=endpoint,
                query=_COLLECT_LOGS_MUTATION,
                api_key=str(api_key),
                service_uuid=str(service_uuid),
                library=str(library),
                version=str(version),
                http2=http2,
            )

            if SF_DEBUG or PRINT_CONFIGURATION_STATUSES:
                print(f"[WebFramework] Worker PID={os.getpid()} log/print capture initialized: print={print_ok}, log={log_ok}", log=False)
        else:
            if SF_DEBUG or PRINT_CONFIGURATION_STATUSES:
                print(f"[WebFramework] Worker PID={os.getpid()} log/print capture skipped (missing config)", log=False)

    except Exception as e:
        print(f"[WebFramework] Worker PID={os.getpid()} failed to reinitialize log/print capture: {e}", log=False)
        import traceback
        traceback.print_exc()
