/** This file is copied from "cpython/Python/Python-tokenize.c" of 3.14 branch. 
 * 
 * Internal header includes, GIL related macros are refactored or ignored.
*/

/** includes */
// include python headers
#include <Python.h>
#include <errcode.h>

// include local headers
#include "_tokenize.h"

/// this header has been refactored to contains only token type constants
#include "_token.h"

/// DO NOT include python internal headers  
/// #include "internal/pycore_critical_section.h"   // Py_BEGIN_CRITICAL_SECTION
#include "./lexer/state.h"
#include "./lexer/lexer.h"
#include "./tokenizer/tokenizer.h"

/// only few functions of `pegen.h` are included; hence expended to inline
/// #include "./pegen.h"                    // _PyPegen_byte_offset_to_character_offset()
/// functions defined in "Parser/pegen.c"
Py_ssize_t
_PyPegen_byte_offset_to_character_offset_raw(const char* str, Py_ssize_t col_offset)
{
    Py_ssize_t len = (Py_ssize_t)strlen(str);
    if (col_offset > len + 1) {
        col_offset = len + 1;
    }
    assert(col_offset >= 0);
    PyObject *text = PyUnicode_DecodeUTF8(str, col_offset, "replace");
    if (!text) {
        return -1;
    }
    Py_ssize_t size = PyUnicode_GET_LENGTH(text);
    Py_DECREF(text);
    return size;
}

Py_ssize_t
_PyPegen_byte_offset_to_character_offset(PyObject *line, Py_ssize_t col_offset)
{
    const char *str = PyUnicode_AsUTF8(line);
    if (!str) {
        return -1;
    }
    return _PyPegen_byte_offset_to_character_offset_raw(str, col_offset);
}

Py_ssize_t
_PyPegen_byte_offset_to_character_offset_line(PyObject *line, Py_ssize_t col_offset, Py_ssize_t end_col_offset)
{
    const unsigned char *data = (const unsigned char*)PyUnicode_AsUTF8(line);

    Py_ssize_t len = 0;
    while (col_offset < end_col_offset) {
        Py_UCS4 ch = data[col_offset];
        if (ch < 0x80) {
            col_offset += 1;
        } else if ((ch & 0xe0) == 0xc0) {
            col_offset += 2;
        } else if ((ch & 0xf0) == 0xe0) {
            col_offset += 3;
        } else if ((ch & 0xf8) == 0xf0) {
            col_offset += 4;
        } else {
            PyErr_SetString(PyExc_ValueError, "Invalid UTF-8 sequence");
            return -1;
        }
        len++;
    }
    return len;
}

/// define module in other file
/// static struct PyModuleDef _tokenizemodule;

/// move to `_tokenize.h`
/// typedef struct {
///     PyTypeObject *TokenizerIter;
/// } tokenize_state;

static tokenize_state *
get_tokenize_state(PyObject *module) {
    return (tokenize_state *)PyModule_GetState(module);
}

#define _tokenize_get_state_by_type(type) \
    get_tokenize_state(PyType_GetModuleByDef(type, &_tokenizemodule))

/// DO NOT include python internal headers 
/// #include "pycore_runtime.h"

