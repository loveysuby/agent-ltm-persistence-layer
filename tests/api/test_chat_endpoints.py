from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from main import app


@pytest.fixture
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture
def test_user_id() -> str:
    return f"test-user-{uuid.uuid4().hex[:8]}"


@pytest.fixture
def test_thread_id() -> str:
    return f"thread-{uuid.uuid4().hex[:8]}"


class TestChatAPI:
    def test_chat_endpoint_basic(self, client: TestClient, test_user_id: str, test_thread_id: str):
        response = client.post(
            "/chat",
            json={"user_id": test_user_id, "message": "Hello, I am testing", "thread_id": test_thread_id},
        )

        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        assert "thread_id" in data
        assert data["thread_id"] == test_thread_id

    def test_chat_endpoint_default_thread(self, client: TestClient, test_user_id: str):
        response = client.post("/chat", json={"user_id": test_user_id, "message": "Hello without thread"})

        assert response.status_code == 200
        data = response.json()
        assert data["thread_id"] == "default"

    def test_get_memories_endpoint(self, client: TestClient, test_user_id: str):
        client.post(
            "/chat", json={"user_id": test_user_id, "message": "I like machine learning", "thread_id": "test-thread"}
        )

        response = client.get(f"/chat/{test_user_id}/memories")

        assert response.status_code == 200
        data = response.json()
        assert "user_id" in data
        assert "memories" in data
        assert "count" in data
        assert data["user_id"] == test_user_id
        assert isinstance(data["memories"], list)
