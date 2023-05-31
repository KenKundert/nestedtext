# NestedText
__version__ = "3.6rc2"
__released__ = "2023-05-23"

from .nestedtext import (
    load, loads, dump, dumps, NestedTextError,
    get_value_from_keys, get_lines_from_keys, get_original_keys, join_keys
)
