#!/usr/bin/env python3
"""
devlog - A simple, fast developer journal CLI
Track your daily work, learnings, and decisions
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict

DEVLOG_DIR = Path.home() / ".devlog"
ENTRIES_FILE = DEVLOG_DIR / "entries.json"


def init_storage():
    """Initialize storage directory and file"""
    DEVLOG_DIR.mkdir(exist_ok=True)
    if not ENTRIES_FILE.exists():
        ENTRIES_FILE.write_text("[]")


def load_entries() -> List[Dict]:
    """Load all entries from storage"""
    try:
        return json.loads(ENTRIES_FILE.read_text())
    except (json.JSONDecodeError, FileNotFoundError):
        return []


def save_entries(entries: List[Dict]):
    """Save entries to storage"""
    ENTRIES_FILE.write_text(json.dumps(entries, indent=2))


def add_entry(text: str, tags: List[str] = None):
    """Add a new journal entry"""
    entries = load_entries()
    entry = {
        "id": len(entries) + 1,
        "timestamp": datetime.now().isoformat(),
        "text": text,
        "tags": tags or [],
    }
    entries.append(entry)
    save_entries(entries)
    print(f"✓ Entry #{entry['id']} added")


def list_entries(limit: int = None, tag: str = None, search: str = None):
    """List journal entries with optional filtering"""
    entries = load_entries()

    # Filter by tag
    if tag:
        entries = [e for e in entries if tag in e.get("tags", [])]

    # Filter by search term
    if search:
        search_lower = search.lower()
        entries = [e for e in entries if search_lower in e["text"].lower()]

    # Apply limit
    if limit:
        entries = entries[-limit:]

    if not entries:
        print("No entries found")
        return

    for entry in entries:
        timestamp = datetime.fromisoformat(entry["timestamp"])
        tags_str = f" [{', '.join(entry['tags'])}]" if entry["tags"] else ""
        print(f"\n#{entry['id']} - {timestamp.strftime('%Y-%m-%d %H:%M')}{tags_str}")
        print(f"  {entry['text']}")


def today_summary():
    """Show today's entries"""
    entries = load_entries()
    today = datetime.now().date()
    today_entries = [
        e for e in entries
        if datetime.fromisoformat(e["timestamp"]).date() == today
    ]

    if not today_entries:
        print(f"No entries for today ({today})")
        return

    print(f"\n📅 Today's log ({today}):\n")
    for entry in today_entries:
        timestamp = datetime.fromisoformat(entry["timestamp"])
        tags_str = f" [{', '.join(entry['tags'])}]" if entry["tags"] else ""
        print(f"#{entry['id']} - {timestamp.strftime('%H:%M')}{tags_str}")
        print(f"  {entry['text']}\n")


def show_stats():
    """Show statistics about entries"""
    entries = load_entries()

    if not entries:
        print("No entries yet")
        return

    # Count by day
    dates = [datetime.fromisoformat(e["timestamp"]).date() for e in entries]
    unique_days = len(set(dates))

    # Tag statistics
    all_tags = []
    for entry in entries:
        all_tags.extend(entry.get("tags", []))

    tag_counts = {}
    for tag in all_tags:
        tag_counts[tag] = tag_counts.get(tag, 0) + 1

    print(f"\n📊 Statistics:")
    print(f"  Total entries: {len(entries)}")
    print(f"  Days logged: {unique_days}")

    if tag_counts:
        print(f"  Top tags:")
        for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    - {tag}: {count}")


def main():
    parser = argparse.ArgumentParser(
        description="devlog - Track your development work",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  devlog add "Fixed authentication bug in login flow" -t bug fix
  devlog add "Learned about Rust lifetimes" -t learning rust
  devlog today
  devlog list --limit 10
  devlog search "authentication"
  devlog stats
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new entry")
    add_parser.add_argument("text", help="Entry text")
    add_parser.add_argument("-t", "--tags", nargs="+", help="Tags for the entry")

    # List command
    list_parser = subparsers.add_parser("list", help="List entries")
    list_parser.add_argument("-l", "--limit", type=int, help="Limit number of entries")
    list_parser.add_argument("-t", "--tag", help="Filter by tag")

    # Search command
    search_parser = subparsers.add_parser("search", help="Search entries")
    search_parser.add_argument("query", help="Search query")

    # Today command
    subparsers.add_parser("today", help="Show today's entries")

    # Stats command
    subparsers.add_parser("stats", help="Show statistics")

    args = parser.parse_args()

    init_storage()

    if args.command == "add":
        add_entry(args.text, args.tags)
    elif args.command == "list":
        list_entries(limit=args.limit, tag=args.tag)
    elif args.command == "search":
        list_entries(search=args.query)
    elif args.command == "today":
        today_summary()
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
