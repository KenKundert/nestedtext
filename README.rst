Udif: A Human Readable and Writable Data Interchange Format
===========================================================

Provides a file format for exchanging data held in strings, lists, and 
dictionaries.  In this way it is similar to JSON, YaML, or StrictYaML, but with 
a restricted set of supported data types, the file format is simpler. It is 
designed to be easy to enter with a text editor and easy to read.  The small 
number of data types supported means that are only a small number of rules and 
exceptions that need to be remembered when creating a file.  The result is 
a data file that can be created, modified, or viewed  with a text editor and can 
be understood and used by both programmers and non-programmers.

A dictionary is a collection of dictionary items, which are key/value pairs 
where the key and value are separated by a colon and the value is terminated by 
an end of line. The colon must be followed by a space or a newline to act as the 
key/value separator. So for example::

    name: Katheryn McDaniel
    phone: 1-210-835-5297
    email: KateMcD@aol.com

In this example both the keys and values are strings.  Keys are always strings, 
but as shown in a bit, the values may be strings, dictionaries or lists.

A list is a collection of list items, which are values that are introduced with 
a dash and end at the end of line. So for example::

    - Alabama
    - Alaska
    - Arizona
    - Arkansas

Values may be multi-line strings.  A multi-line string is a newline followed by 
one or more indented text lines. It ends when the indentation ends::

    name: Katheryn McDaniel
    address:
        138 Almond Street
        Topika, Kansas 20697
    phone: 1-210-835-5297
    email: KateMcD@aol.com

Normally multi-line strings would have neither leading or trailing newlines.  
However, you can place blank lines at the start or end of the string to add such 
newlines.

A value can also be a list or another dictionary::

    president:
        name: Katheryn McDaniel
        address:
            138 Almond Street
            Topika, Kansas 20697
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
            2586 Marigold Land
            Topika, Kansas 20697
        phone: 1-470-974-0398
        email: margarett.hodge@uk.edu
        kids:
            - Arnie
            - Zach
            - Maggie

Dictionaries and lists can be nested to an arbitrary depth.

Unspecified values are converted to None. Be aware that a blank line that 
follows a dictionary or list item without a value is treated as a multi-line 
string. So the following::

    days:
        - Monday
        - Tuesday
        -
        - Thursday
        - Friday

becomes ``{'days': ['Monday', 'Tuesday', None, 'Wednesday', 'Friday']}``, 
whereas::

    days:
        - Monday

        - Tuesday

        -

        - Thursday

        - Friday

becomes ``{'days': ['Monday', 'Tuesday', '', 'Wednesday', 'Friday']}``.


Indentation is always a multiple of 4 spaces and you can only increase one level 
at a time. Thus the start of a key, a list item dash or the start of a string 
always starts after exactly a multiple of 4 spaces.  You can start the lines in 
your multi-line strings after the point were they are expected to begin to add 
leading spaces to your string. For example:

    greeting: Dearest Katherine:
    body:
            It has been such a long time. I am very much looking forward to
        seeing both you and Margaret again.
    closing: See you soon.

In this example, the value of *body* is a multi-line string for which the first 
line is indented by 4 spaces.  The second line in *body* has no leading space.
In other words, on multi-line strings, the indentation required by this format 
is removed from the each line in the string, but any indentation in excess of 
what is required by the format is retained. Also retained is any trailing space 
on each line.  This differs from single line strings: leading and trailing 
spaces are trimmed from single line strings.

If a key contains a colon or a leading space, you can add quotes (either single 
or double quotes) to clarify the extent of the key.  This is only necessary if 
the quote or dash in the key is followed by a space or if the key begins or ends 
with spaces.  Spaces before or after a key or single-line string value are 
ignored. They can be included by quoting the values.  Either single or double 
matching quotes may be used. For example::

    sep: ' — '
    '- key: ': "- value: "

Blank lines within dictionaries or lists are ignored, but in multi-line strings 
blank lines act to continue the string even if no indentation is present.  Lines 
that start with a hash ``#`` are ignored.

Also notice in the last example that the value for *greeting* ends in a colon.  
This does not represent an issue. Only a hash as the first character on a line, 
a leading dash-space on a line, or the first colon-space are treated as special.

Here is typical example::

    # backup settings for root
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
        trouper segregate militia airway pricey sweetmeat tartan bookstall
        obsession charlady twosome silky puffball grubby ranger notation
        rosebud replicate freshen javelin abbot autocue beater byway

Notice that even though some values are given as integers, their values are 
retained as strings.

You can read a data file using:

    >>> import udif
    >>> from inform import display, fatal, os_error, render

    >>> filename = 'filename'
    >>> try:
    ...     with open(filename) as f
    ...         contents = f.read()
    ...     data = udif.loads(contents, filename)
    >>> except OSError as e:
    ...     fatal(os_error(e))
    >>> except udif.Error as e:
    ...     e.report()

    >>> display(render(data))
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

A rendering function for converting Python dictionaries, lists and strings to 
Udif format is planned but not yet available.


Releases
--------

**Latest development release**:
    | Version: 0.0.0
    | Released: 2020-08-24


Questions
---------

Should I use ': ' or '=' for dictionary items?  '=' may look more normal.

Should I use '- ' or '# ', '~ ', or '. ', or '* ' for list items? Some of the 
alternatives may be used less commonly in values, which can reduce quoting.

Are the restrictions on keys acceptable (single line, only one type of internal 
quotes)?

Should I use 4 spaces as indentation?

What is a good name for this package? human-dif (as in human data interchange 
format) or human-dex (human data exchange format).
