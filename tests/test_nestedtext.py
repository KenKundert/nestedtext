# encoding: utf8

# Imports {{{1
import pytest
import nestedtext as nt
import arrow
from pathlib import Path
from functools import wraps
from io import StringIO
from textwrap import dedent
from inform import Error, Info, render, indent, join
from quantiphy import Quantity

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
        return nt.dumps(x, **kwargs) + '\n'

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

# Test load {{{1
# test_load_success_cases {{{2
@parametrize_load_api
@parametrize_load_success_cases
def test_load_success_cases(load_factory, path_in, data_out, tmp_path):
    content = path_in.read_text()
    load, _ = load_factory(content, tmp_path)
    assert load() == data_out

# test_load_error_cases {{{2
@parametrize_load_api
@parametrize_load_error_cases
def test_load_error_cases(load_factory, path_in, lineno, colno, message, tmp_path):
    content = path_in.read_text()
    load, source = load_factory(content, tmp_path)
    lines = content.splitlines()
    line = lines[lineno]
    prev_lines = lines[:lineno]
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
        assert culprit[1] == lineno+1
    else:
        assert culprit[0] == lineno+1
    assert message == e.get_message()
    assert e.line == line
    assert e.source == source
    assert e.lineno == lineno
    assert e.colno == colno
    if e.prev_line:
        assert e.prev_line == prev_line
    else:
        prev_line = None
    if lineno is None:
        assert e.codicil == (f'❬{line}❭',)
    else:
        if colno is None:
            assert e.codicil == (f'{lineno+1:>4} ❬{line}❭',)
        else:
            line = line.replace('\t', '→')
            assert len(e.codicil) == 1
            assert e.codicil[0].endswith(
                (f'{prev_lineno+1:>4} ❬{prev_line}❭\n' if prev_line else '') +
                f'{lineno+1:>4} ❬{line}❭' +
                (f'\n      {" "*colno}△' if colno is not None else '')
            )

    assert isinstance(e, Error)
    assert isinstance(e, ValueError)

# test_load_api_errors {{{2
def test_load_api_errors():
    with pytest.raises(FileNotFoundError):
        nt.load('does_not_exist.nt')

    with pytest.raises(TypeError):
        nt.load(['path_1.nt', 'path_2.nt'])

# test_load_nones {{{2
@parametrize(
    'given, expected, kwargs', [
        ( '',           {},              dict(top=dict) ),
        ( '',           [],              dict(top=list) ),
        ( '',           "",              dict(top=str)  ),
        ( '',           None,            dict(top=any) ),
        ( '-',          [''],            dict(top=list) ),
        ( '-',          [''],            dict(top=any)  ),
        ( 'key:',       {'key':''},      dict(top=dict) ),
        ( 'None: val',  {'None':'val'},  dict(top=dict) ),  # ← wrong?
    ]
)
def test_load_nones(given, expected, kwargs):
    assert nt.loads(given, **kwargs) == expected

# test_load_top {{{2
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

    content = '{key1: value1, key2: value2}'
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

    content = '[value1, value2]'
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

# test_load_top_str {{{3
def test_load_top_str():
    data = nt.loads('> hello', 'str')
    assert data == 'hello'

    data = nt.loads('', top='str')
    assert data == ''

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('- hello', 'str')
    assert e.value.get_message() == 'content must start with greater-than sign (>).'

# test_load_top_list {{{3
def test_load_top_list():
    data = nt.loads('- hello', 'list')
    assert data == ['hello']

    data = nt.loads('', top='list')
    assert data == []

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('> hello', 'list')
    assert e.value.get_message() == 'content must start with dash (-) or bracket ([).'

# test_load_top_dict {{{3
def test_load_top_dict():
    data = nt.loads('key: hello', 'dict')
    assert data == {'key': 'hello'}

    data = nt.loads('', top='dict')
    assert data == {}

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('> hello', 'dict')
    assert e.value.get_message() == 'content must start with key or brace ({).'

# test_load_top_any {{{3
def test_load_top_any():
    data = nt.loads('> hello', 'any')
    assert data == 'hello'

    data = nt.loads('- hello', 'any')
    assert data == ['hello']

    data = nt.loads('key: hello', 'any')
    assert data == {'key': 'hello'}

    data = nt.loads('', 'any')
    assert data == None


# test_load_top_default {{{3
def test_load_top_default():
    data = nt.loads('key: hello')
    assert data == {'key': 'hello'}

    data = nt.loads('')
    assert data == {}

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads('> hello')
    assert e.value.get_message() == 'content must start with key or brace ({).'

