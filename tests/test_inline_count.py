# tests/test_inline_count.py
#
# Cover the dumper's ``inline_count`` argument (minimum number of items
# required to be eligible for inline form) and the ``len()``-failure
# fallback for objects that look like a mapping or collection but do
# not implement ``__len__``.

from collections.abc import Mapping, Sequence

import nestedtext as nt


# ---------------------------------------------------------------------------
# inline_count threshold
# ---------------------------------------------------------------------------

def test_inline_count_threshold_for_dict():
    """A dict with fewer items than ``inline_count`` is rendered in
    block form even when width and inline_level allow inlining."""
    out = nt.dumps({"a": "1", "b": "2"}, width=80, inline_count=3)
    assert out == "a: 1\nb: 2"
    # raising the item count above the threshold flips it back to
    # inline.
    out = nt.dumps({"a": "1", "b": "2", "c": "3"}, width=80, inline_count=3)
    assert out == "{a: 1, b: 2, c: 3}"


def test_inline_count_threshold_for_list():
    """Same threshold logic for lists."""
    out = nt.dumps(["x", "y"], width=80, inline_count=3)
    assert out == "- x\n- y"
    out = nt.dumps(["x", "y", "z"], width=80, inline_count=3)
    assert out == "[x, y, z]"


def test_inline_count_default_one_allows_singleton_inline():
    """Default ``inline_count=1`` permits any non-empty collection to
    be inlined when other constraints allow it."""
    out = nt.dumps({"only": "1"}, width=80)
    assert out == "{only: 1}"
    out = nt.dumps(["solo"], width=80)
    assert out == "[solo]"


def test_list_too_many_items_for_inline_width():
    """A list with more than ``width/3`` items is forced to block form
    even when each individual item is short and the inline form would
    technically fit within ``width``.  This prevents long thin
    one-line lists that would be hard to scan.
    """
    out = nt.dumps(["a", "b", "c", "d", "e"], width=9)
    # five items, width/3 = 3, so 5 > 3 -> block.
    assert not out.startswith("[")
    assert out.startswith("- a")


# ---------------------------------------------------------------------------
# Objects without ``__len__``
# ---------------------------------------------------------------------------

class _MappingNoLen(Mapping):
    """A Mapping that raises ``TypeError`` from ``__len__``.  ``__bool__``
    is overridden so the dumper's early truthiness checks do not call
    ``__len__`` via the ABC default.
    """
    def __init__(self, d):
        self._d = d

    def __getitem__(self, key):
        return self._d[key]

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        raise TypeError("does not have len()")

    def __bool__(self):
        return True


class _SequenceNoLen(Sequence):
    """Similarly, a Sequence whose ``__len__`` raises."""
    def __init__(self, items):
        self._items = items

    def __getitem__(self, idx):
        return self._items[idx]

    def __len__(self):
        raise TypeError("does not have len()")

    def __bool__(self):
        return True


def test_dumps_mapping_without_len_renders_inline():
    """A Mapping that raises from ``__len__`` skips the size guards but
    still renders inline (the post-render width check uses ``len()`` on
    the produced string, which is fine).
    """
    m = _MappingNoLen({"k1": "v1", "k2": "v2"})
    out = nt.dumps(m, width=80)
    assert out == "{k1: v1, k2: v2}"


def test_dumps_sequence_without_len_renders_inline():
    s = _SequenceNoLen(["a", "b", "c"])
    out = nt.dumps(s, width=80)
    assert out == "[a, b, c]"


def test_dumps_mapping_without_len_falls_back_to_block_when_too_wide():
    """If the inline form would exceed ``width``, the dumper falls back
    to block form even when ``__len__`` cannot be consulted up front."""
    m = _MappingNoLen({"key1": "a very long value " * 5})
    out = nt.dumps(m, width=20)
    # block form: no enclosing braces.
    assert not out.startswith("{")
    assert "}" not in out
    assert out.startswith("key1:")


def test_dumps_sequence_without_len_falls_back_to_block_when_too_wide():
    s = _SequenceNoLen(["a very long value " * 5])
    out = nt.dumps(s, width=20)
    # block form: no enclosing brackets.
    assert not out.startswith("[")
    assert "]" not in out
    assert out.startswith("-")
