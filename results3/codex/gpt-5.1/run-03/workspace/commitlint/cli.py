from __future__ import annotations

import argparse
import sys
from typing import Optional

from .core import lint_message, format_errors


def parse_args(argv: Optional[list[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="commitlint-lite",
        description="Validate a commit message against a small Conventional Commits subset.",
    )
    parser.add_argument(
        "message",
        nargs="?",
        help="Commit message string. If omitted, the message is read from stdin.",
    )
    return parser.parse_args(argv)


def main(argv: Optional[list[str]] = None) -> int:
    args = parse_args(argv)

    if args.message is not None:
        message = args.message
    else:
        if sys.stdin.isatty():
            print(
                "No message provided. Pass a message argument or pipe from stdin.",
                file=sys.stderr,
            )
            return 1
        message = sys.stdin.read()

    try:
        errors = lint_message(message)
    except Exception as exc:  # pragma: no cover - defensive
        print(f"Internal error while linting: {exc}", file=sys.stderr)
        return 2

    if errors:
        print("Commit message is INVALID:", file=sys.stderr)
        print(format_errors(errors), file=sys.stderr)
        return 1

    print("Commit message is valid.")
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())

