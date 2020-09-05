Exceptions
----------

:func:`nestedtext.loads()` and :func:`nestedtext.dumps()` both raise 
*NestedTextError* when they discover an error. *NestedTextError* subclasses both 
the Python *ValueError* and the *Error* exception from *Inform*.
You can find more documentation on what you can do with this exception in the 
`Inform documentation 
<https://inform.readthedocs.io/en/stable/api.html#exceptions>`_.

.. autoexception:: nestedtext.NestedTextError
    :members: render, report, terminate, get_culprit, get_codicil, get_extended_codicil

.. ignore the following (there is only one method, so no need for TOC)
   .. autoclasstoc::

The exception provides the following attributes:

source:

    The source of the *NestedText* content, if given. This is often a filename.

doc:

    The *NestedText* content passed to :func:`nestedtext.loads`.

line:

    The line of *NestedText* content where the problem was found.

lineno:

    The number of the line where the problem was found.

colno:

    The number of the character where the problem was found on *line*.

template:

    The possibly parameterized text used for the error message.

As with most exceptions, you can simply cast it to a string to get a reasonable 
error message.

**Example:**

.. code-block:: python

    >>> from textwrap import dedent
    >>> import nestedtext

    >>> content = dedent("""
    ...     name1: value1
    ...     name1: value2
    ...     name3: value3
    ... """).strip()

    >>> try:
    ...     print(nestedtext.loads(content))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    2: duplicate key: name1.

You can also use the *report* method to print the message directly. This is 
appropriate if you are using *inform* for your messaging as it follows 
*inform*'s conventions.

**Example:**

.. code-block:: python

    >> try:
    ..     print(nestedtext.loads(content))
    .. except nestedtext.NestedTextError as e:
    ..     e.report()
    error: 2: duplicate key: name1.
        «name1: value2»
         ↑

The *terminate* method prints the message directly and exits.

**Example:**

.. code-block:: python

    >> try:
    ..     print(nestedtext.loads(content))
    .. except nestedtext.NestedTextError as e:
    ..     e.terminate()
    error: 2: duplicate key: name1.
        «name1: value2»
         ↑

Exceptions produced by *NestedText* contain a *template* attribute that contains 
the basic text of the message. You can change this message by overriding the 
attribute when using *report*, *terminate*, or *render*.  *render* is like 
casting the exception to a string except that allows for the
passing of arguments.  For example, to convert a particular message to Spanish, 
you could use something like the following.

**Example:**

.. code-block:: python

    >>> try:
    ...     print(nestedtext.loads(content))
    ... except nestedtext.NestedTextError as e:
    ...     template = None
    ...     if e.template == 'duplicate key: {}.':
    ...         template = 'llave duplicada: {}.'
    ...     print(e.render(template=template))
    2: llave duplicada: name1.

When you have the exception report itself, you see up to two extra lines in the 
message that are used to display the line and the location where the problem was 
found.  Those extra lines are referred to as the codicil. You do not get them if 
you simply cast the exception to a string, but you can access them using 
:meth:`nestedtext.NestedTextError.get_codicil`.  There is an additional method, 
:meth:`nestedtext.NestedTextError.get_extended_codicil` that also shows the 
source of the problem, but with extra context.

**Example:**

.. code-block:: python

    >> try:
    ..     print(nestedtext.loads(content))
    .. except nestedtext.NestedTextError as e:
    ..     e.report(codicil=e.get_extended_codicil())
    error: 2: duplicate key: name1.
        1> name1: value1
        2> name1: value2
           ↑
        2> name3: value3
