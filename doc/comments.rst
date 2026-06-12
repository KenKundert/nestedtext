.. currentmodule:: nestedtext

********
Comments
********

*NestedText* preserves comments through a load/dump cycle: the loader captures
hand-written comments and attaches each one to a nearby data item.  The loader 
outputs this metadata as a keymap.  The dumper, when given the same keymap, 
re-emits each comment in its place.  An API also exists for attaching comments 
to a keymap from scratch, without any source file at all.

A keymap is a ``dict`` keyed by tuples of keys.  Each value is a
:class:`Location` whose accessor methods give read/write access to the
comments associated with that key.  Document-level header and footer comments
live on the root Location at ``keymap[()]``.

Vertical (blank-line) layout is *not* preserved across a round trip.  Use the
dumper's *spacing* argument to specify the desired layout on output; this
avoids stale blank lines lingering after a data structure is reorganised.

The remainder of this section is organised as follows:

* `Comment Recognition Rules`_ — how the loader identifies comments,
  groups them, and decides which data item each one belongs to.
* `Accessing Comments`_ — how to read comments back from the keymap
  returned by :func:`load` or :func:`loads`.
* `Inserting Comments`_ — how to attach comments to a keymap of your own,
  whether by mutating an existing keymap or by building one from scratch
  with :func:`annotate`.
* `Round-Tripping`_ — putting the two halves together: loading, modifying,
  and dumping while preserving comments and layout.


Comment Recognition Rules
=========================

These rules describe how comments in a *NestedText* file are captured during
load.

Types of Comments
-----------------

There are 5 types of comments:

- *header* comments — found at the very top of the file, before any data.
- *leading* comments — found before a data item, refer to that item.
- *trailing* comments — found after a data item, refer to that item.
- *inline* comments — found within multiline strings.
- *footer* comments — found at the very end of the file, after all data.


Comment Grouping
----------------

Adjacent comment lines at the same level of indentation (no blank line
between them) merge into one :class:`Comment` object whose ``text`` is the
source lines joined by newlines.  A blank line or an indent change closes
the current Comment and starts a new one.

Consider the following example::

    # alpha1
    # alpha2

    # beta
        # gamma
        key: value

There are three Comments leading on ``key``::

    {
      ("key",): Location(
        key_leading_comments = [
          Comment("alpha1\nalpha2", indent=0),
          Comment("beta", indent=0),
          Comment("gamma", indent=4),
        ],
        ...
      )
    }

``alpha1`` and ``alpha2`` are adjacent at indent 0 and merge into one
Comment.  The blank line splits that block from ``beta``, which becomes a
separate Comment at the same indent.  ``gamma`` is at a different indent
and forms its own Comment.

A file with no comments yields a keymap with no comment entries; pure
blank-line layout in the source is not captured anywhere.

When the dumper emits multiple Comments that share the same indent in a
single slot, it writes one blank line between them so that the boundary
survives a re-load (where adjacent same-indent comment lines would
otherwise merge).


Comment Association
-------------------

Header and footer comments associate with the document as a whole.  They
live on the document-root Location at ``keymap[()]``.

Leading and trailing comments associate with a particular data item:

- Leading comments associate with the data item that follows them.
- Trailing comments associate with the data item that precedes them.
- Inline comments associate with the data item that they are found within.
  They can only be found within multiline strings.


Disambiguation Rules
--------------------

Header / leading comments
~~~~~~~~~~~~~~~~~~~~~~~~~

All comments that occur before the first data item are partitioned into
two groups: the first becomes the header, the second becomes the leading
comment for the first data item.  The partition is at the *last blank
line* in the buffer.  If there is no blank line, the entire content is
leading on the first data item (no header).

Comments in a document that contains no data are all header comments.

Leading / trailing comments
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Comments that occur between two data items are partitioned into two groups
based on indentation.  If the indentation is less than or equal to the
indentation of the next data item (key or value) then the comment is a
leading comment for that item.  If the indentation is greater than the
indentation of the next data item, then the comment is a trailing comment
for the previous data item (key or value).

This rule also disambiguates comments that sit between a key and its value
when the value occupies its own line (a multiline value, or a list/dict
child).  The same indentation comparison applies::

    key:
        # this is a leading comment for the value
        > value

::

    key:
            # this is a trailing comment for the key
        > value

In the first case the comment's indent equals the value's indent, so it is
a leading comment for the value.  In the second case the comment's indent
is greater than the value's indent, so it is a trailing comment for the
key.

Key / value comments
~~~~~~~~~~~~~~~~~~~~

If a key and value are found on the same line, then leading comments
associate with the key and trailing comments associate with the value.

Trailing / footer comments
~~~~~~~~~~~~~~~~~~~~~~~~~~

There is no ambiguity here -- trailing and footer comments are distinguished
by their indentation level.  If the indentation is greater than the
indentation of both the previous and next data items, then the comment is 
a trailing comment for the previous item.  If the indentation is less than or 
equal to the indentation of the last data item, then the comment is a footer 
comment for the document as a whole.

No data
~~~~~~~

If there is no data in the file, then all comments are header comments.


Transformation Rules
--------------------

Inline comments are converted to trailing comments immediately upon load,
so the keymap exposes only header, leading, trailing, and footer comments.
The *inline* name is a convenience for describing where the comments are
found in the source; it is not a distinct stored type.


Comment Order
-------------

Comments are reconstituted in the same order as they were encountered
relative to the data item they are attached to.

During round-trip processing the order of the data items may be changed,
but comments maintain their attachment to their data item and are emitted
in the same order relative to that item as they appeared in the input.


Accessing Comments
==================

When a *keymap* is passed to :func:`load` or :func:`loads`, the loader
populates it with one :class:`Location` per data item; that Location holds
the comments attributed to the item by the rules above.

