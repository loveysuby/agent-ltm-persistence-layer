from __future__ import annotations

from typing import Any
from uuid import uuid4

from langgraph.store.postgres import AsyncPostgresStore
from langmem import create_memory_store_manager
from pydantic import BaseModel

from app.api.dependencies import get_database_conn_string
from app.config.settings import get_settings
from app.core.memory_schemas import ALL_MEMORY_SCHEMAS, SCHEMA_INSTRUCTIONS
from app.core.models import MemoryType


# refs: https://langchain-ai.github.io/langmem/guides/delayed_processing
class LangMemStore:
    def __init__(self):
        settings = get_settings()
        self.conn_string = get_database_conn_string()
        self._store_cm = None
        self.store: AsyncPostgresStore | None = None
        self.memory_manager = None
        self.structured_manager = None

    async def setup(self):
        if self.store is None:
            self._store_cm = AsyncPostgresStore.from_conn_string(self.conn_string)
            self.store = await self._store_cm.__aenter__()
            await self.store.setup()

            self.memory_manager = create_memory_store_manager(
                "gpt-4o-mini",
                namespace=("memories",),
                store=self.store,
            )

            self.structured_manager = create_memory_store_manager(
                "gpt-4o-mini",
                namespace=("structured_memories",),
                store=self.store,
                schemas=ALL_MEMORY_SCHEMAS,
                instructions=SCHEMA_INSTRUCTIONS,
            )

    async def aclose(self):
        if self._store_cm is not None:
            try:
                await self._store_cm.__aexit__(None, None, None)
            except Exception as e:
                print(f"Warning: failed to close LangMemStore cleanly: {e}")
            finally:
                self._store_cm = None
                self.store = None

    async def process_conversation(self, user_id: str, messages: list[dict[str, str]]):
        if self.store is None or self.memory_manager is None:
            return
        config = {"configurable": {"user_id": user_id, "memory_strategy": MemoryType.EPISODIC}, "store": self.store}
        extracted_memories = await self.memory_manager.ainvoke({"messages": messages}, config=config)

        for memory in extracted_memories:
            namespace = tuple(list(memory.get("namespace", ("memories",))) + [user_id])
            key = memory.get("key")
            value = memory.get("value")
            if key and value:
                await self.store.aput(namespace, key, value)

    async def search_memories(self, user_id: str, query: str, limit: int = 10) -> list[dict[str, Any]]:
        if self.store is None:
            return []
        namespace = ("memories", user_id)
        search_results = await self.store.asearch(namespace, query=query, limit=limit)
        return [
            {"id": item.key, "content": item.value.get("content", ""), "metadata": item.value}
            for item in search_results
        ]

    async def get_all_memories(self, user_id: str) -> list[dict[str, Any]]:
        if self.store is None:
            return []
        namespace = ("memories", user_id)
        all_items = await self.store.asearch(namespace, limit=100)
        return [
            {"id": item.key, "content": item.value.get("content", ""), "metadata": item.value} for item in all_items
        ]

    async def create_memory(self, user_id: str, content: str, metadata: dict[str, Any] | None = None) -> dict[str, Any]:
        if self.store is None:
            return {}
        namespace = ("memories", user_id)
        memory_data = {"content": content, "kind": "Memory"}
        if metadata:
            memory_data.update(metadata)
        memory_id = str(uuid4())
        await self.store.aput(namespace, memory_id, memory_data)
        return {"id": memory_id, "content": content, "metadata": metadata or {}}

    async def update_memory(self, user_id: str, memory_id: str, content: str) -> dict[str, Any] | None:
        if self.store is None:
            return None
        namespace = ("memories", user_id)
        existing = await self.store.aget(namespace, memory_id)
        if existing is None:
            return None
        updated_data = {**existing.value, "content": content}
        await self.store.aput(namespace, memory_id, updated_data)
        return {"id": memory_id, "content": content, "metadata": existing.value}

    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        if self.store is None:
            return False
        try:
            namespace = ("memories", user_id)
            self.store.delete(namespace, memory_id)
            return True
        except Exception:
            return False

    async def search_memories_with_filter(
        self, user_id: str, query: str, filter_dict: dict[str, Any] | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        if self.store is None:
            return []
        namespace = ("memories", user_id)
        search_results = await self.store.asearch(namespace, query=query, filter=filter_dict, limit=limit)
        return [
            {"id": item.key, "content": item.value.get("content", ""), "metadata": item.value}
            for item in search_results
        ]

    async def process_structured_conversation(
        self, user_id: str, messages: list[dict[str, str]]
    ) -> list[dict[str, Any]]:
        if self.store is None or self.structured_manager is None:
            return []
        config = {"configurable": {"user_id": user_id}, "store": self.store}
        result = await self.structured_manager.ainvoke({"messages": messages}, config=config)

        extracted_memories = []
        for memory in result:
            if isinstance(memory, dict):
                memory_dict = {
                    "id": memory.get("id", str(uuid4())),
                    "schema_type": memory.get("schema_type", "Unknown"),
                    "content": memory.get("content", memory),
                }
            else:
                memory_dict = {
                    "id": memory.id if hasattr(memory, "id") else str(uuid4()),
                    "schema_type": type(memory.content).__name__ if hasattr(memory, "content") else "Unknown",
                    "content": memory.content.model_dump() if isinstance(memory.content, BaseModel) else memory.content,
                }
            extracted_memories.append(memory_dict)

        return extracted_memories

    async def get_memory_by_id(
        self, user_id: str, memory_id: str, namespace_type: str = "memories"
    ) -> dict[str, Any] | None:
        if self.store is None:
            return None
        namespace = (namespace_type, user_id)
        result = await self.store.aget(namespace, memory_id)
        if result is None:
            return None
        return {"id": memory_id, "content": result.value.get("content", ""), "metadata": result.value}

    async def search_structured_memories(
        self, user_id: str, query: str, schema_type: str | None = None, limit: int = 10
    ) -> list[dict[str, Any]]:
        if self.store is None:
            return []
        namespace = ("structured_memories", user_id)

        filter_dict = {"schema_type": schema_type} if schema_type else None
        search_results = await self.store.asearch(namespace, query=query, filter=filter_dict, limit=limit)

        return [
            {
                "id": item.key,
                "schema_type": item.value.get("schema_type", "Unknown"),
                "content": item.value.get("content", {}),
                "metadata": item.value,
            }
            for item in search_results
        ]

    async def get_all_structured_memories(self, user_id: str, schema_type: str | None = None) -> list[dict[str, Any]]:
        if self.store is None:
            return []
        namespace = ("structured_memories", user_id)

        filter_dict = {"schema_type": schema_type} if schema_type else None
        all_items = await self.store.asearch(namespace, filter=filter_dict, limit=100)

        return [
            {
                "id": item.key,
                "schema_type": item.value.get("schema_type", "Unknown"),
                "content": item.value.get("content", {}),
                "metadata": item.value,
            }
            for item in all_items
        ]

    async def create_structured_memory(self, user_id: str, schema_type: str, content: dict[str, Any]) -> dict[str, Any]:
        if self.store is None:
            return {}

        from app.core.memory_schemas import ConversationInsight, UserFact, UserPreference

        schema_map = {
            "UserPreference": UserPreference,
            "UserFact": UserFact,
            "ConversationInsight": ConversationInsight,
        }

        if schema_type not in schema_map:
            return {"error": f"Invalid schema type: {schema_type}"}

        try:
            schema_class = schema_map[schema_type]
            validated_content = schema_class(**content)

            namespace = ("structured_memories", user_id)
            memory_id = str(uuid4())
            memory_data = {
                "kind": "StructuredMemory",
                "schema_type": schema_type,
                "content": validated_content.model_dump(),
            }

            await self.store.aput(namespace, memory_id, memory_data)

            return {
                "id": memory_id,
                "schema_type": schema_type,
                "content": validated_content.model_dump(),
            }
        except Exception as e:
            return {"error": str(e)}
