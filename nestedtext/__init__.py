# NestedText
__version__ = "3.8"
__released__ = "2025-12-26"

from .nestedtext import (
    load, loads, dump, dumps, NestedTextError,

    # utitilies
    get_keys, get_value, get_location, get_line_numbers,

    # deprecated utitilies
    get_value_from_keys, get_lines_from_keys, get_original_keys, join_keys,

    # the following is only needed in order to generate the documentation
    Location
)
