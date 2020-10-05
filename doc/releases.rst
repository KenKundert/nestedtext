************
Installation
************

.. currentmodule:: nestedtext

::

   pip3 install --user nestedtext


Releases
========

**Latest development release**:
    | Version: 1.0.2
    | Released: 2020-10-05

    - Empty dictionaries and lists are rejected by :func:`dump` and 
      :func:`dumps` if *default* argument is specified as 'strict'.

**1.0 (2020-10-03)**:
    - Production release.

**0.6 (2020-09-26)**:
    - Added :func:`load` and :func:`dump`.
    - Eliminated *NestedTextError.get_extended_codicil*.

**0.5 (2020-09-11)**:
    - allow user to manage duplicate keys detected by :func:`loads`.

**0.4 (2020-09-07)**:
    - Change rest-of-line strings to include all characters given, including 
      leading and trailing quotes and spaces.
    - The *NestedText* top-level is no longer restricted to only dictionaries 
      and lists. The top-level can now also be a single string.
    - :func:`loads` now returns *None* when given an empty *NestedText* document.
    - Change :exc:`NestedTextError` attribute names to make them more consistent 
      with those used by JSON package.
    - Added *NestedTextError.get_extended_codicil*.

**0.3 (2020-09-03)**:
    - Allow comments to be indented.

**0.2 (2020-09-02)**:
    - Minor enhancements and bug fixes.

**0.1 (2020-08-30)**:
    - Initial release.
