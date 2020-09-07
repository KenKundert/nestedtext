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
    cull,
    full_stop,
    set_culprit,
    get_culprit,
    is_str,
    is_collection,
    is_mapping,
    Error,
    Info,
    InformantFactory,
)


# Globals {{{1
__version__ = "0.3.1"
__released__ = "2020-09-05"
__all__ = ['loads', 'dumps', 'NestedTextError']


# Exception {{{1
class NestedTextError(Error, ValueError):
    '''
    :func:`nestedtext.loads()` and :func:`nestedtext.dumps()` both raise 
    *NestedTextError* when they discover an error. *NestedTextError* subclasses both 
    the Python *ValueError* and the *Error* exception from *Inform*.
    You can find more documentation on what you can do with this exception in the 
    `Inform documentation 
    <https://inform.readthedocs.io/en/stable/api.html#exceptions>`_.

    The exception provides the following attributes:

    source:

        The source of the *NestedText* content, if given. This is often a 
        filename.

    doc:

        The *NestedText* content passed to :func:`nestedtext.loads`.

    line:

        The line of *NestedText* content where the problem was found.

    lineno:

        The number of the line where the problem was found.

    colno:

        The number of the character where the problem was found on *line*.

    template:

        The possibly parameterized text used for the error message.

    As with most exceptions, you can simply cast it to a string to get a 
    reasonable error message.

    .. code-block:: pycon

        >>> from textwrap import dedent
        >>> import nestedtext

        >>> content = dedent("""
        ...     name1: value1
        ...     name1: value2
        ...     name3: value3
        ... """).strip()

        >>> try:
        ...     print(nestedtext.loads(content))
        ... except nestedtext.NestedTextError as e:
        ...     print(str(e))
        2: duplicate key: name1.

    You can also use the *report* method to print the message directly. This is 
    appropriate if you are using *inform* for your messaging as it follows 
    *inform*'s conventions:

    .. code-block:: pycon

        >> try:
        ..     print(nestedtext.loads(content))
        .. except nestedtext.NestedTextError as e:
        ..     e.report()
        error: 2: duplicate key: name1.
            «name1: value2»
             ↑

    The *terminate* method prints the message directly and exits:

    .. code-block:: pycon

        >> try:
        ..     print(nestedtext.loads(content))
        .. except nestedtext.NestedTextError as e:
        ..     e.terminate()
        error: 2: duplicate key: name1.
            «name1: value2»
             ↑

    Exceptions produced by *NestedText* contain a *template* attribute that 
    contains the basic text of the message. You can change this message by 
    overriding the attribute when using *report*, *terminate*, or *render*.  
    *render* is like casting the exception to a string except that allows for 
    the passing of arguments.  For example, to convert a particular message to 
    Spanish, you could use something like the following.

    .. code-block:: pycon

        >>> try:
        ...     print(nestedtext.loads(content))
        ... except nestedtext.NestedTextError as e:
        ...     template = None
        ...     if e.template == 'duplicate key: {}.':
        ...         template = 'llave duplicada: {}.'
        ...     print(e.render(template=template))
        2: llave duplicada: name1.

    When you have the exception report itself, you see up to two extra lines in 
    the message that are used to display the line and the location where the 
    problem was found.  Those extra lines are referred to as the codicil. You 
    do not get them if you simply cast the exception to a string, but you can 
    access them using :meth:`nestedtext.NestedTextError.get_codicil`.  There is 
    an additional method, 
    :meth:`nestedtext.NestedTextError.get_extended_codicil` that also shows the 
    source of the problem, but with extra context.

    .. code-block:: pycon

        >> try:
        ..     print(nestedtext.loads(content))
        .. except nestedtext.NestedTextError as e:
        ..     e.report(codicil=e.get_extended_codicil())
        error: 2: duplicate key: name1.
            1> name1: value1
            2> name1: value2
               ↑
            2> name3: value3
    '''

    def get_extended_codicil(self):
        # Like the normal codicil, but provides a few lines of surrounding
        # context.
        codicil = self.get_codicil()
        try:
            lineno = self.lineno
            doc = self.doc
            colno = self.colno
            lines_before = doc.split('\n')[max(lineno-2, 0):lineno]
            lines = []
            for i, l in zip(range(lineno-len(lines_before), lineno), lines_before):
                lines.append(f'{i+1:>4}> {l}')
            lines_before = '\n'.join(lines)
            lines_after = doc.split('\n')[lineno:lineno+1]
            lines = []
            for i, l in zip(range(lineno, lineno + len(lines_after)), lines_after):
                lines.append(f'{i+1:>4}> {l}')
            lines_after = '\n'.join(lines)
            codicil = '\n'.join(cull([
                lines_before,
                '      ' + (colno*' ') + '↑',
                lines_after
            ]))
        except Exception:
            pass
        return codicil


