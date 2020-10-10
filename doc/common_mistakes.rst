***************
Common mistakes
***************

.. currentmodule:: nestedtext

When :func:`load()` or :func:`loads()` complains of errors it is important to 
look both at the line fingered by the error message and the one above it.  The 
line that is the target of the error message might by an otherwise valid 
*NestedText* line if it were not for the line above it.  For example, consider 
the following example:

**Example:**

.. code-block:: python

    >>> import nestedtext as nt

    >>> content = """
    ... treasurer:
    ...     name: Fumiko Purvis
    ...     address: Home
    ...         > 3636 Buffalo Ave
    ...         > Topeka, Kansas 20692
    ... """

    >>> try:
    ...     data = nt.loads(content)
    ... except nt.NestedTextError as e:
    ...     print(e.get_message())
    ...     print(e.get_codicil()[0])
    invalid indentation. An indent may only follow a dictionary or list
    item that does not already have a value.
       4 «    address: Home»
       5 «        > 3636 Buffalo Ave»
              ▲

Notice that the complaint is about line 5, but problem stems from line 4 where 
*Home* gave a value to *address*. With a value specified for *address*, any 
further indentation on line 5 indicates a second value is being specified for 
*address*, which is illegal.

A more subtle version of this same error follows:

**Example:**

.. code-block:: python

    >>> content = """
    ... treasurer:
    ...     name: Fumiko Purvis
    ...     address:␣␣
    ...         > 3636 Buffalo Ave
    ...         > Topeka, Kansas 20692
    ... """

    >>> try:
    ...     data = nt.loads(content.replace('␣␣', '  '))
    ... except nt.NestedTextError as e:
    ...     print(e.get_message())
    ...     print(e.get_codicil()[0])
    invalid indentation. An indent may only follow a dictionary or list
    item that does not already have a value, which in this case consists
    only of whitespace.
       4 «    address:  »
       5 «        > 3636 Buffalo Ave»
              ▲

Notice the ␣␣ that follows *address* in *content*.  These are replaced by 
2 spaces before *content* is processed by *loads*.  Thus, in this case there is 
an extra space at the end of line 4.  Anything beyond the: ``:␣`` is considered 
the value for *address*, and in this case that is the single extra space 
specified at the end of the line.  This extra space is taken to be the value of 
*address*, making the multiline string in lines 5 and 6 a value too many.
