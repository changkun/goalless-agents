#!/usr/bin/env python3
"""
Snippit - A lightweight code snippet manager
Store, organize, and quickly retrieve code snippets from the terminal.
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
import argparse


class SnippetManager:
    def __init__(self, data_file: Optional[str] = None):
        if data_file is None:
            data_file = os.path.expanduser("~/.snippits.json")
        self.data_file = Path(data_file)
        self.snippets: Dict[str, Any] = {}
        self._load()

    def _load(self):
        """Load snippets from file."""
        if self.data_file.exists():
            try:
                with open(self.data_file) as f:
                    self.snippets = json.load(f)
            except json.JSONDecodeError:
                self.snippets = {}
        else:
            self.snippets = {}

    def _save(self):
        """Save snippets to file."""
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_file, 'w') as f:
            json.dump(self.snippets, f, indent=2)

    def add(self, name: str, code: str, language: str = "text", tags: Optional[List[str]] = None):
        """Add a new snippet."""
        if name in self.snippets:
            print(f"Error: Snippet '{name}' already exists. Use 'update' to modify it.")
            return False

        self.snippets[name] = {
            "code": code,
            "language": language,
            "tags": tags or [],
            "created": datetime.now().isoformat(),
            "modified": datetime.now().isoformat(),
        }
        self._save()
        print(f"✓ Added snippet: {name}")
        return True

    def update(self, name: str, code: Optional[str] = None, language: Optional[str] = None, tags: Optional[List[str]] = None):
        """Update an existing snippet."""
        if name not in self.snippets:
            print(f"Error: Snippet '{name}' not found.")
            return False

        if code is not None:
            self.snippets[name]["code"] = code
        if language is not None:
            self.snippets[name]["language"] = language
        if tags is not None:
            self.snippets[name]["tags"] = tags

        self.snippets[name]["modified"] = datetime.now().isoformat()
        self._save()
        print(f"✓ Updated snippet: {name}")
        return True

    def delete(self, name: str):
        """Delete a snippet."""
        if name not in self.snippets:
            print(f"Error: Snippet '{name}' not found.")
            return False

        del self.snippets[name]
        self._save()
        print(f"✓ Deleted snippet: {name}")
        return True

    def get(self, name: str) -> Optional[Dict[str, Any]]:
        """Retrieve a snippet by name."""
        return self.snippets.get(name)

    def search(self, query: str, search_type: str = "all") -> List[str]:
        """Search snippets by name, tag, or code content."""
        results = []
        query_lower = query.lower()

        for name, snippet in self.snippets.items():
            match = False

            if search_type in ("all", "name"):
                if query_lower in name.lower():
                    match = True

            if search_type in ("all", "tags"):
                if any(query_lower in tag.lower() for tag in snippet.get("tags", [])):
                    match = True

            if search_type in ("all", "code"):
                if query_lower in snippet.get("code", "").lower():
                    match = True

            if match:
                results.append(name)

        return results

    def list_all(self, tag: Optional[str] = None) -> List[str]:
        """List all snippets, optionally filtered by tag."""
        if tag is None:
            return sorted(self.snippets.keys())

        tag_lower = tag.lower()
        return sorted([
            name for name, snippet in self.snippets.items()
            if any(tag_lower == t.lower() for t in snippet.get("tags", []))
        ])

    def get_tags(self) -> List[str]:
        """Get all unique tags."""
        tags = set()
        for snippet in self.snippets.values():
            tags.update(snippet.get("tags", []))
        return sorted(tags)


def format_snippet(name: str, snippet: Dict[str, Any], show_code: bool = True) -> str:
    """Format a snippet for display."""
    output = f"\n📝 {name}"
    output += f"\n   Language: {snippet.get('language', 'text')}"

    tags = snippet.get("tags", [])
    if tags:
        output += f"\n   Tags: {', '.join(tags)}"

    if show_code:
        output += f"\n   Code:\n"
        for line in snippet.get("code", "").split("\n"):
            output += f"   {line}\n"

    created = snippet.get("created", "")
    if created:
        output += f"   Created: {created.split('T')[0]}"

    return output


def main():
    parser = argparse.ArgumentParser(
        description="Snippit - Manage code snippets from the terminal",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  snippit add "json-parse" 'JSON.parse(str)' --language js
  snippit get json-parse
  snippit search "parse"
  snippit list --tag "js"
  snippit delete json-parse
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new snippet")
    add_parser.add_argument("name", help="Snippet name")
    add_parser.add_argument("code", help="Code content")
    add_parser.add_argument("--language", "-l", default="text", help="Programming language")
    add_parser.add_argument("--tags", "-t", nargs="+", help="Tags for organization")

    # Get command
    get_parser = subparsers.add_parser("get", help="Retrieve a snippet")
    get_parser.add_argument("name", help="Snippet name")
    get_parser.add_argument("--copy", "-c", action="store_true", help="Copy to clipboard")

    # Update command
    update_parser = subparsers.add_parser("update", help="Update an existing snippet")
    update_parser.add_argument("name", help="Snippet name")
    update_parser.add_argument("--code", help="New code content")
    update_parser.add_argument("--language", "-l", help="Update language")
    update_parser.add_argument("--tags", "-t", nargs="+", help="Update tags")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a snippet")
    delete_parser.add_argument("name", help="Snippet name")

    # List command
    list_parser = subparsers.add_parser("list", help="List all snippets")
    list_parser.add_argument("--tag", "-t", help="Filter by tag")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search snippets")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--type", choices=["all", "name", "tags", "code"], default="all", help="Search type")

    # Tags command
    tags_parser = subparsers.add_parser("tags", help="List all tags")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    manager = SnippetManager()

    if args.command == "add":
        manager.add(args.name, args.code, args.language, args.tags)

    elif args.command == "get":
        snippet = manager.get(args.name)
        if snippet:
            output = format_snippet(args.name, snippet)
            print(output)
            if args.copy:
                try:
                    import pyperclip
                    pyperclip.copy(snippet["code"])
                    print("\n✓ Copied to clipboard")
                except ImportError:
                    print("\n(Install pyperclip for --copy: pip install pyperclip)")
        else:
            print(f"Error: Snippet '{args.name}' not found")

    elif args.command == "update":
        manager.update(args.name, args.code, args.language, args.tags)

    elif args.command == "delete":
        manager.delete(args.name)

    elif args.command == "list":
        snippets = manager.list_all(args.tag)
        if snippets:
            if args.tag:
                print(f"\nSnippets with tag '{args.tag}':")
            else:
                print("\nAll snippets:")
            for name in snippets:
                snippet = manager.get(name)
                print(format_snippet(name, snippet, show_code=False))
            print(f"\nTotal: {len(snippets)} snippet(s)")
        else:
            print("No snippets found")

    elif args.command == "search":
        results = manager.search(args.query, args.type)
        if results:
            print(f"Found {len(results)} snippet(s):")
            for name in results:
                snippet = manager.get(name)
                print(format_snippet(name, snippet, show_code=False))
        else:
            print(f"No snippets found matching '{args.query}'")

    elif args.command == "tags":
        tags = manager.get_tags()
        if tags:
            print("\nAll tags:")
            for tag in tags:
                count = sum(1 for s in manager.snippets.values() if tag in s.get("tags", []))
                print(f"  {tag} ({count})")
        else:
            print("No tags found")


if __name__ == "__main__":
    main()
