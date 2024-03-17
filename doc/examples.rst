********
Examples
********

.. doctests:

   >>> import nestedtext as nt

.. currentmodule:: nestedtext

.. _json-to-nestedtext example:

JSON to NestedText
==================

This example implements a command-line utility that converts a *JSON* file to 
*NestedText*.  It demonstrates the use of :func:`dumps()` and 
:exc:`NestedTextError`.

.. literalinclude:: ../examples/conversion-utilities/json-to-nestedtext
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


.. _nestedtext-to-json example:

NestedText to JSON
==================

This example implements a command-line utility that converts a *NestedText* file 
to *JSON*.  It demonstrates the use of :func:`load()` and 
:exc:`NestedTextError`.

.. literalinclude:: ../examples/conversion-utilities/nestedtext-to-json
   :language: python


.. ignore:
    .. _csv-to-nestedtext example:

    CSV to NestedText
    =================

    This example implements a command-line utility that converts a *CSV* file to 
    *NestedText*.  It demonstrates the use of the *converters* argument to 
    :func:`dumps()`, which is used to cull empty dictionary fields.

    .. literalinclude:: ../examples/conversion-utilities/csv-to-nestedtext
    :language: python


.. _parametrize-from-file example:

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

.. literalinclude:: ../examples/parametrize_from_file/test_misc.nt
   :language: nestedtext

And the corresponding test code:

.. literalinclude:: ../examples/parametrize_from_file/test_misc.py
   :language: python


.. _postmortem example:

PostMortem
==========

PostMortem_ is a program that generates a packet of information that is securely 
shared with your dependents in case of your death.  Only the settings processing 
part of the package is shown here.

This example includes :ref:`references <references>`, :ref:`key normalization 
<normalizing keys>`, and different way to implement validation and conversion on 
a per field basis with voluptuous_.  References allow you to define some content 
once and insert that content multiple places in the document.  Key normalization 
allows the keys to be case insensitive and contain white space even though the 
program that uses the data prefers the keys to be lower case identifiers.

Here is a configuration file that Odin might use to generate packets for his 
wife and kids:

.. literalinclude:: ../examples/postmortem/postmortem.nt
    :language: nestedtext

Notice that *estate docs* is defined at the top level. It is not a *PostMortem* 
setting; it simply defines a value that will be interpolated into settings 
later.  The interpolation is done by specifying ``@`` along with the name of the 
reference as a value.  So for example, in *recipients* *attach* is specified as 
``@ estate docs``.  This causes the list of estate documents to be used as 
attachments.  The same thing is done in *sign with*, which interpolates *my gpg 
ids*.

Here is the code for validating and transforming the *PostMortem* settings.  For 
more on *report_voluptuous_errors*, see :ref:`voluptuous example`.

.. literalinclude:: ../examples/postmortem/postmortem
   :language: python

This code uses *expand_settings* to implement references, and it uses the 
*Voluptuous* schema to clean and validate the settings and convert them to 
convenient forms. For example, the user could specify *attach* as a string or 
a list, and the members could use a leading ``~`` to signify a home directory.  
Applying *to_paths* in the schema converts whatever is specified to a list and 
converts each member to a pathlib_ path with the ``~`` properly expanded.

Notice that the schema is defined in a different manner than in the :ref:`
Volupuous example <voluptuous example>`.  In that example, you simply state 
which type you are expecting for the value and you use the *Coerce* function to 
indicate that the value should be cast to that type if needed. In this example, 
simple functions are passed in that perform validation and coercion as needed.  
This is a more flexible approach that allows better control of the conversions 
and the error messages.

This code does not do any thing useful, it just reads in and expands the 
information contained in the input file.  It simply represents the beginnings of 
a program that would use the specified information to generate the postmortem 
reports.  In this case it simply prints the expanded information in the form of 
a *NestedText* document, which is easier to read that if it were pretty-printed 
as *Python* or *JSON*.

Here are the processed settings:

.. literalinclude:: ../examples/postmortem/postmortem.expanded.nt
   :language: nestedtext


.. _voluptuous: https://github.com/alecthomas/voluptuous
.. _PyTest: https://docs.pytest.org
.. _parametrize_from_file: https://parametrize-from-file.readthedocs.io
.. _pathlib: https://docs.python.org/3/library/pathlib.html
.. _PostMortem: https://github.com/kenkundert/postmortem
