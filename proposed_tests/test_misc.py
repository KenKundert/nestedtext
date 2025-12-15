# encoding: utf8

# Imports {{{1
import pytest
import nestedtext as nt
import arrow
from io import StringIO
from inform import Error, Info, join, dedent
from quantiphy import Quantity
import subprocess
import sys
import os

parametrize = pytest.mark.parametrize

# Load Tests {{{1
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

    regular_content = 'key: hello\nkey: goodbye'
    inline_content = '{key: hello, key: goodbye}'

    for content in [regular_content, inline_content]:
        data = nt.loads(content, on_dup='ignore')
        assert data == {'key': 'hello'}, content

        data = nt.loads(content, on_dup=ignore_dup)
        assert data == {'key': 'hello'}, content

        data = nt.loads(content, on_dup='replace')
        assert data == {'key': 'goodbye'}, content

        data = nt.loads(content, on_dup=replace_dup)
        assert data == {'key': 'goodbye'}, content

        data = nt.loads(content, on_dup=de_dup)
        assert data == {'key': 'hello', 'key — #2': 'goodbye'}, content

        with pytest.raises(nt.NestedTextError) as e:
            nt.loads(content)
        assert e.value.get_message() == 'duplicate key: key.', content
        assert e.value.source == None, content

        with pytest.raises(nt.NestedTextError) as e:
            nt.loads(content, on_dup='error')
        assert e.value.get_message() == 'duplicate key: key.', content
        assert e.value.source == None, content

        with pytest.raises(nt.NestedTextError) as e:
            nt.loads(content, on_dup=dup_is_error)
        assert e.value.get_message() == 'duplicate key: key.', content
        assert e.value.source == None, content

        with pytest.raises(nt.NestedTextError) as e:
            nt.loads(content, source='nantucket')
        assert e.value.get_message() == 'duplicate key: key.', content
        assert e.value.source == 'nantucket', content

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
        40  :
        41  : key
        42      > it’s value
        43      >
        44      > it’s a long value
        45  :
        46      >

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
        multiline↲↲key                      → 39 0    42 6    39 42   42 45
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
        rendered = f"{lineno+1:>4} ❬{doc_lines[lineno]}❭\n      {colno*' '}▲"
        assert location.line.render(colno) == rendered
        assert location.as_line() == rendered
        assert location.as_line('value') == rendered
        rendered = f"{key_lineno+1:>4} ❬{doc_lines[key_lineno]}❭\n      {key_colno*' '}▲"
        assert location.as_line('key') == rendered
        line = location.as_line(kind='value', offset=None)
        margin = 6
        offset = 5
        shift = min(margin + offset + colno, len(line) - 1)
        rendered = f"{lineno+1:>4} ❬{doc_lines[lineno]}❭\n{shift*' '}▲"
        assert location.as_line(offset=offset) == rendered
        rendered = f"{lineno+1:>4} ❬{doc_lines[lineno]}❭"
        assert location.as_line(offset=None) == rendered
        assert str(location.line) == doc_lines[lineno]
        assert repr(location.line) == f'Line({lineno+1}: ❬{doc_lines[lineno]}❭)'
        assert repr(location) == f"Location(lineno={lineno}, colno={colno}, key_lineno={key_lineno}, key_colno={key_colno})"

        # check line numbers as tuples
        assert nt.get_lines_from_keys(addresses, keys, keymap, kind='key') == (key_first_line, key_last_line), keys
        assert nt.get_lines_from_keys(addresses, list(keys), keymap, kind='value') == (value_first_line, value_last_line), keys

        # check line numbers as tuples
        assert nt.get_line_numbers(keys, keymap, kind='key') == (key_first_line, key_last_line), keys
        assert nt.get_line_numbers(list(keys), keymap, kind='value') == (value_first_line, value_last_line), keys

        bad_keys = keys + ("does-not-exist",)

        with pytest.raises(KeyError) as exception:
            nt.get_line_numbers(bad_keys, keymap, kind='value', strict=True)
        assert exception.value.args[0] == bad_keys

        assert nt.get_line_numbers(bad_keys, keymap, kind='value', strict=False) == (value_first_line, value_last_line), keys

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

        # check line numbers as strings
        if key_first_line+1 != key_last_line:
            key_lines = f"{key_first_line+1}-{key_last_line}"
        else:
            key_lines = str(key_last_line)
        assert nt.get_line_numbers(keys, keymap, kind='key', sep='-') == key_lines, keys
        if value_first_line+1 != value_last_line:
            value_lines = f"{value_first_line+1}-{value_last_line}"
        else:
            value_lines = str(value_last_line)
        assert nt.get_line_numbers(keys, keymap, kind='value', sep='-') == value_lines, keys

    # Without key normalization
    keymap = {}
    addresses = nt.loads(document, keymap=keymap)
    for case in cases:
        given, expected = case.split('→')
        keys = tuple(fix_key(n, True) for n in given.split())
        check_result(keys, expected, addresses)

    ml_keys = ("multiline\n\nkey",)
    loc = nt.get_location(ml_keys, keymap)
    assert loc.as_line('key') == dedent("""
        ◊ 40 ❬: multiline❭
              ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('key', offset=(1,0)) == dedent("""
        ◊ 41 ❬:❭
              ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('key', offset=(2,0)) == dedent("""
        ◊ 42 ❬: key❭
              ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('value') == dedent("""
        ◊ 43 ❬    > it’s value❭
                    ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('value', offset=(1,0)) == dedent("""
        ◊ 44 ❬    >❭
                   ▲
    """, bolm='◊', strip_nl="b")
        # the above misplacement of the pointer is expected
    assert loc.as_line('value', offset=(2,0)) == dedent("""
        ◊ 45 ❬    > it’s a long value❭
                    ▲
    """, bolm='◊', strip_nl="b")
    ml_keys = ("",)
    loc = nt.get_location(ml_keys, keymap)
    assert loc.as_line('key') == dedent("""
        ◊ 46 ❬:❭
              ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('value') == dedent("""
        ◊ 47 ❬    >❭
                   ▲
    """, bolm='◊', strip_nl="b")

    # With key normalization
    keymap = {}
    addresses = nt.loads(document, keymap=keymap, normalize_key=normalize_key)
    for case in cases:
        given, expected = case.split('→')
        keys = tuple(fix_key(n, False) for n in given.split())
        check_result(keys, expected, addresses)

    addresses = nt.loads(document, keymap=keymap, normalize_key=normalize_key)
    keys = ("president", "address")
    loc = nt.get_location(keys, keymap)
    assert loc.as_line('value') == dedent("""
        ◊  6 ❬        > 138 Almond Street❭
                        ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('value', offset=None) == dedent("""
        ◊  6 ❬        > 138 Almond Street❭
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('value', offset=4) == dedent("""
        ◊  6 ❬        > 138 Almond Street❭
                            ▲
    """, bolm='◊', strip_nl="b")
    assert loc.as_line('value', offset=(1,8)) == dedent("""
        ◊  7 ❬        > Topeka, Kansas 20697❭
                                ▲
    """, bolm='◊', strip_nl="b")
    with pytest.raises(IndexError) as exception:
        loc.as_line('value', offset=(2,8))
    assert exception.value.args == (2,)


# test_keymaps_with_duplicates {{{2
def test_keymaps_with_duplicates():

    document_with_linenos = dedent("""
        0   michael jordan:
        1       occupation: basketball player
        2
        3   michael jordan:
        4       occupation: actor
        5
        6   michael jordan:
        7       occupation: football player
    """).strip()

    # remove line numbers from NestedText document
    doc_lines = [l[4:] for l in document_with_linenos.splitlines()]
    document = '\n'.join(doc_lines)
    print(document)

    #   keys                                  key    value    lines
    #                                         r  c    r  c    k       v
    cases = """
        michael_jordan                      → 0  0    1  4    0  1    1  2
        michael_jordan occupation           → 1  4    1  16   1  2    1  2
        michael_jordan2                     → 3  0    4  4    3  4    4  5
        michael_jordan2 occupation          → 4  4    4  16   4  5    4  5
        michael_jordan3                     → 6  0    7  4    6  7    7  8
        michael_jordan3 occupation          → 7  4    7  16   7  8    7  8
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

    def de_dup(key, state):
        if key not in state:
            state[key] = 1
        state[key] += 1
        return f"{key}{state[key]}"

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
        rendered = f"{lineno+1:>4} ❬{doc_lines[lineno]}❭\n      {colno*' '}▲"
        assert location.line.render(colno) == rendered
        assert location.as_line() == rendered
        assert location.as_line('value') == rendered
        rendered = f"{key_lineno+1:>4} ❬{doc_lines[key_lineno]}❭\n      {key_colno*' '}▲"
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
    addresses = nt.loads(
        document, keymap=keymap, on_dup=de_dup
    )
    for case in cases:
        given, expected = case.split('→')
        keys = tuple(fix_key(n, True) for n in given.split())
        check_result(keys, expected, addresses)

    # With key normalization
    keymap = {}
    addresses = nt.loads(
        document, keymap=keymap, on_dup=de_dup, normalize_key=normalize_key
    )
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

        # check get_value
        value = nt.get_value(data, normalized_keys)
        expected_value = expected_values[normalized_keys]
        try:
            assert isinstance(value, expected_value)
        except TypeError:
            assert value == expected_value

        with pytest.raises(KeyError) as exception:
            value = nt.get_value("", normalized_keys)
        assert exception.value.args == (normalized_keys[0],)

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

        # check get_keys
        assert normalized_keys == nt.get_keys(normalized_keys, keymap, original=False)
        assert original_keys == nt.get_keys(normalized_keys, keymap, original=True)
        assert join(*normalized_keys, sep=', ') == nt.get_keys(normalized_keys, keymap, original=False, sep=", ")
        assert join(*original_keys, sep=', ') == nt.get_keys(normalized_keys, keymap, original=True, sep=", ")
        assert join(*unknown_norm, sep=', ') == nt.get_keys(list(unknown_norm), keymap, original=False, strict="all", sep=", ")
        assert join(*unknown_orig, sep=', ') == nt.get_keys(unknown_norm, keymap, original=True, strict="all", sep=", ")
        assert join(*unknown_norm, sep=', ') == nt.get_keys(unknown_norm, keymap, original=False, strict=False, sep=", ")
        assert join(*unknown_orig, sep=', ') == nt.get_keys(list(unknown_norm), keymap, original=True, strict=False, sep=", ")
        assert join(*unknown_norm[:-1], sep=', ') == nt.get_keys(unknown_norm, keymap, original=False, strict="found", sep=", ")
        assert join(*unknown_orig[:-1], sep=', ') == nt.get_keys(unknown_norm, keymap, original=True, strict="found", sep=", ")
        assert join('unknown key', sep=', ') == nt.get_keys(unknown_norm, keymap, original=False, strict="missing", sep=", ")
        assert join('unknown key', sep=', ') == nt.get_keys(unknown_norm, keymap, original=True, strict="missing", sep=", ")

        with pytest.raises(KeyError) as exception:
            nt.get_keys(unknown_norm, keymap, strict=True)
        assert exception.value.args[0] == unknown_norm
        with pytest.raises(KeyError) as exception:
            nt.get_keys(unknown_norm, keymap, strict="error")
        assert exception.value.args[0] == unknown_norm

# test_load_dialect {{{2
def test_load_dialect():
    document = dedent("""
        [7:0] data:
        {7:0} bits:
    """)
    data = nt.loads(document, dialect="i")
    assert data == {"[7:0] data":"", "{7:0} bits":""}

# test_empty {{{2
@parametrize(
    "top,expected", [(any,None), (dict,{}), (list,[]), (str,"")]
)
def test_empty(top, expected):
    # just blank lines
    document = ""

    keymap = {}
    data = nt.loads(document, top=top, keymap=keymap)
    assert data == expected
    assert keymap[()].as_line(offset=None) == ''

# test_empty_blank_lines {{{2
@parametrize(
    "top,expected", [(any,None), (dict,{}), (list,[]), (str,"")]
)
def test_empty_blank_lines(top, expected):
    # just blank lines
    document = "\n\n\n"

    keymap = {}
    data = nt.loads(document, top=top, keymap=keymap)
    assert data == expected
    assert keymap[()].as_line(offset=None) == '   3 ❬❭'

# test_empty_comments {{{2
@parametrize(
    "top,expected", [(any,None), (dict,{}), (list,[]), (str,"")]
)
def test_empty_comments(top, expected):
    # just blank lines
    document = "#comment 0\n#comment 1\n#comment 2\n# comment3"

    keymap = {}
    data = nt.loads(document, top=top, keymap=keymap)
    assert data == expected
    assert keymap[()].as_line(offset=None) == '   4 ❬# comment3❭'

# test_empty_stdin {{{2
@parametrize(
    "top,expected", [(any,None), (dict,{}), (list,[]), (str,"")]
)
def test_empty_stdin(monkeypatch, top, expected):
    # just blank lines
    document = ""
    monkeypatch.setattr('sys.stdin', StringIO(document))

    keymap = {}
    data = nt.load(sys.stdin, top=top, keymap=keymap, source="❬stdin❭")
    assert data == expected
    assert keymap[()].as_line(offset=None) == ''

# test_empty_dev_null {{{2
@parametrize(
    "top,expected", [(any,None), (dict,{}), (list,[]), (str,"")]
)
def test_empty_dev_null(monkeypatch, top, expected):
    # just blank lines
    keymap = {}
    data = nt.load("/dev/null", top=top, keymap=keymap, source="❬stdin❭")
    assert data == expected
    assert keymap[()].as_line(offset=None) == ''

# test_empty_fd0 {{{2
def test_empty_fd0(monkeypatch):
    # I only seem to get one shot at testing 0 as a file descriptor

    # load stdin, which will be empty
    monkeypatch.setattr('sys.stdin', StringIO(''))
    keymap = {}
    data = nt.load(0, keymap=keymap)
    assert data == {}
    assert keymap[()].as_line(offset=None) == ''


# Dump Tests {{{1
# test_dump_default {{{2
def test_dump_default():
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
    ''').strip()
    assert nt.dumps(data) == expected
    assert nt.dumps(data, default=repr) == expected

    with pytest.raises(nt.NestedTextError):
        data = dict(none = None)
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {None: 'none'}
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = dict(true = True)
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {True: 'true'}
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = dict(false = False)
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {False: 'false'}
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = dict(zero = 0)
        nt.dumps(data, default='strict')

    with pytest.raises(nt.NestedTextError):
        data = {0: 'zero'}
        nt.dumps(data, default='strict')

    data = {
        None: 'none',
        True: 'true',
        False: 'false',
        3: 'three',
    }

    assert nt.dumps(data) == dedent('''\
        :
            > none
        True: true
        False: false
        3: three
    ''').strip()

    assert nt.dumps(data, default=repr) == dedent('''\
        :
            > none
        True: true
        False: false
        3: three
    ''').strip()


# test_dump_sort_key {{{2
def test_dump_sort_key():
    data = dict(cc=3, aaa=1, b=2)

    assert nt.dumps(data, sort_keys=False) == dedent('''\
            cc: 3
            aaa: 1
            b: 2
    ''').strip()

    assert nt.dumps(data, sort_keys=True) == dedent('''\
            aaa: 1
            b: 2
            cc: 3
    ''').strip()

    assert nt.dumps(data, sort_keys=lambda t, k: len(t[0])) == dedent('''\
            b: 2
            cc: 3
            aaa: 1
    ''').strip()

    assert nt.dumps(data, sort_keys=False, width=80) == '{cc: 3, aaa: 1, b: 2}'
    assert nt.dumps(data, sort_keys=True, width=80) == '{aaa: 1, b: 2, cc: 3}'
    assert nt.dumps(data, sort_keys=lambda t, k: len(t[0]), width=80) == '{b: 2, cc: 3, aaa: 1}'

# test_dump_indent {{{2
def test_dump_indent():
    x = dict(A=['B'])

    with pytest.raises(AssertionError):
        nt.dumps(x, indent=0)

    assert nt.dumps(x, indent=1) == "A:\n - B"
    assert nt.dumps(x, indent=2) == "A:\n  - B"
    assert nt.dumps(x, indent=3) == "A:\n   - B"
    assert nt.dumps(x, indent=4) == "A:\n    - B"

# test_dump_converters {{{2
def test_dump_converters():
    x = {'int': 1, 'float': 1.0, 'str': 'A'}

    assert nt.dumps(x, default=str) == dedent('''\
        int: 1
        float: 1.0
        str: A
    ''').strip()

    converters = {str: lambda x: x.lower()}
    assert nt.dumps(x, default=str, converters=converters) == dedent('''\
        int: 1
        float: 1.0
        str: a
    ''').strip()
    assert nt.dumps(x, default=str, converters=converters, width=80) == '{int: 1, float: 1.0, str: a}'

    y = {'info': Info(val=42)}
    converters = {Info: lambda v: f'Info(\n    val={v.val}\n)'}
    assert nt.dumps(y, converters=converters) == dedent('''
        info:
            > Info(
            >     val=42
            > )
    ''').strip()
    assert nt.dumps(y, converters=converters, width=80) == dedent('''
        info:
            > Info(
            >     val=42
            > )
    ''').strip()

    converters = {Info: lambda v: v.__dict__}
    result = nt.dumps(y, converters=converters, width=80)
    expected = '{info: {val: 42}}'
    assert result == expected

    y = dict(info=Info(vals=Info(pair=(42,64))))
    result = nt.dumps(y, converters=converters, width=80)
    expected = '{info: {vals: {pair: [42, 64]}}' + '}'
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
    ''').strip()
    compressed_expected = '{info: {vals: {pair: [[1, 2], [3, 4]]}}' + '}'

    result = nt.dumps(y, converters=converters)
    assert result == full_expected

    result = nt.dumps(y, converters=converters, width=80)
    assert result == compressed_expected

    def defaulter(arg):
        if isinstance(arg, Info):
            return arg.__dict__
        raise TypeError

    result = nt.dumps(y, default=defaulter)
    assert result == full_expected

    result = nt.dumps(y, default=defaulter, width=80)
    assert result == compressed_expected

    class ntInfo(Info):
        def __nestedtext_converter__(self):
            return self.__dict__

    y = {'info': ntInfo(val=42)}
    result = nt.dumps(y, width=80)
    expected = '{info: {val: 42}}'
    assert result == expected

    # assure that converters dominates over __nestedtext_converter__
    converters = {ntInfo: False}
    with pytest.raises(nt.NestedTextError) as exc:
        nt.dumps(y, width=80, converters=converters)
    assert str(exc.value) == "info: unsupported type (ntInfo)."

    # converting arrow object
    date = '1969-07-20'
    fmt = 'YYYY-MM-DD'
    given = arrow.get(date)
    converters = {arrow.Arrow: lambda v: v.format(fmt)}

    # arrow object as value
    y = {'date': given}
    result = nt.dumps(y, converters=converters)
    expected = 'date: 1969-07-20'
    assert result == expected
    result = nt.dumps(y, converters=converters, width=99)
    expected = '{date: 1969-07-20}'
    assert result == expected
    result = nt.dumps(y, default=str)
    expected = 'date: 1969-07-20T00:00:00+00:00'
    assert result == expected
    result = nt.dumps(y, default=str, width=99)
    expected = 'date: 1969-07-20T00:00:00+00:00'
    assert result == expected

    # arrow object as key
    y = {given: 'moon landing'}
    result = nt.dumps(y, converters=converters)
    expected = '1969-07-20: moon landing'
    assert result == expected
    result = nt.dumps(y, converters=converters, width=99)
    expected = '{1969-07-20: moon landing}'
    assert result == expected
    result = nt.dumps(y, default=str)
    expected = '1969-07-20T00:00:00+00:00: moon landing'
    assert result == expected
    result = nt.dumps(y, default=str, width=99)
    expected = '1969-07-20T00:00:00+00:00: moon landing'
    assert result == expected

    # converting quantity object
    converters = {Quantity: lambda q: q.render(prec=8)}

    # arrow object as value
    y = {'c': Quantity('c')}
    result = nt.dumps(y, converters=converters)
    expected = 'c: 299.792458 Mm/s'
    assert result == expected
    result = nt.dumps(y, converters=converters, width=99)
    expected = '{c: 299.792458 Mm/s}'
    assert result == expected
    result = nt.dumps(y, default=str)
    expected = 'c: 299.79 Mm/s'
    assert result == expected
    result = nt.dumps(y, default=str, width=99)
    expected = '{c: 299.79 Mm/s}'
    assert result == expected

    # arrow object as key
    y = {Quantity('c'): 'c'}
    result = nt.dumps(y, converters=converters)
    expected = '299.792458 Mm/s: c'
    assert result == expected
    result = nt.dumps(y, converters=converters, width=99)
    expected = '{299.792458 Mm/s: c}'
    assert result == expected
    result = nt.dumps(y, default=str)
    expected = '299.79 Mm/s: c'
    assert result == expected
    result = nt.dumps(y, default=str, width=99)
    expected = '{299.79 Mm/s: c}'
    assert result == expected

    # integer object as key
    y = {0: 'zero', 'one': 'one', 'four': 'four'}
    result = nt.dumps(y, default=str)
    expected = '0: zero\none: one\nfour: four'
    assert result == expected
    result = nt.dumps(y, default=str, width=99)
    expected = '{0: zero, one: one, four: four}'
    assert result == expected
    result = nt.dumps(y, default=str, sort_keys=True)
    expected = '0: zero\nfour: four\none: one'
    assert result == expected
    result = nt.dumps(y, default=str, width=99, sort_keys=True)
    expected = '{0: zero, four: four, one: one}'
    assert result == expected


# test_dump_converters_err {{{2
z = complex(0, 0)
def defaulter(arg):
    if isinstance(arg, complex):
        raise TypeError
    return str(arg)

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
def test_dump_converters_err(data, culprit, kind, kwargs):
    with pytest.raises(nt.NestedTextError) as exc:
        nt.dumps(data, **kwargs)

    assert str(exc.value) == f"{culprit}: unsupported type ({kind})."
    assert exc.value.args == (data[culprit],)
    assert exc.value.kwargs == dict(
        culprit = (str(culprit),),
        template = f'unsupported type ({kind}).',
    )
    assert isinstance(exc.value, Error)
    assert isinstance(exc.value, ValueError)

# test_dump_width {{{2
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
def test_dump_width(given, expected, kwargs):
    assert nt.dumps(given, **kwargs) == expected

# test_dump_nones {{{2
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
def test_dump_nones(given, expected, kwargs):
    assert nt.dumps(given, **kwargs) == expected

# test_dump_cycle_detection {{{2
def test_dump_cycle_detection():
    a = [0, 1, 2]
    b = [a]
    a.append(b)

    with pytest.raises(nt.NestedTextError) as exception:
        nt.dumps(a)
    assert exception.value.culprit == (3, 0, 3)
    assert 'circular reference' in str(exception.value)

    A = dict(a=a, b=b)

    with pytest.raises(nt.NestedTextError) as exception:
        nt.dumps(A)
    assert exception.value.culprit == ('a', 3, 0)
    assert 'circular reference' in str(exception.value)

# test_dump_map_keys_keymap {{{2
def test_dump_map_keys_keymap():
    document = dedent("""
        Michael Jordan:
            occupation: basketball player
        Michael Jordan:
            occupation: actor
        Michael Jordan:
            occupation: football player
    """).strip()

    expected = dedent("""
        Michael Jordan:
            occupation: basketball player
        Michael Jordan #2:
            occupation: actor
        Michael Jordan #3:
            occupation: football player
    """).strip()

    def de_dup(key, state):
        if key not in state:
            state[key] = 1
        state[key] += 1
        return f"{key} #{state[key]}"

    # without key normalization
    keymap = {}
    people = nt.loads(document, on_dup=de_dup, keymap=keymap)
    output = nt.dumps(people)
    assert output == expected
    output = nt.dumps(people, map_keys=keymap)
    assert output == document

    # with key normalization
    def normalize_key(key, parent_keys):
        return key.lower()

    keymap = {}
    people = nt.loads(document, on_dup=de_dup, keymap=keymap, normalize_key=normalize_key)
    output = nt.dumps(people)
    assert output == expected.lower()
    output = nt.dumps(people, map_keys=keymap)
    assert output == document

    # check error handling
    people['michael jordan'].update(dict(level='goat'))
    output = nt.dumps(people, map_keys=keymap)
    assert 'level: goat' in output

# test_dump_map_keys_func {{{2
def test_dump_map_keys_func():
    document = dedent("""
        declarations:
            count:
                type: reg
                size: [5:0]
                initial: 'bXXX_XXX
        behavior:
            - count = 0 when reset
            - count += 1 on posedge clock
    """).strip()

    expected = document
    for each in ["declarations", "behavior"]:
        expected = expected.replace(each, each.upper())

    def map_keys(key, parent_keys):
        if len(parent_keys) == 0:
            return key.upper()

    code = nt.loads(document)
    output = nt.dumps(code, map_keys=map_keys)
    assert output == expected

# test_dump_dialect {{{2
def test_dump_dialect():
    data = {"dict":{}, "list":[]}
    document = nt.dumps(data, dialect="i")
    assert document.strip() == dedent("""
        dict:
        list:
    """, strip_nl="b")

# Misc tests {{{1
# test_file_descriptors() {{{2
def test_file_descriptors(tmp_path):
    # program that writes out a simple NT document to stdout
    write_data = dedent("""
        import nestedtext
        data = {"dict": {}, "list": [], "str": "", "mls":"\\n"}
        nestedtext.dump(data, 1)
    """)
    writer = tmp_path / "writer.py"
    # program that reads a simple NT document from stderr
    read_data = dedent("""
        import nestedtext
        data = nestedtext.load(0)
        assert data == {"dict": {}, "list": [], "str": "", "mls":"\\n"}
    """)
    reader = tmp_path / "reader.py"

    writer.write_text(write_data)
    reader.write_text(read_data)

    results = subprocess.run(
        f"python {writer!s} | python {reader!s}",
        shell = True,
        capture_output = True,
        env = {"COVERAGE_PROCESS_START":"", "PATH": os.environ["PATH"]}
    )
    assert results.stdout.decode('utf8') == ""
    assert results.stderr.decode('utf8') == ""
    assert results.returncode == 0

# test_binary_files() {{{2
def test_binary_round_trip(tmp_path):
    orig_data = {"dict": {}, "list": [], "str": "", "mls":"\\n"}
    nt_path = tmp_path / "test.nt"

    # dump nestedtext to a binary file
    with nt_path.open('wb') as f:
        nt.dump(orig_data, f)

    # read nestedtext from a binary file
    with nt_path.open('rb') as f:
        data_as_read = nt.load(f)

    assert data_as_read == orig_data

# test_round_trip() {{{2
def test_round_trip(tmp_path):
    data_python = {
        "http://www.kde.org/standards/kcfg/1.0}kcfgfile": None,
        "http://www.kde.org/standards/kcfg/1.0}group": {
            "http://www.kde.org/standards/kcfg/1.0}entry": [
                {"{http://www.kde.org/standards/kcfg/1.0}default": 250},
                {"{http://www.kde.org/standards/kcfg/1.0}default": "krunner,yakuake"}
            ]
        }
    }
    data_after_round_trip = {
        "http://www.kde.org/standards/kcfg/1.0}kcfgfile": "",
        "http://www.kde.org/standards/kcfg/1.0}group": {
            "http://www.kde.org/standards/kcfg/1.0}entry": [
                {"{http://www.kde.org/standards/kcfg/1.0}default": "250"},
                {"{http://www.kde.org/standards/kcfg/1.0}default": "krunner,yakuake"}
            ]
        }
    }
    data_as_nt = nt.dumps(data_python)
    assert nt.loads(data_as_nt) == data_after_round_trip

def test_nt_dump_trailing_newline(tmp_path):
    """Verify that dump() adds trailing newline while dumps() does not"""
    test_cases = [
        {"key": "value"},
        ["item1", "item2"],
        "simple string"
    ]

    for data in test_cases:
        # Get dumps() result (no trailing newline unless already in content)
        dumps_result = nt.dumps(data)

        # Test with string path
        path = tmp_path / "test_newline.nt"
        nt.dump(data, str(path))
        file_content = path.read_text()

        # Verify dump() adds exactly one trailing newline
        assert file_content.endswith('\n'), "dump() should add trailing newline"
        assert not file_content.endswith('\n\n'), "dump() should not add double newline"
        assert file_content == dumps_result + '\n', "dump() should be dumps() + newline"

# vim: fdm=marker
