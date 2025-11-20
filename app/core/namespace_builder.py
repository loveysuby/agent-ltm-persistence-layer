from __future__ import annotations

from app.core.base import MemoryType


# TODO : make type assured (or implemented data-type)
class MemoryNamespaceBuilder:
    @staticmethod
    def for_memory(user_id: str, schema_type: str, memory_type: MemoryType | None = None) -> tuple[str, ...]:
        if memory_type:
            return (
                memory_type.value,
                user_id,
                "memory",
                schema_type,
            )
        return "memory", user_id, schema_type
