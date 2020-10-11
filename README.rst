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
| Version: 1.1.0
| Released: 2020-10-11
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
a manner that it is not easily confused.  Specifically, lines that begin with a 
word (or words) followed by a colon are dictionary items, lines that begin with 
a dash are list items, and lines that begin with a greater-than sign are part of 
a multiline string.  Dictionaries and lists can be nested arbitrarily, and the 
leaf values are always text, hence the name *NestedText*.

*NestedText* is somewhat unique in that the leaf values are always strings. Of 
course the values start off as strings in the input file, but alternatives like 
*YAML* or *TOML* aggressively convert those values into the underlying data 
types such as integers, floats, and Booleans.  For example, a value like 2.10 
would be converted to a floating point number. But making the decision to do so 
is based purely on the form of the value, not the context in which it is found.  
This can lead to misinterpretations.  For example, assume that this value is 
the software version number two point ten. By converting it to a floating point 
number it becomes two point one, which is wrong. There are many possible 
versions of this basic issue. But there is also the inverse problem; values 
that should be converted to particular data types but are not recognized. For 
example, a value of $2.00 should be converted to a real number but would remain 
a string instead.  There are simply too many values types for a general purpose 
solution that is only looking at the values themselves to be able to interpret 
all of them.  For example, 12/10/09 is likely a date, but is it in MM/DD/YY, 
YY/MM/DD or DD/MM/YY form?  The fact is, the value alone is often insufficient 
to reliably determine how to convert values into internal data types.  
*NestedText* avoids these problems by leaving the values in their original form 
and allowing the decision to be made by the end application where more context 
is available to help guide the conversions.  If a price is expected for a value, 
then $2.00 would be checked and converted accordingly. Similarly, local 
conventions along with the fact that a date is expected for a particular value 
allows 12/10/09 to be correctly validated and converted.  This process of 
validation and conversion is referred to as applying a schema to the data.  
There are packages such as `Pydantic <https://pydantic-docs.helpmanual.io>`_ and 
`Voluptuous <https://github.com/alecthomas/voluptuous>`_ available that make 
this process easy and reliable.


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
