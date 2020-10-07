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
| Version: 1.0.3
| Released: 2020-10-06
| Please post all questions, suggestions, and bug reports to
  `NestedText Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


*NestedText* is a file format for holding data that is to be entered, edited, or 
viewed by people.  It allows data to be organized into a nested collection of 
dictionaries, lists, and strings.  In this way it is similar to *JSON*, *YAML* 
and *TOML*, but without the complexity and risk of *YAML* and without the 
syntactic clutter of *JSON* and *TOML*.  *NestedText* is both simple and 
natural.  Only a small number of concepts and rules must be kept in mind when 
creating it.  It is easily created, modified, or viewed with a text editor and 
easily understood and used by both programmers and non-programmers.

*NestedText* is convenient for configuration files, address books, account 
information and the like.  Here is an example of a file that contains a few 
addresses::

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

    treasurer:
        -
            name: Fumiko Purvis
            address:
                > 3636 Buffalo Ave
                > Topeka, Kansas 20692
            phone: 1-268-555-0280
            email: fumiko.purvis@hotmail.com
            additional roles:
                - accounting task force
        -
            name: Merrill Eldridge
                # Fumiko's term is ending at the end of the year.
                # She will be replaced by Merrill.
            phone: 1-268-555-3602
            email: merrill.eldridge@yahoo.com

The format holds dictionaries (ordered collections of name/value pairs), lists 
(ordered collections of values) and strings (text) organized hierarchically to 
any depth.  Indentation is used to indicate the hierarchy of the data, and 
a simple natural syntax is used to distinguish the types of data in such 
a manner that it is not easily confused.  Specifically, lines that begin with 
a word or words followed by a colon are dictionary items; a dash introduces list 
items, and a leading greater-than symbol signifies a line in a multi-line 
string.  Dictionaries and lists are used for nesting and the leaf values are 
always simple text, hence the name, *NestedText*.  The top-level must be 
a dictionary.

*NestedText* is somewhat unique in that the leaf values are always strings. Of 
course the values start off as strings in the input file, but alternatives like 
JSON or YAML aggressively convert those values into the underlying data types 
such as integers, floats, and Booleans.  For example, a value like 2.10 would be 
converted to a floating point number. But making the decision to do so is based 
purely on the form of the value, not the context in which it is found.  This can 
lead to misinterpretations.  For example, assume that this value is the software 
version number two point ten. By converting it to a floating point number it 
becomes two point one, which is wrong. There are many possible versions of this 
basic issue. But there is also the inverse problem; values that should be 
converted to particular data types but are not recognized. For example, a value 
of $2.00 should be converted to a real number but would be a string instead.
There are simply too many values types for a general purpose solution that is 
only looking at the values themselves to be able to interpret all of them.  For 
example, 12/10/09 is likely a date, but is it in MM/DD/YY, YY/MM/DD or DD/MM/YY 
form?  The fact is, the value alone is often insufficient to reliably determine 
how to convert values into internal data types.  *NestedText* avoids these 
problems by leaving the values in their original form and allowing the decision 
to be made by the end application where more context is available to help guide 
the conversions.  If a price is expected for a value, then $2.00 would be 
checked and converted accordingly. Similarly, local conventions along with the 
fact that a date is expected for a particular value allows 12/10/09 to be 
correctly validated and converted.  This process of validation and conversion is 
referred to as applying a schema to the data. There are packages such as 
`Voluptuous <https://github.com/alecthomas/voluptuous>`_ and `Pydantic 
<https://pydantic-docs.helpmanual.io>`_ available that make this process easy 
and reliable.


The Zen of *NestedText*
-----------------------

*NestedText* aspires to be a simple dumb vessel that holds peoples' structured 
data, and to do so in a way that allows people to easily interact with that 
data.

The desire to be simple is an attempt to minimize the effort required to learn 
and use the language. Ideally people can understand it by looking at one or two 
examples and they can use it without without needing to remember any arcane 
rules and without relying on any of the knowledge that programmers accumulate 
through years of experience.  One source of simplicity is consistency.  As such, 
*NestedText* uses a small amount of rules that it applies with few exceptions.

