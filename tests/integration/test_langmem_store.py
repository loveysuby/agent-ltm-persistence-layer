from __future__ import annotations

import uuid

import pytest

from app.infrastructure.memory.memory_manager import MemoryManager


@pytest.fixture
def test_user_id() -> str:
    return f"test-user-{uuid.uuid4().hex[:8]}"


class TestMemoryManager:
    @pytest.mark.asyncio
    async def test_store_initialization(self):
        store = MemoryManager()

        await store.setup()

        assert store.store is not None
        assert store.memory_manager is not None

    @pytest.mark.asyncio
    async def test_process_and_search_memories(self, test_user_id: str):
        store = MemoryManager()
        await store.setup()

        messages = [
            {"role": "user", "content": "My favorite color is blue"},
            {"role": "assistant", "content": "That's a nice color!"},
        ]

        await store.process_conversation(user_id=test_user_id, messages=messages)

        results = await store.search_memories(user_id=test_user_id, query="favorite color", limit=5)

        assert len(results) > 0
        assert any("blue" in str(r.get("content", "")).lower() for r in results)

    @pytest.mark.asyncio
    async def test_user_isolation(self):
        store = MemoryManager()
        await store.setup()

        user1_id = f"user1-{uuid.uuid4().hex[:8]}"
        user2_id = f"user2-{uuid.uuid4().hex[:8]}"

        await store.process_conversation(
            user_id=user1_id,
            messages=[
                {"role": "user", "content": "I like cats"},
                {"role": "assistant", "content": "Nice!"},
            ],
        )
        await store.process_conversation(
            user_id=user2_id,
            messages=[
                {"role": "user", "content": "I like dogs"},
                {"role": "assistant", "content": "Great!"},
            ],
        )

        user1_memories = await store.get_all_memories(user_id=user1_id)
        user2_memories = await store.get_all_memories(user_id=user2_id)

        assert len(user1_memories) > 0
        assert len(user2_memories) > 0
        user1_content = " ".join(str(m.get("content", "")) for m in user1_memories).lower()
        user2_content = " ".join(str(m.get("content", "")) for m in user2_memories).lower()
        assert "cats" in user1_content or "cat" in user1_content
        assert "dogs" in user2_content or "dog" in user2_content
