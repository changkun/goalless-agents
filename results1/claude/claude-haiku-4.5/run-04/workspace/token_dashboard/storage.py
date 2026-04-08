"""Storage layer for token usage data."""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from token_dashboard.models import TokenUsage


class TokenStore:
    """Manages persistent storage of token usage data."""

    def __init__(self, data_dir: Optional[Path] = None):
        """Initialize the token store."""
        self.data_dir = data_dir or Path.home() / ".token-dashboard"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.usage_file = self.data_dir / "usage.json"

    def add_usage(self, usage: TokenUsage) -> None:
        """Add a usage event to storage."""
        usages = self._load_usages()
        usages.append(usage.to_dict())
        self._save_usages(usages)

    def get_usages(self, days: int = 7) -> List[TokenUsage]:
        """Get usage events from the last N days."""
        cutoff = datetime.now() - timedelta(days=days)
        usages = self._load_usages()
        return [
            TokenUsage.from_dict(u)
            for u in usages
            if datetime.fromisoformat(u["timestamp"]) >= cutoff
        ]

    def get_usage_summary(
        self, days: int = 7, model: Optional[str] = None
    ) -> Dict[str, Dict]:
        """Get aggregated usage summary by model."""
        usages = self.get_usages(days)

        summary: Dict[str, Dict] = {}
        for usage in usages:
            if model and usage.model != model:
                continue

            if usage.model not in summary:
                summary[usage.model] = {"input": 0, "output": 0, "total": 0, "count": 0}

            summary[usage.model]["input"] += usage.input_tokens
            summary[usage.model]["output"] += usage.output_tokens
            summary[usage.model]["total"] += usage.total_tokens
            summary[usage.model]["count"] += 1

        return summary

    def get_stats(self) -> Dict:
        """Get overall statistics."""
        usages = self.get_usages(days=30)

        if not usages:
            return {
                "total_operations": 0,
                "total_input": 0,
                "total_output": 0,
                "total_tokens": 0,
                "avg_tokens_per_op": 0,
                "last_operation": "Never",
            }

        total_input = sum(u.input_tokens for u in usages)
        total_output = sum(u.output_tokens for u in usages)
        total_tokens = total_input + total_output
        avg_tokens = total_tokens / len(usages) if usages else 0

        last_op = max(usages, key=lambda u: u.timestamp)
        last_op_str = (
            datetime.now() - last_op.timestamp
        ).total_seconds()
        if last_op_str < 60:
            last_op_time = "< 1 minute ago"
        elif last_op_str < 3600:
            last_op_time = f"{int(last_op_str / 60)} minutes ago"
        else:
            last_op_time = f"{int(last_op_str / 3600)} hours ago"

        return {
            "total_operations": len(usages),
            "total_input": total_input,
            "total_output": total_output,
            "total_tokens": total_tokens,
            "avg_tokens_per_op": avg_tokens,
            "last_operation": last_op_time,
        }

    def clear(self) -> None:
        """Clear all usage data."""
        self._save_usages([])

    def _load_usages(self) -> List[dict]:
        """Load usage data from file."""
        if not self.usage_file.exists():
            return []
        with open(self.usage_file) as f:
            return json.load(f)

    def _save_usages(self, usages: List[dict]) -> None:
        """Save usage data to file."""
        with open(self.usage_file, "w") as f:
            json.dump(usages, f, indent=2)
