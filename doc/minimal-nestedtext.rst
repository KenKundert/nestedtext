.. _minimal nestedtext:

******************
Minimal NestedText
******************

*Minimal NestedText* is *NestedText* without support for multi-line keys and
inline dictionaries and lists.

*Minimal NestedText* is a subset of *NestedText* that foregoes some of the
complications of *NestedText*.  It sacrifices the completeness of *NestedText*
for an even simpler data file format that is still appropriate for
a surprisingly wide variety of applications, such as most configuration files.
The simplicity of *Minimal NestedText* makes it very easy to create readers and
writers.  Indeed, writing such functions is good programming exercise for people
new to recursion.

If you choose to create a *Minimal NestedText* reader or writer it is important
to code it in such a way as to discourage the creation *Minimal NestedText*
documents that are invalid *NestedText*.  Thus, your implementation should
disallow keys that start with ``:␣``, ``[`` or ``{``.  Also, please clearly
indicate that your implementation only supports *Minimal NestedText* to avoid 
any confusion.

Many of the examples given in this document conform to the *Minimal NestedText*
subset.  For convenience, here is another.  It is a configuration file:

.. code-block:: nestedtext

    default repository: home
    report style: tree
    compact format: {repo}: {size:{fmt}}.  Last back up: {last_create:ddd, MMM DD}.
    normal format: {host:<8} {user:<5} {config:<9} {size:<8.2b} {last_create:ddd, MMM DD}
    date format: D MMMM YYYY
    size format: .2b

    repositories:
        # only the composite repositories need be included
        home:
            children: rsync borgbase
        caches:
            children: cache cache@media cache@files
        servers:
            children:
                - root@dev~root
                - root@mail~root
                - root@media~root
                - root@web~root
        all:
            children: home caches servers

Finally, here is a short description of *Minimal NestedText* that you can use to 
describe to your users if you decide to use it for your application.

*Minimal NestedText*:
    `NestedText <https://nestedtext.org>`_ is a file format for holding 
    structured data.  It is intended to be easily entered, edited, or viewed by 
    people.  As such, the syntax is very simple and intuitive.

    It organizes the data into a nested collection of lists and name-value 
    pairs where the lowest level values are all strings.  For example, a simple 
    collection of name-value pairs represented using:

    .. code-block:: nestedtext

        Name 1: Value 1
        Name 2: Value 2

    The name and value are separated by a colon followed immediately by a space.  
    The characters that follow the space are the value.

    A simple list represented with:

    .. code-block:: nestedtext

        - Value 1
        - Value 2

    A list item is introduced by dash as the first non-blank character on a line 
    followed by a space.  The characters that follow the space are the value.

    Indentation is used to denote nesting.  In this case the colon or dash is 
    the last character on the line and is followed by an indented value.  The 
    value may be a collection of name-value pairs, a list, or a multi-line 
    string.  Every line of a multi-line string is introduced by a greater-than 
    symbol followed by a space or newline.

    .. code-block:: nestedtext

        Name 1: Value 1
        Name 2:
            Name 2a: Value 2a
            Name 2b: Value 2b
        Name 3:
            - Value 3a
            - Value 3b
        Name 4:
            > Value 4 line 1
            > Value 4 line 2

    Any line that starts with pound sign (`#`) as the first non-blank character 
    is ignored and so can be used to add comments.

    .. code-block:: nestedtext

        # this line is a comment
        Name: Value

    The name in a name-value pair is referred to as a key.  In *Minimal 
    NestedText* keys can not start with a space, an opening bracket (``[``) or 
    brace (``{``), or a dash followed by a space.  Nor can it contain a colon 
    followed by a space.  Other that that, there are no restrictions on the 
    characters that make up a key or value, and any characters given are taken 
    literally.
