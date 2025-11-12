from collections.abc import Callable
from functools import cached_property
from typing import Any, Literal, overload

from pydantic import BaseModel

from bear_dereth.models.frozen_models import FrozenDict

INVALID_NAME_PREFIXES: list[str] = ["xml"]

type IntLiteral = Literal["int", "integer"]

class Columns[T](BaseModel):
    name: str = ...
    type: str = ...
    default: T | None = None
    default_factory: Callable[..., T] | Any = None
    nullable: bool = False
    primary_key: bool | None = None
    autoincrement: bool | None = None

    @overload
    def __init__(
        self,
        name: str,
        type: IntLiteral,
        *,
        nullable: bool = False,
        primary_key: Literal[True],
        autoincrement: Literal[True],
    ) -> None: ...
    @overload
    def __init__(
        self,
        name: str,
        type: IntLiteral,
        default: int,
        *,
        nullable: bool = False,
        primary_key: Literal[True],
        autoincrement: Literal[True],
    ) -> None: ...
    @overload
    def __init__(
        self,
        name: str,
        type: str = ...,
        default: T = None,
        *,
        nullable: bool = False,
        primary_key: bool | None = None,
        autoincrement: Literal[False] | None = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        name: str,
        type: str = ...,
        *,
        default_factory: Callable[..., T],
        nullable: bool = False,
        primary_key: bool | None = None,
        autoincrement: Literal[False] | None = None,
    ) -> None: ...
    @overload
    def __init__(
        self,
        name: str,
        type: str = ...,
        *,
        default_factory: Callable[..., T],
        nullable: bool = False,
        primary_key: bool | None = None,
        autoincrement: Literal[True] | None = None,
    ) -> None: ...
    def __init__(
        self,
        name: str,
        type: str = ...,
        default: T | None = None,
        default_factory: Callable[..., T] | None = None,
        nullable: bool = False,
        primary_key: bool | None = None,
        autoincrement: bool | None = None,
    ) -> None: ...
    @cached_property
    def type_obj(self) -> type[T]: ...
    @classmethod
    def validate_name(cls, v: Any) -> str: ...
    @classmethod
    def validate_type(cls, v: Any) -> str: ...
    def validate_column_constraints(self) -> Columns: ...
    @property
    def is_int(self) -> bool: ...
    def get_default(self) -> T | None: ...
    def __hash__(self) -> int: ...
    def frozen_dump(self) -> FrozenDict: ...
    def render(self) -> dict[str, Any]: ...
    def items(self) -> list[tuple[str, Any]]: ...

NullColumn: Columns[None] = ...

# ruff: noqa: A002
