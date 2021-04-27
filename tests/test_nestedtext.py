# encoding: utf8

# Imports {{{1
import pytest
import nestedtext as nt
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
        return lambda: nt.load(str(p), top='any'), str(p)

    @param
    @write_file('load_path.nt')
    def load_path(p):
        return lambda: nt.load(p, top='any'), str(p)

    @param
    @write_file('load_path_no_ext')
    def load_path_no_ext(p):
        return lambda: nt.load(p, top='any'), str(p)

    @param
    @write_file('load_fp.nt')
    def load_fp(p):
        def factory():
            with open(p) as f:
                return nt.load(f, top='any')
        return factory, str(p)

    @param
    def load_io(content, _):
        io = StringIO(content)
        return lambda: nt.load(io, top='any'), None

    @param
    def loads(content, _):
        return lambda: nt.loads(content, top='any'), None

    @param
    def loads_src(content, _):
        return lambda: nt.loads(content, top='any', source='SOURCE'), 'SOURCE'

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
        return nt.dumps(x, **kwargs)

    @param
    def dump_str(x, tmp_path, **kwargs):
        p = tmp_path / 'data.nt'
        nt.dump(x, str(p), **kwargs)
        return p.read_text()

    @param
    def dump_path(x, tmp_path, **kwargs):
        p = tmp_path / 'data.nt'
        nt.dump(x, p, **kwargs)
        return p.read_text()

    @param
    def dump_path_no_ext(x, tmp_path, **kwargs):
        p = tmp_path / 'data'
        nt.dump(x, p, **kwargs)
        return p.read_text()

    @param
    def dump_fp(x, tmp_path, **kwargs):
        p = tmp_path / 'data.nt'
        with open(p, 'w') as f:
            nt.dump(x, f, **kwargs)
        return p.read_text()

    @param
    def dump_io(x, tmp_path, **kwargs):
        io = StringIO()
        nt.dump(x, io, **kwargs)
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

        raw_params = nt.load(nt_path, top='any')
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
    prev_lines = lines[:lineno-1]
    prev_lines.reverse()
    prev_line = None
    prev_lineno = lineno
    for l in prev_lines:
        prev_lineno -= 1
        if l.partition('#')[0].strip() != '':
            # it is not blank and it a comments, so its our prev_line
            prev_line = l
            break

    with pytest.raises(nt.NestedTextError) as exc_info:
        load()

    e = exc_info.value

    culprit = e.get_culprit()
    if source:
        assert culprit[0] == source
        assert culprit[1] == lineno
    else:
        assert culprit[0] == lineno
    assert message == e.get_message()
    assert e.line == line
    assert e.source == source
    assert e.lineno == lineno
    assert e.colno == colno
    if lineno is None:
        assert e.codicil == (f'«{line}»',)
    else:
        if colno is None:
            assert e.codicil == (f'{lineno:>4} «{line}»',)
        else:
            assert e.codicil == (
                (f'{prev_lineno:>4} «{prev_line}»\n' if prev_line else '') +
                f'{lineno:>4} «{line}»' +
                (f'\n      {" "*colno}▲' if colno is not None else ''),
            )

    assert isinstance(e, Error)
    assert isinstance(e, ValueError)

# test_load_api_errors {{{1
def test_load_api_errors():
    with pytest.raises(FileNotFoundError):
        nt.load('does_not_exist.nt')

    with pytest.raises(TypeError):
        nt.load(['path_1.nt', 'path_2.nt'])

