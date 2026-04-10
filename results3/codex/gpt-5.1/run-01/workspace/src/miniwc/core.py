from __future__ import annotations

from dataclasses import dataclass
from typing import TextIO


@dataclass
class Counts:
    lines: int
    words: int
    bytes: int


def count_stream(stream: TextIO) -> Counts:
    line_count = 0
    word_count = 0
    byte_count = 0

    for line in stream:
        line_count += 1
        # Use default split behaviour to treat any whitespace as separator
        word_count += len(line.split())
        byte_count += len(line.encode())

    return Counts(lines=line_count, words=word_count, bytes=byte_count)


def format_counts(counts: Counts, label: str | None = None) -> str:
    parts = [f"{counts.lines:7d}", f"{counts.words:7d}", f"{counts.bytes:7d}"]
    if label:
        parts.append(f" {label}")
    return "".join(parts)

