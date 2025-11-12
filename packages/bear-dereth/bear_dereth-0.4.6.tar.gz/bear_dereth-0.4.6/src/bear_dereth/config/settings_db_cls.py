"""Base settings model for Pydantic models used in settings storage."""

from __future__ import annotations

from typing import Any

from bear_dereth.datastore.base_settings import BaseSettingsModel
from bear_dereth.datastore.columns import Columns
from bear_dereth.datastore.record import Record


class SettingsModel(BaseSettingsModel):
    """Pydantic model for settings storage."""

    id: Columns[int] = Columns[int](name="id", type="int", default=0, primary_key=True, autoincrement=True)
    key: Columns[str] = Columns[str](name="key", nullable=False, default="")
    value: Columns[str] = Columns[str](name="value", nullable=False, default="")
    type: Columns[str] = Columns[str](name="type", nullable=False, default="str")

    def to_record(self, key: str, value: Any, cls_type: object) -> Record:
        """Convert the settings model instance to a Record."""
        return Record(
            {
                "id": 0,
                "key": key,
                "value": value,
                "type": cls_type.__name__ if hasattr(cls_type, "__name__") else str(cls_type),  # type: ignore[arg-type]
            }
        )
