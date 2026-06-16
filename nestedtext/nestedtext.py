# encoding: utf8
"""
NestedText: A Human Readable and Writable Data Format

NestedText is a file format for holding structured data that is intended to be
entered, edited, or viewed by people.  It allows data to be organized into a
nested collection of itemized lists (dictionaries), ordered lists (lists), and
scalar text (strings).

It is easily created, modified, or viewed with a text editor and easily
understood and used by both programmers and non-programmers.
"""

# MIT License {{{1
# Copyright (c) 2020-2026 Ken and Kale Kundert
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
    cull,
    full_stop,
    set_culprit,
    get_culprit,
    is_str,
    is_collection,
    is_mapping,
    join,
    plural,
    Error,
    Info,
)
import collections.abc
import io
import re
import unicodedata


# Utility functions {{{1
# convert_line_terminators {{{2
def convert_line_terminators(text):
    return text.replace("\r\n", "\n").replace("\r", "\n")


# Unspecified {{{2
# class that is used as a default in functions to signal nothing was given
class _Unspecified:
    def __bool__(self):  # pragma: no cover
        return False


# OnDupCallback {{{2
class _OnDupCallback(_Unspecified):
    pass


# Exceptions {{{1
# NestedTextError {{{2
class NestedTextError(Error, ValueError):
    r'''
    The *load* and *dump* functions all raise *NestedTextError* when they
    discover an error. *NestedTextError* subclasses both the Python *ValueError*
    and the *Error* exception from *Inform*.  You can find more documentation on
    what you can do with this exception in the `Inform documentation
    <https://inform.readthedocs.io/en/stable/api.html#exceptions>`_.

    All exceptions provide the following attributes:

    Attributes:
        args:
            The exception arguments.  A tuple that usually contains the
            problematic value.

        template:
            The possibly parameterized text used for the error message.

    Exceptions raised by the :func:`loads()` or :func:`load()` functions provide
    the following additional attributes:

    Attributes:
        source:
            The source of the *NestedText* content, if given. This is often a
            filename.

        line:
            The text of the line of *NestedText* content where the problem was found.

        prev_line:
            The text of the meaningful line immediately before where the problem was
            found.  This will not be a comment or blank line.

        lineno:
            The number of the line where the problem was found.  Line numbers are
            zero based except when included in messages to the end user.

        colno:
            The number of the character where the problem was found on *line*.
            Column numbers are zero based.

        codicil:
            The line that contains the error decorated with the location of the
            error.

    The exception culprit is the tuple that indicates where the error was found.
    With exceptions from :func:`loads()` or :func:`load()`, the culprit consists
    of the source name, if available, and the line number.  With exceptions from
    :func:`dumps()` or :func:`dump()`, the culprit consists of the keys that
    lead to the problematic value.

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
               1 ❬name1: value1❭
               2 ❬name1: value2❭
                  ▲

    You can also use the *report* method to print the message directly. This is
    appropriate if you are using *inform* for your messaging as it follows
    *inform*’s conventions::

        >> try:
        ..     print(nt.loads(content))
        .. except nt.NestedTextError as e:
        ..     e.report()
        error: 2: duplicate key: name1.
            ❬name1: value2❭
             ▲

    The *terminate* method prints the message directly and exits::

        >> try:
        ..     print(nt.loads(content))
        .. except nt.NestedTextError as e:
        ..     e.terminate()
        error: 2: duplicate key: name1.
            ❬name1: value2❭
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
           1 ❬name1: value1❭
           2 ❬name1: value2❭
              ▲

    Note the ❬ and ❭ characters in the codicil. They delimit the extent of the
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
        ...     if e.template == "duplicate key: {}.":
        ...         template = "llave duplicada: {}."
        ...     print(e.render(template=template))
        2: llave duplicada: name1.
               1 ❬name1: value1❭
               2 ❬name1: value2❭
                  ▲
    '''

# NT_DataError {{{2
class NestedTextDataError(NestedTextError):
    '''
    This exception is not emitted by NestedText itself, rather it is made
    available for reporting on errors that derive from loaded NestedText data.
    It includes information that would allow the user to easily find the
    offending datum.

    It supports the same arguments as the NestedTextError.  Specifically, you
    can specify any number of unnnamed arguments, that will be joined together
    to form the message.  It also accepts a *template* keyword argument that can
    be used to combine the arguments into a message.  In addition, it supports
    the following keyword-only arguments.

        source (str):
            The name of source file.
        keys (tuple(str)):
            The keys that uniquely identify the datum.
        keymap:
            The keymap created by the loader.
        kind (str):
            Either "value" or "key".  Identifies the offending part of the
            datum. Default is "value".
        offset (None or int):
            The location of the problem.  If not None, a pointer is added that
            points the specified location (given in the number of characters
            from the start of the value).
        show_line (bool):
            Whether or not to show the line in the NestedText document that
            contains the error.
    '''

    # constructor {{{3
    def __init__(
        self, *args,
        source='', keymap=None, keys=None,
        kind="value", offset=None, show_line=True,
        culprit=(), codicil=(),
        **kwargs
    ):
        # Users can use NestedTextError for their own errors.  To do so they
        # would pass a message or a message template along with the source, the
        # keymap, the offending keys, whether the problem is in the key or the
        # value, and perhaps an offset, and the information will be converted
        # into a suitable culprit and codicil.
        if is_str(culprit):
            culprit = cull((culprit,))
        if is_str(codicil):
            codicil = cull((codicil,))

        if keys and keymap:
            loc = get_location(keys, keymap)
            line_nums = loc.get_line_numbers(kind=kind, sep='-')
            if line_nums:
                source += f"@{line_nums}"
            orig_keys = get_keys(keys, keymap, sep="›")
            culprit = (source or None,) + (orig_keys,) + culprit
            kwargs['culprit'] = culprit

            if show_line:
                codicil += loc.as_line(kind=kind, offset=offset),
            kwargs['codicil'] = codicil
        super().__init__(*args, **kwargs)


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
    codicil = [kwargs.get("codicil", "")]
    if culprits:
        kwargs["source"] = culprits[0]
    if line:
        # line numbers are always 0 based unless included in a message to user
        include_prev_line = not (
            line.prev_line is None or kwargs.pop("suppress_prev_line", False)
        )
        if colno is not None:
            # build codicil that shows both the line and the preceding line
            if include_prev_line:
                codicil += [f"{line.prev_line.lineno+1:>4} ❬{line.prev_line.text}❭"]
            else:
                codicil += []
            # replace tabs with → so that arrow points to right location.
            text = line.text.replace("\t", "→")
            codicil += [
                f"{line.lineno+1:>4} ❬{text}❭",
                "      " + (colno*" ") + "▲",
            ]
            kwargs["codicil"] = "\n".join(cull(codicil))
            kwargs["colno"] = colno
        else:
            kwargs["codicil"] = f"{line.lineno+1:>4} ❬{line.text}❭"
        kwargs["culprit"] = get_culprit(line.lineno + 1)
        kwargs["line"] = line.text
        kwargs["lineno"] = line.lineno
        if include_prev_line:
            kwargs["prev_line"] = line.prev_line.text
    else:
        kwargs["culprit"] = culprits  # pragma: no cover
    raise NestedTextError(template=message, *args, **kwargs)


# unrecognized_line {{{2
def unrecognized_line(line):
    # line will not be recognized if there is invalid white space in indentation
    first_non_space = line.text.lstrip(" ")[0]
    index_of_first_non_space = line.text.index(first_non_space)
    if first_non_space.strip() == "":
        # first non-space is a white space character
        # treat it as invalid indentation
        desc = unicodedata.name(first_non_space, "")
        if desc:
            desc = f" ({desc})"
        report(
            f"invalid character in indentation: {first_non_space!r}{desc}.",
            line,
            colno = index_of_first_non_space,
            codicil = "Only simple spaces are allowed in indentation."
        )
    else:
        report("unrecognized line.", line, colno=index_of_first_non_space)


# Lines class {{{2
class Lines:
    # constructor {{{3
    def __init__(self, lines, support_inlines):
        self.lines = lines
        self.support_inlines = support_inlines
        self.generator = self.read_lines()
        self.first_value_line = None
        self.last_comment_line = None
            # a location is needed for the top of the data, keys = ()
            # use the first value given, if the data is not empty
            # use last comment given if data is empty
        # comment-capture state
        self.prev_data_line = None
        self.header_comments = []   # comments before the first data item
        self.eof_comments = []      # footer comments (after the last data item)
        self._comment_buffer = []   # raw comment/blank Lines awaiting attachment
        self.next_line = None
        self._advance_to_data_line()

    # Line class {{{3
    class Line(Info):
        def render(self, col=None):
            result = [f"{self.lineno+1:>4} ❬{self.text}❭"]
            if col is not None:
                l = len(self.text)
                if l < col:
                    col = l
                result += ["      " + (col*" ") + "▲"]
            return "\n".join(result)

        def __str__(self):
            return self.text

        def __repr__(self):
            return self.__class__.__name__ + f"({self.lineno+1}: ❬{self.text}❭)"

    # read_lines() {{{3
    def read_lines(self):
        prev_line = None
        last_line = None
        for lineno, line in enumerate(self.lines):
            key = None
            value = None
            try:
                # decode to utf8 if a byte string or binary file is given
                line = line.decode('utf8')
            except AttributeError:
                pass
            line = line.rstrip("\n")

            # compute indentation
            stripped = line.lstrip(" ")
            depth = len(line) - len(stripped)

            # determine line type and extract values
            if stripped == "":
                kind = "blank"
                value = None
                depth = None
            elif stripped[:1] == "#":
                kind = "comment"
                # remove the '#' and exactly one optional space (the canonical
                # form is '# text'); rstrip whitespace.  This preserves
                # additional leading spaces inside the comment text so that
                # the dumper can round-trip them faithfully.
                value = stripped[1:]
                if value.startswith(" "):
                    value = value[1:]
                value = value.rstrip()
                # depth stays at the computed indent; needed for comment partitioning
            elif stripped == "-" or stripped.startswith("- "):
                kind = "list item"
                value = stripped[2:]
            elif stripped == ">" or stripped.startswith("> "):
                kind = "string item"
                value = line[depth+2:]
            elif stripped == ":" or stripped.startswith(": "):
                kind = "key item"
                value = line[depth+2:]
            elif stripped[0:1] in ["[", "{"] and self.support_inlines:
                tag = stripped[0:1]
                kind = "inline dict" if tag == "{" else "inline list"
                value = line[depth:]
            else:
                matches = dict_item_recognizer.fullmatch(stripped)
                if matches:
                    kind = "dict item"
                    key = matches.group("key")
                    value = matches.group("value")
                    if value is None:
                        value = ""
                else:
                    kind = "unrecognized"
                    value = line

            # bundle information about line
            this_line = self.Line(
                text = line,
                lineno = lineno,
                kind = kind,
                depth = depth,
                key = key,
                value = value,
                prev_line = prev_line,
            )
            if kind.endswith(" item") or kind.startswith("inline "):
                # Create prev_line, which differs from last_line in that it
                # is a copy of the line without a prev_line attribute of its
                # own. This avoids keeping a chain of all previous lines.
                #
                # In contrast, last_line is the actual this_line from the previous
                # non-blank/comment iteration
                prev_line = self.Line(
                    text = this_line.text,
                    value = this_line.value,
                    kind = this_line.kind,
                    depth = this_line.depth,
                    lineno = this_line.lineno,
                )

                # add this line as next_line in prev_line if this is a continued
                # multiline key or multiline string.
                if (
                    last_line                 and
                    depth == last_line.depth  and
                    kind == last_line.kind    and
                    kind in ["key item", "string item"]
                ):
                    last_line.next_line = this_line

            if kind in ['blank', 'comment']:
                self.last_comment_line = this_line
            else:
                last_line = this_line
                if not self.first_value_line:
                    self.first_value_line = this_line
            yield this_line

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
    def still_within_key(self, line, depth):
        if not self.next_line:
            report("indented value must follow multiline key", line)
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
        line = self.next_line
        if line.kind == "unrecognized":
            unrecognized_line(line)

        # ensure the staging lists exist (Info returns None for unset attrs,
        # a fresh list is needed before the upcoming advance can append).
        line.trailing_comments = line.trailing_comments or []
        line.leading_comments = line.leading_comments or []

        self.prev_data_line = line

        # queue up the next useful line, capturing comments along the way.
        self._advance_to_data_line()

        return line

    # _advance_to_data_line() {{{3
    def _advance_to_data_line(self):
        """Pull from the generator until the next data line (or EOF).

        Buffered comment/blank lines are grouped into Comment objects and
        partitioned per the rules onto the surrounding data lines.
        """
        self.next_line = next(self.generator, None)
        while self.next_line and self.next_line.kind in ["blank", "comment"]:
            self._comment_buffer.append(self.next_line)
            self.next_line = next(self.generator, None)

        buffer_lines = self._comment_buffer
        self._comment_buffer = []

        if self.next_line is not None:
            self.next_line.leading_comments = self.next_line.leading_comments or []
            self.next_line.trailing_comments = self.next_line.trailing_comments or []

        if not buffer_lines:
            return

        if self.prev_data_line is None and self.next_line is not None:
            # before the first data line: rule 1 (Header / leading)
            # Partition on the raw buffer at the last blank line, then group
            # each half.  A comment block is leading on the first key only
            # when there is *no* blank between it and that key.
            header_lines, leading_lines = _partition_header_leading(buffer_lines)
            self.header_comments.extend(_group_comments(header_lines))
            self.next_line.leading_comments.extend(_group_comments(leading_lines))
        elif self.prev_data_line is None and self.next_line is None:
            # rule "No data" -- entire content is header
            self.header_comments.extend(_group_comments(buffer_lines))
        elif self.next_line is None:
            # after the last data line: rule 4 (Trailing / footer)
            last_indent = self.prev_data_line.depth or 0
            for c in _group_comments(buffer_lines):
                if c.indent > last_indent:
                    self.prev_data_line.trailing_comments.append(c)
                else:
                    self.eof_comments.append(c)
        else:
            # between two data lines: rule 2 (Leading / trailing)
            next_indent = self.next_line.depth or 0
            for c in _group_comments(buffer_lines):
                if c.indent <= next_indent:
                    self.next_line.leading_comments.append(c)
                else:
                    self.prev_data_line.trailing_comments.append(c)

    # indentation_error {{{3
    def indentation_error(self, line, depth):
        assert line.depth != depth
        prev_line = line.prev_line
        codicil = None
        if not line.prev_line and depth == 0:
            msg = "top-level content must start in column 1."
        elif (
            prev_line                     and
            prev_line.value               and
            prev_line.depth < line.depth  and
            prev_line.kind in ["list item", "dict item"]
        ):
            if prev_line.value.strip() == "":
                obs = ", which in this case consists only of whitespace"
            else:
                obs = ""
            msg = "invalid indentation."
            codicil = join(
                "An indent may only follow a dictionary or list item that does",
                f"not already have a value{obs}.",
                wrap = True
            )
        elif prev_line and prev_line.depth > line.depth:
            msg = "invalid indentation, partial dedent."
        else:
            msg = "invalid indentation."
        report(join(msg, wrap=True), line, colno=depth, codicil=codicil)


