// C-level crash handler that prints registers and stack addresses
// This catches segfaults that happen in C code before Python can handle them

// Ensure we have write() and fsync() available
#ifndef _POSIX_C_SOURCE
#define _POSIX_C_SOURCE 200809L
#endif

#include <Python.h>
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <ucontext.h>
#include <execinfo.h>
#include <sys/types.h>
#include <sys/syscall.h>

// Get thread ID
static long gettid(void) {
#ifdef SYS_gettid
    return (long)syscall(SYS_gettid);
#else
    return (long)getpid();
#endif
}

// Signal handler that prints everything
static void crash_handler(int sig, siginfo_t *si, void *ctx) {
    ucontext_t *uc = (ucontext_t *)ctx;
    void *backtrace_buffer[100];
    int backtrace_size;
    char **bt_symbols;
    int i;

    // Make stderr unbuffered to ensure output appears
    setvbuf(stderr, NULL, _IONBF, 0);

    // Print to stderr directly (unbuffered)
    const char *sig_name =
        sig == SIGSEGV ? "SIGSEGV" :
        sig == SIGABRT ? "SIGABRT" :
        sig == SIGBUS  ? "SIGBUS" :
        sig == SIGFPE  ? "SIGFPE" :
        sig == SIGILL  ? "SIGILL" : "UNKNOWN";

    // Write directly to fd 2 (stderr) to bypass buffering entirely
    const char *header = "\n\n=== CRASH HANDLER TRIGGERED ===\n";
    write(2, header, strlen(header));

    fprintf(stderr, "\n");
    fprintf(stderr, "================================================================================\n");
    fprintf(stderr, "CRASH DETECTED: Signal %d (%s)\n", sig, sig_name);
    fprintf(stderr, "================================================================================\n");
    fprintf(stderr, "Process ID:  %d\n", getpid());
    fprintf(stderr, "Thread ID:   %ld\n", gettid());
    fprintf(stderr, "Signal code: %d\n", si->si_code);
    fprintf(stderr, "Fault addr:  %p\n", si->si_addr);
    fprintf(stderr, "\n");

    // Print registers (platform-specific)
#ifdef __x86_64__
    fprintf(stderr, "--- x86_64 Registers ---\n");
    fprintf(stderr, "RIP: 0x%016llx  RSP: 0x%016llx  RBP: 0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.gregs[REG_RIP],
            (unsigned long long)uc->uc_mcontext.gregs[REG_RSP],
            (unsigned long long)uc->uc_mcontext.gregs[REG_RBP]);
    fprintf(stderr, "RAX: 0x%016llx  RBX: 0x%016llx  RCX: 0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.gregs[REG_RAX],
            (unsigned long long)uc->uc_mcontext.gregs[REG_RBX],
            (unsigned long long)uc->uc_mcontext.gregs[REG_RCX]);
    fprintf(stderr, "RDX: 0x%016llx  RSI: 0x%016llx  RDI: 0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.gregs[REG_RDX],
            (unsigned long long)uc->uc_mcontext.gregs[REG_RSI],
            (unsigned long long)uc->uc_mcontext.gregs[REG_RDI]);
    fprintf(stderr, "R8:  0x%016llx  R9:  0x%016llx  R10: 0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.gregs[REG_R8],
            (unsigned long long)uc->uc_mcontext.gregs[REG_R9],
            (unsigned long long)uc->uc_mcontext.gregs[REG_R10]);
    fprintf(stderr, "R11: 0x%016llx  R12: 0x%016llx  R13: 0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.gregs[REG_R11],
            (unsigned long long)uc->uc_mcontext.gregs[REG_R12],
            (unsigned long long)uc->uc_mcontext.gregs[REG_R13]);
    fprintf(stderr, "R14: 0x%016llx  R15: 0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.gregs[REG_R14],
            (unsigned long long)uc->uc_mcontext.gregs[REG_R15]);
#elif defined(__aarch64__)
    fprintf(stderr, "--- ARM64 Registers ---\n");
    fprintf(stderr, "PC:  0x%016llx  SP:  0x%016llx  FP:  0x%016llx\n",
            (unsigned long long)uc->uc_mcontext.pc,
            (unsigned long long)uc->uc_mcontext.sp,
            (unsigned long long)uc->uc_mcontext.regs[29]);
    for (i = 0; i < 29; i += 3) {
        fprintf(stderr, "X%-2d: 0x%016llx  ", i, (unsigned long long)uc->uc_mcontext.regs[i]);
        if (i + 1 < 29)
            fprintf(stderr, "X%-2d: 0x%016llx  ", i+1, (unsigned long long)uc->uc_mcontext.regs[i+1]);
        if (i + 2 < 29)
            fprintf(stderr, "X%-2d: 0x%016llx", i+2, (unsigned long long)uc->uc_mcontext.regs[i+2]);
        fprintf(stderr, "\n");
    }
#else
    fprintf(stderr, "--- Registers (architecture not recognized) ---\n");
#endif
    fprintf(stderr, "\n");

    // Print native backtrace
    fprintf(stderr, "--- Native Stack Trace (C level) ---\n");
    backtrace_size = backtrace(backtrace_buffer, 100);
    bt_symbols = backtrace_symbols(backtrace_buffer, backtrace_size);

    if (bt_symbols) {
        for (i = 0; i < backtrace_size; i++) {
            fprintf(stderr, "[%2d] %s\n", i, bt_symbols[i]);
        }
        free(bt_symbols);
    } else {
        fprintf(stderr, "Failed to get backtrace symbols\n");
    }
    fprintf(stderr, "\n");

    // Print raw stack memory
    fprintf(stderr, "--- Stack Memory (32 bytes from fault) ---\n");
    unsigned char *fault_ptr = (unsigned char *)si->si_addr;
    fprintf(stderr, "Fault address: %p\n", fault_ptr);

    // Try to read memory around fault address (may fail)
    // Print stack pointer area instead
#ifdef __x86_64__
    unsigned long long *sp = (unsigned long long *)uc->uc_mcontext.gregs[REG_RSP];
#elif defined(__aarch64__)
    unsigned long long *sp = (unsigned long long *)uc->uc_mcontext.sp;
#else
    unsigned long long *sp = NULL;
#endif

    if (sp) {
        fprintf(stderr, "Stack at RSP/SP (%p):\n", sp);
        for (i = 0; i < 4; i++) {
            fprintf(stderr, "  [SP+%2d] 0x%016llx\n", i*8, (unsigned long long)sp[i]);
        }
    }
    fprintf(stderr, "\n");

    fprintf(stderr, "================================================================================\n");
    fprintf(stderr, "Use addr2line to decode addresses:\n");
    fprintf(stderr, "  addr2line -e /path/to/_sffuncspan.*.so <address>\n");
    fprintf(stderr, "================================================================================\n");
    fprintf(stderr, "\n");

    fflush(stderr);
    fsync(2);  // Force write to disk

    const char *footer = "\n=== END CRASH HANDLER ===\n\n";
    write(2, footer, strlen(footer));

    // Re-raise signal with default handler (generates core dump)
    signal(sig, SIG_DFL);
    raise(sig);
}

