# Udif Load
# encoding: utf8
#
# Converts Udif into Python data hierarchies.

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
    Error,
    Info,
    InformantFactory,
)

# Globals {{{1
indent_spaces = 4
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
is_quoted = re.compile(r"\A *" + quoted + r" *\Z")


# Utilities {{{1
highlight = InformantFactory(message_color='blue')


def dbg(line, kind):  # pragma: no cover
    if line.depth is None:
        indents = ' '
    else:
        indents = line.depth//indent_spaces
    highlight(f'{indents}{kind}{line.num:>4}:{line.text}')


def join_and_dequote(l):
    s = "".join(l).strip()
    if is_quoted.match(s):
        return s[1:-1]
    return s


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
    raise Error(template=message, *args, **kwargs)


def indentation_error(line, depth):
    assert line.depth != depth
    report('invalid indentation.', line, loc=depth)


# Lines class {{{1
class Lines:
    class Line(Info):
        pass

    # constructor {{{2
    def __init__(self, contents):
        self.generator = self.read_lines(contents)
        self.next_line = True
        while self.next_line:
            self.next_line = next(self.generator, None)
            if self.next_line and self.next_line.kind not in ["blank", "comment"]:
                return

    # read_lines() {{{2
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
                elif dict_tag in components:
                    kind = "dict item"
                    split_loc = components.index(dict_tag)
                    key = join_and_dequote(components[:split_loc])
                    value = join_and_dequote(components[split_loc + 1 :])
                elif str_tag == "".join(components[:2]).lstrip(" "):
                    kind = "string"
                    value = "".join(components[2:])[:-1]
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

    # type_of_next() {{{2
    def type_of_next(self):
        if self.next_line:
            return self.next_line.kind

    # still_within_level() {{{2
    def still_within_level(self, depth):
        if self.next_line:
            return self.next_line.depth >= depth

    # still_within_string() {{{2
    def still_within_string(self, depth):
        if self.next_line:
            return self.next_line.kind == "string" and self.next_line.depth == depth

    # depth_of_next() {{{2
    def depth_of_next(self):
        if self.next_line:
            return self.next_line.depth
        return 0

    # get_next() {{{2
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


# read_value() {{{1
def read_value(lines, depth):
    if lines.type_of_next() == "list item":
        return read_list(lines, depth)
    if lines.type_of_next() == "dict item":
        return read_dict(lines, depth)
    return read_string(lines, depth)


# read_list() {{{1
def read_list(lines, depth):
    data = []
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "list item":
            report("expected list item", line)
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


# read_dict() {{{1
def read_dict(lines, depth):
    data = {}
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "dict item":
            report("expected dictionary item", line)
        if line.value:
            # dbg(line, 'dv')
            if line.key in data:
                report('duplicate key: {}.', line, line.key)
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


# read_string() {{{1
def read_string(lines, depth):
    data = []
    while lines.still_within_string(depth):
        line = lines.get_next()
        # dbg(line, '""')
        data.append(line.value)
    return "\n".join(data)


# loads() {{{1
def loads(contents, culprit=None):
    """
    Loads Udiff from string.

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

    **Example**::

        >>> import udif
        >>> contents = '''
        ... name: Deryl McKinnon
        ... phone: 212-590-3107
        ... '''

        try:
            data = udif.loads(contents)
            print(data)
        except udif.Error as e:
            e.report()
        {'name': 'Deryl McKinnon', 'phone': 'phone: 212-590-3107'}

    """
    with set_culprit(culprit):
        lines = Lines(contents)

        type_of_first = lines.type_of_next()
        if type_of_first not in ["list item", "dict item"]:
            if type_of_first:
                report("expected list or dictionary item.", lines.get_next())
            else:
                return {}
        else:
            return read_value(lines, 0)