/// only one function of `Python-tokenize.c.h` is included; hence expended to inline
/// #include "clinic/Python-tokenize.c.h"
static PyObject *
tokenizeriter_new(PyTypeObject *type, PyObject *args, PyObject *kwargs)
{
    PyObject *return_value = NULL;
    
    /// Cpython build macros are ignored

    /// #if defined(Py_BUILD_CORE) && !defined(Py_BUILD_CORE_MODULE)
    ///
    /// #define NUM_KEYWORDS 2
    /// static struct {
    ///     PyGC_Head _this_is_not_used;
    ///     PyObject_VAR_HEAD
    ///     Py_hash_t ob_hash;
    ///     PyObject *ob_item[NUM_KEYWORDS];
    /// } _kwtuple = {
    ///     .ob_base = PyVarObject_HEAD_INIT(&PyTuple_Type, NUM_KEYWORDS)
    ///     .ob_hash = -1,
    ///     .ob_item = { &_Py_ID(extra_tokens), &_Py_ID(encoding), },
    /// };
    /// #undef NUM_KEYWORDS
    /// #define KWTUPLE (&_kwtuple.ob_base.ob_base)
    ///
    /// #else  // !Py_BUILD_CORE
    /// #  define KWTUPLE NULL
    /// #endif  // !Py_BUILD_CORE

    /// this funtion calls private API `_PyArg_UnpackKeywords`, has to be refactored

    /// static const char * const _keywords[] = {"", "extra_tokens", "encoding", NULL};
    /// static _PyArg_Parser _parser = {
    ///     .keywords = _keywords,
    ///     .fname = "tokenizeriter",
    ///     .kwtuple = KWTUPLE,
    /// };
    /// #undef KWTUPLE

    /// PyObject *argsbuf[3];
    /// PyObject * const *fastargs;

    /// Py_ssize_t nargs = PyTuple_GET_SIZE(args);
    /// Py_ssize_t noptargs = nargs + (kwargs ? PyDict_GET_SIZE(kwargs) : 0) - 2;
    /// PyObject *readline;
    /// int extra_tokens;
    /// const char *encoding = NULL;

    /// fastargs = _PyArg_UnpackKeywords(_PyTuple_CAST(args)->ob_item, nargs, kwargs, NULL, &_parser,
    ///          /*minpos*/ 1, /*maxpos*/ 1, /*minkw*/ 1, /*varpos*/ 0, argsbuf);

    // parse argumenets of:
    // tokenizeriter_new(args, encoding: str, extra_tokens: bool)
    PyObject *readline;
    const char *encoding = NULL;
    int extra_tokens = 0;

    static char *kwlist[] = {"readline", "encoding", "extra_tokens", NULL};
    if (!PyArg_ParseTupleAndKeywords(
            args, kwargs,
            "O|sp",             // format: O for PyObject; s for string; p for bool
            kwlist,
            &readline,
            &encoding,          // encoding (char*, with defaults)
            &extra_tokens))     // extra_tokens (int, with defaults, 0/1)
    {
        goto exit;
    }
    
    /// if (!fastargs) {
    ///     goto exit;
    /// }

    /// readline = fastargs[0];
    /// extra_tokens = PyObject_IsTrue(fastargs[1]);
    /// if (extra_tokens < 0) {
    ///     goto exit;
    /// }
    /// if (!noptargs) {
    ///     goto skip_optional_kwonly;
    /// }
    /// if (!PyUnicode_Check(fastargs[2])) {
    ///     _PyArg_BadArgument("tokenizeriter", "argument 'encoding'", "str", fastargs[2]);
    ///     goto exit;
    /// }
    /// Py_ssize_t encoding_length;
    /// encoding = PyUnicode_AsUTF8AndSize(fastargs[2], &encoding_length);
    /// if (encoding == NULL) {
    ///     goto exit;
    /// }
    /// if (strlen(encoding) != (size_t)encoding_length) {
    ///     PyErr_SetString(PyExc_ValueError, "embedded null character");
    ///     goto exit;
    /// }
/// skip_optional_kwonly:

    return_value = tokenizeriter_new_impl(type, readline, extra_tokens, encoding);

exit:
    return return_value;
}


/// clinic is an internal code generator tool by cpython
/*[clinic input]
module _tokenizer
class _tokenizer.tokenizeriter "tokenizeriterobject *" "_tokenize_get_state_by_type(type)->TokenizerIter"
[clinic start generated code]*/
/*[clinic end generated code: output=da39a3ee5e6b4b0d input=96d98ee2fef7a8bc]*/

typedef struct
{
    PyObject_HEAD struct tok_state *tok;
    int done;

    /* Needed to cache line for performance */
    PyObject *last_line;
    Py_ssize_t last_lineno;
    Py_ssize_t last_end_lineno;
    Py_ssize_t byte_col_offset_diff;
} tokenizeriterobject;

/*[clinic input]
@classmethod
_tokenizer.tokenizeriter.__new__ as tokenizeriter_new

    readline: object
    /
    *
    extra_tokens: bool
    encoding: str(c_default="NULL") = 'utf-8'
[clinic start generated code]*/

static PyObject *
tokenizeriter_new_impl(PyTypeObject *type, PyObject *readline,
                       int extra_tokens, const char *encoding)
