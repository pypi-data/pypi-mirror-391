"""
Signal handler to print detailed crash information before core dump.

Import this module EARLY in your application to register handlers.
"""
import faulthandler
import signal
import sys
import traceback
import os


def detailed_segfault_handler(signum, frame):
    """
    Print detailed crash information when segfault occurs.
    This runs BEFORE the default handler, so we get both Python trace and core dump.
    """
    sig_name = signal.Signals(signum).name
    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print(f"SEGFAULT DETECTED: Signal {signum} ({sig_name})", file=sys.stderr, flush=True)
    print(f"{'='*80}", file=sys.stderr, flush=True)

    # Print process info
    print(f"\nProcess ID: {os.getpid()}", file=sys.stderr, flush=True)
    print(f"Thread ID: {threading.get_ident()}", file=sys.stderr, flush=True)

    # Print Python stack trace for current thread
    print(f"\n{'-'*80}", file=sys.stderr, flush=True)
    print("Python Stack Trace (Current Thread):", file=sys.stderr, flush=True)
    print(f"{'-'*80}", file=sys.stderr, flush=True)
    traceback.print_stack(frame, file=sys.stderr)

    # Print all threads
    print(f"\n{'-'*80}", file=sys.stderr, flush=True)
    print("All Thread Stack Traces:", file=sys.stderr, flush=True)
    print(f"{'-'*80}", file=sys.stderr, flush=True)
    faulthandler.dump_traceback(file=sys.stderr, all_threads=True)

    # Print frame locals if available
    if frame is not None:
        print(f"\n{'-'*80}", file=sys.stderr, flush=True)
        print("Frame Locals:", file=sys.stderr, flush=True)
        print(f"{'-'*80}", file=sys.stderr, flush=True)
        try:
            for key, value in frame.f_locals.items():
                try:
                    print(f"  {key} = {repr(value)[:200]}", file=sys.stderr, flush=True)
                except:
                    print(f"  {key} = <error printing value>", file=sys.stderr, flush=True)
        except:
            print("  <error accessing frame locals>", file=sys.stderr, flush=True)

    # Print frame globals (top-level only, to avoid spam)
    if frame is not None:
        print(f"\n{'-'*80}", file=sys.stderr, flush=True)
        print("Frame Globals (selected):", file=sys.stderr, flush=True)
        print(f"{'-'*80}", file=sys.stderr, flush=True)
        try:
            important_globals = ['__name__', '__file__']
            for key in important_globals:
                if key in frame.f_globals:
                    try:
                        value = frame.f_globals[key]
                        print(f"  {key} = {repr(value)[:200]}", file=sys.stderr, flush=True)
                    except:
                        print(f"  {key} = <error printing value>", file=sys.stderr, flush=True)
        except:
            print("  <error accessing frame globals>", file=sys.stderr, flush=True)

    print(f"\n{'='*80}", file=sys.stderr, flush=True)
    print("Core dump location: /tmp/core.*", file=sys.stderr, flush=True)
    print(f"{'='*80}\n", file=sys.stderr, flush=True)
    sys.stderr.flush()

    # Chain to default handler (will generate core dump)
    signal.signal(signum, signal.SIG_DFL)
    os.kill(os.getpid(), signum)


def install_segfault_handler():
    """
    Install enhanced segfault handler.
    Call this EARLY in your application startup.
    """
    import threading

    # Enable Python's built-in faulthandler (as backup)
    faulthandler.enable(file=sys.stderr, all_threads=True)

    # Register our custom handler for SIGSEGV
    signal.signal(signal.SIGSEGV, detailed_segfault_handler)

    # Also register for SIGABRT (assertion failures, etc)
    signal.signal(signal.SIGABRT, detailed_segfault_handler)

    # Register for SIGBUS (bus error - alignment issues)
    try:
        signal.signal(signal.SIGBUS, detailed_segfault_handler)
    except AttributeError:
        pass  # SIGBUS not available on all platforms

    print("[segfault_handler] Enhanced crash handlers installed", file=sys.stderr, flush=True)
    print(f"[segfault_handler] PID: {os.getpid()}", file=sys.stderr, flush=True)


# Auto-install on import if SF_DEBUG_BUILD is set
if os.getenv("SF_DEBUG_BUILD", "0") == "1" or os.getenv("SF_DEBUG", "false").lower() == "true":
    try:
        import threading
        install_segfault_handler()
    except Exception as e:
        print(f"[segfault_handler] WARNING: Failed to install handler: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
else:
    print(f"[segfault_handler] Not installing (SF_DEBUG_BUILD={os.getenv('SF_DEBUG_BUILD', '0')}, SF_DEBUG={os.getenv('SF_DEBUG', 'false')})", file=sys.stderr)
