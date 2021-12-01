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
strings, but also allows numbers, Booleans and nulls.  In practice, JSON is 
largely generated and consumed by machines.  The data is stored as text, and so 
can be read, modified, and consumed directly by the end user, but the format is 
not optimized for this use case and so is often cumbersome or inefficient when 
used in this manner.

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
clear advantages over JSON as a human readable and writable data file format:

- strings do not require quotes
- comments
- multiline strings
- no need to escape special characters
- commas are not used to separate dictionary and list items

The following examples illustrate the difference between JSON and *NestedText*:

.. collapse:: JSON

    .. literalinclude:: ../examples/fumiko.json
        :language: json

.. collapse:: NestedText

    .. literalinclude:: ../examples/fumiko.nt
        :language: nestedtext

|

.. _vs_yaml:

YAML
====

YAML_ is considered by many to be a human friendly alternative to JSON.  There 
is less syntactic clutter and the quoting of strings is optional.  However, it 
also supports a wide variety of data types and formats.  The optional quoting 
can result in the type of values being ambiguous. To distinguish between the 
various types, a complicated and non-intuitive set of rules developed.  YAML at 
first appears very appealing when used with simple examples, but things can 
quickly become complicated or provide unexpected results.  A reaction to this is 
the use of YAML subsets, such as StrictYAML_.  However, the subsets still try to 
maintain compatibility with YAML and so inherit much of its complexity. For 
example, both YAML and StrictYAML support `nine different ways of writing 
multiline strings <http://stackoverflow.com/a/21699210/660921>`_.

YAML avoids excessive quoting and supports comments and multiline strings, but 
the multitude of formats and disambiguation rules make YAML a difficult language 
to learn, and the ambiguities creates traps for the user.
To illustrate these points, the following is a condensation of a YAML document 
taken from the GitHub documentation that describes how to configure continuous 
integration using Python:

.. collapse:: YAML

    .. literalinclude:: ../examples/github-orig.yaml
        :language: yaml

|
| And here is the result of running that document through the Python YAML reader 
  and writer.

.. collapse:: YAML (round-trip)

    .. literalinclude:: ../examples/github-rt.yaml
        :language: yaml

|
| There are a few things to notice about this second version.

1. ``on`` key was inappropriately converted to ``true``.
2. Python version ``3.10`` was inappropriately converted to ``3.1``.
3. The multiline string was converted to a different representation that added 
   blank lines between each line, greatly confusing the presentation of the 
   string.
4. Escaping was required for the quotes on ``'requirements.txt'``.
5. Indentation is not an accurate reflection of nesting (notice that 
   ``python-version`` and ``- 3.6`` have the same indentation, but ``- 3.6`` is 
   contained inside ``python-version``).

One might expect that the format might change a bit while the underlying 
information remains constant.  But that is not the case.  The ambiguities in the 
format result in both ``on`` and ``3.10`` being changed in value and meaning.

Now consider the *NestedText* version; it is simpler and not subject to 
misinterpretation.

.. collapse:: NestedText

    .. literalinclude:: ../examples/github-intent.nt
        :language: nestedtext

|
| *NestedText* was inspired by YAML, but eschews its complexity. It has the 
  following clear advantages over YAML as a human readable and writable data 
  file format:

- simple
- unambiguous (no implicit typing)
- no unexpected conversions of the data
- syntax is insensitive to special characters within text
- safe, no risk of malicious code execution
- round-tripping from *NestedText* does not result in changed values or ugly and 
  confusing presentations


.. _vs_toml:

TOML or INI
===========

TOML_ is a configuration file format inspired by the well-known INI_ syntax.  It 
supports a number of basic data types (notably including dates and times) using 
syntax that is more similar to JSON (explicit but verbose) than to YAML 
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

.. collapse:: TOML

    .. literalinclude:: ../examples/sparekeys.toml
        :language: toml

.. collapse:: NestedText

    .. literalinclude:: ../examples/sparekeys.nt
        :language: nestedtext

|
| *NestedText* has the following clear advantages over TOML and INI as a human 
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

.. collapse:: CSV

    .. literalinclude:: ../examples/percent_bachelors_degrees_women_usa.csv
        :language: text

.. collapse:: NestedText

    .. literalinclude:: ../examples/percent_bachelors_degrees_women_usa.nt
        :language: nestedtext

|
| It is hard to beat the compactness of *CSV* for tabular data, however 
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

*NestedText* and its alternatives are all trying to represent structured data.  
Of them, only *NestedText* limits you to strings for the scalar values.
The alternatives all allow other data types to be represented as well, such as
integers, reals, Booleans, etc.  Since real applications invariably require
all these data types, you might think, "if I use *NestedText*, I'll have to
convert all these strings myself, and that will make my application code
more complicated".  In fact, using *NestedText* will make your application
code more robust with little to no increase in complexity:

