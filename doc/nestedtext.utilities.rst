.. currentmodule:: nestedtext

KeyMap Utilities
================

Extras that are useful when using *NestedText*.

.. autofunction:: get_keys

.. autofunction:: get_value

.. autofunction:: get_line_numbers

.. autofunction:: get_location

.. autofunction:: annotate


Transferring a Keymap Between Processes
---------------------------------------

When the load → modify → dump cycle is split across processes (so the data is
serialized between them, for example as JSON), the keymap must travel with the
data if comments and original key spellings are to be restored on dump.
:func:`keymap_to_jsonable` reduces a keymap to a structure built from plain
``dict``, ``list``, ``str``, ``int``, and ``None`` — pass it through
:mod:`json`, :mod:`msgpack`, or any other encoder of your choice — and
:func:`keymap_from_jsonable` rebuilds the keymap on the other side.  Only the
information :func:`dump` actually consults is preserved (original key strings
and comment slots); source line and column numbers are discarded.

.. autofunction:: keymap_to_jsonable

.. autofunction:: keymap_from_jsonable
