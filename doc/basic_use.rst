.. currentmodule:: nestedtext

*********
Basic use
*********

The *NestedText* Python API is similar to that of *JSON*, *YAML*, *TOML*, etc.


Installation
------------

*NestedText* is also available from *pip*.  Install it with:

.. code-block:: text

   pip3 install nestedtext

Alternately, *NestedText* is also available in *Conda*.  Install it with:

.. code-block:: text

    conda install nestedtext --channel conda-forge


NestedText Reader
-----------------

The :func:`loads` function is used to convert *NestedText* held in a string into 
a Python data structure.  If there is a problem interpreting the input text, 
a :exc:`NestedTextError` exception is raised.

.. code-block:: python

    >>> import nestedtext as nt

    >>> content = """
    ... access key id: 8N029N81
    ... secret access key: 9s83109d3+583493190
    ... """

    >>> try:
    ...     data = nt.loads(content, top='dict')
    ... except nt.NestedTextError as e:
    ...     e.terminate()

    >>> print(data)
    {'access key id': '8N029N81', 'secret access key': '9s83109d3+583493190'}

You can also read directly from a file or stream using the :func:`load` 
function.

.. code-block:: python

    >>> from inform import fatal, os_error

    >>> try:
    ...     groceries = nt.load('examples/groceries.nt', top='dict')
    ... except nt.NestedTextError as e:
    ...     e.terminate()
    ... except OSError as e:
    ...     fatal(os_error(e))

    >>> print(groceries)
    {'groceries': ['Bread', 'Peanut butter', 'Jam']}

Notice that the type of the return value is specified to be 'dict'. This is the 
default. You can also specify 'list', 'str', or 'any' (or *dict*, *list*, *str*, 
or *any*).  All but 'any' constrain the data type of the top-level of the 
*NestedText* content.

The *load* functions provide a *keymap* argument that is useful for adding line 
numbers to error message.  This feature is demonstrated in :ref:`voluptuous 
example`.  They also provide a *normalize_key* argument that can be used to 
ignore insignificant variation in keys, such as character case, or to convert 
keys to a desired form, such as to identifiers.  These features are described in 
:meth:`loads`.


NestedText Writer
-----------------

The :func:`dumps` function is used to convert a Python data structure into 
a *NestedText* string.  As before, if there is a problem converting the input 
data, a :exc:`NestedTextError` exception is raised.

.. code-block:: python

    >>> try:
    ...     content = nt.dumps(data)
    ... except nt.NestedTextError as e:
    ...     e.terminate()

    >>> print(content)
    access key id: 8N029N81
    secret access key: 9s83109d3+583493190

The :func:`dump` function writes *NestedText* to a file or stream.

.. code-block:: python

    >>> try:
    ...     nt.dump(data, 'examples/access.nt')
    ... except nt.NestedTextError as e:
    ...     e.terminate()
    ... except OSError as e:
    ...     fatal(os_error(e))

The *dump* functions provide arguments that can control the output format and 
can control the conversion of data types into forms that can be dumped. These
features are described in :meth:`dumps`.
