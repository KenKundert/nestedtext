Udif: A Human Readable and Writable Data Interchange Format
===========================================================

.. image:: https://img.shields.io/travis/KenKundert/udif/master.svg
    :target: https://travis-ci.org/KenKundert/udif

.. image:: https://img.shields.io/coveralls/KenKundert/udif.svg
    :target: https://coveralls.io/r/KenKundert/udif


:Author: Ken Kundert
:Version: 0.0.7
:Released: 2020-08-29


Provides a file format for exchanging data held in strings, lists, and 
dictionaries.  In this way it is similar to JSON, YaML, or StrictYaML, but with 
a restricted set of supported data types, the file format is simpler. It is 
designed to be easy to enter with a text editor and easy to read.  The small 
number of data types supported means few rules need be kept in mind when 
creating a file.  The result is a data file that is easily created, modified, or 
viewed with a text editor and be understood and used by both programmers and 
non-programmers.


File Format
-----------

The file starts with a dictionary or a list. A dictionary is a sequence of 
key/value pairs and a list is an sequence of values.

A dictionary contains one or more dictionary items, each on its own line and in 
each the key and value separated by a colon.  The value is optional and the 
colon must be followed by a space or a newline to act as the key/value 
separator. So for example::

    name: Katheryn McDaniel
    phone: 1-210-835-5297
    email: KateMcD@aol.com

In this example both the keys and values are strings.  Keys are always strings, 
but as shown in a bit, the values may be strings, dictionaries or lists.

A list is represented as one or more list items, which are values that are 
introduced with a dash and end at the end of line. So for example::

    - Alabama
    - Alaska
    - Arizona
    - Arkansas

The values in dictionary and list items may be rest of line strings or 
multi-line strings.  Rest of line strings are simply the remaining characters on 
the line exclusive of any leading or trailing spaces.  If you prefer to keep the 
leading or trailing spaces, you can add quotes suing either single or double 
quotes.  An empty value represents an empty string.

::

    before: '• '
    separator: ' — '
    after:

A multi-line string is a newline followed by one or more indented text lines 
where each line is introduced with '> '::

    name: Katheryn McDaniel
    address:
        > 138 Almond Street
        > Topika, Kansas 20697
    phone: 1-210-835-5297
    email: KateMcD@aol.com

Normally multi-line strings have neither leading or trailing newlines.  However, 
you can place empty strings at the start or end of the string to add such 
newlines::

    Yogi Berra:
        >
        > The future ain’t what it used to be.
        >

In strings, the initial '> ' is removed. Any spaces that follow would be 
included in the string.  For example.::

    greeting: Dearest Katherine:
    body:
        >     It has been such a long time. I am very much looking forward to
        > seeing both you and Margaret again.
    closing: See you soon.
    signature: -Rupert

In this example, the value of *body* is a multi-line string for which the first 
line is indented by 4 spaces.  The second line in *body* has no leading space.

A value can also be a list or another dictionary::

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
            > 2586 Marigold Land
            > Topika, Kansas 20697
        phone: 1-470-974-0398
        email: margarett.hodge@uk.edu
        kids:
            - Arnie
            - Zach
            - Maggie

Dictionaries and lists can be nested to an arbitrary depth.

Blank lines and lines whose first character is a hash ``#`` are ignored.

Also notice in the last example the value for *greeting* ends in a colon.  This 
does not represent an issue. Only a hash as the first character on a line, 
a leading dash-space or greater-space on a line, or the first non-quoted 
colon-space are treated as special.

Multiline keys are not supported; a key must not contain a newline. In addition, 
all keys in the same dictionary must be unique. If a key contains leading or 
trailing spaces, a leading '- ' or '> ', or a ': ' anywhere in the key, you 
should quote the key.  Either single or double matching quotes may be used.  
Single line string values should also be quoted in leading or trailing spaces 
are significant, otherwise those spaces are removed. The quotes clarify the 
extent of the value.
For example::

    sep: ' — '
    '- key: ': "- value: "

Unlike with single-line strings, any leading or trailing white space on the 
lines in a multi-line string is retained.

It is highly recommended that each level of indentation be represented by 
a consistent number of spaces with the suggested number being 4. However, it is 
not required. Any increase in the number of spaced in the indentation represents 
an indent and any decrease represents a dedent. Only spaces are allowed in the 
indentation.  Specifically, tabs are not allowed in the indentation and they 
cannot follow a colon, dash, or greater to form a dictionary, list, or 
multi-line string tag, but can be used elsewhere.

