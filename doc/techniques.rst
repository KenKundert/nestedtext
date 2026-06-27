.. doctests:

   >>> import nestedtext as nt

.. currentmodule:: nestedtext


**********
Techniques
**********

This section documents common patterns of use with examples and suggestions.


.. _voluptuous example:

Validate with *Voluptuous*
==========================

This example shows how to use voluptuous_ to validate and parse a *NestedText* 
file and it demonstrates how to use the *keymap* argument from :func:`loads` or 
:func:`load` to add location information to *Voluptuous* error messages.

The input file in this case specifies deployment settings for a web server:

.. literalinclude:: ../examples/validation/deploy.nt
   :language: nestedtext

Below is the code to parse this file.  Note how the structure of the data is 
specified using basic Python objects.  The :func:`Coerce()` function is 
necessary to have Voluptuous convert string input to the given type; otherwise 
it would simply check that the input matches the given type:

.. literalinclude:: ../examples/validation/deploy_voluptuous.py
   :language: python

This example uses the following code to adapt error reporting in *Voluptuous* to 
*NestedText* (this is a simplified version of *voluptuous_errors*,.the complete 
version is available at voluptuous_errors_.

.. literalinclude:: ../examples/validation/voluptuous_errors.py
   :language: python

This produces the following data structure:

.. code-block:: python

    {'allowed_hosts': ['www.example.com'],
     'database': {'engine': 'django.db.backends.mysql',
                  'host': 'db.example.com',
                  'port': 3306,
                  'user': 'www'},
     'debug': False,
     'secret_key': 't=)40**y&883y9gdpuw%aiig+wtc033(ui@^1ur72w#zhw3_ch',
     'webmaster_email': 'admin@example.com'}

See the :ref:`PostMortem <postmortem example>` example for a more flexible 
approach to validating using validating functions with *Voluptuous*.


.. _pydantic example:

Validate with *Pydantic*
========================

This example shows how to use pydantic_ to validate and parse a *NestedText* 
file.  The input file is the same as in the previous example, i.e. deployment 
settings for a web server:

.. literalinclude:: ../examples/validation/deploy.nt
   :language: nestedtext

Below is the code to parse this file.  Note that basic types like integers, 
strings, Booleans, and lists are specified using standard type annotations.  
Dictionaries with specific keys are represented by model classes, and it is 
possible to reference one model from within another.  Pydantic_ also has 
built-in support for validating email addresses, which we can take advantage of 
here:

.. literalinclude:: ../examples/validation/deploy_pydantic.py
   :language: python

This produces the same result as in the previous example.


.. _error reporting:

Error Reporting
===============

*NestedText* raises a :class:`NestedTextError` when it encounters a problem, and 
you can simply use it to report the error.  It tends to do a good job of 
locating the error for the user.

.. code-block:: python

    import nestedtext as nt
    from inform import fatal, os_error

    try:
        data = nt.load("data.nt")
    except OSError as e:
        fatal(os_error(e))
    except nt.NestedTextError as e:
        e.terminate()

And when validating with *Voluptuous* you will also get good error messages if 
you follow :ref:`above example <voluptuous example>`.

However, what if you encounter an error in a field after you have already read 
in and validated your data.  In this case, you can use 
:class:`NestedTextDataError` to report the error. It identifies the source of 
the problem in a way that is understandable by the user.  *NestedTextDataError* 
is defined by *NestedText*, but is never raised by *NestedText* itself.  Rather 
it is provided so that you can easily report error that derive from 
a *NestedText* document.

To see how this is done, consider the following example.  It involves an 
*NestedText* file that contains some test cases, each of which contains an 
expression to be evaluated by Python, and the expected result.  Both the 
expression and the result are first evaluated by Python, and the result is 
compared with what was expected.  There are two ways in which errors can occur: 
the evaluated result may not match the expected value, which is a failure, or 
the expression itself might not be valid a valid Python expression, in which 
case Python raises an exception.

The test code is in *test_cases.nt*:

.. literalinclude:: ../examples/errors/test_cases.nt
   :language: nestedtext

And here is the code:

.. literalinclude:: ../examples/errors/test
   :language: python

Notice that the tests are run and any exception is caught and passed to 
*NestedTextDataError*, along with the name of the source file, the keys of the 
offending test case, the keymap as returned from the loader.

The following errors are reported::

    test error: test_cases.nt@3, 0›expected, expr=2**8: test failed.
        result=256 ≠ expected=255
    test error: test_cases.nt@5, 1›expr: invalid literal for int() with base 10: 'x'
           5 ❬    expr: int('x')❭
    test error: test_cases.nt@8, 2›expr: '(' was never closed (<string>, line 1)
           8 ❬    expr: math.log2(4096❭
                                  ▲

Notice that each message starts by identifying the source of the error in two 
ways, first is the file name and line number (test_cases.nt@3), and the second 
is the key path (0›expected).  The message ends by showing the offending line, 
unless it suppressed, as it is in the first message.


.. _normalizing keys:

Normalizing Keys
================

With data files created by non-programmers it is often desirable to allow 
a certain amount of flexibility in the keys.  For example, you may wish to 
ignore case and if you allow multi-word keys you may want to be tolerant of 
extra spaces between the words.  However, the end applications often needs the 
keys to be specific values.  It is possible to normalize the keys using 
a schema, but this can interfere with error reporting.  Imagine there is an 
error in the value associated with a set of keys, if the keys have been changed 
by the schema the *keymap* can no longer be used to convert the keys into a line 
number for an error message.  *NestedText* provides the *normalize_key* argument 
to :func:`load` and :func:`loads` to address this issue.  It allows you to pass 
in a function that normalizes the keys before the *keymap* is created, releasing 
the schema from that task.

The following contact look-up program demonstrates both the normalization of 
keys and the associated error reporting.  In this case, the first level of keys 
contains the names of the contacts and should not be normalized. Keys at all 
other levels are considered keywords and so should be normalized.

.. literalinclude:: ../examples/addresses/address
   :language: python

This program takes a name as a command line argument and prints out the 
corresponding address.  It uses the pretty print idea described below to render 
the contact information.  *Voluptuous* checks the validity of the contacts 
database, which is shown next. Notice the variability in the keys given in 
Fumiko's entry:

.. literalinclude:: ../examples/addresses/address.nt
   :language: nestedtext

There are two display statements near the end of the program, the first of which 
is commented out.  The first outputs the contact information using normalized 
keys, and the second outputs the information using the original keys.

Now, requesting Fumiko's contact information gives::

    Fumiko Purvis:
        Position: treasurer
        Address:
            3636 Buffalo Ave
            Topeka, Kansas 20692
        Phone: 1-268-555-0280
        EMail: fumiko.purvis@hotmail.com

Notice that any processing of the information (error checking, deleting 
*additional_roles*) is performed using the normalized keys, but by choice, the 
information is output using the original keys.


.. _duplicate keys:

Duplicate Keys
==============

There are occasions where it is useful to be able to read dictionaries from 
NestedText that contain duplicate keys.  For example, imagine that you have two 
contacts with the same name, and the name is used as a key.  Normally 
:func:`load` and :func:`loads` throw an exception if duplicate keys are detected 
because the underlying Python dictionaries cannot hold items with duplicate 
keys.  However, you can pass a function to the *on_dup* argument that 
de-duplicates the keys, making them safe for Python dictionaries.  For example 
the following *NestedText* document that contains duplicate keys:

.. literalinclude:: ../examples/deduplication/michael_jordan.nt
   :language: nestedtext

In the following, the *de_dup* function adds “#*N*” to the end of the key where 
*N* starts at 2 and increases as more duplicates are found.

.. literalinclude:: ../examples/deduplication/michael_jordan
   :language: python

As shown below, this code outputs the data twice, the first time with the 
de-duplicated keys and the second time using the original keys.  Notice that the 
first contains the duplication markers whereas the second does not.

.. literalinclude:: ../examples/deduplication/michael_jordan.out
   :language: nestedtext


.. _sorting keys:

Sorting Keys
============

The default order of dictionary items in the *NestedText* output of :func:`dump` 
and :func:`dumps` is the natural order of the underlying dictionary, but you can 
use *sort_keys* argument to change the order.  For example, here are two 
different ways of sorting the address list. The first is a simple alphabetic 
sort of the keys at each level, which you get by simply specifying 
*sort_keys=True*.

.. code-block:: python

    >>> addresses = nt.load( 'examples/addresses/address.nt')
    >>> print(nt.dumps(addresses, sort_keys=True))
    Fumiko Purvis:
        Additional  Roles:
            - accounting task force
        Address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        EMail: fumiko.purvis@hotmail.com
        Phone: 1-268-555-0280
        Position: Treasurer
    Katheryn McDaniel:
        additional roles:
            - board member
        address:
            > 138 Almond Street
            > Topeka, Kansas 20697
        email: KateMcD@aol.com
        phone:
            cell: 1-210-555-5297
            work: 1-210-555-8470
        position: president
    Margaret Hodge:
        additional roles:
            - new membership task force
            - accounting task force
        address:
            > 2586 Marigold Lane
            > Topeka, Kansas 20682
        email: margaret.hodge@ku.edu
        phone: 1-470-555-0398
        position: vice president

The second sorts only the first level, by last name then remaining names.  It 
passes a function to *sort_keys*.  That function takes two arguments, the key to 
be sorted and the tuple of parent keys.  The key to be sorted is also a tuple 
that contains the key and the rendered item.  The key is the key as specified in 
the object being dumped, and rendered item is a string that takes the form 
“mapped_key: value”.

The *sort_keys* function is expected to return a string that contains the sort 
key, the key used by the sort.  For example, in this case a first level key 
"Fumiko Purvis" is mapped to “Purvis Fumiko” for the purposes of determining the 
sort order.  At all other levels any key is mapped to “”.  In this way the sort 
keys are all identical, and so the original order is retained.

.. code-block:: python

    >>> def sort_key(key, parent_keys):
    ...      if len(parent_keys) == 0:
    ...          # rearrange names so that last name is given first
    ...          names = key[0].split()
    ...          return ' '.join([names[-1]] + names[:-1])
    ...      return ''  # do not reorder lower levels

    >>> print(nt.dumps(addresses, sort_keys=sort_key))
    Margaret Hodge:
        position: vice president
        address:
            > 2586 Marigold Lane
            > Topeka, Kansas 20682
        phone: 1-470-555-0398
        email: margaret.hodge@ku.edu
        additional roles:
            - new membership task force
            - accounting task force
    Katheryn McDaniel:
        position: president
        address:
            > 138 Almond Street
            > Topeka, Kansas 20697
        phone:
            cell: 1-210-555-5297
            work: 1-210-555-8470
        email: KateMcD@aol.com
        additional roles:
            - board member
    Fumiko Purvis:
        Position: Treasurer
        Address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        Phone: 1-268-555-0280
        EMail: fumiko.purvis@hotmail.com
        Additional  Roles:
            - accounting task force


.. _key presentation:

Key Presentation
================

When generating a *NestedText* document, it is sometimes desirable to transform 
the keys upon output.  Generally one transforms the keys in order to change the 
presentation of the key, not the meaning.  For example, you may want change its 
case, rearrange it (ex: swap first and last names), translate it, etc.  These 
are done by passing a function to the *map_keys* argument.  This function takes
two arguments: the key after it has been rendered to a string and the tuple of 
parent keys.  It is expected to return the transformed string.  For example, 
lets print the address book again, this time with names printed with the last 
name first.

.. code-block:: python

    >>> def last_name_first(key, parent_keys):
    ...     if len(parent_keys) == 0:
    ...         # rearrange names so that last name is given first
    ...         names = key.split()
    ...         return f"{names[-1]}, {' '.join(names[:-1])}"

    >>> def sort_key(key, parent_keys):
    ...     return key if len(parent_keys) == 0 else ''  # only sort first level keys

    >>> print(nt.dumps(addresses, map_keys=last_name_first, sort_keys=sort_key))
    Hodge, Margaret:
        position: vice president
        address:
            > 2586 Marigold Lane
            > Topeka, Kansas 20682
        phone: 1-470-555-0398
        email: margaret.hodge@ku.edu
        additional roles:
            - new membership task force
            - accounting task force
    McDaniel, Katheryn:
        position: president
        address:
            > 138 Almond Street
            > Topeka, Kansas 20697
        phone:
            cell: 1-210-555-5297
            work: 1-210-555-8470
        email: KateMcD@aol.com
        additional roles:
            - board member
    Purvis, Fumiko:
        Position: Treasurer
        Address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        Phone: 1-268-555-0280
        EMail: fumiko.purvis@hotmail.com
        Additional  Roles:
            - accounting task force

When round-tripping a *NestedText* document (reading the document and then later 
writing it back out), one often wants to undo any changes that were made to the 
keys when reading the documents.  These modifications would be due to key 
normalization or key de-duplication.  This is easily accomplished by simply 
retaining the keymap from the original load and passing it to the dumper by way 
of the *map_keys* argument.

.. code-block:: python

    >>> def normalize_key(key, parent_keys):
    ...     if len(parent_keys) == 0:
    ...         return key
    ...     return '_'.join(key.lower().split())

    >>> keymap = {}
    >>> addresses = nt.load(
    ...     'examples/addresses/address.nt',
    ...     normalize_key = normalize_key,
    ...     keymap = keymap
    ... )
    >>> filtered = {k:v for k,v in addresses.items() if 'fumiko' in k.lower()}

    >>> print(nt.dumps(filtered))
    Fumiko Purvis:
        position: Treasurer
        address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        phone: 1-268-555-0280
        email: fumiko.purvis@hotmail.com
        additional_roles:
            - accounting task force

    >>> print(nt.dumps(filtered, map_keys=keymap))
    # Contact information for our officers
    <BLANKLINE>
    Fumiko Purvis:
        Position: Treasurer
            # Fumiko's term is ending at the end of the year.
        Address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        Phone: 1-268-555-0280
        EMail: fumiko.purvis@hotmail.com
        Additional  Roles:
            - accounting task force

Notice that the keys differ between the two.  The normalized key are output in 
the former and original keys in the latter.  Also notice that in the comments 
were included in the second output.

Finally consider the case where you want to do both things; you want to return 
to the original keys but you also want to change the presentation.  For example, 
imagine wanting to display the original keys in blue.  That can be done as 
follows:

.. code-block:: python

    >>> from inform import Color
    >>> blue = Color('blue', enable=Color.isTTY())

    >>> def format_key(key, parent_keys):
    ...    orig_keys = nt.get_keys(parent_keys + (key,), keymap)
    ...    return blue(orig_keys[-1])

    >>> print(nt.dumps(filtered, map_keys=format_key))
    Fumiko Purvis:
        Position: Treasurer
        Address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        Phone: 1-268-555-0280
        EMail: fumiko.purvis@hotmail.com
        Additional  Roles:
            - accounting task force

The result looks identical in the documentation, but if you ran this program in 
a terminal you would see the keys in blue.


.. _adding comments:

Adding Comments
===============

If you are creating a *NestedText* document from raw data, you can add comments 
to your document by creating an empty keymap, adding comments to it, and 
providing it to the dumper.  Here is an example.

The following program outputs a weight diary for an individual.  In this case, 
it output two files, a plain version and one with comments.  This example 
demonstrates how to add header and footer comments, how to add a comment where 
the comment is simply a blank line, and how to add dynamically created comments 
that act as section headings.

.. literalinclude:: ../examples/weight/weight
   :language: python

Here is the output without comments:

.. literalinclude:: ../examples/weight/plain.nt
   :language: nestedtext

And now, with comments:

.. literalinclude:: ../examples/weight/commented.nt
   :language: nestedtext


.. _references:

References
==========

A reference allows you to define some content once and insert that content 
multiple places in the document.  A reference is also referred to as a macro.
Both simple and parametrized references can be easily implemented.  For 
parametrized references, the arguments list is treated as an embedded 
*NestedText* document.

The technique is demonstrated with an example.  This example is a fragment of 
a diet program.  It reads two *NestedText* documents, one containing the known 
foods, and the other that documents the actual meals as consumed.  The foods may 
be single ingredient, like *steel cut oats*, or it may contain multiple 
ingredients, like *oatmeal*.  The use of parametrized references allows one to 
override individual ingredients in a composite ingredient.  In this example, the 
user simply specifies the composite ingredient *oatmeal* on 21 March.  On 22 
March, they specify it as a simple reference, meaning that they end up with the 
same ingredients, but this time they are listed separately in the final summary.  
Finally, on 23 March they specify oatmeal using a parametrized reference so as 
to override the number of tangerines consumed and add some almonds.

..  literalinclude:: ../examples/references/diet
   :language: python

It produces the following output:

.. literalinclude:: ../examples/references/diet.nt
   :language: nestedtext

In this example the content for the references was pulled from a different 
*NestedText* document.  See the :ref:`PostMortem <postmortem example>` as an 
example that pulls the referenced content from the same document.


.. _accumulation:

Accumulation
============

This example demonstrates how to used *NestedText* so that it supports some 
common common aspects of settings files; specifically you can override or 
accumulate to previously specified settings by repeating their names.

It implements an example settings file reader that supports a small variety of 
settings.  *NestedText* is configured to normalize and de-duplicate the keys 
(the names of the settings) with the result being processed to identify and 
report errors and to implement overrides, accumulations, and simple conversions.  
Accumulation is indicated adding a plus sign to the beginning of the key.  The 
keys are normalized by converting them to snake case (all lower case, contiguous 
spaces replaced by a single underscore).

..  literalinclude:: ../examples/accumulation/settings.py
   :language: python

It would interpret this settings file:

.. literalinclude:: ../examples/accumulation/example.in.nt
   :language: nestedtext

as equivalent to this settings file:

.. literalinclude:: ../examples/accumulation/example.out.nt
   :language: nestedtext


.. _include files example:

Include Files
=============

While *NestedText* does not natively support include files, it is possible to 
implement support if the top-level of your *NestedText* document is a dictionary 
by dedicating one key to specifying the include file or files.  That is shown in 
the example below.

There are two challenges to overcome when processing include files.  First is 
merging the data from the various include files in the face of conflicts. The 
data in this case is a collection of tables, each of which contains rows and 
column.  Tables should be merged, but rows are atomic, so a row replaces an 
earlier row rather than inserting new columns in it.  This is handled by 
*merge_to_depth()*.

The second challenge is error reporting.  Error reports must point to the file 
that contains the error.  This is handled by *find_keymap()*, which searches 
through keymaps in reverse order looking for the desired key path.  
*NestedTextDataError*, described above, is used to report the error.

*read_files()* is used to read the files.  When it reads a file, it first 
processes the include files in order before adding its own data to the combined 
results.

.. literalinclude:: ../examples/includes/includes
   :language: python


.. _pretty printing example:

Pretty Printing
===============

Besides being a readable file format, *NestedText* makes a reasonable display 
format for structured data.  This example further simplifies the output by 
stripping leading multiline string tags.

.. code-block:: python

    >>> import nestedtext as nt
    >>> import re
    >>>
    >>> def pp(data):
    ...     try:
    ...         text = nt.dumps(data, default=repr)
    ...         print(re.sub(r'^(\s*)[>:][ ]?(.*)$', r'\1\2', text, flags=re.M))
    ...     except nt.NestedTextError as e:
    ...         e.report()

    >>> addresses = nt.load('examples/addresses/address.nt')

    >>> pp(addresses['Katheryn McDaniel'])
    position: president
    address:
        138 Almond Street
        Topeka, Kansas 20697
    phone:
        cell: 1-210-555-5297
        work: 1-210-555-8470
    email: KateMcD@aol.com
    additional roles:
        - board member

Stripping leading multiline string tags results in the output no longer being 
valid *NestedText* and so should not be done if the output needs to be readable 
later as *NestedText*..


.. _long lines example:

Long Lines
==========

One of the benefits of *NestedText* is that no escaping of special characters is 
ever needed.  However, you might find it helpful to add your own support for 
removing escaped newlines in multiline strings.  Doing so allows you to keep 
your lines short in the source document so as to make them easier to interpret 
in windows of limited width.

This example uses the pretty-print function from the previous example.

.. code-block:: python

    >>> import nestedtext as nt
    >>> from textwrap import dedent
    >>> from voluptuous import Schema

    >>> document = dedent(r"""
    ...     lorum ipsum:
    ...         > Lorem ipsum dolor sit amet, \
    ...         > consectetur adipiscing elit.
    ...         > Sed do eiusmod tempor incididunt \
    ...         > ut labore et dolore magna aliqua.
    ... """)

    >>> def reverse_escaping(text):
    ...     return text.replace("\\\n", "")

    >>> schema = Schema({str: reverse_escaping})
    >>> data = schema(nt.loads(document))
    >>> pp(data)
    lorum ipsum:
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

An alternative to using a backslash to escape the newline is to simply join 
lines that end with a space.  This might be more natural for non-programmers and 
can work well for prose.

.. code-block:: python

    >>> document = dedent(r"""
    ...     lorum ipsum:
    ...         > Lorem ipsum dolor sit amet,␣
    ...         > consectetur adipiscing elit.
    ...         > Sed do eiusmod tempor incididunt␣
    ...         > ut labore et dolore magna aliqua.
    ... """).replace('␣', ' ')

    >>> def reverse_escaping(text):
    ...     return text.replace(" \n", " ")

    >>> schema = Schema({str: reverse_escaping})
    >>> data = schema(nt.loads(document))
    >>> pp(data)
    lorum ipsum:
        Lorem ipsum dolor sit amet, consectetur adipiscing elit.
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.

In this example, a ``␣`` was used to represent the end of line space so you can 
see it, but it is replaced by a true space before processing the document to 
combine long lines.


.. _voluptuous: https://github.com/alecthomas/voluptuous
.. _voluptuous_errors: https://github.com/KenKundert/voluptuous_errors
.. _pydantic: https://pydantic-docs.helpmanual.io
