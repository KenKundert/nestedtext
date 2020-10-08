************
Installation
************

.. currentmodule:: nestedtext

::

   pip3 install --user nestedtext


Releases
========

Latest development release
--------------------------

    | Version: 1.0.3
    | Released: 2020-10-06

    - Top-level object must now be a dictionary.
    - Quoted keys are now less restricted.
    - Empty dictionaries and lists are rejected by :func:`dump` and 
      :func:`dumps` if *default* argument is specified as 'strict'.

    .. warning::

        Be aware that this version is not fully backward compatible.  
        Specifically, the previous version allowed a list or a string as the 
        top-level data, but this version only allows a dictionary as the 
        top-level.  This results in a simpler return value from :func:`load` and 
        :func:`loads` and substantially reduces the change of coding errors.  It 
        was noticed that it was common to simply assume that the top-level was 
        a dictionary when writing code that used these functions, which would 
        result in unexpected errors when users hand-create the input data.

v1.0 (2020-10-03)
-----------------
    - Production release.

v0.6 (2020-09-26)
-----------------
    - Added :func:`load` and :func:`dump`.
    - Eliminated *NestedTextError.get_extended_codicil*.

v0.5 (2020-09-11)
-----------------
    - allow user to manage duplicate keys detected by :func:`loads`.

v0.4 (2020-09-07)
-----------------
    - Change rest-of-line strings to include all characters given, including 
      leading and trailing quotes and spaces.
    - The *NestedText* top-level is no longer restricted to only dictionaries 
      and lists. The top-level can now also be a single string.
    - :func:`loads` now returns *None* when given an empty *NestedText* document.
    - Change :exc:`NestedTextError` attribute names to make them more consistent 
      with those used by JSON package.
    - Added *NestedTextError.get_extended_codicil*.

v0.3 (2020-09-03)
-----------------
    - Allow comments to be indented.

v0.2 (2020-09-02)
-----------------
    - Minor enhancements and bug fixes.

v0.1 (2020-08-30)
-----------------
    - Initial release.
