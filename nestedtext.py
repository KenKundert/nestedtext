# encoding: utf8
"""
NestedText: A Human Readable and Writable Data Format
"""

# MIT License {{{1
# Copyright (c) 2020-21 Kenneth S. Kundert and Kale Kundert
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
    conjoin,
    full_stop,
    set_culprit,
    get_culprit,
    is_str,
    is_collection,
    is_mapping,
    Error,
    Info,
)
from parsy import generate, regex, ParseError
import textwrap
import collections.abc
import re


# Globals {{{1
__version__ = "1.3.6"
__released__ = "2021-05-08"
__all__ = ['load', 'loads', 'dump', 'dumps', 'NestedTextError']


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

        The number of the line where the problem was found.

    colno:

        The number of the character where the problem was found on *line*.

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

    Note the « and » characters in the codicil. They delimit the extend of the
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
    (?P<key>.*?)           # key
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
        kwargs['culprit'] = get_culprit(line.lineno)
        if colno is not None:
            # build codicil that shows both the line and the preceding line
            if line.prev_line is not None:
                codicil = [f'{line.prev_line.lineno:>4} «{line.prev_line.text}»']
            else:
                codicil = []
            codicil += [
                f'{line.lineno:>4} «{line.text}»',
                '      ' + (colno*' ') + '▲',
            ]
            kwargs['codicil'] = '\n'.join(codicil)
            kwargs['colno'] = colno
        else:
            kwargs['codicil'] = f'{line.lineno:>4} «{line.text}»'
        kwargs['line'] = line.text
        kwargs['lineno'] = line.lineno
        if line.prev_line:
            kwargs['prev_line'] = line.prev_line.text
    else:
        kwargs['culprit'] = culprits  # pragma: no cover
    raise NestedTextError(template=message, *args, **kwargs)


