************
Installation
************

.. currentmodule:: nestedtext

::

   pip3 install --user nestedtext

Releases
========
**Latest development release**:
    | Version: 0.4.0
    | Released: 2020-09-07

**0.4 (2020-09-07)**:
    - Change rest-of-line strings to include all characters given, including 
      leading and trailing quotes and spaces.
    - The *NestedText* top-level is no longer restricted to only dictionaries 
      and lists. The top-level can now also be a single string.
    - :func:`loads` now returns *None* when given an empty *NestedString*.
    - Change :exc:`NestedTextError` attribute names to make them more consistent 
      with those used by JSON package.
    - Added :meth:`NestedTextError.get_extended_codicil`.

**0.3 (2020-09-03)**:
    - Allow comments to be indented.

**0.2 (2020-09-02)**:
    - Minor enhancements and bug fixes.

**0.1 (2020-08-30)**:
    - Initial release.
