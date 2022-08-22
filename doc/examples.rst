********
Examples
********

.. currentmodule:: nestedtext

.. _voluptuous example:

Validate with *Voluptuous*
==========================

This example shows how to use voluptuous_ to validate and parse a *NestedText* 
file and it demonstrates how to use the *keymap* argument from :func:`loads` or 
:func:`load` to add location information to *Voluptuous* error messages.

The input file is the same as in the previous example, i.e. deployment settings 
for a web server:

.. literalinclude:: ../examples/deploy.nt
   :language: nestedtext

Below is the code to parse this file.  Note how the structure of the data is 
specified using basic Python objects.  The :func:`Coerce()` function is 
necessary to have Voluptuous convert string input to the given type; otherwise 
it would simply check that the input matches the given type:

.. literalinclude:: ../examples/deploy_voluptuous.py
   :language: python

This produces the same result as in the previous example.


.. _pydantic example:

Validate with *Pydantic*
========================

This example shows how to use pydantic_ to validate and parse a *NestedText* 
file.  The file in this case specifies deployment settings for a web server:

.. literalinclude:: ../examples/deploy.nt
   :language: nestedtext

Below is the code to parse this file.  Note that basic types like integers, 
strings, Booleans, and lists are specified using standard type annotations.  
Dictionaries with specific keys are represented by model classes, and it is 
possible to reference one model from within another.  Pydantic_ also has 
built-in support for validating email addresses, which we can take advantage of 
here:

.. literalinclude:: ../examples/deploy_pydantic.py
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


.. _json-to-nestedtext:

JSON to NestedText
==================

This example implements a command-line utility that converts a *JSON* file to 
*NestedText*.  It demonstrates the use of :func:`dumps()` and 
:exc:`NestedTextError`.

.. literalinclude:: ../examples/json-to-nestedtext
   :language: python

Be aware that not all *JSON* data can be converted to *NestedText*, and in the 
conversion much of the type information is lost.

*json-to-nestedtext* can be used as a JSON pretty printer:

.. code-block:: text

    > json-to-nestedtext < fumiko.json
    treasurer:
        name: Fumiko Purvis
        address:
            > 3636 Buffalo Ave
            > Topeka, Kansas 20692
        phone: 1-268-555-0280
        email: fumiko.purvis@hotmail.com
        additional roles:
            - accounting task force


.. _nestedtext-to-json:

NestedText to JSON
==================

This example implements a command-line utility that converts a *NestedText* file 
to *JSON*.  It demonstrates the use of :func:`load()` and 
:exc:`NestedTextError`.

.. literalinclude:: ../examples/nestedtext-to-json
   :language: python


.. _csv-to-nestedtext:

CSV to NestedText
=================

This example implements a command-line utility that converts a *CSV* file to 
*NestedText*.  It demonstrates the use of the *converters* argument to 
:func:`dumps()`, which is used to cull empty dictionary fields.

.. literalinclude:: ../examples/csv-to-nestedtext
   :language: python


.. _parametrize-from-file:

PyTest
======

This example highlights a PyTest_ package parametrize_from_file_ that allows you 
to neatly separate your test code from your test cases; the test cases being 
held in a *NestedText* file.  Since test cases often contain code snippets, the 
ability of *NestedText* to hold arbitrary strings without the need for quoting 
or escaping results in very clean and simple test case specifications.  Also, 
use of the *eval* function in the test code allows the fields in the test cases 
to be literal Python code.

The test cases:

.. literalinclude:: ../examples/test_misc.nt
   :language: nestedtext

And the corresponding test code:

.. literalinclude:: ../examples/test_misc.py
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

    >>> addresses = nt.load('examples/address.nt')

    >>> pp(addresses['Katheryn McDaniel'])
    position: president
    address:
        138 Almond Street
        Topeka, Kansas 20697
    phone:
        cell: 1-210-555-5297
        home: 1-210-555-8470
    email: KateMcD@aol.com
    additional roles:
        - board member


.. _long lines example:

Long Lines
==========

One of the benefits of *NestedText* is that no escaping of special characters is 
ever needed.  However, you might find it helpful to add your own support for 
removing escaped newlines in multi-line strings.  Doing so would allow you to 
keep your lines short in the source document so as to make them easier to 
interpret in windows of limited width.

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


.. _normalizing keys:

Normalizing keys
================

With data files created by non-programmers it is often desirable to allow 
a certain amount of flexibility in the keys.  For example, you may wish to 
ignore case and be tolerant of extra spacing.  However, the end applications 
often needs the keys to be specific values.  It is possible to normalize the 
keys using a schema, but this can interfere with error reporting.  Imagine there 
is an error in the value associated with a set of keys, if the keys have been 
changed by the schema the *keymap* can no longer be used to convert the keys 
into a line number for an error message.  *NestedText* provides the 
*normalize_key* argument to :func:`load` and :func:`loads` to address this 
issue.  It allows you to pass in a function that normalizes the keys before the 
*keymap* is created, releasing the schema from that task.

