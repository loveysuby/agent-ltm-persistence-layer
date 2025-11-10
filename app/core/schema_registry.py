from __future__ import annotations

from typing import Any

from app.core.base import BaseMemory

MEMORY_SCHEMAS: dict[str, type[BaseMemory]] = {}


def register_schema(schema_class: type[BaseMemory]) -> None:
    MEMORY_SCHEMAS[schema_class.__name__] = schema_class


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
    return MEMORY_SCHEMAS.get(schema_name)


def get_all_schemas() -> SchemaCollection:
    return SchemaCollection(list(MEMORY_SCHEMAS.values()))


def get_schema_names() -> list[str]:
    return list(MEMORY_SCHEMAS.keys())
