NestedText: A Human Friendly Data Format
========================================

.. image:: https://img.shields.io/travis/KenKundert/nestedtext/master.svg
    :target: https://travis-ci.org/KenKundert/nestedtext

.. image:: https://img.shields.io/coveralls/KenKundert/nestedtext.svg
    :target: https://coveralls.io/r/KenKundert/nestedtext

.. image:: https://img.shields.io/pypi/v/nestedtext.svg
    :target: https://pypi.python.org/pypi/nestedtext

.. image:: https://img.shields.io/pypi/pyversions/nestedtext.svg
    :target: https://pypi.python.org/pypi/nestedtext



| Version: 0.2.0
| Released: 2020-09-02
| Please post all questions, suggestions, and bug reports to
  `NestedText Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


*NestedText* is a file format for exchanging data held in strings, lists, and␣
dictionaries.  In this way it is similar to *JSON*, *YAML*, or *StrictYAML*, but 
with a restricted set of supported data types, the file format is simpler. It is␣
designed to be easy to enter with a text editor and easy to read.  The small␣
number of data types supported means few rules need be kept in mind when␣
creating a file.  The result is a data file that is easily created, modified, or␣
viewed with a text editor and be understood and used by both programmers and␣
non-programmers.

*NestedText* is convenient for configuration files, address books, account 
information and the like.  Here is an example of a file that contains a few 
addresses::

    # Contact information for our officers

    president:
        name: Katheryn McDaniel
        address:
            > 138 Almond Street
            > Topika, Kansas 20697
        phone:
            cell: 1-210-555-5297
            home: 1-210-555-8470
        email: KateMcD@aol.com
        kids:
            - Joanie
            - Terrance

    vice president:
        name: Margaret Hodge
        address:
            > 2586 Marigold Lane
            > Topika, Kansas 20682
        phone: 1-470-555-0398
        email: margarett.hodge@uk.edu
        kids:
            - Arnie
            - Zach
            - Maggie

    treasurer:
        name: Fumiko Purvis
        address:
            > 3636 Buffalo Ave
            > Topika, Kansas 20692
        phone: 1-268-555-0280
        email: fumiko.purvis@hotmail.com
        kids:
            - Lue

The format can hold dictionaries (ordered collections of name/value pairs), 
lists (ordered collections of values) and strings organized hierarchically to 
any depth.  Indentation is used to indicate the hierarchy of the data, and 
a simple natural syntax is used to distinguish the types of data in such 
a manner that it is not easily confused.


Alternatives
------------

There are no shortage of well established alternative to *NestedText* for 
storing data in a human-readable text file. Probably the most obvious are `json 
<https://docs.python.org/3/library/json.html>`_ and `YAML 
<https://pyyaml.org/wiki/PyYAMLDocumentation>`_.  Both have serious short 
comings.

*JSON* is a subset of JavaScript suitable for holding data. Like *NestedText* it 
consists of a hierarchical collection of dictionaries, lists, and strings, but 
also allows integers, floats, booleans and nulls.  The problem with *JSON* for 
this application is that it is awkward. All strings have to be quoted; it only 
supports multi-line strings by using long single-line strings with embedded 
newline characters; and dictionary and list items must be separated with commas.  
All of which results in *JSON* being a frustrating format for humans to enter or 
read.

*YAML* was to be the human friendly alternative to *JSON*, but things went very 
wrong at some point. The authors were too ambitious and tried to support too 
many data types and too many formats. To distinguish between all the various 
types and formats, a complicated and non-intuitive set of rules developed.  
*YAML* at first appears very appealing when used with simple examples, but 
things quickly become very complicated.  A reaction to this is the use of *YAML* 
subsets, such as `StrictYAML <https://hitchdev.com/strictyaml>`_.  However, the 
subsets try to maintain compatibility with *YAML* and so inherits much of its 
complexity.

*NestedText* was inspired by *YAML*, but eschews its complexity. It supports 
only a limited number of types and has a very simple set of rules that make up 
the format.


Quick Start
-----------

Install with::

   pip3 install --user nestedtext


Issues
------

Please ask questions or report problems on `Github 
<https://github.com/KenKundert/nestedtext/issues>`_.


Contributing
------------

This package contains a Python implmentation of *NestedText*. For *NestedText* 
to catch on widely, implementations in many language will required. If you like 
the format and have interest in doing so, please consider contributing 
additional implementations, particularly for other languages.
