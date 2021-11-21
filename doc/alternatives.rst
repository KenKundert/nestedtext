.. _alternatives:

************
Alternatives
************

There are no shortage of well established alternatives to *NestedText* for 
storing data in a human-readable text file.  The features and shortcomings of 
some of these alternatives are discussed next.  *NestedText* is intended to be 
used in situations where people either create, modify, or consume the data 
directly.  It is this perspective that informs these comparisons.


.. _vs_json:

JSON
====

JSON_ is a subset of JavaScript suitable for holding data.  Like *NestedText*, 
it consists of a hierarchical collection of objects (dictionaries), lists, and 
strings, but also allows numbers, Booleans and nulls.  In practice, *JSON* is 
largely generated and consumed by machines.  The data is stored as text, and so 
can be read, modified, and consumed directly by the end user, but the format is 
not optimized for this use case and so is often cumbersome or inefficient when 
used in this manner.

*JSON* supports all the native data types common to most languages.  Syntax is 
added to values to unambiguously indicate their type. For example, ``2``, 
``2.0``, and ``"2"`` are three different values with three different types 
(integer, real, string).  This adds two types of complexity. First, the rules 
for distinguishing various types must be learned and used. Second, all strings 
must be quoted, and
with quoting comes escaping, which is needed to allow quote characters to be 
included in strings.

*JSON* was derived as a subset of JavaScript, and so inherits a fair amount of 
syntactic clutter that can be annoying for users to enter and maintain.  In 
addition, features that would improve clarity are lacking.  Comments are not 
allowed, multiline strings are not supported, and whitespace is insignificant 
(leading to the possibility that the appearance of the data may not match its 
true structure).

*NestedText* only supports three data types (strings, lists and dictionaries) 
and does not have the baggage of being the subset of a general purpose 
programming language.  The result is a simpler language that has the following 
clear advantages over *JSON* as a human readable and writable data file format:

- strings do not require quotes
- comments
- multiline strings
- no need to escape special characters
- commas are not used to separate dictionary and list items

The following examples illustrate the difference between *JSON* and 
*NestedText*:

**JSON**:

    .. literalinclude:: ../examples/fumiko.json
        :language: json

**NestedText**:

    .. literalinclude:: ../examples/fumiko.nt
        :language: nestedtext

.. _vs_yaml:

YAML
====

YAML_ is considered by many to be a human friendly alternative to *JSON*.  There 
is less syntactic clutter and the quoting of strings is optional.  However, it 
also supports a wide variety of data types and formats.  The optional quoting 
can result in the type of values being ambiguous. To distinguish between the 
various types, a complicated and non-intuitive set of rules developed.  *YAML* 
at first appears very appealing when used with simple examples, but things can 
quickly become complicated or provide unexpected results.  A reaction to this is 
the use of *YAML* subsets, such as StrictYAML_.  However, the subsets still try 
to maintain compatibility with *YAML* and so inherit much of its complexity. For 
example, both *YAML* and *StrictYAML* support `nine different ways of writing 
multiline strings <http://stackoverflow.com/a/21699210/660921>`_.

*YAML* avoids excessive quoting and supports comments and multiline strings, but 
the multitude of formats and disambiguation rules make *YAML* a difficult 
language to learn, and the ambiguities creates traps for the user.
To illustrate these points, the following is a condensation of a *YAML* document 
taken from the GitHub documentation that describes how to configure continuous 
integration using Python:

**YAML**:

    .. literalinclude:: ../examples/github-orig.yaml
        :language: yaml

And here is the result of running that document through the Python *YAML* reader 
and writer.  One might expect that the format might change a bit but that the 
information conveyed remains unchanged.

**YAML (round-trip)**:

    .. literalinclude:: ../examples/github-rt.yaml
        :language: yaml

There are a few things to notice about this second version.

1. ``on`` key was inappropriately converted to ``true``.
2. Python version ``3.10`` was inappropriately converted to ``3.1``.
3. Blank lines were added to the multiline strings and were converted to another 
   of the 9 possible formats.
