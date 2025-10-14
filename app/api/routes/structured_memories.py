from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from app.api.schemas import Response
from app.core.services import AgentService

router = APIRouter(prefix="/structured-memories", tags=["structured-memories"])


@router.post("/process")
async def process_structured_conversation(user_id: str, messages: list[dict[str, str]]) -> Response:
    service = AgentService(user_id=user_id)
    store = await service.get_store()

    extracted = await store.process_structured_conversation(user_id=user_id, messages=messages)

    return Response(success=True, data={"user_id": user_id, "extracted_memories": extracted, "count": len(extracted)})


@router.post("/create")
async def create_structured_memory(user_id: str, schema_type: str, content: dict[str, Any]) -> Response:
    service = AgentService(user_id=user_id)
    store = await service.get_store()

    result = await store.create_structured_memory(user_id=user_id, schema_type=schema_type, content=content)

    if "error" in result:
        return Response(success=False, error=result["error"])

    return Response(success=True, data=result)


@router.get("/{memory_id}")
async def get_memory_by_id(
    memory_id: str, user_id: str = Query(...), namespace_type: str = Query(default="structured_memories")
) -> Response:
    service = AgentService(user_id=user_id)
    store = await service.get_store()

    memory = await store.get_memory_by_id(user_id=user_id, memory_id=memory_id, namespace_type=namespace_type)

    if memory is None:
        return Response(success=False, error="Memory not found")

    return Response(success=True, data=memory)


@router.post("/search")
async def search_structured_memories(
    user_id: str, query: str, schema_type: str | None = None, limit: int = 10
) -> Response:
    service = AgentService(user_id=user_id)
    store = await service.get_store()

    memories = await store.search_structured_memories(
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


@router.get("/")
async def get_all_structured_memories(user_id: str = Query(...), schema_type: str | None = None) -> Response:
    service = AgentService(user_id=user_id)
    store = await service.get_store()

    memories = await store.get_all_structured_memories(user_id=user_id, schema_type=schema_type)

    return Response(
        success=True,
        data={"user_id": user_id, "schema_type": schema_type, "memories": memories, "count": len(memories)},
    )


@router.get("/schemas/list")
async def list_available_schemas() -> Response:
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
