.. _nestedtext file format:

******************
Language reference
******************

The *NestedText* format follows a small number of simple rules. Here they are.


**Encoding**:

    A *NestedText* document is encoded in UTF-8 and may contain any printing 
    UTF-8 character.


**Line breaks**:

    A *NestedText* document is partitioned into lines where the lines are split 
    by CR LF, CR, or LF where CR and LF are the ASCII carriage return and line 
    feed characters.  A single document may employ any or all of these ways of 
    splitting lines.


**Line types**:

    Each line in a *NestedText* document is assigned one of the following types: 
    *comment*, *blank*, *list item*, *dictionary item*, *string item*, *key 
    item* or *inline*.  Any line that does not fit one of these types is an 
    error.


**Blank lines**:

    Blank lines are lines that are empty or consist only of ASCII space 
    characters.  Blank lines are ignored.


**Line-type tags**:

    Most remaining lines are identified by the presence of tags, where a tag is:

    #.  the first dash (``-``), colon (``:``), or greater-than symbol (``>``) on 
        a line when followed immediately by an ASCII space or line break;
    #.  or a hash {``#``), left bracket (``[``), or left brace (``{``) as the 
        first non-ASCII-space character on a line.

    These symbols only introduce tags when they are the first non-ASCII-space 
    character on a line, except for the colon (``:``) which introduces 
    a dictionary item with an inline key midway through a line.

    The first (left-most) tag on a line determines the line type.  Once the 
    first tag has been found on the line, any subsequent occurrences of any of 
    the line-type tags are treated as simple text.  For example:

    .. code-block:: nestedtext

        - And the winner is: {winner}

    In this case the leading ``-␣`` determines the type of the line and the
    ``:␣`` is simply treated as part of the remaining text on the line.


**Comments**:

    Comments are lines that have ``#`` as the first non-ASCII-space character on 
    the line.  Comments are ignored.


**String items**:

    If the first non-space character on a line is a greater-than symbol followed 
    immediately by an ASCII space (``>␣``) or a line break, the line is a *string 
    item*.  After comments and blank lines have been removed, adjacent string 
    items with the same indentation level are combined in order into 
    a multiline string.  The string value is the multiline string with the 
    tags removed.  Any leading white space that follows the tag is retained, as 
    is any trailing white space. The last newline is removed and all other 
    newlines are converted to the default line terminator for the current 
    operating system.

    String values may contain any printing UTF-8 character.


**List items**:

    If the first non-space character on a line is a dash followed immediately by 
    an ASCII space (``-␣``) or a line break, the line is a *list item*.  
    Adjacent list items with the same indentation level are combined in order 
    into a list.  Each list item has a tag and a value.  The tag is only used to 
    determine the type of the line and is discarded leaving the value.  The 
    value takes one of three forms.

    #. If the line contains further text (characters after the dash-space), then 
       the value is that text.  The text ends at the line break and may contain 
       any other printing UTF-8 character.

    #. If there is no further text on the line and the next line has greater 
       indentation, then the next line holds the value, which may be a list, 
       a dictionary, or a multiline string.

    #. Otherwise the value is empty; it is taken to be an empty string.


**Key items**:

    If the first non-ASCII-space character on a line is a colon followed 
    immediately by an ASCII space (``:␣``) or a line break, the line is a *key 
    item*.  After comments and blank lines have been removed, adjacent key items 
    with the same indentation level are combined in order into a multiline key.  
    The key itself is the multiline string with the tags removed.  Any leading 
    white space that follows the tag is retained, as is any trailing white 
    space. The last newline is removed and all other newlines are converted to 
    the default line terminator for the current operating system.

    Key values may contain any printing UTF-8 character.

    An indented value must follow a multiline key.  The indented value may be 
    either a multiline string, a list or a dictionary.  The combination of the 
    key item and its value forms a *dictionary item*.


