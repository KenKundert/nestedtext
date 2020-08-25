# Imports {{{1
from inform import indent, Error

# Globals {{{1
_sort = False
_level = 0


# dump {{{1
def dump(obj, sort=None, level=None):
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

    *dump* has built in support for the base Python types (*None*, *bool*,
    *int*, *float*, *str*, *set*, *tuple*, *list*, and *dict*).  If you confine
    yourself to these types, the output of dump can be read by the Python
    interpreter.  Other types are converted to string with *repr()*.

    **Example**::

        >>> from inform import display, dump
        >>> display('result =', dump({'a': (0, 1), 'b': [2, 3, 4]}))
        result = {'a': (0, 1), 'b': [2, 3, 4]}

    In addition, you can add support for dump to your classes by adding one or
    both of these methods:

        _inform_get_args(): returns a list of argument values.

        _inform_get_kwargs(): returns a dictionary of keyword arguments.

    **Example**::

        >>> class Chimera:
        ...     def __init__(self, *args, **kwargs):
        ...         self.args = args
        ...         self.kwargs = kwargs
        ...
        ...     def _inform_get_args(self):
        ...         return self.args
        ...
        ...     def _inform_get_kwargs(self):
        ...         return self.kwargs

        >>> lycia = Chimera('Lycia', front='lion', middle='goat', tail='snake')
        >>> display(dump(lycia))
        Chimera(
            'Lycia',
            front='lion',
            middle='goat',
            tail='snake',
        )

    """
    # define sort function
    global _sort
    prev_sort = _sort
    if sort is None:
        sort = _sort
    _sort = sort
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

    # render string
    def render_str(s, is_key=False):
        stripped = s.strip()
        if not s or len(stripped) < len(s):
            return repr(s)
        if is_key:
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

    # determine the level
    global _level
    prev_level = _level
    if level is None:
        level = _level
    else:
        _level = level

    if level == 0:

        def format_multiline_entry(s):
            return s

    else:

        def format_multiline_entry(s):
            return "\n" + indent(s)

    try:
        if isinstance(obj, dict):
            content = format_multiline_entry(
                "\n".join(
                    add_prefix(render_str(k, True) + ":", dump(obj[k], sort, level + 1))
                    for k in order(obj)
                )
            )
        elif isinstance(obj, (list, tuple, set)):
            content = format_multiline_entry(
                "\n".join(add_prefix("-", dump(v, sort, level + 1)) for v in obj)
            )
        elif isinstance(obj, str) and "\n" in obj:
            content = format_multiline_entry(obj)
        elif isinstance(obj, str):
            content = render_str(obj)
        elif obj is None:
            content = ""
        else:
            raise Error(f"unsupported type: {obj!r}")
    finally:
        # restore level and sort
        _level = prev_level
        _sort = prev_sort

    return content
