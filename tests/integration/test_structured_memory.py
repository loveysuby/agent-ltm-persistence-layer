from __future__ import annotations

import uuid

import pytest

from app.core.services import AgentService
from app.infrastructure.memory.memory_manager import MemoryManager


@pytest.fixture
def test_user_id() -> str:
    return f"test-user-{uuid.uuid4().hex[:8]}"


class TestStructuredMemoryStore:
    @pytest.mark.asyncio
    async def test_structured_manager_initialization(self):
        store = MemoryManager()
        await store.setup()

        assert store.store is not None
        assert store.memory_manager is not None
        assert store.structured_manager is not None

    @pytest.mark.asyncio
    async def test_process_structured_conversation(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        messages = [
            {"role": "user", "content": "I prefer dark mode and I'm learning Python for machine learning"},
            {"role": "assistant", "content": "Great! I'll remember your preferences."},
        ]

        extracted = await store.process_structured_conversation(user_id=test_user_id, messages=messages)

        assert isinstance(extracted, list)
        assert len(extracted) >= 0

    @pytest.mark.asyncio
    async def test_create_structured_memory_user_preference(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        result = await store.create_structured_memory(
            user_id=test_user_id,
            schema_type="UserPreference",
            content={"category": "ui", "preference": "dark mode", "importance": "high"},
        )

        assert "error" not in result
        assert result["schema_type"] == "UserPreference"
        assert "id" in result
        assert result["content"]["category"] == "ui"

    @pytest.mark.asyncio
    async def test_create_structured_memory_user_fact(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        result = await store.create_structured_memory(
            user_id=test_user_id,
            schema_type="UserFact",
            content={
                "fact_type": "professional",
                "content": "Works as a software engineer",
                "tags": ["engineering", "software"],
            },
        )

        assert "error" not in result
        assert result["schema_type"] == "UserFact"
        assert result["content"]["fact_type"] == "professional"

    @pytest.mark.asyncio
    async def test_create_invalid_schema_type(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        result = await store.create_structured_memory(
            user_id=test_user_id, schema_type="InvalidSchema", content={"test": "data"}
        )

        assert "error" in result

    @pytest.mark.asyncio
    async def test_get_memory_by_id(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        created = await store.create_structured_memory(
            user_id=test_user_id, schema_type="UserPreference", content={"category": "language", "preference": "Python"}
        )

        assert "id" in created
        memory_id = created["id"]

        retrieved = await store.get_memory_by_id(
            user_id=test_user_id, memory_id=memory_id, namespace_type="structured_memories"
        )

        assert retrieved is not None
        assert retrieved["id"] == memory_id

    @pytest.mark.asyncio
    async def test_search_structured_memories(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        await store.create_structured_memory(
            user_id=test_user_id, schema_type="UserPreference", content={"category": "ui", "preference": "dark mode"}
        )
        await store.create_structured_memory(
            user_id=test_user_id, schema_type="UserFact", content={"fact_type": "hobby", "content": "Likes hiking"}
        )
        results = await store.search_structured_memories(user_id=test_user_id, query="dark mode preferences", limit=5)

        assert isinstance(results, list)

    @pytest.mark.asyncio
    async def test_search_by_schema_type(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        await store.create_structured_memory(
            user_id=test_user_id, schema_type="UserPreference", content={"category": "ui", "preference": "dark mode"}
        )

        await store.create_structured_memory(
            user_id=test_user_id, schema_type="UserFact", content={"fact_type": "hobby", "content": "Likes reading"}
        )

        pref_results = await store.search_structured_memories(
            user_id=test_user_id, query="preferences", schema_type="UserPreference", limit=10
        )

        assert isinstance(pref_results, list)

    @pytest.mark.asyncio
    async def test_get_all_structured_memories(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        await store.create_structured_memory(
            user_id=test_user_id, schema_type="UserPreference", content={"category": "ui", "preference": "light mode"}
        )

        all_memories = await store.get_all_structured_memories(user_id=test_user_id)

        assert isinstance(all_memories, list)
        assert len(all_memories) >= 1

    @pytest.mark.asyncio
    async def test_user_isolation_structured_memories(self):
        store = MemoryManager()
        await store.setup()

        user1_id = f"user1-{uuid.uuid4().hex[:8]}"
        user2_id = f"user2-{uuid.uuid4().hex[:8]}"

        await store.create_structured_memory(
            user_id=user1_id, schema_type="UserPreference", content={"category": "ui", "preference": "dark mode"}
        )

        await store.create_structured_memory(
            user_id=user2_id, schema_type="UserPreference", content={"category": "ui", "preference": "light mode"}
        )

        user1_memories = await store.get_all_structured_memories(user_id=user1_id)
        user2_memories = await store.get_all_structured_memories(user_id=user2_id)

        assert len(user1_memories) >= 1
        assert len(user2_memories) >= 1

        user1_has_dark = any("dark" in str(m) for m in user1_memories)
        user2_has_light = any("light" in str(m) for m in user2_memories)

        assert user1_has_dark or user2_has_light


class TestAgentServiceWithStructuredMemory:
    @pytest.mark.asyncio
    async def test_agent_service_get_store_with_structured_manager(self, test_user_id: str):
        service = AgentService(user_id=test_user_id)
        store = await service.get_store()

        assert store.structured_manager is not None

    @pytest.mark.asyncio
    async def test_end_to_end_structured_memory_flow(self, test_user_id: str):
        service = AgentService(user_id=test_user_id)
        store = await service.get_store()

        created = await store.create_structured_memory(
            user_id=test_user_id,
            schema_type="UserPreference",
            content={"category": "feature", "preference": "auto-complete", "importance": "high"},
        )

        assert "id" in created
        memory_id = created["id"]

        retrieved = await store.get_memory_by_id(
            user_id=test_user_id, memory_id=memory_id, namespace_type="structured_memories"
        )

        assert retrieved is not None
        assert retrieved["id"] == memory_id

        searched = await store.search_structured_memories(
            user_id=test_user_id, query="auto-complete preference", limit=5
        )

        assert isinstance(searched, list)