# NestedText Reader {{{1
# Converts NestedText into Python data hierarchies.

# constants {{{2
dict_tag = ": "
quoted = "|".join([
    r'"[^"\n]*"',  # "string"
    r"'[^'\n]*'",  # 'string'
])
splitters = (
    quoted,           # "string" or 'string' (must be first)
    dict_tag,         # key/value separator in dictionary item
)
splitter = re.compile("(" + "|".join(f"(?:{s})" for s in splitters) + ")")


# debugging utilities {{{2
highlight = InformantFactory(message_color='blue')


def dbg(line, kind):  # pragma: no cover
    if line.depth is None:
        indents = ' '
    else:
        indents = line.depth
    highlight(f'{indents}{kind}{line.lineno:>4}:{line.text}')


# report {{{2
def report(message, line, *args, colno=None, **kwargs):
    message = full_stop(message)
    culprits = get_culprit()
    if culprits:
        kwargs['source'] = culprits[0]
    if line:
        kwargs['culprit'] = get_culprit(line.lineno)
        if colno is not None:
            kwargs['codicil'] = f"«{line.text}»\n {colno*' '}↑"
            kwargs['colno'] = colno
        else:
            kwargs['codicil'] = f"«{line.text}»"
        kwargs['line'] = line.text
        kwargs['lineno'] = line.lineno
        kwargs['doc'] = line.content
    else:
        kwargs['culprit'] = culprits  # pragma: no cover
    raise NestedTextError(template=message, *args, **kwargs)


# indentation_error {{{2
def indentation_error(line, depth):
    assert line.depth != depth
    report('invalid indentation.', line, colno=depth)


# is_quoted {{{2
def is_quoted(s):
    return s[:1] in ['"', "'"] and s[:1] == s[-1:]


# dequote {{{2
def dequote(s):
    s = s.strip()
    if is_quoted(s):
        return s[1:-1]
    return s


