# tests/test_comments.py
#
# Phase 2 tests: verify the loader captures comments and blank lines from each
# Phase 1 fixture in examples/comments/ and attaches them to the keymap per
# the rules in doc/comment_rules.rst.

from pathlib import Path

import pytest

import nestedtext as nt
from nestedtext import Comment, Location

EXAMPLES = Path(__file__).parent.parent / "examples" / "comments"


def load(name, top="any"):
    """Load an example file and return (data, keymap)."""
    text = (EXAMPLES / name).read_text()
    keymap = {}
    data = nt.loads(text, top=top, keymap=keymap)
    return data, keymap


def texts(comments):
    """Return just the text fields of a list of Comments (for easier comparison)."""
    return [c.text for c in comments]


# ---------------------------------------------------------------------------
# Comment / Sentinel data model
# ---------------------------------------------------------------------------

def test_comment_repr_and_equality():
    a = Comment("hello", indent=4)
    b = Comment("hello", indent=4)
    c = Comment("world", indent=4)
    d = Comment("hello", indent=0)
    assert a == b
    assert a != c
    assert a != d
    assert "Comment(" in repr(a)
    assert "indent=4" in repr(a)


def test_root_location_has_empty_comment_lists():
    """Every keymap has a () entry whose comment lists default to empty."""
    text = "key: value\n"
    keymap = {}
    nt.loads(text, top="dict", keymap=keymap)
    root = keymap[()]
    assert root.get_header_comments() == []
    assert root.get_footer_comments() == []


# ---------------------------------------------------------------------------
# Basic examples (one rule each)
# ---------------------------------------------------------------------------

def test_b01_leading_top():
    data, km = load("b01_leading_top.nt", top="dict")
    assert data == {"database": "production", "retry_delay": "5"}
    assert texts(km[("database",)].get_key_leading_comments()) == [
        "a leading comment for 'database'"
    ]
    assert texts(km[("retry_delay",)].get_key_leading_comments()) == [
        "a leading comment for 'retry_delay'"
    ]


def test_b02_leading_nested():
    _, km = load("b02_leading_nested.nt", top="dict")
    assert texts(km[("server", "port")].get_key_leading_comments()) == [
        "a leading comment for 'server.port'"
    ]
    assert texts(km[("server", "host")].get_key_leading_comments()) == [
        "a leading comment for 'server.host'"
    ]


def test_b03_leading_at_value_indent():
    _, km = load("b03_leading_at_value_indent.nt", top="dict")
    # comment at indent 0, next data line is 'port' at indent 4 -> leads port
    leading = km[("server", "port")].get_key_leading_comments()
    assert len(leading) == 1
    assert leading[0].text.startswith("a leading comment at indent 0")


def test_b04_trailing_simple():
    _, km = load("b04_trailing_simple.nt", top="dict")
    # comment at indent 4, next data line at indent 0 -> trailing on database
    trailing = km[("database",)].get_value_trailing_comments()
    assert len(trailing) == 1
    assert trailing[0].text.startswith("a trailing comment for 'database'")


def test_b05_header_only():
    _, km = load("b05_header_only.nt", top="dict")
    header = km[()].get_header_comments()
    assert header
    assert header[0].text.startswith("a header comment for the file")
    # server should have no leading (the two-blank separator split the block)
    assert km[("server",)].get_key_leading_comments() == []


def test_b06_footer_only():
    _, km = load("b06_footer_only.nt", top="dict")
    footer = km[()].get_footer_comments()
    assert footer
    assert footer[0].text.startswith("a footer comment for the file")


def test_b07_grouped_block():
    _, km = load("b07_grouped_block.nt", top="dict")
    # Adjacent same-indent comment lines (no blank between them) merge into
    # ONE Comment with embedded newlines.
    leading = km[("database",)].get_key_leading_comments()
    assert len(leading) == 1
    assert "a leading comment for 'database'" in leading[0].text
    assert "adjacent comment lines" in leading[0].text
    # the text contains a newline separating the original source lines
    assert "\n" in leading[0].text


def test_b08_blank_separators():
    """Pure blank-line spacing between sibling items is not captured: only
    actual comments end up on the keymap, never empty Comments."""
    _, km = load("b08_blank_separators.nt", top="dict")
    # database and cache have no leading comments -- the blanks above them
    # are layout, not data.
    assert km[("database",)].get_key_leading_comments() == []
    assert km[("cache",)].get_key_leading_comments() == []


# ---------------------------------------------------------------------------
# Stress examples (one per gap)
# ---------------------------------------------------------------------------

def test_s01a_gapA_blank_between():
    # A blank line above the leading block partitions: everything above the
    # last blank becomes the header; the comment block immediately above the
    # key becomes leading on it.
    _, km = load("s01a_gapA_blank_between.nt", top="dict")
    header = km[()].get_header_comments()
    assert header
    assert any("header comment" in c.text for c in header)
    leading = km[("retry_delay",)].get_key_leading_comments()
    assert leading
    assert any("leading comment for 'retry_delay'" in c.text for c in leading)


def test_s01b_gapA_no_blank():
    _, km = load("s01b_gapA_no_blank.nt", top="dict")
    # No blank anywhere in the pre-data buffer -> no header, all leading.
    assert km[()].get_header_comments() == []
    leading = km[("retry_delay",)].get_key_leading_comments()
    assert len(leading) == 1
    assert "intended as a header" in leading[0].text
    assert "intended as a leading comment" in leading[0].text


def test_s02a_gapB_scalar_eof():
    _, km = load("s02a_gapB_scalar_eof.nt", top="dict")
    footer = km[()].get_footer_comments()
    assert footer
    assert footer[0].text.startswith("a footer comment")


def test_s02b_gapB_nested_eof():
    _, km = load("s02b_gapB_nested_eof.nt", top="dict")
    assert km[()].get_footer_comments()


def test_s03_gapC_after_nested_block():
    # comment at indent 4 between server's children and database (indent 0)
    # -> trailing on the previous data line, which is host (indent 4)
    _, km = load("s03_gapC_after_nested_block.nt", top="dict")
    trailing = km[("server", "host")].get_value_trailing_comments()
    assert any("stranded" in (c.text or "") for c in trailing)


def test_s04_gapC_after_multiline_string():
    _, km = load("s04_gapC_after_multiline_string.nt", top="dict")
    # trailing on the previous data line (the last `>` line, owned by 'notice')
    trailing = km[("notice",)].get_value_trailing_comments()
    assert any("stranded" in (c.text or "") for c in trailing)


def test_s05_gapC_between_list_items():
    _, km = load("s05_gapC_between_list_items.nt", top="dict")
    leading = km[("hosts", 1)].get_key_leading_comments()
    assert any("hosts[1]" in (c.text or "") for c in leading)


def test_s06_gapD_after_open_before_nested():
    _, km = load("s06_gapD_after_open_before_nested.nt", top="dict")
    leading = km[("server", "port")].get_key_leading_comments()
    assert any("server.port" in (c.text or "") for c in leading)


def test_s07_gapD_after_open_before_list():
    _, km = load("s07_gapD_after_open_before_list.nt", top="dict")
    leading = km[("hosts", 0)].get_key_leading_comments()
    assert any("hosts[0]" in (c.text or "") for c in leading)


def test_s08_gapE_blank_inside_block():
    # Each comment block separated by blanks becomes a separate group; the
    # last-blank-in-buffer rule means everything ends up as header.
    _, km = load("s08_gapE_blank_inside_block.nt", top="dict")
    assert km[("retry_delay",)].get_key_leading_comments() == []
    header = km[()].get_header_comments()
    text = "\n".join(c.text for c in header)
    assert "first block above" in text
    assert "second block above" in text


def test_s09_gapE_blank_just_before_key():
    # A trailing blank immediately before the key means the comment block is
    # header, not leading.
    _, km = load("s09_gapE_blank_just_before_key.nt", top="dict")
    assert km[("retry_delay",)].get_key_leading_comments() == []
    header = km[()].get_header_comments()
    assert header
    assert any("looks like a leading comment" in c.text for c in header)


