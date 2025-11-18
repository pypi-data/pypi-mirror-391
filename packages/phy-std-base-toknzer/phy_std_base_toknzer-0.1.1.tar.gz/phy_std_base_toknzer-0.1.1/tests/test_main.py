# pylint: disable=missing-function-docstring,unused-import
""" main test cases """
# imports
from io import BytesIO, StringIO
from pprint import pprint
import pytest


@pytest.mark.skip()
def test_mod_avaiable():
    # pylint: disable=import-outside-toplevel
    import phy_std_base_toknzer
    pprint(phy_std_base_toknzer.__dict__)


@pytest.mark.skip()
def test_std_base_toknzer():
    code = '''print(f"hello world to {greeter}!")\ntemplate=t"input a {name}"\n'''
    code_readline = BytesIO(code.encode('utf-8')).readline

    # pylint: disable=import-outside-toplevel
    import phy_std_base_toknzer

    _iter = phy_std_base_toknzer.TokenizerIter(code_readline, encoding='utf-8')
    for _token in _iter:
        print(_token)
        print(type(_token))


# @pytest.mark.skip()
def test_std_base_toknzer_interface():
    code = '''print(f"hello world to {greeter}!")\ntemplate=t"input a {name}"\n'''
    code_readline = BytesIO(code.encode('utf-8')).readline
    code_str_readline = StringIO(code).readline

    # pylint: disable=import-outside-toplevel
    import phy_std_base_toknzer

    for _token in phy_std_base_toknzer.tokenize(code_readline):
        print(_token)

    # or
    for _token in phy_std_base_toknzer.generate_tokens(code_str_readline):
        print(_token)