// Install crash handler
static PyObject *install_crash_handler(PyObject *self, PyObject *args) {
    struct sigaction sa;
    memset(&sa, 0, sizeof(sa));
    sa.sa_sigaction = crash_handler;
    sa.sa_flags = SA_SIGINFO | SA_RESTART;
    sigemptyset(&sa.sa_mask);

    if (sigaction(SIGSEGV, &sa, NULL) == -1) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to install SIGSEGV handler");
        return NULL;
    }
    if (sigaction(SIGABRT, &sa, NULL) == -1) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to install SIGABRT handler");
        return NULL;
    }
    if (sigaction(SIGBUS, &sa, NULL) == -1) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to install SIGBUS handler");
        return NULL;
    }
    if (sigaction(SIGFPE, &sa, NULL) == -1) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to install SIGFPE handler");
        return NULL;
    }
    if (sigaction(SIGILL, &sa, NULL) == -1) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to install SIGILL handler");
        return NULL;
    }

    fprintf(stderr, "[_sfcrashhandler] C-level crash handlers installed (PID=%d)\n", getpid());
    fflush(stderr);

    Py_RETURN_NONE;
}

static PyMethodDef crash_handler_methods[] = {
    {"install", install_crash_handler, METH_NOARGS, "Install C-level crash handler"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef crash_handler_module = {
    PyModuleDef_HEAD_INIT,
    "_sfcrashhandler",
    "C-level crash handler for debugging segfaults",
    -1,
    crash_handler_methods
};

PyMODINIT_FUNC PyInit__sfcrashhandler(void) {
    return PyModule_Create(&crash_handler_module);
}