.. collapse:: Schemas make data conversions easy.

    For robustness, all data should be validated when reading it to assure there 
    are no errors.  This is conveniently and efficiently performed with 
    a :ref:`schema <schemas>`.  Schemas are used to specify the expected type 
    for each value and are easily extended to perform type conversion as needed.  
    For example, if a particular value should be an integer but a string is 
    provided, as with *NestedText*, the package that implements the schema can 
    be configured to attempt to convert the string to an integer and only report 
    an error if it cannot.

.. collapse:: You have to handle the bad user input anyway.

    Applications that need to interpret the input data always make assumptions 
    about the data being read.  For example, email fields are expected to 
    contain strings that can be interpreted as an email address.  In practice, 
    every field can and probably should be checked in some way.  Even with 
    *NestedText* that constrains the scalar values to strings, one must assure 
    that a list or dictionary is not given where a string is expected.  When
    every value is being checked there little to no benefit to the underlying 
    data receptacle being aware the type of each value.  Rather it is very 
    constraining.

|
| Supporting native data types raises its own issues:

.. collapse:: No format can support all possible data types.

    *NestedText* gains simplicity by jettisoning native support for scalar data 
    types other than strings.  However it is important to recognize that the 
    alternatives must do this as well.  There are an unlimited number of data 
    types that can be supported and they cannot support them all.  Common data 
    types that are generally not supported include dates, times, and quantities 
    (numbers with units, such as $20.00 and 47 kΩ).  With all languages there is 
    a decision to be made: what types should be supported natively.  Each 
    additional type increases the complexity of the format.  If only strings are 
    supported, as with *NestedText*, things are pretty simple.  Adding any other 
    data type then requires supporting quoting and escaping, which is 
    a substantial jump up in complexity.

    Data types that are not natively supported are generally passed as strings 
    that are later converted to the right type by the end application.  This 
    approach actually provides substantial benefits.  The end application has 
    context that a general purpose data reader cannot have.  For example, the 
    date ``10/07/08`` could represent either 10 August 2008 or October 7, 2008, 
    or perhaps even July 8, 2010.  Only the user and the application would know 
    which.

.. collapse:: Native data types can be ambiguous.

    The type of the value ``2`` is ambiguous; it may be integer or real.  This 
    may cause problems when combined into an array, such as ``[1.85, 1.94, 2, 
    2.09]``.  A casually written program may choke on a non-homogeneous array 
    that consists of an integer among the floats.  This is the reason that JSON 
    does not distinguish between integers and reals.

    YAML is notorious for ambiguities because it allows unquoted strings.  ``2`` 
    is a valid integer, real, and string.  Similarly, ``no`` is a valid Boolean 
    and string.  In fact, every single value in YAML that is not quoted is also 
    a valid string.  Many people that use YAML simply quote every string, but 
    that does not solve all the problems because things that are not intended to 
    be strings can be converted to strings, such as ``09``.

    There is also the issue of the internal representation of the data.  Is the 
    integer represented using 32 bits, 64 bits, or can the integer by 
    arbitrarily large?  Is a real number represented as a 64 bit or 128 bit 
    float, or is it represented by a decimal or rational number?  Are 
    exceptional values such as infinity or not-a-number supported? Sometimes 
    such things are specified in the definition of the format, but often they 
    are left as details of the implementation.  The result could be overflows, 
    underflows, loss of precision, errors, and compatibility issues.

.. collapse:: Native data types can lose information.

    It is common to format real numbers so as to convey the meaningful precision 
    of the number.  For example, ``2`` or ``2.`` represents a number with one 
    digit of precision, ``2.0`` represents a number with two digits of 
    precision, ``2.00`` represents a number with three digits of precision, etc.  
    This information on the precision of the number is lost when these numbers 
    are converted to the float data type.

    This same issue also causes problems when representing version numbers.  The 
    number ``3.10`` is used to represent version three point ten, but when 
    converted to a float becomes version three point one.

    There are also cases where multiple formats map to the same underlying data 
    type.  For example, integers may be given in binary, octal, decimal, or 
    hexadecimal formats.  YAML provides almost a dozen different ways to specify 
    strings.  This causes problems when round-tripping, which is where you read 
    a file, perhaps process it, and then write it back out.  Since the data is 
    converted to an internal data type, the original formatting is lost, meaning 
    that the program that writes out the data cannot know how it was originally 
    specified.  Integers are generally written out as decimal number regardless 
    of how they were specified.  In YAML, the writer checks to see if a string 
    contains a newline and if so simply chooses one of the 9 possible multiline 
    string formats arbitrarily.  This is why in the round-trip :ref:`YAML 
    example <vs_yaml>` given above the Python script ends up being interleaved 
    with blank lines.

|
| Using *NestedText* also makes life easier for your end-users:

