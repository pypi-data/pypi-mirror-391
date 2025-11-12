"""
Ultra-fast SSL socket tee for HTTPS traffic capture.
~15-20ns overhead per recv/send operation.

CRITICAL: This must be patched FIRST before any other HTTP library patches,
because requests/httpx/urllib3/aiohttp all use ssl.SSLSocket underneath.

Architecture:
1. Hot path (~15-20ns): Tee data to thread-local deque, return immediately
2. Background thread: Aggregates bytes → HTTP transactions
3. Push complete transactions to C ring buffer via ctypes
4. C ring handles queueing, retries, HTTP/2, telemetry delivery

Performance:
- Thread-local deque: No locks, ~10ns append
- Graceful degradation: Drop if queue full, never block caller
- Zero hot path impact: All parsing/transmission happens in background

**IMPORTANT: This code is currently DISABLED by default.**
**Set SF_ENABLE_PYTHON_SSL_TEE=1 to enable.**
**By default, SF_SSL_PYTHON_MODE=1 just disables C SSL hooks without Python capture.**

Environment Variables (respects SF_NETWORKREQUEST_CAPTURE_* settings):
- SF_NETWORKREQUEST_CAPTURE_ENABLED: Enable/disable all capture (default: true)
- SF_NETWORKREQUEST_CAPTURE_REQUEST_HEADERS: Capture request headers (default: true)
- SF_NETWORKREQUEST_CAPTURE_REQUEST_BODY: Capture request body (default: true)
- SF_NETWORKREQUEST_CAPTURE_RESPONSE_HEADERS: Capture response headers (default: true)
- SF_NETWORKREQUEST_CAPTURE_RESPONSE_BODY: Capture response body (default: true)
- SF_NETWORKREQUEST_REQUEST_LIMIT_MB: Max request body size in MB (default: 1)
- SF_NETWORKREQUEST_RESPONSE_LIMIT_MB: Max response body size in MB (default: 1)
"""

import ssl
import socket
import threading
import time
import ctypes
from collections import deque
from typing import Optional, Dict, Any
import os

# Import record_network_request for collectNetworkRequest mutation
from .utils import record_network_request, init_fast_network_tracking

# ============================================================================
# CONFIGURATION
# ============================================================================

# Check if Python SSL tee is enabled (DISABLED by default)
_PYTHON_SSL_TEE_ENABLED = os.getenv('SF_ENABLE_PYTHON_SSL_TEE', 'false').lower() == 'true'
_C_RING_AVAILABLE = os.getenv('SF_SSL_PYTHON_MODE', '1') == '1' and _PYTHON_SSL_TEE_ENABLED
_SF_DEBUG = os.getenv('SF_DEBUG', 'false').lower() == 'true'

# SF_NETWORKREQUEST_CAPTURE_* environment variables (for collectNetworkRequest mutations)
# These control what data is captured and sent to the C ring
_CAPTURE_ENABLED = os.getenv('SF_NETWORKREQUEST_CAPTURE_ENABLED', 'true').lower() == 'true'
_CAPTURE_REQUEST_HEADERS = os.getenv('SF_NETWORKREQUEST_CAPTURE_REQUEST_HEADERS', 'true').lower() == 'true'
_CAPTURE_REQUEST_BODY = os.getenv('SF_NETWORKREQUEST_CAPTURE_REQUEST_BODY', 'true').lower() == 'true'
_CAPTURE_RESPONSE_HEADERS = os.getenv('SF_NETWORKREQUEST_CAPTURE_RESPONSE_HEADERS', 'true').lower() == 'true'
_CAPTURE_RESPONSE_BODY = os.getenv('SF_NETWORKREQUEST_CAPTURE_RESPONSE_BODY', 'true').lower() == 'true'

# Size limits (MB to bytes conversion)
_REQUEST_LIMIT_MB = float(os.getenv('SF_NETWORKREQUEST_REQUEST_LIMIT_MB', '1'))
_RESPONSE_LIMIT_MB = float(os.getenv('SF_NETWORKREQUEST_RESPONSE_LIMIT_MB', '1'))
MAX_REQUEST_BODY_CAPTURE = int(_REQUEST_LIMIT_MB * 1024 * 1024)
MAX_RESPONSE_BODY_CAPTURE = int(_RESPONSE_LIMIT_MB * 1024 * 1024)

