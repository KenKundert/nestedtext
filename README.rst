NestedText — A Human Friendly Data Format
=========================================

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
| Version: 3.6
| Released: 2023-05-30
| Documentation: `nestedtext.org <https://nestedtext.org>`_.
| Please post all questions, suggestions, and bug reports to: `Github <https://github.com/KenKundert/nestedtext/issues>`_.
|

*NestedText* is a file format for holding structured data.  It is similar in 
concept to `JSON <https://en.wikipedia.org/wiki/JSON>`_, except that 
*NestedText* is designed to make it easy for people to enter, edit, or view the 
data directly.  It organizes the data into a nested collection of name-value 
pairs, lists, and strings.  The syntax is intended to be very simple and 
intuitive for most people.

A unique feature of this file format is that it only supports one scalar type: 
strings.  As such, quoting strings is unnecessary, and without quoting there is 
no need for escaping.  While the decision to forego other types (integers, 
reals, dates, etc.) may seem counter productive, it leads to simpler data files 
and applications that are more robust.

*NestedText* is convenient for configuration files, address books, account 
information, and the like.  Here is an example of a file that contains a few 
addresses:

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

A strength of *NestedText* is its lack of quoting and escaping, making it 
particularly nice for holding code fragments.  Here is another example of 
*NestedText* that shows off this feature.  It holds some `Parametrize From File 
<https://parametrize-from-file.readthedocs.io>`_ test cases for `pytest 
<https://docs.pytest.org>`_.  In this case a command line program is being 
tested and its response is checked using regular expressions::

    -
        cmd: emborg version
        expected: emborg version: \d+\.\d+(\.\d+(\.?\w+\d+)?)?  \(\d\d\d\d-\d\d-\d\d\)
        expected_type: regex
    -
        cmd: emborg --quiet list
        expected: home-\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d
        expected_type: regex
    -
        cmd: emborg --quiet borg list --glob-archives "home-*" --short @repo
        expected: home-\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d
        expected_type: regex
    -
        cmd: emborg --quiet files -D
        expected:
            > Archive: home-\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d
            > \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\d\d\d\d configs/subdir/(file|)
            > \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\d\d\d\d configs/subdir/(file|)
                # Unfortunately, we cannot check the order as they were both 
                # created at the same time.
        expected_type: regex
    -
        cmd: emborg due --backup-days 1 --message "{elapsed} since last {action}"
        expected: home: (\d+(\.\d)? (seconds|minutes)) since last backup\.
        expected_type: regex

One particularly attractive use-case for *NestedText* is command line programs 
whose output is meant to be consumed by either people or programs.  Many 
programs do so by supporting a ``--json`` command-line flag that indicates the 
output should be computer readable rather than human readable.  But, with 
*NestedText* it is not necessary to make people choose.  Just output the result 
in *NestedText* and it can be read by people or computers.  For example, 
consider a program that reads your address list and output particular fields on 
demand::

    > address --email
    Katheryn McDaniel: KateMcD@aol.com
    Margaret Hodge: margaret.hodge@ku.edu

This output could be fed directly into another program that accepts *NestedText* 
as input::

    > address --email | mail-to-list


Contributing
------------

This package contains a Python reference implementation of *NestedText* and 
a test suite.  Implementation in many languages is required for *NestedText* to 
catch on widely.  If you like the format, please consider contributing 
additional implementations.

Also, please consider using *NestedText* for any applications you create.  It is 
especially suitable for configuration files.
