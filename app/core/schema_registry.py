from __future__ import annotations

from typing import Any

from app.core.base import BaseMemory

_schemas_loaded = False


def _ensure_schemas_loaded() -> None:
    global _schemas_loaded
    if not _schemas_loaded:
        from app.core import schemas
        _ = schemas
        _schemas_loaded = True


def _get_all_subclasses(cls: type) -> list[type]:
    all_subclasses: list[type] = []
    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(_get_all_subclasses(subclass))
    return all_subclasses


def _discover_schemas() -> list[type[BaseMemory]]:
    _ensure_schemas_loaded()
    return _get_all_subclasses(BaseMemory)


class SchemaCollection:
    def __init__(self, schemas: list[type[BaseMemory]]) -> None:
        self._schemas = schemas

    def to_api_dict(self) -> list[dict[str, Any]]:
        return [
            {
                "name": schema.__name__,
                "fields": {
                    field_name: {
                        "type": str(field_info.annotation),
                        "required": field_info.is_required(),
                        "description": field_info.description,
                    }
                    for field_name, field_info in schema.model_fields.items()
                },
            }
            for schema in self._schemas
        ]

    def get_by_name(self, name: str) -> type[BaseMemory] | None:
        return next((s for s in self._schemas if s.__name__ == name), None)

    def get_names(self) -> list[str]:
        return [schema.__name__ for schema in self._schemas]

    def __iter__(self):
        return iter(self._schemas)

    def __len__(self) -> int:
        return len(self._schemas)


def get_schema(schema_name: str) -> type[BaseMemory] | None:
    schemas = _discover_schemas()
    return next((s for s in schemas if s.__name__ == schema_name), None)


def get_all_schemas() -> SchemaCollection:
    return SchemaCollection(_discover_schemas())


def get_schema_names() -> list[str]:
    return [schema.__name__ for schema in _discover_schemas()]
