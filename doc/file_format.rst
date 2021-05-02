.. _nestedtext file format:

******************
Language reference
******************

The *NestedText* format follows a small number of simple rules. Here they are.


**Encoding**:

    A *NestedText* document is encoded in UTF-8.


**Line breaks**:

    A *NestedText* document is partitioned into lines where the lines are split 
    by CR LF, CR, or LF where CR and LF are the ASCII carriage return and line 
    feed characters.  A single document may employ any or all of these ways of 
    splitting lines.


**Line types**:

    Each line in a *NestedText* document is assigned one of the following types: 
    *comment*, *blank*, *list item*, *dict item*, *string item*, *key item* or 
    *inline*.  Any line that does not fit one of these types is an error.


**Comments**:

    Comments are lines that have ``#`` as the first non-white-space character on 
    the line.  Comments are ignored.


**Blank lines**:

    Blank lines are lines that are empty or consist only of white space 
    characters (spaces or tabs).  Blank lines are also ignored.


**Line-type tags**:

    Most remaining lines are identifying by the presence of tags, where a tag is
    the first dash (``-``), colon (``:``), or greater-than symbol (``>``) on 
    a line when followed immediately by a space or line break.

    Dashes and greater-than symbols only introduce tags when they are the first 
    non-space character on a line, but colon tags need not start the line.

    The first (left-most) tag on a line determines the line type.  Once the 
    first tag has been found on the line, any subsequent occurrences of any of 
    the line-type tags are treated as simple text.  For example:

    .. code-block:: nestedtext

        - And the winner is: {winner}

    In this case the leading ``-␣`` determines the type of the line and the
    ``:␣`` is simply treated as part of the remaining text on the line.


**String items**:

    If the first non-space character on a line is a greater-than symbol followed 
    immediately by a space (``>␣``) or a line break, the line is a *string 
    item*.  After comments and blank lines have been removed, adjacent string 
    items with the same indentation level are combined in order into 
    a multi-line string.  The string value is the multi-line string with the 
    tags removed. Any leading white space that follows the tag is retained, as 
    is any trailing white space and all newlines except the last.

    String values may contain any printing UTF-8 character.


**List items**:

    If the first non-space character on a line is a dash followed immediately by 
    a space (``-␣``) or a line break, the line is a *list item*.  Adjacent list 
    items with the same indentation level are combined in order into a list 
    value.  Each list item has a tag and a value.  The tag is only used to 
    determine the type of the line and is discarded leaving the value.  The 
    value takes one of three forms.

    1. If the line contains further text (characters after the dash-space), then 
       the value is that text.  The text ends at the line break and may contain 
       any other printing UTF-8 character.

    2. If there is no further text on the line and the next line has greater 
       indentation, then the next line holds the value, which may be a list, 
       a dictionary, or a multi-line string.

    3. Otherwise the value is empty; it is taken to be an empty string.


**Key items**:

    If the first non-space character on a line is a colon followed immediately 
    by a space (``:␣``) or a line break, the line is a *key item*.  After 
    comments and blank lines have been removed, adjacent key items with the same 
    indentation level are combined in order into a multi-line key.  The key 
    value is the multi-line string with the tags removed. Any leading white 
    space that follows the tag is retained, as is any trailing white space and 
    all newlines except the last.

    Key values may contain any printing UTF-8 character.

    An indented value must follow a multi-line key.  The indented value may be 
    either a multi-line string, a list or a dictionary.  The combination of the 
    key item and its value forms a *dict item*.


