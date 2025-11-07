from __future__ import annotations

import uuid

import pytest

from app.core.services import MemoryManager


@pytest.fixture
def test_user_id() -> str:
    return f"test-user-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_thread_id() -> str:
    return uuid.uuid4().hex[:8]


@pytest.fixture
def mock_agent_service(test_user_id: str):
    return MemoryManager(user_id=test_user_id)


@pytest.mark.asyncio
class TestAgentService:
    async def test_memory_store_isolation(self, test_user_id: str):
        service1 = MemoryManager(user_id=test_user_id)
        service2 = MemoryManager(user_id=test_user_id)

        store1 = await service1.get_store()
        store2 = await service2.get_store()

        assert store1 is not store2

    @pytest.mark.integration
    async def test_thread_continuity(self, mock_agent_service, test_thread_id: str):
        t1, t2 = f"t1-{test_thread_id}", f"t2-{test_thread_id}"
        first_result = await mock_agent_service.chat(message="My favorite number is 42", thread_id=t1)
        second_result = await mock_agent_service.chat(message="What is my favorite number?", thread_id=t2)

        assert "42" in second_result["response"] or "forty" in second_result["response"].lower()

    @pytest.mark.integration
    async def test_memory_persistence_across_threads(self, test_user_id, test_thread_id):
        service = MemoryManager(user_id=test_user_id)
        t1, t2 = f"t1-{test_thread_id}", f"t2-{test_thread_id}"

        await service.chat(message="I am a software engineer", thread_id=t1)
        result = await service.chat(message="What is my profession?", thread_id=t2)

        assert (
            "engineer" in result["response"].lower()
            or "software" in result["response"].lower()
            or "developer" in result["response"].lower()
        )
