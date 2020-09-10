# encoding: utf8
import pytest
from textwrap import dedent
import nestedtext
from inform import Error, Info, render, indent

# Utilities {{{1
def clean(s):
    lines = s.splitlines()
    lines = (l.rstrip() for l in lines if not l or not l.startswith('#'))
    return '\n'.join(lines)

class Case(Info):
    pass


# Test cases {{{1
testcases = dict(
    # testcase1 {{{2
    testcase1 = Case(
        # given {{{3
        given = dedent("""\
            # this is a comment, it is ignored
            key 1: value 1

            "- key2:": value2:

            '  #key3  ':   #value3  

            key 4:
                key 4.1: value 4.1
                key 4.2: value 4.2
                key 4.3:
                    key 4.3.1: value 4.3.1
                    key 4.3.2: value 4.3.2
                key 4.4:
                    - value 4.4.1

                    - value 4.4.2
                    -
                        - value 4.4.3.1
                        - value 4.4.3.2
            key 5:
                > value 5 part 1
            key 6:
                > value 6 part 1
                > value 6 part 2
            key 7:
                > value 7 part 1
                >
                > value 7 part 3
                >

            key 8:
                - value 8.1

                - value 8.2

            key 9:
                - value 9.1
                - value 9.2
            key 10:
                > This is a multiline string.  It should end without a newline.
            key 11:
                > This is a multiline string.  It should end with a newline.
                >
            key 12:
                >
                > This is another
                > multiline string.
                >
                > This continues the same string.
                >
                >
            key 13:
        """),
        # expected {{{3
        expected = {
            'key 1': 'value 1',
            '- key2:': 'value2:',
            "  #key3  ": "  #value3  ",
            'key 4': {
                'key 4.1': 'value 4.1',
                'key 4.2': 'value 4.2',
                'key 4.3': {
                    'key 4.3.1': 'value 4.3.1',
                    'key 4.3.2': 'value 4.3.2',
                },
                'key 4.4': [
                    'value 4.4.1',
                    'value 4.4.2',
                    ['value 4.4.3.1', 'value 4.4.3.2'],
                ],
            },
            'key 5': 'value 5 part 1',
            'key 6': dedent("""
                value 6 part 1
                value 6 part 2
            """).strip(),
            'key 7': dedent("""
                value 7 part 1

                value 7 part 3
            """).lstrip(),
            'key 8': ['value 8.1', 'value 8.2'],
            'key 9': ['value 9.1', 'value 9.2'],
            'key 10': 'This is a multiline string.  It should end without a newline.',
            'key 11': dedent("""
                This is a multiline string.  It should end with a newline.
            """).lstrip(),
            'key 12': dedent("""
                This is another
                multiline string.

                This continues the same string.

            """),
            'key 13': '',
        },
        # invarient {{{3
        invarient = dedent("""
            key 1: value 1
            '- key2:': value2:
            '  #key3  ':   #value3  
            key 4:
                key 4.1: value 4.1
                key 4.2: value 4.2
                key 4.3:
                    key 4.3.1: value 4.3.1
                    key 4.3.2: value 4.3.2
                key 4.4:
                    - value 4.4.1
                    - value 4.4.2
                    -
                        - value 4.4.3.1
                        - value 4.4.3.2
            key 5: value 5 part 1
            key 6:
                > value 6 part 1
                > value 6 part 2
            key 7:
                > value 7 part 1
                >
                > value 7 part 3
                >
            key 8:
                - value 8.1
                - value 8.2
            key 9:
                - value 9.1
                - value 9.2
            key 10: This is a multiline string.  It should end without a newline.
            key 11:
                > This is a multiline string.  It should end with a newline.
                >
            key 12:
                >
                > This is another
                > multiline string.
                >
                > This continues the same string.
                >
                >
            key 13:
        """).strip('\n'),
    ),

    # testcase2 {{{2
    testcase2 = Case(
        # given {{{3
        given = dedent("""
            # backup settings for root
            src_dir: /
            excludes:
                - /dev
                - /home/*/.cache
                - /root/*/.cache
                - /proc
                - /sys
                - /tmp
                - /var/cache
                - /var/lock
                - /var/run
                - /var/tmp
            keep:
                hourly: 24
                daily: 7
                weekly: 4
                monthly: 12
                yearly: 5
            passphrase:
                > trouper segregate militia airway pricey sweetmeat tartan bookstall
                > obsession charlady twosome silky puffball grubby ranger notation
                > rosebud replicate freshen javelin abbot autocue beater byway
                >

        """),
        # expected {{{3
        expected = dict(
            src_dir = '/',
            excludes = [
                '/dev',
                '/home/*/.cache',
                '/root/*/.cache',
                '/proc',
                '/sys',
                '/tmp',
                '/var/cache',
                '/var/lock',
                '/var/run',
                '/var/tmp',
            ],
            keep = dict(
                hourly = '24',
                daily = '7',
                weekly = '4',
                monthly = '12',
                yearly = '5',
            ),
            passphrase = dedent("""
                trouper segregate militia airway pricey sweetmeat tartan bookstall
                obsession charlady twosome silky puffball grubby ranger notation
                rosebud replicate freshen javelin abbot autocue beater byway
            """).lstrip(),
        ),
        # invarient {{{3
        invarient = dedent("""
            src_dir: /
            excludes:
                - /dev
                - /home/*/.cache
                - /root/*/.cache
                - /proc
                - /sys
                - /tmp
                - /var/cache
                - /var/lock
                - /var/run
                - /var/tmp
            keep:
                hourly: 24
                daily: 7
                weekly: 4
                monthly: 12
                yearly: 5
            passphrase:
                > trouper segregate militia airway pricey sweetmeat tartan bookstall
                > obsession charlady twosome silky puffball grubby ranger notation
                > rosebud replicate freshen javelin abbot autocue beater byway
                >
        """).strip('\n'),
    ),

    # testcase3 {{{2
    testcase3 = Case(
        # given {{{3
        given = dedent("""\
            # backup settings for root
            tux:
            jux: lux
            dux:
                - bux
                -
                -
                    >
                    >

                - crux
                -

                -  — 

        """),
        # expected {{{3
        expected = dict(
            tux = '',
            jux = 'lux',
            dux = ['bux', '', '\n', 'crux', '', ' — ']
        ),
        # invarient {{{3
        invarient = dedent("""
            tux:
            jux: lux
            dux:
                - bux
                -
                -
                    >
                    >
                - crux
                -
                -  — 
        """).strip('\n')
    ),
)

