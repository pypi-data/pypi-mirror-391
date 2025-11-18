""" Interfaces of module `std_base_toknzer`. 

These methods are strictly compatible with builtin `tokenize` module.
"""
__all__ = [
    'tokenize',
    'StdTokInfo',
]
__version__ = '0.1.1'


# imports
from tokenize import detect_encoding, TokenError
import itertools
import collections
from typing import Generator

from phy_std_base_toknzer import tok_def
# local imports; pylint: disable=import-error,no-name-in-module
from phy_std_base_toknzer._tokenize import TokenizerIter


class StdTokInfo(collections.namedtuple('StdTokInfo', 'type string start end line')):
    """ overwrite `repr` of builtin `TokenInfo` namedTuple """
    def __repr__(self):
        annotated_type = f'{self.type} ({tok_def.tok_name[self.type]})'
        # pylint: disable=line-too-long
        return f'TokenInfo(type={annotated_type}, string={self.string}, start={self.start}, end={self.end}, line={self.line})'


def tokenize(readline) -> Generator[StdTokInfo, None, None]:
    """
    The tokenize() generator requires one argument, readline, which
    must be a callable object which provides the same interface as the
    readline() method of built-in file objects.  Each call to the function
    should return one line of input as bytes.  Alternatively, readline
    can be a callable function terminating with StopIteration:
        readline = open(myfile, 'rb').__next__  # Example of alternate readline

    The generator produces 5-tuples with these members: the token type; the
    token string; a 2-tuple (srow, scol) of ints specifying the row and
    column where the token begins in the source; a 2-tuple (erow, ecol) of
    ints specifying the row and column where the token ends in the source;
    and the line on which the token was found.  The line passed is the
    physical line.

    The first token sequence will always be an ENCODING token
    which tells you which encoding was used to decode the bytes stream.
    """
    encoding, consumed = detect_encoding(readline)
    rl_gen = itertools.chain(consumed, iter(readline, b""))
    if encoding is not None:
        if encoding == "utf-8-sig":
            # BOM will already have been stripped.
            encoding = "utf-8"
        yield StdTokInfo(tok_def.ENCODING, encoding, (0, 0), (0, 0), '')
    yield from _generate_tokens_from_c_tokenizer(rl_gen.__next__, encoding, extra_tokens=True)


def generate_tokens(readline):
    """Tokenize a source reading Python code as unicode strings.

    This has the same API as tokenize(), except that it expects the *readline*
    callable to return str objects instead of bytes.
    """
    return _generate_tokens_from_c_tokenizer(readline, extra_tokens=True)


def _transform_msg(msg):
    """Transform error messages from the C tokenizer into the Python tokenize

    The C tokenizer is more picky than the Python one, so we need to massage
    the error messages a bit for backwards compatibility.
    """
    if "unterminated triple-quoted string literal" in msg:
        return "EOF in multi-line string"
    return msg


def _generate_tokens_from_c_tokenizer(source, encoding=None, extra_tokens=False):
    """Tokenize a source reading Python code as unicode strings using the internal C tokenizer"""
    if encoding is None:
        it = TokenizerIter(source, extra_tokens=extra_tokens)
    else:
        it = TokenizerIter(source, encoding=encoding, extra_tokens=extra_tokens)
    try:
        for info in it:
            yield StdTokInfo._make(info)
    except SyntaxError as e:
        # pylint: disable=unidiomatic-typecheck
        if type(e) != SyntaxError:
            raise e from None
        msg = _transform_msg(e.msg)
        raise TokenError(msg, (e.lineno, e.offset)) from None