**Dictionary items**:

    Dictionary items take two possible forms.

    The first is a *dictionary item with inline key*.  In this case the line 
    starts with a key followed by a dictionary tag: a colon followed by either 
    an ASCII space (``:␣``) or a newline.  The dictionary item consists of the 
    key, the tag, and the trailing value.  Any white space between the key and 
    the tag is ignored.

    The inline key precedes the tag. It must be a non-empty string and must not:

    #. contain a line break character.
    #. start with a list item, string item or key item tag,
    #. start with ``[`` or ``{``,
    #. contain a dictionary item tag, or
    #. contain Unicode leading spaces
       (any Unicode spaces that follow the key are ignored).

    The tag is only used to determine the type of the line and is discarded 
    leaving the key and the value, which follows the tag.  The value takes one 
    of three forms.

    #. If the line contains further text (characters after the colon-space), 
       then the value is that text.  The text ends at the line break and may 
       contain any other printing UTF-8 character.

    #. If there is no further text on the line and the next line has greater 
       indentation, then the next line holds the value, which may be a list, 
       a dictionary, or a multiline string.

    #. Otherwise the value is empty; it is taken to be an empty string.

    The second form of *dictionary item* is the *dictionary item with multiline 
    key*.  It consists of a multiline key value followed by an indented value.
    The value may be a multiline string, list, or dictionary; or an inline list 
    or dictionary.

    Adjacent dictionary items of either form with the same indentation level are 
    combined in order into a dictionary.


**Inline Lists and Dictionaries**:

    If the first non-ASCII-space character on a line is either a left bracket 
    (``[``) or a left brace (``{``) the line is an *inline structure*.  
    A bracket introduces an inline list and a brace introduces an inline 
    dictionary.

    Inlines are confined to a single line, and so must not contain any 
    line-break white space, such as newlines.

    An *inline list* starts with an open bracket (``[``), ends with a matching 
    closed bracket (``]``), contains inline values separated by commas (``,``), 
    and is contained on a single line.  The values may be inline strings, inline 
    lists, and inline dictionaries.

    An *inline dictionary* starts with an open brace (``{``), ends with 
    a matching closed brace (``}``), contains inline dictionary items separated 
    by commas (``,``), and is contained on a single line.  An inline dictionary 
    item is a key and value separated by a colon (``:``).  A space need not 
    follow the colon and any white space that does follow the colon is ignored.  
    The keys are inline strings and the values may be inline strings, inline 
    lists, and inline dictionaries.

    *Inline strings* are the string values specified in inline dictionaries and 
    lists.  They are somewhat constrained in the characters that they may 
    contain; nothing is allowed that might be confused with the syntax 
    characters used by the inline list or dictionary that contains it.  
    Specifically, inline strings may not include line-break white space 
    characters such as newlines or any of the following characters: ``[``, 
    ``]``, ``{``, ``}``, or ``,``.  In addition, inline strings that are 
    contained in inline dictionaries may not contain ``:``.  Both leading and 
    trailing white space is ignored with inline strings.  This includes all 
    non-line-break white space characters such as ASCII spaces and tabs, as well 
    as the various Unicode white space characters.

    Both inline lists and dictionaries may be empty, and represent the only way 
    to represent empty lists or empty dictionaries in *NestedText*.  An empty 
    dictionary is represented with ``{}`` and an empty list with ``[]``.  In 
    both cases there must be no space between the opening and closing 
    delimiters.  An inline list that contains only white spaces, such as ``[ 
    ]``, is treated as a list with a single empty string (the whitespace is 
    considered a string value, and string values have leading and trailing 
    spaces removed, resulting in an empty string value).  If a list contains 
    multiple values, no white space is required to represent an empty string 
    value.  Thus, ``[]`` represents an empty list, ``[ ]`` a list with a single 
    empty string value, and ``[,]`` a list with two empty string values.


**Indentation**:

    Leading spaces on a line represents indentation.  Only ASCII spaces are 
    allowed in the indentation. Specifically, tabs and the various Unicode 
    spaces are not allowed.

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

    An indented value may only follow a list item or dictionary item that does 
    not have a value on the same line.  An indented value must follow a key 
    item.


**Escaping and Quoting**:

    There is no escaping or quoting in *NestedText*. Once the line has been 
    identified by its tag, and the tag is removed, the remaining text is taken 
    literally.


**Empty document**:

    A document may be empty. A document is empty if it consists only of
    comments and blank lines.  An empty document corresponds to an empty value 
    of unknown type. Implementations may allow a default top-level type of
    dictionary, list, or string to be specified.


**End of file**:

    The last character in a *NestedText* document file is a newline.


**Result**:

    When a document is converted from *NestedText* the result is a hierarchical 
    collection of dictionaries, lists and strings.  All dictionary keys are 
    strings.