/*[clinic end generated code: output=7501a1211683ce16 input=f7dddf8a613ae8bd]*/
{
    tokenizeriterobject *self = (tokenizeriterobject *)type->tp_alloc(type, 0);
    if (self == NULL) {
        return NULL;
    }
    PyObject *filename = PyUnicode_FromString("<string>");
    if (filename == NULL) {
        return NULL;
    }
    self->tok = _PyTokenizer_FromReadline(readline, encoding, 1, 1);
    if (self->tok == NULL) {
        Py_DECREF(filename);
        return NULL;
    }
    self->tok->filename = filename;
    if (extra_tokens) {
        self->tok->tok_extra_tokens = 1;
    }
    self->done = 0;

    self->last_line = NULL;
    self->byte_col_offset_diff = 0;
    self->last_lineno = 0;
    self->last_end_lineno = 0;

    return (PyObject *)self;
}

static int
_tokenizer_error(tokenizeriterobject *it)
{
    /// GIL related macros are ignored
    /// _Py_CRITICAL_SECTION_ASSERT_OBJECT_LOCKED(it);
    /// if (PyErr_Occurred()) {
    ///     return -1;
    /// }

    const char *msg = NULL;
    PyObject* errtype = PyExc_SyntaxError;
    struct tok_state *tok = it->tok;
    switch (tok->done) {
        case E_TOKEN:
            msg = "invalid token";
            break;
        case E_EOF:
            PyErr_SetString(PyExc_SyntaxError, "unexpected EOF in multi-line statement");
            PyErr_SyntaxLocationObject(tok->filename, tok->lineno,
                                       tok->inp - tok->buf < 0 ? 0 : (int)(tok->inp - tok->buf));
            return -1;
        case E_DEDENT:
            msg = "unindent does not match any outer indentation level";
            errtype = PyExc_IndentationError;
            break;
        case E_INTR:
            if (!PyErr_Occurred()) {
                PyErr_SetNone(PyExc_KeyboardInterrupt);
            }
            return -1;
        case E_NOMEM:
            PyErr_NoMemory();
            return -1;
        case E_TABSPACE:
            errtype = PyExc_TabError;
            msg = "inconsistent use of tabs and spaces in indentation";
            break;
        case E_TOODEEP:
            errtype = PyExc_IndentationError;
            msg = "too many levels of indentation";
            break;
        case E_LINECONT: {
            msg = "unexpected character after line continuation character";
            break;
        }
        default:
            msg = "unknown tokenization error";
    }

    PyObject* errstr = NULL;
    PyObject* error_line = NULL;
    PyObject* tmp = NULL;
    PyObject* value = NULL;
    int result = 0;

    Py_ssize_t size = tok->inp - tok->buf;
    assert(tok->buf[size-1] == '\n');
    size -= 1; // Remove the newline character from the end of the line
    error_line = PyUnicode_DecodeUTF8(tok->buf, size, "replace");
    if (!error_line) {
        result = -1;
        goto exit;
    }

    Py_ssize_t offset = _PyPegen_byte_offset_to_character_offset(error_line, tok->inp - tok->buf);
    if (offset == -1) {
        result = -1;
        goto exit;
    }
    tmp = Py_BuildValue("(OnnOOO)", tok->filename, tok->lineno, offset, error_line, Py_None, Py_None);
    if (!tmp) {
        result = -1;
        goto exit;
    }

    errstr = PyUnicode_FromString(msg);
    if (!errstr) {
        result = -1;
        goto exit;
    }

    value = PyTuple_Pack(2, errstr, tmp);
    if (!value) {
        result = -1;
        goto exit;
    }

    PyErr_SetObject(errtype, value);

exit:
    Py_XDECREF(errstr);
    Py_XDECREF(error_line);
    Py_XDECREF(tmp);
    Py_XDECREF(value);
    return result;
}

static PyObject *
_get_current_line(tokenizeriterobject *it, const char *line_start, Py_ssize_t size,
                  int *line_changed)
{
    /// GIL related macros are ignored
    /// _Py_CRITICAL_SECTION_ASSERT_OBJECT_LOCKED(it);
    PyObject *line;
    if (it->tok->lineno != it->last_lineno) {
        // Line has changed since last token, so we fetch the new line and cache it
        // in the iter object.
        Py_XDECREF(it->last_line);
        line = PyUnicode_DecodeUTF8(line_start, size, "replace");
        it->last_line = line;
        it->byte_col_offset_diff = 0;
    }
    else {
        line = it->last_line;
        *line_changed = 0;
    }
    return line;
}