4. Escaping was required for the quotes on ``'requirements.txt'``.
5. Indentation is not an accurate reflection of nesting (notice that 
   ``python-version`` and ``- 3.6`` have the same indentation, but ``- 3.6`` is 
   contained inside ``python-version``).

Now consider the *NestedText* version; it is simpler and not subject to 
misinterpretation.

**NestedText**:

    .. literalinclude:: ../examples/github-intent.nt
        :language: nestedtext

*NestedText* was inspired by *YAML*, but eschews its complexity. It has the 
following clear advantages over *YAML* as a human readable and writable data 
file format:

- simple
- unambiguous (no implicit typing)
- no unexpected conversions of the data
- syntax is insensitive to special characters within text
- safe, no risk of malicious code execution


.. _vs_toml:

TOML or INI
===========

TOML_ is a configuration file format inspired by the well-known INI_ syntax.  It 
supports a number of basic data types (notably including dates and times) using 
syntax that is more similar to *JSON* (explicit but verbose) than to *YAML* 
(succinct but confusing).  As discussed previously, though, this makes it the 
responsibility of the user to specify the correct type for each field.

Another flaw in TOML is that it is difficult to specify deeply nested 
structures.  The only way to specify a nested dictionary is to give the full 
key to that dictionary, relative to the root of the entire hierarchy.  This is 
not much a problem if the hierarchy only has 1-2 levels, but any more than that 
and you find yourself typing the same long keys over and over.  A corollary to 
this is that TOML-based configurations do not scale well: increases in 
complexity are often accompanied by disproportionate decreases in readability 
and writability.

Here is an example of a configuration file in TOML and *NestedText*:

**TOML**:

    .. literalinclude:: ../examples/sparekeys.toml
        :language: toml

**NestedText**:

    .. literalinclude:: ../examples/sparekeys.nt
        :language: nestedtext

*NestedText* has the following clear advantages over TOML and INI as a human 
readable and writable data file format:

- text does not require quoting or escaping
- data is left in its original form
- indentation used to succinctly represent nested data
- the structure of the file matches the structure of the data
- heavily nested data is represented efficiently


.. _vs_csv:

CSV or TSV
==========

CSV_ (comma-separated values) and the closely related TSV_ (tab-separated 
values) are exchange formats for tabular data.  Tabular data consists of 
multiple records where each record is made up of a consistent set of fields.
The format separates the records using line breaks and separates the fields 
using commas or tabs.  Quoting and escaping is required when the fields contain 
line breaks or commas/tabs.

Here is an example data file in CSV and *NestedText*.

**CSV**:

    .. literalinclude:: ../examples/percent_bachelors_degrees_women_usa.csv
        :language: text

**NestedText**:

    .. literalinclude:: ../examples/percent_bachelors_degrees_women_usa.nt
        :language: nestedtext

It is hard to beat the compactness of *CSV* for tabular data, however 
*NestedText* has the following advantages over *CSV* and *TSV* as a human 
readable and writable data file format that may make it preferable in some 
situation:

- text does not require quoting or escaping
- arbitrary data hierarchies are supported
- file representation tends to be tall and skinny rather than short and fat
- easier to read


.. _only_strings:

Really, Only Strings?
=====================

*NestedText* and its alternatives are all trying to represent structured ASCII 
data.  Of them, only *NestedText* limits you to strings for the leaf values.  
All the others allow other data types to be represented as well, such as 
integers, reals, Booleans, etc.  Every additional data type brings a challenge; 
how to unambiguously distinguish it from the others.  The challenge is 
particularly acute for strings because they consist of any possible sequence of 
characters and so can be confused with all other data types.  *NestedText* 
addresses this issue by limiting the leaf values to only be strings. That way, 
there is no need to distinguish the strings from other possible data types.

