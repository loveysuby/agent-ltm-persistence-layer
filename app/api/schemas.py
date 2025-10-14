from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class APIResponse(BaseModel):
    success: bool
    message: str
    data: dict[str, Any] | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    details: dict[str, Any] | None = None


class Response(BaseModel):
    success: bool
    data: dict[str, Any] | list[dict[str, Any]] | None = None
    error: str | None = None


class MemoryCreateRequest(BaseModel):
    user_id: str
    content: str
    metadata: dict[str, Any] | None = None


class MemoryUpdateRequest(BaseModel):
    user_id: str
    content: str


class MemorySearchRequest(BaseModel):
    user_id: str
    query: str
    filter: dict[str, Any] | None = None
    limit: int = Field(default=10, ge=1, le=100)


class ManagedChatRequest(BaseModel):
    user_id: str
    message: str
    thread_id: str = "default"
    enable_memory_tools: bool = True