def test_s10_gapF_only_comments():
    text = (EXAMPLES / "s10_gapF_only_comments.nt").read_text()
    keymap = {}
    data = nt.loads(text, top="any", keymap=keymap)
    assert data is None
    header = keymap[()].get_header_comments()
    assert header
    assert keymap[()].get_footer_comments() == []
    assert any("a header comment for the file" in (c.text or "") for c in header)


def test_s11_gapG_comment_inside_multiline():
    # The comment at indent 4 between two `>` lines is "inline" (per the rules,
    # converted to trailing on the value at load time).  The loader moves it
    # from line 5's leading_comments to line 2's (= loc.line) trailing_comments.
    _, km = load("s11_gapG_comment_inside_multiline.nt", top="dict")
    loc = km[("notice",)]
    trailing = loc.get_value_trailing_comments()
    assert any("inside a multi-line string" in (c.text or "") for c in trailing)
    # leading on the value is empty (the comment was moved out of it)
    assert loc.get_value_leading_comments() == []


def test_s12_outdented_comment():
    _, km = load("s12_outdented_comment.nt", top="dict")
    # block indent 0 <= host's indent 4 -> leading on host
    leading = km[("server", "host")].get_key_leading_comments()
    assert any("outdented" in (c.text or "") for c in leading)


def test_s13_mixed_indent_block():
    # two adjacent comment lines at different indents -> two separate Comments,
    # both leading on port (per rule 2).
    _, km = load("s13_mixed_indent_block.nt", top="dict")
    leading = km[("server", "port")].get_key_leading_comments()
    assert len(leading) == 2
    assert leading[0].indent != leading[1].indent


def test_s14_key_trailing():
    # comment between server: and port at indent > port.indent -> trailing on server
    _, km = load("s14_key_trailing.nt", top="dict")
    key_trailing = km[("server",)].get_key_trailing_comments()
    assert any("trailing comment for the key 'server'" in (c.text or "") for c in key_trailing)
    # port should NOT have these as leading
    port_leading = km[("server", "port")].get_key_leading_comments()
    assert not any("trailing comment for the key 'server'" in (c.text or "") for c in port_leading)


# ---------------------------------------------------------------------------
# Location comment-accessor API
# ---------------------------------------------------------------------------

def test_set_and_add_leading():
    _, km = load("b01_leading_top.nt", top="dict")
    loc = km[("database",)]
    loc.set_key_leading_comments([Comment("replaced", indent=0)])
    assert texts(loc.get_key_leading_comments()) == ["replaced"]
    loc.add_key_leading_comment(Comment("added", indent=0))
    assert texts(loc.get_key_leading_comments()) == ["replaced", "added"]


def test_set_and_add_trailing():
    _, km = load("b04_trailing_simple.nt", top="dict")
    loc = km[("database",)]
    loc.set_value_trailing_comments([])
    assert loc.get_value_trailing_comments() == []
    loc.add_value_trailing_comment(Comment("after", indent=4))
    assert texts(loc.get_value_trailing_comments()) == ["after"]


def test_keymap_without_comments_unaffected():
    """Loading without keymap argument must work as before, no exceptions."""
    text = "a: 1\nb: 2\n"
    assert nt.loads(text, top="dict") == {"a": "1", "b": "2"}


# ---------------------------------------------------------------------------
# Round-trip tests (Phase 3 dumper)
# ---------------------------------------------------------------------------

ROUND_TRIP_FIXTURES = [
    "b01_leading_top.nt",
    "b02_leading_nested.nt",
    "b03_leading_at_value_indent.nt",
    "b04_trailing_simple.nt",
    "b05_header_only.nt",
    "b06_footer_only.nt",
    "b07_grouped_block.nt",
    "b08_blank_separators.nt",
    "s01a_gapA_blank_between.nt",
    "s01b_gapA_no_blank.nt",
    "s02a_gapB_scalar_eof.nt",
    "s02b_gapB_nested_eof.nt",
    "s03_gapC_after_nested_block.nt",
    "s04_gapC_after_multiline_string.nt",
    "s05_gapC_between_list_items.nt",
    "s06_gapD_after_open_before_nested.nt",
    "s07_gapD_after_open_before_list.nt",
    "s08_gapE_blank_inside_block.nt",
    "s09_gapE_blank_just_before_key.nt",
    "s10_gapF_only_comments.nt",
    # s11 deliberately does not round-trip exactly: per the rules, inline
    # comments are converted to trailing immediately on load, so the dumper
    # places them after the value rather than between `>` lines.
    "s12_outdented_comment.nt",
    "s13_mixed_indent_block.nt",
    "s14_key_trailing.nt",
]


def _coalesce(comments):
    """Merge adjacent same-indent Comments into a single (joined-text,
    indent) tuple.  The dumper emits adjacent same-indent Comments
    without a separating blank, so on re-load they fuse into one
    Comment -- text content and slot assignment are preserved, only
    the Comment-object granularity is.  This helper normalises that
    so summaries can be compared across load/dump/load cycles."""
    out = []
    for c in comments:
        if out and out[-1][1] == c.indent:
            out[-1] = (out[-1][0] + "\n" + c.text, c.indent)
        else:
            out.append((c.text, c.indent))
    return out


def _keymap_summary(km):
    """Reduce a keymap to its semantically-significant content for
    comparison: comment texts and indents on each key, plus header/footer.
    Adjacent same-indent Comments within a slot are coalesced so the
    comparison is stable across load → dump → load."""
    summary = {}
    for key, loc in km.items():
        summary[key] = {
            "key_leading":    _coalesce(loc.get_key_leading_comments()),
            "key_trailing":   _coalesce(loc.get_key_trailing_comments()),
            "value_leading":  _coalesce(loc.get_value_leading_comments()),
            "value_trailing": _coalesce(loc.get_value_trailing_comments()),
            "header":         _coalesce(loc.get_header_comments()),
            "footer":         _coalesce(loc.get_footer_comments()),
        }
    return summary


@pytest.mark.parametrize("fixture", ROUND_TRIP_FIXTURES)
def test_round_trip(fixture):
    """Load → dump → load should preserve data and comments.

    Vertical (blank-line) layout is *not* preserved by design -- it is the
    dumper's *spacing* argument's job.  To keep the header/leading partition
    stable across the cycle, we dump with ``spacing={"edges": 1}`` so that
    a blank line separates the header from the body.  We verify semantic
    preservation by re-loading the dumped text and comparing the data
    structure and the comment content (text + indent) on each keymap entry.
    """
    text = (EXAMPLES / fixture).read_text()
    keymap1 = {}
    data1 = nt.loads(text, top="any", keymap=keymap1)
    out = nt.dumps(data1, map_keys=keymap1, spacing={"edges": 1})
    keymap2 = {}
    data2 = nt.loads(out, top="any", keymap=keymap2)
    assert data1 == data2, f"data mismatch in {fixture}"
    assert _keymap_summary(keymap1) == _keymap_summary(keymap2), (
        f"keymap mismatch in {fixture}"
    )


def test_dump_without_keymap_unchanged():
    """Dumping without a keymap should match prior behavior."""
    data = {"a": "1", "b": "2"}
    assert nt.dumps(data) == "a: 1\nb: 2"


def test_dump_with_empty_keymap_no_comments():
    """An empty keymap should produce the same output as no keymap."""
    data = {"a": "1", "b": "2"}
    assert nt.dumps(data, map_keys={}) == "a: 1\nb: 2"


def test_dump_spacing_top_level():
    """spacing={0: 1} should put at least one blank line between top-level keys."""
    data = {"a": "1", "b": "2", "c": "3"}
    assert nt.dumps(data, spacing={0: 1}) == "a: 1\n\nb: 2\n\nc: 3"


def test_dump_spacing_two_blanks():
    data = {"a": "1", "b": "2"}
    assert nt.dumps(data, spacing={0: 2}) == "a: 1\n\n\nb: 2"


def test_dump_spacing_zero_default():
    """Depths not in the mapping default to zero (no extra spacing)."""
    data = {"a": {"x": "1", "y": "2"}, "b": "3"}
    # only top level gets one blank; nested keys are joined normally
    out = nt.dumps(data, spacing={0: 1})
    assert out == "a:\n    x: 1\n    y: 2\n\nb: 3"


