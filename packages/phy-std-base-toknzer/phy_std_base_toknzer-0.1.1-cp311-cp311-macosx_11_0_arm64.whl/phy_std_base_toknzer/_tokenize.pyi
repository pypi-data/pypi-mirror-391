""" Interfaces of c module. """
# imports
from typing import Callable, Iterator, Tuple, Optional

# typings
_Pos = Tuple[int, int]
_BareTokenInfo = Tuple[int, str, _Pos, Optional[_Pos]]


class TokenizerIter(Iterator[_BareTokenInfo]):
    """ interface of c method which creates iterator of tokens """

    # pylint: disable=unused-argument
    def __init__(
            self,
            readline: Callable[[], bytes],
            encoding: str = None,
            extra_tokens: bool = False
        ): ...
    def __iter__(self) -> 'TokenizerIter': ...
    def __next__(self) -> _BareTokenInfo: ...
