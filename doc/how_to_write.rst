************
Basic syntax
************

This is a overview of the syntax of a *NestedText* document, which consists of 
a :ref:`nested collection <nesting>` of :ref:`dictionaries <dictionaries>`, 
:ref:`lists <lists>`, and :ref:`strings <strings>`.  You can find more specifics 
:ref:`later on <nestedtext file format>`.


.. _dictionaries:

Dictionaries
============

    A dictionary is a collection of name/value pairs::

        name 1: value 1
        name 2: value 2
        ...

    A dictionary item is introduced by a key (the name) and a colon at the start 
    of a line.  Anything that follows the space after the colon is the value and 
    is treated as a string.

    The key is a string and must be quoted if it contains characters that could 
    be misinterpreted.

    A dictionary is all adjacent dictionary items at the same indentation 
    level.


.. _lists:

Lists
=====

    A list is a collection of simple values::

        - value 1
        - value 2
        ...

    A list item is introduced with a dash at the start of a line.  Anything that 
    follows the space after the dash is the value and is treated as a string.

    A list is all adjacent list items at the same indentation level.


.. _strings:

Strings
=======

    The values described in the last two sections are all rest-of-line strings; 
    they end at the end of the line.  Rest-of-line strings are simply all the 
    remaining characters on the line.  They can contain any character other than 
    newline::

        regex: [+-]?([0-9]*[.])?[0-9]+
        math: -b + sqrt(b**2 - 4*a*c)
        unicode: José and François

    It is also possible to specify strings that are alone on a line and they can 
    be combined to form multiline strings. To do so, precede the line with 
    a greater-than symbol::

        >     This is the first line of a multiline string, it is indented.
        > This is the second line, it is not indented.

    The content of each line starts after the first space that follows the 
    greater-than symbol.

    You can include empty lines in the string simply by specifying the 
    greater-than symbol alone on a line::

        >
        > The future ain’t what it used to be.
        >
        >                    - Yogi Berra
        >


.. _comments:

Comments
========

    Lines that begin with a hash as the first non-space character, or lines that 
    are empty or consist only of spaces and tabs are ignored.  Indentation is 
    not significant on comment lines.

    ::

        # this line is ignored


.. _nesting:

Nesting
=======

A value for a dictionary or list item may be a rest-of-line string as shown 
above, or it may be a nested dictionary, list or a multiline string.  
Indentation is used to indicate nesting (or composition).  Indentation increases 
to indicate the beginning of a new nested object, and indentation returns to 
a prior level to indicate its end.  In this way, data can be nested to an 
arbitrary depth::

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
            > 2586 Marigold Land
            > Topika, Kansas 20697
        phone: 1-470-555-0398
        email: margaret.hodge@uk.edu
        kids:
            - Arnie
            - Zach
            - Maggie

It is recommended that each level of indentation be represented by a consistent 
number of spaces (with the suggested number being 2 or 4). However, it is not 
required. Any increase in the number of spaces in the indentation represents an 
indent and and the number of spaces need only be consistent over the length of 
the nested object.

The data can be nested arbitrarily deeply using dictionaries and lists, but the 
leaf values, the values that are nested most deeply, must all be strings.
