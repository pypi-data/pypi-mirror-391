/** module definition  */
#define PY_SSIZE_T_CLEAN

/** includes */
// include python headers
#include <Python.h>

// include local headers
#include "_tokenize.h"

/** python module definition */
static PyMethodDef tokenize_methods[] = {
    {NULL, NULL, 0, NULL} /* Sentinel */
};

static PyModuleDef_Slot tokenizemodule_slots[] = {
    {Py_mod_exec, tokenizemodule_exec},
    /// GIL related macros are ignored
    /// {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
    /// {Py_mod_gil, Py_MOD_GIL_NOT_USED},
    {0, NULL}
};

static struct PyModuleDef _tokenizemodule = {
    PyModuleDef_HEAD_INIT, 
    "std_base_toknzer",
    .m_size = sizeof(tokenize_state),
    .m_slots = tokenizemodule_slots,
    .m_methods = tokenize_methods,
    .m_traverse = tokenizemodule_traverse,
    .m_clear = tokenizemodule_clear,
    .m_free = tokenizemodule_free
};

/** name here must match extension name, with `PyInit_` prefix */
PyMODINIT_FUNC PyInit__tokenize(void) {
    return PyModuleDef_Init(&_tokenizemodule);
}
