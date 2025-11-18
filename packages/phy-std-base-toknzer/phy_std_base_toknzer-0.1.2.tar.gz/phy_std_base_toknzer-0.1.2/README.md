# Consistent Tokenizer Across Python Versions

<p align="left">
  <a href="#"><img alt="PyPI" src="https://img.shields.io/pypi/v/phy-std-base-toknzer.svg"></a>
  <a href="#"><img alt="Python Versions" src="https://img.shields.io/pypi/pyversions/phy-std-base-toknzer.svg"></a>
  <a href="#"><img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg"></a>
</p>

This project is part of [`phy`](https://github.com/phy-precompiler).

## Overview

This package provides a replacement for Python builtin `tokenize` module and behaves consistently across active python versions.

The differences of builtin `tokenize` module among versions includes:

- Since Python 3.12, new fstring related token types `FSTRING_START`, `FSTRING_MIDDLE` & `FSTRING_END` were introduced for [PEP 701](https://peps.python.org/pep-0701/), along with notable performance enhancements.

- Python 3.14 brings new token types `TSTRING_START`, `TSTRING_MIDDLE` & `TSTRING_END` for new syntax [Template String](https://peps.python.org/pep-0750/).

- Python's built-in [`token`](https://docs.python.org/3/library/token.html) module assigns an **integer value** to each token type. However, these numeric values are **not guaranteed to be stable** across Python versions: 

| token type       | python 3.10 | python 3.11 | python 3.12 | python 3.13 | python 3.14 |
|------------------|-------------|-------------|-------------|-------------|-------------|
| ENDMARKER        | 0           | 0           | 0           | 0           | 0           |
| NAME             | 1           | 1           | 1           | 1           | 1           |
| NUMBER           | 2           | 2           | 2           | 2           | 2           |
| STRING           | 3           | 3           | 3           | 3           | 3           |
| NEWLINE          | 4           | 4           | 4           | 4           | 4           |
| INDENT           | 5           | 5           | 5           | 5           | 5           |
| DEDENT           | 6           | 6           | 6           | 6           | 6           |
| LPAR             | 7           | 7           | 7           | 7           | 7           |
| RPAR             | 8           | 8           | 8           | 8           | 8           |
| LSQB             | 9           | 9           | 9           | 9           | 9           |
| RSQB             | 10          | 10          | 10          | 10          | 10          |
| COLON            | 11          | 11          | 11          | 11          | 11          |
| COMMA            | 12          | 12          | 12          | 12          | 12          |
| SEMI             | 13          | 13          | 13          | 13          | 13          |
| PLUS             | 14          | 14          | 14          | 14          | 14          |
| MINUS            | 15          | 15          | 15          | 15          | 15          |
| STAR             | 16          | 16          | 16          | 16          | 16          |
| SLASH            | 17          | 17          | 17          | 17          | 17          |
| VBAR             | 18          | 18          | 18          | 18          | 18          |
| AMPER            | 19          | 19          | 19          | 19          | 19          |
| LESS             | 20          | 20          | 20          | 20          | 20          |
| GREATER          | 21          | 21          | 21          | 21          | 21          |
| EQUAL            | 22          | 22          | 22          | 22          | 22          |
| DOT              | 23          | 23          | 23          | 23          | 23          |
| PERCENT          | 24          | 24          | 24          | 24          | 24          |
| LBRACE           | 25          | 25          | 25          | 25          | 25          |
| RBRACE           | 26          | 26          | 26          | 26          | 26          |
| EQEQUAL          | 27          | 27          | 27          | 27          | 27          |
| NOTEQUAL         | 28          | 28          | 28          | 28          | 28          |
| LESSEQUAL        | 29          | 29          | 29          | 29          | 29          |
| GREATEREQUAL     | 30          | 30          | 30          | 30          | 30          |
| TILDE            | 31          | 31          | 31          | 31          | 31          |
| CIRCUMFLEX       | 32          | 32          | 32          | 32          | 32          |
| LEFTSHIFT        | 33          | 33          | 33          | 33          | 33          |
| RIGHTSHIFT       | 34          | 34          | 34          | 34          | 34          |
| DOUBLESTAR       | 35          | 35          | 35          | 35          | 35          |
| PLUSEQUAL        | 36          | 36          | 36          | 36          | 36          |
| MINEQUAL         | 37          | 37          | 37          | 37          | 37          |
| STAREQUAL        | 38          | 38          | 38          | 38          | 38          |
| SLASHEQUAL       | 39          | 39          | 39          | 39          | 39          |
| PERCENTEQUAL     | 40          | 40          | 40          | 40          | 40          |
| AMPEREQUAL       | 41          | 41          | 41          | 41          | 41          |
| VBAREQUAL        | 42          | 42          | 42          | 42          | 42          |
| CIRCUMFLEXEQUAL  | 43          | 43          | 43          | 43          | 43          |
| LEFTSHIFTEQUAL   | 44          | 44          | 44          | 44          | 44          |
| RIGHTSHIFTEQUAL  | 45          | 45          | 45          | 45          | 45          |
| DOUBLESTAREQUAL  | 46          | 46          | 46          | 46          | 46          |
| DOUBLESLASH      | 47          | 47          | 47          | 47          | 47          |
| DOUBLESLASHEQUAL | 48          | 48          | 48          | 48          | 48          |
| AT               | 49          | 49          | 49          | 49          | 49          |
| ATEQUAL          | 50          | 50          | 50          | 50          | 50          |
| RARROW           | 51          | 51          | 51          | 51          | 51          |
| ELLIPSIS         | 52          | 52          | 52          | 52          | 52          |
| COLONEQUAL       | 53          | 53          | 53          | 53          | 53          |
| EXCLAMATION      |             |             | 54          | 54          | 54          |
| OP               | 54          | 54          | 55          | 55          | 55          |
| AWAIT            | 55          | 55          | 56          |             |             |
| ASYNC            | 56          | 56          | 57          |             |             |
| TYPE_IGNORE      | 57          | 57          | 58          | 56          | 56          |
| TYPE_COMMENT     | 58          | 58          | 59          | 57          | 57          |
| SOFT_KEYWORD     | 59          | 59          | 60          | 58          | 58          |
| FSTRING_START    |             |             | 61          | 59          | 59          |
| FSTRING_MIDDLE   |             |             | 62          | 60          | 60          |
| FSTRING_END      |             |             | 63          | 61          | 61          |
| TSTRING_START    |             |             |             |             | 62          |
| TSTRING_MIDDLE   |             |             |             |             | 63          |
| TSTRING_END      |             |             |             |             | 64          |
| COMMENT          | 61          | 61          | 64          | 62          | 65          |
| NL               | 62          | 62          | 65          | 63          | 66          |
| ERRORTOKEN       | 60          | 60          | 66          | 64          | 67          |
| N_TOKENS         | 64          | 64          | 68          | 66          | 69          |
| NT_OFFSET        | 256         | 256         | 256         | 256         | 256         |


This may lead to necessary extra works about token codes alignment if your project relies on consistent numeric token codes across environments.

---

## What this Project Does

This repository extracts the c code related to `lexer` & `tokenize` from CPython 3.14 source code (the latest Python version), and build a standalone python package with the same Python API as built-in `tokenize` module. 

Use this package to tokenize python codes will produce the same results, regardless of which version of python interpreter is used.

This package has **ZERO** dependencies.


## Installation

```shell
pip install phy-std-base-toknzer
```

If theres is issue in installing on Windows, refer to [build-on-windows](#build-on-windows) to built it by ones own.

## How to use

Use this library absolutely the same as builtin `tokenize` module:

```python
from io import BytesIO, StringIO
import phy_std_base_toknzer

code = '''print(f"hello world to {greeter}!")\ntemplate=t"input a {name}"\n'''
code_readline = BytesIO(code.encode('utf-8')).readline
code_str_readline = StringIO(code).readline

for _token in phy_std_base_toknzer.tokenize(code_readline):
    print(_token)

# or
for _token in phy_std_base_toknzer.generate_tokens(code_str_readline):
    print(_token)
```

The generated token is 5-elements `namedTuple` inherited from `tokenize.TokenInfo`, with `__repr__` 
method overwritten since this method is dependent on `token` module of current python version. 
The generated token type int value (the first element) should be interpreted with 3.14 token type 
tables, as provided by `std_base_toknzer.tok_def` submodule.

## Build

This library use [`scikit-build-core`](https://github.com/scikit-build/scikit-build-core) and 
[`uv`](https://github.com/astral-sh/uv) to build; `cmake` is a dependency of `scikit-build-core`.

```bash
uv build
```

### build on Windows

If you use `visual c++` as compiler to build this package, to avoid error "The C compiler identification is unknown", it is better to use `Command Prompt for VS` app to execute the build command.

If error "The C compiler identification is unknown. CMAKE_C_COMPILER could be found" encountered but you have Visual C++ installed, try to install the component `Desktop development with C++`.
