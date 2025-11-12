"""A module defining the Columns model for representing table columns."""

from __future__ import annotations

from collections.abc import Callable  # noqa: TC003
from contextlib import suppress
from functools import cached_property
import re
from typing import TYPE_CHECKING, Any, Literal

from funcy_bear.type_stuffs.builtin_tools import type_name
from pydantic import Field, field_validator, model_validator

from bear_dereth.models.frozen_models import FrozenDict, freeze
from bear_dereth.models.general import ExtraIgnoreModel

if TYPE_CHECKING:
    from pydantic._internal._generics import PydanticGenericMetadata

INVALID_NAME_PREFIXES: list[str] = ["xml"]
type IntLiteral = Literal["int", "integer"]
NOTSET_SENTINEL = "__NOTSET__"


class Columns[T](ExtraIgnoreModel):
    """A model to represent columns in a table."""

    name: str
    type: str = NOTSET_SENTINEL
    default: T | None = None
    default_factory: Callable[..., T] | None = Field(default=None, exclude=True)
    nullable: bool = False
    primary_key: bool | None = None
    autoincrement: bool | None = None

    @cached_property
    def type_obj(self) -> type:
        """Get the Python type object for the column's type."""
        from funcy_bear.type_stuffs.conversions import str_to_type  # noqa: PLC0415

        return str_to_type(self.type)

    def model_post_init(self, context: Any) -> None:
        """Post-initialization to inspect generic metadata."""
        if self.type == NOTSET_SENTINEL:
            metadata: PydanticGenericMetadata = self.__class__.__pydantic_generic_metadata__
            if metadata and metadata.get("args"):
                self.type = type_name(next(iter(metadata["args"])))
        return super().model_post_init(context)

    @field_validator("name", mode="before")
    @classmethod
    def validate_name(cls, v: Any) -> str:
        """Validate column name format."""
        if not isinstance(v, str):
            raise TypeError(f"Column name must be a string, got {type(v).__name__}.")

        if not v or not v.strip():
            raise ValueError("Column name cannot be empty or whitespace.")

        if not v[0].isalpha() and v[0] != "_":
            raise ValueError(f"Column name must start with a letter or underscore, not '{v[0]}'.")

        if " " in v:
            raise ValueError("Column name cannot contain spaces. Use underscores instead.")

        for prefix in INVALID_NAME_PREFIXES:
            if v.lower().startswith(prefix):
                raise ValueError(
                    f"Column name cannot start with '{prefix}' (case insensitive) due to format restrictions."
                )

        return v

    @field_validator("type", mode="before")
    @classmethod
    def validate_type(cls, v: Any) -> str:
        """Ensure the type is stored as a string."""
        if isinstance(v, str) and v == "integer":
            v = "int"
        if isinstance(v, str):
            with suppress(Exception):
                v = re.sub(r"^Columns\[(.+)\]$", r"\1", v)
            return v
        if isinstance(v, type):
            return type_name(v)
        raise TypeError("Type must be a string or a type.")

    @field_validator("default_factory", mode="before")
    @classmethod
    def validate_default_factory(cls, v: Any) -> Callable[..., Any] | None:
        """Ensure default_factory is callable if provided."""
        if v is None:
            return None
        if not callable(v):
            raise TypeError("default_factory must be callable.")
        return v

    @model_validator(mode="after")
    def validate_defaults_mutually_exclusive(self) -> Columns:
        """Ensure default and default_factory are mutually exclusive."""
        if self.default is not None and self.default_factory is not None:
            raise ValueError("Cannot specify both 'default' and 'default_factory'.")
        return self

    @model_validator(mode="after")
    def validate_column_constraints(self) -> Columns:
        """Validate column constraints."""
        if self.primary_key is True and self.nullable is True:
            raise ValueError(f"Primary key column '{self.name}' cannot be nullable.")
        if self.autoincrement is True:
            if self.primary_key is not True:
                raise ValueError(
                    f"Autoincrement can only be set on primary key columns, but column '{self.name}' is not a primary key."
                )
            if not self.is_int:
                raise ValueError(
                    f"Autoincrement can only be set on integer columns, but column '{self.name}' has type '{self.type}'."
                )
        return self

    def get_default(self) -> T | None:
        """Get the default value for the column.

        Returns:
            The default value if set, the result of default_factory if callable,
            or None if neither is provided.
        """
        if self.default is not None:
            return self.default
        if self.default_factory is not None:
            return self.default_factory()
        return None

    @property
    def is_int(self) -> bool:
        """Check if the column type is integer."""
        return self.type.lower() in {"int", "integer"}

    def frozen_dump(self) -> FrozenDict:
        """Return a frozen representation of the column."""
        return freeze(self.model_dump(exclude_none=True))

    def render(self) -> dict[str, Any]:
        """Render the column as a dictionary."""
        return self.model_dump(exclude_none=True)

    def items(self) -> list[tuple[str, Any]]:
        """Return items for the column."""
        return list(self.render().items())

    def __hash__(self) -> int:
        """Hash the column based on its attributes."""
        return hash((self.name, self.type, self.nullable, self.primary_key, self.autoincrement))


NullColumn: Columns[None] = Columns(name="NULL", type="null", nullable=True, default=None)
