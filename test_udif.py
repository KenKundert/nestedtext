# encoding: utf8
import pytest
from textwrap import dedent
from udif import load, dump
from inform import Info, render

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
            "- key2:": "value2:"
            '  #key3  ': '  #value3  '
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
                value 5 part 1
            key 6:
                value 6 part 1
                value 6 part 2
            key 7:
                value 7 part 1

                value 7 part 3

            key 8:
                - value 8.1

                - value 8.2

            key 9:
                - value 9.1
                - value 9.2
            key 10:
                This is a multi-line string.  It should end without a newline.
            key 11:
                This is a multi-line string.  It should end with a newline.

            key 12:

                This is another
                multi-line string.

                This continues the same string.


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
            'key 10': 'This is a multi-line string.  It should end without a newline.',
            'key 11': dedent("""
                This is a multi-line string.  It should end with a newline.
            """).lstrip(),
            'key 12': dedent("""
                This is another
                multi-line string.

                This continues the same string.

            """),
            'key 13': None,
        },
        # invarient {{{3
        invarient = dedent("""
            key 1: value 1
            '- key2:': value2:
            '  #key3  ': '  #value3  '
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
                value 6 part 1
                value 6 part 2
            key 7:
                value 7 part 1

                value 7 part 3

            key 8:
                - value 8.1
                - value 8.2
            key 9:
                - value 9.1
                - value 9.2
            key 10: This is a multi-line string.  It should end without a newline.
            key 11:
                This is a multi-line string.  It should end with a newline.

            key 12:

                This is another
                multi-line string.

                This continues the same string.


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
                trouper segregate militia airway pricey sweetmeat tartan bookstall
                obsession charlady twosome silky puffball grubby ranger notation
                rosebud replicate freshen javelin abbot autocue beater byway

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
                trouper segregate militia airway pricey sweetmeat tartan bookstall
                obsession charlady twosome silky puffball grubby ranger notation
                rosebud replicate freshen javelin abbot autocue beater byway
        """).lstrip('\n'),
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


                - crux
                -

                - ' — '

        """),
        # expected {{{3
        expected = dict(
            tux = None,
            jux = 'lux',
            dux = ['bux', '\n', 'crux', '', ' — ']
        ),
        # invarient {{{3
        invarient = dedent("""
            tux:
            jux: lux
            dux:
                - bux
                -


                - crux
                - ''
                - ' — '
        """).strip('\n')
    ),
)

# test_testcase1() {{{1
def test_testcase1():
    name = 'testcase1'
    case = testcases[name]
    result = load(case.given, name)
    assert result == case.expected, render(result)
    assert dump(result) == case.invarient

# test_testcase2() {{{1
def test_testcase2():
    name = 'testcase2'
    case = testcases[name]
    result = load(case.given, name)
    assert result == case.expected, render(result)
    assert dump(result) == case.invarient

# test_testcase3() {{{1
def test_testcase3():
    name = 'testcase3'
    case = testcases[name]
    result = load(case.given, name)
    assert result == case.expected, render(result)
    assert dump(result) == case.invarient


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

