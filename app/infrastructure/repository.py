from __future__ import annotations

from typing import Any

from langgraph.store.postgres import AsyncPostgresStore

from app.core.namespace_builder import MemoryNamespaceBuilder
from app.infrastructure.store import get_store


class MemoryRepository:
    def __init__(self, store: AsyncPostgresStore | None = None):
        self._store = store

    async def _get_store(self) -> AsyncPostgresStore:
        if self._store is None:
            self._store = await get_store()
        return self._store

    async def save(self, user_id: str, schema_type: str, memory_id: str, value: dict[str, Any]) -> None:
        store = await self._get_store()
        namespace = MemoryNamespaceBuilder.for_memory(user_id, schema_type)
        await store.aput(namespace, memory_id, value)

    async def find_by_id(self, user_id: str, memory_id: str, schema_type: str | None = None) -> dict[str, Any] | None:
        store = await self._get_store()

        if schema_type:
            namespace = MemoryNamespaceBuilder.for_memory(user_id, schema_type)
            result = await store.aget(namespace, memory_id)
            return result.value if result else None
        else:
            # 모든 스키마 타입에서 검색
            from app.core.schema_registry import get_schema_names

            for schema_type_name in get_schema_names():
                namespace = MemoryNamespaceBuilder.for_memory(user_id, schema_type_name)
                result = await store.aget(namespace, memory_id)
                if result:
                    return result.value
        return None

    async def search(
        self, user_id: str, query: str, schema_type: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        store = await self._get_store()

        if schema_type:
            namespace = MemoryNamespaceBuilder.for_memory(user_id, schema_type)
            results = await store.asearch(namespace, query=query, limit=limit)
        else:
            # 모든 메모리 검색 (namespace prefix 사용)
            namespace = ("memory", user_id)
            # TODO:  filter로 schema_type이 있는 항목만 필터링 가능하지만, namespace 구조상 prefix 검색이 더 효율적
            results: SearchItem = await store.asearch(namespace, query=query, limit=limit)  # noqa: F821

        return [{"key": result.key, "value": result.value} for result in results]

    async def find_all(self, user_id: str, schema_type: str | None = None) -> list[dict[str, Any]]:
        return await self.search(user_id, query="", schema_type=schema_type, limit=1000)

    async def delete(self, user_id: str, memory_id: str, schema_type: str | None = None) -> bool:
        store = await self._get_store()

        if schema_type:
            # 특정 스키마 타입에서 삭제
            namespace = MemoryNamespaceBuilder.for_memory(user_id, schema_type)
            try:
                await store.adelete(namespace, memory_id)
                return True
            except Exception:
                return False
        else:
            # 모든 스키마 타입에서 검색하여 삭제
            from app.core.schema_registry import get_schema_names

            for schema_type_name in get_schema_names():
                namespace = MemoryNamespaceBuilder.for_memory(user_id, schema_type_name)
                try:
                    await store.adelete(namespace, memory_id)
                    return True
                except Exception:
                    continue
        return False
