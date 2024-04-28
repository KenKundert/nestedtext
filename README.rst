NestedText — A Human Friendly Data Format
=========================================

|downloads| |build status| |coverage| |rtd status| |pypi version| |anaconda version| |python version|


| Authors: Ken & Kale Kundert
| Version: 3.7
| Released: 2024-04-27
| Documentation: nestedtext.org_
| Please post all questions, suggestions, and bug reports to GitHub_.
|

*NestedText* is a file format for holding structured data.  It is similar in 
concept to JSON_, except that *NestedText* is designed to make it easy for 
people to enter, edit, or view the data directly.  It organizes the data into 
a nested collection of name-value pairs, lists, and strings.  The syntax is 
intended to be very simple and intuitive for most people.

A unique feature of this file format is that it only supports one scalar type: 
strings.  As such, quoting strings is unnecessary, and without quoting there is 
no need for escaping.  While the decision to forego other types (integers, 
reals, Booleans, etc.) may seem counter productive, it leads to simpler data 
files and applications that are more robust.

*NestedText* is convenient for configuration files, data journals, address 
books, account information, and the like.  Here is an example of a file that 
contains a few addresses:

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

Typical Applications
--------------------

Configuration
"""""""""""""

Configuration files are an attractive application for *NestedText*.  
*NestedText* configuration files tend to be simple, clean and unambiguous.  
Plus, they handle hierarchy much better than alternatives such as Ini_ and 
TOML_.


Structured Code
"""""""""""""""

One way to build tools to tackle difficult and complex tasks is to provide an 
application specific language.  That can be a daunting challenge.  However, in 
certain cases, such as specifying complex configurations, *NestedText* can help 
make the task much easier.  *NestedText* conveys the structure of data leaving 
the end application to interpret the data itself.  It can do so with 
a collection of small parsers that are tailored to the specific piece of data to 
which they are applied.  This generally results in a simpler specification since 
each piece of data can be given in its natural format, which might otherwise 
confuse a shared parser.  In this way, rather than building one large very 
general language and parser, a series of much smaller and simpler parsers are 
needed.  These smaller parsers can be as simple as splitters or partitioners, 
value checkers, or converters for numbers in special forms (numbers with units, 
times or dates, GPS coordinates, etc.).  Or they could be full-blown expression 
evaluators or mini-languages.  Structured code provides a nice middle ground 
between data and code and its use is growing in popularity.

An example of structured code is provided by GitHub with its workflow 
specification files.  They use YAML_.  Unfortunately, the syntax of the code 
snippets held in the various fields can be confused with *YAML* syntax, which 
leads to unnecessary errors, confusion, and complexity (see *YAML issues*).  
JSON_ suffers from similar problems.  *NestedText* excels for these applications 
as it holds code snippets without any need for quoting or escaping.  
*NestedText* provides simple unambiguous rules for defining the structure of 
your data and when these rules are followed there is no way for any syntax or 
special characters in the values of your data to be confused with *NestedText* 
syntax.  In fact, it is possible for *NestedText* to hold *NestedText* snippets 
without conflict.

Another example of structured code is provided by the files that contain the 
test cases used by `Parametrize From File`_, a PyTest_ plugin.
*Parametrize From File* simplifies the task of specifying test cases for 
*PyTest* by separating the test cases from the test code.  Here it is being 
applied to test a command line program.  Its response is checked using regular 
expressions.  Each entry includes a shell command to run the program and 
a regular expression that must match the output for the test to pass::

    -
        cmd: emborg version
        expected: emborg version: \d+\.\d+(\.\d+(\.?\w+\d+)?)?  \(\d\d\d\d-\d\d-\d\d\)
        expected type: regex
    -
        cmd: emborg --quiet files -D
        expected:
            > Archive: home-\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d
            > \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\d\d\d\d configs/subdir/(file|)
            > \d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d.\d\d\d\d\d\d configs/subdir/(file|)
                # Unfortunately, we cannot check the order as they were both 
                # created at the same time.
        expected type: regex
    -
        cmd: emborg due --backup-days 1 --message "{elapsed} since last {action}"
        expected: home: (\d+(\.\d)? (seconds|minutes)) since last backup\.
        expected type: regex

Notice that the regular expressions are given clean, without any quoting or 
escaping.


Composable Utilities
""""""""""""""""""""

Another attractive use-case for *NestedText* is command line programs whose 
output is meant to be consumed by either people or other programs.  This is 
another growing trend.  Many programs do this by supporting a ``--json`` 
command-line flag that indicates the output should be computer readable rather 
than human readable.  But, with *NestedText* it is not necessary to make people 
choose.  Just output the result in *NestedText* and it can be read by people or 
computers.  For example, consider a program that reads your address list and 
output particular fields on demand::

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

Also, please consider using *NestedText* for any applications you create.


.. _json: https://www.json.org/json-en.html
.. _yaml: https://yaml.org/
.. _toml: https://toml.io/en/
.. _ini: https://en.wikipedia.org/wiki/INI_file
.. _parametrize from file: https://parametrize-from-file.readthedocs.io
.. _pytest: https://docs.pytest.org
.. _github: https://github.com/KenKundert/nestedtext/issues
.. _nestedtext.org: https://nestedtext.org

.. |downloads| image:: https://pepy.tech/badge/nestedtext/month
    :target: https://pepy.tech/project/nestedtext

.. |rtd status| image:: https://img.shields.io/readthedocs/nestedtext.svg
   :target: https://nestedtext.readthedocs.io/en/latest/?badge=latest

.. |build status| image:: https://github.com/KenKundert/nestedtext/actions/workflows/build.yaml/badge.svg
    :target: https://github.com/KenKundert/nestedtext/actions/workflows/build.yaml

.. |coverage| image:: https://coveralls.io/repos/github/KenKundert/nestedtext/badge.svg?branch=master
    :target: https://coveralls.io/github/KenKundert/nestedtext?branch=master

.. |pypi version| image:: https://img.shields.io/pypi/v/nestedtext.svg
    :target: https://pypi.python.org/pypi/nestedtext

.. |anaconda version| image:: https://anaconda.org/conda-forge/nestedtext/badges/version.svg
    :target: https://anaconda.org/conda-forge/nestedtext

.. |python version| image:: https://img.shields.io/pypi/pyversions/nestedtext.svg
    :target: https://pypi.python.org/pypi/nestedtext

