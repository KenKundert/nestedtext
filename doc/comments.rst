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

Each comment in a *NestedText* document falls into one of six slots,
according to where it sits in the source:

1. *header* — before all data, separated from data.
2. *footer* — after all data, separated from data.
3. *key leading* — before a key.
4. *key trailing* — after a key.
5. *value leading* — after a key, but before a value.
6. *value trailing* — after a value.

Inline comments — comments that appear inside a multiline string value —
are converted to value-trailing comments on load.  They are a
convenience for describing where comments are found in the source, not a
distinct stored type.


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

When two same-indent Comments end up adjacent within a single slot, the
dumper emits them contiguously.  A subsequent re-load merges adjacent
same-indent comment lines into a single Comment (text joined by ``\n``);
the text and slot assignment are preserved across the cycle, only the
Comment-object granularity may change.


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

Header and leading
~~~~~~~~~~~~~~~~~~

Partitioned by blank lines, only the last partition is eligible to be a
leading comment, and would only be so if it were immediately adjacent to
the first key or value.  Comments in a document that contains no data
are all header comments.

Trailing and leading
~~~~~~~~~~~~~~~~~~~~

A comment whose indent matches the indent of an adjacent value attaches
to that value.  If the indent matches both the value above and below, it
is taken to be a leading comment for the value below.

A comment that does not satisfy any of the other rules attaches as a
trailing comment to the closest data line above it whose indent does not
exceed the comment's own.

Examples::

    key:
        # leading on the value
        > value

The comment shares indent with the value below it — it leads the value.

::

    - first
    # leading on the next list item
    - second

Same indent above and below: the rule prefers leading on the next item.

::

    key:
            # trailing on the key
        > value

The comment's indent (8) does not match the value (4), nor any other
adjacent data; the orphan rule attaches it to ``key`` (the closest data
line above with indent ≤ 8) as a trailing comment.

Key / value
~~~~~~~~~~~

When a key and value are on the same line, leading comments associate
with the key and trailing comments associate with the value.

Footer and trailing
~~~~~~~~~~~~~~~~~~~

Partitioned by blank lines, only the first partition is eligible to be a
trailing comment, and would only be so if it were immediately adjacent
to its value with an equal or greater indent.


Implementation Guarantees
-------------------------

Inline comments are converted to value-trailing comments immediately
upon load, so the keymap exposes only header, leading, trailing, and
footer comments.

A comment may be misplaced through a round trip but it is never lost
and never causes an exception.  Some round-trip drift is unavoidable
under these rules -- for example, two adjacent comments at the same
indent in two different slots (such as a ``value_leading`` of one entry
and a ``key_leading`` of the next) merge into a single Comment on
re-load, and a ``value_trailing`` of a non-leaf entry may be
re-attached to a child of that entry rather than the entry itself.

Internally the loader splits "trailing of X" between X's
``key_trailing`` and ``value_trailing`` slots based on whether the
comment appeared before or after X's value in the source, so simple
round-trips of comments that sit adjacent to their data item remain
faithful.


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
    ...     (), keymap,
    ...     header=[Comment('application config')],
    ... )
    >>> _ = annotate(
    ...     ('database',), keymap,
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

Dynamic, Per-Child Comments
---------------------------

Section-style headers and any other comments whose content depends on the
key are produced by passing a **callable** to one of the four per-key
slots of :func:`annotate` instead of a list of :class:`Comment`.  When a
slot is a callable, it is treated as a *provider*: the dumper invokes it
once per child of the Location it is attached to, with the signature ::

    provider(child_key) -> list[Comment]

and prepends the returned Comments to whatever static comments that
child already has at the same slot.  The provider owns its dedup state
(via closure), so it can decide -- per child -- whether to emit anything,
and what to emit.

In the following example a *classifier* is used to add comments that act as 
section headings:

.. code-block:: python

    >>> from nestedtext import Comment, annotate

    >>> seen = set()
    >>> def classify(k):
    ...     cat = ("db" if k.startswith("db_") else
    ...            "log" if k.startswith("log_") else "other")
    ...     if cat in seen:
    ...         return []
    ...     seen.add(cat)
    ...     return [Comment({"db": "Database", "log": "Logging", "other": "Other"}[cat])]

    >>> keymap = {}
    >>> _ = annotate((), keymap, key_leading=classify)

    >>> data = {'db_host': 'localhost', 'db_port': '5432', 'log_level': 'info'}
    >>> print(nt.dumps(data, map_keys=keymap))
    # Database
    db_host: localhost
    db_port: 5432
    # Logging
    log_level: info

A provider also handles transitions in multiple grouping levels at once.
In the following, year and month comments are added to delineate the entries in 
a diary:

.. code-block:: python

    >>> last_year = last_month = None
    >>> def header(k):
    ...     global last_year, last_month
    ...     out = []
    ...     if k[:4] != last_year:
    ...         out.append(Comment(f"=== {k[:4]} ==="))
    ...         last_year = k[:4]
    ...     if k[:7] != last_month:
    ...         out.append(Comment(f"--- {k[5:7]} ---"))
    ...         last_month = k[:7]
    ...     return out

    >>> keymap = {}
    >>> _ = annotate((), keymap, key_leading=header)
    >>> data = {
    ...     "2024-01-15": "first",
    ...     "2024-02-04": "second",
    ...     "2025-01-09": "third",
    ... }
    >>> print(nt.dumps(data, map_keys=keymap))
    # === 2024 ===
    # --- 01 ---
    2024-01-15: first
    # --- 02 ---
    2024-02-04: second
    # === 2025 ===
    # --- 01 ---
    2025-01-09: third

A static list and a provider can coexist in the *same* slot on the
*same* Location, but they cannot both be specified in the same call to 
:func:`annotate`.  Each would need it own call.

When both a statically and dynamically provided comment exist on the same 
location, the dynamically provided comment precedes the static comment.

Providers are callables and therefore not JSON-serializable; they are dropped on
:func:`keymap_to_jsonable` round-trips.


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

You can also set the spacing on :class:`Location` objects in the keymap 
directly, which allows you to specify different spacing rules for different 
parts of the document.

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
per-Location spacing) survives.