# test_load_duplicates {{{2
def test_load_duplicates():
    def de_dup(key, state):
        if key not in state:
            state[key] = 1
        state[key] += 1
        return f"{key} — #{state[key]}"

    def ignore_dup(key, state):
        return None

    def replace_dup(key, state):
        return key

    def dup_is_error(key, state):
        raise KeyError(key)

    content = 'key: hello\nkey: goodbye'

    data = nt.loads(content, on_dup='ignore')
    assert data == {'key': 'hello'}

    data = nt.loads(content, on_dup=ignore_dup)
    assert data == {'key': 'hello'}

    data = nt.loads(content, on_dup='replace')
    assert data == {'key': 'goodbye'}

    data = nt.loads(content, on_dup=replace_dup)
    assert data == {'key': 'goodbye'}

    data = nt.loads(content, on_dup=de_dup)
    assert data == {'key': 'hello', 'key — #2': 'goodbye'}

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads(content)
    assert e.value.get_message() == 'duplicate key: key.'
    assert e.value.source == None

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads(content, on_dup='error')
    assert e.value.get_message() == 'duplicate key: key.'
    assert e.value.source == None

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads(content, on_dup=dup_is_error)
    assert e.value.get_message() == 'duplicate key: key.'
    assert e.value.source == None

    with pytest.raises(nt.NestedTextError) as e:
        nt.loads(content, source='nantucket')
    assert e.value.get_message() == 'duplicate key: key.'
    assert e.value.source == 'nantucket'

# test_load_inline {{{2
@parametrize(
    'given, expected, kwargs', [
        (
            '- v',
            dict(message = 'content must start with key or brace ({).'),
            dict(top='dict'),
        ),
        (
            '> v',
            dict(message = 'content must start with key or brace ({).'),
            dict(top='dict'),
        ),
        (
            '[v]',
            dict(message = 'content must start with key or brace ({).'),
            dict(top='dict'),
        ),
        (
            'k: v',
            dict(message = 'content must start with dash (-) or bracket ([).'),
            dict(top='list'),
        ),
        (
            '{k: v}',
            dict(message = 'content must start with dash (-) or bracket ([).'),
            dict(top='list'),
        ),
        (
            '> v',
            dict(message = 'content must start with dash (-) or bracket ([).'),
            dict(top='list'),
        ),
        (
            'k: v',
            dict(message = 'content must start with greater-than sign (>).'),
            dict(top='str'),
        ),
        (
            '{k: v}',
            dict(message = 'content must start with greater-than sign (>).'),
            dict(top='str'),
        ),
        (
            '- v',
            dict(message = 'content must start with greater-than sign (>).'),
            dict(top='str'),
        ),
        (
            '[v]',
            dict(message = 'content must start with greater-than sign (>).'),
            dict(top='str'),
        ),
        (
            '{k: v1, k: v2}',
            dict(
                message = 'duplicate key: k.',
                colno = 7,
            ),
            dict(top=any),
        ),
        (
            '{k:v1,k:v2}',
            dict(
                message = 'duplicate key: k.',
                source = 'src_filename',
                colno = 6,
            ),
            dict(top=any, source='src_filename'),
        ),
    ]
)
def test_load_inline_errors(given, expected, kwargs):
    if not kwargs:
        kwargs = dict(top=any)

    with pytest.raises(nt.NestedTextError) as exc_info:
        nt.loads(given, **kwargs)

    e = exc_info.value
    assert isinstance(e, Error), given
    assert isinstance(e, ValueError), given

    result = dict(
        lineno = e.lineno,
        colno = e.colno,
        message = e.get_message()
    )
    if e.source:
        result['source'] = e.source
    if 'lineno' not in expected:
        expected['lineno'] = 0
    if 'colno' not in expected:
        expected['colno'] = None
    assert result == expected, given

