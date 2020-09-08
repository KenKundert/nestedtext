.. _nestedtext file format:

***********
File format
***********
The *NestedText* format follows a small number of simple rules. Here they are.

Each line in a *NestedText* document is assigned one of the following types:
*comment*, *blank*, *list-item*, *dict-item*, and *string-item*.  Any line that
does not fit one of these types is an error.

Comments are lines that have `#` as the first non-space character on the line.
Comments are ignored.

Blank lines are lines that are empty or consist only of white space characters
(spaces or tabs).  Blank lines are also ignored.

The remaining lines are identifying by which one of these characters are found
in an unquoted portion of the line: '-', ':', '>' when followed immediately by
a space or newline.  Once the first of one of these pairs has been found in the
unquoted portion of the line, any subsequent occurrences of any of the line-type
tags are treated as simple text.  For example::

    - And the winner is: {winner}

In this case the leading '- ' determines the type of the line and the ': ' is
simply treated as part of the remaining text on the line.

If the line begins with '- ' that is not within quotes or if the line contains
only '-', the line is a *list-item*.  Adjacent list-items with the same
indentation level are combined into a list with their order being retained.
Each list-item has an associated value.

If the line begins with '> ' that is not within quotes, or if the line consists
of a single indented '>', the line is a *string-item*.  Adjacent string-items
with the same indentation level are combined into a multi-line string with their
order being retained.  Any leading white space that follows the '> ' is
retained, as is any trailing space.

If the line contains an ': ' that does not fall within quotes or ends with
a ':', the line is considered a *dict-item*.  Adjacent dict-items with the same
indentation level are combined into a dictionary with their order being
retained.  Each dict-item consists of a key, the colon, and a value.  A key must
be a string; it must not contain a newline, and it must be quoted if it contains
a line-type tag or has leading or trailing spaces.

The values associated with list and dict items may take one of three forms. If
the line contains further text (characters after the '- ' or ': '), then that
text is the value.

If there is no further text on the line and the next line has greater
indentation, then the next line holds the value, which may be a list,
a dictionary, or a multi-line string.  Otherwise the value is empty; it is taken
to be an empty string.

An increase in the number of spaces in the indentation signifies the start of 
a nested object.  Indentation must return to a prior level when the nested 
object ends.  Each level of indentation need not employ the same number of 
additional spaces, though it is recommended that you choose either 2 or 4 spaces 
to represent a level of hierarchy and you use that consistently throughout the 
document.  However, this is not required. Any increase in the number of spaces 
in the indentation represents an indent and any decrease represents a dedent.  
Only spaces are allowed in the indentation. Specifically, tabs are not allowed.  
In addition, tabs cannot follow a colon, cash, or greater-than symbol to form 
a dictionary, list, or string item.  Tabs can be included in string values.