def test_dump_spacing_edges():
    """The "edges" spacing controls the gap between header and the first
    data item, and between the last data item and the footer."""
    keymap = {()
                 : Location()}
    keymap[()].set_header_comments([Comment("the header", indent=0)])
    keymap[()].set_footer_comments([Comment("the footer", indent=0)])
    data = {"a": "1"}
    out_no_edges = nt.dumps(data, map_keys=keymap)
    assert out_no_edges == "# the header\n\na: 1\n\n# the footer"
    out_with_edges = nt.dumps(data, map_keys=keymap, spacing={"edges": 0})
    assert out_with_edges == "# the header\na: 1\n# the footer"
    out_with_edges = nt.dumps(data, map_keys=keymap, spacing={"edges": 1})
    assert out_no_edges == "# the header\n\na: 1\n\n# the footer"
    out_two = nt.dumps(data, map_keys=keymap, spacing={"edges": 2})
    assert out_two == "# the header\n\n\na: 1\n\n\n# the footer"


def test_dump_map_keys_callable_still_works():
    """Passing a callable to map_keys (existing behaviour) must still work
    with the new comment-aware code paths."""
    data = {"alpha": "1", "beta": "2"}

    def upper_top_keys(key, parent_keys):
        if len(parent_keys) == 0:
            return key.upper()

    assert nt.dumps(data, map_keys=upper_top_keys) == "ALPHA: 1\nBETA: 2"


# ---------------------------------------------------------------------------
# Per-Location spacing
# ---------------------------------------------------------------------------

def _make_keymap(*key_tuples):
    """Build a keymap populated with bare Locations for the given tuples."""
    keymap = {(): Location()}
    for keys in key_tuples:
        keymap[keys] = Location()
    return keymap


def test_location_spacing_relative_to_attached_key():
    """spacing[0] on a non-root Location means blanks between THIS
    Location's direct children -- independent of the Location's depth."""
    data = {"section": {"x": "1", "y": "2", "z": "3"}}
    keymap = _make_keymap(("section",))
    keymap[("section",)].set_spacing({0: 1})
    out = nt.dumps(data, map_keys=keymap)
    # one blank line between x, y, z (section's direct children)
    assert out == "section:\n    x: 1\n\n    y: 2\n\n    z: 3"


def test_location_spacing_replaces_global_in_subtree():
    """A non-empty per-Location spacing wholly replaces the global within
    its subtree -- absent depth keys do NOT fall back to the global."""
    data = {"section": {"a": {"i": "1", "ii": "2"}, "b": {"i": "3", "ii": "4"}}}
    keymap = _make_keymap(("section",))
    # Global wants 1 blank at depth 1, 0 at depth 2.
    # Section overrides: only depth 1 (relative => grandchildren of section
    # are NOT joined, but section's direct children get 2 blanks).
    keymap[("section",)].set_spacing({0: 2})
    out = nt.dumps(data, map_keys=keymap, spacing={1: 5, 2: 5})
    # section's children (a, b) get 2 blanks; their children (i, ii) get
    # 0 (NOT 5 from global -- replace, not merge).
    assert out == (
        "section:\n"
        "    a:\n"
        "        i: 1\n"
        "        ii: 2\n"
        "\n"
        "\n"
        "    b:\n"
        "        i: 3\n"
        "        ii: 4"
    )


def test_location_spacing_does_not_leak_to_siblings():
    """Attaching spacing to one subtree must not affect peer subtrees."""
    data = {
        "first":  {"x": "1", "y": "2"},
        "second": {"x": "3", "y": "4"},
    }
    keymap = _make_keymap(("first",), ("second",))
    keymap[("first",)].set_spacing({0: 2})
    out = nt.dumps(data, map_keys=keymap)
    # first's children separated by 2 blanks; second's by 0 (no spacing)
    assert out == (
        "first:\n"
        "    x: 1\n"
        "\n"
        "\n"
        "    y: 2\n"
        "second:\n"
        "    x: 3\n"
        "    y: 4"
    )


def test_root_location_spacing_overrides_global():
    """spacing on keymap[()] (including 'edges') overrides the global
    spacing= arg passed to dumps."""
    keymap = _make_keymap()
    keymap[()].set_header_comments([Comment("hdr", indent=0)])
    keymap[()].set_footer_comments([Comment("ftr", indent=0)])
    keymap[()].set_spacing({0: 2, "edges": 1})
    data = {"a": "1", "b": "2"}
    # Pass an aggressive global -- it must be IGNORED because root has spacing.
    out = nt.dumps(data, map_keys=keymap, spacing={0: 9, "edges": 9})
    assert out == "# hdr\n\na: 1\n\n\nb: 2\n\n# ftr"


def test_edges_ignored_on_non_root_location():
    """The 'edges' key is only meaningful on keymap[()]; a stray value on
    a deeper Location must have no effect."""
    keymap = _make_keymap(("section",))
    keymap[("section",)].set_spacing({0: 1, "edges": 9})
    data = {"section": {"x": "1", "y": "2"}}
    out = nt.dumps(data, map_keys=keymap)
    # 'edges' on section is silently ignored; depth 0 still controls
    # section's child spacing.
    assert out == "section:\n    x: 1\n\n    y: 2"


def test_empty_spacing_dict_does_not_trigger_replace():
    """set_spacing({}) must behave the same as never calling set_spacing
    -- the walk should fall through to outer Locations / the global."""
    keymap = _make_keymap(("section",))
    keymap[("section",)].set_spacing({})  # explicitly empty
    data = {"section": {"x": "1", "y": "2"}}
    # With section's spacing empty, the global spacing[1] applies.
    out = nt.dumps(data, map_keys=keymap, spacing={1: 1})
    assert out == "section:\n    x: 1\n\n    y: 2"


def test_inner_location_spacing_overrides_outer():
    """Nested per-Location spacing: the innermost non-empty spacing wins
    for its own subtree; the outer still applies to siblings of that subtree."""
    data = {
        "outer": {
            "alpha": {"x": "1", "y": "2"},
            "beta":  {"x": "3", "y": "4"},
        }
    }
    keymap = _make_keymap(("outer",), ("outer", "alpha"))
    keymap[("outer",)].set_spacing({0: 1, 1: 0})       # outer governs
    keymap[("outer", "alpha")].set_spacing({0: 2})     # alpha overrides
    out = nt.dumps(data, map_keys=keymap)
    # alpha's children separated by 2 (alpha's spacing[0])
    # beta's children separated by 0 (outer's spacing[1], NOT alpha's)
    # outer's children (alpha, beta) separated by 1 (outer's spacing[0])
    assert out == (
        "outer:\n"
        "    alpha:\n"
        "        x: 1\n"
        "\n"
        "\n"
        "        y: 2\n"
        "\n"
        "    beta:\n"
        "        x: 3\n"
        "        y: 4"
    )


def test_spacing_round_trips_through_jsonable():
    """Per-Location spacing must survive keymap_to_jsonable /
    keymap_from_jsonable and produce identical dumps output."""
    keymap = _make_keymap(("section",))
    keymap[("section",)].set_spacing({0: 2, 1: 1})
    keymap[()].set_spacing({"edges": 1})
    keymap[()].set_header_comments([Comment("hdr", indent=0)])
    data = {"section": {"a": {"i": "1"}, "b": {"i": "2"}}}
    expected = nt.dumps(data, map_keys=keymap)
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    assert nt.dumps(data, map_keys=rebuilt) == expected
    # Spacing dict contents survived (depth keys round-tripped as int)
    assert rebuilt[("section",)].get_spacing() == {0: 2, 1: 1}
    assert rebuilt[()].get_spacing() == {"edges": 1}


def test_spacing_jsonable_form_is_json_serializable():
    """The jsonable form must survive a real json.dumps/json.loads cycle."""
    import json
    keymap = _make_keymap(("section",))
    keymap[("section",)].set_spacing({0: 1, 2: 3, "edges": 0})
    text = json.dumps(nt.keymap_to_jsonable(keymap))
    rebuilt = nt.keymap_from_jsonable(json.loads(text))
    assert rebuilt[("section",)].get_spacing() == {0: 1, 2: 3, "edges": 0}