# KeyPolicy class {{{2
# Used to hold and implement the on_dup policy for dictionaries.
class KeyPolicy:
    @classmethod
    def set_policy(cls, on_dup):
        if callable(on_dup):
            # if on_dup is a function, convert it to a data structure that will
            # hold state during the load
            on_dup = {_OnDupCallback: on_dup}
        cls.on_dup = on_dup

    @classmethod
    def process_duplicate(cls, dictionary, key, keys, line=None, colno=None):
        if cls.on_dup is None or cls.on_dup == "error":
            report("duplicate key: {}.", line, key, colno=colno)
        if cls.on_dup == "ignore":
            return None
        if isinstance(cls.on_dup, dict):
            dup_handler = cls.on_dup.pop(_OnDupCallback)
            cls.on_dup.update(
                dict(dictionary=dictionary, keys=keys)
            )
            try:
                key = dup_handler(key=key, state=cls.on_dup)
                if key is None:
                    return None
            except KeyError:
                report("duplicate key: {}.", line, key, colno=colno)
            cls.on_dup[_OnDupCallback] = dup_handler  # restore dup_handler
        elif cls.on_dup != "replace":  # pragma: no cover
            raise AssertionError(
                f"{cls.on_dup}: unexpected value for on_dup."
            ) from None
        return key


# Comment class {{{2
class Comment:
    """A single comment captured during load or built by the user.

    Holds the comment text (joined by ``\\n`` for multi-line comments) plus
    indent and per-comment blank-line metadata.

    *indent* is the absolute indentation (in spaces) at which the comment's
    ``#`` will be placed.  It is set by the loader and is used by the
    dumper when ``tab`` is None.

    *tab* is the alternative way to express indent: a tabstop offset
    relative to the slot's natural indent.  When *tab* is not None, the
    dumper computes the absolute indent at emit time as
    ``natural_for_slot + tab * dumps.indent``; the ``indent`` field is
    ignored.  The loader leaves *tab* as None; :func:`annotate` and
    user-built Comments may set it.

    *before* / *after* are the number of blank lines emitted before and
    after this comment.  The loader does not set these; they exist for
    user-built comments only.

    *text* may also be ``None``: a Comment with ``text=None`` emits no
    ``#`` line at all; only its ``before`` / ``after`` blank lines are
    rendered.  This is a convenient way to inject pure blank-line
    separators inside a comment list (for example, between two
    Comments returned by a provider).
    """

    def __init__(self, text="", indent=0, *, tab=None, before=0, after=0):
        self.text = text
        self.indent = indent
        self.tab = tab
        self.before = before
        self.after = after

    def __repr__(self):
        extras = []
        if self.tab is not None:
            extras.append(f", tab={self.tab}")
        else:
            extras.append(f", indent={self.indent}")
        if self.before:
            extras.append(f", before={self.before}")
        if self.after:
            extras.append(f", after={self.after}")
        return f"Comment({self.text!r}{''.join(extras)})"

    def __eq__(self, other):
        if not isinstance(other, Comment):
            return NotImplemented
        return (
            self.text == other.text
            and self.indent == other.indent
            and self.tab == other.tab
            and self.before == other.before
            and self.after == other.after
        )

    # Comments are mutable, so they must not be hashable.
    __hash__ = None


# _group_comments {{{2
def _group_comments(comment_lines):
    """Convert a list of blank/comment Line objects into a list of Comments.

    Rules:
    - Adjacent comment lines at the same indent (no blank line between)
      merge into one Comment whose text is the source lines joined by '\\n'.
    - A blank line, or an indent change, closes the current Comment and
      starts a new one.
    - Pure blank lines are otherwise discarded; their spacing is the
      dumper's concern.

    Same-indent comment blocks separated by blanks therefore remain as
    distinct Comment objects.
    """
    comments = []
    cur_text_parts = []
    cur_indent = 0

    def flush():
        nonlocal cur_text_parts, cur_indent
        if cur_text_parts:
            comments.append(
                Comment(text="\n".join(cur_text_parts), indent=cur_indent)
            )
            cur_text_parts = []
            cur_indent = 0

    saw_blank = False
    for line in comment_lines:
        if line.kind == "blank":
            saw_blank = True
            continue
        indent = line.depth
        if cur_text_parts and not saw_blank and indent == cur_indent:
            cur_text_parts.append(line.value)
        else:
            flush()
            cur_text_parts.append(line.value)
            cur_indent = indent
        saw_blank = False
    flush()
    return comments


