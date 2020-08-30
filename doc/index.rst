Udif: A Human Readable and Writable Data Interchange Format
===========================================================

| Version: 0.0.8
| Released: 2020-08-30
| Please post all bugs and suggestions at
  `Udif Github <https://github.com/KenKundert/udif/issues>`_
  (or contact me directly at
  `udif@nurdletech.com <mailto://udif@nurdletech.com>`_).


*Udif* is a file format for exchanging data held in strings, lists, and␣
dictionaries.  In this way it is similar to JSON, YaML, or StrictYaML, but with␣
a restricted set of supported data types, the file format is simpler. It is␣
designed to be easy to enter with a text editor and easy to read.  The small␣
number of data types supported means few rules need be kept in mind when␣
creating a file.  The result is a data file that is easily created, modified, or␣
viewed with a text editor and be understood and used by both programmers and␣
non-programmers.

Here is an example of a file that contains a few addresses::

    # Contact information for our officers

    president:
        name: Katheryn McDaniel
        address:
            > 138 Almond Street
            > Topika, Kansas 20697
        phone:
            cell: 1-210-835-5297
            home: 1-210-478-8470
        email: KateMcD@aol.com
        kids:
            - Joanie
            - Terrance

    vice president:
        name: Margaret Hodge
        address:
            > 2586 Marigold Lane
            > Topika, Kansas 20682
        phone: 1-470-974-0398
        email: margarett.hodge@uk.edu
        kids:
            - Arnie
            - Zach
            - Maggie

    treasurer:
        name: Fumiko Purvis
        address:
            > 3636 Buffalo Ave
            > Topika, Kansas 20692
        phone: 1-268-877-0280
        email: fumiko.purvis@hotmail.com
        kids:
            - Lue

The format can hold dictionaries (ordered collections of name/value pairs), 
lists (ordered collections of values) and strings organized hierarchically to 
any depth.  Indentation is used to indicate the hierarchy of the data, and 
simple syntax is used to distinguish the types of data in such a manner that it 
is not easily confused.


Quick Start
-----------

Install with::

   pip3 install udif     -- not available yet


Issues
------

Please ask questions or report problems on `Github 
<https://github.com/KenKundert/quantiphy/issues>`_.


Contributing
------------

The package contains a Python implmentation on *udif*. For *udif* to catch on 
widely, implementation in many language will required. If you like the format 
and have interest in doing so, please consider contributing additional 
implementations, particularly for other languages.


Documentation
-------------

.. toctree::
   :maxdepth: 1

   format
   reader
   writer
   api
   releases

*  :ref:`genindex`
