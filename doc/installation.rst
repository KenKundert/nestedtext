************
Installation
************

.. currentmodule:: nestedtext

::

   pip3 install --user nestedtext


Releases
========

Latest development release
--------------------------

    | Version: 1.3.0
    | Released: 2021-01-02


v1.3 (2021-01-02)
-----------------

    - Move the test cases to a submodule.

    .. note::

        When cloning the *NestedText* repository you should use the --recursive 
        flag to get the *official_tests* submodule::

            git clone --recursive https://github.com/KenKundert/nestedtext.git

        When updating an existing repository, you need to initialize the 
        submodule after doing a pull::

           git submodule update --init --remote tests/official_tests

        This only need be done once.


v1.2 (2020-10-31)
-----------------

    - Treat CR LF, CR, or LF as a line break.
    - Always quote keys that start with a quote.


v1.1 (2020-10-13)
-----------------

    - Add ability to specify return type of :func:`load` and :func:`loads`.
    - Quoted keys are now less restricted.
    - Empty dictionaries and lists are rejected by :func:`dump` and 
      :func:`dumps` except as top-level object if *default* argument is 
      specified as 'strict'.

    .. warning::

        Be aware that this version is not fully backward compatible.  Unlike 
        previous versions, this version allows you to restrict the type of the 
        return value of the :func:`load` and :func:`loads` functions, and the 
        default is 'dict'.  The previous behavior is still supported, but you 
        must explicitly specify `top='any'` as an argument.

        This change results in a simpler return value from :func:`load` and 
        :func:`loads` in most cases. This substantially reduces the chance of 
        coding errors.  It was noticed that it was common to simply assume that 
        the top-level was a dictionary when writing code that used these 
        functions, which could result in unexpected errors when users 
        hand-create the input data. Specifying the return value eliminates this 
        type of error.

        There is another small change that is not backward compatible. The 
        source argument to these functions is now a keyword only argument.


v1.0 (2020-10-03)
-----------------
    - Production release.


v0.6 (2020-09-26)
-----------------
    - Added :func:`load` and :func:`dump`.
    - Eliminated *NestedTextError.get_extended_codicil*.


v0.5 (2020-09-11)
-----------------
    - allow user to manage duplicate keys detected by :func:`loads`.


v0.4 (2020-09-07)
-----------------
    - Change rest-of-line strings to include all characters given, including 
      leading and trailing quotes and spaces.
    - The *NestedText* top-level is no longer restricted to only dictionaries 
      and lists. The top-level can now also be a single string.
    - :func:`loads` now returns *None* when given an empty *NestedText* document.
    - Change :exc:`NestedTextError` attribute names to make them more consistent 
      with those used by JSON package.
    - Added *NestedTextError.get_extended_codicil*.


v0.3 (2020-09-03)
-----------------
    - Allow comments to be indented.


v0.2 (2020-09-02)
-----------------
    - Minor enhancements and bug fixes.


v0.1 (2020-08-30)
-----------------
    - Initial release.