# _partition_header_leading {{{2
def _partition_header_leading(buffer_lines):
    """Split a pre-data-line buffer into (header_lines, leading_lines).

    The partition is at the LAST blank line in the buffer.  Everything before
    that blank becomes the header; everything after becomes the leading
    comment block on the first data item.  If no blank line is present, the
    entire buffer is leading.
    """
    last_blank = -1
    for i, line in enumerate(buffer_lines):
        if line.kind == "blank":
            last_blank = i
    if last_blank == -1:
        return [], list(buffer_lines)
    return list(buffer_lines[:last_blank]), list(buffer_lines[last_blank + 1:])


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
        # Set by _add_keymap to the last data line consumed within this value's
        # scope (the source of value-trailing comments).  For leaf entries
        # this is ``line``; for nested values, the deepest descendant line.
        self.value_end_line = None
        # Comments are stored on the Location itself (not on the underlying
        # Line) so that two Locations that share a Line (parent and its
        # first child) do not inadvertently share comment lists.
        self.key_leading_comments = []
        self.key_trailing_comments = []
        self.value_leading_comments = []
        self.value_trailing_comments = []
        # Document-level comments only live on the keymap[()] Location.
        self.header_comments = []
        self.footer_comments = []
        # Per-Location dump spacing: when non-empty, replaces the dumps()
        # *spacing* argument for this Location's entire subtree.  Integer
        # keys are relative to this Location (0 == blanks between this
        # Location's direct children).  See get_spacing / set_spacing.
        self.spacing = {}
        # Per-slot comment providers.  Each (if not None) is a callable
        # with the signature ``provider(child_key) -> list[Comment]``,
        # invoked by the dumper for every child of this Location.  The
        # returned Comments are prepended to the child's own static
        # comments at the matching slot.  Closures over the callable's
        # state can be used to dedup or build comments dynamically.
        self.key_leading_provider = None
        self.key_trailing_provider = None
        self.value_leading_provider = None
        self.value_trailing_provider = None

    def __repr__(self):
        components = []
        if self.line:
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
    def as_tuple(self, kind="value"):
        """
        Returns the location of either the value or the key token as a tuple
        that contains the line number and the column number.  The line and
        column numbers are 0 based.

        Args:
            kind:
                Specify either “key” or “value” depending on which token is
                desired.
        """
        if kind == "key":
            line = self.key_line
            col = self.key_col
            if line is None:
                line = self.line
            if col is None:
                col = self.col
        else:
            assert kind == "value"
            line = self.line
            col = self.col
        return line.lineno, col

    # as_line() {{{3
    def as_line(self, kind="value", offset=0):
        """
        Returns a string containing two lines that identify the token in
        context.  The first line contains the line number and text of the line
        that contains the token.  The second line contains a pointer to the
        token.

        Args:
            kind:
                Specify either “key” or “value” depending on which token is
                desired.
            offset:
                If *offset* is None, the error pointer is not added to the line.
                If *offset* is an integer, the pointer is moved to the right by
                this many characters.  The default is 0.
                If *offset* is a tuple, it must have two values.  The first is
                the row offset and the second is the column offset.  This is
                useful for annotating errors in multiline strings.

        Raises:
            *IndexError* if row offset is out of range.
        """
        # get the line and the column number of the key or value
        if kind == "key":
            line = self.key_line
            col = self.key_col
            if line is None:
                line = self.line
            if col is None:
                col = self.col
        else:
            assert kind == "value"
            line = self.line
            col = self.col

        if not line:  # this occurs if input is completely empty
            return ""

        # process the offset
        if offset is None:
            return line.render()
        col_offset = offset
        try:
            row_offset, col_offset = offset
            while row_offset > 0:
                line = line.next_line
                row_offset -= 1
                if line is None:
                    raise IndexError(offset[0])
        except TypeError:
            pass

        return line.render(col + col_offset)

    # get_line_numbers() {{{3
    def get_line_numbers(self, kind="value", sep=None):
        """
        Returns the line numbers of a token either as a pair of integers or as a
        string.

        Args:
            kind:
                Specify either “key” or “value” depending on which token is
                desired.
            sep:
                The separator string.

                If given a string is returned and *sep* is inserted between two
                line numbers.  In this case the line numbers start at 1.

                If *sep* is not given, a tuple of integers is returned.  In this
                case the line numbers start at 0, but the second number returned
                is the last line number plus 1.  This form is suitable to use
                with the Python slice function to extract the lines from the
                *NestedText* source.
        """
        if kind == "key":
            line = self.key_line
            if line is None:
                line = self.line
        else:
            assert kind == "value"
            line = self.line

        # find line numbers
        first_lineno = line.lineno
        while line:
            last_lineno = line.lineno
            line = line.next_line

        if sep is None:
            return (first_lineno, last_lineno + 1)
        if first_lineno != last_lineno:
            return join(first_lineno+1, last_lineno+1, sep=sep)
        return str(first_lineno+1)

    # _get_original_key() {{{3
    def _get_original_key(self, key, strict):
        try:
            line = self.key_line
            if line.kind == "key item":
                # is multiline key (key fragment is actually held in line.text)
                key_frags = [line.text[line.depth+2:]]
                while line.next_line:
                    line = line.next_line
                    key_frags.append(line.text[line.depth+2:])
                key = "\n".join(key_frags)
            else:
                if line.kind != "list item":
                    key = line.key
            return key
        except AttributeError:
            # this occurs for list indexes
            return key

    # comment accessors {{{3
    # get_key_leading_comments() {{{4
    def get_key_leading_comments(self):
        """Return the leading Comments associated with this key."""
        return self.key_leading_comments

    # set_key_leading_comments {{{4
    def set_key_leading_comments(self, comments):
        """Replace the leading Comments for this key."""
        self.key_leading_comments = list(comments)

    # add_key_leading_comment {{{4
    def add_key_leading_comment(self, comment):
        """Append a Comment to the leading list for this key."""
        self.key_leading_comments.append(comment)

    # get_key_trailing_comments {{{4
    def get_key_trailing_comments(self):
        """Return Comments between the key line and the value line (multiline case)."""
        return self.key_trailing_comments

    # set_key_trailing_comments {{{4
    def set_key_trailing_comments(self, comments):
        self.key_trailing_comments = list(comments)

    # add_key_trailing_comment {{{4
    def add_key_trailing_comment(self, comment):
        self.key_trailing_comments.append(comment)

    # get_value_leading_comments {{{4
    def get_value_leading_comments(self):
        """Return Comments leading the value (multiline case)."""
        return self.value_leading_comments

    # set_value_leading_comments {{{4
    def set_value_leading_comments(self, comments):
        self.value_leading_comments = list(comments)

    # add_value_leading_comment {{{4
    def add_value_leading_comment(self, comment):
        self.value_leading_comments.append(comment)

    # get_value_trailing_comments {{{4
    def get_value_trailing_comments(self):
        """Return Comments trailing the value (after its last line)."""
        return self.value_trailing_comments

    # set_value_trailing_comments {{{4
    def set_value_trailing_comments(self, comments):
        self.value_trailing_comments = list(comments)

    # add_value_trailing_comment {{{4
    def add_value_trailing_comment(self, comment):
        self.value_trailing_comments.append(comment)

    # get_header_comments {{{4
    def get_header_comments(self):
        """Return the document's header Comments.

        Header comments only ever live on the document-root Location, i.e.,
        ``keymap[()]``.  On any other Location this list is empty.
        """
        return self.header_comments

    # set_header_comments {{{4
    def set_header_comments(self, comments):
        """Replace the document's header Comments."""
        self.header_comments = list(comments)

    # add_header_comment {{{4
    def add_header_comment(self, comment):
        """Append a Comment to the document's header."""
        self.header_comments.append(comment)

    # get_footer_comments {{{4
    def get_footer_comments(self):
        """Return the document's footer Comments.

        Footer comments only ever live on the document-root Location, i.e.,
        ``keymap[()]``.  On any other Location this list is empty.
        """
        return self.footer_comments

    # set_footer_comments {{{4
    def set_footer_comments(self, comments):
        """Replace the document's footer Comments."""
        self.footer_comments = list(comments)

    # add_footer_comment {{{4
    def add_footer_comment(self, comment):
        """Append a Comment to the document's footer."""
        self.footer_comments.append(comment)

    # get_spacing {{{4
    def get_spacing(self):
        """Return the per-Location spacing dict (empty if none was set).

        When non-empty, this dict replaces the :func:`dumps` *spacing*
        argument for this Location's entire subtree.  Integer keys count
        relative depth below this Location: ``0`` is the number of blank
        lines between this Location's direct children, ``1`` between its
        grandchildren, and so on.  Absent depth keys default to ``0`` --
        the global spacing is *not* consulted as a fallback.

        The ``"edges"`` key is only consulted on the document-root
        Location (``keymap[()]``); it is ignored elsewhere.
        """
        return self.spacing

    # set_spacing {{{4
    def set_spacing(self, spacing):
        """Replace the per-Location spacing dict."""
        self.spacing = dict(spacing)

    # get_key_leading_provider {{{4
    def get_key_leading_provider(self):
        """Return the per-child ``key_leading`` provider callable, if any.

        A provider has the signature ::

            provider(child_key) -> list[Comment]

        where *child_key* is the dict key (or list index) of one of this
        Location's children.  When this Location's value is rendered the
        dumper invokes the provider for every child, and prepends the
        returned Comments to that child's static
        :meth:`get_key_leading_comments` list.  Closures over the
        callable's state can dedup or build Comments dynamically.

        Returned Comments whose ``tab`` is ``None`` are normalized to
        ``tab=0`` at emit time (natural indent).  Providers are
        callables and are *not* JSON-serializable; they are dropped on
        :func:`keymap_to_jsonable` round-trips.
        """
        return self.key_leading_provider

    # set_key_leading_provider {{{4
    def set_key_leading_provider(self, provider):
        """Replace the per-child ``key_leading`` provider callable.

        Pass ``None`` to clear it.  See :meth:`get_key_leading_provider`
        for the expected callable signature.
        """
        self.key_leading_provider = provider

    # get_key_trailing_provider {{{4
    def get_key_trailing_provider(self):
        """Return the per-child ``key_trailing`` provider; see
        :meth:`get_key_leading_provider` for semantics."""
        return self.key_trailing_provider

    # set_key_trailing_provider {{{4
    def set_key_trailing_provider(self, provider):
        """Replace the per-child ``key_trailing`` provider callable."""
        self.key_trailing_provider = provider

    # get_value_leading_provider {{{4
    def get_value_leading_provider(self):
        """Return the per-child ``value_leading`` provider; see
        :meth:`get_key_leading_provider` for semantics."""
        return self.value_leading_provider

    # set_value_leading_provider {{{4
    def set_value_leading_provider(self, provider):
        """Replace the per-child ``value_leading`` provider callable."""
        self.value_leading_provider = provider

    # get_value_trailing_provider {{{4
    def get_value_trailing_provider(self):
        """Return the per-child ``value_trailing`` provider; see
        :meth:`get_key_leading_provider` for semantics."""
        return self.value_trailing_provider

    # set_value_trailing_provider {{{4
    def set_value_trailing_provider(self, provider):
        """Replace the per-child ``value_trailing`` provider callable."""
        self.value_trailing_provider = provider


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
            self.inline_error("line ended without closing delimiter", self.max_index)
        if index < self.max_index:
            extra = self.text[index:]
            self.inline_error(
                f"extra {plural(extra):character} after closing delimiter: ‘{{}}’.",
                index, extra
            )
        assert index == self.max_index

    # parse_inline_value() {{{3
    def parse_inline_value(self, keys, index, forbidden_chars=None):
        if self.text[index] == "{":
            return self.parse_inline_dict(keys, index)
        elif self.text[index] == "[":
            return self.parse_inline_list(keys, index)
        else:
            return self.parse_inline_str(keys, index, forbidden_chars)

    # parse_inline_dict() {{{3
    def parse_inline_dict(self, keys, index):
        starting_index = index
        assert self.text[index] == "{"
        index += 1
        values = {}
        need_another = False

        while self.text[index] != "}":
            prev_index = index
            orig_key, value, location, index = self.parse_inline_dict_item(keys, index)
            key = self.loader.normalize_key(orig_key, keys)
            if key in values:
                key = KeyPolicy.process_duplicate(values, key, keys, self.line, prev_index)
            if key is not None:
                values[key] = value
                self.loader._add_keymap(keys + (key,), location)
            need_another = False
            if self.text[index] not in ",}":
                self.inline_error(
                    "expected ‘,’ or ‘}}’, found ‘{}’", index, self.text[index]
                )
            if self.text[index] == ",":
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
        forbidden_chars = "{}[],:"
        key_index = self.adjust_index(index)
        if self.text[index] in forbidden_chars:
            key = ""
        else:
            key, _, index = self.parse_inline_value(keys, index, forbidden_chars)
        if self.text[index] != ":":
            self.inline_error(
                "expected ‘:’, found ‘{}’", index, self.text[index], culprit=key
            )
        index = self.adjust_index(index+1)
        if self.text[index] in ",}":
            value = ""
            loc = self.location(index)
        else:
            value, loc, index = self.parse_inline_value(keys, index, forbidden_chars)
        self.add_key_location(loc, key_index)
        return key, value, loc, index

    # parse_inline_list() {{{3
    def parse_inline_list(self, keys, index):
        forbidden_chars = "{}[],"
        starting_index = index
        assert self.text[index] == "["
        index += 1

        # handle empty list
        if self.text[index] == "]":
            return [], self.location(starting_index), self.adjust_index(index+1)

        key = 0
        values = []
        value = ""
        loc = self.location(index)
        while True:
            new_keys = keys + (key,)
            c = self.text[index]
            if c in ",]":
                values.append(value)
                self.loader._add_keymap(new_keys, loc)
                key += 1
                if c == "]":
                    return (
                        values,
                        self.location(starting_index),
                        self.adjust_index(index+1)
                    )
                index += 1
                loc = self.location(index)
                index = self.adjust_index(index)
                value = ""
            elif value:
                self.inline_error(
                    "expected ‘,’ or ‘]’, found ‘{}’", index, self.text[index]
                )
            elif c in "}],":
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
        # if desired index points to white space, shift right until it doesn’t
        while index < self.max_index and self.text[index] in " \t":
            index += 1
        return index

    # location() {{{3
    def location(self, index, **kwargs):
        kwargs["line"] = self.line
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
        return f"❬{self.text}❭\n {index*' '}▲"

    # __repr__ {{{3
    def __repr__(self):  # pragma: no cover
        name = self.__class__.__name__
        return f"{name}({self.text!r})"


