# test_misc.py
import parametrize_from_file
import re
import pathlib

@parametrize_from_file
def test_substitution(given, search, replace, expected):
    assert re.sub(search, replace, given) == expected

@parametrize_from_file
def test_expression(given, expected):
    assert eval(given) == eval(expected)