Here is typical example::

    >>> contents = """
    ... # backup settings for root
    ... src_dir: /
    ... excludes:
    ...     - /dev
    ...     - /home/*/.cache
    ...     - /root/*/.cache
    ...     - /proc
    ...     - /sys
    ...     - /tmp
    ...     - /var/cache
    ...     - /var/lock
    ...     - /var/run
    ...     - /var/tmp
    ... keep:
    ...     hourly: 24
    ...     daily: 7
    ...     weekly: 4
    ...     monthly: 12
    ...     yearly: 5
    ... passphrase:
    ...     > trouper segregate militia airway pricey sweetmeat tartan bookstall
    ...     > obsession charlady twosome silky puffball grubby ranger notation
    ...     > rosebud replicate freshen javelin abbot autocue beater byway
    ... """

Notice that even though some values are given as integers, their values are 
retained as strings.


Reader
------

You can read a data file using::

    >>> import udif
    >>> from inform import render

    >>> try:
    ...     data = udif.loads(contents)
    ... except udif.Error as e:
    ...     e.report()

    >>> print(render(data))
    {
        'src_dir': '/',
        'excludes': [
            '/dev',
            '/home/*/.cache',
            '/root/*/.cache',
            '/proc',
            '/sys',
            '/tmp',
            '/var/cache',
            '/var/lock',
            '/var/run',
            '/var/tmp',
        ],
        'keep': {
            'hourly': '24',
            'daily': '7',
            'weekly': '4',
            'monthly': '12',
            'yearly': '5',
        },
        'passphrase': """\
            trouper segregate militia airway pricey sweetmeat tartan bookstall
            obsession charlady twosome silky puffball grubby ranger notation
            rosebud replicate freshen javelin abbot autocue beater byway\
        """,
    }

*loads()* takes an optional second argument, *culprit*. If specified, it will be 
prepended to any error messages. It is often used to designate the source of 
*contents*. For example,if *contents* were read from a file, *culprit* would be 
the file name.


Writer
------

You can use `udif.dumps()` to convert a data structure consisting of 
dictionaries, lists, and strings::

    >>> try:
    ...     print(udif.dumps(data))
    ... except udif.Error as e:
    ...     e.report()
    src_dir: /
    excludes:
        - /dev
        - /home/*/.cache
        - /root/*/.cache
        - /proc
        - /sys
        - /tmp
        - /var/cache
        - /var/lock
        - /var/run
        - /var/tmp
    keep:
        hourly: 24
        daily: 7
        weekly: 4
        monthly: 12
        yearly: 5
    passphrase:
        > trouper segregate militia airway pricey sweetmeat tartan bookstall
        > obsession charlady twosome silky puffball grubby ranger notation
        > rosebud replicate freshen javelin abbot autocue beater byway

There are several mechanisms available for handling objects that are otherwise 
unsupported by the format.

By default, *dumps* is configured to be rather forgiving, so it will render many 
of the base Python data types, such as *None*, *bool*, *int*, *float* and 
list-like options such as *tuple* and *set*. This implies that a round trip 
through *dumps* and *loads* could result in the types of values being 
transformed. You can prevent this by passing `default='strict'` to *dump*. Doing 
so means that values that are not dictionaries, lists, or strings generate 
exceptions::

    >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}

    >>> try:
    ...     print(udif.dumps(data))
    ... except udif.Error as e:
    ...     e.report()
    key: 42
    value: 3.1415926
    valid: True

    >>> try:
    ...     print(udif.dumps(data, default='strict'))
    ... except udif.Error as e:
    ...     print(str(e))
    42: unsupported type.

Alternatively, you can specify a function to *default*, which is used to convert 
values to strings.  It is used if no other converter is available.  Typical 
values are *str* and *repr*::

    >>> class Color:
    ...     def __init__(self, color):
    ...         self.color = color
    ...     def __repr__(self):
    ...         return f'Color({self.color!r})'
    ...     def __str__(self):
    ...         return self.color

    >>> data['house'] = Color('red')
    >>> print(udif.dumps(data, default=repr))
    key: 42
    value: 3.1415926
    valid: True
    house: "Color('red')"

    >>> print(udif.dumps(data, default=str))
    key: 42
    value: 3.1415926
    valid: True
    house: red

You can also specify a dictionary of renderers. The dictionary maps the object 
type to a render function::

    >>> renderers = {
    ...     bool: lambda b: 'yes' if b else 'no',
    ...     int: hex,
    ...     float: lambda f: f'{f:0.3}',
    ...     Color: lambda c: c.color,
    ... }

    >>> try:
    ...    print(udif.dumps(data, renderers=renderers))
    ... except udif.Error as e:
    ...     e.report()
    key: 0x2a
    value: 3.14
    valid: yes
    house: red

Both *default* and *renderers* may be used together. *renderers* has priority 
over the built-in types and *default*. When a function is specified as 
*default*, it is always applied as a last resort.


Releases
--------

**Latest development release**:
    | Version: 0.0.7
    | Released: 2020-08-29
