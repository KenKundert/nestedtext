Programmer's Interface
======================


Reader
------

.. autofunction:: nestedtext.loads


Writer
------

.. autofunction:: nestedtext.dumps


Exception
---------

*NestedText* imports the *Error* exception from `inform 
<https://inform.readthedocs.io/en/stable/api.html#exceptions>`_ and renames it 
*NestedTextError*.  You can find more documentation on what you can do with this 
exception there.

.. autoexception:: nestedtext.NestedTextError
    :members:

.. ignore the following (there is only one method, so no need for TOC)
   .. autoclasstoc::


As with most exceptions, you can simply cast it to a string to get a reasonable 
error message:

.. code-block:: python

    >>> from textwrap import dedent
    >>> import nestedtext

    >>> content = dedent("""
    ...     name:
    ...     name:
    ... """)

    >>> try:
    ...     print(nestedtext.loads(content))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    3: duplicate key: name.

You can also use the *report* method to print the message directly. This is 
appropriate if you are using *inform* for your messaging as it follows 
*inform*'s conventions.

.. code-block:: python

    >> try:
    ..     print(nestedtext.loads(content))
    .. except nestedtext.NestedTextError as e:
    ..     e.report()

The *terminate* method prints the message directly and exits.

.. code-block:: python

    >> try:
    ..     print(nestedtext.loads(content))
    .. except nestedtext.NestedTextError as e:
    ..     e.terminate()

Finally, exceptions produced by *NestedText* contain a *template* attribute that 
contains the basic text of the message. You can change this message by 
overriding the attribute when using *report*, *terminate*, or *render*.  
*render* is like casting the exception to a string except that allows for the
passing of arguments.  For example, to convert a particular message to Spanish, 
you could use:

.. code-block:: python

    >>> try:
    ...     print(nestedtext.loads(content))
    ... except nestedtext.NestedTextError as e:
    ...     template = None
    ...     if e.template == 'duplicate key: {}.':
    ...         template = 'llave duplicada: {}.'
    ...     print(e.render(template=template))
    3: llave duplicada: name.