# ============================================================================
# THREAD-LOCAL CAPTURE QUEUES (Zero-lock, ~10ns append)
# ============================================================================

_capture_queues = {}  # thread_id -> deque
_capture_queues_lock = threading.Lock()


def _get_capture_queue():
    """Get thread-local capture queue (~5ns lookup)"""
    tid = threading.get_ident()
    if tid not in _capture_queues:
        with _capture_queues_lock:
            if tid not in _capture_queues:
                _capture_queues[tid] = deque(maxlen=1000)  # Bounded to prevent OOM
    return _capture_queues[tid]


# ============================================================================
# HOT PATH - ULTRA FAST (~15-20ns overhead)
# ============================================================================

def _tee_capture(sock, data, direction):
    """
    Tee-style capture: ~15ns overhead, non-blocking

    Recursion Prevention:
    - Detects X-Sf3-TelemetryOutbound header in requests (telemetry marker)
    - Marks socket as telemetry and skips all future captures
    - Prevents infinite recursion from capturing our own telemetry traffic

    Performance breakdown:
    - Get thread-local queue: ~5ns
    - Append to deque: ~5-10ns
    - Wake background thread: ~5ns
    Total: ~15-20ns
    """
    # Defensive: ensure data is bytes-like before processing
    if not data:
        return
    if not isinstance(data, (bytes, bytearray)):
        # Invalid data type (should never happen, but be defensive)
        return
    if len(data) == 0:
        return

    # CRITICAL: Recursion prevention - detect telemetry traffic by X-Sf3-TelemetryOutbound header
    # This header is ONLY added to our own telemetry requests (in request_utils.py)
    # Normal application traffic (even to echo endpoints) will NOT have this header
    if b'X-Sf3-TelemetryOutbound:' in data or b'x-sf3-telemetryoutbound:' in data:
        # Mark this socket as telemetry to skip all future captures
        sock._is_telemetry_socket = True
        if _SF_DEBUG:
            print(f"[ssl_socket.py] _tee_capture: Detected telemetry socket, marking to skip", log=False)
        return

    # Skip if already marked as telemetry socket
    if getattr(sock, '_is_telemetry_socket', False):
        return

    try:
        queue = _get_capture_queue()
        sock_id = id(sock)

        if direction == 'TX' and _SF_DEBUG:
            chunk = bytes(data)
            existing = getattr(sock, '_sf_hdr_buf', b'')
            combined = existing + chunk
            if b'\r\n\r\n' in combined and not getattr(sock, '_sf_headers_logged', False):
                header_bytes = combined.split(b'\r\n\r\n', 1)[0]
                try:
                    header_text = header_bytes.decode('latin-1', errors='ignore')
                except Exception:
                    header_text = "<failed to decode headers>"
                print(f"[ssl_socket.py] PRE-SEND HEADERS (sock_id={sock_id}):\n{header_text}", log=False)
                sock._sf_headers_logged = True
                sock._sf_hdr_buf = b''
            else:
                sock._sf_hdr_buf = combined[-8192:]  # keep manageable buffer

        # Debug: Log first capture for each socket
        if _SF_DEBUG and not hasattr(sock, '_first_capture_logged'):
            sock._first_capture_logged = True
            peername = getattr(sock, '_peername_cache', None)
            print(f"[ssl_socket.py] _tee_capture: FIRST CAPTURE sock_id={sock_id}, direction={direction}, size={len(data)} bytes, peername={peername}", log=False)

        queue.append({
            'sock_id': sock_id,
            'peername': getattr(sock, '_peername_cache', None),
            'data': data,
            'direction': direction,
            'timestamp': time.perf_counter_ns()
        })
        _background_event.set()  # Wake background processor (non-blocking)
    except Exception as e:
        # Never let capture errors break the hot path
        if _SF_DEBUG:
            print(f"[ssl_socket.py] _tee_capture: Exception: {e}", log=False)


# ============================================================================
# SSL SOCKET MONKEY PATCHING
# ============================================================================

_original_recv = None
_original_send = None
_original_sendall = None
_original_read = None
_original_write = None
_patched = False


