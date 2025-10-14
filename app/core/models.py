from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel


class MemoryType(str, Enum):
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"


class BaseResponse(BaseModel):
    id: UUID
    created_at: datetime
    updated_at: datetime