Each Location exposes six comment slots, each with ``get_``, ``set_``, and
``add_`` accessors:

- ``key_leading`` — Comments before the item's key line.
- ``key_trailing`` — Comments between the key line and the value's first
  line (multiline value form only).
- ``value_leading`` — Comments between the key line and the value's first
  line, after any ``key_trailing`` (multiline value form only).
- ``value_trailing`` — Comments after the item's last line.
- ``header`` and ``footer`` — document-level; only on ``keymap[()]``.

For example:

.. code-block:: python

    >>> import nestedtext as nt

    >>> source = """
    ... # production deployment
    ...
    ... # database server
    ... database: production
    ... """

    >>> keymap = {}
    >>> data = nt.loads(source, top='dict', keymap=keymap)

    >>> [c.text for c in keymap[()].get_header_comments()]
    ['production deployment']

    >>> [c.text for c in keymap[('database',)].get_key_leading_comments()]
    ['database server']

Every key in the keymap is a tuple, so depth-based iteration using
``len(keys)`` remains safe.  Walk the keymap to inspect every comment in
the document:

.. code-block:: python

    >>> for keys, loc in keymap.items():
    ...     for c in loc.get_key_leading_comments():
    ...         print(keys, c.text)
    ('database',) database server


Inserting Comments
==================

There are two ways to attach comments to a keymap: by mutating an existing
keymap (typically one returned from :func:`load`) or by building one from
scratch.

To mutate, call ``set_`` or ``add_`` on the Location at the key you want to
annotate.  Computing the right absolute indent for each Comment can be
tedious, particularly when keys are nested.  The :func:`annotate` function
streamlines the from-scratch case: create or update a Location in a single
call, and specify each comment's indent in *tabstops* relative to the
slot's natural indent rather than in absolute spaces.

.. code-block:: python

    >>> from nestedtext import Comment, annotate

    >>> keymap = {}
    >>> _ = annotate(
    ...     keymap, (),
    ...     header=[Comment('application config')],
    ... )
    >>> _ = annotate(
    ...     keymap, ('database',),
    ...     key_leading=[Comment('database server')],
    ... )

    >>> data = {'database': 'production'}
    >>> print(nt.dumps(data, map_keys=keymap))
    # application config
    <BLANKLINE>
    # database server
    database: production

The *tab* field on :class:`Comment` is a tabstop offset relative to the
slot's natural indent; default 0 (when *tab* is left as ``None`` the
loader-side absolute *indent* is used instead, so loader-built Comments are
unaffected).  The dumper resolves *tab* at emit time using
``dumps(indent=...)``, so the same comment renders correctly at any chosen
indent step.  The *before* and *after* fields give per-comment blank-line
counts.

For grouped output, pass *sections* to :func:`annotate` on a parent
Location: a list of ``(predicate, [Comment, ...])`` pairs.  When the
dumper renders the parent's children, it emits each section's comments
before the first child whose key matches the section's predicate.  This is
useful when the section's members are determined dynamically.

.. code-block:: python

    >>> keymap = {}
    >>> _ = annotate(keymap, (),
    ...     sections=[
    ...         (lambda k: k.startswith("db_"),  [Comment("Database")]),
    ...         (lambda k: k.startswith("log_"), [Comment("Logging")]),
    ...     ],
    ... )

    >>> data = {'db_host': 'localhost', 'db_port': '5432', 'log_level': 'info'}
    >>> print(nt.dumps(data, map_keys=keymap))
    # Database
    db_host: localhost
    db_port: 5432
    # Logging
    log_level: info

First-match wins among a parent's sections, so a trailing
``lambda k: True`` is a clean catch-all.


Round-Tripping
==============

The load → modify → dump cycle uses the same keymap on both sides:

.. code-block:: python

    >>> source = """
    ... # production deployment
    ...
    ... # database server
    ... database: production
    ...
    ... # how long the worker waits between retries
    ... retry_delay: 5
    ... """

    >>> keymap = {}
    >>> data = nt.loads(source, top='dict', keymap=keymap)
    >>> data['retry_delay'] = '10'

    >>> print(nt.dumps(data, map_keys=keymap, spacing={0: 1, "edges": 1}))
    # production deployment
    <BLANKLINE>
    # database server
    database: production
    <BLANKLINE>
    # how long the worker waits between retries
    retry_delay: 10

The *spacing* argument controls the dumper's vertical layout.  Integer
keys are depths: ``spacing={0: 1}`` puts at least one blank line between
top-level items, ``spacing={1: 1}`` between siblings at the first nested
level, and so on.  The special key ``"edges"`` is the number of blank
lines between the document's header comments and the body, and between
the body and the footer comments.  See :meth:`Location.set_spacing` for
how to attach a *spacing* dict to a particular Location, replacing the
global spacing within that subtree.

When the load and dump happen in different processes (or are otherwise
separated in time), use :func:`keymap_to_jsonable` and
:func:`keymap_from_jsonable` to ship the keymap between them as plain
JSON-serializable data:

.. code-block:: python

    >>> import json
    >>> blob = json.dumps(nt.keymap_to_jsonable(keymap))
    >>> rebuilt = nt.keymap_from_jsonable(json.loads(blob))
    >>> dumped_via_rebuilt = nt.dumps(data, map_keys=rebuilt, spacing={0: 1, "edges": 1})
    >>> dumped_via_original = nt.dumps(data, map_keys=keymap, spacing={0: 1, "edges": 1})
    >>> dumped_via_rebuilt == dumped_via_original
    True

Source line and column information is discarded by the JSON-able form;
only what the dumper consults (original key strings, comment slots,
per-Location spacing) survives.  Section predicates (set via
:meth:`Location.set_sections`) are also dropped because their predicates
are callables and not JSON-serializable.
