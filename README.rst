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
| Version: 1.0.2
| Released: 2020-10-05
| Please post all questions, suggestions, and bug reports to
  `NestedText Github <https://github.com/KenKundert/nestedtext/issues>`_.
|


*NestedText* is a file format for holding data that is to be entered, edited, or 
viewed by people.  It allows data to be organized into a nested collection of 
dictionaries, lists, and strings.  In this way it is similar to *JSON* and 
*YAML*, but without the complexity and risk of *YAML* and without the syntactic 
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
        name: Fumiko Purvis
            # Fumiko's term is ending at the end of the year.
            # She will be replaced by Merrill Eldridge.
        address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
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
items, and a leading greater-than symbol signifies a line in a multi-line 
string.  Dictionaries and lists are used for nesting and the leaf values are 
always strings, hence the name, *NestedText*.

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
of $2.00 should be converted to a real number but would likely not be.  There 
are simply too many values types for a general purpose solution that is only 
looking at the values themselves to be able to interpret all of them.  For 
example, 12/10/09 is likely a date, but is it in MM/DD/YY, YY/MM/DD or DD/MM/YY 
form?  The fact is, the value alone is often insufficient to reliably determine 
how to convert values into internal data types.  *NestedText* avoids these 
problems by leaving the values in their original form and allowing the decision 
to be made by the end application where more context is available to help guide 
the conversions. For example, if a price is expected for a value, then $2.00 
would be checked and converted accordingly. Similarly, local conventions along 
with the fact that a date is expected for a particular value allows 12/10/09 to 
be correctly validated and converted.  This process of validation and conversion 
is referred to as applying a schema to the data. There are packages such as 
`Voluptuous <https://github.com/alecthomas/voluptuous>`_ and `Pydantic 
<https://pydantic-docs.helpmanual.io>`_ available that make this process easy 
and reliable.


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
difficult to interpret.  Finally, dictionary and list items must be separated 
with commas, but a comma must not follow last item.  All of this results in 
*JSON* being a frustrating format for humans to read, enter or edit.

*NestedText* has the following clear advantages over *JSON* as human readable 
and writable data file format:

- text does not require quotes or escape codes
- data type does not change based on seemingly insignificant details (32, 32.0, "32")
- comments
- multiline strings
- special characters without escaping them
- commas are not used to separate dictionary and list items


YAML
""""

*YAML* is considered by many to be a human friendly alternative to *JSON*, but 
over time it has accumulated too many data types and too many formats.  To 
distinguish between all the various types and formats, a complicated and 
non-intuitive set of rules developed.  For example, 2 is interpreted as an 
integer, 2.0 as a real number, while $2.00, 2.0km, 2.0.0 and "2" are strings.  
*YAML* at first appears very appealing when used with simple examples, but 
things can quickly become complicated or provide unexpected results.  A reaction 
to this is the use of *YAML* subsets, such as `StrictYAML 
<https://hitchdev.com/strictyaml>`_.  However, the subsets still try to maintain 
compatibility with *YAML* and so inherit much of its complexity. For example, 
both *YAML* and *StrictYAML* support the `nine different ways to write 
multi-line strings in YAML <http://stackoverflow.com/a/21699210/660921>`_.

*YAML* avoids the problems that result from *JSON* needing to unambiguously 
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
*Enrolled* should be a Boolean and knows how to convert 'NO' to *False*.  It 
also knows to check that the value of *Country Code* is a known country code. 
The same is not possible with *YAML* because the *Country Code* value has been 
transformed and because there are many possible strings that map to *False* 
(`n`, `no`, `false`, `off`; etc.).

This is one example of the many possible problems that stem from implicit 
typing.  In fact, many people make it a habit to add quotes to all values simply 
to avoid the ambiguities, a practice that makes *YAML* feel more like *JSON*.

To be fair, the implicit typing is not innate to *YAML*.  One always employs 
a loader with *YAML*, and it is the loader that implements the implicit  typing.  
It is free to do so as it wishes. Some implement the implicit typing described 
above, some implement less, some implement none at all. For example, *PyYAML*'s  
*BaseLoader* leaves everything as a string, just like *StrictYAML* and 
*NestedText*.

*NestedText* was inspired by *YAML*, but eschews its complexity. It has the 
following clear advantages over *YAML* as human readable and writable data file 
format:

- simple
- unambiguous (no implicit typing)
- data type does not change based on seemingly insignificant details (2, 2.0, 2.0km, $2.00, 2.0.0, "2")
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
