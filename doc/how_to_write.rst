************
Basic syntax
************
A *NestedText* file is composed entirely of:

- Dictionaries_
- Lists_
- Strings_
- Comments_

The file must include either a dictionary or a list (i.e. the file cannot 
consist of just a string).

Dictionaries
============
A dictionary contains one or more dictionary items, each on its own line and in 
each the key and value separated by a colon.  The value is optional and the 
colon must be followed by a space or a newline to act as the key/value 
separator. So for example::

    name: Katheryn McDaniel
    phone: 1-210-555-5297
    email: KateMcD@aol.com

In this example both the keys and values are strings.  Keys are always strings, 
but the values may be strings, dictionaries, or lists.  Dictionaries can be 
nested to arbitrary depth::

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

Note that each level of nesting must be indented. It is highly recommended that 
each level of indentation be represented by a consistent number of spaces (with 
the suggested number being 4). However, it is not required. Any increase in the 
number of spaced in the indentation represents an indent and any decrease 
represents a dedent. Only spaces are allowed in the indentation. Specifically, 
tabs are not allowed in the indentation and they cannot follow a colon, dash, 
or greater to form a dictionary, list, or multi-line string tag, but can be 
used elsewhere.

Multi-line keys are not supported; a key must not contain a newline. In 
addition, all keys in the same dictionary must be unique. If a key contains 
leading or trailing spaces, a leading '- ' or '> ', or a ': ' anywhere in the 
key, you should quote the key.  Either single or double matching quotes may be 
used.  For example::

    '- key: ': value

Lists
=====
A list is represented as one or more list items, which are values that are 
introduced with a dash and end at the end of line. So for example::

    - Alabama
    - Alaska
    - Arizona
    - Arkansas

Any characters that occur after the '- ' are interpreted as a string.  To nest 
dictionaries or other lists within a list, put the nested data structure on a 
new line::

    -
        state: Alabama
        capital: Montgomery
    -
        state: Alaska
        capital: Juneau

The indentation rules for lists are the same as those for dictionaries.

Strings
=======
Strings can be either rest-of-line strings or multi-line.  Rest-of-line strings 
are simply the remaining characters on the line exclusive of any leading or 
trailing spaces.  Note that rest-of-line strings can contain any character 
(other than newline), because only the first ': ' or '- ' on a line is 
significant to *NestedText*::

    regex: [+-]?([0-9]*[.])?[0-9]+
    math: -b + sqrt(b**2 - 4*a*c)
    unicode: José and François

A multi-line string is a newline followed by one or more indented text lines 
where each line is introduced with '> '::

    name: Katheryn McDaniel
    address:
        > 138 Almond Street
        > Topika, Kansas 20697
    phone: 1-210-555-5297
    email: KateMcD@aol.com

You can include empty lines at the beginning or end of the string by using just 
the prefix.  Note that blank lines are always ignored---including before, 
after, and even within multi-line strings::

    Yogi Berra:
        >
        > The future ain’t what it used to be.
        >

Only the initial '> ' is removed from the final string.  This makes it trivial 
to specify strings with leading whitespace::

    greeting: Dearest Kathy:
    body:
        >     It has been such a long time. I am very much looking forward to
        > seeing both you and Margaret again.
    closing: See you soon.
    signature: -Rupert

In this example, the value of *body* is a multi-line string for which the first 
line is indented by 4 spaces.  The second line in *body* has no leading space.

Comments
========
Blank lines and comment lines are ignored. Blank lines are empty lines or lines 
that consist only of white space. Comment lines are lines where the first 
non-space character on the line is a `#`.