# test_keymaps {{{2
def test_keymaps():
    document_with_linenos = dedent("""
        0   # Contact information for our officers
        1
        2   president:
        3       name: Katheryn McDaniel
        4       address:
        5           > 138 Almond Street
        6           > Topeka, Kansas 20697
        7       phone:
        8           cell phone: 1-210-555-5297
        9           work phone: 1-210-555-3423
        10          home phone: 1-210-555-8470
        11              # Katheryn prefers that we always call her on her cell phone.
        12      email: KateMcD@aol.com
        13      kids:
        14          - Joanie
        15          - Terrance
        16
        17  vice president:
        18      name: Margaret Hodge
        19      address:
        20          > 2586 Marigold Lane
        21          > Topeka, Kansas 20697
        22      phone:
        23          {cell phone: 1-470-555-0398, home phone: 1-470-555-7570}
        24      email: margaret.hodge@ku.edu
        25      kids:
        26          [Arnie, Zach, Maggie]
        27
        28  treasurer:
        29      -
        30          name: Fumiko Purvis
        31          address:
        32              > 3636 Buffalo Ave
        33              > Topeka, Kansas 20692
        34          phone: 1-268-555-0280
        35          email: fumiko.purvis@hotmail.com
        36          additional roles:
        37              - accounting task force
        38
        39  : multiline
        40  : key
        41      > it's value

    """).strip()

    # remove line numbers from NestedText document
    doc_lines = [l[4:] for l in document_with_linenos.splitlines()]
    document = '\n'.join(doc_lines)
    print(document)


    #   keys                                  key    value    lines
    #                                         r  c    r  c    k       v
    cases = """
        president                           → 2  0    3  4    2  3    3  4
        president name                      → 3  4    3  10   3  4    3  4
        president address                   → 4  4    5  10   4  5    5  7
        president phone                     → 7  4    8  8    7  8    8  9
        president phone cell_phone          → 8  8    8  20   8  9    8  9
        president phone work_phone          → 9  8    9  20   9  10   9  10
        president phone home_phone          → 10 8    10 20   10 11   10 11
        president email                     → 12 4    12 11   12 13   12 13
        president kids                      → 13 4    14 8    13 14   14 15
        president kids 0                    → 14 8    14 10   14 15   14 15
        president kids 1                    → 15 8    15 10   15 16   15 16
        vice_president                      → 17 0    18 4    17 18   18 19
        vice_president name                 → 18 4    18 10   18 19   18 19
        vice_president address              → 19 4    20 10   19 20   20 22
        vice_president phone                → 22 4    23 8    22 23   23 24
        vice_president phone cell_phone     → 23 9    23 21   23 24   23 24
        vice_president phone home_phone     → 23 37   23 49   23 24   23 24
        vice_president email                → 24 4    24 11   24 25   24 25
        vice_president kids                 → 25 4    26 8    25 26   26 27
        vice_president kids 0               → 26 9    26 9    26 27   26 27
        vice_president kids 1               → 26 16   26 16   26 27   26 27
        vice_president kids 2               → 26 22   26 22   26 27   26 27
        treasurer                           → 28 0    29 4    28 29   29 30
        treasurer 0                         → 29 4    30 8    29 30   30 31
        treasurer 0 name                    → 30 8    30 14   30 31   30 31
        treasurer 0 address                 → 31 8    32 14   31 32   32 34
        treasurer 0 phone                   → 34 8    34 15   34 35   34 35
        treasurer 0 email                   → 35 8    35 15   35 36   35 36
        treasurer 0 additional_roles        → 36 8    37 12   36 37   37 38
        treasurer 0 additional_roles 0      → 37 12   37 14   37 38   37 38
        multiline↲key                       → 39 0    41 6    39 41   41 42
    """.strip().splitlines()

    def fix_key(key, normalize):
        key = key.replace('↲', '\n')
        try:
            return int(key)
        except:
            if normalize:
                return key.replace('_', ' ')
            else:
                return key

    def normalize_key(key, parent_keys):
        return key.replace(' ', '_')

    def check_result(keys, expected, addresses):
        location = keymap[keys]

        # separate expected into 8 expected values
        key_lineno, key_colno, lineno, colno, \
        key_first_line, key_last_line, value_first_line, value_last_line \
            = tuple(int(n) for n in expected.split())

        # check raw row and column numbers
        assert location.as_tuple() == (lineno, colno), keys
        assert location.as_tuple('value') == (lineno, colno), keys
        assert location.as_tuple('key') == (key_lineno, key_colno), keys

        # check rendered row and column numbers
        assert location.line.render() == f'{lineno+1:>4} ❬{doc_lines[lineno]}❭'
        rendered = f"{lineno+1:>4} ❬{doc_lines[lineno]}❭\n      {colno*' '}△"
        assert location.line.render(colno) == rendered
        assert location.as_line() == rendered
        assert location.as_line('value') == rendered
        rendered = f"{key_lineno+1:>4} ❬{doc_lines[key_lineno]}❭\n      {key_colno*' '}△"
        assert location.as_line('key') == rendered
        assert str(location.line) == doc_lines[lineno]
        assert repr(location.line) == f'Line({lineno+1}: ❬{doc_lines[lineno]}❭)'
        assert repr(location) == f"Location(lineno={lineno}, colno={colno}, key_lineno={key_lineno}, key_colno={key_colno})"

        # check line numbers as tuples
        assert nt.get_lines_from_keys(addresses, keys, keymap, kind='key') == (key_first_line, key_last_line), keys
        assert nt.get_lines_from_keys(addresses, keys, keymap, kind='value') == (value_first_line, value_last_line), keys

        # check line numbers as strings
        if key_first_line+1 != key_last_line:
            key_lines = f"{key_first_line+1}-{key_last_line}"
        else:
            key_lines = str(key_last_line)
        assert nt.get_lines_from_keys(addresses, keys, keymap, kind='key', sep='-') == key_lines, keys
        if value_first_line+1 != value_last_line:
            value_lines = f"{value_first_line+1}-{value_last_line}"
        else:
            value_lines = str(value_last_line)
        assert nt.get_lines_from_keys(addresses, keys, keymap, kind='value', sep='-') == value_lines, keys

    # Without key normalization
    keymap = {}
    addresses = nt.loads(document, keymap=keymap)
    for case in cases:
        given, expected = case.split('→')
        keys = tuple(fix_key(n, True) for n in given.split())
        check_result(keys, expected, addresses)

    # With key normalization
    keymap = {}
    addresses = nt.loads(document, keymap=keymap, normalize_key= normalize_key)
    for case in cases:
        given, expected = case.split('→')
        keys = tuple(fix_key(n, False) for n in given.split())
        check_result(keys, expected, addresses)


