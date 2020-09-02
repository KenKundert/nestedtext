# encoding: utf8
"""
NestedText: A Human Readable and Writable Data Format
"""

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
import re
from inform import (
    full_stop,
    set_culprit,
    get_culprit,
    is_str,
    is_collection,
    is_mapping,
    Error as NestedTextError,
    Info,
    InformantFactory,
)


# Globals {{{1
__version__ = "0.2.0"
__released__ = "2020-09-02"
__all__ = ['loads', 'dumps', 'NestedTextError']

# loads {{{1
# Converts NestedText into Python data hierarchies.

# constants {{{2
dict_tag = ": "
list_tag = "- "
str_tag = "> "
quoted = "|".join([
    r'"[^"\n]*"',  # "string"
    r"'[^'\n]*'",  # 'string'
])
splitters = (
    quoted,           # "string" or 'string' (must be first)
    dict_tag,         # key/value separator in dictionary item
    list_tag,         # introduces list item
    str_tag,          # introduces a line in a multi-line string
)
splitter = re.compile("(" + "|".join(f"(?:{s})" for s in splitters) + ")")


# debugging utilities {{{2
highlight = InformantFactory(message_color='blue')


def dbg(line, kind):  # pragma: no cover
    if line.depth is None:
        indents = ' '
    else:
        indents = line.depth
    highlight(f'{indents}{kind}{line.num:>4}:{line.text}')


# report {{{2
def report(message, line, *args, loc=None, **kwargs):
    message = full_stop(message)
    if line:
        kwargs['culprit'] = get_culprit(line.num)
        if loc is not None:
            kwargs['codicil'] = f"«{line.text}»\n {loc*' '}↑"
            kwargs['loc'] = loc
        else:
            kwargs['codicil'] = f"«{line.text}»"
        kwargs['line'] = line.text
    else:
        kwargs['culprit'] = get_culprit()  # pragma: no cover
    raise NestedTextError(template=message, *args, **kwargs)


# indentation_error {{{2
def indentation_error(line, depth):
    assert line.depth != depth
    report('invalid indentation.', line, loc=depth)


# is_quoted {{{2
def is_quoted(s):
    return s[:1] in ['"', "'"] and s[:1] == s[-1:]


# join_and_dequote {{{2
def join_and_dequote(l):
    s = "".join(l).strip()
    if is_quoted(s):
        return s[1:-1]
    return s


# Lines class {{{2
class Lines:
    class Line(Info):
        pass

    # constructor {{{3
    def __init__(self, contents):
        self.generator = self.read_lines(contents)
        self.next_line = True
        while self.next_line:
            self.next_line = next(self.generator, None)
            if self.next_line and self.next_line.kind not in ["blank", "comment"]:
                return

    # read_lines() {{{3
    def read_lines(self, contents):
        for lineno, line in enumerate(contents.splitlines()):
            depth = None
            key = None
            value = None
            if line.strip() == "":
                kind = "blank"
                value = "\n"
            elif line[:1] == "#":
                kind = "comment"
                value = line[1:].strip()
            else:
                stripped = line.lstrip()
                depth = len(line) - len(stripped)
                components = splitter.split(line + " ")
                if list_tag == "".join(components[:2]).lstrip(" "):
                    kind = "list item"
                    value = join_and_dequote(components[2:])
                elif str_tag == "".join(components[:2]).lstrip(" "):
                    kind = "string"
                    value = "".join(components[2:])[:-1]
                elif dict_tag in components:
                    kind = "dict item"
                    split_loc = components.index(dict_tag)
                    key = join_and_dequote(components[:split_loc])
                    value = join_and_dequote(components[split_loc + 1 :])
                else:
                    kind = "unrecognized"
                    value = line

            the_line = self.Line(
                text=line, num=lineno+1, kind=kind, depth=depth, key=key, value=value
            )

            # check the indent for non-spaces
            if depth:
                first_non_space = len(line) - len(line.lstrip(" "))
                if first_non_space < depth:
                    report(
                        f'invalid character in indentation: {line[first_non_space]!r}.',
                        the_line,
                        loc = first_non_space
                    )

            yield the_line

    # type_of_next() {{{3
    def type_of_next(self):
        if self.next_line:
            return self.next_line.kind

    # still_within_level() {{{3
    def still_within_level(self, depth):
        if self.next_line:
            return self.next_line.depth >= depth

    # still_within_string() {{{3
    def still_within_string(self, depth):
        if self.next_line:
            return self.next_line.kind == "string" and self.next_line.depth == depth

    # depth_of_next() {{{3
    def depth_of_next(self):
        if self.next_line:
            return self.next_line.depth
        return 0

    # get_next() {{{3
    def get_next(self):
        this_line = self.next_line

        # queue up the next useful line
        # this is needed so type_of_next() and still_within_level() can easily
        # access the next upcoming line.
        while self.next_line:
            self.next_line = next(self.generator, None)
            if not self.next_line or self.next_line.kind not in ["blank", "comment"]:
                break

        if this_line and this_line.kind == "unrecognized":
            report('unrecognized line.', this_line)
        return this_line