# NestedTextLoader class {{{2
class NestedTextLoader:
    # __init__() {{{3
    def __init__(self, lines, top, source, on_dup, keymap, normalize_key, dialect):
        KeyPolicy.set_policy(on_dup)
        self.source = source
        self.keymap = keymap
        assert self.keymap is None or is_mapping(self.keymap)
        self.normalize_key = normalize_key if normalize_key else lambda k, ks: k
        if dialect and "i" in dialect:
            support_inlines = False
        else:
            support_inlines = True

        with set_culprit(source):
            lines = self.lines = Lines(lines, support_inlines)
            if keymap is not None:
                # add a location for the top-level of the data set
                if lines.first_value_line:
                    keymap[()] = Location(line=lines.first_value_line, col=0)
                else:
                    keymap[()] = Location(line=lines.last_comment_line, col=0)
            next_is = lines.type_of_next()

            if top in ["any", any]:
                if next_is is None:
                    self.values, self.keymap = None, None
                else:
                    self.values, self.keymap = self._read_value(0, ())

            elif top in ["dict", dict]:
                if next_is in ["dict item", "key item", "inline dict"]:
                    self.values, self.keymap = self._read_value(0, ())
                elif next_is is None:
                    self.values, self.keymap = {}, None
                else:
                    report(
                        "content must start with key or brace ({{).",
                        lines.get_next()
                    )

            elif top in ["list", list]:
                if next_is in ["list item", "inline list"]:
                    self.values, self.keymap = self._read_value(0, ())
                elif next_is is None:
                    self.values, self.keymap = [], None
                else:
                    report(
                        "content must start with dash (-) or bracket ([).",
                        lines.get_next(),
                    )

            elif top in ["str", str]:
                if next_is == "string item":
                    self.values, self.keymap = self._read_value(0, ())
                elif next_is is None:
                    self.values, self.keymap = "", None
                else:
                    report(
                        "content must start with greater-than sign (>).",
                        lines.get_next(),
                    )

            else:
                raise NotImplementedError(top)  # pragma: no cover

            if lines.type_of_next():
                report('extra content', lines.get_next())

            # attach header / footer comments to the document-root Location
            # (keymap[()]) so that every keymap key remains a tuple, keeping
            # depth-based iteration (``len(keys)``) safe.
            if keymap is not None and () in keymap:
                root = keymap[()]
                if lines.header_comments:
                    root.header_comments = list(lines.header_comments)
                if lines.eof_comments:
                    root.footer_comments = list(lines.eof_comments)

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
    #         raise NestedTextError(
    #             key, template=f"key not found ({}).", culprit=keys_used
    #         )
    #     return value

    # _add_keymap() {{{3
    def _add_keymap(self, keys, location):
        if self.keymap is not None:
            # The last data line consumed is the last line of this value's
            # scope, where trailing-after-value comments are staged.
            location.value_end_line = self.lines.prev_data_line
            # Claim any comments staged on the relevant Lines.  This makes
            # each Location own its comments outright -- two Locations that
            # share a Line (parent and its first child) cannot then
            # double-emit the same comment block.
            key_first = (
                location.key_line if location.key_line is not None
                else location.line
            )
            vl = location.line
            ve = location.value_end_line
            # For a multi-line key, walk the chain of fragment lines via
            # next_line (set by Lines.read_lines only between consecutive
            # ``key item`` lines at the same depth) so that comments
            # staged on later fragments are claimed too.
            key_last = key_first
            if key_first is not None:
                while (
                    getattr(key_last, "next_line", None) is not None
                    and key_last.next_line.kind == "key item"
                    and key_last.next_line.depth == key_last.depth
                ):
                    key_last = key_last.next_line
            if key_first is not None and key_first.leading_comments:
                location.key_leading_comments = list(key_first.leading_comments)
                key_first.leading_comments = []
            if (
                vl is not None
                and vl is not key_first
                and vl is not key_last
                and vl.leading_comments
            ):
                location.value_leading_comments = list(vl.leading_comments)
                vl.leading_comments = []
            # key_trailing collects (a) leading_comments staged on each
            # *intermediate* key-fragment line -- these are comments that
            # appeared between fragments of the multi-line key, the
            # multi-line-key analogue of inline-in-multi-line-string -- and
            # (b) the trailing_comments on each fragment, including the
            # last.  All are emitted at the key-trailing position.  When
            # the entire key+value is on one line (key_first == ve), the
            # trailing comments belong to value_trailing instead.
            kt = []
            # Inline-in-multi-line-key comments need to be indented past
            # the value's column so that a subsequent re-load classifies
            # them as key_trailing (rather than as value_leading on the
            # value or as a leading comment on the next sibling).  We
            # bump to value-depth + 4 -- one tabstop deeper than the
            # value's natural column at the default indent step.
            safe_inline_indent = (vl.depth + 4) if vl is not None else None
            cur = key_first
            while cur is not None:
                if cur is not key_first and cur.leading_comments:
                    if safe_inline_indent is not None:
                        for c in cur.leading_comments:
                            if c.indent <= vl.depth:
                                c.indent = safe_inline_indent
                    kt.extend(cur.leading_comments)
                    cur.leading_comments = []
                if cur is not ve and cur.trailing_comments:
                    kt.extend(cur.trailing_comments)
                    cur.trailing_comments = []
                if cur is key_last:
                    break
                cur = cur.next_line
            if kt:
                location.key_trailing_comments = kt
            if ve is not None and ve.trailing_comments:
                location.value_trailing_comments = list(ve.trailing_comments)
                ve.trailing_comments = []
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
                    value = ""
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

        # process all items in dictionary
        while lines.still_within_level(depth):
            line = lines.get_next()
            key_line = line
            key_col = depth

            # error checking
            if line.depth != depth:
                lines.indentation_error(line, depth)
            if line.kind not in ["dict item", "key item"]:
                report("expected dictionary item.", line, colno=depth)

            # process key
            if line.kind == "key item":
                # multiline key
                original_key = self._read_key(line, depth)
                value = None
            else:
                # key and value on a single line
                original_key = line.key
                value = line.value
            key = self.normalize_key(original_key, keys)
            if key in values:
                # found duplicate key
                key = KeyPolicy.process_duplicate(values, key, keys, line, depth)
                if key is None:
                    continue
            new_keys = keys + (key,)

            # process value
            if value:
                # this is a single-line item, value was found above
                loc = Location(line=line, col=depth + len(key) + 2)
            else:
                # value is on subsequent lines
                depth_of_next = lines.depth_of_next()
                if depth_of_next > depth:
                    # read indented values
                    value, loc = self._read_value(depth_of_next, new_keys)
                elif line.kind == "dict item":
                    # found the next key in this dictionary, so value is empty
                    value = ""
                    loc = Location(line=line, col=depth + len(key) + 1)
                else:
                    report("multiline key requires a value.", line, None, colno=depth)

            values[key] = value
            loc.key_line = key_line
            loc.key_col = key_col
            self._add_keymap(new_keys, loc)
        return values, Location(line=first_line, col=first_line.depth)

    # _read_key() {{{3
    def _read_key(self, line, depth):
        lines = self.lines
        data = [line.value]
        while lines.still_within_key(line, depth):
            line = lines.get_next()
            data.append(line.value)
        return "\n".join(data)

    # _read_string() {{{3
    def _read_string(self, depth, keys):
        lines = self.lines
        data = []
        first_line = lines.next_line
        loc = Location(line=first_line, key_col=depth)
        last_line = first_line
        while lines.still_within_string(depth):
            line = lines.get_next()
            last_line = line
            data.append(line.value)
            if line.depth != depth:
                lines.indentation_error(line, depth)
        # Per the rules, inline comments (those that appear on continuation
        # lines of a multi-line string) are converted to trailing on the
        # value immediately on load.  After the loop, gather any leading
        # comments from continuation lines and move them onto the last
        # line's trailing slot, which is where the value's trailing
        # comments live (see Location.value_end_line).
        cur = first_line.next_line
        # Inline-in-multi-line-string comments need to be indented past
        # the value's column so that a subsequent re-load classifies
        # them as value_trailing (rather than as a leading comment on
        # the next sibling, or as a footer when at EOF).  Bump shallow
        # ones to value-depth + 4 -- one tabstop deeper than the value
        # at the default indent step.
        safe_inline_indent = depth + 4
        while cur is not None:
            inline = cur.leading_comments
            if inline:
                for c in inline:
                    if c.indent <= depth:
                        c.indent = safe_inline_indent
                last_line.trailing_comments = last_line.trailing_comments or []
                if cur is last_line:
                    # avoid clobbering when cur and last_line are the same
                    last_line.trailing_comments = list(inline) + last_line.trailing_comments
                else:
                    last_line.trailing_comments.extend(inline)
                cur.leading_comments = []
            cur = cur.next_line
        value = "\n".join(data)
        loc.col = depth + (2 if value else 1)
        return value, loc

    # _read_inline() {{{3
    def _read_inline(self, keys):
        lines = self.lines
        line = lines.get_next()
        return Inline(line, keys, self).get_values()


# loads {{{2
def loads(
    content,
    top = "dict",
    *,
    source = None,
    on_dup = None,
    keymap = None,
    normalize_key = None,
    dialect = None
):
    # description {{{3
    r'''
    Loads *NestedText* from string.

    Args:
        content (str):
            String that contains encoded data.

        top (str):
            Top-level data type. The NestedText format allows for a dictionary,
            a list, or a string as the top-level data container.  By specifying
            top as “dict”, “list”, or “str” you constrain both the type of
            top-level container and the return value of this function. By
            specifying “any” you enable support for all three data types, with
            the type of the returned value matching that of top-level container
            in content. As a short-hand, you may specify the *dict*, *list*,
            *str*, and *any* built-ins rather than specifying *top* with a
            string.

        source (str or Path):
            If given, this string is attached to any error messages as the
            culprit. It is otherwise unused. Is often the name of the file that
            originally contained the NestedText content.

        on_dup (str or func):
            Indicates how duplicate keys in dictionaries should be handled.
            Specifying "error" causes them to raise exceptions (the default
            behavior). Specifying "ignore" causes them to be ignored (first
            wins). Specifying "replace" results in them replacing earlier items
            (last wins). By specifying a function, the keys can be
            de-duplicated.  This call-back function returns a new key and takes
            two arguments:

            key:
                The new key (duplicates an existing key).

            state:
                A dictionary containing other possibly helpful information:

                dictionary:
                    The entire dictionary as it is at the moment the duplicate
                    key is found.  You should not change it.
                keys:
                    The keys that identify the dictionary.

                This dictionary is created as *loads* is called and deleted as
                it returns. Any values placed in it are retained and available
                on subsequent calls to this function during the load operation.

            This function should return a new key.  If the key duplicates an
            existing key, the value associated with that key is replaced.  If
            *None* is returned, this key is ignored.  If a *KeyError* is
            raised, the duplicate key is reported as an error.

            Be aware that key de-duplication occurs after key normalization.  As
            such you should generate keys during de-duplication that are
            consistent with your normalization scheme.

        keymap (dict):
            Specify an empty dictionary or nothing at all for the value of
            this argument.  If you give an empty dictionary it will be filled
            with location information for the values that are returned.  Upon
            return the dictionary maps a tuple containing the keys for the value
            of interest to the location of that value in the *NestedText* source
            document. The location is contained in a :class:`Location` object.
            You can access the line and column number using the
            :meth:`Location.as_tuple` method, and the line that contains the
            value annotated with its location using the :meth:`Location.as_line`
            method.

        normalize_key (func):
            A function that takes two arguments; the original key for a value
            and the tuple of normalized keys for its parent values.  It then
            transforms the given key into the desired normalized form.  Only
            called on dictionary keys, so the key will always be a string.

        dialect (str):
            Specifies support for particular variations in *NestedText*.

            In general you are discouraged from using a dialect as it can result
            in *NestedText* documents that are not compliant with the standard.

            The following deviant dialects are supported.

            *support inlines*:
                If "i" is included in *dialect*, support for inline lists and
                dictionaries is dropped.  The default is "I", which enables
                support for inlines.  The main effect of disabling inlines in
                the load functions is that keys may begin with ``[`` or ``{``.

    Returns:
        The extracted data.  The type of the return value is specified by the
        top argument.  If top is “any”, then the return value will match that of
        top-level data container in the input content. If content is empty, an
        empty data value of the type specified by top is returned. If top is
        “any” None is returned.

    Raises:
        NestedTextError: if there is a problem in the *NextedText* document.

    Examples:

        A *NestedText* document is specified to *loads* in the form of a string:

        .. code-block:: python

            >>> import nestedtext as nt

            >>> contents = """
            ... name: Kristel Templeton
            ... gender: female
            ... age: 74
            ... """

            >>> try:
            ...     data = nt.loads(contents, "dict")
            ... except nt.NestedTextError as e:
            ...     e.terminate()

            >>> print(data)
            {'name': 'Kristel Templeton', 'gender': 'female', 'age': '74'}

        *loads()* takes an optional argument, *source*. If specified, it is
        added to any error messages. It is often used to designate the source
        of *NestedText* document. For example, if *contents* were read from a
        file, *source* would be the file name.  Here is a typical example of
        reading *NestedText* from a file:

        .. code-block:: python

            >>> filename = "examples/duplicate-keys.nt"
            >>> try:
            ...     with open(filename, encoding="utf-8") as f:
            ...         addresses = nt.loads(f.read(), source=filename)
            ... except nt.NestedTextError as e:
            ...     print(e.render())
            examples/duplicate-keys.nt, 5: duplicate key: name.
                   4 ❬name:❭
                   5 ❬name:❭
                      ▲

        Notice in the above example the encoding is explicitly specified as
        "utf-8".  *NestedText* files should always be read and written using
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
            nestedtext.nestedtext.NestedTextError: 3: duplicate key: key.
                   2 ❬key: value 1❭
                   3 ❬key: value 2❭
                      ▲

            >>> print(nt.loads(content, on_dup="ignore"))
            {'key': 'value 1', 'name': 'value 4'}

            >>> print(nt.loads(content, on_dup="replace"))
            {'key': 'value 3', 'name': 'value 5'}

            >>> def de_dup(key, state):
            ...     if key not in state:
            ...         state[key] = 1
            ...     state[key] += 1
            ...     return f"{key} — #{state[key]}"

            >>> print(nt.loads(content, on_dup=de_dup))
            {'key': 'value 1', 'key — #2': 'value 2', 'key — #3': 'value 3', 'name': 'value 4', 'name — #2': 'value 5'}

    '''

    # code {{{3
    if isinstance(content, bytes):
        content = content.decode('utf-8-sig', errors='strict')
    f = io.StringIO(content, newline=None)
    loader = NestedTextLoader(
        f, top, source, on_dup, keymap, normalize_key, dialect
    )
    return loader.get_decoded()


# load {{{2
def load(
    f,
    top = "dict",
    *,
    source = None,
    on_dup = None,
    keymap = None,
    normalize_key = None,
    dialect = None
):
    # description {{{3
    r"""
    Loads *NestedText* from file or stream.

    Is the same as :func:`loads` except the *NextedText* is accessed by reading
    a file rather than directly from a string. It does not keep the full
    contents of the file in memory and so is more memory efficient with large
    files.

    Args:
        f (str, os.PathLike, io.TextIOBase, collections.abc.Iterator):
            The file to read the *NestedText* content from.  This can be
            specified either as a path (e.g. a string or a `pathlib.Path`),
            as a text IO object (e.g. an open file, or 0 for stdin), or as an
            iterator.  If a path is given, the file will be opened, read, and
            closed.  If an IO object is given, it will be read and not closed;
            utf-8 encoding should be used..  If an iterator is given, it should
            generate full lines in the same manner that iterating on a file
            descriptor would.
        kwargs:
            See :func:`loads` for optional arguments.

    Returns:
        The extracted data.
        See :func:`loads` description of the return value.

    Raises:
        NestedTextError: if there is a problem in the *NextedText* document.
        OSError: if there is a problem opening the file.

    Examples:

        Load from a path specified as a string:

        .. code-block:: python

            >>> import nestedtext as nt
            >>> print(open("examples/groceries.nt").read())
            groceries:
              - Bread
              - Peanut butter
              - Jam
            <BLANKLINE>

            >>> nt.load("examples/groceries.nt")
            {'groceries': ['Bread', 'Peanut butter', 'Jam']}

        Load from a `pathlib.Path`:

        .. code-block:: python

            >>> from pathlib import Path
            >>> nt.load(Path("examples/groceries.nt"))
            {'groceries': ['Bread', 'Peanut butter', 'Jam']}

        Load from an open file object:

        .. code-block:: python

            >>> with open("examples/groceries.nt") as f:
            ...     nt.load(f)
            ...
            {'groceries': ['Bread', 'Peanut butter', 'Jam']}

    """

    # code {{{3
    # Do not invoke the read method as that would read in the entire contents of
    # the file, possibly consuming a lot of memory. Instead pass the file
    # pointer into loader, it will iterate through the lines, discarding
    # them once they are no longer needed, which reduces the memory usage.

    if isinstance(f, collections.abc.Iterator):
        if not source:
            source = getattr(f, "name", None)
        loader = NestedTextLoader(
            f, top, source, on_dup, keymap, normalize_key, dialect
        )
        return loader.get_decoded()
    else:
        if not source:
            if f == 0:
                source = '<stdin>'
            else:
                source = str(f)
        with open(f, encoding="utf-8-sig") as fp:
            loader = NestedTextLoader(
                fp, top, source, on_dup, keymap, normalize_key, dialect
            )
            return loader.get_decoded()


