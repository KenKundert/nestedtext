# encoding: utf8
# This test suite runs random text strings on a round trip through NestedText to
# assure that what comes out is what was sent in.  Non-printing characters can
# confuse NestedText (often treated as white space by strip(), which can result
# in invalid indentation errors), so they are filtered out.  Also, NestedText
# maps CR/LF and CR to LF, so the same is done to the input before comparing it
# to the output.

from hypothesis import assume, given, settings, strategies as st
import sys
import nestedtext as nt

def normalize_line_breaks(s):
    return s.replace('\r\n', '\n').replace('\r', '\n')

non_printing_chars = set(
    chr(n) for n in range(sys.maxunicode+1) if not chr(n).isprintable()
)
def has_nonprinting_chars(s):
    return non_printing_chars & set(s)

@settings(max_examples=1000)
@given(st.text())
def test_strings(s):
    assert nt.loads(nt.dumps(s), top=str) == normalize_line_breaks(s)

@settings(max_examples=1000)
@given(st.lists(st.tuples(st.text(), st.text())))
def test_dicts(t):
    d = dict(t)

    assume(not any(has_nonprinting_chars(k) or has_nonprinting_chars(v) for k, v in t))

    # test normal dump
    assert nt.loads(nt.dumps(d), top=dict) == {
        normalize_line_breaks(k): normalize_line_breaks(v)
        for k, v in d.items()
    }

    # test dump with inlines
    assert nt.loads(nt.dumps(d, width=999), top=dict) == {
        normalize_line_breaks(k): normalize_line_breaks(v)
        for k, v in d.items()
    }

@settings(max_examples=1000)
@given(st.lists(st.text()))
def test_lists(l):
    assume(not any(has_nonprinting_chars(v) for v in l))

    # test normal dump
    assert nt.loads(nt.dumps(l), top=list) == [normalize_line_breaks(v) for v in l]

    # test dump with inlines
    assert nt.loads(nt.dumps(l, width=999), top=list) == [normalize_line_breaks(v) for v in l]