static void
_get_col_offsets(tokenizeriterobject *it, struct token token, const char *line_start,
                 PyObject *line, int line_changed, Py_ssize_t lineno, Py_ssize_t end_lineno,
                 Py_ssize_t *col_offset, Py_ssize_t *end_col_offset)
{
    /// GIL related macros are ignored
    /// _Py_CRITICAL_SECTION_ASSERT_OBJECT_LOCKED(it);
    Py_ssize_t byte_offset = -1;
    if (token.start != NULL && token.start >= line_start) {
        byte_offset = token.start - line_start;
        if (line_changed) {
            *col_offset = _PyPegen_byte_offset_to_character_offset_line(line, 0, byte_offset);
            it->byte_col_offset_diff = byte_offset - *col_offset;
        }
        else {
            *col_offset = byte_offset - it->byte_col_offset_diff;
        }
    }

    if (token.end != NULL && token.end >= it->tok->line_start) {
        Py_ssize_t end_byte_offset = token.end - it->tok->line_start;
        if (lineno == end_lineno) {
            // If the whole token is at the same line, we can just use the token.start
            // buffer for figuring out the new column offset, since using line is not
            // performant for very long lines.
            Py_ssize_t token_col_offset = _PyPegen_byte_offset_to_character_offset_line(line, byte_offset, end_byte_offset);
            *end_col_offset = *col_offset + token_col_offset;
            it->byte_col_offset_diff += token.end - token.start - token_col_offset;
        }
        else {
            *end_col_offset = _PyPegen_byte_offset_to_character_offset_raw(it->tok->line_start, end_byte_offset);
            it->byte_col_offset_diff += end_byte_offset - *end_col_offset;
        }
    }
    it->last_lineno = lineno;
    it->last_end_lineno = end_lineno;
}

static PyObject *
tokenizeriter_next(PyObject *op)
{
    tokenizeriterobject *it = (tokenizeriterobject*)op;
    PyObject* result = NULL;

    /// GIL related macros are ignored
    /// Py_BEGIN_CRITICAL_SECTION(it);

    struct token token;
    _PyToken_Init(&token);

    int type = _PyTokenizer_Get(it->tok, &token);
    if (type == ERRORTOKEN) {
        if(!PyErr_Occurred()) {
            _tokenizer_error(it);
            assert(PyErr_Occurred());
        }
        goto exit;
    }
    if (it->done || type == ERRORTOKEN) {
        PyErr_SetString(PyExc_StopIteration, "EOF");
        it->done = 1;
        goto exit;
    }
    PyObject *str = NULL;
    if (token.start == NULL || token.end == NULL) {
        /// `Py_GetConstant` is not a consistent symbol across python versions, has to be refactored
        /// str = Py_GetConstant(Py_CONSTANT_EMPTY_STR);
        str = PyUnicode_FromString("");
    }
    else {
        str = PyUnicode_FromStringAndSize(token.start, token.end - token.start);
    }
    if (str == NULL) {
        goto exit;
    }

    int is_trailing_token = 0;
    if (type == ENDMARKER || (type == DEDENT && it->tok->done == E_EOF)) {
        is_trailing_token = 1;
    }

    const char *line_start = ISSTRINGLIT(type) ? it->tok->multi_line_start : it->tok->line_start;
    PyObject* line = NULL;
    int line_changed = 1;
    if (it->tok->tok_extra_tokens && is_trailing_token) {
        /// `Py_GetConstant` is not a consistent symbol across python versions, has to be refactored
        /// line = Py_GetConstant(Py_CONSTANT_EMPTY_STR);
        line = PyUnicode_FromString("");
    } else {
        Py_ssize_t size = it->tok->inp - line_start;
        if (size >= 1 && it->tok->implicit_newline) {
            size -= 1;
        }

        line = _get_current_line(it, line_start, size, &line_changed);
    }
    if (line == NULL) {
        Py_DECREF(str);
        goto exit;
    }

    Py_ssize_t lineno = ISSTRINGLIT(type) ? it->tok->first_lineno : it->tok->lineno;
    Py_ssize_t end_lineno = it->tok->lineno;
    Py_ssize_t col_offset = -1;
    Py_ssize_t end_col_offset = -1;
    _get_col_offsets(it, token, line_start, line, line_changed,
                     lineno, end_lineno, &col_offset, &end_col_offset);

    if (it->tok->tok_extra_tokens) {
        if (is_trailing_token) {
            lineno = end_lineno = lineno + 1;
            col_offset = end_col_offset = 0;
        }
        // Necessary adjustments to match the original Python tokenize
        // implementation
        if (type > DEDENT && type < OP) {
            type = OP;
        }
        else if (type == NEWLINE) {
            Py_DECREF(str);
            if (!it->tok->implicit_newline) {
                if (it->tok->start[0] == '\r') {
                    str = PyUnicode_FromString("\r\n");
                } else {
                    str = PyUnicode_FromString("\n");
                }
            }
            end_col_offset++;
        }
        else if (type == NL) {
            if (it->tok->implicit_newline) {
                Py_DECREF(str);
                /// `Py_GetConstant` is not a consistent symbol across python versions, has to be refactored
                /// str = Py_GetConstant(Py_CONSTANT_EMPTY_STR);
                str = PyUnicode_FromString("");
            }
        }

        if (str == NULL) {
            Py_DECREF(line);
            goto exit;
        }
    }

    result = Py_BuildValue("(iN(nn)(nn)O)", type, str, lineno, col_offset, end_lineno, end_col_offset, line);
exit:
    _PyToken_Free(&token);
    if (type == ENDMARKER) {
        it->done = 1;
    }

    /// GIL related macros are ignored
    /// Py_END_CRITICAL_SECTION();
    return result;
}