# NestedText Writer {{{1
# Converts Python data hierarchies to NestedText.

# add_leader {{{2
def add_leader(s, leader):
    # split into separate lines
    # add leader to each non-blank line
    # add right-stripped leader to each blank line
    #
    # When the leader is pure indentation (only spaces), comment lines (those
    # whose first non-space character is '#') are passed through unchanged --
    # they already carry their own absolute indentation from
    # _comments_to_lines, and re-indenting them at deeper levels would put
    # them out of position.  When the leader contains content like "> "
    # (multi-line string syntax) the leader is always applied -- the input
    # is user data being converted into string items, not pre-rendered
    # comments.
    indent_only = (leader.lstrip(" ") == "")
    rejoined = []
    for line in s.split("\n"):
        if indent_only and line and line.lstrip(" ")[:1] == "#":
            rejoined.append(line)
        elif line:
            rejoined.append(leader + line)
        else:
            rejoined.append(leader.rstrip())
    return "\n".join(rejoined)


# add_prefix {{{2
def add_prefix(prefix, suffix):
    # A simple formatting of dict and list items will result in a space
    # after the colon or dash if the value is placed on next line.
    # This, function simply eliminates that space.
    if not suffix or suffix.startswith("\n"):
        return prefix + suffix
    return prefix + " " + suffix


# grow {{{2
# add object to end of a tuple
def grow(base, ext):
    return base + (ext,)


# NestedTextDumper class {{{2
class NestedTextDumper:
    # constructor {{{3
    def __init__(
        self,
        indent,
        sort_keys,
        converters,
        default,
        spacing,
        map_keys,
        width,
        inline_level,
        inline_count,
        dialect,
    ):
        assert indent > 0
        self.indent = indent
        self.converters = converters
        self.map_keys = map_keys
        self.default = default
        self.spacing = spacing or {}
        self.width = width
        self.inline_level = inline_level
        self.inline_count = inline_count
        self.support_inlines = True
        if dialect and "i" in dialect:
            self.support_inlines = False

        # define key sorting function {{{4
        if sort_keys:
            if callable(sort_keys):
                def sort(items, keys):
                    return sorted(items, key=lambda k: sort_keys(k, keys))
            else:
                def sort(items, keys):
                    return sorted(items)
        else:
            def sort(items, keys):
                return items
        self.sort = sort

        # define object type identification functions {{{4
        if default == "strict":
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
                raise NotImplementedError(default)  # pragma: no cover

    # render_key {{{3
    def render_key(self, key, keys):
        key = self.convert(key, keys)
        if self.is_a_scalar(key):
            if key is None:
                key = ""
            else:
                key = str(key)
        if not self.is_a_str(key) and callable(self.default):
            key = self.default(key)
        if not self.is_a_str(key):
            raise NestedTextError(
                key, template="keys must be strings.", culprit=keys
            ) from None
        return convert_line_terminators(key)

    # render_dict_item {{{3
    def render_dict_item(self, key, value, keys, values):
        multiline_key_required = (
            not key
            or "\n" in key
            or key.strip() != key
            or key[:1] == "#"
            or (key[:1] in "[{" and self.support_inlines)
            or key[:2] in ["- ", "> ", ": "]
            or ": " in key
        )
        # The key_trailing and value_leading comment slots only have a
        # rendering position in the multi-line dict-item *value* form
        # (between the key line and the value's first line).  If either
        # slot has any contribution -- static or via a parent provider --
        # force the value onto its own line so those comments don't get
        # silently dropped.
        force_multiline_value = (
            not multiline_key_required
            and self._comments_force_multiline(keys)
        )
        if multiline_key_required:
            key = "\n".join(": "+l if l else ":" for l in key.split("\n"))
            if self.is_a_dict(value) or self.is_a_list(value):
                return key + self.render_value(value, keys, values)
            if is_str(value):
                # force use of multiline value with multiline keys
                value = convert_line_terminators(value)
            else:
                value = self.render_value(value, keys, values)
            return key + "\n" + add_leader(value, self.indent*" " + "> ")
        if force_multiline_value:
            # Plain "key:" syntax, but force the value onto its own line
            # so key_trailing / value_leading have a place to render.
            if self.is_a_dict(value) or self.is_a_list(value):
                return key + ":" + self.render_value(value, keys, values)
            if is_str(value):
                value_text = convert_line_terminators(value)
            else:
                value_text = self.render_value(value, keys, values)
            return key + ":\n" + add_leader(value_text, self.indent*" " + "> ")
        return add_prefix(key + ":", self.render_value(value, keys, values))

    # _comments_force_multiline {{{3
    def _comments_force_multiline(self, keys):
        """Return True if any source -- static key_trailing/value_leading
        on this Location, or a parent provider for either slot -- will
        contribute Comments that need the multi-line dict-item form.
        """
        if not is_mapping(self.map_keys):
            return False
        loc = self.map_keys.get(keys)
        if loc is not None:
            if loc.get_key_trailing_comments() or loc.get_value_leading_comments():
                return True
        if keys:
            parent_loc = self.map_keys.get(keys[:-1])
            if parent_loc is not None:
                if (
                    parent_loc.get_key_trailing_provider() is not None
                    or parent_loc.get_value_leading_provider() is not None
                ):
                    return True
        return False

    # render_inline_value {{{3
    def render_inline_value(self, obj, exclude, keys, values):
        obj = self.convert(obj, keys)
        if self.is_a_dict(obj):
            return self.render_inline_dict(obj, keys, values)
        if self.is_a_list(obj):
            return self.render_inline_list(obj, keys, values)
        return self.render_inline_scalar(obj, exclude, keys, values)

    # render_inline_dict {{{3
    def render_inline_dict(self, obj, keys, values):
        exclude = set("\n\r[]{}:,")
        rendered = []
        for k, v in obj.items():
            new_keys = grow(keys, k)
            new_values = grow(values, id(v))
            key = self.render_key(k, new_keys)
            mapped_key = self.map_key(key, new_keys)
            v = obj[k]
            rendered_value = self.render_inline_value(
                v, exclude, new_keys, new_values
            )
            rendered_key = self.render_inline_scalar(
                mapped_key, exclude, new_keys, new_values
            )
            rendered.append((mapped_key, key, f"{rendered_key}: {rendered_value}",))
        items = [v for mk, k, v in self.sort(rendered, keys)]
        return ''.join(["{", ", ".join(items), "}"])

    # render_inline_list {{{3
    def render_inline_list(self, obj, keys, values):
        rendered_values = []
        for i, v in enumerate(obj):
            rendered_value = self.render_inline_value(
                v, set("\n\r[]{},"), grow(keys, i), grow(values, id(v))
            )
            rendered_values.append(rendered_value)
        if len(rendered_values) == 1 and not rendered_values[0]:
            return "[ ]"
        content = ", ".join(rendered_values)
        leading_delimiter = "[ " if content[0:1] == "," else "["
        return leading_delimiter + content + "]"

    # render_inline_scalar {{{3
    def render_inline_scalar(self, obj, exclude, keys, values):
        obj = self.convert(obj, keys)
        if self.is_a_str(obj):
            value = obj
        elif self.is_a_scalar(obj):
            value = "" if obj is None else str(obj)
        elif self.default and callable(self.default):
            try:
                obj = self.default(obj)
            except TypeError:
                raise NestedTextError(
                    obj,
                    template = f"unsupported type ({type(obj).__name__}).",
                    culprit = keys
                ) from None
            return self.render_inline_value(obj, exclude, keys, values)
        else:
            raise NotSuitableForInline from None

        if exclude & set(value):
            raise NotSuitableForInline from None
        if value.strip() != value:
            raise NotSuitableForInline from None
        return value

    # _comments_to_lines {{{3
    def _comments_to_lines(self, comments, natural=0):
        """Render a list of Comment objects to a list of lines (no trailing \\n).

        *natural* is the natural indent (in spaces) for this slot at the
        current depth -- used to resolve any Comment whose ``tab`` field
        is not None to an absolute indent of
        ``natural + tab * self.indent`` (clamped to >= 0).  Comments whose
        ``tab`` is None render at their stored ``indent`` field absolutely.

        Per-comment ``before`` / ``after`` blank-line counts are honored.
        Adjacent same-indent Comments are emitted contiguously; if such a
        list is re-loaded the loader will merge them into a single
        Comment (text joined by ``\\n``).  Text and slot assignment are
        preserved; only the Comment-object granularity may change.
        """
        lines = []
        for c in comments:
            if c.tab is not None:
                abs_indent = max(0, natural + c.tab * self.indent)
            else:
                abs_indent = c.indent
            for _ in range(c.before):
                lines.append("")
            if c.text is not None:
                ind = " " * abs_indent
                for line in c.text.split("\n"):
                    if line:
                        lines.append(f"{ind}# {line}")
                    else:
                        lines.append(f"{ind}#")
            for _ in range(c.after):
                lines.append("")
        return lines

    # _resolve_spacing {{{3
    def _resolve_spacing(self, keys):
        """Determine the blank-line count for joining sibling items whose
        shared parent is at *keys* (absolute depth ``len(keys)``).

        Walks the keymap from the innermost prefix to the root looking for
        a Location with a non-empty ``spacing`` dict.  The first one found
        replaces the global *spacing* argument wholesale for that subtree:
        ``spacing.get(N - len(A), 0)`` where ``A`` is that Location's keys
        and ``N`` is the absolute depth.  Falls back to the global
        ``self.spacing[N]`` only when no Location in the walk has a
        non-empty spacing.
        """
        depth = len(keys)
        if is_mapping(self.map_keys):
            for i in range(depth, -1, -1):
                loc = self.map_keys.get(keys[:i])
                if loc is not None:
                    sp = getattr(loc, "spacing", None)
                    if sp:
                        return sp.get(depth - i, 0)
        return self.spacing.get(depth, 0) if self.spacing else 0

    # _join_items {{{3
    def _join_items(self, items, keys):
        """Join rendered sibling items with the configured *spacing*.

        ``keys`` is the path of the parent whose children are being joined;
        the per-Location keymap spacing (if any) at any prefix of ``keys``
        takes precedence over the global ``self.spacing`` (the dumps()
        *spacing* argument).
        """
        n = self._resolve_spacing(keys)
        return ("\n" + "\n" * n).join(items)

    # _wrap_with_comments {{{3
    def _wrap_with_comments(self, rendered_value, keys):
        """Inject the four comment slots from the keymap around the rendered item.

        - ``key_leading_comments``  emitted before the rendered item.
        - ``key_trailing_comments`` injected between the key line and the
          value's first line (multi-line value form only).
        - ``value_leading_comments`` injected at the same position, after
          ``key_trailing_comments`` (multi-line value form only).
        - ``value_trailing_comments`` emitted after the rendered item.

        For each slot the dumper also consults the *parent* Location
        (``keymap[keys[:-1]]``) for a per-child *provider* callable.  If
        present, the provider is invoked as ``provider(child_key)`` and
        the returned Comments are prepended to the child's static
        comments at that slot.  Comments returned by a provider with
        ``tab=None`` are normalized to ``tab=0``.

        Only applies when ``map_keys`` is a keymap dict (the form
        returned by load).  When ``map_keys`` is a callable (key
        transformer), there are no comments to apply.
        """
        if not is_mapping(self.map_keys):
            return rendered_value
        loc = self.map_keys.get(keys)
        parent_loc = self.map_keys.get(keys[:-1]) if keys else None

        # gather child's static comments (if any) {{{4
        if loc is not None:
            kl = list(loc.get_key_leading_comments())
            kt = list(loc.get_key_trailing_comments())
            vl = list(loc.get_value_leading_comments())
            vt = list(loc.get_value_trailing_comments())
        else:
            kl, kt, vl, vt = [], [], [], []

        # prepend parent's per-child provider output (if any) {{{4
        if parent_loc is not None and keys:
            child_key = keys[-1]
            for getter, target in (
                (parent_loc.get_key_leading_provider,  kl),
                (parent_loc.get_key_trailing_provider, kt),
                (parent_loc.get_value_leading_provider, vl),
                (parent_loc.get_value_trailing_provider, vt),
            ):
                provider = getter()
                if provider is None:
                    continue
                extras = list(provider(child_key) or [])
                for c in extras:
                    if c.tab is None:
                        c.tab = 0
                target[:0] = extras

        if not (kl or kt or vl or vt):
            return rendered_value

        n = len(keys)
        key_natural = max(0, (n - 1) * self.indent)
        val_natural = n * self.indent
        leading = self._comments_to_lines(kl, natural=key_natural)
        key_trailing = self._comments_to_lines(kt, natural=val_natural)
        value_leading = self._comments_to_lines(vl, natural=val_natural)
        trailing = self._comments_to_lines(vt, natural=val_natural)
        value_lines = rendered_value.split("\n")
        # Inject key_trailing and value_leading between the rendered key
        # (which may span several lines for multi-line keys) and the
        # value's first line.  We detect the key's line count by counting
        # consecutive leading lines that look like multi-line key
        # fragments (``: frag`` or ``:`` after lstrip) at the *same*
        # indent.  If no multi-line-key prefix is present, the key is the
        # first line (e.g. ``key:``).  Inline values (single-line output)
        # don't get key_trailing / value_leading -- those are forced into
        # multi-line by ``_comments_force_multiline``, which is what
        # ensures we never silently drop them here.
        if (key_trailing or value_leading) and len(value_lines) > 1:
            boundary = 0
            key_indent = None
            for line in value_lines:
                stripped = line.lstrip()
                if not (stripped == ":" or stripped.startswith(": ")):
                    break
                indent = len(line) - len(stripped)
                if key_indent is None:
                    key_indent = indent
                elif indent != key_indent:
                    break
                boundary += 1
            if boundary == 0:
                boundary = 1
            value_lines = (
                value_lines[:boundary]
                + key_trailing
                + value_leading
                + value_lines[boundary:]
            )
        return "\n".join(leading + value_lines + trailing)

    # render value {{{3
    def render_value(self, obj, keys, values):
        level = len(keys)
        error = None
        content = ""
        obj = self.convert(obj, keys)
        need_indented_block = is_collection(obj)

        if self.is_a_dict(obj):
            self.check_for_cyclic_reference(obj, keys, values)
            try:
                if not self.support_inlines:
                    raise NotSuitableForInline from None
                if obj and (self.width <= 0 or level < self.inline_level):
                    raise NotSuitableForInline from None
                try:
                    if 0 < len(obj) < self.inline_count:
                        raise NotSuitableForInline from None
                    if obj and len(obj) > self.width/5:
                        raise NotSuitableForInline from None
                except TypeError:
                    pass  # does not have len()
                content = self.render_inline_dict(obj, keys, values)
                if obj and (len(content) > self.width):
                    raise NotSuitableForInline from None
            except NotSuitableForInline:
                rendered = []
                for k, v in obj.items():
                    new_keys = grow(keys, k)
                    new_values = grow(values, id(v))
                    key = self.render_key(k, new_keys)
                    mapped_key = self.map_key(key, new_keys)
                    rendered_value = self.render_dict_item(
                        mapped_key, obj[k], new_keys, new_values
                    )
                    rendered_value = self._wrap_with_comments(rendered_value, new_keys)
                    rendered.append((mapped_key, key, rendered_value))
                content = self._join_items(
                    [v for mk, k, v in self.sort(rendered, keys)], keys
                )
        elif self.is_a_list(obj):
            self.check_for_cyclic_reference(obj, keys, values)
            try:
                if not self.support_inlines:
                    raise NotSuitableForInline from None
                if obj and (self.width <= 0 or level < self.inline_level):
                    raise NotSuitableForInline from None
                try:
                    if 0 < len(obj) < self.inline_count:
                        raise NotSuitableForInline from None
                    if obj and (self.width <= 0 or len(obj) > self.width/3):
                        raise NotSuitableForInline from None
                except TypeError:
                    pass  # does not have len()
                content = self.render_inline_list(obj, keys, values)
                if obj and (len(content) > self.width):
                    raise NotSuitableForInline from None
            except NotSuitableForInline:
                content = []
                for i, v in enumerate(obj):
                    new_keys = grow(keys, i)
                    rendered_v = self.render_value(v, new_keys, grow(values, id(v)))
                    item = add_prefix("-", rendered_v)
                    item = self._wrap_with_comments(item, new_keys)
                    content.append(item)
                content = self._join_items(content, keys)

        elif self.is_a_str(obj):
            text = convert_line_terminators(obj)
            if "\n" in text or level == 0:
                content = add_leader(text, "> ")
                need_indented_block = True
            else:
                content = text
        elif self.is_a_scalar(obj):
            if obj is None:
                content = ""
            else:
                content = str(obj)
                if level == 0:
                    content = add_leader(content, "> ")
                    need_indented_block = True
        elif self.default and callable(self.default):
            try:
                obj = self.default(obj)
            except TypeError:
                error = f"unsupported type ({type(obj).__name__})."
            else:
                content = self.render_value(obj, keys, values)
        else:
            error = f"unsupported type ({type(obj).__name__})."

        if need_indented_block and content and level:
            content = "\n" + add_leader(content, self.indent*" ")

        if error:
            raise NestedTextError(obj, template=error, culprit=keys) from None

        return content

    # check_for_cyclic_reference {{{3
    def check_for_cyclic_reference(self, obj, keys, values):
        if id(obj) in values[:-1]:
            raise NestedTextError(
                obj, template="circular reference.", culprit=keys
            )

    # convert {{{3
    # apply externally supplied converter to convert value to string
    def convert(self, obj, keys):
        converters = self.converters
        converter = getattr(obj, "__nestedtext_converter__", None)
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
                template = f"unsupported type ({type(obj).__name__}).",
                culprit = keys,
            ) from None
        return obj

    # map_key {{{3
    # apply externally supplied mapping to convert key to desired form
    def map_key(self, key, keys):
        mapper = self.map_keys
        if not mapper:
            return key
        if callable(mapper):
            new_key = mapper(key, keys[:-1])
            if new_key is None:
                return key
            return new_key
        elif is_mapping(mapper):
            try:
                loc = mapper.get(keys)
                if loc:
                    return loc._get_original_key(key, strict=False)
                else:
                    return key
            except AttributeError:    # pragma: no cover
                raise AssertionError(
                    "if map_keys is a dictionary, it must be a keymap"
                ) from None
        else:  # pragma: no cover
            raise AssertionError(
                "map_keys must be a callable or a dictionary"
            ) from None


