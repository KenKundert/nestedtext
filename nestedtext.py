# encoding: utf8
"""
NestedText: A Human Readable and Writable Data Format

NestedText is a file format for holding data that is intended to be entered,
edited, or viewed by people.  It allows data to be organized into a nested
collection of dictionaries, lists, and strings.

It is easily created, modified, or viewed with a text editor and easily
understood and used by both programmers and non-programmers.
"""

# MIT License {{{1
# Copyright (c) 2020-21 Ken and Kale Kundert
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Imports {{{1
from inform import (
    full_stop,
    set_culprit,
    get_culprit,
    is_str,
    is_collection,
    is_mapping,
    plural,
    Error,
    Info,
)
import textwrap
import collections.abc
import re
import unicodedata


# Globals {{{1
__version__ = "3.0.0"
__released__ = "2021-07-17"
__all__ = ['load', 'loads', 'dump', 'dumps', 'NestedTextError']


# Utility functions {{{1
# convert_returns {{{2
def convert_returns(text):
    return text.replace('\r\n', '\n').replace('\r', '\n')


# Exceptions {{{1
# NestedTextError {{{2
class NestedTextError(Error, ValueError):
    r'''
    The *load* and *dump* functions all raise *NestedTextError* when they
    discover an error. *NestedTextError* subclasses both the Python *ValueError*
    and the *Error* exception from *Inform*.  You can find more documentation on
    what you can do with this exception in the `Inform documentation
    <https://inform.readthedocs.io/en/stable/api.html#exceptions>`_.

    The exception provides the following attributes:

    source:

        The source of the *NestedText* content, if given. This is often a
        filename.

    line:

        The text of the line of *NestedText* content where the problem was found.

    lineno:

        The number of the line where the problem was found.  Line numbers are
        zero based except when included in messages to the end user.

    colno:

        The number of the character where the problem was found on *line*.
        Column numbers are zero based.

    prev_line:

        The text of the meaningful line immediately before where the problem was
        found.  This would not be a comment or blank line.

    template:

        The possibly parameterized text used for the error message.

    As with most exceptions, you can simply cast it to a string to get a
    reasonable error message.

    .. code-block:: python

        >>> from textwrap import dedent
        >>> import nestedtext as nt

        >>> content = dedent("""
        ...     name1: value1
        ...     name1: value2
        ...     name3: value3
        ... """).strip()

        >>> try:
        ...     print(nt.loads(content))
        ... except nt.NestedTextError as e:
        ...     print(str(e))
        2: duplicate key: name1.

    You can also use the *report* method to print the message directly. This is
    appropriate if you are using *inform* for your messaging as it follows
    *inform*'s conventions::

        >> try:
        ..     print(nt.loads(content))
        .. except nt.NestedTextError as e:
        ..     e.report()
        error: 2: duplicate key: name1.
            «name1: value2»
             ▲

    The *terminate* method prints the message directly and exits::

        >> try:
        ..     print(nt.loads(content))
        .. except nt.NestedTextError as e:
        ..     e.terminate()
        error: 2: duplicate key: name1.
            «name1: value2»
             ▲

    With exceptions generated from :func:`load` or :func:`loads` you may see
    extra lines at the end of the message that show the problematic lines if
    you have the exception report itself as above.  Those extra lines are
    referred to as the codicil and they can be very helpful in illustrating the
    actual problem. You do not get them if you simply cast the exception to a
    string, but you can access them using :meth:`NestedTextError.get_codicil`.
    The codicil or codicils are returned as a tuple.  You should join them with
    newlines before printing them.

    .. code-block:: python

        >>> try:
        ...     print(nt.loads(content))
        ... except nt.NestedTextError as e:
        ...     print(e.get_message())
        ...     print(*e.get_codicil(), sep="\n")
        duplicate key: name1.
           1 «name1: value1»
           2 «name1: value2»
              ▲

    Note the « and » characters in the codicil. They delimit the extent of the
    text on each line and help you see troublesome leading or trailing white
    space.

    Exceptions produced by *NestedText* contain a *template* attribute that
    contains the basic text of the message. You can change this message by
    overriding the attribute using the *template* argument when using *report*,
    *terminate*, or *render*.  *render* is like casting the exception to a
    string except that allows for the passing of arguments.  For example, to
    convert a particular message to Spanish, you could use something like the
    following.

    .. code-block:: python

        >>> try:
        ...     print(nt.loads(content))
        ... except nt.NestedTextError as e:
        ...     template = None
        ...     if e.template == 'duplicate key: {}.':
        ...         template = 'llave duplicada: {}.'
        ...     print(e.render(template=template))
        2: llave duplicada: name1.

    '''


# NotSuitableForInline {{{2
# this is only intended for internal use
class NotSuitableForInline(Exception):
    pass


# NestedText Reader {{{1
# Converts NestedText into Python data hierarchies.

# constants {{{2
# regular expressions used to recognize dict items
dict_item_regex = r"""
    (?P<key>[^\s].*?)      # key (must start with non-space character)
    \s*                    # optional white space
    :                      # separator
    (?:\ (?P<value>.*))?   # value
"""
dict_item_recognizer = re.compile(dict_item_regex, re.VERBOSE)


# report {{{2
def report(message, line, *args, colno=None, **kwargs):
    message = full_stop(message)
    culprits = get_culprit()
    if culprits:
        kwargs['source'] = culprits[0]
    if line:
        # line numbers are always 0 based unless included in a message to user
        include_prev_line = not (
            line.prev_line is None or kwargs.pop('suppress_prev_line', False)
        )
        if colno is not None:
            # build codicil that shows both the line and the preceding line
            if include_prev_line:
                codicil = [f'{line.prev_line.lineno+1:>4} «{line.prev_line.text}»']
            else:
                codicil = []
            # replace tabs with → so that arrow points to right location.
            text = line.text.replace("\t", "→")
            codicil += [
                f'{line.lineno+1:>4} «{text}»',
                '      ' + (colno*' ') + '▲',
            ]
            kwargs['codicil'] = '\n'.join(codicil)
            kwargs['colno'] = colno
        else:
            kwargs['codicil'] = f'{line.lineno+1:>4} «{line.text}»'
        kwargs['culprit'] = get_culprit(line.lineno+1)
        kwargs['line'] = line.text
        kwargs['lineno'] = line.lineno
        if include_prev_line:
            kwargs['prev_line'] = line.prev_line.text
    else:
        kwargs['culprit'] = culprits  # pragma: no cover
    raise NestedTextError(template=message, *args, **kwargs)


# unrecognized_line {{{2
def unrecognized_line(line):
    # line will not be recognized if there is invalid white space in indentation
    first_non_space = line.text.lstrip(' ')[0]
    index_of_first_non_space = line.text.index(first_non_space)
    if first_non_space.strip() == '':
        # first non-space is a white space character
        # treat it as invalid indentation
        desc = unicodedata.name(first_non_space, "")
        if desc:
            desc = f' ({desc})'
        report(
            f'invalid character in indentation: {first_non_space!r}{desc}.',
            line,
            colno = index_of_first_non_space
        )
    else:
        report('unrecognized line.', line, colno=index_of_first_non_space)


# Lines class {{{2
class Lines:
    # constructor {{{3
    def __init__(self, lines):
        self.lines = lines
        self.generator = self.read_lines()
        self.next_line = True
        while self.next_line:
            self.next_line = next(self.generator, None)
            if self.next_line and self.next_line.kind not in ["blank", "comment"]:
                return

    # Line class {{{3
    class Line(Info):
        def render(self, col=None):
            result = [f'{self.lineno:>4} «{self.text}»']
            if col is not None:
                result += ['      ' + (col*' ') + '▲']
            return '\n'.join(result)

        def __str__(self):
            return self.text

        def __repr__(self):
            return self.__class__.__name__ + f"({self.lineno}: «{self.text}»)"

    # read_lines() {{{3
    def read_lines(self):
        prev_line = None
        for lineno, line in enumerate(self.lines):
            key = None
            value = None
            line = line.rstrip('\n')

            # compute indentation
            stripped = line.lstrip(' ')
            depth = len(line) - len(stripped)

            # determine line type and extract values
            if stripped == "":
                kind = "blank"
                value = None
                depth = None
            elif stripped[:1] == "#":
                kind = "comment"
                value = line[1:].strip()
                depth = None
            elif stripped == '-' or stripped.startswith('- '):
                kind = "list item"
                value = stripped[2:]
            elif stripped == '>' or stripped.startswith('> '):
                kind = "string item"
                value = line[depth+2:]
            elif stripped == ':' or stripped.startswith(': '):
                kind = "key item"
                value = line[depth+2:]
            elif stripped[0:1] in ['[', '{']:
                tag = stripped[0:1]
                kind = 'inline dict' if tag == '{' else 'inline list'
                value = line[depth:]
            else:
                matches = dict_item_recognizer.fullmatch(stripped)
                if matches:
                    kind = "dict item"
                    key = matches.group('key')
                    value = matches.group('value')
                    if value is None:
                        value = ''
                else:
                    kind = "unrecognized"
                    value = line

            # bundle information about line
            the_line = self.Line(
                text = line,
                lineno = lineno,
                kind = kind,
                depth = depth,
                key = key,
                value = value,
                prev_line = prev_line,
            )
            if kind.endswith(' item'):
                # Do not include the_line.prev_line in the prev_line to avoid
                # keeping the chain of all previous lines.
                prev_line = self.Line(
                    text = the_line.text,
                    value = the_line.value,
                    kind = the_line.kind,
                    depth = the_line.depth,
                    lineno = the_line.lineno,
                )

            yield the_line

    # type_of_next() {{{3e
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
            return (
                self.next_line.kind == "string item" and
                self.next_line.depth >= depth
            )

    # still_within_key() {{{3
    def still_within_key(self, depth):
        if self.next_line:
            return (
                self.next_line.kind == "key item" and
                self.next_line.depth == depth
            )

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
            unrecognized_line(this_line)
        return this_line

    # indentation_error {{{3
    def indentation_error(self, line, depth):
        assert line.depth != depth
        prev_line = line.prev_line
        if not line.prev_line and depth == 0:
            msg = 'top-level content must start in column 1.'
        elif (
            prev_line and
            prev_line.value and
            prev_line.depth < line.depth and
            prev_line.kind in ['list item', 'dict item']
        ):
            if prev_line.value.strip() == '':
                obs = ', which in this case consists only of whitespace'
            else:
                obs = ''
            msg = ' '.join([
                'invalid indentation.',
                'An indent may only follow a dictionary or list item that does',
                f'not already have a value{obs}.'
            ])
        elif (
            prev_line and
            prev_line.depth > line.depth
        ):
            msg = 'invalid indentation, partial dedent.'
        else:
            msg = 'invalid indentation.'
        report(textwrap.fill(msg), line, colno=depth)


# KeyPolicy class {{{2
# Used to hold and implement the on_dup policy for dictionaries.
class KeyPolicy:
    @classmethod
    def set_policy(cls, on_dup):
        if callable(on_dup):
            # if on_dup is a function, convert it to a data structure that will
            # hold state during the load
            on_dup = dict(_callback_func=on_dup)
        cls.on_dup = on_dup

    @classmethod
    def add_to_dictionary(cls, dictionary, key, value, line=None, colno=None):
        if key in dictionary:
            # found duplicate key
            if cls.on_dup is None:
                report('duplicate key: {}.', line, key, colno=colno)
            if cls.on_dup == 'ignore':
                return
            if isinstance(cls.on_dup, dict):
                key = cls.on_dup['_callback_func'](
                    key, value, dictionary, cls.on_dup
                )
                assert key not in dictionary
            elif cls.on_dup != 'replace':
                raise NotImplementedError(f'{cls.on_dup}: unknown value for on_dup.')
        dictionary[key] = value


# Location class {{{2
class Location:
    """Holds information about the location of a token.

    Returned from :func:`load` and :func:`loads` as the values in a *keymap*.
    Objects of this class holds the line and column numbers of the key and value
    tokens.
    """
    def __init__(self, line=None, col=None, key_line=None, key_col=None):
        self.line = line
        self.key_line = key_line
        self.col = col
        self.key_col = key_col

    def __repr__(self):
        components = []
        components.append(f"lineno={self.line.lineno}")
        components.append(f"colno={self.col}")
        key_line = self.key_line
        if key_line is None:
            key_line = self.line
        components.append(f"key_lineno={key_line.lineno}")
        key_col = self.key_col
        if key_col is None:
            key_col = self.col
        components.append(f"key_colno={key_col}")
        return f"{self.__class__.__name__}({', '.join(components)})"

    # as_tuple() {{{3
    def as_tuple(self, kind='value'):
        """
        Returns the location either the value or the key token as a tuple
        that contains the line number and the column number.  The line and
        column numbers are 0 based.

        Args:
            kind (str):
                Specify either 'key' or 'value' depending on which token is
                desired.
        """
        if kind == 'key':
            line = self.key_line
            col = self.key_col
            if line is None:
                line = self.line
            if col is None:
                col = self.col
        else:
            line = self.line
            col = self.col
        return line.lineno, col

    # as_line() {{{3
    def as_line(self, kind='value'):
        """
        Returns a string containing two lines that identify the token in
        context.  The first line contains the line number and text of the line
        that contains the token.  The second line contains a pointer to the
        token.

        Args:
            kind (str):
                Specify either 'key' or 'value' depending on which token is
                desired.
        """
        if kind == 'key':
            line = self.key_line
            col = self.key_col
            if line is None:
                line = self.line
            if col is None:
                col = self.col
        else:
            line = self.line
            col = self.col
        return line.render(col)


# Inline class {{{2
class Inline:
    # a recursive descent parser to interpret inline lists and dictionaries

    # constructor() {{{3
    def __init__(self, line, keys, loader):
        self.line = line
        self.loader = loader
        self.text = line.value
        self.max_index = len(self.text)
        self.starting_col = line.depth
        try:
            self.values, self.keymap, index = self.parse_inline_value(keys, 0)
        except IndexError:
            self.inline_error(
                "line ended without closing delimiter", self.max_index
            )
        if index < self.max_index:
            extra = self.text[index:]
            self.inline_error(
                f"extra {plural(extra):character} after closing delimiter: ‘{{}}’.",
                index, extra
            )
        assert index == self.max_index

    # parse_inline_value() {{{3
    def parse_inline_value(self, keys, index, forbidden_chars=None):
        if self.text[index] == '{':
            return self.parse_inline_dict(keys, index)
        elif self.text[index] == '[':
            return self.parse_inline_list(keys, index)
        else:
            return self.parse_inline_str(keys, index, forbidden_chars)

    # parse_inline_dict() {{{3
    def parse_inline_dict(self, keys, index):
        starting_index = index
        assert self.text[index] == '{'
        index += 1
        values = {}
        need_another = False

        while self.text[index] != '}':
            prev_index = index
            key, value, location, index = self.parse_inline_dict_item(keys, index)
            KeyPolicy.add_to_dictionary(values, key, value, self.line, prev_index)
            self.loader._add_keymap(keys + (key,), location)
            need_another = False
            if self.text[index] not in ',}':
                self.inline_error(
                    "expected ‘,’ or ‘}}’, found ‘{}’", index, self.text[index]
                )
            if self.text[index] == ',':
                index += 1
                need_another = True
        if need_another:
            self.inline_error("expected value", index)
        return (
            values,
            self.location(starting_index),
            self.adjust_index(index+1)
        )

    # parse_inline_dict_item() {{{3
    def parse_inline_dict_item(self, keys, index):
        forbidden_chars = '{}[],:'
        key_index = self.adjust_index(index)
        if self.text[index] in forbidden_chars:
            key = ''
        else:
            key, _, index = self.parse_inline_value(keys, index, forbidden_chars)
        if self.text[index] != ':':
            self.inline_error(
                "expected ‘:’, found ‘{}’", index, self.text[index], culprit=key
            )
        index = self.adjust_index(index+1)
        if self.text[index] in ',}':
            value = ''
            loc = self.location(index)
        else:
            value, loc, index = self.parse_inline_value(keys, index, forbidden_chars)
        self.add_key_location(loc, key_index)
        return key, value, loc, index

    # parse_inline_list() {{{3
    def parse_inline_list(self, keys, index):
        forbidden_chars = '{}[],'
        starting_index = index
        assert self.text[index] == '['
        index += 1

        # handle empty list
        if self.text[index] == ']':
            return [], self.location(starting_index), self.adjust_index(index+1)

        key = 0
        values = []
        value = ''
        loc = self.location(index)
        while True:
            new_keys = keys + (key,)
            c = self.text[index]
            if c in ',]':
                values.append(value)
                self.loader._add_keymap(new_keys, loc)
                key += 1
                if c == ']':
                    return (
                        values,
                        self.location(starting_index),
                        self.adjust_index(index+1)
                    )
                index += 1
                loc = self.location(index)
                index = self.adjust_index(index)
                value = ''
            elif value:
                self.inline_error(
                    "expected ‘,’ or ‘]’, found ‘{}’", index, self.text[index]
                )
            elif c in '}],':
                self.inline_error("expected value", index)
            else:
                value, loc, index = self.parse_inline_value(
                    new_keys, index, forbidden_chars
                )

    # parse_inline_str() {{{3
    def parse_inline_str(self, keys, index, forbidden_chars):
        starting_index = index
        while self.text[index] not in forbidden_chars:
            index = self.adjust_index(index+1)
        value = self.text[starting_index:index].strip()
        return value, self.location(starting_index), index

    # adjust_index() {{{3
    def adjust_index(self, index):
        # if desired index points to white space, shift right until it doesn't
        while index < self.max_index and self.text[index] in ' \t':
            index += 1
        return index

    # location() {{{3
    def location(self, index, **kwargs):
        if self.line:
            kwargs['line'] = self.line
        return Location(col=index + self.starting_col, **kwargs)

    # add_key_location() {{{3
    def add_key_location(self, loc, key_index):
        loc.key_col = key_index + self.starting_col

    # inline_error {{{3
    def inline_error(self, message, index, *args, culprit=None, **kwargs):
        report(
            full_stop(message),
            self.line,
            *args,
            colno = index + self.starting_col,
            culprit = culprit,
            suppress_prev_line = True,
            **kwargs,
        )

    # get_values() {{{3
    def get_values(self):
        return self.values, self.keymap

    # render {{{3
    def render(self, index):  # pragma: no cover
        return f"«{self.text}»\n {index*' '}▲"

    # __repr__ {{{3
    def __repr__(self):  # pragma: no cover
        name = self.__class__.__name__
        return f"{name}({self.text!r})"


# NestedTextLoader class {{{2
class NestedTextLoader:
    # __init__() {{{3
    def __init__(self, lines, top, source, on_dup, keymap):
        KeyPolicy.set_policy(on_dup)
        self.source = source
        self.keymap = {} if keymap is True else keymap

        with set_culprit(source):
            lines = self.lines = Lines(lines)
            next_is = lines.type_of_next()

            if top in ['any', any]:
                if next_is is None:
                    self.values, self.keymap = None, None
                else:
                    self.values, self.keymap = self._read_value(0, ())
                return

            if top in ['dict', dict]:
                if next_is in ["dict item", "key item", "inline dict"]:
                    self.values, self.keymap = self._read_value(0, ())
                elif next_is is None:
                    self.values, self.keymap = {}, None
                else:
                    report('content must start with key or brace ({{).', lines.get_next())
                return

            if top in ['list', list]:
                if next_is in ["list item", "inline list"]:
                    self.values, self.keymap = self._read_value(0, ())
                elif next_is is None:
                    self.values, self.keymap = [], None
                else:
                    report('content must start with dash (-) or bracket ([).', lines.get_next())
                return

            if top in ['str', str]:
                if next_is == "string item":
                    self.values, self.keymap = self._read_value(0, ())
                elif next_is is None:
                    self.values, self.keymap = "", None
                else:
                    report('content must start with greater-than sign (>).', lines.get_next())
                return

            raise NotImplementedError(top)

    # get_decoded() {{{3
    def get_decoded(self):
        return self.values

    # # get_keymap() {{{3
    # this method becomes useful when an interface that returns the loader develops
    # def get_keymap(self):
    #     return self.keymap

    # # get_source() {{{3
    # this method becomes useful when an interface that returns the loader develops
    # def get_source(self):
    #     return self.source

    # # get_value() {{{3
    # this method becomes useful when an interface that returns the loader develops
    # def get_value(self, keys):
    #     """
    #     Return the value associated with a set of keys.
    #     """
    #     value = self.values
    #     key = None
    #     keys_used = ()
    #     try:
    #         for key in keys:
    #             keys_used += (key,)
    #             value = value[key]
    #     except (KeyError, IndexError) as e:
    #         raise NestedTextError(f"bad key.", key=key, culprit=keys_used)
    #     return value

    # _add_keymap() {{{3
    def _add_keymap(self, keys, location):
        if self.keymap is not None:
            self.keymap[keys] = location

    # _read_value() {{{3
    def _read_value(self, depth, keys):
        lines = self.lines
        if lines.type_of_next() == "list item":
            return self._read_list(depth, keys)
        if lines.type_of_next() in ["dict item", "key item"]:
            return self._read_dict(depth, keys)
        if lines.type_of_next() == "string item":
            return self._read_string(depth, keys)
        if lines.type_of_next() in ["inline dict", "inline list"]:
            return self._read_inline(keys)
        unrecognized_line(lines.get_next())

    # _read_list() {{{3
    def _read_list(self, depth, keys):
        lines = self.lines
        values = []
        index = 0
        first_line = lines.next_line
        while lines.still_within_level(depth):
            line = lines.get_next()
            if line.depth != depth:
                lines.indentation_error(line, depth)
            if line.kind != "list item":
                report("expected list item.", line, colno=depth)
            new_keys = keys + (index,)
            if line.value:
                values.append(line.value)
                self._add_keymap(
                    new_keys, Location(line=line, key_col=depth, col=depth + 2)
                )
            else:
                # value may simply be empty, or it may be on next line, in which
                # case it must be indented.
                depth_of_next = lines.depth_of_next()
                if depth_of_next > depth:
                    value, loc = self._read_value(depth_of_next, new_keys)
                    loc.key_line = line
                    loc.key_col = depth
                else:
                    value = ''
                    loc = Location(line=line, key_col=depth, col=depth + 1)
                values.append(value)
                self._add_keymap(new_keys, loc)
            index += 1

        return values, Location(line=first_line, col=first_line.depth)

    # _read_dict() {{{3
    def _read_dict(self, depth, keys):
        lines = self.lines
        values = {}
        first_line = lines.next_line
        while lines.still_within_level(depth):
            line = lines.get_next()
            if line.depth != depth:
                lines.indentation_error(line, depth)
            if line.kind not in ["dict item", "key item"]:
                report("expected dictionary item.", line, colno=depth)
            key_line = line
            key_col = depth
            if line.kind == "key item":
                # multiline key
                key = self._read_key(line, depth)
                value = None
            else:
                # key and value on a single line
                key = line.key
                value = line.value

            new_keys = keys + (key,)
            if value:
                loc = Location(line=line, col=depth+len(key)+2)
            else:
                depth_of_next = lines.depth_of_next()
                if depth_of_next > depth:
                    value, loc = self._read_value(depth_of_next, new_keys)
                elif line.kind == "dict item":
                    value = ''
                    loc = Location(line=line, col=depth+len(key)+1)
                else:
                    report('multiline key requires a value.', line, None, colno=depth)

            try:
                KeyPolicy.add_to_dictionary(values, key, value, line, depth)
                loc.key_line = key_line
                loc.key_col = key_col
                self._add_keymap(new_keys, loc)
            except NestedTextError as e:
                report(e.template, line, key, colno=depth)
        return values, Location(line=first_line, col=first_line.depth)

    # _read_key() {{{3
    def _read_key(self, line, depth):
        lines = self.lines
        data = [line.value]
        while lines.still_within_key(depth):
            line = lines.get_next()
            data.append(line.value)
        return "\n".join(data)

    # _read_string() {{{3
    def _read_string(self, depth, keys):
        lines = self.lines
        data = []
        loc = Location(line=lines.next_line, key_col=depth)
        while lines.still_within_string(depth):
            line = lines.get_next()
            data.append(line.value)
            if line.depth != depth:
                lines.indentation_error(line, depth)
        value = "\n".join(data)
        loc.col = depth + (2 if value else 1)
        return value, loc

    # _read_inline() {{{3
    def _read_inline(self, keys):
        lines = self.lines
        line = lines.get_next()
        return Inline(line, keys, self).get_values()


# loads {{{2
def loads(content, top='dict', *, source=None, on_dup=None, keymap=None):
    # description {{{3
    r'''
    Loads *NestedText* from string.

    Args:
        content (str):
            String that contains encoded data.
        top (str):
            Top-level data type. The NestedText format allows for a dictionary,
            a list, or a string as the top-level data container.  By specifying
            top as 'dict', 'list', or 'str' you constrain both the type of
            top-level container and the return value of this function. By
            specifying 'any' you enable support for all three data types, with
            the type of the returned value matching that of top-level container
            in content. As a short-hand, you may specify the *dict*, *list*,
            *str*, and *any* built-ins rather than specifying *top* with a
            string.
        source (str or Path):
            If given, this string is attached to any error messages as the
            culprit. It is otherwise unused. Is often the name of the file that
            originally contained the NestedText content.
        on_dup (str or func):
            Indicates how duplicate keys in dictionaries should be handled. By
            default they raise exceptions. Specifying 'ignore' causes them to be
            ignored (first wins). Specifying 'replace' results in them replacing
            earlier items (last wins). By specifying a function, the keys can be
            de-duplicated.  This call-back function returns a new key and takes
            four arguments:

            1. The new key (duplicates an existing key).
            2. The new value.
            3. The entire dictionary as it is at the moment the duplicate key is
               found.
            4. The state; a dictionary that is created as the *loads* is called
               and deleted as it returns. Values placed in this dictionary are
               retained between multiple calls to this call back function.
        keymap (dict):
            Specify an empty dictionary or nothing at all for the value of
            this argument.  If you give an empty dictionary it will be filled
            with location information for the values that are returned.  Upon
            return the dictionary maps a tuple containing the keys for the value
            of interest to the location of that value in the NestedText source
            document. The location is contained in a :class:`Location` object.
            You can access the line and column number using the
            :meth:`Location.as_tuple` method, and the line that contains the
            value annotated with its location using the :meth:`Location.as_line`
            method.

    Returns:
        The extracted data.  The type of the return value is specified by the
        top argument.  If top is 'any', then the return value will match that of
        top-level data container in the input content. If content is empty, an
        empty data value of the type specified by top is returned. If top is
        'any' None is returned.

    Raises:
        NestedTextError: if there is a problem in the *NextedText* content.

    Examples:

        A *NestedText* document is specified to *loads* in the form of a string:

        .. code-block:: python

            >>> import nestedtext as nt

            >>> contents = """
            ... name: Kristel Templeton
            ... sex: female
            ... age: 74
            ... """

            >>> try:
            ...     data = nt.loads(contents, 'dict')
            ... except nt.NestedTextError as e:
            ...     e.terminate()

            >>> print(data)
            {'name': 'Kristel Templeton', 'sex': 'female', 'age': '74'}

        *loads()* takes an optional argument, *source*. If specified, it is
        added to any error messages. It is often used to designate the source
        of *contents*. For example, if *contents* were read from a file,
        *source* would be the file name.  Here is a typical example of reading
        *NestedText* from a file:

        .. code-block:: python

            >>> filename = 'examples/duplicate-keys.nt'
            >>> try:
            ...     with open(filename, encoding='utf-8') as f:
            ...         addresses = nt.loads(f.read(), source=filename)
            ... except nt.NestedTextError as e:
            ...     print(e.render())
            ...     print(*e.get_codicil(), sep="\n")
            examples/duplicate-keys.nt, 5: duplicate key: name.
               4 «name:»
               5 «name:»
                  ▲

        Notice in the above example the encoding is explicitly specified as
        'utf-8'.  *NestedText* files should always be read and written using
        *utf-8* encoding.

        The following examples demonstrate the various ways of handling
        duplicate keys:

        .. code-block:: python

            >>> content = """
            ... key: value 1
            ... key: value 2
            ... key: value 3
            ... name: value 4
            ... name: value 5
            ... """

            >>> print(nt.loads(content))
            Traceback (most recent call last):
            ...
            nestedtext.NestedTextError: 3: duplicate key: key.

            >>> print(nt.loads(content, on_dup='ignore'))
            {'key': 'value 1', 'name': 'value 4'}

            >>> print(nt.loads(content, on_dup='replace'))
            {'key': 'value 3', 'name': 'value 5'}

            >>> def de_dup(key, value, data, state):
            ...     if key not in state:
            ...         state[key] = 1
            ...     state[key] += 1
            ...     return f"{key}#{state[key]}"

            >>> print(nt.loads(content, on_dup=de_dup))
            {'key': 'value 1', 'key#2': 'value 2', 'key#3': 'value 3', 'name': 'value 4', 'name#2': 'value 5'}

    '''

    # code {{{3
    lines = convert_returns(content).split('\n')
    loader = NestedTextLoader(lines, top, source, on_dup, keymap)
    return loader.get_decoded()


# load {{{2
def load(f=None, top='dict', *, on_dup=None, keymap=None):
    # description {{{3
    r'''
    Loads *NestedText* from file or stream.

    Is the same as :func:`loads` except the *NextedText* is accessed by reading
    a file rather than directly from a string. It does not keep the full
    contents of the file in memory and so is more memory efficient with large
    files.

    Args:
        f (str, os.PathLike, io.TextIOBase, collections.abc.Iterator):
            The file to read the *NestedText* content from.  This can be
            specified either as a path (e.g. a string or a `pathlib.Path`),
            as a text IO object (e.g. an open file), or as an iterator.  If a
            path is given, the file will be opened, read, and closed.  If an IO
            object is given, it will be read and not closed; utf-8 encoding
            should be used..  If an iterator is given, it should generate full
            lines in the same manner that iterating on a file descriptor would.

        kwargs:
            See :func:`loads` for optional arguments.

    Returns:
        The extracted data.
        See :func:`loads` description of the return value.

    Raises:
        NestedTextError: if there is a problem in the *NextedText* content.
        OSError: if there is a problem opening the file.

    Examples:

        Load from a path specified as a string:

        .. code-block:: python

            >>> import nestedtext as nt
            >>> print(open('examples/groceries.nt').read())
            groceries:
              - Bread
              - Peanut butter
              - Jam
            <BLANKLINE>

            >>> nt.load('examples/groceries.nt')
            {'groceries': ['Bread', 'Peanut butter', 'Jam']}

        Load from a `pathlib.Path`:

        .. code-block:: python

            >>> from pathlib import Path
            >>> nt.load(Path('examples/groceries.nt'))
            {'groceries': ['Bread', 'Peanut butter', 'Jam']}

        Load from an open file object:

        .. code-block:: python

            >>> with open('examples/groceries.nt') as f:
            ...     nt.load(f)
            ...
            {'groceries': ['Bread', 'Peanut butter', 'Jam']}

    '''

    # code {{{3
    # Do not invoke the read method as that would read in the entire contents of
    # the file, possibly consuming a lot of memory. Instead pass the file
    # pointer into _read_all(), it will iterate through the lines, discarding
    # them once they are no longer needed, which reduces the memory usage.

    if isinstance(f, collections.abc.Iterator):
        source = getattr(f, 'name', None)
        loader = NestedTextLoader(f, top, source, on_dup, keymap)
        return loader.get_decoded()
    else:
        source = str(f)
        with open(f, encoding='utf-8') as fp:
            loader = NestedTextLoader(fp, top, source, on_dup, keymap)
            return loader.get_decoded()


# NestedText Writer {{{1
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


# add_prefix {{{2
def add_prefix(prefix, suffix):
    # A simple formatting of dict and list items will result in a space
    # after the colon or dash if the value is placed on next line.
    # This, function simply eliminates that space.
    if not suffix or suffix.startswith("\n"):
        return prefix + suffix
    return prefix + " " + suffix


# NestedTextDumper class {{{2
class NestedTextDumper:
    # constructor {{{3
    def __init__(self, width, inline_level, sort_keys, indent, converters, default):
        assert indent > 0
        self.width = width
        self.inline_level = inline_level
        self.indent = indent
        self.converters = converters
        self.default = default

        # define key sorting function {{{4
        if sort_keys:
            def sort(keys):
                return sorted(keys, key=sort_keys if callable(sort_keys) else None)
        else:
            def sort(keys):
                return keys
        self.sort_keys = sort

        # define object type identification functions {{{4
        if default == 'strict':
            self.is_a_dict = lambda obj: isinstance(obj, dict)
            self.is_a_list = lambda obj: isinstance(obj, list)
            self.is_a_str = lambda obj: isinstance(obj, str)
            self.is_a_scalar = lambda obj: False
        else:
            self.is_a_dict = is_mapping
            self.is_a_list = is_collection
            self.is_a_str = is_str
            self.is_a_scalar = lambda obj: obj is None or isinstance(obj, (bool, int, float))
            if is_str(default):
                raise NotImplementedError(default)

    # convert {{{3
    def convert(self, obj):
        converters = self.converters
        converter = getattr(obj, '__nestedtext_converter__', None)
        converter = converters.get(type(obj)) if converters else converter
        if converter:
            try:
                return converter(obj)
            except TypeError:
                # is bound method
                return converter()
        elif converter is False:
            raise NestedTextError(
                obj,
                template = "unsupported type.",
                culprit=repr(obj)
            ) from None
        return obj

    # render_key {{{3
    def render_key(self, key):
        key = self.convert(key)
        if self.is_a_scalar(key):
            key = str(key)
        if not self.is_a_str(key) and callable(self.default):
            key = self.default(key)
        if not self.is_a_str(key):
            raise NestedTextError(
                template = 'keys must be strings.',
                culprit = key
            ) from None
        return convert_returns(key)

    # render_dict_item {{{3
    def render_dict_item(self, key, value, level):
        multiline_key_required = (
            not key
            or '\n' in key
            or key.strip() != key
            or key[:1] in "#[{"
            or key[:2] in ["- ", "> ", ": "]
            or ': ' in key
        )
        if multiline_key_required:
            key = "\n".join(": "+l if l else ":" for l in key.split("\n"))
            if is_str(value):
                # force use of multiline value with multiline keys
                value = convert_returns(value)
                return key + "\n" + add_leader(value, self.indent*" " + "> ")
            else:
                return key + self.render_content(value, level + 1)
        else:
            return add_prefix(key + ":", self.render_content(value, level + 1))

    # render_inline_value {{{3
    def render_inline_value(self, obj, exclude):
        obj = self.convert(obj)
        if self.is_a_dict(obj):
            return self.render_inline_dict(obj)
        if self.is_a_list(obj):
            return self.render_inline_list(obj)
        return self.render_inline_scalar(obj, exclude)

    # render_inline_dict {{{3
    def render_inline_dict(self, obj):
        exclude = set('\n\r[]{}:,')
        rendered = {}
        for k, v in obj.items():
            v = self.render_inline_value(obj[k], exclude=exclude)
            k = self.render_inline_scalar(k, exclude=exclude)
            rendered[k] = v
        items = []
        for k in self.sort_keys(rendered):
            items.append(f'{k}: {rendered[k]}')
        return '{' + ', '.join(items) + '}'

    # render_inline_list {{{3
    def render_inline_list(self, obj):
        items = []
        for v in obj:
            v = self.render_inline_value(v, exclude=set('\n\r[]{},'))
            items.append(v)
        if len(items) == 1 and not items[0]:
            return '[ ]'
        content = ', '.join(items)
        leading_delimiter = '[ ' if content[0:1] == ',' else '['
        return leading_delimiter + content + ']'

    # render_inline_scalar {{{3
    def render_inline_scalar(self, obj, exclude):
        obj = self.convert(obj)
        if self.is_a_str(obj):
            value = obj
        elif self.is_a_scalar(obj):
            value = '' if obj is None else str(obj)
        elif self.default and callable(self.default):
            try:
                obj = self.default(obj)
            except TypeError:
                raise NestedTextError(
                    obj,
                    template = "unsupported type.",
                    culprit = repr(obj)
                ) from None
            return self.render_inline_value(obj, exclude)
        else:
            raise NotSuitableForInline from None

        if exclude & set(value):
            raise NotSuitableForInline from None
        if value.strip() != value:
            raise NotSuitableForInline from None
        return value

    # render content {{{3
    def render_content(self, obj, level):
        assert level >= 0
        error = None
        content = ''
        obj = self.convert(obj)
        need_indented_block = is_collection(obj)

        if self.is_a_dict(obj):
            try:
                if level < self.inline_level:
                    raise NotSuitableForInline from None
                if obj and not (self.width > 0 and len(obj) <= self.width/6):
                    raise NotSuitableForInline from None
                content = self.render_inline_dict(obj)
                if obj and len(content) > self.width:
                    raise NotSuitableForInline from None
            except NotSuitableForInline:
                rendered = {}
                for k, v in obj.items():
                    key = self.render_key(k)
                    v = self.render_dict_item(key, obj[k], level)
                    rendered[key] = v
                content = "\n".join(rendered[k] for k in self.sort_keys(rendered))
        elif self.is_a_list(obj):
            try:
                if level < self.inline_level:
                    raise NotSuitableForInline from None
                if obj and not (self.width > 0 and len(obj) <= self.width/6):
                    raise NotSuitableForInline from None
                content = self.render_inline_list(obj)
                if obj and len(content) > self.width:
                    raise NotSuitableForInline from None
            except NotSuitableForInline:
                content = "\n".join(
                    add_prefix("-", self.render_content(v, level+1))
                    for v in obj
                )
        elif self.is_a_str(obj):
            text = convert_returns(obj)
            if "\n" in text or level == 0:
                content = add_leader(text, '> ')
                need_indented_block = True
            else:
                content = text
        elif self.is_a_scalar(obj):
            if obj is None:
                content = ''
            else:
                content = str(obj)
        elif self.default and callable(self.default):
            try:
                obj = self.default(obj)
            except TypeError:
                error = 'unsupported type.'
            else:
                content = self.render_content(obj, level+1)
        else:
            error = 'unsupported type.'

        if need_indented_block and content and level:
            content = "\n" + add_leader(content, self.indent*" ")

        if error:
            raise NestedTextError(obj, template=error, culprit=repr(obj)) from None

        return content


# dumps {{{2
def dumps(
    obj,
    *,
    width = 0,
    inline_level = 0,
    sort_keys = False,
    indent = 4,
    converters = None,
    default = None,
):
    # description {{{3
    """Recursively convert object to *NestedText* string.

    Args:
        obj:
            The object to convert to *NestedText*.
        width (int):
            Enables inline lists and dictionaries if greater than zero and if
            resulting line would be less than or equal to given width.
        inline_level (int):
            Recursion depth must be equal to this value or greater to be
            eligible for inlining.
        sort_keys (bool or func):
            Dictionary items are sorted by their key if *sort_keys* is true.
            If a function is passed in, it is used as the key function.
        indent (int):
            The number of spaces to use to represent a single level of
            indentation.  Must be one or greater.
        converters (dict):
            A dictionary where the keys are types and the values are converter
            functions (functions that take an object and return it in a form
            that can be processed by *NestedText*).  If a value is False, an
            unsupported type error is raised.

            An object may provide its own converter by defining the
            ``__nestedtext_converter__`` attribute.  It may be False, or it may
            be a method that converts the object to a supported data type for
            NestedText.  A matching converter specified in the *converters*
            argument dominates over this attribute.
        default (func or 'strict'):
            The default converter. Use to convert otherwise unrecognized objects
            to a form that can be processed. If not provided an error will be
            raised for unsupported data types. Typical values are *repr* or
            *str*. If 'strict' is specified then only dictionaries, lists,
            strings, and those types that have converters are allowed. If
            *default* is not specified then a broader collection of value types
            are supported, including *None*, *bool*, *int*, *float*, and *list*-
            and *dict*-like objects.  In this case Booleans are rendered as
            'True' and 'False' and None is rendered as an empty string.  If
            *default* is a function, it acts as the default converter.  If
            it raises a TypeError, the value is reported as an
            unsupported type.
        _level (int):
            The number of indentation levels.  When dumps is invoked recursively
            this is used to increment the level and so the indent.  This argument
            is use internally and should not be specified by the user.

    Returns:
        The *NestedText* content.

    Raises:
        NestedTextError: if there is a problem in the input data.

    Examples:

        .. code-block:: python

            >>> import nestedtext as nt

            >>> data = {
            ...     'name': 'Kristel Templeton',
            ...     'sex': 'female',
            ...     'age': '74',
            ... }

            >>> try:
            ...     print(nt.dumps(data))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            name: Kristel Templeton
            sex: female
            age: 74

        The *NestedText* format only supports dictionaries, lists, and strings.
        By default, *dumps* is configured to be rather forgiving, so it will
        render many of the base Python data types, such as *None*, *bool*,
        *int*, *float* and list-like types such as *tuple* and *set* by
        converting them to the types supported by the format.  This implies that
        a round trip through *dumps* and *loads* could result in the types of
        values being transformed. You can restrict *dumps* to only supporting
        the native types of *NestedText* by passing `default='strict'` to
        *dumps*.  Doing so means that values that are not dictionaries, lists,
        or strings generate exceptions.

        .. code-block:: python

            >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}

            >>> try:
            ...     print(nt.dumps(data))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            key: 42
            value: 3.1415926
            valid: True

            >>> try:
            ...     print(nt.dumps(data, default='strict'))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            42: unsupported type.

        Alternatively, you can specify a function to *default*, which is used
        to convert values to recognized types.  It is used if no suitable
        converter is available.  Typical values are *str* and *repr*.

        .. code-block:: python

            >>> class Color:
            ...     def __init__(self, color):
            ...         self.color = color
            ...     def __repr__(self):
            ...         return f'Color({self.color!r})'
            ...     def __str__(self):
            ...         return self.color

            >>> data['house'] = Color('red')
            >>> print(nt.dumps(data, default=repr))
            key: 42
            value: 3.1415926
            valid: True
            house: Color('red')

            >>> print(nt.dumps(data, default=str))
            key: 42
            value: 3.1415926
            valid: True
            house: red

        If *Color* is consistently used with *NestedText*, you can include the
        converter in *Color* itself.

        .. code-block:: python

            >>> class Color:
            ...     def __init__(self, color):
            ...         self.color = color
            ...     def __nestedtext_converter__(self):
            ...         return self.color.title()

            >>> data['house'] = Color('red')
            >>> print(nt.dumps(data))
            key: 42
            value: 3.1415926
            valid: True
            house: Red

        You can also specify a dictionary of converters. The dictionary maps the
        object type to a converter function.

        .. code-block:: python

            >>> class Info:
            ...     def __init__(self, **kwargs):
            ...         self.__dict__ = kwargs

            >>> converters = {
            ...     bool: lambda b: 'yes' if b else 'no',
            ...     int: hex,
            ...     float: lambda f: f'{f:0.3}',
            ...     Color: lambda c: c.color,
            ...     Info: lambda i: i.__dict__,
            ... }

            >>> data['attributes'] = Info(readable=True, writable=False)

            >>> try:
            ...    print(nt.dumps(data, converters=converters))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            key: 0x2a
            value: 3.14
            valid: yes
            house: red
            attributes:
                readable: yes
                writable: no

        The above example shows that *Color* in the *converters* argument
        dominates over the ``__nestedtest__converter__`` class.

        If the dictionary maps a type to *None*, then the default behavior is
        used for that type. If it maps to *False*, then an exception is raised.

        .. code-block:: python

            >>> converters = {
            ...     bool: lambda b: 'yes' if b else 'no',
            ...     int: hex,
            ...     float: False,
            ...     Color: lambda c: c.color,
            ...     Info: lambda i: i.__dict__,
            ... }

            >>> try:
            ...    print(nt.dumps(data, converters=converters))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            3.1415926: unsupported type.

        *converters* need not actually change the type of a value, it may simply
        transform the value.  In the following example, *converters* is used to
        transform dictionaries by removing empty dictionary fields.  It is also
        converts dates and physical quantities to strings.

        .. code-block:: python

            >>> import arrow
            >>> from inform import cull
            >>> import quantiphy

            >>> class Dollars(quantiphy.Quantity):
            ...     units = '$'
            ...     form = 'fixed'
            ...     prec = 2
            ...     strip_zeros = False
            ...     show_commas = True

            >>> converters = {
            ...     dict: cull,
            ...     arrow.Arrow: lambda d: d.format('D MMMM YYYY'),
            ...     quantiphy.Quantity: lambda q: str(q)
            ... }

            >>> transaction = dict(
            ...     date = arrow.get('2013-05-07T22:19:11.363410-07:00'),
            ...     description = "Incoming wire from Publisher's Clearing House",
            ...     debit = 0,
            ...     credit = Dollars(12345.67)
            ... )

            >>> print(nt.dumps(transaction, converters=converters))
            date: 7 May 2013
            description: Incoming wire from Publisher's Clearing House
            credit: $12,345.67

        Both *default* and *converters* may be used together. *converters* has
        priority over the built-in types and *default*.  When a function is
        specified as *default*, it is always applied as a last resort.
    """

    # code {{{3
    dumper = NestedTextDumper(
        width, inline_level, sort_keys, indent, converters, default
    )
    return dumper.render_content(obj, 0)


# dump {{{2
def dump(obj, f, **kwargs):
    # description {{{3
    """Write the *NestedText* representation of the given object to the given file.

    Args:
        obj:
            The object to convert to *NestedText*.
        f (str, os.PathLike, io.TextIOBase):
            The file to write the *NestedText* content to.  The file can be
            specified either as a path (e.g. a string or a `pathlib.Path`) or
            as a text IO instance (e.g. an open file).  If a path is given, the
            will be opened, written, and closed.  If an IO object is given, it
            must have been opened in a mode that allows writing (e.g.
            ``open(path, 'w')``), if applicable.  It will be written and not
            closed.

            The name used for the file is arbitrary but it is tradition to use a
            .nt suffix.  If you also wish to further distinguish the file type
            by giving the schema, it is recommended that you use two suffixes,
            with the suffix that specifies the schema given first and .nt given
            last. For example: flicker.sig.nt.

        kwargs:
            See :func:`dumps` for optional arguments.

    Returns:
        The *NestedText* content.

    Raises:
        NestedTextError: if there is a problem in the input data.
        OSError: if there is a problem opening the file.

    Examples:

        This example writes to a pointer to an open file.

        .. code-block:: python

            >>> import nestedtext as nt
            >>> from inform import fatal, os_error

            >>> data = {
            ...     'name': 'Kristel Templeton',
            ...     'sex': 'female',
            ...     'age': '74',
            ... }

            >>> try:
            ...     with open('data.nt', 'w', encoding='utf-8') as f:
            ...         nt.dump(data, f)
            ... except nt.NestedTextError as e:
            ...     e.terminate()
            ... except OSError as e:
            ...     fatal(os_error(e))

        This example writes to a file specified by file name.  In general, the
        file name and extension are arbitrary. However, by convention a
        '.nt' suffix is generally used for *NestedText* files.

        .. code-block:: python

            >>> try:
            ...     nt.dump(data, 'data.nt')
            ... except nt.NestedTextError as e:
            ...     e.terminate()
            ... except OSError as e:
            ...     fatal(os_error(e))

    """

    # code {{{3
    content = dumps(obj, **kwargs)

    try:
        f.write(content)
    except AttributeError:
        # Avoid nested try-except blocks, since they lead to chained exceptions
        # (e.g. if the file isn't found, etc.) that unnecessarily complicate the
        # stack trace.
        pass
    else:
        return

    with open(f, 'w', encoding='utf-8') as f:
        f.write(content)
