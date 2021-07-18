.. _language changes:

****************
Language changes
****************

.. currentmodule:: nestedtext

Currently the language and the :ref:`Python implementation <implementation 
changes>`  share version numbers.  Since the language is more stable than the 
implementation, you will see versions that include no changes to the language.


Latest development version
--------------------------

| Version: 3.0.0
| Released: 2021-07-17


v3.0 (2021-07-17)
-----------------

- Deprecate trailing commas in inline lists and dictionaries.

.. warning::

    Be aware that aspects of this version are not backward compatible.
    Specifically, trailing commas are no longer supported in inline
    dictionaries and lists.  In addition, ``[ ]`` now represents a list with
    an that contains an empty string, whereas previously it represented an
    empty list.


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


v1.0 (2020-10-03)
-----------------

- Initial release.
