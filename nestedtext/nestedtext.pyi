from inform import Error
from pathlib import Path
from typing import Any, Callable, TextIO, Type

# NestedTextError {{{1
class NestedTextError(Error, ValueError): ...


# Line {{{1
class Line:
    text: str
    lineno: int
    kind: str
    depth: int
    key: str
    value: str | None
    prev_line: Line
    leading_comments: list[Comment]
    trailing_comments: list[Comment]

    def render(
        self,
        col: int = ...
    ) -> str:
        ...

# Comment {{{1
class Comment:
    text: str
    indent: int
    tab: int | None
    before: int
    after: int

    def __init__(
        self,
        text: str = ...,
        indent: int = ...,
        *,
        tab: int | None = ...,
        before: int = ...,
        after: int = ...,
    ) -> None:
        ...

# Location {{{1
class Location:
    line: Line
    key_line: Line
    col: int
    key_col: int
    value_end_line: Line | None
    key_leading_comments: list[Comment]
    key_trailing_comments: list[Comment]
    value_leading_comments: list[Comment]
    value_trailing_comments: list[Comment]
    header_comments: list[Comment]
    footer_comments: list[Comment]
    spacing: dict[int | str, int]
    sections: list[tuple[Callable[[Any], bool], list[Comment]]]

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
        kind: str = ...,
        offset: int | (int, int) | None = ...
    ) -> str:
        ...

    def get_line_numbers(
        self,
        kind: str = ...,
        sep: str = ...,
    ) -> tuple[int, int] | str:
        ...

    def get_key_leading_comments(self) -> list[Comment]: ...
    def set_key_leading_comments(self, comments: list[Comment]) -> None: ...
    def add_key_leading_comment(self, comment: Comment) -> None: ...

    def get_key_trailing_comments(self) -> list[Comment]: ...
    def set_key_trailing_comments(self, comments: list[Comment]) -> None: ...
    def add_key_trailing_comment(self, comment: Comment) -> None: ...

    def get_value_leading_comments(self) -> list[Comment]: ...
    def set_value_leading_comments(self, comments: list[Comment]) -> None: ...
    def add_value_leading_comment(self, comment: Comment) -> None: ...

    def get_value_trailing_comments(self) -> list[Comment]: ...
    def set_value_trailing_comments(self, comments: list[Comment]) -> None: ...
    def add_value_trailing_comment(self, comment: Comment) -> None: ...

    def get_header_comments(self) -> list[Comment]: ...
    def set_header_comments(self, comments: list[Comment]) -> None: ...
    def add_header_comment(self, comment: Comment) -> None: ...

    def get_footer_comments(self) -> list[Comment]: ...
    def set_footer_comments(self, comments: list[Comment]) -> None: ...
    def add_footer_comment(self, comment: Comment) -> None: ...

    def get_spacing(self) -> dict[int | str, int]: ...
    def set_spacing(self, spacing: dict[int | str, int]) -> None: ...

    def get_sections(self) -> list[tuple[Callable[[Any], bool], list[Comment]]]: ...
    def set_sections(
        self, sections: list[tuple[Callable[[Any], bool], list[Comment]]]
    ) -> None: ...

# loads() {{{1
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

# load() {{{1
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

# dumps() {{{1
def dumps(
    obj: Any,
    *,
    width: int = ...,
    inline_level: int = ...,
    sort_keys: bool | Callable = ...,
    indent: int = ...,
    converters: dict[Type, Callable] | None = ...,
    default: str | Callable | None = ...,
    map_keys: dict[tuple[str | int, ...], Any] | Callable = ...,
    spacing: dict = ...,
) -> str:
    ...

# dump() {{{1
def dump(
    obj: Any,
    dest,
    **kwargs
) -> None: ...

# get_keys() {{{1
def get_keys(
    keys: tuple[str | int, ...],
    keymap: dict[tuple[str | int, ...], Location],
    original: bool = ...,
    strict: bool | str = ...,
    sep: str = ...,
) -> tuple[str | int, ...] | str:
    ...

# get_value() {{{1
def get_value(
    obj: str | list | dict | None,
    keys: tuple[str, ...],
) -> str | list | dict:
    ...

def get_location(
    keys: tuple[str | int, ...],
    keymap: dict[tuple[str | int, ...], Location],
) -> Location:
    ...

# get_line_numbers() {{{1
def get_line_numbers(
    keys: tuple[str | int, ...],
    keymap: dict[tuple[str | int, ...], Location],
    kind: str = ...,
    base: int = ...,
    strict: bool = ...,
    sep: str = ...,
) -> tuple[int, int] | str:
    ...

# annotate() {{{1
def annotate(
    keymap: dict[tuple[str | int, ...], Location],
    keys: tuple[str | int, ...],
    *,
    key_leading: list[Comment] = ...,
    key_trailing: list[Comment] = ...,
    value_leading: list[Comment] = ...,
    value_trailing: list[Comment] = ...,
    header: list[Comment] = ...,
    footer: list[Comment] = ...,
    sections: list[tuple[Callable[[Any], bool], list[Comment]]] = ...,
    spacing: dict[int | str, int] | None = ...,
) -> Location:
    ...

# keymap_to_jsonable() {{{1
def keymap_to_jsonable(
    keymap: dict[tuple[str | int, ...], Any],
) -> dict[str, Any]:
    ...

# keymap_from_jsonable() {{{1
def keymap_from_jsonable(
    data: dict[str, Any],
) -> dict[tuple[str | int, ...], Location]:
    ...
