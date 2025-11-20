from __future__ import annotations

import uuid
from typing import Any

from app.core.schema_registry import get_schema, get_schema_names
from app.infrastructure.models import Memory
from app.infrastructure.repository import MemoryRepository


class MemoryService:
    def __init__(self, repository: MemoryRepository | None = None):
        self._repository = repository or MemoryRepository()

    async def create(self, user_id: str, schema_type: str, content: dict[str, Any]) -> dict[str, Any]:
        schema_class = get_schema(schema_type)
        if schema_class is None:
            return {"error": f"Invalid schema type: {schema_type}. Available types: {', '.join(get_schema_names())}"}

        try:
            memory_instance = schema_class(**content)
        except Exception as e:
            return {"error": f"Invalid content for schema {schema_type}: {str(e)}"}

        # 저장할 데이터 구성
        memory_id = str(uuid.uuid4())
        value = {
            "schema_type": schema_type,
            "schema": memory_instance.model_dump(),
            "content": content,
        }

        # 저장
        await self._repository.save(user_id, schema_type, memory_id, value)

        return {
            "id": memory_id,
            "schema_type": schema_type,
            "content": memory_instance.model_dump(),
        }

    async def get_by_id(self, user_id: str, memory_id: str, schema_type: str | None = None) -> Memory | None:
        result = await self._repository.find_by_id(user_id, memory_id, schema_type)
        if result is None:
            return None

        # namespace는 결과에서 schema_type을 추출하여 구성
        result_schema_type = schema_type or result.get("schema_type")
        namespace = self._build_namespace(user_id, result_schema_type)
        return Memory.from_store_result(memory_id, result, namespace)

    async def search(self, user_id: str, query: str, schema_type: str | None = None, limit: int = 10) -> list[Memory]:
        results = await self._repository.search(user_id, query, schema_type, limit)

        # BaseStore의 결과를 Memory 엔티티로 변환
        memories = []
        for result in results:
            memory_data = result["value"]
            memory_id = result["key"]

            result_schema_type = memory_data.get("schema_type") or schema_type
            namespace = self._build_namespace(user_id, result_schema_type)

            memories.append(Memory.from_store_result(memory_id, memory_data, namespace))  # type: ignore[arg-type]

        return memories

    async def get_all(self, user_id: str, schema_type: str | None = None) -> list[Memory]:
        """
        사용자의 모든 메모리를 조회합니다.

        Args:
            user_id: 사용자 ID
            schema_type: 스키마 타입 필터 (None이면 모든 타입)

        Returns:
            Memory 인스턴스 리스트
        """
        return await self.search(user_id, query="", schema_type=schema_type, limit=1000)

    async def delete(self, user_id: str, memory_id: str, schema_type: str | None = None) -> bool:
        """
        메모리를 삭제합니다.

        Args:
            user_id: 사용자 ID
            memory_id: 메모리 ID
            schema_type: 스키마 타입 (None이면 모든 타입에서 검색하여 삭제)

        Returns:
            삭제 성공 여부
        """
        return await self._repository.delete(user_id, memory_id, schema_type)

    def _build_namespace(self, user_id: str, schema_type: str | None) -> tuple[str, ...]:
        """
        네임스페이스를 구성합니다.

        Args:
            user_id: 사용자 ID
            schema_type: 스키마 타입

        Returns:
            네임스페이스 tuple
        """
        if schema_type:
            from app.core.namespace_builder import MemoryNamespaceBuilder

            return MemoryNamespaceBuilder.for_memory(user_id, schema_type)
        return "memory", user_id