# test_key_utilities {{{2
def test_key_utilities():
    document = dedent("""
        KEY 1:
            key 1a: 1
            KEY 1B: 2
            Key-1c:
                - a
                - b
        user  Names:
            Anastacia Pickett__Cheek:
                key 2a: 5
                KEY-2B: 6
        : Scores :
            : Day One:
            :   25 Jan 2022
                -
                    Sabercats : 63
                    Rattlers: 49
                -
                    Predators : 42
                    Storm: 35
    """)
    expected_normalized_keys = [
        ('key_1',),
        ('key_1', 'key_1a'),
        ('key_1', 'key_1b'),
        ('key_1', 'key_1c'),
        ('key_1', 'key_1c', 0),
        ('key_1', 'key_1c', 1),
        ('user_names',),
        ('user_names', 'Anastacia Pickett Cheek'),
        ('user_names', 'Anastacia Pickett Cheek', 'key_2a'),
        ('user_names', 'Anastacia Pickett Cheek', 'key_2b'),
        ("scores",),
        ("scores", "day_one_25_jan_2022"),
        ("scores", "day_one_25_jan_2022", 0),
        ("scores", "day_one_25_jan_2022", 0, 'sabercats'),
        ("scores", "day_one_25_jan_2022", 0, 'rattlers'),
        ("scores", "day_one_25_jan_2022", 1),
        ("scores", "day_one_25_jan_2022", 1, 'predators'),
        ("scores", "day_one_25_jan_2022", 1, 'storm'),
    ]
    expected_original_keys = [
        ('KEY 1',),
        ('KEY 1', 'key 1a'),
        ('KEY 1', 'KEY 1B'),
        ('KEY 1', 'Key-1c'),
        ('KEY 1', 'Key-1c', 0),
        ('KEY 1', 'Key-1c', 1),
        ('user  Names',),
        ('user  Names', 'Anastacia Pickett__Cheek'),
        ('user  Names', 'Anastacia Pickett__Cheek', 'key 2a'),
        ('user  Names', 'Anastacia Pickett__Cheek', 'KEY-2B'),
        ("Scores :",),
        ("Scores :", "Day One:\n  25 Jan 2022"),
        ("Scores :", "Day One:\n  25 Jan 2022", 0),
        ("Scores :", "Day One:\n  25 Jan 2022", 0, 'Sabercats'),
        ("Scores :", "Day One:\n  25 Jan 2022", 0, 'Rattlers'),
        ("Scores :", "Day One:\n  25 Jan 2022", 1),
        ("Scores :", "Day One:\n  25 Jan 2022", 1, 'Predators'),
        ("Scores :", "Day One:\n  25 Jan 2022", 1, 'Storm'),
    ]
    expected_values = {
        ('key_1',): dict,
        ('key_1', 'key_1a'): '1',
        ('key_1', 'key_1b'): '2',
        ('key_1', 'key_1c'): list,
        ('key_1', 'key_1c', 0): 'a',
        ('key_1', 'key_1c', 1): 'b',
        ('user_names',): dict,
        ('user_names', 'Anastacia Pickett Cheek'): dict,
        ('user_names', 'Anastacia Pickett Cheek', 'key_2a'): '5',
        ('user_names', 'Anastacia Pickett Cheek', 'key_2b'): '6',
        ("scores",): dict,
        ("scores", "day_one_25_jan_2022"): list,
        ("scores", "day_one_25_jan_2022", 0): dict,
        ("scores", "day_one_25_jan_2022", 0, 'sabercats'): '63',
        ("scores", "day_one_25_jan_2022", 0, 'rattlers'): '49',
        ("scores", "day_one_25_jan_2022", 1): dict,
        ("scores", "day_one_25_jan_2022", 1, 'predators'): '42',
        ("scores", "day_one_25_jan_2022", 1, 'storm'): '35',
    }

    unknown_norm = ('user_names', 'Anastacia Pickett Cheek', 'unknown key')
    unknown_orig = ('user  Names', 'Anastacia Pickett__Cheek', 'unknown key')
    unknown_index = ('scores', 3)

    def normalize_key(key, parent_keys):
        if parent_keys == ('user_names',):
            return ' '.join(key.replace('_', ' ').split())
        else:
            return '_'.join(key.lower().replace('-', ' ').replace(':', ' ').split())

    keymap = dict()
    data = nt.loads(document, keymap=keymap, normalize_key=normalize_key)
    #print('KEYMAP:', keymap)
    for index, normalized_keys in enumerate(expected_normalized_keys):
        print(normalized_keys)

        # check get_original_keys
        original_keys = nt.get_original_keys(normalized_keys, keymap, strict=True)
        assert original_keys == expected_original_keys[index]
        assert unknown_orig == nt.get_original_keys(unknown_norm, keymap, strict=False)
        with pytest.raises(KeyError) as exception:
            nt.get_original_keys(unknown_norm, keymap, strict=True)
        assert exception.value.args[0] == unknown_norm

        # check get_value_from_keys
        value = nt.get_value_from_keys(data, normalized_keys)
        expected_value = expected_values[normalized_keys]
        try:
            assert isinstance(value, expected_value)
        except TypeError:
            assert value == expected_value

        # print(value)
        # try:
        #     assert index == int(value)
        # except (TypeError, ValueError):
        #     if normalized_keys[:2] == ('key_1', 'key_1c'):
        #         assert type(value) == list
        #     elif normalized_keys == ('scores', 'day_one_25_jan_2022'):
        #         assert type(value) == list
        #     elif normalized_keys == ('scores', 'day_one_25_jan_2022', 0):
        #     else:
        #         assert type(value) == dict

        # check join_keys
        assert join(*normalized_keys, sep=', ') == nt.join_keys(normalized_keys)
        assert join(*normalized_keys, sep='.') == nt.join_keys(normalized_keys, sep='.')
        assert join(*original_keys, sep=', ') == nt.join_keys(normalized_keys, keymap=keymap)
        assert join(*unknown_norm, sep=', ') == nt.join_keys(unknown_norm)
        assert join(*unknown_orig, sep=', ') == nt.join_keys(unknown_norm, keymap=keymap)