The alternatives all distinguish strings by surrounding them with quotes.  This 
adds visual clutter and makes them more difficult to type.  This is not 
generally a problem if there are only a few stings, but it becomes a drag if 
there is are many.  However, quoting brings another challenge.  Since a string 
can consist of any sequence of characters, it can include the quote characters.  
Now the quote characters within the string must be distinguished from the quote 
characters that delimit the string; a process referred to as escaping the 
character.  This is often done with an escape character, generally the 
backslash, but may be done by duplicating the character to be escaped.  The 
string may naturally contain escape characters and they would need escaping as 
well.  This can represent a deep hole.  For example, consider the following 
Python dictionary that contains a collection of regular expressions.  The 
regular expressions are quoted strings that by their very nature generally 
require a large amount of escaping:

.. code-block:: python

    regexes = dict(
        double_quoted_string = r'"(?:[^"\\]|\\.)*"',
        single_quoted_string = r"'(?:[^'\\]|\\.)*'",
        identifier = r'[a-zA-Z_][a-zA-Z_0-9]*',
        number = r"[+-]?[0-9]+\.?[0-9]*(?:[eE][+-]?[0-9]+)?",
    )

Converting this to *JSON* illustrates the problem:

.. code-block:: json

    {
        "double_quoted_string": "\"(?:[^\"\\\\]|\\\\.)*\"",
        "single_quoted_string": "'(?:[^'\\\\]|\\\\.)*'",
        "identifier": "[a-zA-Z_][a-zA-Z_0-9]*",
        "number": "[+-]?[0-9]+\\.?[0-9]*(?:[eE][+-]?[0-9]+)?"
    }

The number of escape characters more than doubled.  This problem does not occur 
in *NestedText*, which is actually cleaner than the original Python:

.. code-block:: nestedtext

    double_quoted_string: "(?:[^"\\]|\\.)*"
    single_quoted_string: '(?:[^'\\]|\\.)*'
    identifier: [a-zA-Z_][a-zA-Z_0-9]*
    number: [+-]?[0-9]+\.?[0-9]*(?:[eE][+-]?[0-9]+)?

*NestedText* gains this simplicity by jettisoning native support for the other 
data types.  However it is important to recognize that the alternatives must do 
this as well.  There are an unlimited number of data types that can be 
supported; they cannot support all of them.  Common data types that are 
generally not supported include dates, times, and quantities (numbers with 
units, such as $20.00 and 47 kΩ).  Rather, these values are treated as strings 
that are later converted to the right type by the end application.  This 
actually provides substantial benefits.  The end application has context that 
a general purpose data reader cannot have.  For example, the date 10/07/08 could 
represent either July 8, 2010 or October 7, 2008: only the user and the 
application would know which.

There are further issues with natively supported data types.  For example, the 
type of the value 2 is ambiguous, it may either be integer or real.  This may 
cause problems when combined into an array, such as [1.85, 1.94, 2, 2.09].  
A casually written program may choke on a non-homogeneous array that consists of 
an integer among the floats.  There is also the issue of the internal 
representation of the data.  Is the integer represented using 32 bits, 64 bits, 
or can the integer by arbitrarily large.  Is a real number represented as a 64 
bit or 128 bit float, or is it represented by a decimal or rational number.  
Sometimes such things are specified in the definition of the format, but often 
they are left as details of the implementation.  The result could be overflows, 
underflows, loss of precision, or compatibility issues.

All of these issues affect the readability, writeability, and fidelity of the 
format.  By limiting the leaf values to be only strings, *NestedText* sidesteps 
all of these issues.


.. _json: https://www.json.org/json-en.html
.. _yaml: https://yaml.org/
.. _strictyaml: <https://hitchdev.com/strictyaml
.. _toml: https://toml.io/en/
.. _ini: https://en.wikipedia.org/wiki/INI_file
.. _csv: https://en.wikipedia.org/wiki/Comma-separated_values
.. _tsv: https://en.wikipedia.org/wiki/Tab-separated_values
