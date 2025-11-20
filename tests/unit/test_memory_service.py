from __future__ import annotations

import pytest

from app.infrastructure.models import Memory
from app.services.service import MemoryService


class TestMemoryServiceCreate:
    @pytest.mark.parametrize(
        "schema_type,content,expected_fields",
        [
            (
                "UserPreference",
                {"category": "ui", "preference": "dark mode", "importance": "high"},
                {"schema_type": "UserPreference", "category": "ui", "preference": "dark mode"},
            ),
            (
                "UserFact",
                {"fact_type": "professional", "content": "Software engineer", "tags": ["tech"]},
                {"schema_type": "UserFact", "fact_type": "professional"},
            ),
        ],
    )
    async def test_create_success(
        self,
        memory_service: MemoryService,
        test_user_id: str,
        schema_type: str,
        content: dict,
        expected_fields: dict,
    ):
        result = await memory_service.create(test_user_id, schema_type, content)

        assert "error" not in result
        assert "id" in result
        assert result["schema_type"] == expected_fields["schema_type"]
        for key, value in expected_fields.items():
            if key != "schema_type":
                assert result["content"][key] == value

    @pytest.mark.parametrize(
        "schema_type,content,expected_error",
        [
            ("InvalidSchema", {"test": "data"}, "Invalid schema type"),
            ("UserPreference", {"category": "ui"}, "Invalid content"),
        ],
    )
    async def test_create_failure(
        self, memory_service: MemoryService, test_user_id: str, schema_type: str, content: dict, expected_error: str
    ):
        result = await memory_service.create(test_user_id, schema_type, content)

        assert "error" in result
        assert expected_error in result["error"]


class TestMemoryServiceGetById:
    async def test_get_by_id_success(self, memory_service: MemoryService, test_user_id: str):
        content = {"category": "ui", "preference": "dark mode"}
        create_result = await memory_service.create(test_user_id, "UserPreference", content)
        memory_id = create_result["id"]

        memory = await memory_service.get_by_id(test_user_id, memory_id, "UserPreference")

        assert memory is not None
        assert isinstance(memory, Memory)
        assert memory.id == memory_id

    async def test_get_by_id_not_found(self, memory_service: MemoryService, test_user_id: str):
        memory = await memory_service.get_by_id(test_user_id, "non-existent-id", "UserPreference")
        assert memory is None

    async def test_get_by_id_without_schema_type(self, memory_service: MemoryService, test_user_id: str):
        content = {"category": "ui", "preference": "dark mode"}
        create_result = await memory_service.create(test_user_id, "UserPreference", content)
        memory_id = create_result["id"]

        memory = await memory_service.get_by_id(test_user_id, memory_id)

        assert memory is not None
        assert memory.id == memory_id


class TestMemoryServiceSearch:
    async def test_search_success(self, memory_service: MemoryService, test_user_id: str):
        content = {"category": "feature", "preference": "code completion"}
        await memory_service.create(test_user_id, "UserPreference", content)

        results = await memory_service.search(test_user_id, "code completion", limit=10)

        assert len(results) >= 1

    async def test_search_with_schema_type_filter(self, memory_service: MemoryService, test_user_id: str):
        await memory_service.create(test_user_id, "UserPreference", {"category": "ui", "preference": "dark"})
        await memory_service.create(test_user_id, "UserFact", {"fact_type": "hobby", "content": "photography"})

        results = await memory_service.search(test_user_id, "dark", schema_type="UserPreference")

        assert len(results) >= 1
        assert all(isinstance(m, Memory) for m in results)

    async def test_search_empty_query(self, memory_service: MemoryService, test_user_id: str):
        await memory_service.create(test_user_id, "UserPreference", {"category": "ui", "preference": "dark"})

        results = await memory_service.search(test_user_id, "", limit=10)

        assert len(results) >= 1


class TestMemoryServiceGetAll:
    async def test_get_all_success(self, memory_service: MemoryService, test_user_id: str):
        await memory_service.create(test_user_id, "UserPreference", {"category": "ui", "preference": "dark"})
        await memory_service.create(test_user_id, "UserFact", {"fact_type": "hobby", "content": "music"})

        results = await memory_service.get_all(test_user_id)

        assert len(results) >= 2

    async def test_get_all_with_schema_type_filter(self, memory_service: MemoryService, test_user_id: str):
        await memory_service.create(test_user_id, "UserPreference", {"category": "ui", "preference": "dark"})
        await memory_service.create(test_user_id, "UserFact", {"fact_type": "hobby", "content": "music"})

        results = await memory_service.get_all(test_user_id, schema_type="UserPreference")

        assert len(results) >= 1
        assert all(isinstance(m, Memory) for m in results)


class TestMemoryServiceDelete:
    async def test_delete_success(self, memory_service: MemoryService, test_user_id: str):
        content = {"category": "ui", "preference": "dark mode"}
        create_result = await memory_service.create(test_user_id, "UserPreference", content)
        memory_id = create_result["id"]

        success = await memory_service.delete(test_user_id, memory_id, "UserPreference")

        assert success is True

        memory = await memory_service.get_by_id(test_user_id, memory_id, "UserPreference")
        assert memory is None

    async def test_delete_not_found(self, memory_service: MemoryService, test_user_id: str):
        success = await memory_service.delete(test_user_id, "non-existent-id", "UserPreference")
        assert success is False

    async def test_delete_without_schema_type(self, memory_service: MemoryService, test_user_id: str):
        content = {"category": "ui", "preference": "dark mode"}
        create_result = await memory_service.create(test_user_id, "UserPreference", content)
        memory_id = create_result["id"]

        success = await memory_service.delete(test_user_id, memory_id)

        assert success is True


class TestMemoryServiceIntegration:
    async def test_full_crud_cycle(self, memory_service: MemoryService, test_user_id: str):
        content = {"category": "feature", "preference": "autocomplete", "importance": "high"}
        create_result = await memory_service.create(test_user_id, "UserPreference", content)
        memory_id = create_result["id"]
        assert memory_id is not None

        memory = await memory_service.get_by_id(test_user_id, memory_id, "UserPreference")
        assert memory is not None
        assert memory.id == memory_id

        results = await memory_service.search(test_user_id, "autocomplete")
        assert len(results) >= 1

        success = await memory_service.delete(test_user_id, memory_id, "UserPreference")
        assert success is True

        deleted_memory = await memory_service.get_by_id(test_user_id, memory_id, "UserPreference")
        assert deleted_memory is None