.. collapse::
    Native types may be unfamiliar, inconvenient, or confusing for end users.

    Casual users may not understand that ``2`` is treated differently than 
    ``2.0``, which may cause issues in applications that are not carefully 
    written.

    TOML natively accepts dates and times, but only in `ISO-8601 formats 
    <https://en.wikipedia.org/wiki/ISO_8601>`_.  Casual users are unlikely to be 
    familiar with this format or may find it awkward or cumbersome.

    YAML natively accepts sexagesimal (base 60) numbers in the form ``2:30:00``, 
    which YAML converts to 9000.  If this is a duration, it would likely imply 
    2 hours, 30 minutes and 0 seconds, which totals to 9000 seconds.  It may be 
    also used for the time of day.  Someone that normally uses twelve hour time 
    formatting might write ``2:30:00 AM`` and get a string.  Someone that uses 
    twenty-four hours formatting might write ``2:30:00`` and get the integer 
    9000, or they might write ``02:30:00`` and get a string.  However, if they 
    entered a time 12 hours later, ``16:30:00``, they would get an integer 
    again.

    Native data types are distinguished from each other by using conventions 
    that are second nature to programmers.  Conventions such as "you must quote 
    strings", "quote characters in strings must be escaped", "you escape an 
    escape character by doubling it up", "real numbers must contain a decimal 
    point" and "real numbers may not contain units".

    Casual users are unlikely to know these conventions, which causes 
    frustration and errors.  Forcing them to know and use these conventions 
    represents an undesirable and sometimes overwhelming burden.  This is 
    particularly true for YAML, which can be a minefield even for programmers.
    Consider the following:

    | ``Hey there!`` and ``"Hey there!"`` represent the same string.
    | ``She said, "Hey there!"`` is a valid string,
        but ``"She said, "Hey there!""`` is an error.
    | ``She said, "Hey there!"`` is a valid string,
        but ``She said: "Hey there!"`` is an error.
    | ``3.10.4`` is a string, but ``3.10`` is a real and ``3`` is an integer.
    | ``10`` is 10, but ``010`` is 8 and ``09`` is "09", a string.
    | ``Now`` is a string, but ``No`` is a Boolean.
    | ``(1 + 2)`` is a string, but ``[1 + 2]`` is a list.
    | ``02:30:00`` is a string but ``2:30:00`` is 9000.

    Only programmers with substantial experience with YAML can anticipate or 
    even understand this behavior.

    Other languages have similar, but less extreme challenges, particularly the 
    need for quoting and escaping.

.. collapse::
    Support for non-string types creates the requirement for quoting and 
    escaping, and ultimately leads to either verbosity (JSON) or ambiguity 
    (YAML).

    Every additional supported data type brings a challenge; how to 
    unambiguously distinguish it from the others.  The challenge is particularly 
    acute for strings because they consist of any possible sequence of 
    characters and so can be confused with all other data types.  *NestedText* 
    addresses this issue by limiting the scalar values to only be strings. That 
    way, there is no need to distinguish the strings from other possible data 
    types.

    The alternatives all distinguish strings by surrounding them with quotes.  
    This adds visual clutter and makes them more difficult to type.  This is not 
    generally a problem if there are only a few stings, but it becomes a drag if 
    there is are many.  However, quoting brings another challenge.  Since 
    a string can consist of any sequence of characters, it can include the quote 
    characters.  Now the quote characters within the string must be 
    distinguished from the quote characters that delimit the string; a process 
    referred to as escaping the character.  This is often done with an special 
    escape character, generally the backslash, but may be done by duplicating 
    the character to be escaped.  The string may naturally contain escape 
    characters and they would need escaping as well.  This represents a deep 
    hole.  For example, consider the following Python dictionary that contains 
    a collection of regular expressions.  The regular expressions are quoted 
    strings that by their very nature generally require a large amount of 
    escaping:

    .. code-block:: python

        regexes = dict(
            double_quoted_string = r'"(?:[^"\\]|\\.)*"',
            single_quoted_string = r"'(?:[^'\\]|\\.)*'",
            identifier = r'[a-zA-Z_][a-zA-Z_0-9]*',
            number = r"[+-]?[0-9]+\.?[0-9]*(?:[eE][+-]?[0-9]+)?",
        )

    Converting this to JSON illustrates the problem:

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

.. collapse::
    Data type is an implementation detail that should not concern the end user.

    In general, users that are expected to read, write, or modify structured 
    data benefit from formats tailored to their needs.  That only happens when 
    the values are passed as strings that are interpreted by the end 
    application.

    Native data types should only be used when both the data generator and the 
    data consumer are machines, preferably using the same software packages to 
    both read and write the data files.  In such cases, only programmers would 
    view or edit the files, and only in unusual cases.

|
| Native data types provide little value but many drawbacks.  By limiting the 
  scalar values to be only strings, *NestedText* sidesteps all of these issues, 
  and it is unique in that regard.


.. _json: https://www.json.org/json-en.html
.. _yaml: https://yaml.org/
.. _strictyaml: <https://hitchdev.com/strictyaml
.. _toml: https://toml.io/en/
.. _ini: https://en.wikipedia.org/wiki/INI_file
.. _csv: https://en.wikipedia.org/wiki/Comma-separated_values
.. _tsv: https://en.wikipedia.org/wiki/Tab-separated_values
