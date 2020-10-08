********
Examples
********

.. currentmodule:: nestedtext

.. _pydantic example:

Validate with ``pydantic``
==========================

This example shows how to use pydantic_ to validate and parse a *NestedText* 
file.  The file in this case specifies deployment settings for a web server:

.. literalinclude:: ../examples/deploy.nt

Below is the code to parse this file.  Note that basic types like integers, 
strings, booleans, and lists are specified using standard type annotations.  
Dictionaries with specific keys are represented by model classes, and it is 
possible to reference one model from within another.  Pydantic_ also has 
built-in support for validating email addresses, which we can take advantage of 
here:

.. literalinclude:: ../examples/deploy_pydantic.py

This produces the following data structure::

    {'allowed_hosts': ['www.example.com'],
     'database': {'engine': 'django.db.backends.mysql',
                  'host': 'db.example.com',
                  'port': 3306,
                  'user': 'www'},
     'debug': False,
     'secret_key': 't=)40**y&883y9gdpuw%aiig+wtc033(ui@^1ur72w#zhw3_ch',
     'webmaster_email': 'admin@example.com'}
  
.. _voluptuous example:

Validate with ``voluptuous``
============================

This example shows how to use voluptuous_ to validate and parse a *NestedText* 
file.  The input file is the same as in the previous example, i.e. deployment 
settings for a web server:

.. literalinclude:: ../examples/deploy.nt

Below is the code to parse this file.  Note how the structure of the data is 
specified using basic python objects.  The :func:`Coerce()` function is 
necessary to have voluptuous convert string input to the given type; otherwise 
it would simply check that the input matches the given type:

.. literalinclude:: ../examples/deploy_voluptuous.py

This produces the following data structure::

    {'allowed_hosts': ['www.example.com'],
     'database': {'engine': 'django.db.backends.mysql',
                  'host': 'db.example.com',
                  'port': 3306,
                  'user': 'www'},
     'debug': True,
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
========================

This example implements a command-line utility that displays the current value 
of cryptocurrency holdings.  The program starts by reading a settings file held 
in ``~/.config/cc`` that in this case holds::

    holdings:
        - 5 BTC
        - 50 ETH
        - 50,000 XLM
    currency: USD
    date format: h:mm A, dddd MMMM D

This file, of course, is in *NestedText* format.  After being read by 
:func:`loads()` it is processed by a voluptuous_ schema that does some checking 
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


.. _pydantic: https://pydantic-docs.helpmanual.io/
.. _voluptuous: https://github.com/alecthomas/voluptuous
