.. currentmodule:: nestedtext

*********
Basic use
*********

The *NestedText* API is patterned after that of JSON.

NestedText Reader
-----------------

The :func:`loads` function is used to convert *NestedText* into a Python data 
structure.  If there is a problem interpreting the input text, 
a :exc:`NestedTextError` exception is raised.

.. code-block:: python

    >>> import nestedtext

    >>> content = """
    ... access key id: 8N029N81
    ... secret access key: 9s83109d3+583493190
    ... """

    >>> try:
    ...     data = nestedtext.loads(content)
    ... except nestedtext.NestedTextError as e:
    ...     e.terminate()

    >>> print(data)
    {'access key id': '8N029N81', 'secret access key': '9s83109d3+583493190'}


NestedText Writer
-----------------

The :func:`dumps` function is used to convert a Python data structure into 
*NestedText*.  As before, if there is a problem converting the input data, 
a :exc:`NestedTextError` exception is raised.

.. code-block:: python

    >>> try:
    ...     content = nestedtext.dumps(data)
    ... except nestedtext.NestedTextError as e:
    ...     e.terminate()

    >>> print(content)
    access key id: 8N029N81
    secret access key: 9s83109d3+583493190