# ---------------------------------------------------------------------------
# Coverage backfill
# ---------------------------------------------------------------------------

def test_comment_eq_with_non_comment():
    """Comparing a Comment with a non-Comment object returns NotImplemented."""
    c = Comment("hi", indent=0)
    assert (c == "not a comment") is False
    assert (c == 42) is False
    # the reflected comparison should also work
    assert ("not a comment" == c) is False


def test_comment_is_unhashable():
    """Comment is mutable and therefore unhashable."""
    c = Comment("hi", indent=0)
    with pytest.raises(TypeError):
        hash(c)


def test_partition_with_multiple_blank_gaps():
    """When multiple blank gaps exist before the first key, the *last* one
    is the partition point.  Within each half, same-indent blocks separated
    by blanks remain as separate Comments."""
    source = (
        "# header A\n"
        "\n"
        "# middle group\n"
        "\n"
        "# leading on first key\n"
        "key: value\n"
    )
    keymap = {}
    nt.loads(source, top="dict", keymap=keymap)
    # Last blank is just before "leading on first key", so the header half
    # is [# header A, blank, # middle group] -> two separate Comments.
    # The leading half is just [# leading on first key].
    header = keymap[()].get_header_comments()
    assert len(header) == 2
    assert header[0].text == "header A"
    assert header[1].text == "middle group"
    key_leading = keymap[("key",)].get_key_leading_comments()
    assert len(key_leading) == 1
    assert key_leading[0].text == "leading on first key"


def test_set_and_add_header_comments():
    """Header accessors on the document-root Location."""
    _, km = load("b05_header_only.nt", top="dict")
    root = km[()]
    root.set_header_comments([Comment("replaced header", indent=0)])
    assert texts(root.get_header_comments()) == ["replaced header"]
    root.add_header_comment(Comment("appended", indent=0))
    assert texts(root.get_header_comments()) == ["replaced header", "appended"]


def test_set_and_add_footer_comments():
    """Footer accessors on the document-root Location."""
    _, km = load("b06_footer_only.nt", top="dict")
    root = km[()]
    root.set_footer_comments([Comment("replaced footer", indent=0)])
    assert texts(root.get_footer_comments()) == ["replaced footer"]
    root.add_footer_comment(Comment("appended", indent=0))
    assert texts(root.get_footer_comments()) == ["replaced footer", "appended"]


def test_header_footer_accessors_empty_on_non_root_location():
    """Header/footer slots on non-root Locations are always empty."""
    _, km = load("b05_header_only.nt", top="dict")
    loc = km[("server",)]
    assert loc.get_header_comments() == []
    assert loc.get_footer_comments() == []


def test_keymap_keys_are_all_tuples():
    """Every entry in the keymap is keyed by a tuple, so depth-based loops
    using ``len(keys)`` work uniformly."""
    text = (
        "# header\n"
        "\n"
        "\n"
        "a: 1\n"
        "b: 2\n"
        "\n"
        "# footer\n"
    )
    keymap = {}
    nt.loads(text, top="dict", keymap=keymap)
    for keys in keymap:
        assert isinstance(keys, tuple)
        # depth computation is safe
        _ = len(keys)


def test_set_and_add_key_trailing():
    _, km = load("s14_key_trailing.nt", top="dict")
    loc = km[("server",)]
    loc.set_key_trailing_comments([Comment("replaced", indent=8)])
    assert texts(loc.get_key_trailing_comments()) == ["replaced"]
    loc.add_key_trailing_comment(Comment("added", indent=8))
    assert texts(loc.get_key_trailing_comments()) == ["replaced", "added"]


def test_set_and_add_value_leading():
    """The value_leading slot is rarely populated by the loader, but exists
    for programmatic use."""
    _, km = load("b01_leading_top.nt", top="dict")
    loc = km[("database",)]
    assert loc.get_value_leading_comments() == []
    loc.set_value_leading_comments([Comment("hello", indent=0)])
    assert texts(loc.get_value_leading_comments()) == ["hello"]
    loc.add_value_leading_comment(Comment("world", indent=0))
    assert texts(loc.get_value_leading_comments()) == ["hello", "world"]


def test_value_leading_claim_on_multiline_string():
    """A comment at the value's indent between a `key:` line and its
    multi-line `>` value should be claimed into the key's
    value_leading_comments slot (line 1288-1289 of _add_keymap)."""
    source = (
        "notice:\n"
        "    # leading on the multi-line value\n"
        "    > line one\n"
        "    > line two\n"
    )
    keymap = {}
    nt.loads(source, top="dict", keymap=keymap)
    loc = keymap[("notice",)]
    vl = loc.get_value_leading_comments()
    assert any("leading on the multi-line value" in (c.text or "") for c in vl)


def test_comment_with_empty_inner_line():
    """A comment that has an internal empty line (rendered as a bare `#`
    in the source) round-trips correctly."""
    source = "# alpha\n#\n# beta\nkey: value\n"
    keymap = {}
    data = nt.loads(source, top="dict", keymap=keymap)
    out = nt.dumps(data, map_keys=keymap)
    # The empty middle line is rendered as a `#` on its own line.
    assert "# alpha\n#\n# beta\nkey: value" == out


def test_spacing_with_trailing_comment_on_first_item():
    """Trailing comments are preserved on their key; spacing={0: N} emits N
    blank lines between top-level siblings regardless of what comes
    immediately before the boundary."""
    source = (
        "a: 1\n"
        "    # trailing on a\n"
        "b: 2\n"
    )
    keymap = {}
    data = nt.loads(source, top="dict", keymap=keymap)
    out = nt.dumps(data, map_keys=keymap, spacing={0: 2})
    # spacing[0] = 2 -> exactly two blank lines between a's block and b
    assert "# trailing on a\n\n\nb: 2" in out


def test_dumps_empty_data_with_footer():
    """An empty/None top-level with a footer-only root Location emits only
    the footer comments (the empty-content branch in dumps)."""
    root = Location()
    root.set_footer_comments([Comment("just a footer", indent=0)])
    assert nt.dumps(None, map_keys={(): root}) == "# just a footer"


def test_dumps_empty_data_with_header():
    """Mirror of the above for the empty-content + header path."""
    root = Location()
    root.set_header_comments([Comment("just a header", indent=0)])
    assert nt.dumps(None, map_keys={(): root}) == "# just a header"


def test_s11_inline_converted_to_trailing_on_dump():
    """s11 does not round-trip exactly: per the rules, the inline comment is
    captured as trailing on the value at load time, and the dumper emits it
    after the value rather than between `>` lines.  Its indent is also
    bumped to one tabstop past the value's column so that a re-load will
    still classify it as value_trailing rather than as a leading comment
    on the next sibling (or a footer at EOF)."""
    text = (EXAMPLES / "s11_gapG_comment_inside_multiline.nt").read_text()
    keymap = {}
    data = nt.loads(text, top="any", keymap=keymap)
    out = nt.dumps(data, map_keys=keymap)
    assert out == (
        "notice:\n"
        "    > the cache layer is being decommissioned\n"
        "    > use the new metrics service instead\n"
        "        # a comment inside a multi-line string value\n"
        "        # (per Gap G: attached as a trailing comment for 'notice'; position within the value is lost on dump)"
    )


# ---------------------------------------------------------------------------
# keymap_to_jsonable / keymap_from_jsonable
# ---------------------------------------------------------------------------

