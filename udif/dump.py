# Udif Dump
# encoding: utf8
#
# Converts Python data hierarchies to Udif.

# License {{{1
# Copyright (c) 2020 Kenneth S. Kundert
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/.

# Imports {{{1
from inform import indent, Error, is_str, is_collection, is_mapping


# dumps {{{1
def dumps(obj, *, sort_keys=False, renderers=None, default=None, level=0):
    """Recursively convert object to string with reasonable formatting.

    Args:
        obj:
            The object to convert.
        sort_keys (bool or func):
            Dictionary items are sorted by their key if *sort_keys* is true.
            If a function is passed in, it is used as the key function.
        renderers (dict):
            A dictionary where the keys are types and the values are render
            functions (functions that take an object and convert it to a string).
            These will be used to convert values to strings during the
            conversion.
        default (str or func):
            The default renderer. Use to render otherwise unrecognized objects
            to strings. If not provided an error will be raised for unsupported
            data types. Typical values are *repr* or *str*. If 'strict' is
            specified then only dictionaries, lists, strings, and those types
            specified in *renderers* are allowed. If *default* is not specified
            then a broader collection of value types are supported, including
            *None*, *bool*, *int*, *float*, and *list*- and *dict*-like objects.
        level (int):
            The indent level.  When dumps is invoked recursively this is used to
            increment the level and so the indent.  Generally not specified by
            the user, but can be useful in unusual situations to specify an
            initial indent.

    **Example**::

        >>> import udif

        >>> try:
        ...     print(udif.dumps({'a': [0, 1], 'b': [2, 3, 4]}))
        ... except udif.Error as e:
        ...     e.report()
        a:
            - 0
            - 1
        b:
            - 2
            - 3
            - 4

    *dumps* has built in support for the base Python types of *None*, *bool*,
    *str*, *float*, *list*, *tuple*, *set*, and *dict*.  If *default*='strict'
    is specified, that list shrinks to *str*, *list*, and *dict*.

    You must make special arrangements to handle objects of other types.  There
    are two approaches that can be used separately or together. You can specify
    a default renderer that converts any unknown object type to a string.

    **Example**::

        >>> class Color:
        ...     def __init__(self, color):
        ...         self.color = color
        ...     def __repr__(self):
        ...         return f'Color({self.color!r})'
        ...     def __str__(self):
        ...         return self.color

        >>> data = {'key': 42, 'value': 3.1415926, 'valid': True, 'color': Color('red')}
        >>> try:
        ...     print(udif.dumps(data))
        ... except udif.Error as e:
        ...     print(str(e))
        unsupported type: Color('red').

        >>> print(udif.dumps(data, default=repr))
        key: 42
        value: 3.1415926
        valid: True
        color: Color('red')

        >>> print(udif.dumps(data, default=str))
        key: 42
        value: 3.1415926
        valid: True
        color: red

    You may also specify a dictionary of renderers.

    **Example**::

        >>> renderers = {
        ...     bool: lambda b: 'yes' if b else 'no',
        ...     int: hex,
        ...     float: lambda f: f'{f:0.3}',
        ...     Color: lambda c: c.color,
        ... }

        >>> try:
        ...     print(udif.dumps(data, renderers=renderers))
        ... except udif.Error as e:
        ...     e.report()
        key: 0x2a
        value: 3.14
        valid: yes
        color: red

    """

    # define sort function
    if sort_keys:
        def sort(keys):
            return sorted(keys, key=sort_keys if callable(sort_keys) else None)
    else:
        def sort(keys):
            return keys

    # define object type identification functions
    if default == 'strict':
        is_a_dict = lambda obj: isinstance(obj, dict)
        is_a_list = lambda obj: isinstance(obj, list)
        is_a_str = lambda obj: isinstance(obj, str)
        is_a_scalar = lambda obj: False
    else:
        is_a_dict = is_mapping
        is_a_list = is_collection
        is_a_str = is_str
        is_a_scalar = lambda obj: obj is None or isinstance(obj, (bool, int, float))
        if is_str(default):
            raise NotImplementedError(default)

    # define dumps function for recursion
    def rdumps(v):
        return dumps(
            v,
            sort_keys = sort_keys,
            renderers = renderers,
            default = default,
            level = level + 1
        )

    # render string
    def render_str(s, is_key=False):
        stripped = s.strip(' ')
        if is_key:
            if '\n' in s:
                raise Error(s, template='keys must not contain newlines.', culprit=repr(s))
            if (
                not s
                or len(stripped) < len(s)
                or s[0] == "#"
                or s.startswith("- ")
                or s.endswith(":")
            ):
                return repr(s)
        if len(stripped) < len(s):
            return repr(s)
        return s

    def add_prefix(prefix, suffix):
        # A simple formatting of dict and list items will result in a space
        # after the colon or dash if the value is placed on next line.
        # This, function simply eliminates that space.
        if not suffix or suffix.startswith("\n"):
            return prefix + suffix
        return prefix + " " + suffix

    # render content
    error = None
    content = ''
    render = renderers.get(type(obj)) if renderers else None
    if render is False:
        error = "unsupported type: {!r}."
    elif render:
        content = render(obj)
    elif is_a_dict(obj):
        content = "\n".join(
            add_prefix(render_str(k, True) + ":", rdumps(obj[k]))
            for k in sort(obj)
        )
    elif is_a_list(obj):
        content = "\n".join(
            add_prefix("-", rdumps(v))
            for v in obj
        )
    elif is_a_str(obj):
        if "\n" in obj:
            content = indent(obj, '> ')
        else:
            content = obj
    elif is_a_scalar(obj):
        content = str(obj)
    elif default and callable(default):
        if level == 0:
            error = 'expected dictionary or list.'
        content = default(obj)
    else:
        error = "unsupported type: {!r}."

    if level == 0:
        if not is_collection(obj):
            error = 'expected dictionary or list.'
    else:
        if is_collection(obj) or '\n' in content:
            content = "\n" + indent(content)
        else:
            content = render_str(content)

    if error:
        raise Error(obj, template=error, codicil=repr(obj))

    return content