def patch_ssl_sockets():
    """
    Patch ssl.SSLSocket for tee-style HTTPS capture.

    CRITICAL: Call this FIRST before patching requests/httpx/urllib3,
    because all HTTP libraries use ssl.SSLSocket underneath.

    Patches: recv, send, sendall, read, write

    NOTE: By default, this function is a NO-OP (Python SSL tee is DISABLED).
    Only when SF_ENABLE_PYTHON_SSL_TEE=1 will it actually patch SSL sockets.
    SF_SSL_PYTHON_MODE=1 by default only disables C SSL hooks.
    """
    global _original_recv, _original_send, _original_sendall, _original_read, _original_write, _patched

    # Always log entry when SF_DEBUG is enabled
    if _SF_DEBUG:
        print(f"[ssl_socket.py] patch_ssl_sockets() CALLED - _PYTHON_SSL_TEE_ENABLED={_PYTHON_SSL_TEE_ENABLED}, _patched={_patched}, SF_ENABLE_PYTHON_SSL_TEE={os.getenv('SF_ENABLE_PYTHON_SSL_TEE', 'NOT_SET')}", log=False)

    if _patched:
        if _SF_DEBUG:
            print("[ssl_socket.py] Already patched, skipping", log=False)
        return

    # Check if Python SSL tee is enabled
    if not _PYTHON_SSL_TEE_ENABLED:
        if _SF_DEBUG:
            print("[ssl_socket.py] Python SSL tee DISABLED (SF_ENABLE_PYTHON_SSL_TEE not set to 'true')", log=False)
            print("[ssl_socket.py] SF_SSL_PYTHON_MODE=1 only disables C SSL hooks (no Python capture)", log=False)
            print("[ssl_socket.py] httpcore/requests/etc will handle their own capture instead", log=False)
        return

    if _SF_DEBUG:
        print("[ssl_socket.py] Python SSL tee ENABLED - Patching ssl.SSLSocket for tee capture", log=False)
        print("[ssl_socket.py] This should only be used for testing/debugging!", log=False)
        print(f"[ssl_socket.py] Capture config: enabled={_CAPTURE_ENABLED}, "
              f"req_headers={_CAPTURE_REQUEST_HEADERS}, req_body={_CAPTURE_REQUEST_BODY}, "
              f"resp_headers={_CAPTURE_RESPONSE_HEADERS}, resp_body={_CAPTURE_RESPONSE_BODY}", log=False)
        print(f"[ssl_socket.py] Size limits: request={_REQUEST_LIMIT_MB}MB, response={_RESPONSE_LIMIT_MB}MB", log=False)

    # Initialize fast network tracking for collectNetworkRequest emission
    init_fast_network_tracking()
    if _SF_DEBUG:
        print("[ssl_socket.py] Initialized fast network tracking for collectNetworkRequest", log=False)

    # Save originals
    _original_recv = ssl.SSLSocket.recv
    _original_send = ssl.SSLSocket.send
    _original_sendall = ssl.SSLSocket.sendall
    _original_read = ssl.SSLSocket.read
    _original_write = ssl.SSLSocket.write

    # Patch recv/send (socket interface)
    def fast_recv(self, bufsize, flags=0):
        """~15ns overhead tee wrapper"""
        if _SF_DEBUG and not hasattr(self, '_recv_logged'):
            self._recv_logged = True
            print(f"[ssl_socket.py] fast_recv: FIRST CALL on sock_id={id(self)}", log=False)
        data = _original_recv(self, bufsize, flags)
        if data:
            _tee_capture(self, data, 'RX')
        return data

    def fast_send(self, data, flags=0):
        """~15ns overhead tee wrapper"""
        if _SF_DEBUG and not hasattr(self, '_send_logged'):
            self._send_logged = True
            print(f"[ssl_socket.py] fast_send: FIRST CALL on sock_id={id(self)}, sending {len(data)} bytes", log=False)
        result = _original_send(self, data, flags)
        if result > 0:
            _tee_capture(self, data[:result], 'TX')
        return result

    def fast_sendall(self, data):
        """~15ns overhead tee wrapper for sendall()"""
        # sendall() doesn't return number of bytes sent, it sends all or raises exception
        if _SF_DEBUG and not hasattr(self, '_sendall_logged'):
            self._sendall_logged = True
            print(f"[ssl_socket.py] fast_sendall: FIRST CALL on sock_id={id(self)}, sending {len(data)} bytes", log=False)
        _original_sendall(self, data)
        # If we get here, all data was sent
        _tee_capture(self, data, 'TX')
        return None  # sendall returns None on success

    # Patch read/write (file interface)
    def fast_read(self, len=1024, buffer=None):
        """~15ns overhead tee wrapper"""
        if _SF_DEBUG and not hasattr(self, '_read_logged'):
            self._read_logged = True
            print(f"[ssl_socket.py] fast_read: FIRST CALL on sock_id={id(self)}", log=False)
        data = _original_read(self, len, buffer)
        if buffer is not None:
            # readinto mode: data is int (bytes read), actual data is in buffer
            if data and isinstance(data, int) and data > 0:
                # Extract bytes from buffer for capture
                captured_data = bytes(buffer[:data])
                _tee_capture(self, captured_data, 'RX')
        elif data:
            # Normal mode: data is bytes
            _tee_capture(self, data, 'RX')
        return data

    def fast_write(self, data):
        """~15ns overhead tee wrapper"""
        if _SF_DEBUG and not hasattr(self, '_write_logged'):
            self._write_logged = True
            print(f"[ssl_socket.py] fast_write: FIRST CALL on sock_id={id(self)}, writing {len(data)} bytes", log=False)
        result = _original_write(self, data)
        if result > 0:
            _tee_capture(self, data[:result], 'TX')
        return result

    # Apply patches
    ssl.SSLSocket.recv = fast_recv
    ssl.SSLSocket.send = fast_send
    ssl.SSLSocket.sendall = fast_sendall
    ssl.SSLSocket.read = fast_read
    ssl.SSLSocket.write = fast_write

    # Cache peername on connect to avoid repeated syscalls on hot path
    _patch_ssl_connect()

    # Start background processor
    _start_background_processor()

    _patched = True

    if _SF_DEBUG:
        print("[ssl_socket.py] ✓ SSL patching complete - all HTTPS traffic will be captured automatically", log=False)
        print("[ssl_socket.py]   Patched methods: recv, send, sendall, read, write", log=False)
        print("[ssl_socket.py]   requests, httpx, urllib3, aiohttp all use ssl.SSLSocket underneath", log=False)


