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
from inform import indent, Error


# Globals {{{1
BASIC_RENDERERS = {
    bool: lambda v: str(v),
    int: lambda v: str(v),
    float: lambda v: str(v),
}


# dump {{{1
def dump(obj, *, sort_keys=False, renderers=None, default=None, level=0):
    """Recursively convert object to string with reasonable formatting.

    Args:
        obj:
            The object to dump
        sort_keys (bool):
            Dictionary items are sorted by their key if *sort_keys* is true.
        renderers (dict):
            A dictionary where the keys are types and the values are render
            functions (functions that take an object and convert it to a string).
            These will be used to convert values to strings during the dump.
        default (func):
            The default renderer. Use to render otherwise unrecognized objects
            to strings. If not provided an error will be raised for unsupported
            data types. Typical values are *repr* or *str*.
        level (int):
            The indent level.  When dump is invoked recursively this is used to
            increment the level and so the indent.  Generally not specified by
            the user, but can be useful in unusual situations to specify an
            initial indent.

    **Example**::

        >>> import udif

        >>> try:
        ...     print(udif.dump({'a': ['0', '1'], 'b': ['2', '3', '4']}))
        ... except udif.Error as e:
        ...     e.report()
        a:
            - 0
            - 1
        b:
            - 2
            - 3
            - 4

    *dump* has built in support for the base Python types of *str*, *list*, and
    *dict*.

    You must make special arrangements to handle objects of other types.  There
    are two approaches that can be used separately or together. You can specify
    a default renderer that converts any unknown object type to a string.

    **Example**::

        >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}
        >>>
        >>> try:
        ...     print(udif.dump(data))
        ... except udif.Error as e:
        ...     print(str(e))
        unsupported type: 42

        >>> try:
        ...     print(udif.dump(data, default=repr))
        ... except udif.Error as e:
        ...     e.report()
        key: 42
        value: 3.1415926
        valid: True

    You may also specify a dictionary of renderers.

    **Example**::

        >>> renderers = {
        ...     bool: lambda b: 'yes' if b else 'no',
        ...     int: hex,
        ...     float: lambda f: f'{f:0.3}'
        ... }

        >>> try:
        ...     print(udif.dump(data, renderers=renderers))
        ... except udif.Error as e:
        ...     e.report()
        key: 0x2a
        value: 3.14
        valid: yes

    """

    # define sort function
    if sort_keys:
        def order(keys):
            return sorted(keys, key=sort_keys if callable(sort_keys) else None)
    else:
        def order(keys):
            return keys

    # define dump function for recursion
    def rdump(v):
        return dump(
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

    # adjust formatting based on level
    if level == 0:
        def format_multiline_entry(s):
            return s
    else:
        def format_multiline_entry(s):
            return "\n" + indent(s)

    # render content
    error = None
    render = renderers.get(type(obj)) if renderers else None
    if render is False:
        error = "unsupported type: {!r}"
    elif render:
        content = render(obj)
        if '\n' in content:
            content = format_multiline_entry(content)
        else:
            content = render_str(content)
    elif isinstance(obj, dict):
        content = format_multiline_entry(
            "\n".join(
                add_prefix(render_str(k, True) + ":", rdump(obj[k]))
                for k in order(obj)
            )
        )
    elif isinstance(obj, (list, tuple, set)):
        content = format_multiline_entry(
            "\n".join(
                add_prefix("-", rdump(v))
                for v in obj
            )
        )
    elif isinstance(obj, str):
        if level == 0:
            error = 'expected dictionary or list.'
        if "\n" in obj:
            if obj.startswith('- '):
                error = "multi-line string must not start with '- '."
            content = format_multiline_entry(obj)
        else:
            content = render_str(obj)
    elif default:
        if level == 0:
            error = 'expected dictionary or list.'
        content = default(obj)
        if '\n' in content:
            content = format_multiline_entry(content)
        else:
            content = render_str(content)
    else:
        error = "unsupported type: {!r}"
    if error:
        raise Error(obj, template=error, codicil=repr(obj))

    return content