# Test dump {{{1
# test_dump_success_cases {{{2
@parametrize_dump_api
@parametrize_dump_success_cases
def test_dump_success_cases(dump, data_in, path_out, tmp_path):
    assert dump(data_in, tmp_path, default='strict') == path_out.read_text()

# test_dump_error_cases {{{2
@parametrize_dump_api
@parametrize_dump_error_cases
def test_dump_error_cases(dump, data_in, culprit, message, tmp_path):
    with pytest.raises(nt.NestedTextError) as exc_info:
        dump(data_in, tmp_path, default='strict')

    e = exc_info.value

    if culprit is None:
        culprit = ()
    elif isinstance(culprit, list):
        culprit = tuple(culprit)
    elif not isinstance(culprit, tuple):
        culprit = (culprit,)
    assert culprit == e.get_culprit()
    assert message == e.get_message()

    assert isinstance(e, Error)
    assert isinstance(e, ValueError)

# test_dump_default {{{2
@parametrize_dump_api
def test_dump_default(dump, tmp_path):
    data = dict(
        none = None,
        true = True,
        false = False,
        empty_dict = {},
        empty_list = [],
        zero = 0
    )

    expected = dedent('''\
        none:
        true: True
        false: False
        empty_dict:
            {}
        empty_list:
            []
        zero: 0
    ''').lstrip()
    assert dump(data, tmp_path) == expected
    assert dump(data, tmp_path, default=repr) == expected

    with pytest.raises(nt.NestedTextError):
        data = dict(none = None)
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {None: 'none'}
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = dict(true = True)
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {True: 'true'}
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = dict(false = False)
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {False: 'false'}
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = dict(zero = 0)
        dump(data, tmp_path, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {0: 'zero'}
        dump(data, tmp_path, default='strict')

    data = {
        None: 'none',
        True: 'true',
        False: 'false',
        3: 'three',
    }

    assert dump(data, tmp_path) == dedent('''\
        :
            > none
        True: true
        False: false
        3: three
    ''').lstrip()

    assert dump(data, tmp_path, default=repr) == dedent('''\
        :
            > none
        True: true
        False: false
        3: three
    ''').lstrip()


# test_dump_sort_keys {{{2
@parametrize_dump_api
def test_dump_sort_keys(dump, tmp_path):
    data = dict(cc=3, aaa=1, b=2)

    assert dump(data, tmp_path, sort_keys=False) == dedent('''\
            cc: 3
            aaa: 1
            b: 2
    ''').lstrip()

    assert dump(data, tmp_path, sort_keys=True) == dedent('''\
            aaa: 1
            b: 2
            cc: 3
    ''').lstrip()

    assert dump(data, tmp_path, sort_keys=len) == dedent('''\
            b: 2
            cc: 3
            aaa: 1
    ''').lstrip()

    assert dump(data, tmp_path, sort_keys=False, width=80) == '{cc: 3, aaa: 1, b: 2}\n'
    assert dump(data, tmp_path, sort_keys=True, width=80) == '{aaa: 1, b: 2, cc: 3}\n'
    assert dump(data, tmp_path, sort_keys=len, width=80) == '{b: 2, cc: 3, aaa: 1}\n'

# test_dump_indent {{{2
@parametrize_dump_api
def test_dump_indent(dump, tmp_path):
    x = dict(A=['B'])

    with pytest.raises(AssertionError):
        dump(x, tmp_path, indent=0)

    assert dump(x, tmp_path, indent=1) == "A:\n - B\n"
    assert dump(x, tmp_path, indent=2) == "A:\n  - B\n"
    assert dump(x, tmp_path, indent=3) == "A:\n   - B\n"
    assert dump(x, tmp_path, indent=4) == "A:\n    - B\n"

# test_dump_converters {{{2
@parametrize_dump_api
def test_dump_converters(dump, tmp_path):
    x = {'int': 1, 'float': 1.0, 'str': 'A'}

    assert dump(x, tmp_path, default=str) == dedent('''\
        int: 1
        float: 1.0
        str: A
    ''').lstrip()

    converters = {str: lambda x: x.lower()}
    assert dump(x, tmp_path, default=str, converters=converters) == dedent('''\
        int: 1
        float: 1.0
        str: a
    ''').lstrip()
    assert dump(x, tmp_path, default=str, converters=converters, width=80) == '{int: 1, float: 1.0, str: a}\n'

    y = {'info': Info(val=42)}
    converters = {Info: lambda v: f'Info(\n    val={v.val}\n)'}
    assert dump(y, tmp_path, converters=converters) == dedent('''
        info:
            > Info(
            >     val=42
            > )
    ''').lstrip()
    assert dump(y, tmp_path, converters=converters, width=80) == dedent('''
        info:
            > Info(
            >     val=42
            > )
    ''').lstrip()

    converters = {Info: lambda v: v.__dict__}
    result = dump(y, tmp_path, converters=converters, width=80)
    expected = '{info: {val: 42}}\n'
    assert result == expected

    y = dict(info=Info(vals=Info(pair=(42,64))))
    result = dump(y, tmp_path, converters=converters, width=80)
    expected = '{info: {vals: {pair: [42, 64]}}' + '}\n'
    assert result == expected

    y = dict(info=Info(vals=Info(pair=((1,2), (3,4)))))
    full_expected = dedent('''
        info:
            vals:
                pair:
                    -
                        - 1
                        - 2
                    -
                        - 3
                        - 4
    ''').lstrip()
    compressed_expected = '{info: {vals: {pair: [[1, 2], [3, 4]]}}' + '}\n'

    result = dump(y, tmp_path, converters=converters)
    assert result == full_expected

    result = dump(y, tmp_path, converters=converters, width=80)
    assert result == compressed_expected

    def defaulter(arg):
        if isinstance(arg, Info):
            return arg.__dict__
        raise TypeError

    result = dump(y, tmp_path, default=defaulter)
    assert result == full_expected

    result = dump(y, tmp_path, default=defaulter, width=80)
    assert result == compressed_expected

    class ntInfo(Info):
        def __nestedtext_converter__(self):
            return self.__dict__

    y = {'info': ntInfo(val=42)}
    result = dump(y, tmp_path, width=80)
    expected = '{info: {val: 42}}\n'
    assert result == expected

    # assure that converters dominates over __nestedtext_converter__
    converters = {ntInfo: False}
    with pytest.raises(nt.NestedTextError) as exc:
        dump(y, tmp_path, width=80, converters=converters)
    assert str(exc.value) == f"info: unsupported type (ntInfo)."

    # converting arrow object
    date = '1969-07-20'
    fmt = 'YYYY-MM-DD'
    given = arrow.get(date)
    converters = {arrow.Arrow: lambda v: v.format(fmt)}

    # arrow object as value
    y = {'date': given}
    result = dump(y, tmp_path, converters=converters)
    expected = 'date: 1969-07-20\n'
    assert result == expected
    result = dump(y, tmp_path, converters=converters, width=99)
    expected = '{date: 1969-07-20}\n'
    assert result == expected
    result = dump(y, tmp_path, default=str)
    expected = 'date: 1969-07-20T00:00:00+00:00\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, width=99)
    expected = 'date: 1969-07-20T00:00:00+00:00\n'
    assert result == expected

    # arrow object as key
    y = {given: 'moon landing'}
    result = dump(y, tmp_path, converters=converters)
    expected = '1969-07-20: moon landing\n'
    assert result == expected
    result = dump(y, tmp_path, converters=converters, width=99)
    expected = '{1969-07-20: moon landing}\n'
    assert result == expected
    result = dump(y, tmp_path, default=str)
    expected = '1969-07-20T00:00:00+00:00: moon landing\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, width=99)
    expected = '1969-07-20T00:00:00+00:00: moon landing\n'
    assert result == expected

    # converting quantity object
    converters = {Quantity: lambda q: q.render(prec=8)}

    # arrow object as value
    y = {'c': Quantity('c')}
    result = dump(y, tmp_path, converters=converters)
    expected = 'c: 299.792458 Mm/s\n'
    assert result == expected
    result = dump(y, tmp_path, converters=converters, width=99)
    expected = '{c: 299.792458 Mm/s}\n'
    assert result == expected
    result = dump(y, tmp_path, default=str)
    expected = 'c: 299.79 Mm/s\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, width=99)
    expected = '{c: 299.79 Mm/s}\n'
    assert result == expected

    # arrow object as key
    y = {Quantity('c'): 'c'}
    result = dump(y, tmp_path, converters=converters)
    expected = '299.792458 Mm/s: c\n'
    assert result == expected
    result = dump(y, tmp_path, converters=converters, width=99)
    expected = '{299.792458 Mm/s: c}\n'
    assert result == expected
    result = dump(y, tmp_path, default=str)
    expected = '299.79 Mm/s: c\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, width=99)
    expected = '{299.79 Mm/s: c}\n'
    assert result == expected

    # integer object as key
    y = {0: 'zero', 'one': 'one', 'four': 'four'}
    result = dump(y, tmp_path, default=str)
    expected = '0: zero\none: one\nfour: four\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, width=99)
    expected = '{0: zero, one: one, four: four}\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, sort_keys=True)
    expected = '0: zero\nfour: four\none: one\n'
    assert result == expected
    result = dump(y, tmp_path, default=str, width=99, sort_keys=True)
    expected = '{0: zero, four: four, one: one}\n'
    assert result == expected


# test_dump_converters_err {{{2
z = complex(0, 0)
def defaulter(arg):
    if isinstance(arg, complex):
        raise TypeError
    return str(arg)

@parametrize_dump_api
@parametrize(
        'data, culprit, kind, kwargs', [
            ({'key': 42},   'key', 'int',     dict(default='strict')),
            ({'key': 42.0}, 'key', 'float',   dict(default='strict')),
            ({'key': True}, 'key', 'bool',    dict(default='strict')),
            ({'key': 42},   'key', 'int',     dict(default=str, converters={int: False})),
            ({'key': z},    'key', 'complex', dict(default=defaulter)),
            ({'key': 42},   'key', 'int',     dict(default='strict', width=80)),
            ({'key': 42.0}, 'key', 'float',   dict(default='strict', width=80)),
            ({'key': True}, 'key', 'bool',    dict(default='strict', width=80)),
            ({'key': 42},   'key', 'int',     dict(default=str, converters={int: False}, width=80)),
            ({'key': z},    'key', 'complex', dict(default=defaulter, width=80)),
        ]
)
def test_dump_converters_err(dump, tmp_path, data, culprit, kind, kwargs):
    with pytest.raises(nt.NestedTextError) as exc:
        dump(data, tmp_path, **kwargs)

    assert str(exc.value) == f"{culprit}: unsupported type ({kind})."
    assert exc.value.args == (data[culprit],)
    assert exc.value.kwargs == dict(
        culprit = (str(culprit),),
        template = f'unsupported type ({kind}).',
    )
    assert isinstance(exc.value, Error)
    assert isinstance(exc.value, ValueError)

# test_dump_width {{{2
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
        ([''], '[ ]', dict(width=80)),
        (['a'], '[a]', dict(width=80)),
        ([':'], '[:]', dict(width=80)),
        ([[]], '[[]]', dict(width=80)),
        ([['a']], '[[a]]', dict(width=80)),
        ([{}], '[{}]', dict(width=80)),
        ([{'a': '0'}], '[{a: 0}]', dict(width=80)),
        (['a', 'b'], '[a, b]', dict(width=80)),
        (['', ''], '[ , ]', dict(width=80)),
        ([[], []], '[[], []]', dict(width=80)),
        ([['a', 'b'], ['c', 'd']], '[[a, b], [c, d]]', dict(width=80)),
        ([{}, {}], '[{}, {}]', dict(width=80)),
        ([{'a': '0', 'b': '1'}, {'c': '2', 'd': '3'}], '[{a: 0, b: 1}, {c: 2, d: 3}]', dict(width=80)),
        (['a', []], '[a, []]', dict(width=80)),
        ([[], {}], '[[], {}]', dict(width=80)),
        ([{}, 'b'], '[{}, b]', dict(width=80)),
        (['a', 'b'], '[a, b]', dict(width=80)),
        (['a', 'b', ''], '[a, b, ]', dict(width=80)),
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
            dict(width=10)
        ),
        (
            [['11', '12', '13'], ['21', '22', '23'], ['31', '32', '33']],
            dedent("""
                -
                    [11, 12, 13]
                -
                    [21, 22, 23]
                -
                    [31, 32, 33]
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

        ([None], '[ ]', dict(width=80)),
        ([Info(arg='a'), Info(arg='b')], "[Info(arg='a'), Info(arg='b')]", dict(width=80, default=repr)),
        ({'a': Info(arg=0), 'b': Info(arg=1)}, "{a: Info(arg=0), b: Info(arg=1)}", dict(width=80, default=repr)),
        (
            [{'a': '0', 'b': '1'}, {'c': '2', 'd': '3'}],
            '[{a: 0, b: 1}, {c: 2, d: 3}]',
            dict(inline_level=0, width=80)
        ),
        (
            [{'a': '0', 'b': '1'}, {'c': '2', 'd': '3'}],
            dedent("""
                -
                    {a: 0, b: 1}
                -
                    {c: 2, d: 3}
            """).strip(),
            dict(inline_level=1, width=80)
        ),
        (
            [{'a': '0', 'b': '1'}, {'c': '2', 'd': '3'}],
            dedent("""
                -
                    a: 0
                    b: 1
                -
                    c: 2
                    d: 3
            """).strip(),
            dict(inline_level=2, width=80)
        ),
        (
            ['aaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bbbbbbbbbbbbbbbbbbbbbbbbbbb'],
            '[aaaaaaaaaaaaaaaaaaaaaaaaaaa, bbbbbbbbbbbbbbbbbbbbbbbbbbb]',
            dict(inline_level=0, width=80)
        ),
        (
            ['aaaaaaaaaaaaaaaaaaaaaaaaaaa', 'bbbbbbbbbbbbbbbbbbbbbbbbbbb'],
            dedent("""
                - aaaaaaaaaaaaaaaaaaaaaaaaaaa
                - bbbbbbbbbbbbbbbbbbbbbbbbbbb
            """).strip(),
            dict(inline_level=0, width=20)
        ),
        ({' a': 'A'}, ':  a\n    > A', dict(width=80)),
        ({'a ': 'A'}, ': a \n    > A', dict(width=80)),
        ({'\ta': 'A'}, ': \ta\n    > A', dict(width=80)),
        ({'a\t': 'A'}, ': a\t\n    > A', dict(width=80)),
        ({'a,b': 'A'}, 'a,b: A', dict(width=80)),
        ({'a:b': 'A'}, 'a:b: A', dict(width=80)),
        ({'a[b': 'A'}, 'a[b: A', dict(width=80)),
        ({'a]b': 'A'}, 'a]b: A', dict(width=80)),
        ({'a{b': 'A'}, 'a{b: A', dict(width=80)),
        ({'a}b': 'A'}, 'a}b: A', dict(width=80)),
        ({'a\nb': 'A'}, ': a\n: b\n    > A', dict(width=80)),
        ({'a\rb': 'A'}, ': a\n: b\n    > A', dict(width=80)),

        ({'A': ' a'}, 'A:  a', dict(width=80)),
        ({'A': 'a '}, 'A: a ', dict(width=80)),
        ({'A': '\ta'}, 'A: \ta', dict(width=80)),
        ({'A': 'a\t'}, 'A: a\t', dict(width=80)),
        ({'A': 'a,b'}, 'A: a,b', dict(width=80)),
        ({'A': 'a:b'}, 'A: a:b', dict(width=80)),
        ({'A': 'a[b'}, 'A: a[b', dict(width=80)),
        ({'A': 'a]b'}, 'A: a]b', dict(width=80)),
        ({'A': 'a{b'}, 'A: a{b', dict(width=80)),
        ({'A': 'a}b'}, 'A: a}b', dict(width=80)),
        ({'A': 'a\nb'}, 'A:\n    > a\n    > b', dict(width=80)),
        ({'A': 'a\rb'}, 'A:\n    > a\n    > b', dict(width=80)),
    ]
)
def test_dump_width(dump, tmp_path, given, expected, kwargs):
    assert dump(given, tmp_path, **kwargs) == expected + '\n'

# test_dump_nones {{{2
@parametrize_dump_api
@parametrize(
    'given, expected, kwargs', [
        ( None,          '',             {} ),
        ( None,          '',             {} ),
        ( None,          '',             {} ),
        ( None,          '',             {} ),
        ( [None],        '-',            {} ),
        ( [None],        '-',            {} ),
        ( {'key':None},  'key:',         {} ),
        ( {None:'val'},  ':\n    > val', {} ),
    ]
)
def test_dump_nones(dump, tmp_path, given, expected, kwargs):
    assert dump(given, tmp_path, **kwargs) == expected + '\n'

# test_cycle_detection {{{2
def test_cycle_detection():
    a = [0, 1, 2]
    b = [a]
    a.append(b)

    with pytest.raises(nt.NestedTextError) as exception:
        nt.dumps(a)
    assert exception.value.culprit == (3, 0, 3,)
    assert 'circular reference' in str(exception.value)

    A = dict(a=a, b=b)

    with pytest.raises(nt.NestedTextError) as exception:
        nt.dumps(A)
    assert exception.value.culprit == ('a', 3, 0)
    assert 'circular reference' in str(exception.value)

# vim: fdm=marker
