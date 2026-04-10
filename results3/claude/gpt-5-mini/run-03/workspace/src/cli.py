"""Simple CLI with a greeting function.

Provides:
- greet(name: str, excited: bool, caps: bool) -> str
- main() -> None : CLI entrypoint
"""
from __future__ import annotations

import argparse
import sys

from src import __version__


def greet(name: str, excited: bool = False, caps: bool = False) -> str:
    """Return a greeting for `name`.

    If `name` is empty or None, uses "World". If `excited` is True, append an exclamation mark.
    If `caps` is True, return the greeting in uppercase.
    """
    if not name:
        name = "World"
    msg = f"Hello, {name}" + ("!" if excited else "")
    return msg.upper() if caps else msg


def main(argv: list[str] | None = None) -> None:
    """Command-line entrypoint.

    Usage examples:
      python -m src.cli Alice
      python -m src.cli --excited Alice
      python -m src.cli --version
      python -m src.cli --caps Alice
    """
    parser = argparse.ArgumentParser(description="Greet someone.")
    parser.add_argument("name", nargs="?", default="World", help="Name to greet")
    parser.add_argument("-e", "--excited", action="store_true", help="Add an exclamation mark")
    parser.add_argument("-c", "--caps", action="store_true", help="Return greeting in uppercase")
    parser.add_argument("--version", action="store_true", help="Show package version and exit")

    args = parser.parse_args(args=argv)

    if args.version:
        print(__version__)
        return

    print(greet(args.name, args.excited, args.caps))


if __name__ == "__main__":
    main()
