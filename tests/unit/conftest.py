from __future__ import annotations

import uuid
from typing import Any

import pytest

from app.core.schemas import ConversationInsight, UserFact, UserPreference  # noqa: F401
from app.infrastructure.repository import MemoryRepository
from app.services.service import MemoryService
from tests.unit.mocks import MockStore


@pytest.fixture
def memory_service() -> MemoryService:
    storage: dict[str, dict[str, Any]] = {}
    mock_store = MockStore(storage)
    repository = MemoryRepository(store=mock_store)  # type: ignore[arg-type]
    return MemoryService(repository=repository)


@pytest.fixture
def test_user_id() -> str:
    return f"test-user-{uuid.uuid4().hex[:8]}"
