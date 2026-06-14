# NestedText
__version__ = "3.8"
__released__ = "2025-12-26"

from .nestedtext import (
    load, loads, dump, dumps, NestedTextError, NestedTextDataError,

    # utitilies
    get_keys, get_value, get_location, get_line_numbers,

    # comments
    Comment, keymap_to_jsonable, keymap_from_jsonable, annotate,

    # the following is only needed in order to generate the documentation
    Location
)