# Lines class {{{2
class Lines:
    class Line(Info):
        pass

    # constructor {{{3
    def __init__(self, content):
        self.content = content
        self.generator = self.read_lines()
        self.next_line = True
        while self.next_line:
            self.next_line = next(self.generator, None)
            if self.next_line and self.next_line.kind not in ["blank", "comment"]:
                return

    # read_lines() {{{3
    def read_lines(self):
        for lineno, line in enumerate(self.content.splitlines()):
            depth = None
            key = None
            value = None
            stripped = line.lstrip()
            depth = len(line) - len(stripped)
            if stripped == "":
                kind = "blank"
                value = "\n"
            elif stripped[:1] == "#":
                kind = "comment"
                value = line[1:].strip()
            elif stripped == '-' or stripped.startswith('- '):
                kind = "list item"
                value = dequote(stripped[2:])
            elif stripped == '>' or stripped.startswith('> '):
                kind = "string"
                value = line[depth+2:]
            else:
                components = splitter.split(line + " ")
                if dict_tag in components:
                    kind = "dict item"
                    split_loc = components.index(dict_tag)
                    key = dequote("".join(components[:split_loc]))
                    value = dequote("".join(components[split_loc + 1 :]))
                else:
                    kind = "unrecognized"
                    value = line

            the_line = self.Line(
                text = line,
                lineno = lineno+1,
                kind = kind,
                depth = depth,
                key = key,
                value = value,
                content = self.content
            )

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
            report("expected list item", line, colno=depth)
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
            report("expected dictionary item", line, colno=depth)
        if line.key in data:
            report('duplicate key: {}.', line, line.key, colno=depth)
        if '"' in line.key and "'" in line.key:
            report("""key must not contain both " and '.""", line, line.key, colno=depth)
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
def loads(content, culprit=None):
    '''
    Loads *NestedText* from string.

    Args:
        content (str):
            String that contains encoded data.
        culprit (str):
            Optional culprit. It is prepended to any error messages but is
            otherwise unused. Is often the name of the file that originally
            contained the NestedText content.

    Returns:
        A dictionary or list containing the data.  If content is empty, an
        empty dictionary is returned.

    Examples:

        *NestedText* is specified to *loads* in the form of a string:

        .. code-block:: pycon

            >>> import nestedtext
            >>> from inform import render

            >>> contents = """
            ... name: Kristel Templeton
            ... sex: female
            ... age: 74
            ... """

            >>> try:
            ...     data = nestedtext.loads(contents)
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))

            >>> print(render(data))
            {
                'name': 'Kristel Templeton',
                'sex': 'female',
                'age': '74',
            }

        *loads()* takes an optional second argument, *culprit*. If specified, 
        it will be prepended to any error messages. It is often used to 
        designate the source of *contents*. For example, if *contents* were 
        read from a file, *culprit* would be the file name.  Here is a typical 
        example of reading *NestedText* from a file:

        .. code-block:: pycon

            >>> filename = 'examples/duplicate-keys.nt'
            >>> try:
            ...     with open(filename) as f:
            ...         addresses = nestedtext.loads(f.read(), filename)
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))
            examples/duplicate-keys.nt, 5: duplicate key: name.

        Parsing data can be a difficult challenge. One way to reduce the 
        challenge is to reduce the scope of what is being parsed. With 
        *NestedText* you can delegate the parsing the of the structure and 
        instead focus on parsing individual values given as strings.  A 
        transforming validator like `Voluptuous 
        <https://github.com/alecthomas/voluptuous>`_ can greatly simply the 
        process.

        To use *Voluptuous* you would create a schema and then apply the schema 
        to the data. The schema details what fields are expected, and what what 
        kind of values they should contain. Normally the schema is used to 
        validate the data, but with a little extra plumbing the data can be 
        transformed to the needed form.  The following is a very simple example 
        (see :ref:`cryptocurrency holdings <cryptocurrency example>` for a more 
        complete example).

        In order for *Voluptuous* to convert the data to the desired type, a 
        converter function is helpful:

        .. code-block:: pycon

            >>> import voluptuous

            >>> def coerce(type, msg=None):
            ...     """Coerce a value to a type.
            ...
            ...     If the type constructor throws a ValueError, the value will be
            ...     marked as Invalid.
            ...     """
            ...     def f(v):
            ...         try:
            ...             return type(v)
            ...         except ValueError:
            ...             raise voluptuous.Invalid(msg or ('expected %s' % type.__name__))
            ...     return f

        The next step is to define a schema that declares the expected types of 
        the various fields in the configuration file. For example, imagine the 
        configuration file has has three values, *name*, *value*, and 
        *editable*, the first of which must be a string, the second a float, 
        and the third a boolean that is specified using either 'yes' or 'no'. 
        This can be done as follows:

        .. code-block:: pycon

            >>> import nestedtext
            >>> from inform import render

            >>> def to_bool(v):
            ...     try:
            ...         v = v.lower()
            ...         assert v in ['yes', 'no']
            ...         return v == 'yes'
            ...     except:
            ...         raise ValueError("expected 'yes' or 'no'.")

            >>> config = """
            ... name: volume
            ... value: 50
            ... editable: yes
            ... """

            >>> config_data = nestedtext.loads(config)
            >>> print(render(config_data))
            {
                'name': 'volume',
                'value': '50',
                'editable': 'yes',
            }

            >>> schema = voluptuous.Schema(
            ...     dict(name=str, value=coerce(float), editable=coerce(to_bool))
            ... )

            >>> settings = schema(config_data)
            >>> print(render(settings))
            {
                'name': 'volume',
                'value': 50.0,
                'editable': True,
            }

        Notice that a dictionary that contains the expected types and 
        conversion functions is passed to *Schema*. Then the raw configuration 
        is parsed for structure by *NestedText*, and the resulting data 
        structure is processed by the schema to and converted to its final 
        form.
    '''
    with set_culprit(culprit):
        lines = Lines(content)

        type_of_first = lines.type_of_next()
        if type_of_first not in ["list item", "dict item"]:
            if type_of_first:
                report("expected list or dictionary item.", lines.get_next(), colno=0)
            else:
                return {}
        else:
            return read_value(lines, 0)


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

    Examples:
        This example writes to a string, but it is common to write to a file.  
        The file name and extension are arbitrary. However, by convention a 
        '.nt' suffix is generally used for *NestedText* files.

        .. code-block:: pycon

            >>> import nestedtext

            >>> data = {
            ...     'name': 'Kristel Templeton',
            ...     'sex': 'female',
            ...     'age': '74',
            ... }

            >>> try:
            ...     print(nestedtext.dumps(data))
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))
            name: Kristel Templeton
            sex: female
            age: 74

        The *NestedText* format only supports dictionaries, lists, and strings.
        By default, *dumps* is configured to be rather forgiving, so it will 
        render many of the base Python data types, such as *None*, *bool*, 
        *int*, *float* and list-like types such as *tuple* and *set* by 
        converting them to the types supported by the format.  This implies 
        that a round trip through *dumps* and *loads* could result in the types 
        of values being transformed. You can prevent this by passing 
        `default='strict'` to *dumps*.  Doing so means that values that are not 
        dictionaries, lists, or strings generate exceptions.

        .. code-block:: pycon

            >>> data = {'key': 42, 'value': 3.1415926, 'valid': True}

            >>> try:
            ...     print(nestedtext.dumps(data))
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))
            key: 42
            value: 3.1415926
            valid: True

            >>> try:
            ...     print(nestedtext.dumps(data, default='strict'))
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))
            42: unsupported type.

        Alternatively, you can specify a function to *default*, which is used 
        to convert values to strings.  It is used if no other converter is 
        available.  Typical values are *str* and *repr*.

        .. code-block:: pycon

            >>> class Color:
            ...     def __init__(self, color):
            ...         self.color = color
            ...     def __repr__(self):
            ...         return f'Color({self.color!r})'
            ...     def __str__(self):
            ...         return self.color

            >>> data['house'] = Color('red')
            >>> print(nestedtext.dumps(data, default=repr))
            key: 42
            value: 3.1415926
            valid: True
            house: Color('red')

            >>> print(nestedtext.dumps(data, default=str))
            key: 42
            value: 3.1415926
            valid: True
            house: red

        You can also specify a dictionary of renderers. The dictionary maps the 
        object type to a render function.

        .. code-block:: pycon

            >>> renderers = {
            ...     bool: lambda b: 'yes' if b else 'no',
            ...     int: hex,
            ...     float: lambda f: f'{f:0.3}',
            ...     Color: lambda c: c.color,
            ... }

            >>> try:
            ...    print(nestedtext.dumps(data, renderers=renderers))
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))
            key: 0x2a
            value: 3.14
            valid: yes
            house: red

        If the dictionary maps a type to *None*, then the default behavior is 
        used for that type. If it maps to *False*, then an exception is raised.

        .. code-block:: pycon

            >>> renderers = {
            ...     bool: lambda b: 'yes' if b else 'no',
            ...     int: hex,
            ...     float: False,
            ...     Color: lambda c: c.color,
            ... }

            >>> try:
            ...    print(nestedtext.dumps(data, renderers=renderers))
            ... except nestedtext.NestedTextError as e:
            ...     print(str(e))
            3.1415926: unsupported type.

        Both *default* and *renderers* may be used together. *renderers* has 
        priority over the built-in types and *default*.  When a function is 
        specified as *default*, it is always applied as a last resort.
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
            error = 'expected top-level dictionary or list.'
    else:
        if need_indented_block:
            content = "\n" + add_leader(content, indent*' ')
        else:
            content = render_str(content)

    if error:
        raise NestedTextError(obj, template=error, culprit=repr(obj))

    return content

# vim: fdm=marker