def _patch_ssl_connect():
    """Cache peername after SSL handshake to avoid syscalls on hot path"""
    original_do_handshake = ssl.SSLSocket.do_handshake

    def cached_do_handshake(self):
        result = original_do_handshake(self)
        try:
            self._peername_cache = self.getpeername()
        except Exception:
            pass
        return result

    ssl.SSLSocket.do_handshake = cached_do_handshake


# ============================================================================
# BACKGROUND PROCESSING (Zero hot path impact)
# ============================================================================

_background_thread = None
_background_event = threading.Event()
_background_running = False
_sock_aggregators = {}  # sock_id -> HTTPAggregator


class HTTPAggregator:
    """Aggregates captured bytes into complete HTTP transactions"""

    def __init__(self, sock_id):
        self.sock_id = sock_id
        self.tx_buffer = bytearray()
        self.rx_buffer = bytearray()
        self.current_transaction = None
        self.last_activity = time.time()
        self.peername = None
        self._first_feed_logged = False  # Debug flag

    def feed(self, data, direction, peername=None):
        """Feed captured data, parse when complete"""
        # Early exit if capture is disabled globally
        if not _CAPTURE_ENABLED:
            return

        # Debug: Log first feed for this socket
        if _SF_DEBUG and not self._first_feed_logged:
            self._first_feed_logged = True
            print(f"[ssl_socket.py] HTTPAggregator.feed: FIRST FEED sock_id={self.sock_id}, direction={direction}, size={len(data)} bytes", log=False)

        if peername:
            self.peername = peername

        if direction == 'TX':
            # Only buffer request data if we're capturing headers or body
            if _CAPTURE_REQUEST_HEADERS or _CAPTURE_REQUEST_BODY:
                self.tx_buffer.extend(data)
                if _SF_DEBUG:
                    print(f"[ssl_socket.py] HTTPAggregator.feed: TX buffer now {len(self.tx_buffer)} bytes, calling _try_parse_request()", log=False)
                self._try_parse_request()
        else:  # RX
            # Only buffer response data if we're capturing headers or body
            if _CAPTURE_RESPONSE_HEADERS or _CAPTURE_RESPONSE_BODY:
                self.rx_buffer.extend(data)
                if _SF_DEBUG:
                    print(f"[ssl_socket.py] HTTPAggregator.feed: RX buffer now {len(self.rx_buffer)} bytes, calling _try_parse_response()", log=False)
                self._try_parse_response()

        self.last_activity = time.time()

    def _try_parse_request(self):
        """Try to parse complete HTTP request from buffer"""
        # Look for \r\n\r\n (end of headers)
        headers_end = self.tx_buffer.find(b'\r\n\r\n')
        if headers_end == -1:
            if _SF_DEBUG and len(self.tx_buffer) > 0:
                print(f"[ssl_socket.py] _try_parse_request: Incomplete headers (buffer={len(self.tx_buffer)} bytes, waiting for \\r\\n\\r\\n)", log=False)
            return  # Incomplete headers

        try:
            headers = self.tx_buffer[:headers_end].decode('latin-1', errors='ignore')
        except Exception:
            return

        if _SF_DEBUG:
            preview = headers if len(headers) < 1000 else headers[:1000] + "...<truncated>"
            print(f"[ssl_socket.py] RAW REQUEST HEADERS:\n{preview}", log=False)

        lines = headers.split('\r\n')

        if not lines:
            return

        # Parse request line
        request_line = lines[0].split(' ', 2)
        if len(request_line) < 3:
            return

        method, target, version = request_line

        # Parse headers
        host = None
        content_length = 0
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip().lower()
                value = value.strip()
                if key == 'host':
                    host = value
                elif key == 'content-length':
                    try:
                        content_length = int(value)
                    except ValueError:
                        pass

        # Use peername as fallback for host
        if not host and self.peername:
            host = f"{self.peername[0]}:{self.peername[1]}"

        # Check if body complete
        body_start = headers_end + 4
        body_available = len(self.tx_buffer) - body_start

        # Capture up to configured limit
        body_capture_limit = MAX_REQUEST_BODY_CAPTURE if _CAPTURE_REQUEST_BODY else 0
        expected_body_size = min(content_length, body_capture_limit) if _CAPTURE_REQUEST_BODY else 0

        if body_available >= expected_body_size:
            # Request complete!
            body = self.tx_buffer[body_start:body_start + expected_body_size] if _CAPTURE_REQUEST_BODY else b''

            self.current_transaction = {
                'method': method,
                'target': target,
                'host': host or 'unknown',
                'req_headers': headers if _CAPTURE_REQUEST_HEADERS else '',
                'req_body': bytes(body),
                't_start': time.perf_counter_ns()
            }

            if _SF_DEBUG:
                print(f"[ssl_socket.py] _try_parse_request: REQUEST COMPLETE - {method} {host}{target}, waiting for response", log=False)
                print(f"[ssl_socket.py] _try_parse_request: Captured req_headers_len={len(headers) if _CAPTURE_REQUEST_HEADERS else 0}, req_body_len={len(body)}", log=False)
                if _CAPTURE_REQUEST_HEADERS and len(headers) > 0:
                    header_lines = headers.split('\r\n')[:5]  # First 5 lines
                    print(f"[ssl_socket.py] _try_parse_request: First headers lines: {header_lines}", log=False)

            # Clear buffer
            self.tx_buffer.clear()

    def _try_parse_response(self):
        """Try to parse complete HTTP response from buffer"""
        if not self.current_transaction:
            if _SF_DEBUG and len(self.rx_buffer) > 0:
                print(f"[ssl_socket.py] _try_parse_response: No current transaction (received response without request?), buffer={len(self.rx_buffer)} bytes", log=False)
            return  # No request to match

        # Look for \r\n\r\n
        headers_end = self.rx_buffer.find(b'\r\n\r\n')
        if headers_end == -1:
            if _SF_DEBUG and len(self.rx_buffer) > 0:
                print(f"[ssl_socket.py] _try_parse_response: Incomplete headers (buffer={len(self.rx_buffer)} bytes, waiting for \\r\\n\\r\\n)", log=False)
            return

        try:
            headers = self.rx_buffer[:headers_end].decode('latin-1', errors='ignore')
        except Exception:
            return

        lines = headers.split('\r\n')

        if not lines:
            return

        # Parse status line
        status_line = lines[0].split(' ', 2)
        status = 0
        if len(status_line) >= 2:
            try:
                status = int(status_line[1])
            except ValueError:
                pass

        # Parse content-length
        content_length = 0
        for line in lines[1:]:
            if ':' in line:
                key, value = line.split(':', 1)
                if key.strip().lower() == 'content-length':
                    try:
                        content_length = int(value.strip())
                    except ValueError:
                        pass

        # Check if body complete (capture up to configured limit)
        body_start = headers_end + 4
        body_available = len(self.rx_buffer) - body_start

        # Capture up to configured limit
        body_capture_limit = MAX_RESPONSE_BODY_CAPTURE if _CAPTURE_RESPONSE_BODY else 0
        expected_body_size = min(content_length, body_capture_limit) if _CAPTURE_RESPONSE_BODY else 0

        if body_available >= expected_body_size:
            # Response complete!
            body = self.rx_buffer[body_start:body_start + expected_body_size] if _CAPTURE_RESPONSE_BODY else b''

            self.current_transaction.update({
                'status': status,
                'resp_headers': headers if _CAPTURE_RESPONSE_HEADERS else '',
                'resp_body': bytes(body),
                't_end': time.perf_counter_ns()
            })

            if _SF_DEBUG:
                method = self.current_transaction.get('method', 'UNKNOWN')
                host = self.current_transaction.get('host', 'unknown')
                target = self.current_transaction.get('target', '/')
                print(f"[ssl_socket.py] _try_parse_response: RESPONSE COMPLETE - {method} {host}{target} -> status={status}, pushing to ring", log=False)
                print(f"[ssl_socket.py] _try_parse_response: Captured resp_headers_len={len(headers) if _CAPTURE_RESPONSE_HEADERS else 0}, resp_body_len={len(body)}", log=False)
                if _CAPTURE_RESPONSE_HEADERS and len(headers) > 0:
                    header_lines = headers.split('\r\n')[:5]  # First 5 lines
                    print(f"[ssl_socket.py] _try_parse_response: First headers lines: {header_lines}", log=False)
                if len(body) > 0:
                    print(f"[ssl_socket.py] _try_parse_response: Body preview: {body[:100]}", log=False)

            # Push to C ring
            _push_transaction_to_c_ring(self.current_transaction)

            # Clear state
            self.current_transaction = None
            self.rx_buffer.clear()


