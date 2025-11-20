from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    SEMANTIC = "semantic"
    EPISODIC = "episodic"
    PROCEDURAL = "procedural"


class BaseMemory(BaseModel):
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
