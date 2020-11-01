************
Alternatives
************

There are no shortage of well established alternatives to *NestedText* for 
storing data in a human-readable text file.  The features and shortcomings of 
some of these alternatives are discussed next.

JSON
====

JSON_ is a subset of JavaScript suitable for holding data.  Like *NestedText*, 
it consists of a hierarchical collection of dictionaries, lists, and strings, 
but also allows integers, floats, Booleans and nulls.  The fundamental problem 
with *JSON* in this context is that its meant for serializing and exchanging 
data between programs; it's not meant for configuration files.  Of course, it's 
used for this purpose anyways, where it has a number of glaring shortcomings.

To begin, it has an excessive amount of syntactic clutter.  Dictionary keys and 
strings both have to be quoted, commas are required between dictionary and list 
items (but forbidden after the last item), braces are required around 
dictionaries, etc.  Features that would improve clarity are also lacking.  
Comments are not allowed, multiline strings are not supported, and whitespace 
is insignificant (leading to the possibility that the appearance of the data 
may not match its true structure).  More conceptually, it is the responsibility 
of the user to provide data of the correct type (e.g. ``32`` vs. ``32.0`` vs.  
``"32"``), even though the application already knows what type it expects.  All 
of this results in *JSON* being a frustrating format for humans to read, enter 
or edit.

*NestedText* has the following clear advantages over *JSON* as human readable 
and writable data file format:

- text does not require quotes
- data is left in its original form
- comments
- multiline strings
- special characters without escaping them
- commas are not used to separate dictionary and list items

YAML
====

YAML_ is considered by many to be a human friendly alternative to *JSON*, but 
over time it has accumulated too many data types and too many formats.  To 
distinguish between all the various types and formats, a complicated and 
non-intuitive set of rules developed.  *YAML* at first appears very appealing 
when used with simple examples, but things can quickly become complicated or 
provide unexpected results.  A reaction to this is the use of *YAML* subsets, 
such as StrictYAML_.  However, the subsets still try to maintain compatibility 
with *YAML* and so inherit much of its complexity. For example, both *YAML* and 
*StrictYAML* support `nine different ways of writing multiline strings 
<http://stackoverflow.com/a/21699210/660921>`_.

*YAML* avoids excessive quoting and supports comments and multiline strings, but 
like *JSON* it converts data to the underlying data types as appropriate, but 
unlike with *JSON*, the lack of quoting makes the format ambiguous, which means 
it has to guess at times, and small seemingly insignificant details can affect 
the result.

*NestedText* was inspired by *YAML*, but eschews its complexity. It has the 
following clear advantages over *YAML* as human readable and writable data file 
format:

- simple
- unambiguous (no implicit typing)
- data is left in its original form
- syntax is insensitive to special characters within text
- safe, no risk of malicious code execution

TOML
====

TOML_ is a configuration file format inspired by the well-known *INI* syntax.  
It supports a number of basic data types (notably including dates and times) 
using syntax that is more similar to *JSON* (explicit but verbose) than to 
*YAML* (succinct but confusing).  As discussed previously, though, this makes 
it the responsibility of the user to specify the correct type for each field, 
when it should be the responsibility of the application to convert each field 
to the correct type.

Another flaw in TOML is that it is difficult to specify deeply nested 
structures.  The only way to specify a nested dictionary is to give the full 
key to that dictionary, relative to the root of the entire hierarchy.  This is 
not much a problem if the hierarchy only has 1-2 levels, but any more than that 
and you find yourself typing the same long keys over and over.  A corollary to 
this is that TOML-based configurations do not scale well: increases in 
complexity are often accompanied by disproportionate decreases in readability 
and writability.

*NestedText* has the following clear advantages over *TOML* as human readable 
and writable data file format:

- text does not require quotes
- data is left in its original form
- indentation used to succinctly represent nested data
- the structure of the file matches the structure of the data

.. _json: https://www.json.org/json-en.html
.. _yaml: https://yaml.org/
.. _strictyaml: <https://hitchdev.com/strictyaml
.. _toml: https://toml.io/en/
