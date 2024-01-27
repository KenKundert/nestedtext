# NestedText
__version__ = "3.6.1"
__released__ = "2024-01-26"

from .nestedtext import (
    load, loads, dump, dumps, NestedTextError,
    get_value_from_keys, get_lines_from_keys, get_original_keys, join_keys,
    set_prefs
)
