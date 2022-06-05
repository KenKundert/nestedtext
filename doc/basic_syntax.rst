*********************
Language introduction
*********************

This is a overview of the syntax of a *NestedText* document, which consists of 
a :ref:`nested collection <nesting>` of :ref:`dictionaries <dictionaries>`, 
:ref:`lists <lists>`, and :ref:`strings <strings>` where indentation is used to 
indicate nesting.  All leaf values must be simple text or empty. You can find 
more specifics :ref:`in the next section <nestedtext file format>`.


.. _dictionaries:

Dictionaries
============

A dictionary is an ordered collection of key value pairs:

.. code-block:: nestedtext

    key 1: value 1
    key 2: value 2
    key 3: value 3

A dictionary item is a single key value pair.  A dictionary is all adjacent 
dictionary items in which the keys all begin at the same level of indentation.
There are several different ways to specify dictionaries.

In the first form, the key and value are separated by a dictionary tag, which is 
a colon followed by a space or newline (``:␣`` or  ``:↵``).  The key must be 
a string and must not start with a ``-␣``, ``>␣``, ``:␣``, ``[``, ``{``, ``#``, 
or white space character; or contain newline characters or the ``:␣`` character 
sequence.  Any spaces between the key and the tag are ignored.

The value of this dictionary item may be a rest-of-line string, a multiline 
string, a list, or a dictionary. If it is a rest-of-line string, it contains all 
characters following the tag that separates the key from the value (``:␣``).  
For all other values, the rest of the line must be empty, with the value given 
on the next line, which must be further indented.


.. code-block:: nestedtext

    key 1: value 1
    key 2:
    key 3:
        - value 3a
        - value 3b
    key 4:
        key 4a: value 4a
        key 4b: value 4b
    key 5:
        > first line of value 5
        > second line of value 5

Which is equivalent to the following JSON code:

.. code-block:: json

    {
        "key 1": "value 1",
        "key 2": "",
        "key 3": [
            "value 3a",
            "value 3b"
        ],
        "key 4": {
            "key 4a": "value 4a",
            "key 4b": "value 4b"
        },
        "key 5": "first line of value 5\nsecond line of value 5"
    }

A second less common form of a dictionary item employs multiline keys.  In this 
case there are no limitations on the key other than it being a string.  Each 
line of a multiline key is introduced with a colon (``:``) followed by a space 
or newline.  The key is all adjacent lines at the same level that start with 
a colon tag with the tags removed but leading and trailing white space retained, 
including all newlines except the last.

This form of dictionary does not allow rest-of-line string values; you would use 
a multiline string value instead:

.. code-block:: nestedtext

    : key 1
    :     the first key
        > value 1
    : key 2: the second key
        - value 2a
        - value 2b

A dictionary may consist of dictionary items of either form.

The final form of a dictionary is the inline dictionary.  This is a compact form 
where all the dictionary items are given on the same line.  There is a bit of 
syntax that defines inline dictionaries, so the keys and values are constrained 
to avoid ambiguities in the syntax.  An inline dictionary starts with an opening 
brace (``{``), ends with a matching closing brace (``}``), and contains inline 
dictionary items separated by commas (``,``). An inline dictionary item is a key 
and value separated by a colon (``:``).  A space need not follow the colon.  The 
keys are inline strings and the values may be inline strings, inline lists, and 
inline dictionaries.  An empty dictionary is represented with ``{}`` (there can 
be no space between the opening and closing braces).  Leading and trailing 
spaces are stripped from keys and string values within inline dictionaries.

For example:

.. code-block:: nestedtext

    {key 1: value 1, key 2: value 2, key 3: value 3}

.. code-block:: nestedtext

    {key 1: value 1, key 2: [value 2a, value 2b], key 3: {key 3a: value 3a, key 3b: value 3b}}


.. _lists:

Lists
=====

A list is an ordered collection of values:

.. code-block:: nestedtext

    - value 1
    - value 2
    - value 3

A list item is introduced with a list tag: a dash followed by a space or 
a newline at the start of a line (``-␣`` or ``-↵``).  All adjacent list items at 
the same level of indentation form the list.

The value of a list item may be a rest-of-line string, a multiline string, 
a list, or a dictionary. If it is a rest-of-line string, it contains all 
characters that follow the tag that introduces the list item.  For all other 
values, the rest of the line must be empty, with the value given on the next 
line, which must be further indented.

.. code-block:: nestedtext

    - value 1
    -
    -
        - value 3a
        - value 3b
    -
        key 4a: value 4a
        key 4b: value 4b
    -
        > first line of value 5
        > second line of value 5

Which is equivalent to the following JSON code:

.. code-block:: json

    [
        "value 1",
        "",
        [
            "value 3a",
            "value 3b"
        ],
        {
            "key 4a": "value 4a",
            "key 4b": "value 4b"
        },
        "first line of value 5\nsecond line of value 5"
    ]

Another form of a list is the inline list.  This is a compact form where all the 
list items are given on the same line.  There is a bit of syntax that defines 
the list, so the values are constrained to avoid ambiguities in the syntax.  An 
inline list starts with an opening bracket (``[``), ends with a matching closing 
bracket (``]``), and contains inline values separated by commas.  The values may 
be inline strings, inline lists, and inline dictionaries.  An empty list is 
represented by ``[]`` (there should be no space between the opening and closing 
brackets).  Leading and trailing spaces are stripped from string values within 
inline lists.

For example:

.. code-block:: nestedtext

    [value 1, value 2, value 3]

.. code-block:: nestedtext

    [value 1, [value 2a, value 2b], {key 3a: value 3a, key 3b: value 3b}]

``[ ]`` is not treated as an empty list as there is space between the brackets, 
rather this represents a list with a single empty string value.  The contents of 
the brackets, which consists only of white space, is stripped of its padding, 
leaving an empty string.


.. _strings:

Strings
=======

There are three types of strings: rest-of-line strings, multiline strings, and 
inline strings.  Rest-of-line strings are simply all the characters on a line 
that follow a list tag (``-␣``) or dictionary tag (``:␣``), including any 
leading or trailing white space.  They can contain any character other than 
a newline.  The content of the rest-of-line string starts after the first space 
that follows the dash or colon of the tag:

.. code-block:: nestedtext

    code   : input signed [7:0] level
    regex  : [+-]?([0-9]*[.])?[0-9]+\s*\w*
    math   : $x = \frac{{-b \pm \sqrt {b^2 - 4ac}}}{2a}$
    unicode: José and François

Multi-line strings are all adjacent lines that are prefixed with a string tag; 
the greater-than symbol followed by a space or a newline (``>␣`` or ``>↵``).  
The content of each line starts after the first space that follows the 
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
    >

The multiline string is all adjacent lines that start with a string tag with the 
tags removed and the lines joined together with newline characters inserted 
between each line.  Except for the space that follows the ``>`` in the tag,
white space from both the beginning and the end of each line is retained, along 
with all newlines except the last.

Inline strings are the string values specified in inline dictionaries and lists.  
They are somewhat constrained in the characters that they may contain; nothing 
that might be confused with the syntax characters used by the inline list or 
dictionary that contains it.  Specifically, inline strings may not contain 
newlines or any of the following characters: ``[``, ``]``, ``{``, ``}``, or 
``,``.  In addition, inline strings that are contained in inline dictionaries 
may not contain ``:``.  Leading and trailing white space are ignored with inline 
strings.


.. _comments:

Comments
========

Lines that begin with a hash as the first non-white-space character, or lines 
that are empty or consist only of white space are comment lines and are ignored.  
Indentation is not significant on comment lines.

.. code-block:: nestedtext

    # this line is ignored

    # this line is also ignored, as is the blank line above.

Comment lines are ignored when determining whether adjacent lines belong to the 
same dictionary, list, or string.  For example, the following represents one 
multiline string:

.. code-block:: nestedtext

    > this is the first line of a multiline string
    # this line is ignored
    > this is the second line of the multiline string


.. _nesting:

Nesting
=======

A value for a dictionary or list item may be a rest-of-line string or it may be 
a nested dictionary, list, multiline string, or inline dictionary or list.  
Indentation is used to indicate nesting.  Indentation increases to indicate the 
beginning of a new nested object, and indentation returns to a prior level to 
indicate its end.  In this way, data can be nested to an arbitrary depth:

.. code-block:: nestedtext

    # Contact information for our officers

    Katheryn McDaniel:
        position: president
        address:
            > 138 Almond Street
            > Topeka, Kansas 20697
        phone:
            cell: 1-210-555-5297
            work: 1-210-555-3423
            home: 1-210-555-8470
                # Katheryn prefers that we always call her on her cell phone.
        email: KateMcD@aol.com
        kids:
            - Joanie
            - Terrance

    Margaret Hodge:
        position: vice president
        address:
            > 2586 Marigold Lane
            > Topeka, Kansas 20697
        phone:
            {cell: 1-470-555-0398, home: 1-470-555-7570}
        email: margaret.hodge@ku.edu
        kids:
            [Arnie, Zach, Maggie]

It is recommended that each level of indentation be represented by a consistent 
number of spaces (with the suggested number being 2 or 4). However, it is not 
required. Any increase in the number of spaces in the indentation represents an 
indent and the number of spaces need only be consistent over the length of the 
nested object.

The data can be nested arbitrarily deeply.


.. _nestedtext_files:

NestedText Files
================

*NestedText* files should be encoded with `UTF-8 
<https://en.wikipedia.org/wiki/UTF-8>`_ and should end with a newline.  The 
top-level object must not be indented.

The name used for the file is arbitrary but it is tradition to use a
.nt suffix.  If you also wish to further distinguish the file type
by giving the schema, it is recommended that you use two suffixes,
with the suffix that specifies the schema given first and .nt given
last. For example: officers.addr.nt.