# dumps {{{2
def dumps(
    obj,
    *,
    indent = 4,
    sort_keys = False,
    converters = None,
    default = None,
    spacing = None,
    map_keys = None,
    width = 0,
    inline_level = 0,
    inline_count = 1,
    dialect = None,
):
    # description {{{3
    '''Recursively convert object to *NestedText* string.

    Args:
        obj:
            The object to convert to *NestedText*.

        indent (int):
            The number of spaces to use to represent a single level of
            indentation.  Must be one or greater.

        sort_keys (bool or func):
            Dictionary items are sorted by their key if *sort_keys* is *True*.
            In this case, keys at all level are sorted alphabetically.  If
            *sort_keys* is *False*, the natural order of dictionaries is
            retained.

            If a function is passed in, it is expected to return the sort key.
            The function is passed two tuples, each consists only of strings.
            The first contains the mapped key, the original key, and the
            rendered item.  So it takes the form::

                ('<mapped_key>', '<orig_key>', '<mapped_key>: <value>')

            The second contains the keys of the parent.

        converters (dict):
            A dictionary where the keys are types and the values are converter
            functions (functions that take an object and return it in a form
            that can be processed by *NestedText*).  If a value is False, an
            unsupported type error is raised.

            An object may provide its own converter by defining the
            ``__nestedtext_converter__`` attribute.  It may be False, or it may
            be a method that converts the object to a supported data type for
            *NestedText*.  A matching converter specified in the *converters*
            argument dominates over this attribute.

        default (func or “strict”):
            The default converter. Use to convert otherwise unrecognized objects
            to a form that can be processed. If not provided an error will be
            raised for unsupported data types. Typical values are *repr* or
            *str*. If “strict” is specified then only dictionaries, lists,
            strings, and those types that have converters are allowed. If
            *default* is not specified then a broader collection of value types
            are supported, including *None*, *bool*, *int*, *float*, and *list*-
            and *dict*-like objects.  In this case Booleans are rendered as
            “True” and “False” and None is rendered as an empty string.  If
            *default* is a function, it acts as the default converter.  If
            it raises a TypeError, the value is reported as an
            unsupported type.

        spacing (dict):
            A mapping that controls vertical spacing in the rendered output.

            Integer keys specify the minimum number of blank lines between
            sibling items at that depth.  ``spacing={0: 1}`` requests one blank
            line between top-level items; ``spacing={0: 2, 1: 1}`` requests two
            blank lines between top-level items and one between items at the
            first nested level.  Depths not present in the mapping default to
            zero.

            The special key ``"edges"`` is the number of blank lines between
            the document's header comments and the first data item, and
            between the last data item and the document's footer comments.
            One number applies to both.  Defaults to zero.

        map_keys (func or keymap):
            This argument is used to modify the way keys are rendered, and,
            when it is a keymap, to preserve comments and blank-line spacing
            on round trip.

            It may be a keymap that was created by :func:`load` or
            :func:`loads`, in which case keys are rendered into their original
            form, before any normalization or de-duplication was performed by
            the load functions.  In addition, any comments captured by the
            loader and stored on the keymap are re-emitted around their
            associated keys.  Document-level header and footer comments are
            stored on the root Location (``keymap[()]``) and emitted at the
            top and bottom of the document.

            It may also be a function that takes two arguments: the key after
            any needed conversion has been performed, and the tuple of parent
            keys.  The value returned is used as the key and so must be a
            string.  If no value is returned, the key is not modified.

        width (int):
            Enables inline lists and dictionaries if greater than zero and if
            resulting line would be less than or equal to given width.

        inline_level (int):
            Recursion depth must be equal to this value or greater to be
            eligible for inlining.

        inline_count (int):
            The minimum number of items required of a dictionary or list to be
            eligible for inlining.

        dialect (str):
            Specifies support for particular variations in *NestedText*.

            In general you are discouraged from using a dialect as it can result
            in *NestedText* documents that are not compliant with the standard.

            The following deviant dialects are supported.

            *support inlines*:
                If "i" is included in *dialect*, support for inline lists and
                dictionaries is dropped.  The default is "I", which enables
                support for inlines.  The main effect of disabling inlines in
                the dump functions is that empty lists and dictionaries are
                output using an empty value, which is normally interpreted by
                *NestedText* as an empty string.

    Returns:
        The *NestedText* content without a trailing newline.  *NestedText* files
        should end with a newline, but unlike :func:`dump`, this function does
        not output that newline.  You will need to explicitly add that newline
        when writing the output :func:`dumps` to a file.

    Raises:
        NestedTextError: if there is a problem in the input data.

    Examples:

        .. code-block:: python

            >>> import nestedtext as nt

            >>> data = {
            ...     "name": "Kristel Templeton",
            ...     "gender": "female",
            ...     "age": "74",
            ... }

            >>> try:
            ...     print(nt.dumps(data))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            name: Kristel Templeton
            gender: female
            age: 74

        The *NestedText* format only supports dictionaries, lists, and strings.
        By default, *dumps* is configured to be rather forgiving, so it will
        render many of the base Python data types, such as *None*, *bool*,
        *int*, *float* and list-like types such as *tuple* and *set* by
        converting them to the types supported by the format.  This implies that
        a round trip through *dumps* and *loads* could result in the types of
        values being transformed. You can restrict *dumps* to only supporting
        the native types of *NestedText* by passing `default="strict"` to
        *dumps*.  Doing so means that values that are not dictionaries, lists,
        or strings generate exceptions.

        .. code-block:: python

            >>> data = {"key": 42, "value": 3.1415926, "valid": True}

            >>> try:
            ...     print(nt.dumps(data))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            key: 42
            value: 3.1415926
            valid: True

            >>> try:
            ...     print(nt.dumps(data, default="strict"))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            key: unsupported type (int).

        Alternatively, you can specify a function to *default*, which is used
        to convert values to recognized types.  It is used if no suitable
        converter is available.  Typical values are *str* and *repr*.

        .. code-block:: python

            >>> class Color:
            ...     def __init__(self, color):
            ...         self.color = color
            ...     def __repr__(self):
            ...         return f"Color({self.color!r})"
            ...     def __str__(self):
            ...         return self.color

            >>> data["house"] = Color("red")
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

            >>> data["house"] = Color("red")
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
            ...     bool: lambda b: "yes" if b else "no",
            ...     int: hex,
            ...     float: lambda f: f"{f:0.3}",
            ...     Color: lambda c: c.color,
            ...     Info: lambda i: i.__dict__,
            ... }

            >>> data["attributes"] = Info(readable=True, writable=False)

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
            ...     bool: lambda b: "yes" if b else "no",
            ...     int: hex,
            ...     float: False,
            ...     Color: lambda c: c.color,
            ...     Info: lambda i: i.__dict__,
            ... }

            >>> try:
            ...    print(nt.dumps(data, converters=converters))
            ... except nt.NestedTextError as e:
            ...     print(str(e))
            value: unsupported type (float).

        *converters* need not actually change the type of a value, it may simply
        transform the value.  In the following example, *converters* is used to
        transform dictionaries by removing empty dictionary fields.  It is also
        converts dates and physical quantities to strings.

        .. code-block:: python

            >>> import arrow
            >>> from inform import cull
            >>> import quantiphy

            >>> class Dollars(quantiphy.Quantity):
            ...     units = "$"
            ...     form = "fixed"
            ...     prec = 2
            ...     strip_zeros = False
            ...     show_commas = True

            >>> converters = {
            ...     dict: cull,
            ...     arrow.Arrow: lambda d: d.format("D MMMM YYYY"),
            ...     quantiphy.Quantity: lambda q: str(q)
            ... }

            >>> transaction = dict(
            ...     date = arrow.get("2013-05-07T22:19:11.363410-07:00"),
            ...     description = "Incoming wire from Publisher’s Clearing House",
            ...     debit = 0,
            ...     credit = Dollars(12345.67)
            ... )

            >>> print(nt.dumps(transaction, converters=converters))
            date: 7 May 2013
            description: Incoming wire from Publisher’s Clearing House
            credit: $12,345.67

        Both *default* and *converters* may be used together. *converters* has
        priority over the built-in types and *default*.  When a function is
        specified as *default*, it is always applied as a last resort.

        Use the *map_keys* argument to format the keys as you wish.  For
        example, you may wish to render the keys at the first level of hierarchy
        in upper case:

        .. code-block:: python

            >>> def map_keys(key, parent_keys):
            ...     if len(parent_keys) == 0:
            ...         return key.upper()

            >>> print(nt.dumps(transaction, converters=converters, map_keys=map_keys))
            DATE: 7 May 2013
            DESCRIPTION: Incoming wire from Publisher’s Clearing House
            CREDIT: $12,345.67

        It can also be used map the keys back to their original form when
        round-tripping a dataset when using key normalization or key
        de-duplication:

        .. code-block:: python

            >>> content = """
            ... Michael Jordan:
            ...     occupation: basketball player
            ... Michael Jordan:
            ...     occupation: actor
            ... Michael Jordan:
            ...     occupation: football player
            ... """

            >>> def de_dup(key, state):
            ...     if key not in state:
            ...         state[key] = 1
            ...     state[key] += 1
            ...     return f"{key}  ⟪#{state[key]}⟫"

            >>> keymap = {}
            >>> people = nt.loads(content, dict, on_dup=de_dup, keymap=keymap)
            >>> print(nt.dumps(people))
            Michael Jordan:
                occupation: basketball player
            Michael Jordan  ⟪#2⟫:
                occupation: actor
            Michael Jordan  ⟪#3⟫:
                occupation: football player

            >>> print(nt.dumps(people, map_keys=keymap))
            Michael Jordan:
                occupation: basketball player
            Michael Jordan:
                occupation: actor
            Michael Jordan:
                occupation: football player

    '''

    # code {{{3
    dumper = NestedTextDumper(
        indent, sort_keys, converters, default, spacing,
        map_keys, width, inline_level, inline_count, dialect
    )
    content = dumper.render_value(obj, (), ())

    # prepend header / append footer comments when map_keys is a keymap dict
    # carrying a document-root Location.  The blank-line gap between header
    # and body (and between body and footer) is taken from spacing["edges"]
    # if present, else zero.
    if is_mapping(map_keys):
        root = map_keys.get(())
        header = root.get_header_comments() if root is not None else None
        footer = root.get_footer_comments() if root is not None else None
        root_spacing = root.get_spacing() if root is not None else None
        if root_spacing:
            edge_blanks = root_spacing.get("edges", 1)
        else:
            edge_blanks = (spacing or {}).get("edges", 1)
        edge_sep = "\n" + ("\n" * edge_blanks)
        if header:
            header_lines = dumper._comments_to_lines(header, natural=0)
            if header_lines:
                rendered = "\n".join(header_lines)
                content = rendered + edge_sep + content if content else rendered
        if footer:
            footer_lines = dumper._comments_to_lines(footer, natural=0)
            if footer_lines:
                rendered = "\n".join(footer_lines)
                content = content + edge_sep + rendered if content else rendered

    return content