The desire to be dumb means that it tries not to transform the data in any 
meaningful way. It allows you to recover the structure in your data without 
doing anything that might change the interpretation of the data. Rather, it 
tries to make it easy for you to interpret the data by managing the structure, 
which allows you to analyze it in small easy to interpret pieces without making 
any changes that would get in your way.


Alternatives
------------

There are no shortage of well established alternatives to *NestedText* for 
storing data in a human-readable text file. Probably the most obvious are `json 
<https://docs.python.org/3/library/json.html>`_ and `YAML 
<https://pyyaml.org/wiki/PyYAMLDocumentation>`_.  Both are primarily intended to 
be used as serialization languages. *NestedText* is not intended to be used as 
a serialization language, rather it is more suitable for configuration and hand 
generated and edited data files.  In these applications, both *JSON* and *YAML* 
have significant short comings.


JSON
""""

*JSON* is a subset of JavaScript suitable for holding data. Like *NestedText*, 
it consists of a hierarchical collection of dictionaries, lists, and strings, 
but also allows integers, floats, Booleans and nulls.  The problem with *JSON* 
for this application is that it is awkward.  With all those data types it must 
syntactically distinguish between them.  For example, in *JSON* 32 is an 
integer, 32.0 is the real version of 32, and "32" is the string version. These 
distinctions are not meaningful and can be confusing to non-programmers. In 
addition, in most datasets a majority of leaf values are strings and the 
required quotes adds substantial visual clutter.  *NestedText* avoids these 
issues by keeping all leaf values as unmodified strings; no need for quoting or 
escaping.  It is up to the application that employs *NestedText* as an input 
format to use context to check these strings and convert them to the right 
datatype.

*JSON* does not provide for multi-line strings and any special characters like 
newlines are encoded with escape codes, which can make strings long and 
difficult to interpret.  Also, dictionary and list items must be separated with 
commas, but a comma must not follow last item.  All of this results in *JSON* 
being a frustrating format for humans to read, enter or edit.

*NestedText* has the following clear advantages over *JSON* as human readable 
and writable data file format:

- text does not require quotes
- data is left in its original form
- comments
- multiline strings
- special characters without escaping them
- commas are not used to separate dictionary and list items


YAML
""""

*YAML* is considered by many to be a human friendly alternative to *JSON*, but 
over time it has accumulated too many data types and too many formats.  To 
distinguish between all the various types and formats, a complicated and 
non-intuitive set of rules developed.  *YAML* at first appears very appealing 
when used with simple examples, but things can quickly become complicated or 
provide unexpected results.  A reaction to this is the use of *YAML* subsets, 
such as `StrictYAML <https://hitchdev.com/strictyaml>`_.  However, the subsets 
still try to maintain compatibility with *YAML* and so inherit much of its 
complexity. For example, both *YAML* and *StrictYAML* support `nine different 
ways of writing multi-line strings 
<http://stackoverflow.com/a/21699210/660921>`_.

*YAML* avoids excessive quoting and supports comments and multiline strings, but 
like *JSON* it converts data to the underlying data types as appropriate, but 
unlike with *JSON*, the lack of quoting makes the format ambiguous, which means 
it has to guess at times, and small seemingly insignificant details can affect 
the result.

*NestedText* was inspired by *YAML*, but eschews its complexity. It has the 
following clear advantages over *YAML* as human readable and writable data file 
format:

- simple
- unambiguous (no implicit typing)
- data is left in its original form
- syntax is insensitive to special characters within text
- safe, no risk of malicious code execution


Issues
------

Please ask questions or report problems on `Github 
<https://github.com/KenKundert/nestedtext/issues>`_.


Contributing
------------

This package contains a Python reference implementation of *NestedText* and 
a test suite.  Implementation in many languages is required for *NestedText* to 
catch on widely.  If you like the format, please consider contributing 
additional implementations. 
