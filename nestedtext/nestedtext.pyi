from inform import Error
from pathlib import Path
from typing import Any, Callable, TextIO, Type

class NestedTextError(Error, ValueError): ...

class Line:
    text: str
    lineno: int
    kind: str
    depth: int
    key: str
    value: str | None
    prev_line: Line

    def render(
        self,
        col: int = ...
    ) -> str:
        ...

class Location:
    line: Line
    key_line: Line
    col: int
    key_col: int

    def __init__(
        self,
        line: Line = ...,
        col: int = ...,
        key_line: Line = ...,
        key_col: int = ...
    ) -> None:
        ...

    def as_tuple(
        self,
        kind: str = ...
    ) -> tuple[Line, int]:
        ...

    def as_line(
        self,
        kind: str = ...
    ) -> str:
        ...

def loads(
    content : str,
    top: str | Callable | Type[dict] | Type[list] | Type[str] = ...,
    *,
    source: str | Path = ...,
    on_dup: str | Callable = ...,
    # keymap: dict[tuple[str, ...], Location] = ...,
    keymap: dict[tuple[str, ...], Any] = ...,
    normalize_key: Callable = ...,
) -> str | list | dict | None:
    ...

def load(
    f: str | Path | TextIO,
    top: str | Callable | Type[dict] | Type[list] | Type[str] = ...,
    *,
    on_dup: str | Callable = ...,
    # keymap: dict[tuple[str, ...], Location] = ...,
    keymap: dict[tuple[str, ...], Any] = ...,
    normalize_key: Callable = ...,
) -> str | list | dict | None:
    ...

def dumps(
    obj: Any,
    *,
    width: int = ...,
    inline_level: int = ...,
    sort_keys: bool | Callable = ...,
    indent: int = ...,
    converters: dict[Type, Callable] | None = ...,
    default: str | Callable | None = ...
) -> str:
    ...

def dump(
    obj: Any,
    dest,
    **kwargs
) -> None: ...

def get_value_from_keys(
    obj: str | list | dict | None,
    keys: tuple[str, ...],
) -> str | list | dict:
    ...

def get_lines_from_keys(
    obj: str | list | dict | None,
    keys: tuple[str, ...],
    # keymap: dict[tuple[str, ...], Location],
    keymap: dict[tuple[str, ...], Any] = ...,
    kind: str = ...,
    sep: str = ...
) -> str | tuple[int, int]:
    ...

def get_original_keys(
    keys: tuple[str, ...],
    # keymap: dict[tuple[str, ...], Location],
    keymap: dict[tuple[str, ...], Any] = ...,
    strict: bool = ...
) -> tuple[int]:
    ...

def join_keys(
    keys: tuple[str, ...],
    sep: str = ...,
    # keymap: dict[tuple[str], Location] = ...,
    keymap: dict[tuple[str, ...], Any] = ...,
    strict: bool = ...
) -> str:
    ...
