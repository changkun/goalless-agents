"""Small greeting utility with CLI."""
import sys


def greet(name: str) -> str:
    """Return a friendly greeting for `name`."""
    if not name:
        raise ValueError("name must be non-empty")
    return f"Hello, {name}!"


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if not argv:
        print("Usage: python hello.py NAME")
        return 2
    try:
        print(greet(argv[0]))
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