**Dictionary items**:

    Dictionary items take two possible forms.

    The first is a *dict item with inline key*.  In this case the line does not 
    start with a tag, but instead contains an interior dict tag: a colon 
    followed by either a space (``:␣``) or a line break where the colon is not 
    the first non-space character on the line.  The dict item consists of a key, 
    the tag, and a value.  Any space between the key and the tag is ignored.

    The inline key precedes the tag. It must be a string and must not:

    1. contain a line break character.
    2. start with a list item, string item or key item tag,
    3. contain a dict item tag, or
    4. contain leading or trailing spaces (any spaces that follow the key are 
       ignored).

    The tag is only used to determine the type of the line and is discarded 
    leaving the value, which follows the tag.  The value takes one of three 
    forms.

    1. If the line contains further text (characters after the colon-space), 
       then the value is that text.  The text ends at the line break and may 
       contain any other printing UTF-8 character.

    2. If there is no further text on the line and the next line has greater 
       indentation, then the next line holds the value, which may be a list, 
       a dictionary, or a multi-line string.

    3. Otherwise the value is empty; it is taken to be an empty string.

    The second form of *dict item* is the *dict item with multi-line key*.  It 
    consists of a multi-line key value followed by an indented multi-line 
    string, list, or dictionary.

    Adjacent dict items of either form with the same indentation level are 
    combined in order into a dictionary value.


**Inline Lists and Dictionaries**:

    If the first character on a line is either a left bracket (``[``) or a left 
    brace (``{``) the line is an *inline structure*.  A bracket introduces an 
    *inline list* and a brace introduces an *inline dictionary*.

    An inline list starts with an open bracket (``[``), ends with a matching 
    closed bracket (``]``), contains inline values separated by commas (``,``), 
    and is contained on a single line.  The values may be inline strings, inline 
    lists, and inline dictionaries.

    An inline dictionary starts with an open brace (``{``), ends with a matching 
    closed brace (``}``), contains inline dictionary items separated by commas 
    (``,``), and is contained on a single line.  An inline dictionary item is 
    a key and value separated by a colon (``:``).  A space need not follow the 
    colon and any spaces that do follow the colon are ignored. The keys are 
    inline strings and the values may be inline strings, inline lists, and 
    inline dictionaries.

    Both inline lists and dictionaries may be empty, and represent the only way 
    to represent empty lists or empty dictionaries in *NestedText*.

    *Inline strings* are the string values specified in inline dictionaries and 
    lists.  They are somewhat constrained in the characters that they may 
    contain; nothing that might be confused with syntax characters used by the 
    inline list or dictionary that contains it.  Specifically, inline strings 
    may not contain newlines or any of the following characters: ``[``, ``]``, 
    ``{``, ``}``, or ``,``.  In addition, inline strings that are contained in 
    inline dictionaries may not contain ``:``.  Leading and trailing white space 
    are ignored with inline strings.

    Empty inline strings must be followed by a comma to be recognized.  For 
    example, ``[]`` is an empty list and ``[,]`` is a list that contains 
    a single empty string.


**Indentation**:

    There is no indentation on the top-level object.

    An increase in the number of spaces in the indentation signifies the start 
    of a nested object.  Indentation must return to a prior level when the 
    nested object ends.

    Each level of indentation need not employ the same number of additional 
    spaces, though it is recommended that you choose either 2 or 4 spaces to 
    represent a level of nesting and you use that consistently throughout the 
    document.  However, this is not required. Any increase in the number of 
    spaces in the indentation represents an indent and a decrease to return to 
    a prior indentation represents a dedent.

    An indented value may only follow a list item or dict item that does not 
    have a value on the same line.  An indented value must follow a key item.

    Only ASCII spaces are allowed in the indentation. Specifically, tabs and the 
    various Unicode spaces are not allowed.


**Escaping and Quoting**:

    There is no escaping or quoting in *NestedText*. Once the line has been 
    identified by its tag, and the tag is removed, the remaining text is taken 
    literally.


**Empty document**:

    A document may be empty. A document is empty if it consists only of
    comments and blank lines.  An empty document corresponds to an empty value 
    of unknown type.


**Result**:

    When a document is converted from *NestedText* the result is a hierarchical 
    collection of dictionaries, lists and strings.  All dictionary keys are 
    strings.