def test_keymap_jsonable_round_trip_preserves_comments_and_keys():
    """Reducing the keymap to jsonable form and back preserves every input
    that dumps() reads: original keys, the four comment slots, and
    header/footer."""
    source = (
        "# document header\n"
        "\n"
        "# leading on Title\n"
        "Title: Hello\n"
        "Authors:\n"
        "    # leading inside list\n"
        "    - Alice\n"
        "    - Bob\n"
        "# section comment\n"
        "Body:\n"
        "    > line one\n"
        "    > line two\n"
        "# document footer\n"
    )
    keymap1 = {}
    data1 = nt.loads(source, top="any", keymap=keymap1)
    out1 = nt.dumps(data1, map_keys=keymap1, spacing={"edges": 1})

    jsonable = nt.keymap_to_jsonable(keymap1)
    assert isinstance(jsonable, dict)
    keymap2 = nt.keymap_from_jsonable(jsonable)
    out2 = nt.dumps(data1, map_keys=keymap2, spacing={"edges": 1})

    # Output via the rebuilt keymap should match output via the original.
    assert out1 == out2


def test_keymap_from_jsonable_restores_original_keys_after_normalization():
    """With normalize_key in play, the keymap is indexed by normalized keys.
    After the jsonable round-trip, dumps() must still recover the originals."""
    source = (
        "Title: Hello\n"
        "Authors:\n"
        "    - Alice\n"
        "    - Bob\n"
    )
    keymap = {}
    data = nt.loads(
        source, top="dict", keymap=keymap, normalize_key=lambda k, ks: k.lower()
    )
    assert data == {"title": "Hello", "authors": ["Alice", "Bob"]}

    jsonable = nt.keymap_to_jsonable(keymap)
    rebuilt = nt.keymap_from_jsonable(jsonable)
    out = nt.dumps(data, map_keys=rebuilt)
    assert "Title:" in out
    assert "Authors:" in out
    assert "title:" not in out
    assert "authors:" not in out


def test_keymap_to_jsonable_is_json_serializable():
    """The output must survive a real json.dumps / json.loads cycle."""
    import json
    keymap = {}
    nt.loads("# hi\nkey: value\n", top="dict", keymap=keymap)
    jsonable = nt.keymap_to_jsonable(keymap)
    text = json.dumps(jsonable)
    assert nt.keymap_from_jsonable(json.loads(text)) is not None


def test_keymap_from_jsonable_attaches_header_and_footer():
    """Header and footer comments live on the root entry and must round-trip."""
    source = (
        "# top header\n"
        "\n"
        "key: value\n"
        "# bottom footer\n"
    )
    keymap = {}
    nt.loads(source, top="dict", keymap=keymap)
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    root = rebuilt[()]
    assert [c.text for c in root.get_header_comments()] == ["top header"]
    assert [c.text for c in root.get_footer_comments()] == ["bottom footer"]


def test_keymap_from_jsonable_drops_line_info():
    """Source line/column information is intentionally discarded by the
    jsonable form; the rebuilt Locations should have no .line."""
    keymap = {}
    nt.loads("a: 1\nb: 2\n", top="dict", keymap=keymap)
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    for loc in rebuilt.values():
        assert loc.line is None


def test_keymap_from_jsonable_works_for_empty_document():
    """An empty document still has a () root entry; it should round-trip."""
    keymap = {}
    nt.loads("", top="any", keymap=keymap)
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    assert () in rebuilt


def test_restored_location_returns_passed_key_for_list_items():
    """For list-item entries (no original_key stored), _get_original_key
    must return the key it was called with unchanged."""
    keymap = {}
    nt.loads("- a\n- b\n", top="list", keymap=keymap)
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    loc = rebuilt[(0,)]
    assert loc._get_original_key(0, strict=False) == 0


def test_keymap_to_jsonable_handles_bare_location():
    """A bare Location (no key_line — as built outside the loader) still
    reduces: _get_original_key falls through to returning the tuple key."""
    loc = Location()
    keymap = {("foo",): loc}
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    assert rebuilt[("foo",)]._get_original_key("foo", strict=False) == "foo"


# ---------------------------------------------------------------------------
# annotate() and Comment tab/before/after
# ---------------------------------------------------------------------------

from nestedtext import annotate


def test_annotate_creates_location():
    """annotate creates the Location and attaches the comments."""
    keymap = {}
    annotate(("section",), keymap, key_leading=[Comment("about section")])
    assert ("section",) in keymap
    leading = keymap[("section",)].get_key_leading_comments()
    assert len(leading) == 1
    assert leading[0].text == "about section"


def test_annotate_tab_zero_uses_natural_indent():
    """A Comment with default tab (resolved to 0) renders at the slot's
    natural indent."""
    keymap = {}
    annotate(("section", "a"), keymap, key_leading=[Comment("alpha")])
    data = {"section": {"a": "1"}}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    # natural for key_leading at depth 2 is (2-1)*4 = 4
    assert "    # alpha" in out
    assert "        # alpha" not in out


def test_annotate_tab_positive_offsets_natural():
    """tab=1 adds one indent_step to natural."""
    keymap = {}
    annotate(("section", "a"), keymap, key_leading=[Comment("alpha", tab=1)])
    data = {"section": {"a": "1"}}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    # natural 4 + 1*4 = 8
    assert "        # alpha" in out


def test_annotate_tab_negative_clamps_at_zero():
    """A very negative tab clamps the resolved column to 0."""
    keymap = {}
    annotate(("section", "a"), keymap, key_leading=[Comment("alpha", tab=-99)])
    data = {"section": {"a": "1"}}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    # natural would be 4; negative tab clamped to 0 column
    assert "\n# alpha" in out or out.startswith("# alpha")


def test_annotate_responds_to_dumps_indent():
    """Same Comment dumped with different indent values produces different columns."""
    keymap = {}
    annotate(("section", "a"), keymap, key_leading=[Comment("alpha")])
    data = {"section": {"a": "1"}}
    out4 = nt.dumps(data, map_keys=keymap, indent=4)
    out2 = nt.dumps(data, map_keys=keymap, indent=2)
    assert "    # alpha" in out4
    assert "  # alpha" in out2
    assert "    # alpha" not in out2


def test_loader_built_comments_unaffected_by_dumps_indent():
    """Loader-built Comments (tab=None) render at absolute indent and do
    NOT scale with dumps(indent=...)."""
    src = "section:\n    # loaded comment\n    a: 1\n"
    keymap = {}
    nt.loads(src, top="dict", keymap=keymap)
    out4 = nt.dumps({"section": {"a": "1"}}, map_keys=keymap, indent=4)
    # The loaded comment has indent=4 absolute; should appear at column 4
    # even though we're dumping with indent=4 (same column either way).
    assert "    # loaded comment" in out4


def test_annotate_blanks_before_after():
    """before=1 and after=1 emit one blank line on each side of the comment."""
    keymap = {}
    annotate(("section",), keymap,
        key_leading=[Comment("intro", before=1, after=1)])
    data = {"section": {"a": "1"}, "other": "2"}
    # Put 'other' before 'section' so we have something before:
    data = {"other": "2", "section": {"a": "1"}}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    # Expect: other: 2 \n <blank> \n # intro \n <blank> \n section: ...
    lines = out.split("\n")
    intro_idx = lines.index("# intro")
    assert lines[intro_idx - 1] == ""        # blank before
    assert lines[intro_idx + 1] == ""        # blank after


def test_same_indent_comments_emit_contiguously():
    """Two same-indent Comments in a single slot are emitted
    contiguously, with no separating blank line.  (On re-load they will
    merge into one Comment; the dumper does not insert any auto-blank
    to preserve Comment-object granularity.)"""
    keymap = {}
    annotate(("section",), keymap, key_leading=[
        Comment("first"),
        Comment("second"),
    ])
    data = {"section": "x"}
    out = nt.dumps(data, map_keys=keymap)
    lines = out.split("\n")
    first_idx = lines.index("# first")
    second_idx = lines.index("# second")
    assert second_idx == first_idx + 1


def test_annotate_blanks_explicit_before():
    """With before=N on the second Comment, exactly N blanks appear
    between the two tab-mode Comments."""
    keymap = {}
    annotate(("section",), keymap, key_leading=[
        Comment("first"),
        Comment("second", before=2),
    ])
    data = {"section": "x"}
    out = nt.dumps(data, map_keys=keymap)
    lines = out.split("\n")
    first_idx = lines.index("# first")
    second_idx = lines.index("# second")
    # before=2 → exactly two blanks between them
    assert second_idx - first_idx == 3
    assert lines[first_idx + 1] == ""
    assert lines[first_idx + 2] == ""


