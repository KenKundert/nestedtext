Programmer's Interface
======================


Reader
------

.. autofunction:: nestedtext.loads


Writer
------

.. autofunction:: nestedtext.dumps


Exception
---------

*NestedText* imports the *Error* exception from `inform 
<https://inform.readthedocs.io/en/stable/api.html#exceptions>`_ and renames it 
*NestedTextError*.  You can find more documentation on what you can do with this 
exception there.

.. autoexception:: nestedtext.NestedTextError
    :members:

.. ignore the following (there is only one method, so no need for TOC)
   .. autoclasstoc::
