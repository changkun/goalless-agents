#!/usr/bin/env python3
"""Generate a compact JSON snapshot of a project directory."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path


EXTENSION_NAMES = {
    ".css": "CSS",
    ".html": "HTML",
    ".js": "JavaScript",
    ".json": "JSON",
    ".jsx": "JSX",
    ".md": "Markdown",
    ".py": "Python",
    ".rs": "Rust",
    ".sh": "Shell",
    ".sql": "SQL",
    ".toml": "TOML",
    ".ts": "TypeScript",
    ".tsx": "TSX",
    ".txt": "Text",
    ".yml": "YAML",
    ".yaml": "YAML",
}

IGNORE_DIRS = {
    ".git",
    ".hg",
    ".svn",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
}


def detect_language(path: Path) -> str:
    if path.name == "Dockerfile":
        return "Dockerfile"
    return EXTENSION_NAMES.get(path.suffix.lower(), "Other")


def iter_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in IGNORE_DIRS for part in path.parts):
            continue
        yield path


def make_snapshot(root: Path, limit: int) -> dict:
    files = []
    language_counts = Counter()
    total_bytes = 0

    for path in iter_files(root):
        size = path.stat().st_size
        rel_path = path.relative_to(root).as_posix()
        language = detect_language(path)
        language_counts[language] += 1
        total_bytes += size
        files.append({"path": rel_path, "bytes": size, "language": language})

    files.sort(key=lambda item: (-item["bytes"], item["path"]))

    return {
        "root": str(root.resolve()),
        "file_count": len(files),
        "total_bytes": total_bytes,
        "is_empty": len(files) == 0,
        "languages": dict(sorted(language_counts.items(), key=lambda item: (-item[1], item[0]))),
        "largest_files": files[:limit],
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".", help="Directory to scan")
    parser.add_argument(
        "--limit",
        type=int,
        default=10,
        help="Number of largest files to include in the snapshot",
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print the JSON output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    root = Path(args.path).resolve()

    if not root.exists():
        raise SystemExit(f"Path does not exist: {root}")
    if not root.is_dir():
        raise SystemExit(f"Path is not a directory: {root}")
    if args.limit < 1:
        raise SystemExit("--limit must be at least 1")

    snapshot = make_snapshot(root, args.limit)
    indent = 2 if args.pretty else None
    print(json.dumps(snapshot, indent=indent, sort_keys=args.pretty))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
