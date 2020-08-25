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

# dump {{{1
def dump(obj, *, sort=None, renderers=None, default=None, level=0):
    """Recursively convert object to string with reasonable formatting.

    Args:
        obj:
            The object to dump
        sort (bool):
            Dictionary keys and set values are sorted if *sort* is *True*.
            Sometimes this is not possible because the values are not
            comparable, in which case *dump* reverts to using the natural
            order.
        level (int):
            The indent level.
            If not specified and dump is called recursively the indent
            will be incremented, otherwise the indent is 0.
        renderers (dict):
            A dictionary where the keys are types and the values are render
            functions (functions that take an object and convert it to a string).
            These will be used to convert values to strings during the dump.
        default (func):
            The default renderer. Use to render otherwise unrecognized objects
            to strings. If not provided an error will be raised for unsupported
            data types. Typical values are *repr* or *str*.

    **Example**::

        >>> import udif

        >>> try:
        ...     print(udif.dump({'a': (0, 1), 'b': [2, 3, 4]}))
        ... except udif.Error as e:
        ...     e.report()
        a:
            - 0
            - 1
        b:
            - 2
            - 3
            - 4

    *dump* has built in support for the base Python types of (*None*,
    *int*, *str*, *set*, *tuple*, *list*, and *dict*.  You will need to make special
    arrangements to handle objects of other types. There are two approaches that can
    be used separately or together. You can specify a default renderer that used to convert
    any unknown object type to a string.

    **Example**::

        >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}
        >>>
        >>> try:
        ...     print(udif.dump(data))
        ... except udif.Error as e:
        ...     print(str(e))
        unsupported type: 3.1415926

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
    if sort:
        def order(keys):
            try:
                return sorted(keys)
            except TypeError:
                # keys are not homogeneous, cannot sort
                return keys
    else:
        def order(keys):
            return keys

    # define dump function for recursion
    def rdump(v):
        return dump(v, sort=sort, renderers=renderers, default=default, level=level+1)

    # render string
    def render_str(s, is_key=False):
        stripped = s.strip()
        if not s or len(stripped) < len(s):
            return repr(s)
        if is_key:
            if '\n' in s:
                raise Error(s, template='keys must not contain newlines.')
            if s[0] == "#" or s.startswith("- ") or s.endswith(":"):
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
    render = renderers.get(type(obj), None) if renderers else None
    if render:
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
        if sort and isinstance(obj, set):
            obj = order(obj)
        content = format_multiline_entry(
            "\n".join(
                add_prefix("-", rdump(v))
                for v in obj
            )
        )
    elif isinstance(obj, str):
        if "\n" in obj:
            content = format_multiline_entry(obj)
        else:
            content = render_str(obj)
    elif isinstance(obj, int) and not isinstance(obj, bool):
        content = str(obj)
    elif obj is None:
        content = ""
    elif default:
        content = default(obj)
        if '\n' in content:
            content = format_multiline_entry(content)
        else:
            content = render_str(content)
    else:
        raise Error(f"unsupported type: {obj!r}")

    return content