# read_value() {{{2
def read_value(lines, depth):
    if lines.type_of_next() == "list item":
        return read_list(lines, depth)
    if lines.type_of_next() == "dict item":
        return read_dict(lines, depth)
    return read_string(lines, depth)


# read_list() {{{2
def read_list(lines, depth):
    data = []
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "list item":
            report("expected list item", line, loc=depth)
        if line.value:
            # dbg(line, 'lv')
            data.append(line.value)
        else:
            # dbg(line, 'l↵')
            # value may simply be empty, or it may be on next line, in which
            # case it must be indented.
            depth_of_next = lines.depth_of_next()
            if depth_of_next > depth:
                value = read_value(lines, depth_of_next)
            else:
                value = ''
            data.append(value)
    return data


# read_dict() {{{2
def read_dict(lines, depth):
    data = {}
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "dict item":
            report("expected dictionary item", line, loc=depth)
        if line.key in data:
            report('duplicate key: {}.', line, line.key, loc=depth)
        if '"' in line.key and "'" in line.key:
            report("""key must not contain both " and '.""", line, line.key, loc=depth)
        if line.value:
            # dbg(line, 'dv')
            data.update({line.key: line.value})
        else:
            # dbg(line, 'd↵')
            # value may simply be empty, or it may be on next line, in which
            # case it must be indented.
            depth_of_next = lines.depth_of_next()
            if depth_of_next > depth:
                value = read_value(lines, depth_of_next)
            else:
                value = ''
            data.update({line.key: value})
    return data


# read_string() {{{2
def read_string(lines, depth):
    data = []
    while lines.still_within_string(depth):
        line = lines.get_next()
        # dbg(line, '""')
        data.append(line.value)
    return "\n".join(data)


# loads() {{{2
def loads(contents, culprit=None):
    """
    Loads NestedText from string.

    Args:
        contents (str):
            String that contains encoded data.
        culprit (str):
            Optional culprit. It is prepended to any error messages but is
            otherwise unused. Is often the name of the file that originally
            contained contents.

    Returns:
        A dictionary or list containing the data.  If contents is empty, an
        empty dictionary is returned.
    """
    with set_culprit(culprit):
        lines = Lines(contents)

        type_of_first = lines.type_of_next()
        if type_of_first not in ["list item", "dict item"]:
            if type_of_first:
                report("expected list or dictionary item.", lines.get_next(), loc=0)
            else:
                return {}
        else:
            return read_value(lines, 0)


# dumps {{{1
# Converts Python data hierarchies to NestedText.

# add_leader {{{2
def add_leader(s, leader):
    # split into separate lines
    # add leader to each non-blank line
    # add right-stripped leader to each blank line
    # rejoin and return
    return '\n'.join(
        leader + line if line else leader.rstrip()
        for line in s.split('\n')
    )


# dumps {{{2
def dumps(obj, *, sort_keys=False, indent=4, renderers=None, default=None, level=0):
    """Recursively convert object to string with reasonable formatting.

    Args:
        obj:
            The object to convert.
        sort_keys (bool or func):
            Dictionary items are sorted by their key if *sort_keys* is true.
            If a function is passed in, it is used as the key function.
        indent (int):
            The number of spaces to use to represent a single level of
            indentation.  Must be one or greater.
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
            The number of indentation levels.  When dumps is invoked recursively
            this is used to increment the level and so the indent.  Generally
            not specified by the user, but can be useful in unusual situations
            to specify an initial indent.
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
            indent = indent,
            renderers = renderers,
            default = default,
            level = level + 1
        )

    # render string
    def render_str(s, is_key=False):
        stripped = s.strip(' ')
        if is_key:
            if '\n' in s:
                raise NestedTextError(
                    s,
                    template='keys must not contain newlines.',
                    culprit=repr(s)
                )
            if '"' in s and "'" in s:
                raise NestedTextError(
                    s,
                    template="""keys must not contain both " and '.""",
                    culprit=repr(s)
                )
            if (
                len(stripped) < len(s)
                or s[:1] == "#"
                or s.startswith("- ")
                or s.startswith("> ")
                or ': ' in s
                or '"' in s
                or "'" in s
            ):
                return repr(s)
        if (
            len(stripped) < len(s)
            or s[:1] + s[-1:] in ['""', "''"]
        ):
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
    assert indent > 0
    error = None
    need_indented_block = is_collection(obj)
    content = ''
    render = renderers.get(type(obj)) if renderers else None
    if render is False:
        error = "unsupported type."
    elif render:
        content = render(obj)
        if "\n" in content or ('"' in content and "'" in content):
            need_indented_block = True
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
        if "\n" in obj or ('"' in obj and "'" in obj):
            content = add_leader(obj, '> ')
            need_indented_block = True
        else:
            content = obj
    elif is_a_scalar(obj):
        content = str(obj)
    elif default and callable(default):
        content = default(obj)
    else:
        error = "unsupported type."

    if level == 0:
        if not is_collection(obj):
            error = 'expected dictionary or list.'
    else:
        if need_indented_block:
            content = "\n" + add_leader(content, indent*' ')
        else:
            content = render_str(content)

    if error:
        raise NestedTextError(obj, template=error, culprit=repr(obj))

    return content
