from __future__ import annotations

import pytest
from core.schemas import ConversationInsight, UserFact, UserPreference
from pydantic import ValidationError


class TestUserPreference:
    def test_valid_user_preference(self):
        pref = UserPreference(category="ui", preference="dark mode", importance="high")

        assert pref.category == "ui"
        assert pref.preference == "dark mode"
        assert pref.importance == "high"
        assert 0.0 <= pref.confidence <= 1.0

    def test_default_importance(self):
        pref = UserPreference(category="language", preference="Python")

        assert pref.importance == "medium"

    def test_invalid_category(self):
        with pytest.raises(ValidationError):
            UserPreference(category="invalid_category", preference="test")

    def test_invalid_importance(self):
        with pytest.raises(ValidationError):
            UserPreference(category="ui", preference="test", importance="invalid")

    def test_model_dump(self):
        pref = UserPreference(category="feature", preference="code completion", importance="high", confidence=0.95)

        dumped = pref.model_dump()

        assert isinstance(dumped, dict)
        assert dumped["category"] == "feature"
        assert dumped["preference"] == "code completion"
        assert dumped["importance"] == "high"
        assert dumped["confidence"] == 0.95
        assert "created_at" in dumped


class TestUserFact:
    def test_valid_user_fact(self):
        fact = UserFact(
            fact_type="professional",
            content="Software engineer with 5 years experience",
            tags=["engineering", "backend"],
        )

        assert fact.fact_type == "professional"
        assert fact.content == "Software engineer with 5 years experience"
        assert len(fact.tags) == 2

    def test_default_tags(self):
        fact = UserFact(fact_type="hobby", content="Likes playing guitar")

        assert fact.tags == []

    def test_invalid_fact_type(self):
        with pytest.raises(ValidationError):
            UserFact(fact_type="invalid_type", content="test")

    def test_confidence_bounds(self):
        with pytest.raises(ValidationError):
            UserFact(fact_type="personal", content="test", confidence=1.5)

        with pytest.raises(ValidationError):
            UserFact(fact_type="personal", content="test", confidence=-0.1)


class TestConversationInsight:
    def test_valid_conversation_insight(self):
        insight = ConversationInsight(
            topic="Python programming",
            sentiment="positive",
            key_points=["Discussed async/await", "Covered error handling"],
        )

        assert insight.topic == "Python programming"
        assert insight.sentiment == "positive"
        assert len(insight.key_points) == 2

    def test_default_sentiment(self):
        insight = ConversationInsight(topic="General discussion", key_points=["Point 1"])

        assert insight.sentiment == "neutral"

    def test_optional_context(self):
        insight = ConversationInsight(topic="Test", key_points=["Point 1"], context="Additional context here")

        assert insight.context == "Additional context here"

    def test_invalid_sentiment(self):
        with pytest.raises(ValidationError):
            ConversationInsight(topic="Test", sentiment="invalid_sentiment", key_points=["Point 1"])


class TestSchemaIntegration:
    def test_all_schemas_have_base_fields(self):
        pref = UserPreference(category="ui", preference="test")
        fact = UserFact(fact_type="personal", content="test")
        insight = ConversationInsight(topic="test", key_points=["test"])

        for schema in [pref, fact, insight]:
            assert hasattr(schema, "created_at")
            assert hasattr(schema, "confidence")
            assert 0.0 <= schema.confidence <= 1.0

    def test_schema_serialization_and_deserialization(self):
        original = UserPreference(category="language", preference="English", importance="high")

        dumped = original.model_dump()
        restored = UserPreference(**dumped)

        assert restored.category == original.category
        assert restored.preference == original.preference
        assert restored.importance == original.importance
