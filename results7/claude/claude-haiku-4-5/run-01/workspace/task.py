#!/usr/bin/env python3
import json
import sys
from datetime import datetime
from pathlib import Path
import argparse
from typing import List, Dict, Any

TASKS_FILE = Path.home() / ".tasks.json"


def load_tasks() -> List[Dict[str, Any]]:
    if TASKS_FILE.exists():
        with open(TASKS_FILE) as f:
            return json.load(f)
    return []


def save_tasks(tasks: List[Dict[str, Any]]) -> None:
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def add_task(title: str, priority: str = "medium", due_date: str = None) -> None:
    tasks = load_tasks()
    task = {
        "id": max((t.get("id", 0) for t in tasks), default=0) + 1,
        "title": title,
        "priority": priority,
        "due_date": due_date,
        "completed": False,
        "created": datetime.now().isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    print(f"✓ Added task #{task['id']}: {title}")


def list_tasks(priority: str = None, show_completed: bool = False) -> None:
    tasks = load_tasks()

    if not tasks:
        print("No tasks yet. Add one with: task add '<title>'")
        return

    filtered = [t for t in tasks if not t.get("completed") or show_completed]
    if priority:
        filtered = [t for t in filtered if t["priority"] == priority]

    if not filtered:
        print("No tasks found.")
        return

    priority_order = {"high": 0, "medium": 1, "low": 2}
    filtered.sort(key=lambda t: (t.get("completed"), priority_order.get(t["priority"], 3)))

    print("\n" + "─" * 70)
    for task in filtered:
        status = "✓" if task.get("completed") else " "
        due = f" | Due: {task['due_date']}" if task.get("due_date") else ""
        pri = f"[{task['priority'].upper()}]".ljust(8)
        print(f"[{status}] #{task['id']:<3} {pri} {task['title']}{due}")
    print("─" * 70 + "\n")


def complete_task(task_id: int) -> None:
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)
    if task:
        task["completed"] = True
        save_tasks(tasks)
        print(f"✓ Completed: {task['title']}")
    else:
        print(f"Task #{task_id} not found")


def delete_task(task_id: int) -> None:
    tasks = load_tasks()
    tasks = [t for t in tasks if t["id"] != task_id]
    save_tasks(tasks)
    print(f"✓ Deleted task #{task_id}")


def search_tasks(query: str) -> None:
    tasks = load_tasks()
    results = [t for t in tasks if query.lower() in t["title"].lower()]

    if not results:
        print(f"No tasks matching '{query}'")
        return

    print(f"\nSearch results for '{query}':")
    print("─" * 70)
    for task in results:
        status = "✓" if task.get("completed") else " "
        due = f" | Due: {task['due_date']}" if task.get("due_date") else ""
        pri = f"[{task['priority'].upper()}]".ljust(8)
        print(f"[{status}] #{task['id']:<3} {pri} {task['title']}{due}")
    print("─" * 70 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Quick task manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  task add 'Buy groceries'
  task add 'Fix bug' --priority high
  task add 'Call mom' --due 2026-05-01
  task list
  task list --priority high
  task complete 1
  task delete 2
  task search 'bug'
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")
    add_parser.add_argument("--priority", choices=["low", "medium", "high"], default="medium")
    add_parser.add_argument("--due", dest="due_date", help="Due date (YYYY-MM-DD)")

    list_parser = subparsers.add_parser("list", help="List tasks")
    list_parser.add_argument("--priority", choices=["low", "medium", "high"], help="Filter by priority")
    list_parser.add_argument("--all", action="store_true", help="Show completed tasks")

    complete_parser = subparsers.add_parser("complete", help="Mark task complete")
    complete_parser.add_argument("id", type=int, help="Task ID")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("id", type=int, help="Task ID")

    search_parser = subparsers.add_parser("search", help="Search tasks")
    search_parser.add_argument("query", help="Search query")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.title, args.priority, args.due_date)
    elif args.command == "list":
        list_tasks(args.priority, args.all)
    elif args.command == "complete":
        complete_task(args.id)
    elif args.command == "delete":
        delete_task(args.id)
    elif args.command == "search":
        search_tasks(args.query)
    else:
        list_tasks()


if __name__ == "__main__":
    main()
