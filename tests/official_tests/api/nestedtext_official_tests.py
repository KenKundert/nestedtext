#!/usr/bin/env python3

import json
from pathlib import Path
from natsort import natsorted

# load_test_cases {{{1
def load_test_cases(families=None):
    root_dir = Path(__file__).parent.parent
    test_dir = root_dir / 'test_cases'
    test_cases = [
            TestCase(d)
            for d in natsorted(test_dir.iterdir())
            if not families or any(d.name.startswith(f) for f in families)
    ]
    return test_cases

# load_json {{{1
def load_json(path):
    try:
        return json.loads(path.read_text())
    except json.JSONDecodeError as err:
        # If there's a problem, include the path in the error message.
        raise json.JSONDecodeError(
                f"{path}: {err.msg}",
                err.doc,
                err.pos,
        ) from None

# load_py {{{1
def load_py(path):
    with open(path, 'rb') as f:
        code = compile(f.read(), str(path), 'exec')
        globals = {}; locals = {}
        exec(code, globals, locals)

    try:
        return locals['data']
    except KeyError:
        raise AssertionError(f"{path}: 'data' not defined")


# iter_load_success_cases {{{1
def iter_load_success_cases(cases):
    yield from (x for x in cases if x.is_load_success())

# iter_load_error_cases {{{1
def iter_load_error_cases(cases):
    yield from (x for x in cases if x.is_load_error())

# iter_dump_success_cases {{{1
def iter_dump_success_cases(cases):
    yield from (x for x in cases if x.is_dump_success())

# iter_dump_error_cases {{{1
def iter_dump_error_cases(cases):
    yield from (x for x in cases if x.is_dump_error())


# TestCase {{{1
class TestCase:

    def __init__(self, dir):
        self.case = case = {}
        self.case['path'] = {}

        self.dir = Path(dir)
        self.id = self.dir.name
        if '_' in self.id:
            self.family, self.num = self.id.rsplit('_', 1)
        else:
            self.family = self.id
            self.num = None

        load_in = dir / 'load_in.nt'
        load_out = dir / 'load_out.json'
        load_err = dir / 'load_err.json'

        dump_in_json = dir / 'dump_in.json'
        dump_in_py = dir / 'dump_in.py'
        dump_out = dir / 'dump_out.nt'
        dump_err = dir / 'dump_err.json'

        if load_in.exists():
            case['load'] = {}
            case['load']['in'] = {
                    'path': load_in,
            }

            if load_out.exists() and load_err.exists():
                raise AssertionError(f"{dir}: ambiguous expected result: both '{load_out.name}' and '{load_err.name}' are present")
            elif load_out.exists():
                case['load']['out'] = {
                        'path': load_out,
                        'data': load_json(load_out),
                }
            elif load_err.exists():
                case['load']['err'] = {
                        'path': load_err,
                        'data': load_json(load_err),
                }
            else:
                raise AssertionError(f"{dir}: no expected result: neither '{load_out.name}' nor '{load_err.name}' are present")

        if dump_in_json.exists() or dump_in_py.exists():
            case['dump'] = {}

            if dump_in_json.exists() and dump_in_py.exists():
                raise AssertionError(f"{dir}: ambiguous input: both '{dump_in_json.name}' and '{dump_in_py.name}' are present")
            elif dump_in_json.exists():
                case['dump']['in'] = {
                        'path': dump_in_json,
                        'data': load_json(dump_in_json),
                }
            elif dump_in_py.exists():
                case['dump']['in'] = {
                        'path': dump_in_py,
                        'data': load_py(dump_in_py),
                }
            
            if dump_out.exists() and dump_err.exists():
                raise AssertionError(f"{dir}: ambiguous expected result: both '{dump_out.name}' and '{dump_err.name}' are present")
            elif dump_out.exists():
                case['dump']['out'] = {
                        'path': dump_out,
                }
            elif dump_err.exists():
                case['dump']['err'] = {
                        'path': dump_err,
                        'data': load_json(dump_err),
                }
            else:
                raise AssertionError(f"{dir}: no expected result: neither '{dump_out.name}' nor '{dump_err.name}' are present")

        expected_files = {
                load_in,
                load_out,
                load_err,

                dump_in_json,
                dump_in_py,
                dump_out,
                dump_err,

                dir / 'README',
                dir / '__pycache__',
        }
        actual_files = set(dir.glob('*'))
        unexpected_files = actual_files - expected_files
        if unexpected_files:
            raise AssertionError(f"{dir}: found unexpected files: {quoted_join(unexpected_files)}")

    def __getitem__(self, key):
        return self.case[key]

    def __contains__(self, key):
        return key in self.case

    def is_load_case(self):
        return 'load' in self

    def is_dump_case(self):
        return 'dump' in self

    def is_success_case(self):
        return self.is_load_success() or self.is_dump_success()

    def is_error_case(self):
        return self.is_load_error() or self.is_dump_error()

    def is_load_success(self):
        return ('load' in self) and ('out' in self['load'])

    def is_load_error(self):
        return ('load' in self) and ('err' in self['load'])

    def is_dump_success(self):
        return ('dump' in self) and ('out' in self['dump'])

    def is_dump_error(self):
        return ('dump' in self) and ('err' in self['dump'])


def quoted_join(paths):
    return ', '.join(f"'{x.name}'" for x in sorted(paths))


# vim: fdm=marker