static void
tokenizeriter_dealloc(PyObject *op)
{
    tokenizeriterobject *it = (tokenizeriterobject*)op;
    PyTypeObject *tp = Py_TYPE(it);
    Py_XDECREF(it->last_line);
    _PyTokenizer_Free(it->tok);
    tp->tp_free(it);
    Py_DECREF(tp);
}

static PyType_Slot tokenizeriter_slots[] = {
    {Py_tp_new, tokenizeriter_new},
    {Py_tp_dealloc, tokenizeriter_dealloc},
    {Py_tp_getattro, PyObject_GenericGetAttr},
    {Py_tp_iter, PyObject_SelfIter},
    {Py_tp_iternext, tokenizeriter_next},
    {0, NULL},
};

static PyType_Spec tokenizeriter_spec = {
    .name = "_tokenize.TokenizerIter",
    .basicsize = sizeof(tokenizeriterobject),
    .flags = (Py_TPFLAGS_DEFAULT | Py_TPFLAGS_IMMUTABLETYPE),
    .slots = tokenizeriter_slots,
};

/* static */ int
tokenizemodule_exec(PyObject *m)
{
    tokenize_state *state = get_tokenize_state(m);
    if (state == NULL) {
        return -1;
    }

    state->TokenizerIter = (PyTypeObject *)PyType_FromModuleAndSpec(m, &tokenizeriter_spec, NULL);
    if (state->TokenizerIter == NULL) {
        return -1;
    }
    if (PyModule_AddType(m, state->TokenizerIter) < 0) {
        return -1;
    }

    return 0;
}

/// define module in other file
/// static PyMethodDef tokenize_methods[] = {
///     {NULL, NULL, 0, NULL} /* Sentinel */
/// };
/// 
/// static PyModuleDef_Slot tokenizemodule_slots[] = {
///     {Py_mod_exec, tokenizemodule_exec},
///     /// GIL related macros are ignored
///     /// {Py_mod_multiple_interpreters, Py_MOD_PER_INTERPRETER_GIL_SUPPORTED},
///     /// {Py_mod_gil, Py_MOD_GIL_NOT_USED},
///     {0, NULL}
/// };

/* static */ int
tokenizemodule_traverse(PyObject *m, visitproc visit, void *arg)
{
    tokenize_state *state = get_tokenize_state(m);
    Py_VISIT(state->TokenizerIter);
    return 0;
}

/* static */ int
tokenizemodule_clear(PyObject *m)
{
    tokenize_state *state = get_tokenize_state(m);
    Py_CLEAR(state->TokenizerIter);
    return 0;
}

/* static */ void
tokenizemodule_free(void *m)
{
    tokenizemodule_clear((PyObject *)m);
}

/// define module in other file
/// static struct PyModuleDef _tokenizemodule = {
///     PyModuleDef_HEAD_INIT,
///     .m_name = "_tokenize",
///     .m_size = sizeof(tokenize_state),
///     .m_slots = tokenizemodule_slots,
///     .m_methods = tokenize_methods,
///     .m_traverse = tokenizemodule_traverse,
///     .m_clear = tokenizemodule_clear,
///     .m_free = tokenizemodule_free,
/// };

/// define module in other file
/// PyMODINIT_FUNC
/// PyInit__tokenize(void)
/// {
///     return PyModuleDef_Init(&_tokenizemodule);
/// }
