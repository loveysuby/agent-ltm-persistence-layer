from __future__ import annotations

import uuid
from collections.abc import Generator
from unittest.mock import AsyncMock

import pytest
from fastapi.testclient import TestClient

from app.core.schemas import ConversationInsight, UserFact, UserPreference  # noqa: F401
from app.main import app
from app.services import get_memory_service
from app.services.service import MemoryService as MemoryServiceClass


@pytest.fixture
def mock_repository() -> AsyncMock:
    """
    mock_repo.find_by_id.return_value = {"id": "123", "schema_type": "UserPreference"}
    mock_repo.search.return_value = [{"key": "123", "value": {...}}]
    """
    mock_repo = AsyncMock()
    # 기본 반환값 설정 (필요에 따라 각 테스트에서 오버라이드)
    mock_repo.save.return_value = None
    mock_repo.find_by_id.return_value = None
    mock_repo.search.return_value = []
    mock_repo.find_all.return_value = []
    mock_repo.delete.return_value = False
    return mock_repo


@pytest.fixture
def mock_memory_service(mock_repository: AsyncMock) -> MemoryServiceClass:
    return MemoryServiceClass(repository=mock_repository)


# TODO : Need refactor with TestClient fixture in app/tests/conftest.py
@pytest.fixture
def client(mock_memory_service: MemoryServiceClass) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_memory_service] = lambda: mock_memory_service
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def test_user_id() -> str:
    return f"test-user-{uuid.uuid4().hex[:8]}"
