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


| Authors: Ken & Kale Kundert
| Version: 1.0.0
| Released: 2020-10-03
| Please post all questions, suggestions, and bug reports to
  `NestedText Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


*NestedText* is a file format for holding data that is to be entered, edited, or 
viewed by people.  It allows data to be organized into a nested collection of 
dictionaries, lists, and strings.  In this way it is similar to *JSON* and 
*YAML*, but without the complexity and risk of *YAML* and without the syntatic 
clutter of *JSON*.  *NestedText* is both simple and natural. Only a small number 
of concepts and rules must be kept in mind when creating it.
It is easily created, modified, or viewed with a text editor and easily 
understood and used by both programmers and non-programmers.

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
        additional roles:
            - board member

    vice president:
        name: Margaret Hodge
        address:
            > 2586 Marigold Lane
            > Topika, Kansas 20682
        phone: 1-470-555-0398
        email: margaret.hodge@uk.edu
        additional roles:
            - new membership task force
            - accounting task force

    treasurer:
        name: Fumiko Purvis
            # Fumiko's term is ending at the end of the year.
            # She will be replaced by Merrill Eldridge.
        address:
            > 3636 Buffalo Ave
            > Topika, Kansas 20692
        phone: 1-268-555-0280
        email: fumiko.purvis@hotmail.com
        additional roles:
            - accounting task force

The format holds dictionaries (ordered collections of name/value pairs), lists 
(ordered collections of values) and strings (text) organized hierarchically to 
any depth.  Indentation is used to indicate the hierarchy of the data, and 
a simple natural syntax is used to distinguish the types of data in such 
a manner that it is not easily confused.  Specifically, lines that begin with 
a word or words followed by a colon are dictionary items; a dash introduces list 
items, and a leading greater-than symbol signifies a line in a multiline string.
Dictionaries and lists are used for nesting, the leaf values are always strings.


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
for this application is that it is awkward.  With all those data types it must 
syntactically distinguish between them.  For example, in *JSON* 32 is an 
integer, 32.0 is the real version of 32, and "32" is the string version. These 
distinctions are not meaningful and can be confusing to non-programmers. In 
addition, in most datasets a majority of leaf values are strings and the 
required quotes adds substantial visual clutter.  *NestedText* avoids these 
issues by treating all leaf values as strings with no need for quoting or 
escaping.  It is up to the application that employs *NestedText* as an input 
format to sort things out later.

*JSON* does not provide for multiline strings and any special characters like 
newlines or unicode are encoded with escape codes, which can make strings quite 
difficult to interpret.  Finally, dictionary and list items must be separated 
with commas, but a comma must not follow last item.  All of this results in 
*JSON* being a frustrating format for humans to read, enter or edit.

*NestedText* has the following clear advantages over *JSON* as human readable 
and writable data file format:

- text does not require quotes
- data type does not change based on seemingly insignificant details (32, 32.0, "32")
- comments
- multiline strings
- special characters without escaping them
- Unicode characters without encoding them
- commas are not used to separate dictionary and list items

*YAML* was to be the human friendly alternative to *JSON*, but the authors were 
too ambitious and tried to support too many data types and too many formats. To 
distinguish between all the various types and formats, a complicated and 
non-intuitive set of rules developed.  For example, 2 is interpreted as an 
integer, 2.0 as a real number, and both 2.0.0 and "2" are strings.  *YAML* at 
first appears very appealing when used with simple examples, but things can 
quickly become complicated or provide unexpected results.  A reaction to this is 
the use of *YAML* subsets, such as `StrictYAML 
<https://hitchdev.com/strictyaml>`_.  However, the subsets still try to maintain 
compatibility with *YAML* and so inherit much of its complexity. For example, 
both *YAML* and *StrictYAML* support the `nine different ways to write 
multi-line strings in YAML <http://stackoverflow.com/a/21699210/660921>`_.

*YAML* recognized the problems that result from *JSON* needing to unambiguously 
distinguish between many data types and instead uses implicit typing, which 
creates its own `problems
<https://hitchdev.com/strictyaml/why/implicit-typing-removed>`_.
For example, consider the following *YAML* fragment::

    Enrolled: NO
    Country Code: NO

Presumably *Enrolled* is meant to be a Boolean value whereas *Country Code* is 
meant to be a string (*NO* is the country code for Norway). Reading this 
fragment with *YAML* results in {'Enrolled': *False*, 'Country Code': *False*}.  
When read by *NestedText* both values are retained in their original form as 
strings.  With *NestedText* any decisions about how to interpret the leaf values 
are passed to the end application, which is the only place where they can be 
made knowledgeably.  The assumption is that the end application knows that 
*Enrolled* should be a Boolean and knows how to convert 'NO' to *False*.  The 
same is not possible with *YAML* because the *Country Code* value has been 
transformed and because there are many possible strings that map to *False* 
(`n`, `no`, `false`, `off`; etc.).

This is one example of the many possible problems that stem from implicit 
typing.  In fact, many people make it a habit to add quotes to all values simply 
to avoid the ambiguities, which makes *YAML* more like *JSON*.

*NestedText* was inspired by *YAML*, but eschews its complexity. It has the 
following clear advantages over *YAML* as human readable and writable data file 
format:

- simple
- unambiguous (no implicit typing)
- data type does not change based on seemingly insignificant details (2, 2.0, 2.0.0, "2")
- syntax is insensitive to special characters within text
- safe, no risk of malicious code execution


Issues
------

Please ask questions or report problems on `Github 
<https://github.com/KenKundert/nestedtext/issues>`_.


Contributing
------------

This package contains a Python reference implementation of *NestedText*.
Implementation in many languages is required for *NestedText* to catch on widely.
If you like the format, please consider contributing additional implementations. 