# indentation_error {{{2
def indentation_error(line, depth):
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
        pass

    # read_lines() {{{3
    def read_lines(self):
        prev_line = None
        for lineno, line in enumerate(self.lines):
            key = None
            value = None
            line = line.rstrip('\n')

            # compute indentation
            stripped = line.lstrip()
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
                kind = "inline"
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
                lineno = lineno+1,
                kind = kind,
                depth = depth,
                key = key,
                value = value,
                prev_line = prev_line,
            )
            if kind.endswith(' item'):
                prev_line = the_line

            # check the indent for non-spaces
            if depth:
                first_non_space = len(line) - len(line.lstrip(" "))
                if first_non_space < depth:
                    report(
                        f'invalid character in indentation: {line[first_non_space]!r}.',
                        the_line,
                        colno = first_non_space
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
            report('unrecognized line.', this_line)
        return this_line


# read_value() {{{2
def read_value(lines, depth, on_dup):
    if lines.type_of_next() == "list item":
        return read_list(lines, depth, on_dup)
    if lines.type_of_next() in ["dict item", "key item"]:
        return read_dict(lines, depth, on_dup)
    if lines.type_of_next() == "string item":
        return read_string(lines, depth)
    if lines.type_of_next() == "inline":
        return read_inline(lines)
    report('unrecognized line.', lines.get_next())


# read_list() {{{2
def read_list(lines, depth, on_dup):
    data = []
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind != "list item":
            report("expected list item.", line, colno=depth)
        if line.value:
            data.append(line.value)
        else:
            # value may simply be empty, or it may be on next line, in which
            # case it must be indented.
            depth_of_next = lines.depth_of_next()
            if depth_of_next > depth:
                value = read_value(lines, depth_of_next, on_dup)
            else:
                value = ''
            data.append(value)
    return data


# read_dict() {{{2
def read_dict(lines, depth, on_dup):
    data = {}
    while lines.still_within_level(depth):
        line = lines.get_next()
        if line.depth != depth:
            indentation_error(line, depth)
        if line.kind not in ["dict item", "key item"]:
            report("expected dictionary item.", line, colno=depth)
        if line.kind == "key item":
            # multiline key
            key = read_key(lines, line, depth)
            value = None
        else:
            # inline key
            key = line.key
            value = line.value

        if not value:
            depth_of_next = lines.depth_of_next()
            if depth_of_next > depth:
                value = read_value(lines, depth_of_next, on_dup)
            elif line.kind == "dict item":
                value = ''
            else:
                report('multiline key requires a value.', line, None, colno=depth)

        if line.key in data:
            # found duplicate key
            if on_dup is None:
                report('duplicate key: {}.', line, line.key, colno=depth)
            if on_dup == 'ignore':
                continue
            if isinstance(on_dup, dict):
                key = on_dup['_callback_func'](key, value, data, on_dup)
                assert key not in data
            elif on_dup != 'replace':
                raise NotImplementedError(f'{on_dup}: unknown value for on_dup.')
        data[key] = value
    return data


# read_string() {{{2
def read_string(lines, depth):
    data = []
    while lines.still_within_string(depth):
        line = lines.get_next()
        data.append(line.value)
        if line.depth != depth:
            indentation_error(line, depth)
    return "\n".join(data)


# read_key() {{{2
def read_key(lines, line, depth):
    data = [line.value]
    while lines.still_within_key(depth):
        line = lines.get_next()
        data.append(line.value)
    return "\n".join(data)


# read_all() {{{2
def read_all(lines, top, source, on_dup):
    if callable(on_dup):
        on_dup = dict(_callback_func=on_dup)

    with set_culprit(source):
        lines = Lines(lines)

        if top in ['any', any]:
            if lines.type_of_next():
                return read_value(lines, 0, on_dup)
            else:
                return None

        next_is = lines.type_of_next()

        if top in ['dict', dict]:
            if next_is in ["dict item", "key item"]:
                return read_dict(lines, 0, on_dup)
            elif next_is:
                report('content must start with key.', lines.get_next())
            else:
                return {}

        if top in ['list', list]:
            if next_is == "list item":
                return read_list(lines, 0, on_dup)
            elif next_is:
                report('content must start with dash (-).', lines.get_next())
            else:
                return []

        if top in ['str', str]:
            if next_is == "string item":
                return read_string(lines, 0)
            elif next_is:
                report('content must start with greater-than sign (>).', lines.get_next())
            else:
                return ""

        raise NotImplementedError(top)


# read_inline() {{{2
def read_inline(lines):
    line = lines.get_next()
    value = line.value
    try:
        return (inline_list | inline_dict).parse(value)
    except ParseError as e:
        expected = sorted(lexer_aliases.get(x, x) for x in e.expected)
        msg = f'expected {conjoin(expected, conj=", or ")}.'
        msg = msg.replace('{', r'{{').replace('}', r'}}')
        report(msg, line, colno=e.index + line.depth)


# inline_list() {{{3
@generate
def inline_list():
    yield list_open
    items = yield list_value.sep_by(sep)
    trailing_sep = yield sep.optional()
    yield list_close

    if not trailing_sep and items[-1] == '':
        items.pop()

    return items


# inline_dict() {{{3
@generate
def inline_dict():
    yield dict_open
    items = yield dict_item.sep_by(sep)
    yield sep.optional()
    yield dict_close
    return dict(items)


# dict_item() {{{3
@generate
def dict_item():
    key = yield dict_key
    yield dict_key_sep
    value = yield dict_value
    return key, value


# strip() {{{3
def strip(x):
    return x.strip()


# parsing rules() {{{3
padded_literal = lambda x: regex(rf'{re.escape(x)}\s*').desc(repr(x))
list_open = padded_literal('[')
list_close = padded_literal(']')
list_value = inline_list | inline_dict | regex(r'[^{}[\],]*').map(strip)
dict_open = padded_literal('{')
dict_close = padded_literal('}')
dict_key = regex(r'[^{}[\],:]*').map(strip).desc('key')
dict_key_sep = padded_literal(':')
dict_value = inline_list | inline_dict | dict_key
sep = padded_literal(',')
lexer_aliases = dict(EOF='end of line')


# loads() {{{2
def loads(content, top='dict', *, source=None, on_dup=None):
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

    Returns:
        The extracted data.  The type of the return value is specified by the
        top argument.  If top is 'any', then the return value will match that of
        top-level data container in the input content. If content is empty, an
        empty data value is return of the type specified by top. If top is
        'any' None is returned.

    Raises:
        NestedTextError: if there is a problem in the *NextedText* content.

    Examples:

        *NestedText* is specified to *loads* in the form of a string:

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
    lines = content.replace('\r\n', '\n').replace('\r', '\n').split('\n')
    return read_all(lines, top, source, on_dup)


# load() {{{2
def load(f=None, top='dict', *, on_dup=None):
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
    # pointer into read_all(), it will iterate through the lines, discarding
    # them once they are no longer needed, which reduces the memory usage.

    if isinstance(f, collections.abc.Iterator):
        source = getattr(f, 'name', None)
        return read_all(f, top, source, on_dup)
    else:
        source = str(f)
        with open(f, encoding='utf-8') as fp:
            return read_all(fp, top, source, on_dup)


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


# dumps {{{2
def dumps(
    obj,
    *,
    width = 0,
    sort_keys = False,
    indent = 4,
    converters = None,
    default = None,
    _level = 0
):
    # description {{{3
    """Recursively convert object to *NestedText* string.

    Args:
        obj:
            The object to convert to *NestedText*.
        width (int):
            Enables compact lists and dictionaries if greater than zero and if
            resulting line would be less than or equal to given width.
        sort_keys (bool or func):
            Dictionary items are sorted by their key if *sort_keys* is true.
            If a function is passed in, it is used as the key function.
        indent (int):
            The number of spaces to use to represent a single level of
            indentation.  Must be one or greater.
        converters (dict):
            A dictionary where the keys are types and the values are converter
            functions (functions that take an object and convert it into a form
            that can be processed by NestedText).  If a value is False, an
            unsupported type error is raised.

            An object may provide its own converter by defining the
            ``__nestedtext_converter__`` attribute.  It may be False, or it may
            be a method that converts the object to a supported data type for
            NestedText.  Converters specified in the argument dominate over the
            ``__nestedtext_converter__`` attribute.
        default (func or 'strict'):
            The default converter. Use to convert otherwise unrecognized objects
            to a form that can be processed. If not provided an error will be
            raised for unsupported data types. Typical values are *repr* or
            *str*. If 'strict' is specified then only dictionaries, lists,
            strings, and those types specified in *converters* are allowed. If
            *default* is not specified then a broader collection of value types
            are supported, including *None*, *bool*, *int*, *float*, and *list*-
            and *dict*-like objects.  In this case Booleans are rendered as
            'True' and 'False' and None is rendered as an empty string.  If
            *default* is a function, it acts as the default converter.  If
            converter raises a TypeError, the value is reported as an
            unsupported type.
        _level (int):
            The number of indentation levels.  When dumps is invoked recursively
            this is used to increment the level and so the indent.  Should not
            be specified by the user.

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
        or strings generate exceptions; as do empty dictionaries and lists.

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
        to convert values to strings.  It is used if no other converter is
        available.  Typical values are *str* and *repr*.

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

        Both *default* and *converters* may be used together. *converters* has
        priority over the built-in types and *default*.  When a function is
        specified as *default*, it is always applied as a last resort.
    """

    # define sort function {{{3
    if sort_keys:
        def sort(keys):
            return sorted(keys, key=sort_keys if callable(sort_keys) else None)
    else:
        def sort(keys):
            return keys

    # convert {{{3
    def convert(obj):
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

    # render_dict_item {{{3
    def render_dict_item(key, dictionary, indent, rdumps):
        value = dictionary[key]
        if is_a_scalar(key):
            key = str(key)
        if not is_a_str(key):
            raise NestedTextError(
                template = 'keys must be strings.',
                culprit = key
            ) from None
        multiline_key_required = (
            not key
            or '\n' in key
            or key.strip(' ') != key
            or key[:1] in "#[{"
            or key[:2] in ["- ", "> ", ": "]
            or ': ' in key
        )
        if multiline_key_required:
            key = "\n".join(": "+l if l else ":" for l in key.split('\n'))
            if is_str(value):
                # force use of multiline value with multiline keys
                return key + "\n" + add_leader(value, indent*' ' + '> ')
            else:
                return key + rdumps(value)
        else:
            return add_prefix(key + ":", rdumps(value))

    # render_inline_dict {{{3
    def render_inline_dict(obj):
        exclude = set('\n[]{}:,')
        items = []
        for k in sort(obj):
            v = render_inline_value(obj[k], exclude=exclude)
            k = render_inline_scalar(k, exclude=exclude)
            items.append(f'{k}: {v}')
        return '{' + ', '.join(items) + '}'

    # render_inline_list {{{3
    def render_inline_list(obj):
        items = []
        for v in obj:
            v = render_inline_value(v, exclude=set('\n[]{},'))
            items.append(v)
        endcap = ', ]' if len(items) and items[-1] == '' else ']'
        return '[' + ', '.join(items) + endcap

    # render_inline_value {{{3
    def render_inline_value(obj, exclude):
        obj = convert(obj)
        if is_a_dict(obj):
            return render_inline_dict(obj)
        if is_a_list(obj):
            return render_inline_list(obj)
        return render_inline_scalar(obj, exclude)

    # render_inline_scalar {{{3
    def render_inline_scalar(obj, exclude):
        if is_a_str(obj):
            value = obj
        elif is_a_scalar(obj):
            value = '' if obj is None else str(obj)
        elif default and callable(default):
            try:
                obj = default(obj)
            except TypeError:
                raise NestedTextError(
                    obj,
                    template = "unsupported type.",
                    culprit = repr(obj)
                ) from None
            return render_inline_value(obj, exclude)
        else:
            raise NotSuitableForInline()

        if exclude & set(value):
            raise NotSuitableForInline()
        if value.strip(' ') != value:
            raise NotSuitableForInline()
        return value

    # define object type identification functions {{{3
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

    # define dumps function for recursion {{{3
    def rdumps(v):
        return dumps(
            v,
            width = width - indent,
            sort_keys = sort_keys,
            indent = indent,
            converters = converters,
            default = default,
            _level = _level + 1
        )

    # render content {{{3
    assert indent > 0
    error = None
    content = ''
    obj = convert(obj)
    need_indented_block = is_collection(obj)

    if is_a_dict(obj):
        try:
            if obj and not (width > 0 and len(obj) <= width/6):
                raise NotSuitableForInline
            content = render_inline_dict(obj)
            if obj and len(content) > width:
                raise NotSuitableForInline
        except NotSuitableForInline:
            content = "\n".join(
                render_dict_item(k, obj, indent, rdumps)
                for k in sort(obj)
            )
    elif is_a_list(obj):
        try:
            if obj and not (width > 0 and len(obj) <= width/6):
                raise NotSuitableForInline
            content = render_inline_list(obj)
            if obj and len(content) > width:
                raise NotSuitableForInline
        except NotSuitableForInline:
            content = "\n".join(
                add_prefix("-", rdumps(v))
                for v in obj
            )
    elif is_a_str(obj):
        text = obj.replace('\r\n', '\n').replace('\r', '\n')
        if "\n" in text or _level == 0:
            content = add_leader(text, '> ')
            need_indented_block = True
        else:
            content = text
    elif is_a_scalar(obj):
        if obj is None:
            content = ''
        else:
            content = str(obj)
    elif default and callable(default):
        try:
            obj = default(obj)
        except TypeError:
            error = 'unsupported type.'
        else:
            content = dumps(
                obj,
                width = width,
                sort_keys = sort_keys,
                indent = indent,
                converters = converters,
                default = default,
                _level = _level
            )
    else:
        error = 'unsupported type.'

    if need_indented_block and content and _level:
        content = "\n" + add_leader(content, indent*' ')

    if error:
        raise NestedTextError(obj, template=error, culprit=repr(obj))

    return content


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

    with open(f, 'w', encoding='utf-8') as fp:
        fp.write(content)