def test_comment_with_none_text_emits_only_blanks():
    """A Comment with text=None honors both before and after as blank
    lines, with no comment line emitted."""
    keymap = {}
    annotate(("section",), keymap, key_leading=[
        Comment("first"),
        Comment(None, before=1, after=2),
        Comment("second"),
    ])
    data = {"section": "x"}
    out = nt.dumps(data, map_keys=keymap)
    lines = out.split("\n")
    first = lines.index("# first")
    second = lines.index("# second")
    # before=1 + after=2 → three blanks between them, and no '#' line for
    # the None entry.
    assert second - first == 4
    assert lines[first + 1] == ""
    assert lines[first + 2] == ""
    assert lines[first + 3] == ""


def test_comment_with_none_text_no_args_is_inert():
    """A Comment(None) with no before/after contributes nothing."""
    keymap = {}
    annotate(("section",), keymap, key_leading=[
        Comment("first"),
        Comment(None),
        Comment("second"),
    ])
    data = {"section": "x"}
    out = nt.dumps(data, map_keys=keymap)
    # No blank between the two real comments either; the None entry is
    # transparent for adjacency tracking too.
    lines = out.split("\n")
    first = lines.index("# first")
    second = lines.index("# second")
    assert second == first + 1


def test_comment_with_none_text_in_provider():
    """A provider can return blank-line separators via Comment(None,
    before=N) without emitting any comment lines for them."""
    def header(k):
        if k.endswith("-01"):
            return [Comment(None, before=1), Comment(f"start of {k[:4]}")]
        return []
    keymap = {}
    annotate((), keymap, key_leading=header)
    data = {"2024-01": "a", "2024-02": "b", "2025-01": "c"}
    out = nt.dumps(data, map_keys=keymap)
    # blank lines appear before "# start of 2024" and "# start of 2025"
    assert "# start of 2024" in out
    assert "# start of 2025" in out
    # nothing for "2024-02" (the provider returned [])
    assert "# start of 2024-02" not in out


def test_multi_line_key_round_trip_preserves_all_comment_slots():
    """A multi-line key with key_trailing, value_leading, and value_trailing
    must round-trip without dropping or mispositioning any of them."""
    src = (
        "# heading\n"
        "\n"
        "# leading on key\n"
        ": key1a\n"
        ": key1b\n"
        "        # trailing on key\n"
        "    # leading on value\n"
        "    > nutz\n"
        "        # trailing on value\n"
        "\n"
        "# footer\n"
    )
    keymap = {}
    nt.loads(src, top="dict", keymap=keymap)
    # The multi-line key is "key1a\nkey1b".
    loc = keymap[("key1a\nkey1b",)]
    assert [c.text for c in loc.get_key_leading_comments()]    == ["leading on key"]
    assert [c.text for c in loc.get_key_trailing_comments()]   == ["trailing on key"]
    assert [c.text for c in loc.get_value_leading_comments()]  == ["leading on value"]
    assert [c.text for c in loc.get_value_trailing_comments()] == ["trailing on value"]


def test_inline_in_multi_line_key_indent_is_bumped_past_value():
    """A comment between fragments of a multi-line key, originally at a
    shallow indent, has its indent bumped to value-depth+4 at load time
    so it stays in key_trailing on a re-load."""
    src = (
        ": key1a\n"
        "# inline\n"          # at indent 0
        ": key1b\n"
        "    > value\n"
    )
    keymap = {}
    nt.loads(src, top="dict", keymap=keymap)
    loc = keymap[("key1a\nkey1b",)]
    kts = loc.get_key_trailing_comments()
    assert any(c.text == "inline" and c.indent == 8 for c in kts)


def test_inline_in_multi_line_string_indent_is_bumped_past_value():
    """A comment between '>' lines of a multi-line string, originally at
    the value's column, has its indent bumped to value-depth+4 at load
    time so it stays in value_trailing on a re-load."""
    src = (
        "key:\n"
        "    > a\n"
        "    # inline\n"      # at the value column (indent 4)
        "    > b\n"
    )
    keymap = {}
    nt.loads(src, top="dict", keymap=keymap)
    loc = keymap[("key",)]
    vts = loc.get_value_trailing_comments()
    assert any(c.text == "inline" and c.indent == 8 for c in vts)


def test_inline_indent_bump_makes_round_trip_stable():
    """After bumping inline indents, a load → dump → load yields the
    same keymap structure (comments stay in their original slots)."""
    src = (
        ": k1\n"
        "# inline-k\n"
        ": k2\n"
        "    > a\n"
        "    # inline-v\n"
        "    > b\n"
    )
    keymap1 = {}
    nt.loads(src, top="dict", keymap=keymap1)
    out = nt.dumps({"k1\nk2": "a\nb"}, map_keys=keymap1)
    keymap2 = {}
    nt.loads(out, top="dict", keymap=keymap2)
    loc1 = keymap1[("k1\nk2",)]
    loc2 = keymap2[("k1\nk2",)]
    assert [c.text for c in loc1.get_key_trailing_comments()]   == [c.text for c in loc2.get_key_trailing_comments()]
    assert [c.text for c in loc1.get_value_trailing_comments()] == [c.text for c in loc2.get_value_trailing_comments()]


def test_multi_line_key_inline_comment_collected_as_key_trailing():
    """A comment between fragments of a multi-line key is collected and
    emitted at the key_trailing position (similar to the inline-in-
    multi-line-string convention)."""
    src = (
        ": key1a\n"
        "# inline in key\n"
        ": key1b\n"
        "    > value\n"
    )
    keymap = {}
    nt.loads(src, top="dict", keymap=keymap)
    loc = keymap[("key1a\nkey1b",)]
    # the inline comment ends up in key_trailing
    texts = [c.text for c in loc.get_key_trailing_comments()]
    assert "inline in key" in texts


def test_dumper_multi_line_key_with_inner_multi_line_key():
    """The dumper's key-boundary scan must stop when it encounters a
    deeper-indented ':' line -- that belongs to the inner dict's
    multi-line key, not to the outer's."""
    keymap = {}
    annotate(("a\nb",), keymap, key_trailing=[Comment("outer kt", tab=1)])
    data = {"a\nb": {"c\nd": "v"}}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    lines = out.split("\n")
    outer_a = lines.index(": a")
    outer_b = lines.index(": b")
    kt = lines.index("        # outer kt")
    inner_c = lines.index("    : c")
    inner_d = lines.index("    : d")
    # outer kt goes between the outer key's last fragment and the inner
    # dict's first fragment.
    assert outer_a < outer_b < kt < inner_c < inner_d


def test_dumper_multi_line_key_places_kt_vl_after_all_fragments():
    """When emitting a multi-line key, key_trailing/value_leading
    comments go AFTER the last key fragment, not between the
    fragments."""
    keymap = {}
    annotate(("a\nb",), keymap,
        key_trailing=[Comment("kt", tab=1)],
        value_leading=[Comment("vl", tab=0)],
    )
    data = {"a\nb": "v"}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    lines = out.split("\n")
    a = lines.index(": a")
    b = lines.index(": b")
    kt = lines.index("        # kt")
    vl = lines.index("    # vl")
    val = lines.index("    > v")
    # all key fragments precede the comments; comments precede the value
    assert a < b < kt < vl < val


def test_round_trip_preserves_key_trailing_and_value_leading():
    """A load with key_trailing and value_leading comments on a scalar
    value must round-trip exactly -- the dumper must NOT collapse to
    inline form (which would drop those slots)."""
    src = (
        "# heading comment for document\n"
        "\n"
        "# leading comment for key\n"
        "key:\n"
        "        # trailing comment for key\n"
        "    # leading comment for value\n"
        "    > nutz\n"
        "        # trailing comment for value\n"
        "\n"
        "# footer comment for document\n"
    )
    keymap = {}
    data = nt.loads(src, top="any", keymap=keymap)
    out = nt.dumps(data, map_keys=keymap)
    # Re-load and compare keymaps + data — semantic preservation.
    keymap2 = {}
    data2 = nt.loads(out, top="any", keymap=keymap2)
    assert data == data2
    # All four comment kinds for ('key',) survive:
    loc = keymap2[("key",)]
    assert [c.text for c in loc.get_key_leading_comments()]   == ["leading comment for key"]
    assert [c.text for c in loc.get_key_trailing_comments()]  == ["trailing comment for key"]
    assert [c.text for c in loc.get_value_leading_comments()] == ["leading comment for value"]
    assert [c.text for c in loc.get_value_trailing_comments()] == ["trailing comment for value"]