# test_testcase1() {{{1
def test_testcase1():
    name = 'testcase1'
    case = testcases[name]
    result = nestedtext.loads(case.given, name)
    assert result == case.expected, render(result)
    assert nestedtext.dumps(result) == case.invarient

# test_testcase2() {{{1
def test_testcase2():
    name = 'testcase2'
    case = testcases[name]
    result = nestedtext.loads(case.given, name)
    assert result == case.expected, render(result)
    assert nestedtext.dumps(result) == case.invarient

# test_testcase3() {{{1
def test_testcase3():
    name = 'testcase3'
    case = testcases[name]
    result = nestedtext.loads(case.given, name)
    assert result == case.expected, render(result)
    assert nestedtext.dumps(result) == case.invarient


# test_loads() {{{1
def test_loads():
    content = ''
    data = nestedtext.loads(content)
    assert data == None

    content = dedent("""
        ingredients:
          > green chilies
    """)
    data = nestedtext.loads(content)
    assert data == dict(ingredients = 'green chilies')

    content = dedent("""
        what makes it green\t: \tgreen\tchilies\t
    """)
    data = nestedtext.loads(content)
    assert data == {'what makes it green': '\tgreen\tchilies\t'}

    content = dedent("""
        # this is a comment
        output current: out
        description: Output current
        range: V(gnda) + 0.5V < V < V(vdda) - 0.5V; -500μA <= I <= 500μA
            # this is another comment
        behavior:
            > current:
            >     I = On*Iout;
            # this is mid-string comment
            >     Vout=V;

            >     IoutMeas=I with prail=vdda; nrail=gnda

        nominal: V=1.25V+1Ω*I

            # this is the final comment
    """)
    data = nestedtext.loads(content)
    assert data == {
        "output current": "out",
        "description": "Output current",
        "range": "V(gnda) + 0.5V < V < V(vdda) - 0.5V; -500μA <= I <= 500μA",
        "behavior": dedent("""
            current:
                I = On*Iout;
                Vout=V;
                IoutMeas=I with prail=vdda; nrail=gnda
        """).strip(),
        "nominal": "V=1.25V+1Ω*I",
    }

    content = dedent("""
        key: value " value
    """).strip()
    data = nestedtext.loads(content)
    expected = dict(key = 'value " value')
    assert data == expected

    content = dedent("""
        key: value ' value
    """).strip()
    data = nestedtext.loads(content)
    expected = dict(key = "value ' value")
    assert data == expected

    content = dedent("""
        key "' key:
          > value '" value
    """).strip()
    data = nestedtext.loads(content)
    expected = {"""key "' key""": """value '" value"""}
    assert data == expected

    content = dedent("""
        key1: 'And Fred said "yabba dabba doo!" to Barney.'
        key2: "And Fred said 'yabba dabba doo!' to Barney."
        key3: "And Fred said "yabba dabba doo!" to Barney."
        key4: 'And Fred said 'yabba dabba doo!' to Barney.'
        key5: And Fred said "yabba dabba doo!" to Barney.
        key6: And Fred said 'yabba dabba doo!' to Barney.
    """).strip()
    data = nestedtext.loads(content)
    expected = dict(
        key1 = """'And Fred said "yabba dabba doo!" to Barney.'""",
        key2 = '''"And Fred said 'yabba dabba doo!' to Barney."''',
        key3 = '''"And Fred said "yabba dabba doo!" to Barney."''',
        key4 = """'And Fred said 'yabba dabba doo!' to Barney.'""",
        key5 = """And Fred said "yabba dabba doo!" to Barney.""",
        key6 = """And Fred said 'yabba dabba doo!' to Barney.""",
    )
    assert data == expected

    content = dedent("""
        # various valid dictionary items with unusual unquoted keys
        -#:'>: -#:">:
        -#:">: -#:'>:
        -#'\'>:: -#"\">::
        -#"\">:: -#'\'>::
            # indented comment
        :-#:'>: :-#:">:
        :-#:">: :-#:'>:
        :-#'\'>:: :-#"\">::
        :-#"\">:: :-#'\'>::
                # indented comment
        >:-#:'>: >:-#:">:
        >:-#:">: >:-#:'>:
        >:-#'\'>:: >:-#"\">::
        >:-#"\">:: >:-#'\'>::
    """).strip()
    data = nestedtext.loads(content)
    expected = {
        "-#:'>": '-#:">:',
        '-#:">': "-#:'>:",
        "-#'\'>:": '-#"\">::',
        '-#"\">:': "-#'\'>::",
        ":-#:'>": ':-#:">:',
        ':-#:">': ":-#:'>:",
        ":-#'\'>:": ':-#"\">::',
        ':-#"\">:': ":-#'\'>::",
        ">:-#:'>": '>:-#:">:',
        '>:-#:">': ">:-#:'>:",
        ">:-#'\'>:": '>:-#"\">::',
        '>:-#"\">:': ">:-#'\'>::",
    }
    assert data == expected

    content = dedent("""
        > ingredients
        > green chilies
    """).lstrip()
    expected = dedent("""
        ingredients
        green chilies
    """).strip()
    data = nestedtext.loads(content)
    assert data == expected

    content = dedent("""
        key1 :
        key2 :
    """).lstrip()
    expected = dict(key1='', key2='')
    data = nestedtext.loads(content)
    assert data == expected

    content = dedent("""
        -
        -
    """).lstrip()
    expected = ['', '']
    data = nestedtext.loads(content)
    assert data == expected

    content = dedent("""
        >
        >
    """).lstrip()
    expected = '\n'
    data = nestedtext.loads(content)
    assert data == expected



