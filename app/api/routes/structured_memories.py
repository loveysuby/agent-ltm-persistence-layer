from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends

from app.api.schemas import Response
from app.infrastructure.memory.memory_manager import MemoryManager
from app.infrastructure.memory.standalone_structured_memory import get_memory_manager

router = APIRouter(prefix="/memories", tags=["json-memories"])


@router.get("/schemas")
async def list_schemas() -> Response:
    """사용 가능한 메모리 스키마 목록 조회"""
    from app.core.memory_schemas import ALL_MEMORY_SCHEMAS

    schemas_info = []
    for schema in ALL_MEMORY_SCHEMAS:
        schema_dict = {
            "name": schema.__name__,
            "fields": {
                field_name: {
                    "type": str(field_info.annotation),
                    "required": field_info.is_required(),
                    "description": field_info.description,
                }
                for field_name, field_info in schema.model_fields.items()
            },
        }
        schemas_info.append(schema_dict)

    return Response(success=True, data={"schemas": schemas_info})


@router.get("/search")
async def search_memories(
    user_id: str,
    query: str,
    schema_type: str | None = None,
    limit: int = 10,
    manager: MemoryManager = Depends(get_memory_manager),
) -> Response:
    """쿼리로 메모리 검색"""
    memories = await manager.search_structured_memories(
        user_id=user_id, query=query, schema_type=schema_type, limit=limit
    )

    return Response(
        success=True,
        data={
            "user_id": user_id,
            "query": query,
            "schema_type": schema_type,
            "memories": memories,
            "count": len(memories),
        },
    )


@router.post("/")
async def create_memory(
    user_id: str,
    schema_type: str,
    content: dict[str, Any] = Body(...),
    manager: MemoryManager = Depends(get_memory_manager),
) -> Response:
    """구조화된 메모리 생성"""
    result = await manager.create_structured_memory(user_id=user_id, schema_type=schema_type, content=content)

    if "error" in result:
        return Response(success=False, error=result["error"])

    return Response(success=True, data=result)


@router.get("/")
async def get_all_memories(
    user_id: str,
    schema_type: str | None = None,
    manager: MemoryManager = Depends(get_memory_manager),
) -> Response:
    memories = await manager.get_all_structured_memories(user_id=user_id, schema_type=schema_type)

    return Response(
        success=True,
        data={"user_id": user_id, "schema_type": schema_type, "memories": memories, "count": len(memories)},
    )


@router.get("/{memory_id}")
async def get_memory(
    memory_id: str,
    user_id: str,
    manager: MemoryManager = Depends(get_memory_manager),
) -> Response:
    """ID로 메모리 조회"""
    memory = await manager.get_memory_by_id(user_id=user_id, memory_id=memory_id, namespace_type="structured_memories")

    if memory is None:
        return Response(success=False, error="Memory not found")

    return Response(success=True, data=memory)