The following contact look-up program demonstrates both the normalization of 
keys and the associated error reporting.  In this case, the first level of keys 
contains the names of the contacts and should not be normalized. Keys at all 
other levels are considered keywords and so should be normalized.

.. literalinclude:: ../examples/address
   :language: python

This program takes a name as a command line argument and prints out the 
corresponding address.  It uses the pretty print idea from the previous section 
to render the contact information.  *Voluptuous* checks the validity of the 
contacts database, which is shown next. Notice the variability in the keys given 
in Fumiko's entry:

.. literalinclude:: ../examples/address.nt
   :language: nestedtext

Now, requesting Fumiko's contact information gives::

    Fumiko Purvis
        position: treasurer
        address:
            3636 Buffalo Ave
            Topeka, Kansas 20692
        phone: 1-268-555-0280
        email: fumiko.purvis@hotmail.com
        additional roles:
            - accounting task force

Notice that other than Fumiko's name, the displayed keys are all normalized.


.. _postmortem example:

References
==========

This example illustrates how one can implement references or macros in 
*NestedText*.  A reference allows you to define some content once and insert 
that content multiple places in the document.  This example also demonstrates 
a slightly different way to implement validation and conversion on a per field 
basis with voluptuous_.  Finally, it includes key normalization, which allows 
the keys to be case insensitive and contain white space even though the program 
that uses the data prefers the keys to be lower case identifiers.  The 
*normalize_key* function passed to :meth:`load` is used to transform the keys to 
the desired form.

PostMortem_ is a program that generates a packet of information that is securely 
shared with your dependents in case of your death.  Only the settings processing 
part of the package is shown here.  Here is a configuration file that Odin might 
use to generate packets for his wife and kids:

.. literalinclude:: ../examples/postmortem.nt
    :language: nestedtext

Notice that *estate docs* is defined at the top level. It is not a *PostMortem* 
setting; it simply defines a value that will be interpolated into a setting 
later. The interpolation is done by specifying ``@`` along with the name of the 
reference as a value.  So for example, in *recipients* *attach* is specified as 
``@ estate docs``.  This causes the list of estate documents to be used as 
attachments.  The same thing is done in *sign with*, which interpolates *my gpg 
ids*.

Here is the code for validating and transforming the *PostMortem* settings:

.. literalinclude:: ../examples/postmortem
   :language: python

This code uses *expand_settings* to implement references, and it uses the 
*Voluptuous* schema to clean and validate the settings and convert them to 
convenient forms. For example, the user could specify *attach* as a string or 
a list, and the members could use a leading ``~`` to signify a home directory.  
Applying *to_paths* in the schema converts whatever is specified to a list and 
converts each member to a pathlib_ path with the ``~`` properly expanded.

Notice that the schema is defined in a different manner that the above examples.  
In those, you simply state which type you are expecting for the value and you 
use the *Coerce* function to indicate that the value should be cast to that type 
if needed. In this example, simple functions are passed in that perform 
validation and coercion as needed.  This is a more flexible approach and allows 
better control of the error messages.

Here are the processed settings:

.. code-block:: python

    {'my_gpg_ids': ['odin@norse-gods.com'],
     'recipients': {'Frigg': {'attach': [PosixPath('/home/ken/home/estate/trust.pdf'),
                                         PosixPath('/home/ken/home/estate/will.pdf'),
                                         PosixPath('/home/ken/home/estate/deed-valhalla.pdf')],
                              'category': 'wife',
                              'email': ['frigg@norse-gods.com'],
                              'networth': 'odin'},
                    'Loki': {'attach': [PosixPath('/home/ken/home/estate/trust.pdf'),
                                        PosixPath('/home/ken/home/estate/will.pdf'),
                                        PosixPath('/home/ken/home/estate/deed-valhalla.pdf')],
                             'category': 'kids',
                             'email': ['loki@norse-gods.com']},
                     'Thor': {'attach': [PosixPath('/home/ken/home/estate/trust.pdf'),
                                         PosixPath('/home/ken/home/estate/will.pdf'),
                                         PosixPath('/home/ken/home/estate/deed-valhalla.pdf')],
                              'category': 'kids',
                              'email': ['thor@norse-gods.com']}}}


.. _voluptuous: https://github.com/alecthomas/voluptuous
.. _pydantic: https://pydantic-docs.helpmanual.io
.. _PyTest: https://docs.pytest.org
.. _parametrize_from_file: https://parametrize-from-file.readthedocs.io
.. _PostMortem: https://github.com/kenkundert/postmortem
.. _pathlib: https://docs.python.org/3/library/pathlib.html