def _background_processor():
    """Background thread that aggregates and pushes to C ring"""
    global _background_running
    _background_running = True

    if _SF_DEBUG:
        print("[ssl_socket.py] Background processor started", log=False)

    items_processed = 0  # Debug counter

    while _background_running:
        _background_event.wait(timeout=0.01)  # 10ms or on signal
        _background_event.clear()

        # Drain all capture queues
        batch_count = 0
        for tid, queue in list(_capture_queues.items()):
            while queue:
                try:
                    item = queue.popleft()
                    sock_id = item['sock_id']
                    batch_count += 1

                    # Get or create aggregator for this socket
                    if sock_id not in _sock_aggregators:
                        _sock_aggregators[sock_id] = HTTPAggregator(sock_id)
                        if _SF_DEBUG:
                            print(f"[ssl_socket.py] _background_processor: Created new aggregator for sock_id={sock_id}", log=False)

                    agg = _sock_aggregators[sock_id]
                    agg.feed(item['data'], item['direction'], item.get('peername'))

                except Exception as e:
                    if _SF_DEBUG:
                        print(f"[ssl_socket.py] Background processing error: {e}", log=False)

        # Debug: Log processing activity
        if _SF_DEBUG and batch_count > 0:
            items_processed += batch_count
            print(f"[ssl_socket.py] _background_processor: Processed {batch_count} items (total: {items_processed})", log=False)

        # Cleanup stale aggregators (>30s idle)
        now = time.time()
        stale = [sid for sid, agg in _sock_aggregators.items()
                 if now - agg.last_activity > 30]
        for sid in stale:
            del _sock_aggregators[sid]


