from __future__ import annotations

from fastapi import APIRouter

from app.api.schemas import MemoryCreateRequest, MemorySearchRequest, MemoryUpdateRequest, Response
from app.core.services import AgentService

router = APIRouter(prefix="/memories", tags=["memories"])


@router.post("")
async def create_memory(request: MemoryCreateRequest) -> Response:
    service = AgentService(user_id=request.user_id)
    store = await service.get_store()
    memory = await store.create_memory(user_id=request.user_id, content=request.content, metadata=request.metadata)
    return Response(success=True, data=memory)


@router.put("/{memory_id}")
async def update_memory(memory_id: str, request: MemoryUpdateRequest) -> Response:
    service = AgentService(user_id=request.user_id)
    store = await service.get_store()
    memory = await store.update_memory(user_id=request.user_id, memory_id=memory_id, content=request.content)
    if memory is None:
        return Response(success=False, error="Memory not found")
    return Response(success=True, data=memory)


@router.delete("/{memory_id}")
async def delete_memory(memory_id: str, user_id: str) -> Response:
    service = AgentService(user_id=user_id)
    store = await service.get_store()
    success = await store.delete_memory(user_id=user_id, memory_id=memory_id)
    return Response(success=success, data={"deleted": success})


@router.post("/search")
async def search_memories(request: MemorySearchRequest) -> Response:
    service = AgentService(user_id=request.user_id)
    store = await service.get_store()
    memories = await store.search_memories_with_filter(
        user_id=request.user_id, query=request.query, filter_dict=request.filter, limit=request.limit
    )
    return Response(success=True, data={"memories": memories, "count": len(memories)})
