#!/usr/bin/env python3
"""Create a compact summary and keyword index for plain text files."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

STOP_WORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "has",
    "he",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "that",
    "the",
    "to",
    "was",
    "were",
    "will",
    "with",
}


def split_sentences(text: str) -> list[str]:
    cleaned = re.sub(r"\s+", " ", text.strip())
    if not cleaned:
        return []
    return [part.strip() for part in re.split(r"(?<=[.!?])\s+", cleaned) if part.strip()]


def extract_keywords(text: str, limit: int) -> list[dict[str, int | str]]:
    words = re.findall(r"[A-Za-z']+", text.lower())
    counts = Counter(word for word in words if word not in STOP_WORDS and len(word) > 2)
    return [
        {"term": term, "count": count}
        for term, count in counts.most_common(limit)
    ]


def summarize(text: str, sentence_limit: int = 2, keyword_limit: int = 5) -> dict[str, object]:
    sentences = split_sentences(text)
    summary = " ".join(sentences[:sentence_limit])
    return {
        "summary": summary,
        "sentence_count": len(sentences),
        "keyword_count": keyword_limit,
        "keywords": extract_keywords(text, keyword_limit),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a short summary and keyword index for a text file."
    )
    parser.add_argument("path", help="Path to a UTF-8 plain text file.")
    parser.add_argument(
        "--sentences",
        type=int,
        default=2,
        help="Number of sentences to keep in the summary.",
    )
    parser.add_argument(
        "--keywords",
        type=int,
        default=5,
        help="Number of top keywords to include.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of plain text output.",
    )
    return parser


def render_plain(result: dict[str, object]) -> str:
    keywords = result["keywords"]
    keyword_text = ", ".join(f"{item['term']} ({item['count']})" for item in keywords)
    return "\n".join(
        [
            f"Summary: {result['summary']}",
            f"Sentences: {result['sentence_count']}",
            f"Keywords: {keyword_text or 'None'}",
        ]
    )


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.sentences < 1 or args.keywords < 1:
        parser.error("--sentences and --keywords must be positive integers")

    path = Path(args.path)
    if not path.exists():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1

    text = path.read_text(encoding="utf-8")
    result = summarize(text, sentence_limit=args.sentences, keyword_limit=args.keywords)

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(render_plain(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
