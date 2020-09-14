# encoding: utf8

# Imports {{{1
import pytest
import nestedtext
from pathlib import Path
from functools import wraps
from io import StringIO
from textwrap import dedent
from inform import Error, Info, render, indent

test_api = Path(__file__).parent / 'official_tests' / 'api'
import sys; sys.path.append(str(test_api))
import nestedtext_official_tests as official

# Parametrization {{{1

parametrize = pytest.mark.parametrize

# parametrize_load_api {{{2
def parametrize_load_api(f):
    """
    Parametrize a test function with different ways to load NestedText from a
    file.

    In particular, this parametrizes the different load functions (`load` and
    `loads`), and the different types of arguments that both functions accepts.
    The test function will receive the following parameter:

    - ``load_factory``: A callable that can be used to create a parametrized
      load function.  The factory takes two arguments:

      - ``content`: A string in the NestedText format, to be loaded.
      - ``tmp_path``: The ``tmp_path`` pytest fixture.

      The factory returns two values:

      - ``load``: A function that can be called with no arguments to load the
        content given previously to the factory with a unique set of
        parameters.
      - ``source``: A string indicating where the content was loaded from (e.g.
        a temporary file name).
    """
    args = 'load_factory',
    params = []

    def param(f):
        params.append(pytest.param(f, id=f.__name__))
        return f

    def write_file(name):
        def decorator(f):
            @wraps(f)
            def load(content, tmp_path):
                p = tmp_path / name
                p.write_text(content)
                return f(p)
            return load
        return decorator

    @param
    @write_file('load_str.nt')
    def load_str(p):
        return lambda: nestedtext.load(str(p)), str(p)

    @param
    @write_file('load_path.nt')
    def load_path(p):
        return lambda: nestedtext.load(p), str(p)

    @param
    @write_file('load_path_no_ext')
    def load_path_no_ext(p):
        return lambda: nestedtext.load(p), str(p)

    @param
    @write_file('load_fp.nt')
    def load_fp(p):
        def factory():
            with open(p) as f:
                return nestedtext.load(f)
        return factory, str(p)

    @param
    def load_io(content, _):
        io = StringIO(content)
        return lambda: nestedtext.load(io), None

    @param
    def loads(content, _):
        return lambda: nestedtext.loads(content), None

    @param
    def loads_src(content, _):
        return lambda: nestedtext.loads(content, 'SOURCE'), 'SOURCE'

    return parametrize(args, params)(f)

# parametrize_load_success_cases {{{2
def parametrize_load_success_cases(f):
    """
    Parametrize a test function with test cases that should be successfully 
    loaded.

    These test cases are taken from the official NestedText test suite.  The  
    test function will receive the following parameters:

    - ``path_in``: The path to a NestedText file to load.
    - ``data_out``: The data structure that should result from loading the 
      above file.
    """
    cases = official.load_test_cases()
    args = 'path_in', 'data_out'
    params = []
    marks = {}

    for case in official.iter_load_success_cases(cases):
        param = pytest.param(
                case['load']['in']['path'],
                case['load']['out']['data'],
                id=case.id,
                marks=marks.get(case.id, []),
        )
        params.append(param)

    return parametrize(args, params)(f)

# parametrize_load_error_cases {{{2
def parametrize_load_error_cases(f):
    """
    Parametrize a test function with test cases that should not be 
    successfully loaded.

    These test cases are taken from the official NestedText test suite.  The 
    test function will receive the following parameters:

    - ``path_in``: The path to a NestedText file to load.
    - ``lineno``: The line number where the error occurs (1-indexed).
    - ``colno``: The column number where the error occurs (0-indexed).
    - ``message``: The error message that should be produced.
    """
    cases = official.load_test_cases()
    args = 'path_in', 'lineno', 'colno', 'message'
    params = []
    marks = {}

    for case in official.iter_load_error_cases(cases):
        param = pytest.param(
                case['load']['in']['path'],
                case['load']['err']['data']['lineno'],
                case['load']['err']['data']['colno'],
                case['load']['err']['data']['message'],
                id=case.id,
                marks=marks.get(case.id, []),
        )
        params.append(param)

    return parametrize(args, params)(f)