# test_loads_errors() {{{1
def test_loads_errors():
    content = dedent("""
        ingredients:
            > green chilies
          > red chilies
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content, 'recipe')
    assert str(exception.value) == 'recipe, 4: invalid indentation.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = ('recipe', 4),
        codicil = ('«  > red chilies»\n ↑',),
        source = 'recipe',
        doc = content,
        line = '  > red chilies',
        lineno = 4,
        colno = 0,
        template = 'invalid indentation.',
    )
    assert exception.value.line == '  > red chilies'
    assert exception.value.source == 'recipe'
    assert exception.value.lineno == 4
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        ingredients:
          > green chilies
            > red chilies
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content, 'recipe')
    assert str(exception.value) == 'recipe, 4: invalid indentation.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = ('recipe', 4),
        codicil = ('«    > red chilies»\n ↑',),
        source = 'recipe',
        doc = content,
        line = '    > red chilies',
        lineno = 4,
        colno = 0,
        template = 'invalid indentation.',
    )
    assert exception.value.line == '    > red chilies'
    assert exception.value.source == 'recipe'
    assert exception.value.lineno == 4
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        ingredients:
        - green chilies
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '3: expected dictionary item.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = (3,),
        codicil = ('«- green chilies»\n ↑',),
        doc = content,
        line = '- green chilies',
        lineno = 3,
        colno = 0,
        template = 'expected dictionary item.',
    )
    assert exception.value.line == '- green chilies'
    assert exception.value.source == None
    assert exception.value.lineno == 3
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        - green chilies
        ingredients:
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '3: expected list item.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = (3,),
        codicil = ('«ingredients:»\n ↑',),
        doc = content,
        line = 'ingredients:',
        lineno = 3,
        colno = 0,
        template = 'expected list item.',
    )
    assert exception.value.line == 'ingredients:'
    assert exception.value.source == None
    assert exception.value.lineno == 3
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
            - green chilies
        - red chilies
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content, 'recipe')
    assert str(exception.value) == 'recipe, 2: invalid indentation.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = ('recipe', 2),
        codicil = ('«    - green chilies»\n ↑',),
        source = 'recipe',
        doc = content,
        line = '    - green chilies',
        lineno = 2,
        colno = 0,
        template = 'invalid indentation.',
    )
    assert exception.value.line == '    - green chilies'
    assert exception.value.source == 'recipe'
    assert exception.value.lineno == 2
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        - green chilies
            - red chilies
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content, 'recipe')
    assert str(exception.value) == 'recipe, 3: invalid indentation.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = ('recipe', 3),
        codicil = ('«    - red chilies»\n ↑',),
        source = 'recipe',
        line = '    - red chilies',
        lineno = 3,
        colno = 0,
        doc = content,
        template = 'invalid indentation.',
    )
    assert exception.value.line == '    - red chilies'
    assert exception.value.source == 'recipe'
    assert exception.value.lineno == 3
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        ingredients:
            green chilies
    """).lstrip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '2: unrecognized line.'
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = (2,),
        codicil = ('«    green chilies»',),
        line = '    green chilies',
        lineno = 2,
        doc = content,
        template = 'unrecognized line.',
    )
    assert exception.value.line == '    green chilies'
    assert exception.value.source == None
    assert exception.value.lineno == 2
    assert exception.value.colno == None
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        key: value 1
        key: value 2
    """).lstrip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '2: duplicate key: key.'
    assert exception.value.args == ('key',)
    assert exception.value.kwargs == dict(
        culprit = (2,),
        codicil = ('«key: value 2»\n ↑',),
        doc = content,
        line = 'key: value 2',
        lineno = 2,
        colno = 0,
        template = 'duplicate key: {}.',
    )
    assert exception.value.line == 'key: value 2'
    assert exception.value.source == None
    assert exception.value.lineno == 2
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        key:
            \t    > first line
            \t    > second line
    """).lstrip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == r"2: invalid character in indentation: '\t'."
    assert exception.value.args == ()
    assert exception.value.kwargs == dict(
        culprit = (2,),
        codicil = ('«    \t    > first line»\n     ↑',),
        doc = content,
        line = '    \t    > first line',
        lineno = 2,
        colno = 4,
        template = r"invalid character in indentation: '\t'.",
    )
    assert exception.value.line == '    \t    > first line'
    assert exception.value.source == None
    assert exception.value.lineno == 2
    assert exception.value.colno == 4
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        name :
        name :
    """)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '3: duplicate key: name.'
    assert exception.value.args == ('name',)
    assert exception.value.kwargs == dict(
        culprit = (3,),
        codicil = ('«name :»\n ↑',),
        doc = content,
        line = 'name :',
        lineno = 3,
        colno = 0,
        template = 'duplicate key: {}.',
    )
    assert exception.value.line == 'name :'
    assert exception.value.render(template='llave duplicada: {}.') == '3: llave duplicada: name.'
    assert exception.value.source == None
    assert exception.value.lineno == 3
    assert exception.value.colno == 0
    assert exception.value.doc == content
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    content = dedent("""
        key:
          key1 : value1
          key1 : value2
          key3 : value3
          key4 : value4
    """).strip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '3: duplicate key: key1.'
    extended_codicil = exception.value.get_extended_codicil()
    assert len(extended_codicil) == 1
    expected = dedent("""
        |   2 «  key1 : value1»
        |   3 «  key1 : value2»
        |        ↑
        |   4 «  key3 : value3»
    """).strip()
    extended_codicil = indent(extended_codicil[0], leader='|')
    assert extended_codicil == expected
    assert exception.value.get_codicil()[0] == "«  key1 : value2»\n   ↑"
    assert exception.value.lineno == 3
    assert exception.value.colno == 2

    content = dedent("""
        key1 : value1
        key1 : value2
        key3 : value3
        key4 : value4
    """).strip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '2: duplicate key: key1.'
    extended_codicil = exception.value.get_extended_codicil()
    assert len(extended_codicil) == 1
    expected = dedent("""
        |   1 «key1 : value1»
        |   2 «key1 : value2»
        |      ↑
        |   3 «key3 : value3»
    """).strip()
    extended_codicil = indent(extended_codicil[0], leader='|')
    assert extended_codicil == expected
    assert exception.value.lineno == 2
    assert exception.value.get_codicil()[0] == "«key1 : value2»\n ↑"
    assert exception.value.colno == 0

    content = dedent("""
        key1 : value1
        key2 : value2
        key2 : value3
        key4 : value4
    """).strip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '3: duplicate key: key2.'
    extended_codicil = exception.value.get_extended_codicil('Peek a boo!')
    assert len(extended_codicil) == 2
    expected = dedent("""
        |   2 «key2 : value2»
        |   3 «key2 : value3»
        |      ↑
        |   4 «key4 : value4»
        |Peek a boo!
    """).strip()
    extended_codicil = indent('\n'.join(extended_codicil), leader='|')
    assert extended_codicil == expected
    assert exception.value.lineno == 3
    assert exception.value.get_codicil()[0] == "«key2 : value3»\n ↑"
    assert exception.value.colno == 0

    content = dedent("""
        key1 : value1
        key2 : value2
        key3 : value3
        key3 : value4
    """).strip()
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '4: duplicate key: key3.'
    extended_codicil = exception.value.get_extended_codicil(('Peek a boo!', 'I see you.'))
    assert len(extended_codicil) == 3
    expected = dedent("""
        |   3 «key3 : value3»
        |   4 «key3 : value4»
        |      ↑
        |Peek a boo!
        |I see you.
    """).strip()
    extended_codicil = indent('\n'.join(extended_codicil), leader='|')
    assert extended_codicil == expected
    assert exception.value.lineno == 4
    assert exception.value.get_codicil()[0] == "«key3 : value4»\n ↑"
    assert exception.value.colno == 0

    content = "ingredients"
    with pytest.raises(nestedtext.NestedTextError) as exception:
        nestedtext.loads(content)
    assert str(exception.value) == '1: unrecognized line.'
    assert exception.value.get_codicil()[0] == "«ingredients»"
    assert exception.value.lineno == 1
    assert exception.value.colno == None
    assert exception.value.get_extended_codicil()[0] == "«ingredients»"

# test_dump() {{{1
def test_dump():
    data = {'peach': 3, 'apricot': 8, 'blueberry': '1 lb', 'orange': 4}
    content = nestedtext.dumps(data, sort_keys=True, default=str)
    expected = dedent('''
        apricot: 8
        blueberry: 1 lb
        orange: 4
        peach: 3
    ''').strip()
    assert content == expected

    data = ('peach', 'apricot', 'blueberry', ['date', 'apple'], 'orange')
    content = nestedtext.dumps(data)
    expected = dedent('''
        - peach
        - apricot
        - blueberry
        -
            - date
            - apple
        - orange
    ''').strip()
    assert content == expected

    val = Info(val=42)
    renderers = {Info: lambda v: f'Info(\n    val={v.val}\n)'}
    content = nestedtext.dumps(dict(name = val), renderers=renderers)
    expected = dedent('''
        name:
            Info(
                val=42
            )
    ''').strip()
    assert content == expected

    content0 = dedent("""
        ingredients:
          - green chilies
          - red chilies
    """)
    data = nestedtext.loads(content0)
    assert data == dict(ingredients = ['green chilies', 'red chilies'])
    content1 = nestedtext.dumps(data, indent=2)
    assert content1 == content0.strip()

    data = dict(key = 'value " value')
    content = nestedtext.dumps(data, indent=2)
    expected = dedent("""
        key: value " value
    """).strip()
    assert content == expected

    data = dict(key = "value ' value")
    content = nestedtext.dumps(data, indent=2)
    expected = dedent("""
        key: value ' value
    """).strip()
    assert content == expected

    data = {"""key "' key""": """value '" value"""}
    content = nestedtext.dumps(data, indent=2)
    expected = dedent("""
        key "' key: value '" value
    """).strip()
    assert content == expected

    data = dict(key = 'And Fred said "yabba dabba doo!" to Barney.')
    content = nestedtext.dumps(data, indent=2)
    expected = dedent("""
        key: And Fred said "yabba dabba doo!" to Barney.
    """).strip()
    assert content == expected

    content = dedent("""
        # the following uses tabs in a legal way
        treasurer:
            name\t : \t       Fumiko\tPurvis    \t
            address:
                > \t 3636 Buffalo Ave \t
                > \t Topika, Kansas 20692\t 
    """)
    data = nestedtext.loads(content)
    expected_data = dict(
        treasurer = dict(
            name = '\t       Fumiko\tPurvis    \t',
            address = '\t 3636 Buffalo Ave \t\n\t Topika, Kansas 20692\t '
        )
    )
    assert data == expected_data
    achieved_content = nestedtext.dumps(data, indent=2)
    expected_content = dedent("""
        treasurer:
          name: \t       Fumiko\tPurvis    \t
          address:
            > \t 3636 Buffalo Ave \t
            > \t Topika, Kansas 20692\t 
    """).strip('\n')
    assert achieved_content == expected_content

    data = {}
    content = nestedtext.dumps(data)
    assert content == ""

    data = []
    content = nestedtext.dumps(data)
    assert content == ""

    data = ""
    content = nestedtext.dumps(data)
    content = '>'

    data = []
    content = nestedtext.dumps(data)
    content = '-'

    data = {}
    content = nestedtext.dumps(data)
    content = ':'

    data = 42
    content = nestedtext.dumps(data)
    content = '> 42'

    data = {"""key '" key""": 'value'}
    content = nestedtext.dumps(data)
    assert content == """key '" key: value"""


