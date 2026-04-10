#!/usr/bin/env python3
"""
Habit Tracker CLI - Track daily habits with streaks and statistics.
"""

import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

DATA_FILE = Path.home() / ".habits.json"


def load_data() -> dict:
    """Load habit data from file."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"habits": {}, "completions": {}}


def save_data(data: dict) -> None:
    """Save habit data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def today() -> str:
    """Get today's date as string."""
    return datetime.now().strftime("%Y-%m-%d")


def calculate_streak(habit_name: str, data: dict) -> int:
    """Calculate current streak for a habit."""
    completions = data["completions"].get(habit_name, [])
    if not completions:
        return 0

    completions = sorted(completions, reverse=True)
    streak = 0
    check_date = datetime.now().date()

    # If not completed today, start checking from yesterday
    if today() not in completions:
        check_date = check_date - timedelta(days=1)

    for _ in range(len(completions) + 1):
        date_str = check_date.strftime("%Y-%m-%d")
        if date_str in completions:
            streak += 1
            check_date -= timedelta(days=1)
        else:
            break

    return streak


def calculate_total_completions(habit_name: str, data: dict) -> int:
    """Get total number of completions for a habit."""
    return len(data["completions"].get(habit_name, []))


def add_habit(name: str, description: str = "") -> None:
    """Add a new habit to track."""
    data = load_data()
    if name in data["habits"]:
        print(f"Habit '{name}' already exists.")
        return

    data["habits"][name] = {
        "description": description,
        "created": today()
    }
    data["completions"][name] = []
    save_data(data)
    print(f"Added habit: {name}")


def remove_habit(name: str) -> None:
    """Remove a habit."""
    data = load_data()
    if name not in data["habits"]:
        print(f"Habit '{name}' not found.")
        return

    del data["habits"][name]
    if name in data["completions"]:
        del data["completions"][name]
    save_data(data)
    print(f"Removed habit: {name}")


def complete_habit(name: str) -> None:
    """Mark a habit as complete for today."""
    data = load_data()
    if name not in data["habits"]:
        print(f"Habit '{name}' not found.")
        return

    if name not in data["completions"]:
        data["completions"][name] = []

    if today() in data["completions"][name]:
        print(f"'{name}' already completed today!")
        return

    data["completions"][name].append(today())
    save_data(data)

    streak = calculate_streak(name, data)
    print(f"Completed '{name}' for today! Current streak: {streak} day(s)")


def uncomplete_habit(name: str) -> None:
    """Unmark a habit for today."""
    data = load_data()
    if name not in data["habits"]:
        print(f"Habit '{name}' not found.")
        return

    if today() not in data["completions"].get(name, []):
        print(f"'{name}' was not marked complete today.")
        return

    data["completions"][name].remove(today())
    save_data(data)
    print(f"Unmarked '{name}' for today.")


def show_status() -> None:
    """Show status of all habits for today."""
    data = load_data()

    if not data["habits"]:
        print("No habits tracked yet. Add one with: habit add <name>")
        return

    print(f"\n{'='*50}")
    print(f"  HABIT TRACKER - {today()}")
    print(f"{'='*50}\n")

    completed_today = 0
    total_habits = len(data["habits"])

    for name, info in sorted(data["habits"].items()):
        is_done = today() in data["completions"].get(name, [])
        streak = calculate_streak(name, data)
        total = calculate_total_completions(name, data)

        status = "[x]" if is_done else "[ ]"
        if is_done:
            completed_today += 1

        streak_display = f"[{streak} day streak]" if streak > 0 else ""
        print(f"  {status} {name:<20} {streak_display}")
        if info.get("description"):
            print(f"      {info['description']}")

    print(f"\n{'─'*50}")
    print(f"  Progress: {completed_today}/{total_habits} completed today")

    if completed_today == total_habits and total_habits > 0:
        print("  All habits completed! Great job!")
    print()


def show_stats() -> None:
    """Show detailed statistics for all habits."""
    data = load_data()

    if not data["habits"]:
        print("No habits to show stats for.")
        return

    print(f"\n{'='*50}")
    print("  HABIT STATISTICS")
    print(f"{'='*50}\n")

    for name, info in sorted(data["habits"].items()):
        streak = calculate_streak(name, data)
        total = calculate_total_completions(name, data)
        created = info.get("created", "unknown")

        # Calculate days since creation
        try:
            created_date = datetime.strptime(created, "%Y-%m-%d")
            days_tracked = (datetime.now() - created_date).days + 1
            completion_rate = (total / days_tracked * 100) if days_tracked > 0 else 0
        except ValueError:
            days_tracked = 0
            completion_rate = 0

        print(f"  {name}")
        print(f"  {'─'*40}")
        print(f"    Current Streak:   {streak} day(s)")
        print(f"    Total Completions: {total}")
        print(f"    Days Tracked:     {days_tracked}")
        print(f"    Completion Rate:  {completion_rate:.1f}%")
        print(f"    Started:          {created}")
        print()


def print_help() -> None:
    """Print help message."""
    print("""
Habit Tracker - Track your daily habits

Usage:
  habit                     Show today's habit status
  habit add <name> [desc]   Add a new habit to track
  habit remove <name>       Remove a habit
  habit done <name>         Mark habit complete for today
  habit undo <name>         Unmark habit for today
  habit stats               Show detailed statistics
  habit list                List all habits
  habit help                Show this help message

Examples:
  habit add exercise "30 minutes of workout"
  habit done exercise
  habit stats
""")


def list_habits() -> None:
    """List all habits."""
    data = load_data()

    if not data["habits"]:
        print("No habits tracked yet.")
        return

    print("\nTracked Habits:")
    for name, info in sorted(data["habits"].items()):
        desc = f" - {info['description']}" if info.get("description") else ""
        print(f"  - {name}{desc}")
    print()


def main() -> None:
    """Main entry point."""
    import sys

    args = sys.argv[1:]

    if not args:
        show_status()
        return

    command = args[0].lower()

    if command == "help" or command == "--help" or command == "-h":
        print_help()
    elif command == "add" and len(args) >= 2:
        name = args[1]
        description = " ".join(args[2:]) if len(args) > 2 else ""
        add_habit(name, description)
    elif command == "remove" and len(args) >= 2:
        remove_habit(args[1])
    elif command == "done" and len(args) >= 2:
        complete_habit(args[1])
    elif command == "undo" and len(args) >= 2:
        uncomplete_habit(args[1])
    elif command == "stats":
        show_stats()
    elif command == "list":
        list_habits()
    elif command == "status":
        show_status()
    else:
        print(f"Unknown command: {command}")
        print("Run 'habit help' for usage information.")


if __name__ == "__main__":
    main()