# parametrize_dump_api {{{2
def parametrize_dump_api(f):
    """
    Parametrize a test function with different ways to dump a data structure to 
    NestedText.

    In particular, this parametrizes the different dump functions (`dump` and 
    `dumps`), and the different types of arguments that both functions accepts.  
    The test function will receive the following parameter:

    - ``dump``: A function that will convert a data structure to a string in 
      the NestedText format.  The function takes the following arguments:

      - ``x``: The data structure to dump.
      - ``tmp_path``: The ``tmp_path`` pytest fixture.
      - ``**kwargs``: Any keyword arguments that should be passed to the 
        underlying dump function.
    """
    args = 'dump',
    params = []

    def param(f):
        params.append(pytest.param(f, id=f.__name__))
        return f

    @param
    def dumps(x, tmp_path, **kwargs):
        return nestedtext.dumps(x, **kwargs)

    @param
    def dump_str(x, tmp_path, **kwargs):
        p = tmp_path / 'data.nt'
        nestedtext.dump(x, str(p), **kwargs)
        return p.read_text()

    @param
    def dump_path(x, tmp_path, **kwargs):
        p = tmp_path / 'data.nt'
        nestedtext.dump(x, p, **kwargs)
        return p.read_text()

    @param
    def dump_path_no_ext(x, tmp_path, **kwargs):
        p = tmp_path / 'data'
        nestedtext.dump(x, p, **kwargs)
        return p.read_text()

    @param
    def dump_fp(x, tmp_path, **kwargs):
        p = tmp_path / 'data.nt'
        with open(p, 'w') as f:
            nestedtext.dump(x, f, **kwargs)
        return p.read_text()

    @param
    def dump_io(x, tmp_path, **kwargs):
        io = StringIO()
        nestedtext.dump(x, io, **kwargs)
        return io.getvalue()

    return parametrize(args, params)(f)

# parametrize_dump_success_cases {{{2
def parametrize_dump_success_cases(f):
    """
    Parametrize a test function with test cases that should be successfully 
    dumped.

    These test cases are taken from the official NestedText test suite.  The  
    test function will receive the following parameters:

    - ``data_in``: The data structure to dump.
    - ``path_out``: The path to a file containing the NestedText that 
      should result from dumping the above data structure.
    """
    cases = official.load_test_cases()
    args = 'data_in', 'path_out'
    params = []
    marks = {
        #   'string_5': [pytest.mark.skip],
    }

    for case in official.iter_dump_success_cases(cases):
        param = pytest.param(
                case['dump']['in']['data'],
                case['dump']['out']['path'],
                id=case.id,
                marks=marks.get(case.id, []),
        )
        params.append(param)

    return parametrize(args, params)(f)

# parametrize_dump_error_cases {{{2
def parametrize_dump_error_cases(f):
    """
    Parametrize a test function with test cases that should not be 
    successfully dumped.

    These test cases are taken from the official NestedText test suite.  The 
    test function will receive the following parameters:

    - ``data_in``: The data structure to dump.
    - ``culprit``: The specific object responsible for the error.
    - ``message``: The error message that should be produced.
    """
    cases = official.load_test_cases()
    args = 'data_in', 'culprit', 'message'
    params = []
    marks = {}

    for case in official.iter_dump_error_cases(cases):
        param = pytest.param(
                case['dump']['in']['data'],
                case['dump']['err']['data']['culprit'],
                case['dump']['err']['data']['message'],
                id=case.id,
                marks=marks.get(case.id, []),
        )
        params.append(param)

    return parametrize(args, params)(f)

# parametrize_via_nt {{{2
def parametrize_via_nt(relpath):
    """
    Parametrize a test function with examples loaded from a NestedText file.

    The given file is specified as a path relative to this file.  It must 
    contain a list of dictionaries.  The items in those dictionaries will be 
    provided as parameters to the decorated test.  Each dictionary must have 
    all the same keys.
    """

    def decorator(f):
        import inspect

        # The path is relative to the file the caller is defined in.
        module = inspect.getmodule(f)
        test_path = Path(module.__file__)
        nt_path = test_path.parent / relpath

        raw_params = nestedtext.load(nt_path)
        raw_args = set.union(*(set(x) for x in raw_params)) - {'id'}

        # Make sure there aren't any missing/extra parameters:
        for params in raw_params:
            missing = raw_args - set(params)
            if missing:
                missing_str = ', '.join(f"'{x}'" for x in missing)
                raise ValueError(f"{nt_path}: {f.__name__}: missing parameter(s) {missing_str}")

        args = list(raw_args)
        params = [
                pytest.param(*(x[k] for k in args), id=x.get('id', None))
                for x in raw_params
        ]
        return parametrize(args, params)(f)

    return decorator

# }}}1

# test_load_success_cases {{{1
@parametrize_load_api
@parametrize_load_success_cases
def test_load_success_cases(load_factory, path_in, data_out, tmp_path):
    content = path_in.read_text()
    load, _ = load_factory(content, tmp_path)
    assert load() == data_out

