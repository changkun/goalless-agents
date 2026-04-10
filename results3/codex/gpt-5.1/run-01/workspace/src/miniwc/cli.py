from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable, List

from .core import count_stream, format_counts


def parse_args(argv: Iterable[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="miniwc",
        description="Count lines, words, and bytes in files or stdin (minimal wc clone).",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Files to read. With no FILE or when FILE is -, read standard input.",
    )
    return parser.parse_args(list(argv))


def run(files: List[str]) -> int:
    counts_list = []

    if not files:
        # Only stdin
        counts = count_stream(sys.stdin)
        print(format_counts(counts))
        return 0

    for name in files:
        if name == "-":
            counts = count_stream(sys.stdin)
            counts_list.append((counts, None))
            print(format_counts(counts))
            continue

        path = Path(name)
        try:
            with path.open("rb") as raw:
                # Decode using locale default, falling back to utf-8
                data = raw.read()
            try:
                text = data.decode()
            except UnicodeDecodeError:
                text = data.decode("utf-8", errors="replace")
        except OSError as exc:
            print(f"miniwc: {name}: {exc.strerror}", file=sys.stderr)
            continue

        from io import StringIO

        counts = count_stream(StringIO(text))
        counts_list.append((counts, name))
        print(format_counts(counts, name))

    if len(counts_list) > 1:
        total_lines = sum(c.lines for c, _ in counts_list)
        total_words = sum(c.words for c, _ in counts_list)
        total_bytes = sum(c.bytes for c, _ in counts_list)
        from .core import Counts

        total = Counts(total_lines, total_words, total_bytes)
        print(format_counts(total, "total"))

    return 0


def main(argv: Iterable[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    args = parse_args(argv)
    return run(args.files)


if __name__ == "__main__":
    raise SystemExit(main())

