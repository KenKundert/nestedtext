.. currentmodule:: nestedtext

Comment
-------

Comment objects can be attached to keymap entries to associate comments with 
specific keys or values.  Comments are automatically captured and attached to 
a keymap entry by :func:`load` / :func:`loads` when a *keymap* is supplied.  It 
is also possible to build a keymap up from scratch and attach comments using 
:func:`annotate`.  Then, the output of :func:`dump` / :func:`dumps` via 
``map_keys=`` is adorned with the comments when such a *keymap* is passed in via 
``map_keys=``.  See :doc:`comments` for the full story (attribution rules,
read/write API, and round-tripping).

.. autoclass:: Comment

The :class:`Location` class exposes accessor methods for reading and modifying
the comments attached to each key (``get_key_leading_comments`` and friends).
Document-level header and footer comments live on the root Location at
``keymap[()]``, accessed via :meth:`Location.get_header_comments` /
:meth:`~Location.set_header_comments` / :meth:`~Location.add_header_comment`
and the equivalent footer trio.  Every key in the keymap is a tuple, so
depth-based iteration using ``len(keys)`` remains safe.

Per-Location spacing is also supported via :meth:`Location.get_spacing` /
:meth:`~Location.set_spacing`.  A non-empty spacing dict attached to a
Location replaces the :func:`dumps` ``spacing`` argument for that
Location's entire subtree; integer keys are interpreted as *relative*
depth (``0`` = blank lines between this Location's direct children, ``1``
= grandchildren, …) and absent depth keys default to zero.  The
``"edges"`` key is only consulted on the document-root Location
(``keymap[()]``).
