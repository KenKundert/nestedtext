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
| Version: 3.3.0
| Released: 2022-06-07
| Documentation: `nestedtext.org <https://nestedtext.org>`_.
| Please post all questions, suggestions, and bug reports to: `Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


NestedText is a file format for holding structured data to be entered, edited, 
or viewed by people. It organizes the data into a nested collection of 
dictionaries, lists, and strings without the need for quoting or escaping.  
A unique feature of this file format is that it only supports one scalar type: 
strings.  While the decision to eschew integer, real, date, etc. types may seem 
counter intuitive, it leads to simpler data files and applications that are more 
robust.

*NestedText* is convenient for configuration files, address books, account 
information, and the like.  Because there is no need for quoting or escaping, it 
is particularly nice for holding code fragments.  Here is an example of a file 
that contains a few addresses:

.. code-block:: nestedtext

    # Contact information for our officers

    Katheryn McDaniel:
        position: president
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

    Margaret Hodge:
        position: vice president
        address:
            > 2586 Marigold Lane
            > Topeka, Kansas 20682
        phone: 1-470-555-0398
        email: margaret.hodge@ku.edu
        additional roles:
            - new membership task force
            - accounting task force


Contributing
------------

This package contains a Python reference implementation of *NestedText* and 
a test suite.  Implementation in many languages is required for *NestedText* to 
catch on widely.  If you like the format, please consider contributing 
additional implementations.

Also, please consider using *NestedText* for any applications you create.  It is 
especially suitable for configuration files.
