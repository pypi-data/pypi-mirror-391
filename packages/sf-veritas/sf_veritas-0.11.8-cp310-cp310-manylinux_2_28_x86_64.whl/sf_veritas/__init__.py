# Note: LD_PRELOAD must be set manually by user for C library mode
# The C library (libsfnettee.so) is available but requires explicit LD_PRELOAD configuration

# Install C-level crash handler FIRST (catches crashes before Python can)
import sys
try:
    sys.stderr.write("[__init__] Attempting to load C crash handler...\n")
    sys.stderr.flush()
    from . import _sfcrashhandler
    sys.stderr.write("[__init__] C crash handler module loaded, installing...\n")
    sys.stderr.flush()
    _sfcrashhandler.install()
    sys.stderr.write("[__init__] C crash handler installed successfully\n")
    sys.stderr.flush()
except Exception as e:
    import traceback
    sys.stderr.write(f"[WARNING] Failed to install C crash handler: {e}\n")
    traceback.print_exc(file=sys.stderr)
    sys.stderr.flush()

# Install Python-level segfault handler as backup
try:
    from . import segfault_handler  # noqa: F401
except Exception:
    pass  # Silently fail if handler can't be installed

from .function_span_profiler import (
    skip_tracing,  # Backward compatibility
    skip_function_tracing,
    skip_network_tracing,
    capture_function_spans,
)
from .package_metadata import __version__
from .transmit_exception_to_sailfish import transmit_exception_to_sailfish
from .unified_interceptor import setup_interceptors, reinitialize_after_fork

__all__ = [
    "setup_interceptors",
    "transmit_exception_to_sailfish",
    "skip_tracing",  # Backward compatibility
    "skip_function_tracing",
    "skip_network_tracing",
    "capture_function_spans",
    "reinitialize_after_fork",
    "__version__",
]
