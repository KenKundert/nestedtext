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


| Version: 0.4.0
| Released: 2020-09-07
| Please post all questions, suggestions, and bug reports to
  `NestedText Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


*NestedText* is a file format for exchanging data held in lists, dictionaries, 
and strings.  In this way it is similar to JSON, YaML, or StrictYaML, but with 
a restricted set of supported data types, the file format is simpler. It is 
designed to be easy to enter with a text editor and easy to read.  The small 
number of data types supported means few rules need be kept in mind when 
creating a file.  The result is a data file that is easily created, modified, or 
viewed with a text editor and easily understood and used by both programmers and 
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
                # Katheryn prefers that we always call her on her cell phone.
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
        email: margaret.hodge@uk.edu
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

The format holds dictionaries (ordered collections of name/value pairs), lists 
(ordered collections of values) and strings organized hierarchically to any 
depth.  Indentation is used to indicate the hierarchy of the data, and a simple 
natural syntax is used to distinguish the types of data in such a manner that it 
is not easily confused.


Alternatives
------------

There are no shortage of well established alternatives to *NestedText* for 
storing data in a human-readable text file. Probably the most obvious are `json 
<https://docs.python.org/3/library/json.html>`_ and `YAML 
<https://pyyaml.org/wiki/PyYAMLDocumentation>`_.  Both have serious short 
comings.

*JSON* is a subset of JavaScript suitable for holding data. Like *NestedText*, 
it consists of a hierarchical collection of dictionaries, lists, and strings, 
but also allows integers, floats, Booleans and nulls.  The problem with *JSON* 
for this application is that it is awkward. All strings have to be quoted; it 
only supports multi-line strings by using long single-line strings with embedded 
newline characters; and dictionary and list items must be separated with commas.  
All of which results in *JSON* being a frustrating format for humans to read, 
enter or edit.

*YAML* was to be the human friendly alternative to *JSON*, but things went very 
wrong. The authors were too ambitious and tried to support too many data types 
and too many formats. To distinguish between all the various types and formats, 
a complicated and non-intuitive set of rules developed.  *YAML* at first appears 
very appealing when used with simple examples, but things quickly become very 
complicated.  A reaction to this is the use of *YAML* subsets, such as 
`StrictYAML <https://hitchdev.com/strictyaml>`_.  However, the subsets still try 
to maintain compatibility with *YAML* and so inherits much of its complexity.

*NestedText* was inspired by *YAML*, but eschews its complexity. It supports 
only a limited number of types and has a very simple set of rules that make up 
the format.  *NestedText* is an improvement over *JSON* in that it only accepts 
strings as it leaf values, where as *JSON* needs to distinguish between many 
possible types. For example, in *JSON* 32 is an integer, 32.0 is the real 
version of 32, and "32" is the string version. As a result, all strings in 
*JSON* must be quoted, which, since most leaf values are strings, adds 
substantial clutter.  The problem is different in *YAML*, which tries to 
determine the value's type based on context. So 32 alone in a field is an 
integer, but if combined with other characters, such as 32.0.2 or *I have 32 
kites*, it is part of a string.  *NestedText* avoids these issues by treating 
all leaf values as strings. It is up to application that employs *NestedText* as 
an input format to sort things out later.  Consider the following *YAML* 
fragment::

    Enrolled: NO
    Country Code: NO

Presumably *Enrolled* is meant to be a Boolean value whereas *Country Code* is 
meant to be a string (*NO* is the country code for Norway). Reading this 
fragment with *YAML* results in {'Enrolled': *False*, 'Country Code': *False*}.  
When read by *NestedText* both values become 'NO', but the assumption is that 
*Enrolled* knows how to convert 'NO' to *False*. The same is not possible with 
*YAML* because many possible strings map to *False* (`n`, `no`, `false`, `off`; 
etc.) and it is hard to know which one was given.

Fundamentally the issue with *YAML* is a crisis of its own making. It reads 
a language that is inherently ambiguous and so is forced to make decisions it 
has no ability to make sensibly.  With *NestedText* the language is unambiguous 
and any decisions about how to interpret the leaf values are passed to the end 
application, which is the only place where they can be made knowledgeably.



Issues
------

Please ask questions or report problems on `Github 
<https://github.com/KenKundert/nestedtext/issues>`_.


Contributing
------------

This package contains a Python reference implementation of *NestedText*.
Implementation in many languages is required for *NestedText* to catch on widely.
If you like the format, please consider contributing additional implementations. 
