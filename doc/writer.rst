Writer
------

*dumps* converts Python data objects to *NextedText*.

.. autofunction:: nestedtext.dumps

**Example:**

.. code-block:: python

    >>> import nestedtext

    >>> data = {
    ...     'name': 'Kristel Templeton',
    ...     'sex': 'female',
    ...     'age': '74',
    ... }

    >>> try:
    ...     print(nestedtext.dumps(data))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    name: Kristel Templeton
    sex: female
    age: 74

This example writes to a string, but it is common to write to a file.  The file 
name and extension are arbitrary. However, by convention a '.nt' suffix is 
generally used for *NestedText* files.


Deviant Types
~~~~~~~~~~~~~

The *NextedText* format only supports dictionaries, lists, and strings.
By default, *dumps* is configured to be rather forgiving, so it will render many 
of the base Python data types, such as *None*, *bool*, *int*, *float* and 
list-like types such as *tuple* and *set* by converting them to the types 
supported by the format.  This implies that a round trip through *dumps* and 
*loads* could result in the types of values being transformed. You can prevent 
this by passing `default='strict'` to *dumps*.  Doing so means that values that 
are not dictionaries, lists, or strings generate exceptions.

**Example:**

.. code-block:: python

    >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}

    >>> try:
    ...     print(nestedtext.dumps(data))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    key: 42
    value: 3.1415926
    valid: True

    >>> try:
    ...     print(nestedtext.dumps(data, default='strict'))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    42: unsupported type.

Alternatively, you can specify a function to *default*, which is used to convert 
values to strings.  It is used if no other converter is available.  Typical 
values are *str* and *repr*.

**Example:**

.. code-block:: python

    >>> class Color:
    ...     def __init__(self, color):
    ...         self.color = color
    ...     def __repr__(self):
    ...         return f'Color({self.color!r})'
    ...     def __str__(self):
    ...         return self.color

    >>> data['house'] = Color('red')
    >>> print(nestedtext.dumps(data, default=repr))
    key: 42
    value: 3.1415926
    valid: True
    house: "Color('red')"

    >>> print(nestedtext.dumps(data, default=str))
    key: 42
    value: 3.1415926
    valid: True
    house: red

You can also specify a dictionary of renderers. The dictionary maps the object 
type to a render function.

**Example:**

.. code-block:: python

    >>> renderers = {
    ...     bool: lambda b: 'yes' if b else 'no',
    ...     int: hex,
    ...     float: lambda f: f'{f:0.3}',
    ...     Color: lambda c: c.color,
    ... }

    >>> try:
    ...    print(nestedtext.dumps(data, renderers=renderers))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    key: 0x2a
    value: 3.14
    valid: yes
    house: red

If the dictionary maps a type to *None*, then the default behavior is used for 
that type. If it maps to *False*, then an exception is raised.

**Example:**

.. code-block:: python

    >>> renderers = {
    ...     bool: lambda b: 'yes' if b else 'no',
    ...     int: hex,
    ...     float: False,
    ...     Color: lambda c: c.color,
    ... }

    >>> try:
    ...    print(nestedtext.dumps(data, renderers=renderers))
    ... except nestedtext.NestedTextError as e:
    ...     print(str(e))
    3.1415926: unsupported type.

Both *default* and *renderers* may be used together. *renderers* has priority 
over the built-in types and *default*.  When a function is specified as 
*default*, it is always applied as a last resort.
