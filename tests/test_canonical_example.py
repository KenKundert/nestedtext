# tests/test_canonical_example.py
#
# The canonical worked example for the comment-preservation rules.
# Exercises every comment slot at every depth across a small data
# structure that mixes scalar, dict, and set values.  Use it as the
# go-to reference when changing comment-related code.

from inform import dedent

import nestedtext as nt
from nestedtext import Comment, annotate


def test_canonical_example():
    data = {
        "k0a": {"k1a": "v1a", "k1b": {"v1b"}},
        "k0b": "v0b",
    }
    keymap = {}
    annotate((), keymap, header=(Comment("header"),))
    annotate(("k0a",), keymap, key_leading=(Comment("k0a: key leading"),))
    annotate(("k0a",), keymap, key_trailing=(Comment("k0a: key trailing"),))
    annotate(("k0a",), keymap, value_leading=(Comment("k0a: value leading"),))
    annotate(("k0a",), keymap, value_trailing=(Comment("k0a: value trailing"),))
    annotate(("k0a", "k1a"), keymap, key_leading=(Comment("k1a: key leading"),))
    annotate(("k0a", "k1a"), keymap, key_trailing=(Comment("k1a: key trailing"),))
    annotate(("k0a", "k1a"), keymap, value_leading=(Comment("k1a: value leading"),))
    annotate(("k0a", "k1a"), keymap, value_trailing=(Comment("k1a: value trailing"),))
    annotate(("k0a", "k1b"), keymap, key_leading=(Comment("k1b: key leading"),))
    annotate(("k0a", "k1b"), keymap, key_trailing=(Comment("k1b: key trailing"),))
    annotate(("k0a", "k1b"), keymap, value_leading=(Comment("k1b: value leading"),))
    annotate(
        ("k0a", "k1b"), keymap,
        value_trailing=(
            Comment("k1b: value trailing"),
            Comment("k1b: value trailing #2"),
            Comment("- v1c", indent=8),
        ),
    )
    annotate(("k0b",), keymap, key_leading=(Comment("k0b: key leading"),))
    annotate(("k0b",), keymap, key_trailing=(Comment("k0b: key trailing"),))
    annotate(("k0b",), keymap, value_leading=(Comment("k0b: value leading"),))
    annotate(("k0b",), keymap, value_trailing=(Comment("k0b: value trailing"),))
    annotate((), keymap, footer=(Comment("footer"),))

    expected = dedent("""
        # header

        # k0a: key leading
        k0a:
                # k0a: key trailing
            # k0a: value leading
            # k1a: key leading
            k1a:
                    # k1a: key trailing
                # k1a: value leading
                > v1a
                    # k1a: value trailing
            # k1b: key leading
            k1b:
                    # k1b: key trailing
                # k1b: value leading
                - v1b
                    # k1b: value trailing
                    # k1b: value trailing #2
                # - v1c
                # k0a: value trailing
        # k0b: key leading
        k0b:
                # k0b: key trailing
            # k0b: value leading
            > v0b
                # k0b: value trailing

        # footer
    """).strip("\n")

    result = nt.dumps(data, width=90, map_keys=keymap)
    assert result == expected


def test_canonical_example_reaches_fixed_point():
    """The first round-trip drifts in a few documented spots (see
    velvet-hugging-naur plan).  After one more cycle the document
    must be stable: dump -> load -> dump -> load -> dump must equal
    the second dump.
    """
    data = {
        "k0a": {"k1a": "v1a", "k1b": {"v1b"}},
        "k0b": "v0b",
    }
    keymap = {}
    annotate((), keymap, header=(Comment("header"),))
    annotate(("k0a",), keymap, key_leading=(Comment("k0a: key leading"),))
    annotate(("k0a",), keymap, key_trailing=(Comment("k0a: key trailing"),))
    annotate(("k0a",), keymap, value_leading=(Comment("k0a: value leading"),))
    annotate(("k0a",), keymap, value_trailing=(Comment("k0a: value trailing"),))
    annotate(("k0a", "k1a"), keymap, key_leading=(Comment("k1a: key leading"),))
    annotate(("k0a", "k1a"), keymap, key_trailing=(Comment("k1a: key trailing"),))
    annotate(("k0a", "k1a"), keymap, value_leading=(Comment("k1a: value leading"),))
    annotate(("k0a", "k1a"), keymap, value_trailing=(Comment("k1a: value trailing"),))
    annotate(("k0a", "k1b"), keymap, key_leading=(Comment("k1b: key leading"),))
    annotate(("k0a", "k1b"), keymap, key_trailing=(Comment("k1b: key trailing"),))
    annotate(("k0a", "k1b"), keymap, value_leading=(Comment("k1b: value leading"),))
    annotate(
        ("k0a", "k1b"), keymap,
        value_trailing=(
            Comment("k1b: value trailing"),
            Comment("k1b: value trailing #2"),
            Comment("- v1c", indent=8),
        ),
    )
    annotate(("k0b",), keymap, key_leading=(Comment("k0b: key leading"),))
    annotate(("k0b",), keymap, key_trailing=(Comment("k0b: key trailing"),))
    annotate(("k0b",), keymap, value_leading=(Comment("k0b: value leading"),))
    annotate(("k0b",), keymap, value_trailing=(Comment("k0b: value trailing"),))
    annotate((), keymap, footer=(Comment("footer"),))

    first = nt.dumps(data, width=90, map_keys=keymap)

    km1 = {}
    nt.loads(first, top="dict", keymap=km1)
    second = nt.dumps(nt.loads(first, top="dict"), width=90, map_keys=km1)

    km2 = {}
    nt.loads(second, top="dict", keymap=km2)
    third = nt.dumps(nt.loads(second, top="dict"), width=90, map_keys=km2)

    assert second == third
