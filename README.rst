NestedText: A Human Friendly Data Format
========================================

.. image:: https://pepy.tech/badge/nestedtext/month
    :target: https://pepy.tech/project/nestedtext

.. image:: https://img.shields.io/readthedocs/nestedtext.svg
   :target: https://nestedtext.readthedocs.io/en/latest/?badge=latest

..  image:: https://github.com/KenKundert/nestedtext/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/KenKundert/nestedtext/actions/workflows/build.yaml

.. image:: https://coveralls.io/repos/github/KenKundert/nestedtext/badge.svg?branch=master
    :target: https://coveralls.io/github/KenKundert/nestedtext?branch=master

.. image:: https://img.shields.io/pypi/v/nestedtext.svg
    :target: https://pypi.python.org/pypi/nestedtext

.. image:: https://img.shields.io/pypi/pyversions/nestedtext.svg
    :target: https://pypi.python.org/pypi/nestedtext


| Authors: Ken & Kale Kundert
| Version: 3.1.0
| Released: 2021-07-23
| Documentation: `nestedtext.org <https://nestedtext.org>`_.
| Please post all questions, suggestions, and bug reports to: `Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


*NestedText* is a file format for holding structured data to be entered, edited, 
or viewed by people. It organizes into a nested collection of dictionaries, 
lists, and strings without the need for quoting or escaping.

*NestedText* is convenient for configuration files, address books, account 
information, and the like.  Because there is no need for quoting or escaping, it 
is particularly nice for holding code fragments.  Here is an example of a file 
that contains a few addresses:

.. code-block:: nestedtext

    # Contact information for our officers

    president:
        name: Katheryn McDaniel
        address:
            > 138 Almond Street
            > Topeka, Kansas 20697
        phone:
            cell: 1-210-555-5297
            home: 1-210-555-8470
                # Katheryn prefers that we always call her on her cell phone.
        email: KateMcD@aol.com
        additional roles:
            - board member

    vice president:
        name: Margaret Hodge
        address:
            > 2586 Marigold Lane
            > Topeka, Kansas 20682
        phone: 1-470-555-0398
        email: margaret.hodge@ku.edu
        additional roles:
            - new membership task force
            - accounting task force

*NestedText* is an alternative to *JSON*, *YAML*, and other such languages in 
that it represents a nested collection of values.  However, it has one very 
important distinguishing feature that makes it unique: all the leaf values are 
strings (hence the name).  All the alternatives support many scalar types for 
the leaf values, such as Booleans, integers, real numbers, strings, etc.  As 
such, the they must distinguish all these various types by syntax, which 
complicates the alternatives, typically by requiring the use of quoting and 
escaping on strings.  Since every leaf value is a string in *NestedText*, the 
end application becomes responsible for converting values to their final types 
when needed, but this is the best place to do it because the it generally knows 
that is expected and how to do the conversion.


Contributing
------------

This package contains a Python reference implementation of *NestedText* and 
a test suite.  Implementation in many languages is required for *NestedText* to 
catch on widely.  If you like the format, please consider contributing 
additional implementations.
