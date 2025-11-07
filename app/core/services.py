from __future__ import annotations

from typing import Any

from app.config.settings import get_pg_store_conn_string
from app.core.namespace_builder import MemoryNamespaceBuilder
from app.infrastructure.store import get_store


class MemoryManager:
    def __init__(self):
        self._database_url: str = get_pg_store_conn_string()

    async def chat(self, message: str, thread_id: str = "default") -> dict[str, Any]:
        store = await get_store()
        namespace = MemoryNamespaceBuilder.for_episodic_memory(thread_id)
        memories = await store.asearch(namespace, query=message, limit=3)
        return {"response": "This is a placeholder response.", "memories": memories}

    async def get_memories(self, key: str) -> tuple[str, Any]:
        store = await get_store()
        # TODO : request user id getter middleware
        user_id = "TEST"
        namespace = MemoryNamespaceBuilder.for_user(user_id)
        results = await store.aget(namespace, key)

        return results.key, results.value
