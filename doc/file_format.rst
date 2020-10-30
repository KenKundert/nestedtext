.. _nestedtext file format:

***********
File format
***********
The *NestedText* format follows a small number of simple rules. Here they are.

**Encoding**:

    A *NestedText* document encoded in UTF-8.

**Line breaks**:

    A *NestedText* document is partitioned into lines where the lines are split 
    by CR LF, CR, or LF where CR and LF are the ASCII carriage return and line 
    feed characters.  A single document may employ any or all of these ways of 
    splitting lines.

**Line types**:

    Each line in a *NestedText* document is assigned one of the following types: 
    *comment*, *blank*, *list-item*, *dict-item*, and *string-item*.  Any line 
    that does not fit one of these types is an error.

**Comments**:

    Comments are lines that have ``#`` as the first non-space character on the 
    line.  Comments are ignored.

**Blank lines**:

    Blank lines are lines that are empty or consist only of white space 
    characters (spaces or tabs).  Blank lines are also ignored.

**Line-type tags**:

    The remaining lines are identifying by which one of these ASCII characters 
    are found in an unquoted portion of the line: dash (``-``), colon (``:``), 
    or greater-than symbol (``>``) when followed immediately by a space or 
    newline.  Once the first of one of these pairs has been found in the 
    unquoted portion of the line, any subsequent occurrences of any of the 
    line-type tags are treated as simple text.  For example:

    .. code-block:: nestedtext

        - And the winner is: {winner}

    In this case the leading ``-␣`` determines the type of the line and the
    ``:␣`` is simply treated as part of the remaining text on the line.

**String items**:

    If the first non-space character on a line is a greater-than symbol followed 
    immediately by a space (``>␣``) or a newline, the line is a *string-item*.  
    Adjacent string-items with the same indentation level are combined into 
    a multiline string with their order being retained.  Any leading white space 
    that follows the space that follows the greater-than symbol is retained, as 
    is any trailing white space.

**List items**:

    If the first non-space character on a line is a dash followed immediately by 
    a space (``-␣``) or a newline, the line is a *list-item*.  Adjacent 
    list-items with the same indentation level are combined into a list with 
    their order being retained.  Each list-item has a single associated value.

**Dictionary items**:

    If the line is not a string-item or a list item and it contains a colon 
    followed by either a space (``:␣``) that does not fall within a quoted key 
    or is followed by a newline, the line is considered a *dict-item*.  Adjacent 
    dict-items with the same indentation level are combined into a dictionary 
    with their order being retained.  Each dict-item consists of a key, the tag 
    (colon), and a value.

    A key must be a string and it must not contain a newline.  The key must be 
    quoted if it:

    1. starts with a *list-item* or *string-item* tag,
    2. contains a *dict-item* tag,
    3. starts with a quote character, or
    4. has leading or trailing spaces or tabs.

    A key is quoted by delimiting it with matching single or double quote 
    characters, which are discarded.  Unlike traditional programming languages, 
    a quoted key delimited with single quote characters may contain additional 
    single quote characters. Similarly, a quoted key delimited with double quote 
    characters may contain additional double quote characters.  Also, backslash 
    is not used as an escape character; backslash has no special meaning 
    anywhere in *NestedText*.

    A quoted key starts with the leading quote character and ends when the 
    matching quote character is found along with a trailing colon (there may be 
    white space between the closing quote and the colon).
    A key is invalid if it contains two or more instances of a quote character 
    separated from ``:␣`` by zero or more space characters where the quote 
    character in one is a single quote and the quote character in another is the 
    double quote.  In this case the key cannot be quoted with either character 
    so that the separator from the key and value can be identified 
    unambiguously.

**Values**:

    The value associated with a list and dict item may take one of three forms.  

    If the line contains further text (characters after the dash-space or 
    colon-space), then the value is that text.

    If there is no further text on the line and the next line has greater 
    indentation, then the next line holds the value, which may be a list, 
    a dictionary, or a multiline string.

    Otherwise the value is empty; it is taken to be an empty string.

    String values may contain any printing UTF-8 character.

**Indentation**:

    An increase in the number of spaces in the indentation signifies the start 
    of a nested object.  Indentation must return to a prior level when the 
    nested object ends.

    Each level of indentation need not employ the same number of additional 
    spaces, though it is recommended that you choose either 2 or 4 spaces to 
    represent a level of nesting and you use that consistently throughout the 
    document.  However, this is not required. Any increase in the number of 
    spaces in the indentation represents an indent and a decrease to return to 
    a prior indentation represents a dedent.

    An indent may only follow a list-item or dict-item that does not have 
    a value on the same line.

    Only spaces are allowed in the indentation. Specifically, tabs are not 
    allowed.

**Empty document**:

    A document may be empty. A document is empty if it consists only of
    comments and blank lines.  An empty document corresponds to an empty value 
    of unknown type.

**Result**:

    When a document is converted from *NestedText* the result is a hierarchical 
    collection of dictionaries, lists and strings where all leaf values are 
    strings.  All dictionary keys are also strings.
