*Udif* File Format
------------------

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
        > trouper segregate militia airway pricey sweetmeat tartan bookstall
        > obsession charlady twosome silky puffball grubby ranger notation
        > rosebud replicate freshen javelin abbot autocue beater byway

Notice that even though some values are given as integers, their values are 
retained as strings.
