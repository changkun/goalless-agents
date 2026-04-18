#!/usr/bin/env python3
"""Task Journal - A lightweight CLI for logging and tracking tasks."""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
import argparse
from typing import Optional, List, Dict


class TaskJournal:
    def __init__(self, data_dir: Optional[str] = None):
        self.data_dir = Path(data_dir or Path.home() / ".task_journal")
        self.data_dir.mkdir(exist_ok=True)
        self.journal_file = self.data_dir / "tasks.json"
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Dict]:
        if not self.journal_file.exists():
            return []
        try:
            with open(self.journal_file) as f:
                return json.load(f)
        except json.JSONDecodeError:
            return []

    def _save_tasks(self):
        with open(self.journal_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def add_task(self, description: str, tags: List[str]):
        task = {
            "id": len(self.tasks) + 1,
            "description": description,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "completed": False,
        }
        self.tasks.append(task)
        self._save_tasks()
        return task

    def complete_task(self, task_id: int) -> Optional[Dict]:
        for task in self.tasks:
            if task["id"] == task_id:
                task["completed"] = True
                task["completed_at"] = datetime.now().isoformat()
                self._save_tasks()
                return task
        return None

    def search(self, query: str, tag_filter: Optional[str] = None) -> List[Dict]:
        results = []
        query_lower = query.lower()

        for task in self.tasks:
            desc_match = query_lower in task["description"].lower()
            tag_match = not tag_filter or tag_filter in task["tags"]

            if desc_match and tag_match:
                results.append(task)

        return results

    def get_report(self, days: int = 1, tag_filter: Optional[str] = None) -> Dict:
        cutoff = datetime.now() - timedelta(days=days)
        cutoff_iso = cutoff.isoformat()

        period_tasks = [
            t for t in self.tasks
            if t["created_at"] >= cutoff_iso and (not tag_filter or tag_filter in t["tags"])
        ]

        completed = [t for t in period_tasks if t["completed"]]
        pending = [t for t in period_tasks if not t["completed"]]

        return {
            "period_days": days,
            "total": len(period_tasks),
            "completed": len(completed),
            "pending": len(pending),
            "completion_rate": f"{100 * len(completed) // max(1, len(period_tasks))}%",
            "pending_tasks": pending,
        }

    def list_all(self, limit: Optional[int] = None) -> List[Dict]:
        result = sorted(self.tasks, key=lambda t: t["created_at"], reverse=True)
        return result[:limit] if limit else result


def format_task(task: Dict) -> str:
    status = "✓" if task["completed"] else "•"
    tags_str = f" [{', '.join(task['tags'])}]" if task["tags"] else ""
    created = datetime.fromisoformat(task["created_at"]).strftime("%Y-%m-%d %H:%M")
    return f"{status} #{task['id']} {task['description']}{tags_str} ({created})"


def main():
    parser = argparse.ArgumentParser(
        prog="task",
        description="Task Journal - Log and track your tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  task add "Write report" --tag work --tag urgent
  task search "report"
  task complete 1
  task report --days 7 --tag work
  task list --limit 10
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Add subcommand
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("description", help="Task description")
    add_parser.add_argument("--tag", dest="tags", action="append", default=[], help="Add a tag (can use multiple times)")

    # Complete subcommand
    complete_parser = subparsers.add_parser("complete", help="Mark task as completed")
    complete_parser.add_argument("task_id", type=int, help="Task ID to complete")

    # Search subcommand
    search_parser = subparsers.add_parser("search", help="Search tasks")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument("--tag", help="Filter by tag")

    # Report subcommand
    report_parser = subparsers.add_parser("report", help="Generate a report")
    report_parser.add_argument("--days", type=int, default=1, help="Number of days to include (default: 1)")
    report_parser.add_argument("--tag", help="Filter by tag")

    # List subcommand
    list_parser = subparsers.add_parser("list", help="List all tasks")
    list_parser.add_argument("--limit", type=int, help="Limit number of results")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    journal = TaskJournal()

    if args.command == "add":
        task = journal.add_task(args.description, args.tags)
        print(f"✓ Task #{task['id']} added")
        print(format_task(task))

    elif args.command == "complete":
        task = journal.complete_task(args.task_id)
        if task:
            print(f"✓ Task #{args.task_id} completed")
        else:
            print(f"✗ Task #{args.task_id} not found", file=sys.stderr)
            sys.exit(1)

    elif args.command == "search":
        results = journal.search(args.query, args.tag)
        if results:
            print(f"Found {len(results)} task(s):\n")
            for task in results:
                print(format_task(task))
        else:
            print("No tasks found.")

    elif args.command == "report":
        report = journal.get_report(args.days, args.tag)
        print(f"\n{'━' * 50}")
        print(f"Report: Last {args.days} day(s)")
        if args.tag:
            print(f"Filter: tag={args.tag}")
        print(f"{'━' * 50}")
        print(f"Total tasks:     {report['total']}")
        print(f"Completed:       {report['completed']}")
        print(f"Pending:         {report['pending']}")
        print(f"Completion:      {report['completion_rate']}")

        if report["pending_tasks"]:
            print(f"\n{'─' * 50}")
            print("Pending tasks:")
            for task in report["pending_tasks"]:
                print(format_task(task))
        print(f"{'━' * 50}\n")

    elif args.command == "list":
        tasks = journal.list_all(args.limit)
        if tasks:
            for task in tasks:
                print(format_task(task))
        else:
            print("No tasks found.")


if __name__ == "__main__":
    main()
