# encoding: utf8
# This test suite runs random text strings on a round trip through NestedText to
# assure that what comes out is what was sent in.  Non-printing characters can
# confuse NestedText (often treated as white space by strip(), which can result
# in invalid indentation errors), so they are filtered out.  Also, NestedText
# maps CR/LF and CR to LF, so the same is done to the input before comparing it
# to the output.

from hypothesis import assume, given, settings, strategies as st
import nestedtext as nt
from random import randint
import re
import sys

max_examples = 1000  # takes several minutes
max_examples = 100

def normalize_line_breaks(s):
    return s.replace('\r\n', '\n').replace('\r', '\n')

non_printing_chars = set(
    chr(n) for n in range(sys.maxunicode+1) if not chr(n).isprintable()
)
def has_invalid_chars_for_strs(s):
    return non_printing_chars & set(s)

def has_invalid_chars_for_dicts(s):
    return (non_printing_chars | set('{}[],:')) & set(s)

def has_invalid_chars_for_lists(s):
    return (non_printing_chars | set('{}[],')) & set(s)

def pad_randomly(match):
    # pad with 0-2 spaces before and after text
    text = match.group(0)
    leading_padding = randint(0,1)*' '
    trailing_padding = randint(0,1)*' '
    return leading_padding + text + trailing_padding

def add_spaces(content, targets):
    if content[0:] not in ['[', '{']:
        return content  # ignore content that is not inline list or dict
    if content.strip(' ') in ['[]', '{}']:
        return content  # ignore an empty list or dict
    return re.sub(f'[{re.escape(targets)}]', pad_randomly, content).lstrip(' ')


@settings(max_examples=max_examples)
@given(st.from_type(bool | None | int | float))
def test_types(v):
    expected = None if v is None else str(v)
    assert nt.loads(nt.dumps(v), top=any) == expected

@settings(max_examples=max_examples)
@given(st.text())
def test_strings(s):
    assert nt.loads(nt.dumps(s), top=str) == normalize_line_breaks(s)


@settings(max_examples=max_examples)
@given(
    st.dictionaries(
        keys = st.text(
            alphabet = st.characters(blacklist_categories='C')
        ),
        values = st.text(
            alphabet = st.characters(blacklist_categories='C')
        )
    )
)
def test_dicts(data):
    expected = {
        normalize_line_breaks(k): normalize_line_breaks(v)
        for k, v in data.items()
    }

    # test normal dump
    result = nt.loads(nt.dumps(data), top=dict)
    assert nt.loads(nt.dumps(data), top=dict) == expected

    # test dump with inlines
    content = nt.dumps(data, width=999)
    assert nt.loads(content, top=dict) == expected

    # test dump with inlines and random spaces
    if content[0:] in ['[', '{']:
        spacey_content = add_spaces(content, '{}[],:')
        assert nt.loads(spacey_content, top=dict) == expected


@settings(max_examples=max_examples)
@given(
    st.lists(
        st.text(
            alphabet = st.characters(blacklist_categories='C')
        )
    )
)
def test_lists(values):
    expected = [normalize_line_breaks(v) for v in values]

    # test normal dump
    assert nt.loads(nt.dumps(values), top=list) == expected

    # test dump with inlines
    content = nt.dumps(values, width=999)
    assert nt.loads(content, top=list) == expected

    # test dump with inlines and random spaces
    if content[0:] in ['[', '{']:
        content = add_spaces(content, '{}[],')
        assert nt.loads(content, top=list) == expected
