/** Header for `_tokenize.c`. 
 * 
 * Expose necessary symbols for module definition fields. 
 */

/** includes */
// include python headers
#include <Python.h>

/** symbols declaration */
static PyObject *
tokenizeriter_new_impl(PyTypeObject *type, PyObject *readline,
                       int extra_tokens, const char *encoding);

static PyObject *
tokenizeriter_new(PyTypeObject *type, PyObject *args, PyObject *kwargs);

typedef struct {
    PyTypeObject *TokenizerIter;
} tokenize_state;

int
tokenizemodule_exec(PyObject *m);

int
tokenizemodule_traverse(PyObject *m, visitproc visit, void *arg);

int
tokenizemodule_clear(PyObject *m);

void
tokenizemodule_free(void *m);
