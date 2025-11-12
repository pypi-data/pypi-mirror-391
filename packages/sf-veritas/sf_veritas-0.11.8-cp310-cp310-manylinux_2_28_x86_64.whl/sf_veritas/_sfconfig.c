// Python C extension module to configure the C library
// This provides a clean, secure interface using dlsym to find runtime symbols
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <dlfcn.h>
#include <stdlib.h>
#include <stdio.h>

// Function pointers for the C library functions
typedef void (*sf_set_sink_url_t)(const char *url);
typedef void (*sf_set_api_key_t)(const char *key);
typedef void (*sf_set_service_uuid_t)(const char *uuid);
typedef void (*sf_initialize_t)(void);

static sf_set_sink_url_t sf_set_sink_url_ptr = NULL;
static sf_set_api_key_t sf_set_api_key_ptr = NULL;
static sf_set_service_uuid_t sf_set_service_uuid_ptr = NULL;
static sf_initialize_t sf_initialize_ptr = NULL;
static int symbols_resolved = 0;

// Lazy symbol resolution - called on first use of any function
static void ensure_symbols_resolved(void) {
    if (symbols_resolved) {
        return;  // Already resolved
    }

    // Clear any previous dlsym errors
    dlerror();

    // Use RTLD_DEFAULT to search all loaded libraries (including LD_PRELOAD)
    sf_set_sink_url_ptr = (sf_set_sink_url_t)dlsym(RTLD_DEFAULT, "sf_set_sink_url");
    const char *err1 = dlerror();

    sf_set_api_key_ptr = (sf_set_api_key_t)dlsym(RTLD_DEFAULT, "sf_set_api_key");
    const char *err2 = dlerror();

    sf_set_service_uuid_ptr = (sf_set_service_uuid_t)dlsym(RTLD_DEFAULT, "sf_set_service_uuid");
    const char *err3 = dlerror();

    sf_initialize_ptr = (sf_initialize_t)dlsym(RTLD_DEFAULT, "sf_initialize");
    const char *err4 = dlerror();

    // Debug output to help diagnose symbol resolution issues
    if (!sf_set_sink_url_ptr || !sf_set_api_key_ptr || !sf_set_service_uuid_ptr || !sf_initialize_ptr) {
        const char *ld_preload = getenv("LD_PRELOAD");
        fprintf(stderr, "[_sfconfig] Symbol resolution FAILED!\n");
        fprintf(stderr, "  LD_PRELOAD=%s\n", ld_preload ? ld_preload : "(not set)");
        fprintf(stderr, "  sf_set_sink_url: %s (%s)\n",
                sf_set_sink_url_ptr ? "OK" : "FAILED", err1 ? err1 : "no error");
        fprintf(stderr, "  sf_set_api_key: %s (%s)\n",
                sf_set_api_key_ptr ? "OK" : "FAILED", err2 ? err2 : "no error");
        fprintf(stderr, "  sf_set_service_uuid: %s (%s)\n",
                sf_set_service_uuid_ptr ? "OK" : "FAILED", err3 ? err3 : "no error");
        fprintf(stderr, "  sf_initialize: %s (%s)\n",
                sf_initialize_ptr ? "OK" : "FAILED", err4 ? err4 : "no error");
        fflush(stderr);
    }

    symbols_resolved = 1;
}

// Python wrapper: sf_set_sink_url(url: str) -> None
static PyObject* py_sf_set_sink_url(PyObject* self, PyObject* args) {
    const char *url;
    if (!PyArg_ParseTuple(args, "s", &url)) {
        return NULL;
    }

    // Lazy symbol resolution on first call
    ensure_symbols_resolved();

    if (!sf_set_sink_url_ptr) {
        PyErr_SetString(PyExc_RuntimeError, "C library not loaded (LD_PRELOAD not active?)");
        return NULL;
    }
    sf_set_sink_url_ptr(url);
    Py_RETURN_NONE;
}

// Python wrapper: sf_set_api_key(key: str) -> None
static PyObject* py_sf_set_api_key(PyObject* self, PyObject* args) {
    const char *key;
    if (!PyArg_ParseTuple(args, "s", &key)) {
        return NULL;
    }

    // Lazy symbol resolution on first call
    ensure_symbols_resolved();

    if (!sf_set_api_key_ptr) {
        PyErr_SetString(PyExc_RuntimeError, "C library not loaded (LD_PRELOAD not active?)");
        return NULL;
    }
    sf_set_api_key_ptr(key);
    Py_RETURN_NONE;
}

// Python wrapper: sf_set_service_uuid(uuid: str) -> None
static PyObject* py_sf_set_service_uuid(PyObject* self, PyObject* args) {
    const char *uuid;
    if (!PyArg_ParseTuple(args, "s", &uuid)) {
        return NULL;
    }

    // Lazy symbol resolution on first call
    ensure_symbols_resolved();

    if (!sf_set_service_uuid_ptr) {
        PyErr_SetString(PyExc_RuntimeError, "C library not loaded (LD_PRELOAD not active?)");
        return NULL;
    }
    sf_set_service_uuid_ptr(uuid);
    Py_RETURN_NONE;
}

// Python wrapper: sf_initialize() -> None
static PyObject* py_sf_initialize(PyObject* self, PyObject* args) {
    // Lazy symbol resolution on first call
    ensure_symbols_resolved();

    if (!sf_initialize_ptr) {
        PyErr_SetString(PyExc_RuntimeError, "C library not loaded (LD_PRELOAD not active?)");
        return NULL;
    }
    sf_initialize_ptr();
    Py_RETURN_NONE;
}

// Method definitions
static PyMethodDef SfConfigMethods[] = {
    {"set_sink_url", py_sf_set_sink_url, METH_VARARGS,
     "Set the GraphQL endpoint URL for the C library"},
    {"set_api_key", py_sf_set_api_key, METH_VARARGS,
     "Set the API key for the C library"},
    {"set_service_uuid", py_sf_set_service_uuid, METH_VARARGS,
     "Set the service UUID for the C library"},
    {"initialize", py_sf_initialize, METH_NOARGS,
     "Initialize and activate the C library (sets SF_INITIALIZED=1)"},
    {NULL, NULL, 0, NULL}
};

// Module definition
static struct PyModuleDef sfconfig_module = {
    PyModuleDef_HEAD_INIT,
    "_sfconfig",
    "Configuration interface for the Sailfish C library",
    -1,
    SfConfigMethods
};

// Module initialization
PyMODINIT_FUNC PyInit__sfconfig(void) {
    PyObject *module = PyModule_Create(&sfconfig_module);
    if (module == NULL) {
        return NULL;
    }

    // Symbol resolution is done lazily on first function call
    // This ensures the C library is fully loaded before we try to find symbols

    return module;
}
