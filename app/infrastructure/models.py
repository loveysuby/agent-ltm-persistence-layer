from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class Memory:
    id: str
    user_id: str
    schema_type: str
    content: dict[str, Any]
    namespace: tuple[str, ...]

    @classmethod
    def from_store_result(cls, key: str, value: dict[str, Any], namespace: tuple[str, ...]) -> Memory:
        return cls(
            id=key,
            user_id=namespace[1] if len(namespace) > 1 else "",
            schema_type=value.get("schema_type", ""),
            content=value.get("schema", value.get("content", {})),
            namespace=namespace,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "schema_type": self.schema_type,
            "content": self.content,
        }
