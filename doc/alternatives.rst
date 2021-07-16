************
Alternatives
************

There are no shortage of well established alternatives to *NestedText* for 
storing data in a human-readable text file.  The features and shortcomings of 
some of these alternatives are discussed next.  *NestedText* is intended to be 
used in situations where people either create, modify, or consume the data 
directly.  It is this perspective that informs these comparisons.


JSON
====

JSON_ is a subset of JavaScript suitable for holding data.  Like *NestedText*, 
it consists of a hierarchical collection of objects (dictionaries), lists, and 
strings, but also allows reals, integers, Booleans and nulls.  In practice, JSON 
is largely generated and consumed by machines.  The data is stored as text, and 
so can be read, modified, and consumed directly by the end user, but the format 
is not optimized for this use case and so is often cumbersome or inefficient 
when used in this manner.

JSON supports all the native data types common to most languages.  Syntax is 
added to values to unambiguously indicate their type. For example, ``2``, 
``2.0``, and ``"2"`` are three different values with three different types 
(integer, real, string).  This adds two types of complexity. First, the rules 
for distinguishing various types must be learned and used. Second, all strings 
must be quoted, and
with quoting comes escaping, which is needed to allow quote characters to be 
included in strings.

JSON was derived as a subset of JavaScript, and so inherits a fair amount of 
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

The following examples illustrate the difference between JSON and *NestedText*:

**JSON**:

    .. literalinclude:: ../examples/fumiko.json
        :language: json

**NestedText**:

    .. literalinclude:: ../examples/fumiko.nt
        :language: nestedtext

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
To illustrate these points, the following is a condensation of a YAML document 
taken from the GitHub documentation that describes host to configure continuous 
integration using Python:

**YAML**:

    .. literalinclude:: ../examples/github-orig.yaml
        :language: yaml

And here is the result of running that document through the YAML reader and 
writer.  One might expect that the format might change a bit but that the 
information conveyed remains unchanged.

YAML (round-trip):
    .. literalinclude:: ../examples/github-rt.yaml
        :language: yaml

There are a few things to notice about this second version.

1. ``on`` key was inappropriately converted to ``true``.
2. Python version ``3.10`` was inappropriately converted to ``3.1``.
3. The multiline strings were converted to an even more obscure format.
4. Indentation is not an accurate reflection of nesting (notice that 
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

*NestedText* has the following clear advantages over *CSV* and *TSV* as a human 
readable and writable data file format:

- text does not require quoting or escaping
- arbitrary data hierarchies are supported
- file representation tends to be tall and skinny rather than short and fat
- easier to read


.. _json: https://www.json.org/json-en.html
.. _yaml: https://yaml.org/
.. _strictyaml: <https://hitchdev.com/strictyaml
.. _toml: https://toml.io/en/
.. _ini: https://en.wikipedia.org/wiki/INI_file
.. _csv: https://en.wikipedia.org/wiki/Comma-separated_values
.. _tsv: https://en.wikipedia.org/wiki/Tab-separated_values
