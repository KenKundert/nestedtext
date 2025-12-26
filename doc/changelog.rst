.. _language changes:

****************
Language changes
****************

.. currentmodule:: nestedtext

Currently the language and the :ref:`Python implementation <implementation 
changes>` share version numbers.  Since the language is more stable than the 
implementation, you will see versions that include no changes to the language.


Latest development version
--------------------------

| Version: 3.8
| Released: 2025-12-26

.. _v3.8:

v3.8 (2025-12-26)
-----------------

- No changes to language.
- Replaced official test suite.


.. _v3.7:

v3.7 (2024-04-27)
-----------------

- Clarified policy on white space in inline strings.


.. _v3.6:

v3.6 (2023-05-30)
-----------------

- No changes.


.. _v3.5:

v3.5 (2022-11-04)
-----------------

- No changes.


.. _v3.4:

v3.4 (2022-06-15)
-----------------

- No changes.


.. _v3.3:

v3.3 (2022-06-07)
-----------------

- Defined *Minimal NestedText*, a subset of *NestedText*.
- *NestedText* document files should end with a newline.


.. _v3.2:

v3.2 (2022-01-17)
-----------------

- No changes.


.. _v3.1:

v3.1 (2021-07-23)
-----------------

- No changes.


.. _v3.0:

v3.0 (2021-07-17)
-----------------

- Deprecate trailing commas in inline lists and dictionaries.

.. warning::

    Be aware that aspects of this version are not backward compatible.
    Specifically, trailing commas are no longer supported in inline
    dictionaries and lists.  In addition, ``[ ]`` now represents a list
    that contains an empty string, whereas previously it represented an
    empty list.


.. _v2.0:

v2.0 (2021-05-28)
-----------------

- Deprecate quoted dictionary keys.
- Add multiline dictionary keys to replace quoted keys.
- Add single-line lists and dictionaries.

.. warning::

    Be aware that this version is not backward compatible because it no 
    longer supports quoted dictionary keys.


v1.3 (2021-01-02)
-----------------

- No changes.


v1.2 (2020-10-31)
-----------------

- Treat CR LF, CR, or LF as a line break.


v1.1 (2020-10-13)
-----------------

- No changes.


.. _v1.0:

v1.0 (2020-10-03)
-----------------

- Initial release.
