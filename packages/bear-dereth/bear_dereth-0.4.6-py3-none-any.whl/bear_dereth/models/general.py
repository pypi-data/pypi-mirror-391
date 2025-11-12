"""A set of general-purpose Pydantic models and utilities."""

import json
from typing import Any

from pydantic import BaseModel, ConfigDict


class FrozenModel(BaseModel):
    """A Pydantic model that is immutable after creation."""

    model_config = ConfigDict(frozen=True, extra="forbid")


class ExtraIgnoreModel(BaseModel):
    """A Pydantic model that ignores extra fields."""

    model_config = ConfigDict(extra="ignore", arbitrary_types_allowed=True)


class LowRentPydanticMixin:
    """A mixin that provides Pydantic-like dump methods for non-Pydantic classes."""

    def model_dump(
        self,
        *,
        exclude_none: bool = False,
        exclude: set[str] | tuple[str] | list[str] | None = None,
    ) -> dict[str, Any]:
        """Return a dictionary representation of the model.

        Args:
            exclude_none: If True, exclude None values from the output.

        Returns:
            A dictionary containing the model's attributes.
        """
        data: dict[str, Any] = {key: value for key, value in self.__dict__.items() if not key.startswith("_")}

        if exclude_none:
            data = {k: v for k, v in data.items() if v is not None}

        if exclude is not None:
            for key in exclude:
                data.pop(key, None)

        return data

    def model_dump_json(self, *, exclude_none: bool = False, indent: int | None = None) -> str:
        """Return a JSON string representation of the model.

        Args:
            exclude_none: If True, exclude None values from the output.
            indent: Number of spaces for indentation (None for compact output).

        Returns:
            A JSON string representation of the model.
        """
        return json.dumps(self.model_dump(exclude_none=exclude_none), indent=indent)
