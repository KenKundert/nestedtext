Reader
------

You can read *NestedTest* data using :func:`nestedtext.loads()`, which takes 
a string as an argument:

.. code-block:: python

    >>> import nestedtext
    >>> from inform import render

    >>> contents = """
    ... # backup settings for root
    ... src_dir: /
    ... excludes:
    ...     - /dev
    ...     - /home/*/.cache
    ...     - /root/*/.cache
    ...     - /proc
    ...     - /sys
    ...     - /tmp
    ...     - /var/cache
    ...     - /var/lock
    ...     - /var/run
    ...     - /var/tmp
    ... keep:
    ...     hourly: 24
    ...     daily: 7
    ...     weekly: 4
    ...     monthly: 12
    ...     yearly: 5
    ... passphrase:
    ...     > trouper segregate militia airway pricey sweetmeat tartan bookstall
    ...     > obsession charlady twosome silky puffball grubby ranger notation
    ...     > rosebud replicate freshen javelin abbot autocue beater byway
    ... """

    >>> try:
    ...     data = nestedtext.loads(contents)
    ... except nestedtext.NestedTextError as e:
    ...     e.report()

    >>> print(render(data))
    {
        'src_dir': '/',
        'excludes': [
            '/dev',
            '/home/*/.cache',
            '/root/*/.cache',
            '/proc',
            '/sys',
            '/tmp',
            '/var/cache',
            '/var/lock',
            '/var/run',
            '/var/tmp',
        ],
        'keep': {
            'hourly': '24',
            'daily': '7',
            'weekly': '4',
            'monthly': '12',
            'yearly': '5',
        },
        'passphrase': """\
            trouper segregate militia airway pricey sweetmeat tartan bookstall
            obsession charlady twosome silky puffball grubby ranger notation
            rosebud replicate freshen javelin abbot autocue beater byway\
        """,
    }

*loads()* takes an optional second argument, *culprit*. If specified, it will be 
prepended to any error messages. It is often used to designate the source of 
*contents*. For example,if *contents* were read from a file, *culprit* would be 
the file name.


*NestedText* as a Structure Parser
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Parsing data can be a difficult challenge. One way to reduce the challenge is to 
reduce the scope of what is being parsed. With *NestedText* you can delegate the 
parsing the of the structure, and instead focus on parsing individual values 
given as strings.  A transforming validator line `Voluptuous 
<https://github.com/alecthomas/voluptuous>`_ can greatly simply the process.

To use *Voluptuous* you would create a schema and then apply the schema to the 
data. Normally the schema used to validate the data, but with a little extra 
plumbing the data can be transformed to the needed form.  This will be 
demonstrated with a very simple example.

In order for *voluptuous* to convert the data to the desired type, a converter 
function is helpful:

.. code-block:: python

    >>> import voluptuous

    >>> def coerce(type, msg=None):
    ...     """Coerce a value to a type.
    ...
    ...     If the type constructor throws a ValueError, the value will be
    ...     marked as Invalid.
    ...     """
    ...     def f(v):
    ...         try:
    ...             return type(v)
    ...         except ValueError:
    ...             raise voluptuous.Invalid(msg or ('expected %s' % type.__name__))
    ...     return f

The next step is to define a schema that declares the expected types of the 
various fields in the configuration file. For example, imagine the configuration 
file has has three values, *name*, *value*, and *editable*, the first of which 
must be a string, the second a float, and the third a boolean that is specified 
using either 'yes' or 'no'. This can be done as follows:

.. code-block:: python

    >>> import nestedtext
    >>> from inform import render

    >>> def to_bool(v):
    ...     try:
    ...         v = v.lower()
    ...         assert v in ['yes', 'no']
    ...         return v == 'yes'
    ...     except:
    ...         raise ValueError("expected 'yes' or 'no'.")

    >>> config = '''
    ... name: volume
    ... value: 50
    ... editable: yes
    ... '''

    >>> config_data = nestedtext.loads(config)
    >>> print(render(config_data))
    {
        'name': 'volume',
        'value': '50',
        'editable': 'yes',
    }

    >>> schema = voluptuous.Schema(
    ...     dict(name=str, value=coerce(float), editable=coerce(to_bool))
    ... )

    >>> settings = schema(config_data)
    >>> print(render(settings))
    {
        'name': 'volume',
        'value': 50.0,
        'editable': True,
    }

Notice that a dictionary that contains the expected types and conversion 
functions is passed to *Schema*. Then the raw configuration is parsed for 
structure by *NestedText*, and the resulting data structure is processed by the 
schema to and converted to its final form.
