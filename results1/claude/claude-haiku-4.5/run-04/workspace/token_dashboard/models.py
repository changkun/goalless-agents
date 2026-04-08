"""Data models for token tracking."""

from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class TokenUsage:
    """Represents a single token usage event."""

    name: str
    model: str
    input_tokens: int
    output_tokens: int
    timestamp: datetime

    @property
    def total_tokens(self) -> int:
        """Calculate total tokens used."""
        return self.input_tokens + self.output_tokens

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        data = asdict(self)
        data["timestamp"] = self.timestamp.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "TokenUsage":
        """Create from dictionary."""
        data = data.copy()
        data["timestamp"] = datetime.fromisoformat(data["timestamp"])
        return cls(**data)
