********
Examples
********

.. currentmodule:: nestedtext

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

.. _voluptuous example:

Validate with *Voluptuous*
==========================

This example shows how to use voluptuous_ to validate and parse a *NestedText* 
file.  The input file is the same as in the previous example, i.e. deployment 
settings for a web server:

.. literalinclude:: ../examples/deploy.nt
   :language: nestedtext

Below is the code to parse this file.  Note how the structure of the data is 
specified using basic Python objects.  The :func:`Coerce()` function is 
necessary to have voluptuous convert string input to the given type; otherwise 
it would simply check that the input matches the given type:

.. literalinclude:: ../examples/deploy_voluptuous.py
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

The presence of this example should not be taken as a suggestion that 
*NestedText* is a replacement for *JSON*.  Be aware that not all *JSON* data can 
be converted to *NestedText*, and in the conversion all type information is 
lost.

.. _nestedtext-to-json:

NestedText to JSON
==================

This example implements a command-line utility that converts a *NestedText* file 
to *JSON*.  It demonstrates the use of :func:`load()` and 
:exc:`NestedTextError`.

.. literalinclude:: ../examples/nestedtext-to-json
   :language: python


.. _cryptocurrency example:

Cryptocurrency holdings
=======================

This example implements a command-line utility that displays the current value 
of cryptocurrency holdings.  The program starts by reading a settings file held 
in ``~/.config/cc`` that in this case holds:

.. code-block:: nestedtext

    holdings:
        - 5 BTC
        - 50 ETH
        - 50,000 XLM
    currency: USD
    date format: h:mm A, dddd MMMM D
    screen width: 90

This file, of course, is in *NestedText* format.  After being read by 
:func:`load()` it is processed by a voluptuous_ schema that does some checking 
on the form of the values specified and then converts the holdings to a list of 
`QuantiPhy <https://quantiphy.readthedocs.io>`_ quantities.  The latest prices 
are then downloaded from `cryptocompare <https://www.cryptocompare.com>`_, the 
value of the holdings are computed, and then displayed. The result looks like 
this::

    Holdings as of 11:18 AM, Wednesday September 2.
    5 BTC = $56.8k @ $11.4k/BTC    68.4% ████████████████████████████████████▏
    50 ETH = $21.7k @ $434/ETH     26.1% █████████████▊
    50 kXLM = $4.6k @ $92m/XLM     5.5%  ██▉
    Total value = $83.1k.

And finally, the code:

.. literalinclude:: ../examples/cryptocurrency
   :language: python


.. _postmortem example:

PostMortem
==========

This example illustrates how one can implement references in *NestedText*.  
A reference allows you to define some content once and insert that content 
multiple places in the document.  The example also demonstrates a slightly 
different way to implement validation and conversion on a per field basis with 
voluptuous_.

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

.. literalinclude:: ../examples/postmortem.py
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

    {'my gpg ids': ['odin@norse-gods.com'],
    'name template': '{name}-{now:YYMMDD}',
    'recipients': {'frigg': {'attach': [PosixPath('/home/ken/home/estate/trust.pdf'),
                                        PosixPath('/home/ken/home/estate/will.pdf'),
                                        PosixPath('/home/ken/home/estate/deed-valhalla.pdf')],
                            'category': 'wife',
                            'email': ['frigg@norse-gods.com'],
                            'networth': 'odin'},
                    'loki': {'attach': [PosixPath('/home/ken/home/estate/trust.pdf'),
                                        PosixPath('/home/ken/home/estate/will.pdf'),
                                        PosixPath('/home/ken/home/estate/deed-valhalla.pdf')],
                            'category': 'kids',
                            'email': ['loki@norse-gods.com']},
                    'thor': {'attach': [PosixPath('/home/ken/home/estate/trust.pdf'),
                                        PosixPath('/home/ken/home/estate/will.pdf'),
                                        PosixPath('/home/ken/home/estate/deed-valhalla.pdf')],
                            'category': 'kids',
                            'email': ['thor@norse-gods.com']}},
    'sign with': 'odin@norse-gods.com'}


.. _pydantic: https://pydantic-docs.helpmanual.io
.. _voluptuous: https://github.com/alecthomas/voluptuous
.. _PostMortem: https://github.com/kenkundert/postmortem
.. _pathlib: https://docs.python.org/3/library/pathlib.html
