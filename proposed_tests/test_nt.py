# IMPORTS {{{1
from functools import partial
from inform import cull, indent, render
from parametrize_from_file import parametrize
from pathlib import Path
from voluptuous import Schema, Optional, Required, Any, Invalid
from base64 import b64decode
import nestedtext as nt
import json

# GLOBALS {{{1
TEST_SUITE = Path('tests.json')
TEST_DIR = Path(__file__).parent

# PARAMETERIZATION {{{1
# Adapt parametrize_for_file to read dictionary rather than list {{{2
def name_from_dict_keys(cases):
    return [{**v, 'id': k} for k,v in cases.items()]
        # the name 'id' is special, do not change it
parametrize = partial(parametrize, preprocess=name_from_dict_keys)


# SCHEMA {{{1
def as_int(arg):
    return int(arg)

schema = Schema({
    Required("id", default='❬not given❭'): str,
    Required("load_in"): str,
    Required("load_out", default=None): Any(dict, list, str, None),
    Required("load_err", default={}): dict(
        message = str,
        line = str,
        lineno = Any(None, as_int),
        colno = Any(None, as_int)
    ),
    Required("encoding", default='utf-8'): str,
    Required("types"): {str:int},
})


# Checker {{{1
class Checker:
    def __init__(self, test_name):
        self.test_name = test_name

    def check(self, expected, result, phase):
        self.expected = expected
        self.result = result
        self.phase = phase
        assert expected == result, self.fail_message()

    def fail_message(self):
        expected = list(render(self.expected).splitlines())
        result = list(render(self.result).splitlines())

        for i, lines in enumerate(zip(expected, result)):
            eline, rline = lines
            if eline != rline:
                break
        else:
            elen = len(expected)
            rlen = len(result)
            i += 1
            if elen > rlen:
                eline = expected[i]
                rline = '❬not available❭'
            else:
                eline = '❬not available❭'
                rline = result[i]

        expected = f"expected[{i}]: {eline}"
        result = f"  result[{i}]: {rline}"
        desc = f"{self.test_name} while {self.phase}"

        return '\n'.join([desc, expected, result])

# TESTS {{{1
@parametrize(
    path = TEST_DIR / TEST_SUITE,
    key = "load_tests",
    schema = schema,
)
def test_nt(tmp_path, load_in, load_out, load_err, encoding, types, request):
    checker = Checker(request.node.callspec.id)

    # check load
    content = b64decode(load_in.encode('ascii'))
    try:
        result = nt.loads(content, top=any)
        if load_err:
            checker.check("@@@ an error @@@", result, "loading")
            return
        else:
            checker.check(load_out, result, "loading")
    except nt.NestedTextError as e:
        result = dict(
            message = e.get_message(),
            line = e.line,
            lineno = e.lineno,
            colno = e.colno
        )
        checker.check(cull(load_err), cull(result), "loading")
        return
    except UnicodeDecodeError as e:
        problematic = e.object[e.start:e.end]
        prefix = e.object[:e.start]
        suffix = e.object[e.start:]
        lineno = prefix.count(b'\n')
        _, _, bol = prefix.rpartition(b'\n')
        eol, _, _ = e.object[e.start:].partition(b'\n')
        line = bol + eol
        colno = line.index(problematic)

        if encoding != 'bytes':
            line = line.decode(encoding)
        else:
            line = line.decode('ascii', errors='backslashreplace')
            load_err['line'] = load_err['line'].encode(
                'ascii', errors='backslashreplace'
            ).decode('ascii')

        result = dict(
            message = e.reason,
            line = line,
            lineno = lineno,
            colno = colno,
        )
        checker.check(load_err, result, "loading")
        return

    # check dump by doing a round-trip through load
    # the stimulus file does not have expected dump results because they can
    # vary between implementations and with dump options.
    try:
        dumped = nt.dumps(result)
    except nt.NestedTextError as e:
        checker.check(None, result, "dumping")

    try:
        result = nt.loads(dumped, top=any)
        checker.check(load_out, result, "re-loading")
    except nt.NestedTextError as e:
        checker.check(None, result, "re-loading")
