#!/usr/bin/env python3
"""Personal task management CLI tool."""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

import click
from tabulate import tabulate


TASKS_FILE = Path.home() / ".task_manager.json"


def load_tasks() -> list[dict]:
    """Load tasks from JSON file."""
    if TASKS_FILE.exists():
        with open(TASKS_FILE, "r") as f:
            return json.load(f)
    return []


def save_tasks(tasks: list[dict]) -> None:
    """Save tasks to JSON file."""
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=2)


def next_task_id(tasks: list[dict]) -> int:
    """Get the next task ID."""
    if not tasks:
        return 1
    return max(t["id"] for t in tasks) + 1


@click.group()
def cli():
    """Personal task manager - manage your todos with ease."""
    pass


@cli.command()
@click.argument("title")
@click.option(
    "-p",
    "--priority",
    type=click.Choice(["low", "medium", "high"]),
    default="medium",
    help="Task priority level",
)
@click.option("-d", "--due", help="Due date (YYYY-MM-DD)")
def add(title: str, priority: str, due: Optional[str]) -> None:
    """Add a new task."""
    tasks = load_tasks()
    task = {
        "id": next_task_id(tasks),
        "title": title,
        "priority": priority,
        "due": due,
        "status": "pending",
        "created": datetime.now().isoformat(),
    }
    tasks.append(task)
    save_tasks(tasks)
    click.secho(f"✓ Task added (ID: {task['id']})", fg="green")


@cli.command()
@click.option("-s", "--status", type=click.Choice(["pending", "done", "all"]), default="all")
@click.option("-p", "--priority", type=click.Choice(["low", "medium", "high", "all"]), default="all")
@click.option("--sort", type=click.Choice(["id", "priority", "due"]), default="id", help="Sort results")
def list(status: str, priority: str, sort: str) -> None:
    """List all tasks."""
    tasks = load_tasks()

    if status != "all":
        tasks = [t for t in tasks if t["status"] == status]
    if priority != "all":
        tasks = [t for t in tasks if t["priority"] == priority]

    if not tasks:
        click.echo("No tasks found.")
        return

    # Sort tasks
    priority_order = {"high": 0, "medium": 1, "low": 2}
    if sort == "priority":
        tasks.sort(key=lambda t: priority_order[t["priority"]])
    elif sort == "due":
        tasks.sort(key=lambda t: (t["due"] or "z", t["id"]))

    # Format for display
    table_data = []
    for task in tasks:
        status_icon = "✓" if task["status"] == "done" else "○"
        priority_color = {"high": "red", "medium": "yellow", "low": "green"}[task["priority"]]
        due_str = task["due"] or "-"
        table_data.append(
            [
                task["id"],
                status_icon,
                task["title"],
                task["priority"],
                due_str,
            ]
        )

    headers = ["ID", "Status", "Title", "Priority", "Due"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))


@cli.command()
@click.argument("task_id", type=int)
def complete(task_id: int) -> None:
    """Mark a task as complete."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        click.secho(f"✗ Task {task_id} not found", fg="red")
        return

    task["status"] = "done"
    save_tasks(tasks)
    click.secho(f"✓ Task {task_id} marked as done", fg="green")


@cli.command()
@click.argument("task_id", type=int)
def delete(task_id: int) -> None:
    """Delete a task."""
    tasks = load_tasks()
    original_count = len(tasks)
    tasks = [t for t in tasks if t["id"] != task_id]

    if len(tasks) == original_count:
        click.secho(f"✗ Task {task_id} not found", fg="red")
        return

    save_tasks(tasks)
    click.secho(f"✓ Task {task_id} deleted", fg="green")


@cli.command()
@click.argument("query")
def search(query: str) -> None:
    """Search tasks by title or content."""
    tasks = load_tasks()
    query_lower = query.lower()
    results = [t for t in tasks if query_lower in t["title"].lower()]

    if not results:
        click.echo(f"No tasks found matching '{query}'")
        return

    table_data = [
        [
            t["id"],
            "✓" if t["status"] == "done" else "○",
            t["title"],
            t["priority"],
            t["due"] or "-",
        ]
        for t in results
    ]

    headers = ["ID", "Status", "Title", "Priority", "Due"]
    click.echo(tabulate(table_data, headers=headers, tablefmt="grid"))


@cli.command()
@click.argument("task_id", type=int)
def show(task_id: int) -> None:
    """Show detailed information about a task."""
    tasks = load_tasks()
    task = next((t for t in tasks if t["id"] == task_id), None)

    if not task:
        click.secho(f"✗ Task {task_id} not found", fg="red")
        return

    click.echo(f"\nTask #{task['id']}")
    click.echo(f"  Title:    {task['title']}")
    click.echo(f"  Status:   {task['status']}")
    click.echo(f"  Priority: {task['priority']}")
    click.echo(f"  Due:      {task['due'] or 'N/A'}")
    click.echo(f"  Created:  {task['created']}\n")


@cli.command()
def stats() -> None:
    """Show task statistics."""
    tasks = load_tasks()

    if not tasks:
        click.echo("No tasks yet.")
        return

    total = len(tasks)
    done = sum(1 for t in tasks if t["status"] == "done")
    pending = total - done
    high_priority = sum(1 for t in tasks if t["priority"] == "high" and t["status"] == "pending")

    click.echo(f"\nTask Statistics:")
    click.echo(f"  Total:      {total}")
    click.echo(f"  Done:       {done} ({done * 100 // total}%)")
    click.echo(f"  Pending:    {pending}")
    click.echo(f"  High Pri:   {high_priority}\n")


if __name__ == "__main__":
    cli()