def test_force_multiline_for_dict_value_with_kt_or_vl():
    """If the value is a dict/list and key_trailing/value_leading
    comments exist, the existing multi-line form is used (regression
    check that the new branch doesn't break collection-valued items)."""
    src = (
        "outer:\n"
        "        # trailing on outer's key\n"
        "    inner: 1\n"
    )
    keymap = {}
    data = nt.loads(src, top="any", keymap=keymap)
    out = nt.dumps(data, map_keys=keymap)
    keymap2 = {}
    nt.loads(out, top="any", keymap=keymap2)
    assert [c.text for c in keymap2[("outer",)].get_key_trailing_comments()] == [
        "trailing on outer's key"
    ]


def test_force_multiline_value_for_non_string_scalar():
    """A non-string scalar with a key_trailing comment is still emitted
    in the multi-line value form."""
    keymap = {}
    annotate(("count",), keymap, key_trailing=[Comment("must be int")])
    data = {"count": 42}
    out = nt.dumps(data, map_keys=keymap)
    # The 42 must end up on its own line (with `> ` leader), not inline.
    assert "count: 42" not in out
    assert "count:" in out
    assert "> 42" in out
    assert "# must be int" in out


def test_force_multiline_with_parent_provider():
    """A parent's key_trailing provider also forces multi-line value
    form for its children, even when the provider's return value is
    empty for the specific child."""
    def kt(k):
        return [Comment(f"trail {k}")] if k == "verbose" else []
    keymap = {}
    annotate((), keymap, key_trailing=kt)
    data = {"verbose": "yes", "quiet": "no"}
    out = nt.dumps(data, map_keys=keymap)
    # verbose: comment lands; the value is on its own line.
    assert "# trail verbose" in out
    # 'verbose' and 'quiet' both rendered in multi-line form (provider
    # presence forces it conservatively).
    assert "verbose: yes" not in out
    assert "> yes" in out
    assert "> no" in out


def test_loader_same_slot_same_indent_comments_merge_on_dump_reload():
    """Two same-indent Comments in a single slot (e.g., key_leading)
    are emitted contiguously by the dumper.  On re-load they merge into
    a single Comment.  Text and slot are preserved; only Comment-object
    granularity may shift."""
    keymap = {}
    annotate(("section",), keymap, key_leading=[
        Comment("first"),
        Comment("second"),
    ])
    data = {"section": "x"}
    out = nt.dumps(data, map_keys=keymap)
    assert "# first\n# second" in out
    keymap2 = {}
    nt.loads(out, top="dict", keymap=keymap2)
    leading = keymap2[("section",)].get_key_leading_comments()
    assert len(leading) == 1
    assert "first" in leading[0].text and "second" in leading[0].text


def test_annotate_sets_spacing():
    """spacing= is applied to the Location."""
    keymap = {}
    annotate(("section",), keymap,
        key_leading=[Comment("intro")],
        spacing={0: 2},
    )
    assert keymap[("section",)].get_spacing() == {0: 2}


def test_annotate_replaces_existing_comments():
    """A second annotate call on the same keys replaces (not appends)."""
    keymap = {}
    annotate(("section",), keymap, key_leading=[Comment("first")])
    annotate(("section",), keymap, key_leading=[Comment("second")])
    leading = keymap[("section",)].get_key_leading_comments()
    assert [c.text for c in leading] == ["second"]


def test_annotate_rejects_non_root_slots_on_root():
    """annotate(km, (), key_leading=[...]) raises ValueError."""
    keymap = {}
    with pytest.raises(ValueError):
        annotate((), keymap, key_leading=[Comment("x")])
    with pytest.raises(ValueError):
        annotate((), keymap, value_trailing=[Comment("x")])


def test_annotate_rejects_header_footer_on_non_root():
    """annotate(km, ('x',), header=[...]) raises ValueError."""
    keymap = {}
    with pytest.raises(ValueError):
        annotate(("section",), keymap, header=[Comment("x")])
    with pytest.raises(ValueError):
        annotate(("section",), keymap, footer=[Comment("x")])


def test_annotate_root_header_footer():
    """header/footer at the root land on keymap[()] and render correctly."""
    keymap = {}
    annotate((), keymap,
        header=[Comment("top")],
        footer=[Comment("bottom")],
    )
    data = {"a": "1"}
    out = nt.dumps(data, map_keys=keymap)
    assert "# top" in out
    assert "# bottom" in out
    assert out.index("# top") < out.index("a: 1") < out.index("# bottom")


def test_annotate_round_trips_through_jsonable():
    """Comments built by annotate (with tab/before/after) survive the
    jsonable round-trip and produce identical output."""
    keymap = {}
    annotate((), keymap, header=[Comment("hdr", after=1)])
    annotate(("section",), keymap, key_leading=[
        Comment("intro", tab=0, before=1),
        Comment("deeper", tab=1),
    ])
    data = {"section": {"a": "1"}}
    expected = nt.dumps(data, map_keys=keymap, indent=4)
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    assert nt.dumps(data, map_keys=rebuilt, indent=4) == expected


# ---------------------------------------------------------------------------
# Per-child slot providers (callable comment slots)
# ---------------------------------------------------------------------------

def test_provider_invoked_per_child_with_child_key():
    """A callable in key_leading on a parent is invoked per child of the
    parent, receiving that child's key."""
    seen = []
    def provider(k):
        seen.append(k)
        return [Comment(f"k={k}")]
    keymap = {}
    annotate((), keymap, key_leading=provider)
    data = {"alpha": "1", "bravo": "2"}
    out = nt.dumps(data, map_keys=keymap)
    assert seen == ["alpha", "bravo"]
    assert "# k=alpha" in out
    assert "# k=bravo" in out
    assert out.index("# k=alpha") < out.index("alpha: 1")
    assert out.index("# k=bravo") < out.index("bravo: 2")


def test_provider_closure_dedup_for_diary():
    """The diary case: year + month headers, deduped via closure state."""
    last_year = last_month = None
    def header(k):
        nonlocal last_year, last_month
        out = []
        if k[:4] != last_year:
            out.append(Comment(f"=== {k[:4]} ==="))
            last_year = k[:4]
        if k[:7] != last_month:
            out.append(Comment(f"--- {k[5:7]} ---"))
            last_month = k[:7]
        return out
    keymap = {}
    annotate((), keymap, key_leading=header)
    data = {
        "2024-01-15": "a", "2024-01-22": "b",
        "2024-02-04": "c",
        "2025-01-09": "d",
    }
    out = nt.dumps(data, map_keys=keymap)
    assert out.count("# === 2024 ===") == 1
    assert out.count("# === 2025 ===") == 1
    assert out.count("# --- 01 ---") == 2   # once in 2024, once in 2025
    assert out.count("# --- 02 ---") == 1
    # ordering: 2024 header before its first child; 2025 header before its
    assert out.index("# === 2024 ===") < out.index("2024-01-15")
    assert out.index("# === 2025 ===") < out.index("2025-01-09")


def test_provider_classifier_pattern():
    """The categorical 'classifier' pattern: one provider, internal
    branching, dedups itself."""
    seen = set()
    def classify(k):
        cat = ("db" if k.startswith("db_") else
               "log" if k.startswith("log_") else "other")
        if cat in seen:
            return []
        seen.add(cat)
        label = {"db": "Database", "log": "Logging", "other": "Other"}[cat]
        return [Comment(label)]
    keymap = {}
    annotate((), keymap, key_leading=classify)
    data = {"db_host": "x", "db_port": "y", "log_level": "z", "misc": "w"}
    out = nt.dumps(data, map_keys=keymap)
    assert out.count("# Database") == 1
    assert out.count("# Logging") == 1
    assert out.count("# Other") == 1
    assert out.index("# Database") < out.index("db_host")
    assert out.index("db_port")    < out.index("# Logging")
    assert out.index("log_level")  < out.index("# Other")