# dump {{{2
def dump(obj, dest, **kwargs):
    # description {{{3
    """Write the *NestedText* representation of the given object to the given file.

    Args:
        obj:
            The object to convert to *NestedText*.
        dest (str, os.PathLike, io.TextIOBase):
            The file to write the *NestedText* content to.  The file can be
            specified either as a path (e.g. a string or a `pathlib.Path`) or
            as a text IO instance (e.g. an open file, or 1 for stdout).  If a
            path is given, the will be opened, written, and closed.  If an IO
            object is given, it must have been opened in a mode that allows
            writing (e.g.  ``open(path, "w")``), if applicable.  It will be
            written and not closed.

            The name used for the file is arbitrary but it is tradition to use a
            .nt suffix.  If you also wish to further distinguish the file type
            by giving the schema, it is recommended that you use two suffixes,
            with the suffix that specifies the schema given first and .nt given
            last. For example: flicker.sig.nt.
        kwargs:
            See :func:`dumps` for optional arguments.

    Returns:
        The *NestedText* content with a trailing newline.  This differs from
        :func:`dumps`, which does not add the trailing newline.

    Raises:
        NestedTextError: if there is a problem in the input data.
        OSError: if there is a problem opening the file.

    Examples:

        This example writes to a pointer to an open file.

        .. code-block:: python

            >>> import nestedtext as nt
            >>> from inform import fatal, os_error

            >>> data = {
            ...     "name": "Kristel Templeton",
            ...     "gender": "female",
            ...     "age": "74",
            ... }

            >>> try:
            ...     with open("data.nt", "w", encoding="utf-8") as f:
            ...         nt.dump(data, f)
            ... except nt.NestedTextError as e:
            ...     e.terminate()
            ... except OSError as e:
            ...     fatal(os_error(e))

        This example writes to a file specified by file name.  In general, the
        file name and extension are arbitrary. However, by convention a
        ‘.nt’ suffix is generally used for *NestedText* files.

        .. code-block:: python

            >>> try:
            ...     nt.dump(data, "data.nt")
            ... except nt.NestedTextError as e:
            ...     e.terminate()
            ... except OSError as e:
            ...     fatal(os_error(e))

    """

    # code {{{3
    content = dumps(obj, **kwargs)

    try:
        dest.write(content + "\n")
    except (AttributeError, TypeError) as e:
        # Avoid nested try-except blocks, since they lead to chained exceptions
        # (e.g. if the file isn’t found, etc.) that unnecessarily complicate the
        # stack trace.
        exception = e
    else:
        return

    if isinstance(exception, TypeError):
        # file may be binary, encode in utf8 and try again
        dest.write((content + "\n").encode('utf8'))
    else:
        # dest is a file name rather than a file pointer
        with open(dest, "w", encoding="utf-8") as f:
            f.write(content + "\n")


# NestedText Utilities {{{1
# Extras that are useful when using NestedText.

# get_keys {{{2
def get_keys(keys, keymap, *, original=True, strict=True, sep=None):
    # description {{{3
    '''
    Returns a key sequence given a normalized key sequence.

    Keys in the dataset output by the load functions are referred to as
    normalized keys, even though no key normalization may have occurred.  This
    distinguishes them from the original keys, which are the keys given in the
    NestedText document read by the load functions.  The original keys are
    mapped to normalized keys by the *normalize_key* argument to the load
    function.  If normalization is not performed, the normalized keys are
    the same as the original keys.

    By default this function returns the original key sequence that corresponds
    to *keys*, a normalized key sequence.

    Args:
        keys:
            The sequence of normalized keys that identify a value in the
            dataset.
        keymap:
            The keymap returned from :meth:`load` or :meth:`loads`.
        original:
            If true, return keys as originally given in the NestedText document
            (pre-normalization). Otherwise return keys as they exist in the
            dataset (post-normalization).  The value of this argument has no
            effect if the keys were not normalized.
        strict:
            *strict* controls what happens if the given keys are not found in
            *keymap*.

            The various options can be helpful when reporting errors on key
            sequences that do not exist in the data set.  Since they are not in
            the dataset, the original keys are not available.

            True or "error":
                A *KeyError* is raised.
            False or "all":
                All keys given in *keys* are returned.
            "found":
                Only the initial available keys are returned.
            "missing":
                Only the missing final keys are returned.

            When returning keys, the initial available keys are converted to
            their original form if *original* is true,  The missing keys are
            always returned as given.

        sep:
            A join string.  If given the keys are interleaved with *sep* and
            joined into a string before being returned.

    Returns:
        A tuple containing the desired keys if *sep* is not given.
        A string formed by joining the keys with *sep* if *sep* is given.

    Examples:

        .. code-block:: python

            >>> import nestedtext as nt

            >>> contents = """
            ... Names:
            ...     Given: Fumiko
            ... """

            >>> def normalize_key(key, keys):
            ...     return key.lower()

            >>> data = nt.loads(contents, "dict", normalize_key=normalize_key, keymap=(keymap:={}))

            >>> print(get_keys(("names", "given"), keymap))
            ('Names', 'Given')

            >>> print(get_keys(("names", "given"), keymap, sep="❭"))
            Names❭Given

            >>> print(get_keys(("names", "given"), keymap, original=False))
            ('names', 'given')

            >>> keys = get_keys(("names", "surname"), keymap, strict=True)
            Traceback (most recent call last):
            ...
            KeyError: ('names', 'surname')

            >>> print(get_keys(("names", "surname"), keymap, strict="found"))
            ('Names',)

            >>> print(get_keys(("names", "surname"), keymap, strict="missing"))
            ('surname',)

            >>> print(get_keys(("names", "surname"), keymap, strict="all"))
            ('Names', 'surname')

    '''

    # code {{{3
    assert strict in [True, False, "missing", "error", "all", "found"], strict
    if type(keys) is not tuple:
        keys = tuple(keys)

    to_return = ()
    for i in range(len(keys)):
        try:
            loc = keymap[tuple(keys[:i+1])]
            key = loc._get_original_key(keys[i], strict) if original else keys[i]
            if strict != "missing":
                to_return += key,
        except (KeyError, IndexError):
            if strict in [True, "error"]:
                raise
            if strict != "found":
                to_return += keys[i],
    if sep:
        return sep.join(str(k) for k in to_return)
    return to_return


# get_value{{{2
def get_value(data, keys):
    # description {{{3
    '''
    Get value from keys.

    Args:
        data:
            Your data set as returned by :meth:`load` or :meth:`loads`.
        keys:
            The sequence of normalized keys that identify a value in the
            dataset.

    Returns:
        The value that corresponds to a tuple of keys from a keymap.

    Examples:

        .. code-block:: python

            >>> import nestedtext as nt

            >>> contents = """
            ... names:
            ...     given: Fumiko
            ...     surname: Purvis
            ... """

            >>> data = nt.loads(contents, "dict")

            >>> nt.get_value(data, ("names", "given"))
            'Fumiko'

    '''

    # code {{{3
    for key in keys:
        try:
            data = data[key]
        except TypeError:
            raise KeyError(key)
    return data


