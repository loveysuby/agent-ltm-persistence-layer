from __future__ import annotations

from app.core.base import MemoryType


class MemoryNamespaceBuilder:
    """
    langchain BaseStore 내 store 테이블에, prefix 로 설정됩니다.
    prefix는 유사도 search index, filtering query로 생성됨
    """

    @staticmethod
    def for_memory(user_id: str, schema_type: str, memory_type: MemoryType | None = None) -> tuple[str, ...]:
        if memory_type:
            return "memory", memory_type.value, user_id, schema_type
        return "memory", user_id, schema_type
