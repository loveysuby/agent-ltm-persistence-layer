from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BaseMemory(BaseModel):
    """Base class for all structured memories."""

    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence score of the extracted information")


class UserPreference(BaseMemory):
    """User preference memory for UI, language, features, etc."""

    category: Literal["ui", "language", "feature", "communication", "workflow"] = Field(
        description="Category of the preference"
    )
    preference: str = Field(description="The specific preference expressed by the user")
    importance: Literal["low", "medium", "high"] = Field(
        default="medium", description="Importance level of this preference"
    )


class UserFact(BaseMemory):
    """Factual information about the user."""

    fact_type: Literal["personal", "professional", "hobby", "goal", "background"] = Field(
        description="Type of factual information"
    )
    content: str = Field(description="The factual information content")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")


class ConversationInsight(BaseMemory):
    """Insights and context extracted from conversations."""

    topic: str = Field(description="Main topic of the conversation")
    sentiment: Literal["positive", "neutral", "negative"] = Field(
        default="neutral", description="Overall sentiment of the conversation"
    )
    key_points: list[str] = Field(description="Key takeaways from the conversation")
    context: str | None = Field(default=None, description="Additional contextual information")


ALL_MEMORY_SCHEMAS = [UserPreference, UserFact, ConversationInsight]

SCHEMA_INSTRUCTIONS = """
Extract structured information from the conversation:

1. UserPreference: Extract any preferences about UI, language, features, communication style, or workflow.
   - Be specific about the category
   - Capture the exact preference
   - Infer importance from context (explicit statements are 'high', casual mentions are 'low')

2. UserFact: Extract factual information about the user's background, profession, hobbies, or goals.
   - Categorize appropriately
   - Add relevant tags for easy retrieval
   - Only extract information with high confidence

3. ConversationInsight: Capture the main topic, sentiment, and key points from significant conversations.
   - Identify the core topic
   - Assess the overall sentiment
   - List 2-5 key takeaways

Be precise and only extract information that is clearly stated or strongly implied.
"""