def _start_background_processor():
    """Start background processor thread"""
    global _background_thread
    if _background_thread is None:
        _background_thread = threading.Thread(
            target=_background_processor,
            daemon=True,
            name='ssl_capture_processor'
        )
        _background_thread.start()


# ============================================================================
# C RING BRIDGE (Called from background thread only)
# ============================================================================

_c_lib = None


def _init_c_bridge():
    """Initialize ctypes bridge to C ring buffer"""
    global _c_lib

    if not _C_RING_AVAILABLE:
        if _SF_DEBUG:
            print("[ssl_socket.py] C ring not available (SF_SSL_PYTHON_MODE not set)", log=False)
        return False

    try:
        # Try to load the library
        import sf_veritas
        lib_path = os.path.join(os.path.dirname(sf_veritas.__file__), 'libsfnettee.so')

        if not os.path.exists(lib_path):
            if _SF_DEBUG:
                print(f"[ssl_socket.py] libsfnettee.so not found at {lib_path}", log=False)
            return False

        _c_lib = ctypes.CDLL(lib_path)

        # Define function signature
        _c_lib.sf_ring_push_from_python.argtypes = [
            ctypes.c_char_p,  # req_method
            ctypes.c_char_p,  # req_target
            ctypes.c_char_p,  # req_host
            ctypes.c_char_p,  # req_headers
            ctypes.c_char_p,  # req_body
            ctypes.c_size_t,  # req_body_len
            ctypes.c_char_p,  # resp_headers
            ctypes.c_char_p,  # resp_body
            ctypes.c_size_t,  # resp_body_len
            ctypes.c_int,     # resp_status
            ctypes.c_uint64,  # t_start_ns
            ctypes.c_uint64,  # t_end_ns
            ctypes.c_char_p,  # parent_trace_id
            ctypes.c_int,     # is_ssl
        ]
        _c_lib.sf_ring_push_from_python.restype = ctypes.c_int

        if _SF_DEBUG:
            print("[ssl_socket.py] ✓ C ring bridge initialized successfully", log=False)

        return True

    except Exception as e:
        if _SF_DEBUG:
            print(f"[ssl_socket.py] Failed to init C bridge: {e}", log=False)
        return False


