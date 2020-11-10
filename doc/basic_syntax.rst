************
Basic syntax
************

This is a overview of the syntax of a *NestedText* document, which consists of 
a :ref:`nested collection <nesting>` of :ref:`dictionaries <dictionaries>`, 
:ref:`lists <lists>`, and :ref:`strings <strings>`.  All leaf values must be 
simple text. You can find more specifics :ref:`later on <nestedtext file 
format>`.


.. _dictionaries:

Dictionaries
============

A dictionary is an ordered collection of name/value pairs:

.. code-block:: nestedtext

    name 1: value 1
    name 2: value 2

A dictionary item is introduced by a key followed by a colon at the start of 
a line.  The key is a string and must be quoted if it contains characters that 
could be misinterpreted.  You quote it using either single or double quotes 
(both have the same meaning).  Keys are the only place in *NestedText* where 
quoting is used to protect text.

The value of a dictionary item may be a rest-of-line string, a multiline string, 
a list, or a dictionary. If it is a rest-of-line string, it contains all 
characters following the ":␣" that separates the key from the value.  For all 
other values, the rest of the line must be empty, with the value given on the 
next line, which must be further indented.

A dictionary is all adjacent dictionary items at the same indentation level.


.. _lists:

Lists
=====

A list is an ordered collection of values:

.. code-block:: nestedtext

    - value 1
    - value 2

A list item is introduced with a dash at the start of a line.  The value of 
a list item may be a rest-of-line string, a multiline string, a list, or 
a dictionary. If it is a rest-of-line string, it contains all characters that 
follow the "-␣" that introduces the list item.  For all other values, the rest 
of the line must be empty, with the value given on the next line, which must be 
further indented.

A list is all adjacent list items at the same indentation level.


.. _strings:

Strings
=======

There are two types of strings: rest-of-line strings and multiline strings.  
Rest-of-line strings are simply all the remaining characters on the line, 
including any leading or trailing white space.  They can contain any character 
other than newline:

.. code-block:: nestedtext

    code   : input signed [7:0] level
    regex  : [+-]?([0-9]*[.])?[0-9]+\s*\w*
    math   : -b + sqrt(b**2 - 4*a*c)
    unicode: José and François

Multi-line strings are specified on lines prefixed with the greater-than 
symbol.  The content of each line starts after the first space that follows the 
greater-than symbol:

.. code-block:: nestedtext

    >     This is the first line of a multiline string, it is indented.
    > This is the second line, it is not indented.

You can include empty lines in the string simply by specifying the greater-than 
symbol alone on a line:

.. code-block:: nestedtext

    >
    > “The worth of a man to his society can be measured by the contribution he
    >  makes to it — less the cost of sustaining himself and his mistakes in it.”
    >
    >                                                — Erik Jonsson

The multiline string is all adjacent lines that start with a greater than tag 
with the tags removed and the lines joined together with newline characters 
inserted between each line.  Except for the space that separates the tag from 
the text, white space from both the beginning and the end of each line is 
retained.


.. _comments:

Comments
========

Lines that begin with a hash as the first non-space character, or lines that are 
empty or consist only of spaces and tabs are comment lines and are ignored.  
Indentation is not significant on comment lines.

.. code-block:: nestedtext

    # this line is ignored


.. _nesting:

Nesting
=======

A value for a dictionary or list item may be a rest-of-line string or it may be 
a nested dictionary, list or a multiline string.  Indentation is used to 
indicate nesting.  Indentation increases to indicate the beginning of a new 
nested object, and indentation returns to a prior level to indicate its end.  In 
this way, data can be nested to an arbitrary depth:

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
        kids:
            - Joanie
            - Terrance

    vice president:
        name: Margaret Hodge
        address:
            > 2586 Marigold Land
            > Topeka, Kansas 20697
        phone: 1-470-555-0398
        email: margaret.hodge@ku.edu
        kids:
            - Arnie
            - Zach
            - Maggie

It is recommended that each level of indentation be represented by a consistent 
number of spaces (with the suggested number being 2 or 4). However, it is not 
required. Any increase in the number of spaces in the indentation represents an 
indent and the number of spaces need only be consistent over the length of the 
nested object.

The data can be nested arbitrarily deeply using dictionaries and lists, but the 
leaf values, the values that are nested most deeply, must all be strings.


.. _nestedtext_files:

NestedText Files
================

*NestedText* files should be encoded with `UTF-8 
<https://en.wikipedia.org/wiki/UTF-8>`_.

The name used for the file is arbitrary but it is tradition to use a
.nt suffix.  If you also wish to further distinguish the file type
by giving the schema, it is recommended that you use two suffixes,
with the suffix that specifies the schema given first and .nt given
last. For example: officers.addr.nt.
