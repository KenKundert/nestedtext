.. _implementation changes:

********
Releases
********

.. currentmodule:: nestedtext

This page documents the changes in the Python implementation of *NestedText*.
Changes to the *NestedText* language are shown in :ref:`language changes`.


Latest development version
--------------------------

| Version: 3.8.dev2
| Released: 2025-04-05

**Bug Fixes**:

- Catch multi-line key not followed by indented value.
- Make line-ending recognition consistent for files and strings.
- Fix bug in :func:`get_value()`.
- Report error if there is content that follows top-level inline dictionary.

**Enhancements**:

- Support files that have utf8 byte-order marker (BOM).
- Allow binary files to be passed to :func:`load()` and :func:`dump()`.
- Allow byte strings to be passed to :func:`loads()`.

**Tests**:

In version 3.8 a new implementation independent set of tests is being developed.  
These tests should be more comprehensive and more independent of the Python 
implementation of *NestedText*.


v3.7 (2024-04-27)
-----------------
- Added ability to disable support for inlines using *dialect* argument to 
  :func:`load()` and :func:`loads()`.
- Added :func:`get_keys()`, :func:`get_value()`, :func:`get_line_numbers()`, and 
  :func:`get_location()`.
- Deprecated :func:`get_value_from_keys()`, :func:`get_lines_from_keys()`,
  :func:`get_original_keys()`, and :func:`join_keys()`.
- Added *offset* argument to :meth:`Location.as_line()`.
- Add ability to specify *source* to :func:`load()`.
- Clarified policy on white space in inline strings.


v3.6 (2023-05-30)
-----------------

- De-duplicating with the *on_dup* argument to :func:`loads` now works well for 
  error reporting with keymaps.
- The *map_keys* argument has been added to :func:`dump` and :func:`dumps`.

.. warning::

    The *sort_keys* argument to :func:`dump` and :func:`dumps` has changed.  
    When passing a call-back function to *sort_keys*, that call-back function 
    now has a second argument, *parent_keys*.  In addition, the first argument 
    has changed.  It is now a tuple with three members rather than two, with the 
    new and leading member being the mapped key rather than the original key.

.. warning::

    The state passed to the *on_dup* functions of :func:`dump` and :func:`dumps` 
    no longer contains the value associated with the duplicate key.


v3.5 (2022-11-04)
-----------------

- Minor refinements and fixes.


v3.4 (2022-06-15)
-----------------

- Improved the *on_dup* parameter to :meth:`load` and :meth:`loads`.
- Added *strict* argument to :func:`join_keys`.

.. warning::

    Be aware that the new version of the *on_dup* parameter is not compatible 
    with previous versions.


v3.3 (2022-06-07)
-----------------

- Add *normalize_key* argument to :meth:`load` and :meth:`loads`.
- Added utility functions for operating on keys and keymaps:

  - :func:`get_value_from_keys`
  - :func:`get_lines_from_keys`
  - :func:`get_original_keys`
  - :func:`join_keys`

- None passed as key is now converted to an empty string rather than "None".


v3.2 (2022-01-17)
-----------------

- Add circular reference detection and reporting.


v3.1 (2021-07-23)
-----------------

- Change error reporting for :func:`dumps` and :func:`dump` functions;
  culprit is now the keys rather than the value.


v3.0 (2021-07-17)
-----------------

- Deprecate trailing commas in inline lists and dictionaries.
- Adds *keymap* argument to :func:`load` and :func:`loads`.
- Adds *inline_level* argument to :func:`dump` and :func:`dumps`.
- Implement *on_dup* argument to :func:`load` and :func:`loads` in inline 
  dictionaries.
- Apply *convert* and *default* arguments of :func:`dump` and :func:`dumps` to 
  dictionary keys.

.. warning::

    Be aware that aspects of this version are not backward compatible.
    Specifically, trailing commas are no longer supported in inline dictionaries 
    and lists.  In addition, ``[ ]`` now represents a list that contains an 
    empty string, whereas previously it represented an empty list.


v2.0 (2021-05-28)
-----------------

- Deprecate quoted keys.
- Add multiline keys to replace quoted keys.
- Add inline lists and dictionaries.
- Move from *renderers* to *converters* in :func:`dump` and :func:`dumps`.  
  Both allow you to support arbitrary data types.  With *renderers* you 
  provide functions that are responsible for directly creating the text to 
  be inserted in the *NestedText* output.  This can be complicated and error 
  prone.  With *converters* you instead convert the object to a known 
  *NestedText* data type (dict, list, string, ...) and the *dump* function 
  automatically formats it appropriately.
- Restructure documentation.

.. warning::

    Be aware that aspects of this version are not backward compatible.

    1. It no longer supports quoted dictionary keys.

    2. The *renderers* argument to :func:`dump` and :func:`dumps` has been replaced by *converters*.

    3. It no longer allows one to specify *level* in :func:`dump` and :func:`dumps`.


v1.3 (2021-01-02)
-----------------

- Move the test cases to a submodule.

.. note::

    When cloning the *NestedText* repository you should use the --recursive 
    flag to get the *official_tests* submodule::

        git clone --recursive https://github.com/KenKundert/nestedtext.git

    When updating an existing repository, you need to initialize the 
    submodule after doing a pull::

       git submodule update --init --remote tests/official_tests

    This only need be done once.


v1.2 (2020-10-31)
-----------------

- Treat CR LF, CR, or LF as a line break.
- Always quote keys that start with a quote.


v1.1 (2020-10-13)
-----------------

- Add ability to specify return type of :func:`load` and :func:`loads`.
- Quoted keys are now less restricted.
- Empty dictionaries and lists are rejected by :func:`dump` and 
  :func:`dumps` except as top-level object if *default* argument is 
  specified as 'strict'.

.. warning::

    Be aware that this version is not fully backward compatible.  Unlike 
    previous versions, this version allows you to restrict the type of the 
    return value of the :func:`load` and :func:`loads` functions, and the 
    default is 'dict'.  The previous behavior is still supported, but you 
    must explicitly specify `top='any'` as an argument.

    This change results in a simpler return value from :func:`load` and 
    :func:`loads` in most cases. This substantially reduces the chance of 
    coding errors.  It was noticed that it was common to simply assume that 
    the top-level was a dictionary when writing code that used these 
    functions, which could result in unexpected errors when users 
    hand-create the input data. Specifying the return value eliminates this 
    type of error.

    There is another small change that is not backward compatible. The 
    source argument to these functions is now a keyword only argument.


v1.0 (2020-10-03)
-----------------
- Production release.


.. ignore earlier releases:

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