def _debug_log_sf_header_anomalies(raw_headers: str) -> None:
    """Log duplicate or mismatched Sailfish headers when SF_DEBUG enabled."""
    if not (_SF_DEBUG and raw_headers):
        return

    sf3_values = []
    sf4_values = []
    for line in raw_headers.split('\r\n'):
        if not line or ':' not in line:
            continue
        key, value = line.split(':', 1)
        key_strip = key.strip()
        value_strip = value.strip()
        key_lower = key_strip.lower()
        if key_lower == 'x-sf3-rid':
            sf3_values.append((key_strip, value_strip))
        elif key_lower == 'x-sf4-prid':
            sf4_values.append((key_strip, value_strip))

    if len(sf3_values) > 1:
        print(f"[ssl_socket.py] ⚠️ Multiple X-Sf3-Rid headers detected: {sf3_values}", log=False)
    if len(sf4_values) > 1:
        print(f"[ssl_socket.py] ⚠️ Multiple X-Sf4-Prid headers detected: {sf4_values}", log=False)
    if sf3_values and sf4_values and sf3_values[0][1] == sf4_values[0][1]:
        print(
            "[ssl_socket.py] ⚠️ X-Sf3-Rid matches X-Sf4-Prid "
            f"(possible parent propagation) sf3={sf3_values} sf4={sf4_values}",
            log=False,
        )