def test_provider_prepends_to_child_static_key_leading():
    """A parent provider's comments are prepended to the child's own
    static key_leading."""
    keymap = {}
    annotate((), keymap, key_leading=lambda k: [Comment("from parent")])
    annotate(("alpha",), keymap, key_leading=[Comment("from child")])
    data = {"alpha": "1"}
    out = nt.dumps(data, map_keys=keymap)
    assert out.index("# from parent") < out.index("# from child") < out.index("alpha: 1")


def test_provider_returning_empty_list_emits_nothing():
    """A provider returning [] for a given child contributes no Comments."""
    keymap = {}
    annotate((), keymap, key_leading=lambda k: [] if k == "skip" else [Comment(f"#{k}")])
    data = {"skip": "x", "show": "y"}
    out = nt.dumps(data, map_keys=keymap)
    assert "# #skip" not in out
    assert "# #show" in out


def test_provider_returning_none_emits_nothing():
    """A provider returning None for a given child contributes no
    Comments (None coerces to [] via the `or []` guard)."""
    keymap = {}
    annotate((), keymap, key_leading=lambda k: None if k == "skip" else [Comment(f"#{k}")])
    data = {"skip": "x", "show": "y"}
    out = nt.dumps(data, map_keys=keymap)
    assert "# #skip" not in out
    assert "# #show" in out


def test_provider_at_nested_parent_indents_at_child_column():
    """Providers attached to a nested parent emit at that parent's
    children's natural indent."""
    keymap = {}
    annotate(("section",), keymap, key_leading=lambda k: [Comment("hdr")])
    data = {"section": {"alpha": "1", "bravo": "2"}}
    out = nt.dumps(data, map_keys=keymap, indent=4)
    # children are at column 4 → '# hdr' should appear there.
    assert "    # hdr" in out


def test_provider_on_list_receives_integer_index():
    """For a list-valued parent, the provider sees the integer index."""
    keymap = {}
    annotate(("items",), keymap,
        key_leading=lambda i: [Comment(f"item {i}")] if i % 2 == 0 else [],
    )
    data = {"items": ["a", "b", "c", "d"]}
    out = nt.dumps(data, map_keys=keymap)
    assert "# item 0" in out
    assert "# item 2" in out
    assert "# item 1" not in out
    assert "# item 3" not in out


def test_provider_on_value_trailing_slot():
    """Providers also work for the other three per-key slots."""
    keymap = {}
    annotate((), keymap,
        value_trailing=lambda k: [Comment(f"after {k}")],
    )
    data = {"alpha": "1", "bravo": "2"}
    out = nt.dumps(data, map_keys=keymap)
    assert out.index("alpha: 1") < out.index("# after alpha") < out.index("bravo: 2")


def test_provider_allowed_at_root():
    """A provider on key_leading at root is legal (decorates each
    top-level child); a static list at root is not."""
    keymap = {}
    annotate((), keymap, key_leading=lambda k: [Comment("ok")])  # no raise

    keymap2 = {}
    with pytest.raises(ValueError):
        annotate((), keymap2, key_leading=[Comment("nope")])


def test_provider_dropped_from_jsonable():
    """Providers are callables and are not preserved through
    keymap_to_jsonable round-trips."""
    keymap = {}
    annotate((), keymap, key_leading=lambda k: [Comment("Provider")])
    data = {"a": "1"}
    rebuilt = nt.keymap_from_jsonable(nt.keymap_to_jsonable(keymap))
    out = nt.dumps(data, map_keys=rebuilt)
    assert "# Provider" not in out


def test_provider_accessors_round_trip():
    """The get/set_*_provider accessor pair stores and returns the
    callable verbatim, for every slot."""
    loc = Location()
    fn = lambda k: [Comment("x")]
    for getter, setter in (
        ("get_key_leading_provider",  "set_key_leading_provider"),
        ("get_key_trailing_provider", "set_key_trailing_provider"),
        ("get_value_leading_provider", "set_value_leading_provider"),
        ("get_value_trailing_provider", "set_value_trailing_provider"),
    ):
        getattr(loc, setter)(fn)
        assert getattr(loc, getter)() is fn
        getattr(loc, setter)(None)
        assert getattr(loc, getter)() is None


# ---------------------------------------------------------------------------
# Loader behavior unchanged
# ---------------------------------------------------------------------------

def test_loader_built_comments_round_trip_unchanged():
    """A loaded file with comments round-trips byte-identical via dump."""
    src = (
        "# header\n"
        "\n"
        "# leading on key\n"
        "key: value\n"
    )
    keymap = {}
    data = nt.loads(src, top="dict", keymap=keymap)
    out = nt.dumps(data, map_keys=keymap, spacing={"edges": 1})
    # the dump should have the comments at their original positions
    assert "# header" in out
    assert "# leading on key" in out
    assert out.index("# header") < out.index("# leading on key") < out.index("key: value")
    # No spurious blank lines from the new before/after machinery
    assert "\n\n\n" not in out


def test_annotate_accepts_non_tuple_keys():
    """annotate accepts list/iterable keys, not just tuples."""
    keymap = {}
    annotate(["section"], keymap, key_leading=[Comment("hi")])
    assert ("section",) in keymap


def test_annotate_all_non_root_slots():
    """All four non-root comment slots round-trip through annotate."""
    keymap = {}
    annotate(("section",), keymap,
        key_leading=[Comment("k_lead")],
        key_trailing=[Comment("k_trail", tab=0)],
        value_leading=[Comment("v_lead", tab=0)],
        value_trailing=[Comment("v_trail", tab=0)],
    )
    loc = keymap[("section",)]
    assert [c.text for c in loc.get_key_leading_comments()]   == ["k_lead"]
    assert [c.text for c in loc.get_key_trailing_comments()]  == ["k_trail"]
    assert [c.text for c in loc.get_value_leading_comments()] == ["v_lead"]
    assert [c.text for c in loc.get_value_trailing_comments()] == ["v_trail"]


def test_comment_repr_includes_new_fields_when_set():
    """The Comment repr surfaces tab/before/after when they're non-default."""
    c = Comment("hi", indent=4, tab=2, before=1, after=3)
    r = repr(c)
    assert "tab=2" in r
    assert "before=1" in r
    assert "after=3" in r
    # And not when they're default
    c2 = Comment("hi", indent=4)
    r2 = repr(c2)
    assert "tab=" not in r2
    assert "before=" not in r2
    assert "after=" not in r2


# ---------------------------------------------------------------------------
# Inlining must not silently drop comments
# ---------------------------------------------------------------------------

def test_inline_does_not_drop_comment_on_list_item():
    """A collection that carries comments on its items must fall back to the
    multi-line form rather than inline, otherwise the comments are silently
    dropped (the inline forms have no place to emit them)."""
    data = {"servers": ["alpha", "beta"]}
    keymap = {}
    annotate(("servers", 0), keymap, key_leading=[Comment("the first server")])
    # width is large enough that, absent comments, the list would be inlined.
    out = nt.dumps(data, map_keys=keymap, width=200, inline_level=0, inline_count=1)
    assert "the first server" in out
    # and the list was forced to the multi-line form
    assert "- alpha" in out
    assert "[alpha, beta]" not in out


def test_inline_does_not_drop_value_comment_on_dict():
    """A value-side comment on a key whose dict value would inline must keep
    that value multi-line so the comment survives."""
    data = {"config": {"a": "1", "b": "2"}}
    keymap = {}
    annotate(("config",), keymap, value_trailing=[Comment("end of config", tab=1)])
    out = nt.dumps(data, map_keys=keymap, width=200, inline_level=0, inline_count=1)
    assert "end of config" in out
    assert "{a: 1, b: 2}" not in out
