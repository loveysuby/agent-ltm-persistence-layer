from __future__ import annotations

from typing import Literal

from pydantic import Field

from app.core.base import BaseMemory


class UserPreference(BaseMemory):
    category: Literal["ui", "language", "feature", "communication", "workflow"]
    preference: str
    importance: Literal["low", "medium", "high"] = Field(default="medium")


class UserFact(BaseMemory):
    fact_type: Literal["personal", "professional", "hobby", "goal", "background"]
    content: str
    tags: list[str] = Field(default_factory=list)


class ConversationInsight(BaseMemory):
    topic: str
    sentiment: Literal["positive", "neutral", "negative"] = Field(default="neutral")
    key_points: list[str]
    context: str | None = None
