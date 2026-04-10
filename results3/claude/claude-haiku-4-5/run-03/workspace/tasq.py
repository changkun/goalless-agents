#!/usr/bin/env python3
"""
TASQ - A simple yet powerful task manager CLI.
Manage tasks with projects, priorities, and persistent storage.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import argparse
import textwrap

DATA_FILE = Path.home() / ".tasq_tasks.json"


def get_due_status(due_date: Optional[str]) -> tuple[str, bool]:
    """
    Return (status_indicator, is_overdue).
    Status: 🔴 overdue, 🟡 due soon (next 3 days), ⚪ normal
    """
    if not due_date:
        return "⚪", False

    try:
        due = datetime.fromisoformat(due_date).date()
        today = datetime.now().date()
        days_until = (due - today).days

        if days_until < 0:
            return "🔴", True
        elif days_until <= 3:
            return "🟡", False
        else:
            return "⚪", False
    except (ValueError, AttributeError):
        return "⚪", False


def is_overdue(due_date: Optional[str]) -> bool:
    """Check if task is overdue."""
    _, overdue = get_due_status(due_date)
    return overdue


def load_tasks() -> dict:
    """Load tasks from storage or initialize empty."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"tasks": [], "next_id": 1}


def save_tasks(data: dict) -> None:
    """Save tasks to storage."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_task(title: str, project: str = "inbox", priority: str = "normal", due: Optional[str] = None) -> None:
    """Add a new task."""
    data = load_tasks()
    task = {
        "id": data["next_id"],
        "title": title,
        "project": project,
        "priority": priority,
        "completed": False,
        "created": datetime.now().isoformat(),
        "due": due,
    }
    data["tasks"].append(task)
    data["next_id"] += 1
    save_tasks(data)
    print(f"✓ Added task #{task['id']}: {title}")


def list_tasks(
    project: Optional[str] = None,
    status: str = "all",
    sort_by: str = "created",
    show_overdue: bool = False,
) -> None:
    """List tasks with filtering and sorting."""
    data = load_tasks()
    tasks = data["tasks"]

    # Filter by project
    if project:
        tasks = [t for t in tasks if t["project"] == project]

    # Filter by status
    if status == "done":
        tasks = [t for t in tasks if t["completed"]]
    elif status == "pending":
        tasks = [t for t in tasks if not t["completed"]]

    # Filter for overdue only
    if show_overdue:
        tasks = [t for t in tasks if is_overdue(t.get("due"))]

    # Sort
    if sort_by == "priority":
        priority_order = {"high": 0, "normal": 1, "low": 2}
        tasks.sort(key=lambda t: priority_order.get(t["priority"], 1))
    elif sort_by == "created":
        tasks.sort(key=lambda t: t["created"])
    elif sort_by == "due":
        tasks.sort(key=lambda t: (t.get("due") or "z"), reverse=False)

    if not tasks:
        print("No tasks found.")
        return

    # Print header
    print(f"\n{'ID':<4} {'✓':<3} {'Due':<3} {'Priority':<8} {'Project':<12} {'Title':<35}")
    print("-" * 80)

    for task in tasks:
        status_icon = "✓" if task["completed"] else " "
        due_indicator, _ = get_due_status(task.get("due"))
        title = task["title"][:35]
        print(
            f"{task['id']:<4} {status_icon:<3} {due_indicator:<3} {task['priority']:<8} {task['project']:<12} {title:<35}"
        )

    # Print stats
    total = len(tasks)
    completed = sum(1 for t in tasks if t["completed"])
    overdue = sum(1 for t in tasks if is_overdue(t.get("due")) and not t["completed"])
    print(f"\nTotal: {total} | Completed: {completed} | Pending: {total - completed}", end="")
    if overdue:
        print(f" | 🔴 Overdue: {overdue}", end="")
    print()


def complete_task(task_id: int) -> None:
    """Mark a task as complete."""
    data = load_tasks()
    for task in data["tasks"]:
        if task["id"] == task_id:
            task["completed"] = True
            save_tasks(data)
            print(f"✓ Completed task #{task_id}")
            return
    print(f"Task #{task_id} not found.")


def delete_task(task_id: int) -> None:
    """Delete a task."""
    data = load_tasks()
    original_len = len(data["tasks"])
    data["tasks"] = [t for t in data["tasks"] if t["id"] != task_id]
    if len(data["tasks"]) < original_len:
        save_tasks(data)
        print(f"✓ Deleted task #{task_id}")
    else:
        print(f"Task #{task_id} not found.")


def show_stats() -> None:
    """Show task statistics."""
    data = load_tasks()
    tasks = data["tasks"]

    if not tasks:
        print("No tasks yet.")
        return

    by_project = {}
    by_priority = {"high": 0, "normal": 0, "low": 0}
    total_completed = 0
    total_overdue = 0

    for task in tasks:
        project = task["project"]
        if project not in by_project:
            by_project[project] = {"total": 0, "completed": 0}
        by_project[project]["total"] += 1
        if task["completed"]:
            by_project[project]["completed"] += 1
            total_completed += 1
        else:
            if is_overdue(task.get("due")):
                total_overdue += 1
        by_priority[task["priority"]] += 1

    print("\n📊 Task Statistics")
    print("=" * 40)
    print(f"Total tasks: {len(tasks)}")
    print(f"Completed: {total_completed} ({total_completed*100//len(tasks)}%)")
    pending = len(tasks) - total_completed
    print(f"Pending: {pending}", end="")
    if total_overdue:
        print(f" (🔴 {total_overdue} overdue)", end="")
    print()
    print("\nBy Priority:")
    for priority in ["high", "normal", "low"]:
        print(f"  {priority.capitalize()}: {by_priority[priority]}")
    print("\nBy Project:")
    for project, counts in sorted(by_project.items()):
        print(
            f"  {project}: {counts['completed']}/{counts['total']} completed"
        )


def main():
    parser = argparse.ArgumentParser(
        description="TASQ - A simple task manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Examples:
              tasq add "Buy groceries"
              tasq add "Implement auth" --project backend --priority high --due 2026-04-20
              tasq list
              tasq list --overdue
              tasq list --sort due
              tasq list --project inbox --status pending
              tasq done 1
              tasq delete 1
              tasq stats
            """
        ),
    )

    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument(
        "--project", default="inbox", help="Project name (default: inbox)"
    )
    add_parser.add_argument(
        "--priority",
        choices=["high", "normal", "low"],
        default="normal",
        help="Task priority (default: normal)",
    )
    add_parser.add_argument(
        "--due", help="Due date (YYYY-MM-DD format, e.g., 2026-04-15)"
    )

    # List command
    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--project", help="Filter by project")
    list_parser.add_argument(
        "--status",
        choices=["all", "done", "pending"],
        default="all",
        help="Filter by status (default: all)",
    )
    list_parser.add_argument(
        "--sort",
        choices=["created", "priority", "due"],
        default="created",
        dest="sort_by",
        help="Sort by (default: created)",
    )
    list_parser.add_argument(
        "--overdue",
        action="store_true",
        help="Show only overdue tasks",
    )

    # Done command
    done_parser = subparsers.add_parser("done", help="Mark task as complete")
    done_parser.add_argument("task_id", type=int, help="Task ID")

    # Delete command
    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("task_id", type=int, help="Task ID")

    # Stats command
    subparsers.add_parser("stats", help="Show task statistics")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.title, args.project, args.priority, getattr(args, "due", None))
    elif args.command == "list":
        list_tasks(args.project, args.status, args.sort_by, args.overdue)
    elif args.command == "done":
        complete_task(args.task_id)
    elif args.command == "delete":
        delete_task(args.task_id)
    elif args.command == "stats":
        show_stats()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
