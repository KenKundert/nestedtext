*******
Schemas
*******

Because *NestedText* explicitly does not attempt to interpret the data it 
parses, it is meant to be paired with a tool that can both validate the data 
and convert them to the expected types.  For example, if you are expecting a 
date for a particular field, you would want to validate that the input looks 
like a date (e.g. ``YYYY/MM/DD``) and then convert it to a useful type (e.g.  
:class:`arrow.Arrow`).  You can do this on an ad hoc basis, or you can apply 
a schema.

A schema is the specification of what fields are expected (e.g. "birthday"), 
what types they should be (e.g. a date), and what values are legal (e.g. must 
be in the past).  There are many libraries available for applying a schema to 
data such as those parsed by *NestedText*.  Because different libraries may be 
more or less appropriate in different scenarios, *NestedText* avoids favoring 
any one library specifically:

- pydantic_: Define schema using type annotations
- voluptuous_: Define schema using objects
- schema_: Define schema using objects
- colander_: Define schema using classes
- schematics_: Define schema using classes
- cerebus_ : Define schema using strings
- valideer_: Define schema using strings
- jsonschema_: Define schema using JSON

See the :doc:`examples` page for examples of how to use some of these libraries 
with *NestedText*.

The approach of using separate tools for parsing and interpreting the data has 
two significant advantages that are worth briefly highlighting.  First is that 
the validation tool understands the context and meaning of the data in a way 
that the parsing tool cannot.  For example, "12" can be an integer if it 
represents a day of a month, a float if it represents the output voltage of a 
power brick, or a string if represents the version of a software package.  
Attempting to interpret "12" without this context is inherently unreliable.  
Second is that when data is interpreted by the parser, it puts the onus on the 
user to specify the correct types.  Going back to the previous example, the 
user would be required to know whether ``12``, ``12.0``, or ``"12"`` should be 
entered.  It does not make sense for this decision to be made by the user 
instead of the application.


.. _pydantic: https://pydantic-docs.helpmanual.io/
.. _voluptuous: https://github.com/alecthomas/voluptuous
.. _cerebus: https://docs.python-cerberus.org/en/stable/
.. _colander: https://docs.pylonsproject.org/projects/colander/en/latest/
.. _jsonschema: https://python-jsonschema.readthedocs.io/en/latest/
.. _schema: https://github.com/keleshev/schema
.. _schematics: http://schematics.readthedocs.io/en/latest/
.. _valideer: https://github.com/podio/valideer
