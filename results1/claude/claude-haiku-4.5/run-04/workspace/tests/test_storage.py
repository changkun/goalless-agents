"""Tests for storage layer."""

import tempfile
from datetime import datetime
from pathlib import Path

from token_dashboard.models import TokenUsage
from token_dashboard.storage import TokenStore


def test_add_and_retrieve_usage():
    """Test adding and retrieving usage data."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = TokenStore(Path(tmpdir))
        usage = TokenUsage(
            name="test_op",
            model="claude-opus-4-6",
            input_tokens=100,
            output_tokens=50,
            timestamp=datetime.now(),
        )

        store.add_usage(usage)
        usages = store.get_usages(days=1)

        assert len(usages) == 1
        assert usages[0].name == "test_op"
        assert usages[0].total_tokens == 150


def test_usage_summary():
    """Test aggregated usage summary."""
    with tempfile.TemporaryDirectory() as tmpdir:
        store = TokenStore(Path(tmpdir))

        for i in range(3):
            usage = TokenUsage(
                name=f"op_{i}",
                model="claude-opus-4-6",
                input_tokens=100,
                output_tokens=50,
                timestamp=datetime.now(),
            )
            store.add_usage(usage)

        summary = store.get_usage_summary(days=1)

        assert "claude-opus-4-6" in summary
        assert summary["claude-opus-4-6"]["count"] == 3
        assert summary["claude-opus-4-6"]["total"] == 450