# test_load_error_cases {{{1
@parametrize_load_api
@parametrize_load_error_cases
def test_load_error_cases(load_factory, path_in, lineno, colno, message, tmp_path):
    content = path_in.read_text()
    load, source = load_factory(content, tmp_path)
    lines = content.splitlines()
    line = lines[lineno-1]
    prev_line = lines[lineno-2:lineno-1]

    with pytest.raises(nestedtext.NestedTextError) as exc_info:
        load()

    e = exc_info.value

    assert (f'{source}, {lineno}:' if source else f'{lineno}:') in str(e)
    assert message in str(e)

    assert e.line == line
    assert e.source == source
    assert e.lineno == lineno
    assert e.colno == colno
    assert e.culprit == (source, lineno) if source else (lineno,)
    if lineno is None:
        assert e.codicil == (f'«{line}»',)
    else:
        if colno is None:
            assert e.codicil == (f'{lineno:>4} «{line}»',)
        else:
            assert e.codicil == (
                (f'{lineno-1:>4} «{prev_line[0]}»\n' if prev_line else '') +
                f'{lineno:>4} «{line}»' +
                (f'\n      {" "*colno}▲' if colno is not None else ''),
            )

    assert isinstance(e, Error)
    assert isinstance(e, ValueError)

# test_load_api_errors {{{1
def test_load_api_errors():
    with pytest.raises(FileNotFoundError):
        nestedtext.load('does_not_exist.nt')

    with pytest.raises(TypeError):
        nestedtext.load(['path_1.nt', 'path_2.nt'])

# test_dump_success_cases {{{1
@parametrize_dump_api
@parametrize_dump_success_cases
def test_dump_success_cases(dump, data_in, path_out, tmp_path):
    assert dump(data_in, tmp_path) == path_out.read_text().rstrip('\n')

# test_dump_error_cases {{{1
@parametrize_dump_api
@parametrize_dump_error_cases
def test_dump_error_cases(dump, data_in, culprit, message, tmp_path):
    with pytest.raises(nestedtext.NestedTextError) as exc_info:
        dump(data_in, tmp_path)

    e = exc_info.value

    assert culprit in str(e)
    assert message in str(e)

    assert isinstance(e, Error)
    assert isinstance(e, ValueError)

# test_dump_sort_keys {{{1
@parametrize_dump_api
def test_dump_sort_keys(dump, tmp_path):
    data = dict(cc=3, aaa=1, b=2)

    assert dump(data, tmp_path, sort_keys=False) == dedent('''\
            cc: 3
            aaa: 1
            b: 2
    ''').strip()

    assert dump(data, tmp_path, sort_keys=True) == dedent('''\
            aaa: 1
            b: 2
            cc: 3
    ''').strip()

    assert dump(data, tmp_path, sort_keys=len) == dedent('''\
            b: 2
            cc: 3
            aaa: 1
    ''').strip()

# test_dump_indent {{{1
@parametrize_dump_api
def test_dump_indent(dump, tmp_path):
    x = dict(A=['B'])

    with pytest.raises(AssertionError):
        dump(x, tmp_path, indent=0)

    assert dump(x, tmp_path, indent=1) == "A:\n - B"
    assert dump(x, tmp_path, indent=2) == "A:\n  - B"
    assert dump(x, tmp_path, indent=3) == "A:\n   - B"
    assert dump(x, tmp_path, indent=4) == "A:\n    - B"

# test_dump_renderers {{{1
@parametrize_dump_api
def test_dump_renderers(dump, tmp_path):
    x = {'int': 1, 'float': 1.0, 'str': 'A'}

    assert dump(x, tmp_path, default=str) == dedent('''\
            int: 1
            float: 1.0
            str: A
    ''').strip()

    renderers = {str: lambda x: x.lower()}
    assert dump(x, tmp_path, default=str, renderers=renderers) == dedent('''\
            int: 1
            float: 1.0
            str: a
    ''').strip()

    y = {'info': Info(val=42)}
    renderers = {Info: lambda v: f'Info(\n    val={v.val}\n)'}
    assert dump(y, tmp_path, renderers=renderers) == dedent('''\
            info:
                Info(
                    val=42
                )
    ''').strip()

# test_dump_renderers_err {{{1
@parametrize_dump_api
@parametrize(
        'data, culprit, kwargs', [
            ({'key': 42},   42,   dict(default='strict')),
            ({'key': 42.0}, 42.0, dict(default='strict')),
            ({'key': True}, True, dict(default='strict')),
            ({'key': 42},   42,   dict(default=str, renderers={int: False})),
        ]
)
def test_dump_renderers_err(dump, tmp_path, data, culprit, kwargs):
    with pytest.raises(nestedtext.NestedTextError) as exc:
        dump(data, tmp_path, **kwargs)

    assert str(exc.value) == f"{culprit}: unsupported type."
    assert exc.value.args == (culprit,)
    assert exc.value.kwargs == dict(
        culprit = (str(culprit),),
        template = 'unsupported type.',
    )
    assert isinstance(exc.value, Error)
    assert isinstance(exc.value, ValueError)

# vim: fdm=marker
