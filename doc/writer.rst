Writer
------

You can use :func:`nestedtext.dumps()` to convert a data structure consisting of 
dictionaries, lists, and strings to *NestedText*:

.. code-block:: python

    >>> from textwrap import dedent
    >>> import nestedtext

    >>> data = {
    ... 'src_dir': '/',
    ... 'excludes': [
    ...     '/dev',
    ...     '/home/*/.cache',
    ...     '/root/*/.cache',
    ...     '/proc',
    ...     '/sys',
    ...     '/tmp',
    ...     '/var/cache',
    ...     '/var/lock',
    ...     '/var/run',
    ...     '/var/tmp',
    ... ],
    ... 'keep': {
    ...     'hourly': '24',
    ...     'daily': '7',
    ...     'weekly': '4',
    ...     'monthly': '12',
    ...     'yearly': '5',
    ... },
    ... 'passphrase': dedent("""\
    ...     trouper segregate militia airway pricey sweetmeat tartan bookstall
    ...     obsession charlady twosome silky puffball grubby ranger notation
    ...     rosebud replicate freshen javelin abbot autocue beater byway\
    ... """),
    ... }

    >>> try:
    ...     print(nestedtext.dumps(data))
    ... except nestedtext.NestedTextError as e:
    ...     e.report()
    src_dir: /
    excludes:
        - /dev
        - /home/*/.cache
        - /root/*/.cache
        - /proc
        - /sys
        - /tmp
        - /var/cache
        - /var/lock
        - /var/run
        - /var/tmp
    keep:
        hourly: 24
        daily: 7
        weekly: 4
        monthly: 12
        yearly: 5
    passphrase:
        > trouper segregate militia airway pricey sweetmeat tartan bookstall
        > obsession charlady twosome silky puffball grubby ranger notation
        > rosebud replicate freshen javelin abbot autocue beater byway

This example writes to a string, but it is common to write to a file.  The file 
name and extension are arbitrary. However, by convention a '.nt' suffix is 
generally used for *NestedText* files.

There are several mechanisms available for handling objects that are otherwise 
unsupported by the format.

By default, *dumps* is configured to be rather forgiving, so it will render many 
of the base Python data types, such as *None*, *bool*, *int*, *float* and 
list-like options such as *tuple* and *set*. This implies that a round trip 
through *dumps* and *loads* could result in the types of values being 
transformed. You can prevent this by passing `default='strict'` to *dump*. Doing 
so means that values that are not dictionaries, lists, or strings generate 
exceptions:

.. code-block:: python

    >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}

    >>> try:
    ...     print(nestedtext.dumps(data))
    ... except nestedtext.NestedTextError as e:
    ...     e.report()
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
values are *str* and *repr*:

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
type to a render function:

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
    ...     e.report()
    key: 0x2a
    value: 3.14
    valid: yes
    house: red

Both *default* and *renderers* may be used together. *renderers* has priority 
over the built-in types and *default*. When a function is specified as 
*default*, it is always applied as a last resort.
