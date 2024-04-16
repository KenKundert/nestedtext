.. hide:

    >>> from inform import Inform
    >>> ignore = Inform(prog_name=False)


***************
Common mistakes
***************

.. currentmodule:: nestedtext

Two values for one key
----------------------

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
    invalid indentation.
    An indent may only follow a dictionary or list item that does not
    already have a value.
       4 ❬    address: Home❭
       5 ❬        > 3636 Buffalo Ave❭
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
    invalid indentation.
    An indent may only follow a dictionary or list item that does not
    already have a value, which in this case consists only of whitespace.
       4 ❬    address:  ❭
       5 ❬        > 3636 Buffalo Ave❭
              ▲

Notice the ␣␣ that follows *address* in *content*.  These are replaced by 
2 spaces before *content* is processed by *loads*.  Thus, in this case there is 
an extra space at the end of line 4.  Anything beyond the: ``:␣`` is considered 
the value for *address*, and in this case that is the single extra space 
specified at the end of the line.  This extra space is taken to be the value of 
*address*, making the multiline string in lines 5 and 6 a value too many.

This mistake is easier to see in advance if you configure your editor to show 
trailing whitespace.  To do so in Vim, add::

    set listchars=trail:␣

to your ~/.vimrc file.


Lists or strings at the top level
---------------------------------

Most *NestedText* files start with key-value pairs at the top-level and we 
noticed that many developers would simply assume this in their code, which would 
result in unexpected crashes when their programs read legal *NestedText* files 
that had either a list or a string at the top level.  To avoid this, the 
:func:`load` and :func:`loads` functions are configured to expect a dictionary 
at the top level by default, which results in an error being reported if 
a dictionary key is not the first token found:

.. code-block:: python

    >>> import nestedtext as nt

    >>> content = """
    ... - a
    ... - b
    ... """

    >>> try:
    ...     print(nt.loads(content))
    ... except nt.NestedTextError as e:
    ...     e.report()
    error: 2: content must start with key or brace ({).
           2 ❬- a❭

This restriction is easily removed using *top*:

.. code-block:: python

    >>> try:
    ...     print(nt.loads(content, top=list))
    ... except nt.NestedTextError as e:
    ...     e.report()
    ['a', 'b']

The *top* argument can take any of the following values: *"dict"*, *dict*, 
*"list"*, *list*, *"str"*, *str*, *"any"*, or *any*.  The default value is 
*dict*.  The value given for *top* also determines the value returned by 
:func:`load` and :func:`loads` if the *NestedText* document is empty.

================ =================================
*top*            value returned for empty document
---------------- ---------------------------------
*"dict"*, *dict* ``{}``
*"list"*, *list* ``[]``
*"str"*, *str*   ``""``
*"any"*, *any*   *None*
================ =================================