# test_load_top {{{1
def test_load_top():
    content = ''
    data = nt.loads(content, top='dict')
    assert data == {}
    data = nt.loads(content, top=dict)
    assert data == {}
    data = nt.loads(content, top='list')
    assert data == []
    data = nt.loads(content, top=list)
    assert data == []
    data = nt.loads(content, top='str')
    assert data == ''
    data = nt.loads(content, top=str)
    assert data == ''
    data = nt.loads(content, top='any')
    assert data == None
    data = nt.loads(content, top=any)
    assert data == None

    content = 'key1: value1\nkey2: value2'
    expected = {'key1': 'value1', 'key2': 'value2'}
    data = nt.loads(content, top='dict')
    assert data == expected
    data = nt.loads(content, top=dict)
    assert data == expected
    data = nt.loads(content, top='any')
    assert data == expected
    data = nt.loads(content, top=any)
    assert data == expected
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top='list')
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top=list)
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top='str')
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top=str)

    content = '- value1\n- value2'
    expected = ['value1', 'value2']
    data = nt.loads(content, top='list')
    assert data == expected
    data = nt.loads(content, top=list)
    assert data == expected
    data = nt.loads(content, top='any')
    assert data == expected
    data = nt.loads(content, top=any)
    assert data == expected
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top='dict')
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top=dict)
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top='str')
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top=str)

    content = '> this is a test\n> this is only a test'
    expected = 'this is a test\nthis is only a test'
    data = nt.loads(content, top='str')
    assert data == expected
    data = nt.loads(content, top=str)
    assert data == expected
    data = nt.loads(content, top='any')
    assert data == expected
    data = nt.loads(content, top=any)
    assert data == expected
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top='dict')
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top=dict)
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top='list')
    with pytest.raises(nt.NestedTextError):
        data = nt.loads(content, top=list)

def test_load_top_str():
    data = nt.loads('> hello', 'str')
    assert data == 'hello'

    data = nt.loads('', top='str')
    assert data == ''

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('- hello', 'str')
    assert e.value.get_message() == 'content must start with greater-than sign (>).'

def test_load_top_list():
    data = nt.loads('- hello', 'list')
    assert data == ['hello']

    data = nt.loads('', top='list')
    assert data == []

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('> hello', 'list')
    assert e.value.get_message() == 'content must start with dash (-).'

def test_load_top_dict():
    data = nt.loads('key: hello', 'dict')
    assert data == {'key': 'hello'}

    data = nt.loads('', top='dict')
    assert data == {}

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('> hello', 'dict')
    assert e.value.get_message() == 'content must start with key.'

def test_load_top_default():
    data = nt.loads('key: hello')
    assert data == {'key': 'hello'}

    data = nt.loads('')
    assert data == {}

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('> hello')
    assert e.value.get_message() == 'content must start with key.'

def test_load_top_any():
    data = nt.loads('> hello', 'any')
    assert data == 'hello'

    data = nt.loads('- hello', 'any')
    assert data == ['hello']

    data = nt.loads('key: hello', 'any')
    assert data == {'key': 'hello'}

    data = nt.loads('', 'any')
    assert data == None


# test_dump_success_cases {{{1
@parametrize_dump_api
@parametrize_dump_success_cases
def test_dump_success_cases(dump, data_in, path_out, tmp_path):
    assert dump(data_in, tmp_path, default='strict') == path_out.read_text().rstrip('\n')

# test_dump_error_cases {{{1
@parametrize_dump_api
@parametrize_dump_error_cases
def test_dump_error_cases(dump, data_in, culprit, message, tmp_path):
    with pytest.raises(nt.NestedTextError) as exc_info:
        dump(data_in, tmp_path, default='strict')

    e = exc_info.value

    if culprit is None:
        culprit = ()
    elif not isinstance(culprit, tuple):
        culprit = (culprit,)
    assert culprit == e.get_culprit()
    assert message == e.get_message()

    assert isinstance(e, Error)
    assert isinstance(e, ValueError)

# test_dump_default {{{1
@parametrize_dump_api
def test_dump_default(dump, tmp_path):
    data = dict(none=None, true=True, false=False, empty_dict={}, empty_list=[])

    assert dump(data, tmp_path) == dedent('''\
            none:
            true: True
            false: False
            empty_dict:
                {}
            empty_list:
                []
    ''').strip()

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

    assert dump(data, tmp_path, sort_keys=False, width=80) == '{cc: 3, aaa: 1, b: 2}'
    assert dump(data, tmp_path, sort_keys=True, width=80) == '{aaa: 1, b: 2, cc: 3}'
    assert dump(data, tmp_path, sort_keys=len, width=80) == '{b: 2, cc: 3, aaa: 1}'

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
    assert dump(x, tmp_path, default=str, renderers=renderers, width=80) == '{int: 1, float: 1.0, str: a}'

    y = {'info': Info(val=42)}
    renderers = {Info: lambda v: f'Info(\n    val={v.val}\n)'}
    assert dump(y, tmp_path, renderers=renderers) == dedent('''\
        info:
            Info(
                val=42
            )
    ''').strip()
    assert dump(y, tmp_path, renderers=renderers, width=80) == dedent('''\
        info:
            Info(
                val=42
            )
    ''').strip()
    renderers = {Info: lambda v: f'Info(val={v.val})'}
    assert dump(y, tmp_path, renderers=renderers, width=80) == '{info: Info(val=42)}'

