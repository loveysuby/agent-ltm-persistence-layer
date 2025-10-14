from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.services import AgentService

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    user_id: str
    thread_id: str = Field(default="default", description="Thread ID for conversation continuity")


class ChatResponse(BaseModel):
    response: Any
    thread_id: str


class MemoriesResponse(BaseModel):
    user_id: str
    memories: list[dict[str, Any]]
    count: int


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    service = AgentService(user_id=request.user_id)
    result = await service.chat(request.message, thread_id=request.thread_id)

    return ChatResponse(response=result["response"], thread_id=result["thread_id"])


@router.post("/managed")
async def managed_chat(request: ChatRequest, enable_memory_tools: bool = True) -> dict[str, Any]:
    service = AgentService(user_id=request.user_id)
    result = await service.chat_with_tools(
        message=request.message, thread_id=request.thread_id, enable_memory_tools=enable_memory_tools
    )
    return result


@router.get("/{user_id}/memories", response_model=MemoriesResponse)
async def get_memories(user_id: str) -> MemoriesResponse:
    service = AgentService(user_id=user_id)
    memories = await service.get_memories()
    return MemoriesResponse(user_id=user_id, memories=memories, count=len(memories))
