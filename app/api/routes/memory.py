from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, Depends

from app.api.schemas import Response
from app.core.schema_registry import get_all_schemas
from app.services import MemoryService, get_memory_service

router = APIRouter(prefix="/memories", tags=["memories"])


@router.get("/schemas", description="사용 가능한 메모리 스키마 목록 조회")
async def list_schemas() -> Response:
    schemas = get_all_schemas()
    return Response(success=True, data={"schemas": schemas.to_api_dict()})


@router.get("/search", description="쿼리(사용자 질의)로 메모리 유사도 검색")
async def search_memories(
    user_id: str,
    query: str,
    schema_type: str | None = None,
    limit: int = 10,
    service: MemoryService = Depends(get_memory_service),
) -> Response:
    """쿼리로 메모리 검색"""
    memories = await service.search(user_id=user_id, query=query, schema_type=schema_type, limit=limit)

    return Response(
        success=True,
        data={
            "user_id": user_id,
            "query": query,
            "schema_type": schema_type,
            "memories": [memory.to_dict() for memory in memories],
            "count": len(memories),
        },
    )


@router.post("/", description="새 메모리 생성")
async def create_memory(
    user_id: str,
    schema_type: str,
    content: dict[str, Any] = Body(...),
    service: MemoryService = Depends(get_memory_service),
) -> Response:
    """메모리 생성"""
    result = await service.create(user_id=user_id, schema_type=schema_type, content=content)

    if "error" in result:
        return Response(success=False, error=result["error"])

    return Response(success=True, data=result)


@router.get("/", description="사용자의 모든 메모리 조회")
async def get_all_memories(
    user_id: str,
    schema_type: str | None = None,
    service: MemoryService = Depends(get_memory_service),
) -> Response:
    memories = await service.get_all(user_id=user_id, schema_type=schema_type)

    return Response(
        success=True,
        data={
            "user_id": user_id,
            "schema_type": schema_type,
            "memories": [memory.to_dict() for memory in memories],
            "count": len(memories),
        },
    )


@router.get("/{memory_id}", description="메모리 ID로 메모리 조회")
async def get_memory_by_id(
    memory_id: str,
    user_id: str,
    schema_type: str | None = None,
    service: MemoryService = Depends(get_memory_service),
) -> Response:
    memory = await service.get_by_id(user_id=user_id, memory_id=memory_id, schema_type=schema_type)

    if memory is None:
        return Response(success=False, error="Memory not found")

    return Response(success=True, data=memory.to_dict())


@router.delete("/{memory_id}", description="ID로 메모리 삭제")
async def delete_memory_by_id(
    memory_id: str,
    user_id: str,
    schema_type: str | None = None,
    service: MemoryService = Depends(get_memory_service),
) -> Response:
    success = await service.delete(user_id=user_id, memory_id=memory_id, schema_type=schema_type)

    if not success:
        return Response(success=False, error="Memory not found or deletion failed")

    return Response(success=True, data={"deleted": True, "memory_id": memory_id})
