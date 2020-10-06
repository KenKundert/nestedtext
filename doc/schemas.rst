*******
Schemas
*******

The default schema used by *NestedText* is that all leaf values are arbitrary 
strings.  This is not always desired. It may be that the data contains certain 
values that should be represented as data types other than strings.  Common 
examples include Booleans, numbers, quantities, dates, times, etc.  For example, 
in a list of employees, the dictionary that describes each employee may contain 
a field *year born* that should be converted to an integer that is greater than 
1900 and less than the current year.  This involves two operations: validation 
(assuring that given value represents a year in the acceptable range) and 
coercion (converting value from a string to an integer).  Both operations can be 
performed by a transforming validator like `Voluptuous 
<https://github.com/alecthomas/voluptuous>`_.

To use *Voluptuous* you would create a schema and then apply the schema to the 
data. The schema details what fields are expected, and what what kind of values 
they should contain. Normally the schema is used to validate the data, but with 
a little extra plumbing the data can be transformed to the needed form.  The 
following is a very simple example (see :ref:`cryptocurrency holdings 
<cryptocurrency example>` for a more complete example).

In order for *Voluptuous* to convert the data to the desired type, a 
converter function is helpful:

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

The next step is to define a schema that declares the expected types of 
the various fields in the configuration file. For example, imagine the 
configuration file has has three values, *name*, *value*, and 
*editable*, the first of which must be a string, the second a float, 
and the third a Boolean that is specified using either 'yes' or 'no'. 
This can be done as follows:

.. code-block:: python

    >>> import nestedtext as nt

    >>> def to_bool(v):
    ...     try:
    ...         v = v.lower()
    ...         assert v in ['yes', 'no']
    ...         return v == 'yes'
    ...     except:
    ...         raise ValueError("expected 'yes' or 'no'.")

    >>> config = """
    ... name: volume
    ... value: 50
    ... editable: yes
    ... """

    >>> config_data = nt.loads(config)
    >>> print(config_data)
    {'name': 'volume', 'value': '50', 'editable': 'yes'}

    >>> schema = voluptuous.Schema(
    ...     dict(name=str, value=coerce(float), editable=coerce(to_bool))
    ... )

    >>> settings = schema(config_data)
    >>> print(settings)
    {'name': 'volume', 'value': 50.0, 'editable': True}

Notice that a dictionary that contains the expected types and 
conversion functions is passed to *Schema*. Then the raw configuration 
is parsed for structure by *NestedText*, and the resulting data structure is 
processed by the schema to and converted to its final form.

One way to interpret this process is that *NestedText* is used to hold 
structured but untyped data, and *Voluptuous* is used to restore the intended 
type of each value while also checking the data to assure it satisfies basic 
assumptions.  This approach is very flexible in that the same string can be 
converted to different types based on the value it represents. For example, 12 
can be an integer if it represents a day of a month, it can be a float if it 
represents the output voltage of a power brick, and it could be a string if 
represents the version of a software package.