# get_line_numbers {{{2
def get_line_numbers(keys, keymap, kind="value", *, strict=True, sep=None):
    # description {{{3
    '''
    Get line numbers from normalized key sequence.

    This function returns the line numbers of the key or value selected by
    *keys*.  It is used when reporting an error in a value that is possibly a
    multiline string.  If the location contained in a keymap were used the user
    would only see the line number of the first line, which may confuse some
    users into believing the error is actually contained in the first line.
    Using this function gives both the starting and ending line number so the
    user focuses on the whole string and not just the first line.  This only
    happens for multiline keys and multiline strings.

    If *sep* is given, either one line number or both the beginning and ending line
    numbers are returned, joined with the separator. In this case the line numbers
    start from line 1.

    If *sep* is not given, the line numbers are returned as a tuple containing a pair
    of integers that is tailored to be suitable to be arguments to the Python slice
    function (see example). The beginning line number and 1 plus the ending line
    number is returned as a tuple. In this case the line numbers start at 0.

    If *keys* corresponds to a composite value (a dictionary or list), the
    line on which it ends cannot be easily determined, so the value is treated
    as if it consists of a single line.  This is considered tolerable as it is
    expected that this function is primarily used to return the line number of
    leaf values, which are always strings.

    Args:
        keys:
            The sequence of normalized keys that identify a value in the
            dataset.
        keymap:
            The keymap returned from :meth:`load` or :meth:`loads`.
        kind:
            Specify either “key” or “value” depending on which token is
            desired.
        strict:
            If *strict* is true, a *KeyError* is raised if *keys* is not found.
            Otherwise the line number that corresponds to composite value that
            would contain *keys* if it existed.  This composite value
            corresponds to the largest sequence of keys that does actually exist
            in the dataset.
        sep:
            The separator string. If given a string is returned and *sep* is
            inserted between two line numbers.  Otherwise a tuple is returned.

    Raises:
        KeyError:
            If keys are not in *keymap* and *strict* is true.

    Example:
        >>> import nestedtext as nt

        >>> doc = """
        ... key:
        ...     > this is line 1
        ...     > this is line 2
        ...     > this is line 3
        ... """

        >>> data = nt.loads(doc, keymap=(keymap:={}))
        >>> keys = ("key",)
        >>> lines = nt.get_line_numbers(keys, keymap, sep="-")
        >>> text = doc.splitlines()
        >>> print(
        ...     f"Lines {lines}:",
        ...     *text[slice(*nt.get_line_numbers(keys, keymap))],
        ...     sep="\\n"
        ... )
        Lines 3-5:
            > this is line 1
            > this is line 2
            > this is line 3

    '''

    # code {{{3
    loc = get_location(keys, keymap)
    if not loc:
        if strict:
            raise KeyError(keys)
        else:
            found = get_keys(keys, keymap, original=False, strict="found")
            loc = keymap[found]
    return loc.get_line_numbers(kind, sep)


# get_location {{{2
def get_location(keys, keymap):
    # description {{{3
    '''
    Returns :class:`Location` information from the keys.
    None is returned if location is unknown.

    Args:
        keys:
            The sequence of normalized keys that identify a value in the
            dataset.
        keymap:
            The keymap returned from :meth:`load` or :meth:`loads`.
    '''

    # code {{{3
    if type(keys) is not tuple:
        keys = tuple(keys)

    try:
        return keymap[keys]
    except KeyError:
        return None


# annotate {{{2
def annotate(
    keys,
    keymap,
    *,
    key_leading=(),
    key_trailing=(),
    value_leading=(),
    value_trailing=(),
    header=(),
    footer=(),
    spacing=None,
):
    '''Create or update ``keymap[tuple(keys)]`` with comments and
    per-Location spacing in a single call.

    This is the from-scratch counterpart to the keymap that :func:`load`
    builds.  Each of the four per-key slot kwargs --
    ``key_leading``, ``key_trailing``, ``value_leading``,
    ``value_trailing`` -- accepts either:

    - an iterable of :class:`Comment` objects (static), which become
      the comments attached to *this* Location at that slot.  Each
      Comment is interpreted in *tab mode*: its ``tab`` field
      (defaulting to 0 when ``None``) is the tabstop offset from the
      slot's natural indent, resolved by the dumper at emit time using
      the ``dumps(indent=...)`` setting; or
    - a callable (a *provider*) with the signature ::

          provider(child_key) -> list[Comment]

      installed on this Location to be invoked by the dumper for **each
      child** of this Location's value.  The returned Comments are
      prepended to the matching child's static comments at the same
      slot, before rendering.  This is how dynamic section / group
      headers are produced (the closure can dedup over previously-seen
      keys).  Comments returned by a provider with ``tab=None`` are
      normalized to ``tab=0`` at emit time.  Providers are not
      JSON-serializable and are dropped on :func:`keymap_to_jsonable`
      round-trips.

    The natural indent for each slot, given ``N = len(keys)`` and
    ``S = dumps.indent``:

    +-------------------+---------------------+
    | slot              | natural indent      |
    +===================+=====================+
    | ``key_leading``   | ``(N - 1) * S``     |
    +-------------------+---------------------+
    | ``key_trailing``, |                     |
    | ``value_leading``,| ``N * S``           |
    | ``value_trailing``|                     |
    +-------------------+---------------------+
    | ``header``,       | ``0``               |
    | ``footer``        |                     |
    +-------------------+---------------------+

    Static lists in the per-key slots are not allowed at the root
    (``keys == ()``) since the root has no key line to attach to.  A
    provider callable, however, *is* allowed at the root -- it
    decorates each top-level child.

    ``spacing``, if given, is applied via :meth:`Location.set_spacing`.

    Args:
        keys:
            The keys tuple identifying the Location.  Use ``()`` for the
            document-root Location.
        keymap:
            The keymap dict to mutate.
        key_leading, key_trailing, value_leading, value_trailing:
            Either an iterable of :class:`Comment` objects (stored on
            this Location) or a callable provider (invoked per child of
            this Location; see above).  Static lists are not allowed
            when ``keys == ()``.
        header, footer:
            Iterables of :class:`Comment` objects for the document
            header and footer.  Only allowed when ``keys == ()``.
        spacing:
            Per-Location spacing dict; see :meth:`Location.set_spacing`.

    Returns:
        The :class:`Location` that was created or updated.

    Raises:
        ValueError: if a static list is supplied for any of
            ``key_leading``/``key_trailing``/``value_leading``/
            ``value_trailing`` at the root, or if ``header``/``footer``
            is supplied for non-root keys.
    '''
    if not isinstance(keys, tuple):
        keys = tuple(keys)

    is_root = (keys == ())

    def _is_provider(value):
        # A provider is callable but not a tuple/list/Comment/dict; we
        # check `callable(value)` and exclude iterables (which would be
        # static comment lists).
        return callable(value) and not isinstance(
            value, (list, tuple, set, frozenset)
        )

    per_key_slots = (
        ("key_leading",    key_leading,    "set_key_leading_comments",    "set_key_leading_provider"),
        ("key_trailing",   key_trailing,   "set_key_trailing_comments",   "set_key_trailing_provider"),
        ("value_leading",  value_leading,  "set_value_leading_comments",  "set_value_leading_provider"),
        ("value_trailing", value_trailing, "set_value_trailing_comments", "set_value_trailing_provider"),
    )

    if is_root:
        for name, value, _, _ in per_key_slots:
            if value and not _is_provider(value):
                raise ValueError(
                    f"{name}= as a static Comment list is not allowed at the"
                    " document root (keys=()); use header/footer, or pass a"
                    " provider callable to decorate each top-level child."
                )
    if not is_root and (header or footer):
        raise ValueError(
            "header/footer are only allowed at the document root (keys=())."
        )

    loc = keymap.get(keys)
    if loc is None:
        loc = Location()
        keymap[keys] = loc

    def _tab_mode(comments):
        out = []
        for c in comments:
            if c.tab is None:
                c.tab = 0
            out.append(c)
        return out

    for _name, value, set_static, set_provider in per_key_slots:
        if not value:
            continue
        if _is_provider(value):
            getattr(loc, set_provider)(value)
        else:
            getattr(loc, set_static)(_tab_mode(value))
    if header:
        loc.set_header_comments(_tab_mode(header))
    if footer:
        loc.set_footer_comments(_tab_mode(footer))

    if spacing is not None:
        loc.set_spacing(spacing)

    return loc


# keymap_to/from_json {{{2
class _RestoredLocation(Location):
    """A Location reconstructed from JSON.

    Carries only what :func:`dumps` reads from a keymap: the original key
    string (for ``_get_original_key``) and the comment slots.
    """
    def __init__(self, original_key=None):
        super().__init__()
        self._original_key = original_key

    def _get_original_key(self, key, strict):
        if self._original_key is not None:
            return self._original_key
        return key


def _comment_to_dict(c):
    d = {"text": c.text, "indent": c.indent}
    if c.tab is not None:
        d["tab"] = c.tab
    if c.before:
        d["before"] = c.before
    if c.after:
        d["after"] = c.after
    return d


def _comment_from_dict(d):
    return Comment(
        text=d["text"],
        indent=d["indent"],
        tab=d.get("tab"),
        before=d.get("before", 0),
        after=d.get("after", 0),
    )


def keymap_to_jsonable(keymap, **kwargs):
    '''Reduce a keymap to a JSON-serializable structure for use with :func:`dumps`.

    Captures only what :func:`dumps` needs from the keymap to reconstruct
    the original file: the original key strings (so ``map_keys`` can
    restore them) and the per-entry comment slots, plus the document
    header / footer on ``keymap[()]``.  Source line/column information is
    discarded.  Per-slot provider callables (set via
    :meth:`Location.set_key_leading_provider` and the matching
    ``set_*_provider`` methods) are also dropped because callables are
    not JSON-serializable; rebuilt keymaps therefore omit any
    provider-driven decoration.

    The returned object is built from ``dict``, ``list``, ``str``, ``int``,
    and ``None`` — safe to pass through :mod:`json`, :mod:`msgpack`, or any
    similar encoder.

    Args:
        keymap:
            The keymap returned from :func:`load` or :func:`loads`, or any
            equivalent mapping from key-tuples to :class:`Location`
            objects.
        **kwargs:
            Any extra keyword arguments are included in the returned structure
            under a top-level "meta" key.  These values are not used by
            :func:`keymap_from_jsonable` but are included to allow you to
            include any extra metadata you wish in the JSON-serializable
            structure.  No attempt is made to ensure that the values in
            **kwargs** are themselves JSON-serializable, so you should ensure
            that they are if you intend to pass the output through a JSON
            encoder.

    Returns:
        A JSON-serializable ``dict``.  Pass it to :func:`keymap_from_jsonable`
        to rebuild a keymap that can be given to :func:`dumps` as
        ``map_keys=``.
    '''
    entries = []
    for keys, loc in keymap.items():
        entry = {"keys": list(keys)}
        if keys and isinstance(keys[-1], str):
            entry["original_key"] = loc._get_original_key(keys[-1], strict=False)
        for attr, label in (
            ("key_leading_comments",   "key_leading"),
            ("key_trailing_comments",  "key_trailing"),
            ("value_leading_comments", "value_leading"),
            ("value_trailing_comments","value_trailing"),
        ):
            comments = getattr(loc, attr, None)
            if comments:
                entry[label] = [_comment_to_dict(c) for c in comments]
        if not keys:
            if loc.header_comments:
                entry["header"] = [_comment_to_dict(c) for c in loc.header_comments]
            if loc.footer_comments:
                entry["footer"] = [_comment_to_dict(c) for c in loc.footer_comments]
        sp = getattr(loc, "spacing", None)
        if sp:
            # JSON object keys must be strings; integer depth keys are
            # stringified here and parsed back in keymap_from_jsonable.
            entry["spacing"] = {str(k): v for k, v in sp.items()}
        entries.append(entry)
    return cull(dict(keymap=entries, meta=kwargs))


def keymap_from_jsonable(data):
    '''Rebuild a keymap from the output of :func:`keymap_to_jsonable`.

    The returned mapping is suitable for passing to :func:`dumps` (or
    :func:`dump`) as ``map_keys=``; it will restore the original key
    strings and inject the captured comments.  Locations in the rebuilt
    keymap do *not* carry source line/column information.

    Args:
        data:
            The JSON-serializable structure produced by
            :func:`keymap_to_jsonable` (or an equivalent reconstruction of
            it, e.g., from ``json.loads``).
    '''
    keymap = {}
    for entry in data["keymap"]:
        keys = tuple(entry["keys"])
        loc = _RestoredLocation(original_key=entry.get("original_key"))
        loc.key_leading_comments = [
            _comment_from_dict(d) for d in entry.get("key_leading", [])
        ]
        loc.key_trailing_comments = [
            _comment_from_dict(d) for d in entry.get("key_trailing", [])
        ]
        loc.value_leading_comments = [
            _comment_from_dict(d) for d in entry.get("value_leading", [])
        ]
        loc.value_trailing_comments = [
            _comment_from_dict(d) for d in entry.get("value_trailing", [])
        ]
        if not keys:
            loc.header_comments = [
                _comment_from_dict(d) for d in entry.get("header", [])
            ]
            loc.footer_comments = [
                _comment_from_dict(d) for d in entry.get("footer", [])
            ]
        raw_spacing = entry.get("spacing")
        if raw_spacing:
            # Convert numeric string keys back to int (depth keys); leave
            # non-numeric keys -- e.g. "edges" -- as strings.
            loc.spacing = {
                (int(k) if k.lstrip("-").isdigit() else k): v
                for k, v in raw_spacing.items()
            }
        keymap[keys] = loc
    return keymap

# vim: set sw=4 sts=4 tw=80 fo=croqj foldmethod=marker et spell:
