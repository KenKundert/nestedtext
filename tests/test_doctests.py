# encoding: utf8

import pytest
import doctest
import glob
from shlib import cd


def test_README():
    rv = doctest.testfile('../README.rst', optionflags=doctest.ELLIPSIS)
    assert rv.attempted == 0
    assert rv.failed == 0

def test_nestedtext():
    rv = doctest.testfile('../nestedtext.py', optionflags=doctest.ELLIPSIS)
    assert rv.attempted == 55
    assert rv.failed == 0

def test_manual():
    expected_test_count = {
        '../doc/alternatives.rst': 0,
        '../doc/basic_syntax.rst': 0,
        '../doc/basic_use.rst': 10,
        '../doc/changelog.rst': 0,
        '../doc/common_mistakes.rst': 5,
        '../doc/examples.rst': 5,
        '../doc/file_format.rst': 0,
        '../doc/index.rst': 0,
        '../doc/nestedtext.dump.rst': 0,
        '../doc/nestedtext.dumps.rst': 0,
        '../doc/nestedtext.load.rst': 0,
        '../doc/nestedtext.loads.rst': 0,
        '../doc/nestedtext.Location.rst': 0,
        '../doc/nestedtext.NestedTextError.rst': 0,
        '../doc/philosophy.rst': 0,
        '../doc/python_api.rst': 0,
        '../doc/releases.rst': 0,
        '../doc/schemas.rst': 0,
    }
    found = glob.glob('../doc/*.rst')
    for path in found:
        assert path in expected_test_count, path
    for path, tests in expected_test_count.items():
        rv = doctest.testfile(path, optionflags=doctest.ELLIPSIS)
        assert rv.attempted == tests, path
        assert rv.failed == 0, path

if __name__ == '__main__':
    # As a debugging aid allow the tests to be run on their own, outside pytest.
    # This makes it easier to see and interpret and textual output.

    defined = dict(globals())
    for k, v in defined.items():
        if callable(v) and k.startswith('test_'):
            print()
            print('Calling:', k)
            print((len(k)+9)*'=')
            v()
