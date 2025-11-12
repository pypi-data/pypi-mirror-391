"""
Auto-detection and configuration of LD_PRELOAD mode.

This module automatically detects if libsfnettee.so is available in the package
and sets the LD_PRELOAD environment variable if it's not already set. This enables
LD_PRELOAD mode automatically without requiring manual configuration.
"""

import os
import sys


def _auto_enable_ld_preload() -> bool:
    """
    Check if LD_PRELOAD mode is active.

    This function checks if the C library (libsfnettee.so) is loaded via LD_PRELOAD.
    It does NOT attempt to automatically enable it - users must set LD_PRELOAD themselves.

    To enable high-performance C library mode, set LD_PRELOAD before starting Python:
        export LD_PRELOAD=/path/to/site-packages/sf_veritas/libsfnettee.so
        python your_app.py

    Or in your Dockerfile entrypoint:
        ENV LD_PRELOAD=/usr/local/lib/python3.12/site-packages/sf_veritas/libsfnettee.so

    Returns:
        True if LD_PRELOAD mode is active (C library loaded)
        False if not active (will use Python patches)
    """
    # Check if LD_PRELOAD is already set with libsfnettee.so
    current_ld_preload = os.getenv("LD_PRELOAD", "")
    if "libsfnettee.so" in current_ld_preload or "_sfteepreload" in current_ld_preload:
        if os.getenv("SF_DEBUG", "false").lower() == "true":
            sys.stderr.write(f"[sf_veritas] ✓ C library active via LD_PRELOAD: {current_ld_preload}\n")
            sys.stderr.flush()
        return True

    # Not active - check if library exists and print helpful message
    try:
        package_dir = os.path.dirname(os.path.abspath(__file__))
        libsfnettee_path = os.path.join(package_dir, "libsfnettee.so")

        if os.path.isfile(libsfnettee_path):
            if os.getenv("SF_DEBUG", "false").lower() == "true":
                sys.stderr.write(f"[sf_veritas] C library available but not loaded (using Python patches)\n")
                sys.stderr.write(f"[sf_veritas] For better performance, set LD_PRELOAD before starting Python:\n")
                sys.stderr.write(f"[sf_veritas]   export LD_PRELOAD={libsfnettee_path}\n")
                sys.stderr.flush()
        else:
            if os.getenv("SF_DEBUG", "false").lower() == "true":
                sys.stderr.write(f"[sf_veritas] C library not found at {libsfnettee_path}\n")
                sys.stderr.write(f"[sf_veritas] Using Python patches (slower but works)\n")
                sys.stderr.flush()
    except Exception:
        pass

    return False


# Check if LD_PRELOAD mode is active
_LD_PRELOAD_ACTIVE = _auto_enable_ld_preload()

# Enable Python SSL mode when LD_PRELOAD is active (default ON)
# This tells the C library to disable its SSL hooks (Python handles HTTPS, C handles HTTP)
if _LD_PRELOAD_ACTIVE:
    # Default to '1' (C SSL hooks disabled) unless explicitly overridden
    if 'SF_SSL_PYTHON_MODE' not in os.environ:
        os.environ['SF_SSL_PYTHON_MODE'] = '1'

    if os.getenv("SF_DEBUG", "false").lower() == "true":
        sys.stderr.write("[sf_veritas] ✓ Python SSL mode enabled (C handles HTTP, Python handles HTTPS)\n")
        sys.stderr.flush()
