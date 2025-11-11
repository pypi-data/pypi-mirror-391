"""
Helper script to get the LD_PRELOAD path for the C library.

Usage:
    # In your shell:
    export LD_PRELOAD=$(python -m sf_veritas.get_preload_path)
    python your_app.py

    # Or in your Dockerfile:
    ENV LD_PRELOAD=/usr/local/lib/python3.12/site-packages/sf_veritas/libsfnettee.so
"""
import os
import sys


def get_preload_path():
    """Get the full path to libsfnettee.so"""
    package_dir = os.path.dirname(os.path.abspath(__file__))
    libsfnettee_path = os.path.join(package_dir, "libsfnettee.so")

    if os.path.isfile(libsfnettee_path):
        return libsfnettee_path
    else:
        return None


if __name__ == "__main__":
    path = get_preload_path()
    if path:
        print(path)
        sys.exit(0)
    else:
        sys.stderr.write("Error: libsfnettee.so not found\n")
        sys.exit(1)