# test_dump_renderers_err {{{1
@parametrize_dump_api
@parametrize(
        'data, culprit, kwargs', [
            ({'key': 42},   42,   dict(default='strict')),
            ({'key': 42.0}, 42.0, dict(default='strict')),
            ({'key': True}, True, dict(default='strict')),
            ({'key': 42},   42,   dict(default=str, renderers={int: False})),
            ({'key': 42},   42,   dict(default='strict', width=80)),
            ({'key': 42.0}, 42.0, dict(default='strict', width=80)),
            ({'key': True}, True, dict(default='strict', width=80)),
            ({'key': 42},   42,   dict(default=str, renderers={int: False}, width=80)),
        ]
)
def test_dump_renderers_err(dump, tmp_path, data, culprit, kwargs):
    with pytest.raises(nt.NestedTextError) as exc:
        dump(data, tmp_path, **kwargs)

    assert str(exc.value) == f"{culprit}: unsupported type."
    assert exc.value.args == (culprit,)
    assert exc.value.kwargs == dict(
        culprit = (str(culprit),),
        template = 'unsupported type.',
    )
    assert isinstance(exc.value, Error)
    assert isinstance(exc.value, ValueError)

# test_dump_width {{{1
@parametrize_dump_api
@parametrize(
        'given, expected, kwargs', [
            (['a[b'], '- a[b', dict(width=80)),
            (['a]b'], '- a]b', dict(width=80)),
            (['a{b'], '- a{b', dict(width=80)),
            (['a}b'], '- a}b', dict(width=80)),
            ({'a,b'}, '- a,b', dict(width=80)),
            ({'a[b': 0}, 'a[b: 0', dict(width=80)),
            ({'a]b': 0}, 'a]b: 0', dict(width=80)),
            ({'a{b': 0}, 'a{b: 0', dict(width=80)),
            ({'a}b': 0}, 'a}b: 0', dict(width=80)),
            ({'a,b': 0}, 'a,b: 0', dict(width=80)),
            ({'a:b': 0}, 'a:b: 0', dict(width=80)),
            ({0: 'a[b'}, '0: a[b', dict(width=80)),
            ({0: 'a]b'}, '0: a]b', dict(width=80)),
            ({0: 'a{b'}, '0: a{b', dict(width=80)),
            ({0: 'a}b'}, '0: a}b', dict(width=80)),
            ({0: 'a,b'}, '0: a,b', dict(width=80)),
            ({0: 'a:b'}, '0: a:b', dict(width=80)),
            ([' ab'], '-  ab', dict(width=80)),
            ({'ab '}, '- ab ', dict(width=80)),
            ({0: ' ab'}, '0:  ab', dict(width=80)),
            ({0: 'ab '}, '0: ab ', dict(width=80)),
            ({0: 'ab '}, '0: ab ', dict(width=80)),

            ([], '[]', dict(width=80)),
            ([''], '[, ]', dict(width=80)),
            (['a'], '[a]', dict(width=80)),
            ([':'], '[:]', dict(width=80)),
            ([[]], '[[]]', dict(width=80)),
            ([['a']], '[[a]]', dict(width=80)),
            ([{}], '[{}]', dict(width=80)),
            ([{'a': '0'}], '[{a: 0}]', dict(width=80)),
            (['a', 'b'], '[a, b]', dict(width=80)),
            (['', ''], '[, , ]', dict(width=80)),
            ([[], []], '[[], []]', dict(width=80)),
            ([['a', 'b'], ['c', 'd']], '[[a, b], [c, d]]', dict(width=80)),
            ([{}, {}], '[{}, {}]', dict(width=80)),
            ([{'a': '0', 'b': '1'}, {'c': '2', 'd': '3'}], '[{a: 0, b: 1}, {c: 2, d: 3}]', dict(width=80)),
            (['a', []], '[a, []]', dict(width=80)),
            ([[], {}], '[[], {}]', dict(width=80)),
            ([{}, 'b'], '[{}, b]', dict(width=80)),
            (['a', 'b'], '[a, b]', dict(width=80)),
            (['a', 'b', ''], '[a, b, , ]', dict(width=80)),
            ([['11', '12', '13'], ['21', '22', '23'], ['31', '32', '33']], '[[11, 12, 13], [21, 22, 23], [31, 32, 33]]', dict(width=80)),
            ({}, '{}', dict(width=80)),
            ({'': ''}, '{: }', dict(width=80)),
            ({'a': '0'}, '{a: 0}', dict(width=80)),
            ({'a': 'k'}, '{a: k}', dict(width=80)),
            ({'a': []}, '{a: []}', dict(width=80)),
            ({'a': ['b']}, '{a: [b]}', dict(width=80)),
            ({'a': {}}, '{a: {}}', dict(width=80)),
            ({'a': {'b': '1'}}, '{a: {b: 1}}', dict(width=80)),
            ({'a': '0', 'b': '1'}, '{a: 0, b: 1}', dict(width=80)),
            ({'a': {'A': '0'}, 'b': {'B': '1'}}, '{a: {A: 0}, b: {B: 1}}', dict(width=80)),
            ({'a': ['1', '2', '3'], 'b': ['4', '5', '6']}, '{a: [1, 2, 3], b: [4, 5, 6]}', dict(width=80)),
            ({'a': '0', 'b': '1'}, '{a: 0, b: 1}', dict(width=80)),
            ({'a': [], 'b': []}, '{a: [], b: []}', dict(width=80)),
            ({'a': ['0', '1'], 'b': ['2', '3']}, '{a: [0, 1], b: [2, 3]}', dict(width=80)),
            ({'a': {}, 'b': {}}, '{a: {}, b: {}}', dict(width=80)),
            ({'a': {'b': '0', 'c': '1'}, 'd': {'e': '2', 'f': '3'}}, '{a: {b: 0, c: 1}, d: {e: 2, f: 3}}', dict(width=80)),
            ({'a': '0', 'b': []}, '{a: 0, b: []}', dict(width=80)),
            ({'a': [], 'b': {}}, '{a: [], b: {}}', dict(width=80)),
            ({'a': {}, 'b': '0'}, '{a: {}, b: 0}', dict(width=80)),

            (
                [['11', '12', '13'], ['21', '22', '23'], ['31', '32', '33']],
                dedent("""
                    -
                        - 11
                        - 12
                        - 13
                    -
                        - 21
                        - 22
                        - 23
                    -
                        - 31
                        - 32
                        - 33
                """).strip(),
                dict(width=20)
            ),
            (
                {'a': {'b': '0', 'c': '1'}, 'd': {'e': '2', 'f': '3'}},
                dedent("""
                    a:
                        {b: 0, c: 1}
                    d:
                        {e: 2, f: 3}
                """).strip(),
                dict(width=20)
            ),
            (
                {'a': {'b': '0', 'c': '1'}, 'd': {'e': '2', 'f': '3'}},
                dedent("""
                    a:
                        b: 0
                        c: 1
                    d:
                        e: 2
                        f: 3
                """).strip(),
                dict(width=5)
            ),

            ([None], '[, ]', dict(width=80)),
            ([Info(arg='a'), Info(arg='b')], "[Info(arg='a'), Info(arg='b')]", dict(width=80, default=repr)),
            ({'a': Info(arg=0), 'b': Info(arg=1)}, "{a: Info(arg=0), b: Info(arg=1)}", dict(width=80, default=repr)),
        ]
)
def test_dump_width(dump, tmp_path, given, expected, kwargs):
    assert dump(given, tmp_path, **kwargs) == expected

# vim: fdm=marker

