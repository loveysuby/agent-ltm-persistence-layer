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


class TestStructuredMemoryEndpoints:
    def test_list_schemas(self, client: TestClient):
        response = client.get("/structured-memories/schemas/list")

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "schemas" in data["data"]
        assert len(data["data"]["schemas"]) == 3

    def test_create_structured_memory_user_preference(self, client: TestClient, test_user_id: str):
        response = client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "UserPreference"},
            json={"category": "ui", "preference": "dark mode", "importance": "high"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "id" in data["data"]
        assert data["data"]["schema_type"] == "UserPreference"

    def test_create_structured_memory_user_fact(self, client: TestClient, test_user_id: str):
        response = client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "UserFact"},
            json={"fact_type": "hobby", "content": "Enjoys photography", "tags": ["photography", "art"]},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["schema_type"] == "UserFact"

    def test_create_with_invalid_schema_type(self, client: TestClient, test_user_id: str):
        response = client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "InvalidSchema"},
            json={"test": "data"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is False
        assert "error" in data

    def test_get_memory_by_id(self, client: TestClient, test_user_id: str):
        create_response = client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "UserPreference"},
            json={"category": "language", "preference": "English"},
        )

        assert create_response.status_code == 200
        memory_id = create_response.json()["data"]["id"]

        get_response = client.get(
            f"/structured-memories/{memory_id}",
            params={"user_id": test_user_id, "namespace_type": "structured_memories"},
        )

        assert get_response.status_code == 200
        data = get_response.json()
        assert data["success"] is True
        assert data["data"]["id"] == memory_id

    def test_search_structured_memories(self, client: TestClient, test_user_id: str):
        client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "UserPreference"},
            json={"category": "feature", "preference": "code completion"},
        )

        response = client.post(
            "/structured-memories/search", params={"user_id": test_user_id, "query": "code completion", "limit": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "memories" in data["data"]

    def test_get_all_structured_memories(self, client: TestClient, test_user_id: str):
        client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "ConversationInsight"},
            json={"topic": "Python programming", "key_points": ["Discussed async", "Covered testing"]},
        )

        response = client.get("/structured-memories/", params={"user_id": test_user_id})

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "memories" in data["data"]
        assert data["data"]["count"] >= 1

    def test_get_all_filtered_by_schema_type(self, client: TestClient, test_user_id: str):
        client.post(
            "/structured-memories/create",
            params={"user_id": test_user_id, "schema_type": "UserPreference"},
            json={"category": "ui", "preference": "dark mode"},
        )

        response = client.get(
            "/structured-memories/", params={"user_id": test_user_id, "schema_type": "UserPreference"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