def _push_transaction_to_c_ring(transaction: Dict[str, Any]):
    """
    Emit collectNetworkRequest mutation via record_network_request().
    Respects SF_NETWORKREQUEST_CAPTURE_* environment variables.

    NOTE: This now uses record_network_request() instead of sf_ring_push_from_python()
    to emit the standard collectNetworkRequest mutation like other library patches.
    """
    # Early exit if capture is disabled
    if not _CAPTURE_ENABLED:
        if _SF_DEBUG:
            print(f"[ssl_socket.py] _push_transaction_to_c_ring: capture disabled, skipping", log=False)
        return

    if _SF_DEBUG:
        method = transaction.get('method', 'UNKNOWN')
        host = transaction.get('host', 'unknown')
        target = transaction.get('target', '/')
        status = transaction.get('status', 0)
        print(f"[ssl_socket.py] _push_transaction_to_c_ring: DATA RECEIVED - {method} {host}{target} -> status={status}", log=False)

    try:
        # Extract trace_id from X-Sf3-Rid header (injected by outbound header manager)
        trace_id = ""
        req_headers_str = transaction.get('req_headers', '')
        if req_headers_str:
            _debug_log_sf_header_anomalies(req_headers_str)
            # Parse X-Sf3-Rid header from raw HTTP headers
            for line in req_headers_str.split('\r\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    if key.strip().lower() == 'x-sf3-rid':
                        trace_id = value.strip()
                        break

        # Build full URL (SSL socket only captures HTTPS)
        host = transaction.get('host', 'unknown')
        target = transaction.get('target', '/')
        url = f"https://{host}{target}"

        # Convert headers from raw HTTP format to JSON dict
        import json
        try:
            import orjson
            HAS_ORJSON = True
        except ImportError:
            HAS_ORJSON = False

        def parse_http_headers(headers_str: str) -> bytes:
            """Parse raw HTTP headers into JSON dict."""
            if not headers_str:
                return b"{}"
            headers_dict = {}
            for line in headers_str.split('\r\n')[1:]:  # Skip request/status line
                if ':' in line:
                    key, value = line.split(':', 1)
                    headers_dict[key.strip()] = value.strip()
            if HAS_ORJSON:
                return orjson.dumps(headers_dict)
            else:
                return json.dumps(headers_dict).encode('utf-8')

        # Prepare data based on capture flags
        req_headers_json = parse_http_headers(req_headers_str) if _CAPTURE_REQUEST_HEADERS else b'{}'
        req_body = transaction.get('req_body', b'') if _CAPTURE_REQUEST_BODY else b''

        resp_headers_str = transaction.get('resp_headers', '')
        resp_headers_json = parse_http_headers(resp_headers_str) if _CAPTURE_RESPONSE_HEADERS else b'{}'
        resp_body = transaction.get('resp_body', b'') if _CAPTURE_RESPONSE_BODY else b''

        # Enforce size limits (already enforced during parsing, but double-check)
        if len(req_body) > MAX_REQUEST_BODY_CAPTURE:
            req_body = req_body[:MAX_REQUEST_BODY_CAPTURE]
        if len(resp_body) > MAX_RESPONSE_BODY_CAPTURE:
            resp_body = resp_body[:MAX_RESPONSE_BODY_CAPTURE]

        # Convert timestamps from nanoseconds to milliseconds
        timestamp_start = transaction['t_start'] // 1_000_000  # ns to ms
        timestamp_end = transaction.get('t_end', transaction['t_start']) // 1_000_000  # ns to ms

        # Get status and determine success
        status = transaction.get('status', 0)
        success = status > 0 and status < 400

        if _SF_DEBUG:
            print(f"[ssl_socket.py] PREPARING TO SEND collectNetworkRequest:", log=False)
            print(f"[ssl_socket.py]   url={url} (type={type(url).__name__})", log=False)
            print(f"[ssl_socket.py]   method={transaction['method']} (type={type(transaction['method']).__name__})", log=False)
            print(f"[ssl_socket.py]   status_code={status}", log=False)
            print(f"[ssl_socket.py]   success={success}", log=False)
            print(f"[ssl_socket.py]   trace_id={trace_id}", log=False)
            print(f"[ssl_socket.py]   request_headers_size={len(req_headers_json)} bytes", log=False)
            print(f"[ssl_socket.py]   request_body_size={len(req_body)} bytes", log=False)
            print(f"[ssl_socket.py]   response_headers_size={len(resp_headers_json)} bytes", log=False)
            print(f"[ssl_socket.py]   response_body_size={len(resp_body)} bytes", log=False)
            print(f"[ssl_socket.py]   timestamp_start={timestamp_start}ms", log=False)
            print(f"[ssl_socket.py]   timestamp_end={timestamp_end}ms", log=False)
            # Show first 200 chars of headers/body for debugging
            if len(req_headers_json) > 2:
                print(f"[ssl_socket.py]   req_headers_preview={req_headers_json[:200]}", log=False)
            if len(resp_headers_json) > 2:
                print(f"[ssl_socket.py]   resp_headers_preview={resp_headers_json[:200]}", log=False)
            if len(req_body) > 0:
                print(f"[ssl_socket.py]   req_body_preview={req_body[:100]}", log=False)
            if len(resp_body) > 0:
                print(f"[ssl_socket.py]   resp_body_preview={resp_body[:100]}", log=False)

        # Emit collectNetworkRequest mutation
        record_network_request(
            trace_id=trace_id,
            url=url,
            method=transaction['method'],
            status_code=status,
            success=success,
            timestamp_start=timestamp_start,
            timestamp_end=timestamp_end,
            request_data=req_body,
            response_data=resp_body,
            request_headers=req_headers_json,
            response_headers=resp_headers_json,
        )

        if _SF_DEBUG:
            print(f"[ssl_socket.py] ✓ SUCCESSFULLY SENT collectNetworkRequest for {transaction['method']} {url} (status={status})", log=False)

    except Exception as e:
        if _SF_DEBUG:
            print(f"[ssl_socket.py] Failed to emit collectNetworkRequest: {e}", log=False)
