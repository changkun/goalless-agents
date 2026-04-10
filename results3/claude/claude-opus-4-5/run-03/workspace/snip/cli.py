#!/usr/bin/env python3
"""CLI interface for the snippet manager."""
import argparse
import sys
from typing import Optional

from . import core
from .display import format_snippet, format_snippet_list, print_error, print_success


def cmd_add(args: argparse.Namespace) -> int:
    """Add a new snippet."""
    # Read code from stdin if not provided
    if args.code:
        code = args.code
    elif not sys.stdin.isatty():
        code = sys.stdin.read()
    else:
        print_error("No code provided. Use -c or pipe code via stdin.")
        return 1

    tags = args.tags.split(",") if args.tags else []

    snippet_id = core.add_snippet(
        name=args.name,
        code=code.rstrip("\n"),
        language=args.language,
        tags=tags,
        description=args.description,
    )

    print_success(f"Snippet '{args.name}' saved with ID: {snippet_id}")
    return 0


def cmd_get(args: argparse.Namespace) -> int:
    """Get and display a snippet."""
    snippet = core.get_snippet(args.identifier)

    if not snippet:
        print_error(f"Snippet '{args.identifier}' not found.")
        return 1

    if args.raw:
        print(snippet["code"])
    else:
        print(format_snippet(snippet))

    if args.copy:
        if core.copy_to_clipboard(snippet["code"]):
            print_success("Copied to clipboard!")
        else:
            print_error("Could not copy to clipboard (no clipboard tool available).")

    return 0


def cmd_list(args: argparse.Namespace) -> int:
    """List snippets."""
    snippets = core.search_snippets(
        query=args.query,
        tag=args.tag,
        language=args.language,
    )

    if not snippets:
        print("No snippets found.")
        return 0

    print(format_snippet_list(snippets))
    return 0


def cmd_delete(args: argparse.Namespace) -> int:
    """Delete a snippet."""
    if not args.force:
        snippet = core.get_snippet(args.identifier)
        if snippet:
            print(f"Delete snippet '{snippet['name']}' ({snippet['id']})? [y/N] ", end="")
            confirm = input().strip().lower()
            if confirm != "y":
                print("Cancelled.")
                return 0

    if core.delete_snippet(args.identifier):
        print_success(f"Snippet '{args.identifier}' deleted.")
        return 0
    else:
        print_error(f"Snippet '{args.identifier}' not found.")
        return 1


def cmd_edit(args: argparse.Namespace) -> int:
    """Edit a snippet (update fields)."""
    tags = args.tags.split(",") if args.tags else None

    # Read new code from stdin if available
    code = None
    if not sys.stdin.isatty():
        code = sys.stdin.read().rstrip("\n")

    if core.update_snippet(
        identifier=args.identifier,
        name=args.name,
        code=code,
        language=args.language,
        tags=tags,
        description=args.description,
    ):
        print_success(f"Snippet '{args.identifier}' updated.")
        return 0
    else:
        print_error(f"Snippet '{args.identifier}' not found.")
        return 1


def cmd_exec(args: argparse.Namespace) -> int:
    """Execute a snippet."""
    snippet = core.get_snippet(args.identifier)
    if not snippet:
        print_error(f"Snippet '{args.identifier}' not found.")
        return 1

    if not args.yes:
        print(f"Execute snippet '{snippet['name']}' ({snippet['language']})? [y/N] ", end="")
        confirm = input().strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return 0

    exit_code, stdout, stderr = core.execute_snippet(args.identifier, args.args)

    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, end="", file=sys.stderr)

    return exit_code


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="snip",
        description="A CLI code snippet manager. Save, search, and retrieve code snippets.",
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", aliases=["a"], help="Add a new snippet")
    add_parser.add_argument("name", help="Name for the snippet")
    add_parser.add_argument("-c", "--code", help="Code content (or pipe via stdin)")
    add_parser.add_argument("-l", "--language", help="Programming language")
    add_parser.add_argument("-t", "--tags", help="Comma-separated tags")
    add_parser.add_argument("-d", "--description", help="Description")
    add_parser.set_defaults(func=cmd_add)

    # Get command
    get_parser = subparsers.add_parser("get", aliases=["g"], help="Get a snippet by ID or name")
    get_parser.add_argument("identifier", help="Snippet ID or name")
    get_parser.add_argument("-r", "--raw", action="store_true", help="Output raw code only")
    get_parser.add_argument("-C", "--copy", action="store_true", help="Copy to clipboard")
    get_parser.set_defaults(func=cmd_get)

    # List command
    list_parser = subparsers.add_parser("list", aliases=["ls", "l"], help="List/search snippets")
    list_parser.add_argument("query", nargs="?", help="Search query")
    list_parser.add_argument("-t", "--tag", help="Filter by tag")
    list_parser.add_argument("-l", "--language", help="Filter by language")
    list_parser.set_defaults(func=cmd_list)

    # Delete command
    del_parser = subparsers.add_parser("delete", aliases=["rm", "d"], help="Delete a snippet")
    del_parser.add_argument("identifier", help="Snippet ID or name")
    del_parser.add_argument("-f", "--force", action="store_true", help="Skip confirmation")
    del_parser.set_defaults(func=cmd_delete)

    # Edit command
    edit_parser = subparsers.add_parser("edit", aliases=["e"], help="Edit a snippet")
    edit_parser.add_argument("identifier", help="Snippet ID or name")
    edit_parser.add_argument("-n", "--name", help="New name")
    edit_parser.add_argument("-l", "--language", help="New language")
    edit_parser.add_argument("-t", "--tags", help="New tags (comma-separated)")
    edit_parser.add_argument("-d", "--description", help="New description")
    edit_parser.set_defaults(func=cmd_edit)

    # Exec command
    exec_parser = subparsers.add_parser("exec", aliases=["x", "run"], help="Execute a snippet")
    exec_parser.add_argument("identifier", help="Snippet ID or name")
    exec_parser.add_argument("-y", "--yes", action="store_true", help="Skip confirmation")
    exec_parser.add_argument("args", nargs="*", help="Additional arguments to pass to the interpreter")
    exec_parser.set_defaults(func=cmd_exec)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args(argv)

    if not args.command:
        # Default: list all snippets
        args.query = None
        args.tag = None
        args.language = None
        return cmd_list(args)

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
