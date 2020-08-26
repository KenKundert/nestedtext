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
)

# Globals {{{1
indent_spaces = 4
colon = ": "
dash = "- "
quoted = "|".join([
    r'"[^"\n]*"',  # "string"
    r"'[^'\n]*'",  # 'string'
])
splitters = (
    quoted,        # "string" or 'string'
    colon,         # colon-space -- key/value separator
    dash,          # dash-space -- introduces list item
)
splitter = re.compile("(" + "|".join(f"(?:{s})" for s in splitters) + ")")
is_quoted = re.compile(r"\A *" + quoted + r" *\Z")


# Utilities {{{1
def increment(depth):
    return depth + indent_spaces


def join_and_dequote(l):
    s = "".join(l).strip()
    if is_quoted.match(s):
        return s[1:-1]
    return s


def report(message, line, loc=None):
    message = full_stop(message)
    kwargs = {}
    if line:
        kwargs['culprit'] = get_culprit(line.num+1)
        if loc is not None:
            kwargs['codicil'] = f"«{line.text}»\n {loc*' '}↑"
            kwargs['loc'] = loc
        else:
            kwargs['codicil'] = f"«{line.text}»"
        kwargs['line'] = line.text
    else:
        kwargs['culprit'] = get_culprit(line.num+1)
    raise Error(message, **kwargs)


def indentation_error(line, depth):
    assert line.depth != depth
    if line.depth % indent_spaces:
        message = f"indentation must be a multiple of {indent_spaces} spaces."
    else:
        kind = "indent" if line.depth > depth else "dedent"
        message = f"unexpected {kind}."
    report(message, line, loc=depth)


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
            if self.next_line and self.next_line.kind not in ["empty", "comment"]:
                return

    # read_lines() {{{2
    def read_lines(self, contents):
        for lineno, line in enumerate(contents.splitlines()):
            depth = None
            key = None
            value = None
            if line.strip() == "":
                kind = "empty"
                value = "\n"
            elif line[:1] == "#":
                kind = "comment"
                value = line[1:].strip()
            else:
                stripped = line.lstrip(" ")
                depth = len(line) - len(stripped)
                components = splitter.split(line + " ")
                if dash == "".join(components[:2]).lstrip(" "):
                    kind = "list item"
                    value = join_and_dequote(components[2:])
                elif colon in components:
                    kind = "dict item"
                    split_loc = components.index(colon)
                    key = join_and_dequote(components[:split_loc])
                    value = join_and_dequote(components[split_loc + 1 :])
                else:
                    kind = "string"
                    value = line
            yield self.Line(
                text=line, num=lineno, kind=kind, depth=depth, key=key, value=value
            )

    # type_of_next() {{{2
    def type_of_next(self):
        if self.next_line:
            return self.next_line.kind

    # still_within_level() {{{2
    def still_within_level(self, depth):
        if self.next_line:
            return self.next_line.kind == "empty" or self.next_line.depth >= depth

    # next_indented() {{{2
    def next_indented(self, depth):
        if self.next_line:
            return self.next_line.kind == "empty" or self.next_line.depth > depth

    # get_next() {{{2
    def get_next(self):
        this_line = self.next_line

        # queue up the next useful line
        # this is needed so type_of_next() and still_within_level() can easily
        # access the next upcoming line.
        while self.next_line:
            self.next_line = next(self.generator, None)
            if not self.next_line or self.next_line.kind != "comment":
                break

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
        if line.kind == "empty":
            continue
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "list item":
            report("expected list item", line)
        if line.value:
            data.append(line.value)
        else:
            # value may simply be empty, or it may be on next line, in which
            # case it must be indented.
            if lines.next_indented(depth):
                value = read_value(lines, increment(depth))
            else:
                value = ''
            data.append(value)
    return data


# read_dict() {{{1
def read_dict(lines, depth):
    data = {}
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.kind == "empty":
            continue
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "dict item":
            report("expected dictionary item", line)
        if line.value:
            data.update({line.key: line.value})
        else:
            # value may simply be empty, or it may be on next line, in which
            # case it must be indented.
            if lines.next_indented(depth):
                value = read_value(lines, increment(depth))
            else:
                value = ''
            data.update({line.key: value})
    return data


# read_string() {{{1
def read_string(lines, depth):
    data = []
    while lines.still_within_level(depth):
        line = lines.get_next()
        data.append(line.text[depth:])
    return "\n".join(data)


# load() {{{1
def load(contents, culprit=None):
    """
    Loads Udiff from string.

    Args:
        contents 9str):
            String that contains Udif data.
        culprit (str):
            Optional culprit. It is prepended to any error messages but is
            otherwise unused.

    **Example**::

        >>> import udif
        >>> contents = '''
        ... name: Deryl McKinnon
        ... phone: 212-590-3107
        ... '''

        try:
            data = udif.load(contents)
            print(data)
        except udif.Error as e:
            e.report()
        {'name': 'Deryl McKinnon', 'phone': 'phone: 212-590-3107'}

    """
    with set_culprit(culprit):
        lines = Lines(contents)

        if lines.type_of_next() not in ["list item", "dict item"]:
            report("expected list or dictionary item.", lines.get_next())
        else:
            return read_value(lines, 0)
