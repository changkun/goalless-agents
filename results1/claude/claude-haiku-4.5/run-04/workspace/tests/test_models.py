"""Tests for data models."""

from datetime import datetime

from token_dashboard.models import TokenUsage


def test_token_usage_total():
    """Test total tokens calculation."""
    usage = TokenUsage(
        name="test",
        model="claude-opus-4-6",
        input_tokens=100,
        output_tokens=50,
        timestamp=datetime.now(),
    )
    assert usage.total_tokens == 150


def test_token_usage_serialization():
    """Test serialization to and from dict."""
    now = datetime.now()
    usage = TokenUsage(
        name="test",
        model="claude-opus-4-6",
        input_tokens=100,
        output_tokens=50,
        timestamp=now,
    )

    data = usage.to_dict()
    restored = TokenUsage.from_dict(data)

    assert restored.name == usage.name
    assert restored.model == usage.model
    assert restored.input_tokens == usage.input_tokens
    assert restored.output_tokens == usage.output_tokens