# test_dumps_errors() {{{1
def test_dumps_errors():

    data = {'peach': '3', 'apricot\n': '8', 'blueberry': '1 lb', 'orange': '4'}
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data)
    assert str(exception.value) == "'apricot\\n': keys must not contain newlines."
    assert exception.value.args == ('apricot\n',)
    assert exception.value.kwargs == dict(
        culprit = ("'apricot\\n'",),
        template = 'keys must not contain newlines.',
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    data = dict(name=42)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data, default='strict')
    assert str(exception.value) == "42: unsupported type."
    assert exception.value.args == (42,)
    assert exception.value.kwargs == dict(
        culprit = ('42',),
        template = 'unsupported type.',
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    data = dict(name=42.0)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data, default='strict')
    assert str(exception.value) == "42.0: unsupported type."
    assert exception.value.args == (42.0,)
    assert exception.value.kwargs == dict(
        culprit = ('42.0',),
        template = 'unsupported type.',
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    data = dict(name=True)
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data, default='strict')
    assert str(exception.value) == "True: unsupported type."
    assert exception.value.args == (True,)
    assert exception.value.kwargs == dict(
        culprit = ('True',),
        template = 'unsupported type.',
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    data = dict(name=42)
    renderers = {int: False}
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data, renderers=renderers)
    assert str(exception.value) == "42: unsupported type."
    assert exception.value.args == (42,)
    assert exception.value.kwargs == dict(
        culprit = ('42',),
        template = 'unsupported type.',
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    data = {"""'key " key'""": 'value'}
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data)
    assert str(exception.value) == """'key " key': keys that require quoting must not contain both " and '."""
    assert exception.value.args == ("""'key " key'""",)
    assert exception.value.kwargs == dict(
        culprit = (r"""'key " key'""",),
        template =  """keys that require quoting must not contain both " and '."""
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

    data = {'''"key ' key"''': 'value'}
    with pytest.raises(nestedtext.NestedTextError) as exception:
        content = nestedtext.dumps(data)
    assert str(exception.value) == '''"key ' key": keys that require quoting must not contain both " and '.'''
    assert exception.value.args == ('''"key ' key"''',)
    assert exception.value.kwargs == dict(
        culprit = (r'''"key ' key"''',),
        template =  """keys that require quoting must not contain both " and '."""
    )
    assert isinstance(exception.value, Error)
    assert isinstance(exception.value, ValueError)

# main {{{1
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

