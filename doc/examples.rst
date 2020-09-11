********
Examples
********

.. currentmodule:: nestedtext

.. _json-to-nestedtext:

JSON to NestedText
==================

This example implements a command-line utility that converts a *JSON* file to 
*NestedText*.  It demonstrates the use of :func:`dumps()` and 
:exc:`NestedTextError`.

.. literalinclude:: ../examples/json-to-nestedtext
   :language: python


.. _nestedtext-to-json:

NestedText to JSON
==================

This example implements a command-line utility that converts a *NestedText* file 
to *JSON*.  It demonstrates the use of :func:`loads()` and 
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
    screen width: 90

This file, of course, is in *NestedText* format.  After being read by 
:func:`loads()` it is processed by a `Voluptuous 
<https://github.com/alecthomas/voluptuous>`_ schema that does some checking on 
the form of the values specified and then converts the holdings to a list of 
`QuantiPhy <https://quantiphy.readthedocs.io>`_ quantities and the screen width 
to an integer.  The latest prices are then downloaded from `cryptocompare 
<https://www.cryptocompare.com>`_, the value of the holdings are computed, and 
then displayed. The result looks like this::

    Holdings as of 11:18 AM, Wednesday September 2.
    5 BTC = $56.8k @ $11.4k/BTC    68.4% ████████████████████████████████████▏
    50 ETH = $21.7k @ $434/ETH     26.1% █████████████▊
    50 kXLM = $4.6k @ $92m/XLM     5.5%  ██▉
    Total value = $83.1k.

And finally, the code:

.. literalinclude:: ../examples/cryptocurrency
   :language: python
