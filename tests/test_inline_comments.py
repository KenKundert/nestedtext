# tests/test_inline_comments.py
#
# Inline-suppression behaviour: when a comment is attached anywhere
# inside an inline dict/list/scalar via the keymap, the dumper must
# expand to multi-line form so the comment is not silently lost
# (nestedtext.py rev 504: ``_inline_would_drop_comments``).
#
# Each parametrised case takes the canonical fixture
#     data = [{1: {2: "nutz"}}]
# attaches a comment via ``annotate`` at one of the slots on one of the
# enclosing entries, and asserts the dumper produces the expected text.
# A second round-trip (dump -> load -> dump -> load -> dump) is also
# checked: the second dump must equal the third (the system reaches a
# fixed point even when the first round-trip drifts).

import pytest

import nestedtext as nt
from nestedtext import Comment, annotate


DATA = [{1: {2: "nutz"}}]


def _strip(s):
    # leading/trailing blank lines off a dedented expected string
    return s.strip("\n")


def _dump(keymap):
    return nt.dumps(DATA, width=90, map_keys=keymap)


def _roundtrip(text):
    keymap = {}
    data = nt.loads(text, top=list, keymap=keymap)
    return nt.dumps(data, width=90, map_keys=keymap)


# ---------------------------------------------------------------------------
# No comments: inline form chosen for the whole document
# ---------------------------------------------------------------------------

def test_no_comments_renders_inline():
    out = _dump({})
    assert out == "[{1: {2: nutz}}]"


# ---------------------------------------------------------------------------
# Static comments at every depth and slot
# ---------------------------------------------------------------------------

STATIC_CASES = [
    pytest.param(
        (0, 1, 2), "value_trailing",
        """
-
    1:
        2: nutz
                # voltz
""",
        id="value_trailing-at-2",
    ),
    pytest.param(
        (0, 1, 2), "value_leading",
        """
-
    1:
        2:
            # voltz
            > nutz
""",
        id="value_leading-at-2",
    ),
    pytest.param(
        (0, 1, 2), "key_trailing",
        """
-
    1:
        2:
                # voltz
            > nutz
""",
        id="key_trailing-at-2",
    ),
    pytest.param(
        (0, 1, 2), "key_leading",
        """
-
    1:
        # voltz
        2: nutz
""",
        id="key_leading-at-2",
    ),
    pytest.param(
        (0, 1), "key_trailing",
        """
-
    1:
            # voltz
        2: nutz
""",
        id="key_trailing-at-1",
    ),
    pytest.param(
        (0, 1), "key_leading",
        """
-
    # voltz
    1:
        2: nutz
""",
        id="key_leading-at-1",
    ),
    pytest.param(
        (0, 1), "value_trailing",
        """
-
    1:
        2: nutz
            # voltz
""",
        id="value_trailing-at-1",
    ),
    pytest.param(
        (0, 1), "value_leading",
        """
-
    1:
        # voltz
        2: nutz
""",
        id="value_leading-at-1",
    ),
    pytest.param(
        (0,), "key_trailing",
        """
-
        # voltz
    1:
        {2: nutz}
""",
        id="key_trailing-at-0",
    ),
    pytest.param(
        (0,), "key_leading",
        """
# voltz
-
    1:
        {2: nutz}
""",
        id="key_leading-at-0",
    ),
    pytest.param(
        (0,), "value_trailing",
        """
-
    1:
        {2: nutz}
        # voltz
""",
        id="value_trailing-at-0",
    ),
    pytest.param(
        (0,), "value_leading",
        """
-
    # voltz
    1:
        {2: nutz}
""",
        id="value_leading-at-0",
    ),
]


@pytest.mark.parametrize("path,slot,expected", STATIC_CASES)
def test_static_comment_suppresses_inline(path, slot, expected):
    keymap = {}
    annotate(path, keymap, **{slot: (Comment("voltz"),)})
    out = _dump(keymap)
    assert out == _strip(expected)
    # A second round-trip reaches a fixed point even when the first
    # drifts (the loader may re-attach the comment to a different slot
    # but the resulting tree is stable).
    once = _roundtrip(out)
    twice = _roundtrip(once)
    assert once == twice


# ---------------------------------------------------------------------------
# Provider (callable) comments at every slot
# ---------------------------------------------------------------------------

DYNAMIC_CASES = [
    pytest.param(
        "key_leading",
        """
-
    1:
        # 2: key leading
        2: nutz
""",
        id="provider-key_leading",
    ),
    pytest.param(
        "key_trailing",
        """
-
    1:
        2:
                # 2: key trailing
            > nutz
""",
        id="provider-key_trailing",
    ),
    pytest.param(
        "value_leading",
        """
-
    1:
        2:
            # 2: value leading
            > nutz
""",
        id="provider-value_leading",
    ),
    pytest.param(
        "value_trailing",
        """
-
    1:
        2: nutz
                # 2: value trailing
""",
        id="provider-value_trailing",
    ),
]


@pytest.mark.parametrize("slot,expected", DYNAMIC_CASES)
def test_provider_comment_for_children(slot, expected):
    """A provider callable installed on the parent (0, 1) decorates
    each of its children -- only child 2 exists -- with the given
    slot's comment."""
    keymap = {}
    annotate(
        (0, 1), keymap,
        **{slot: lambda k, slot=slot: f"{k}: {slot.replace('_', ' ')}"},
    )
    out = _dump(keymap)
    assert out == _strip(expected)


def test_provider_returns_single_comment():
    """A provider may return a single Comment instead of a list."""
    keymap = {}
    annotate(
        (0, 1), keymap,
        key_leading=lambda k: Comment(f"child {k}"),
    )
    out = _dump(keymap)
    assert "# child 2" in out


def test_provider_returns_mixed_iterable():
    """A provider may return an iterable that mixes strings and
    Comment objects -- strings are wrapped on the dumper side."""
    keymap = {}
    annotate(
        (0, 1), keymap,
        key_leading=lambda k: [f"plain {k}", Comment(f"wrapped {k}")],
    )
    out = _dump(keymap)
    assert "# plain 2" in out
    assert "# wrapped 2" in out
