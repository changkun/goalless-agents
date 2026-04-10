#!/usr/bin/env python3
"""
Habit Tracker CLI - Track daily habits with streak visualization
"""

import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".habits.json"

def load_data():
    """Load habits data from file."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"habits": {}}

def save_data(data):
    """Save habits data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def today_str():
    """Get today's date as string."""
    return datetime.now().strftime("%Y-%m-%d")

def date_range(start_date, days):
    """Generate a range of dates."""
    start = datetime.strptime(start_date, "%Y-%m-%d")
    return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]

def calculate_streak(completions):
    """Calculate current streak for a habit."""
    if not completions:
        return 0

    sorted_dates = sorted(completions, reverse=True)
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)

    # Check if the most recent completion is today or yesterday
    most_recent = datetime.strptime(sorted_dates[0], "%Y-%m-%d").date()
    if most_recent < yesterday:
        return 0

    streak = 1
    for i in range(1, len(sorted_dates)):
        current = datetime.strptime(sorted_dates[i-1], "%Y-%m-%d").date()
        prev = datetime.strptime(sorted_dates[i], "%Y-%m-%d").date()
        if (current - prev).days == 1:
            streak += 1
        else:
            break

    return streak

def render_calendar(completions, weeks=4):
    """Render a GitHub-style contribution calendar."""
    end_date = datetime.now()
    start_date = end_date - timedelta(days=weeks * 7 - 1)

    # Build calendar grid
    lines = []
    days = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

    # Header with week numbers
    lines.append("    " + " ".join(f"W{(start_date + timedelta(days=i*7)).isocalendar()[1]:02d}" for i in range(weeks)))

    for day_idx in range(7):
        row = f"{days[day_idx]} "
        current = start_date + timedelta(days=(day_idx - start_date.weekday()) % 7)

        for week in range(weeks):
            date = current + timedelta(days=week * 7)
            if date > end_date:
                row += "    "
            elif date.strftime("%Y-%m-%d") in completions:
                row += " \033[32m[*]\033[0m"  # Green filled
            else:
                row += " [ ]"  # Empty
        lines.append(row)

    return "\n".join(lines)

def cmd_add(args):
    """Add a new habit to track."""
    if not args:
        print("Usage: habits add <habit_name>")
        return

    name = " ".join(args)
    data = load_data()

    if name in data["habits"]:
        print(f"Habit '{name}' already exists!")
        return

    data["habits"][name] = {
        "created": today_str(),
        "completions": []
    }
    save_data(data)
    print(f"Added habit: {name}")

def cmd_done(args):
    """Mark a habit as done for today."""
    if not args:
        print("Usage: habits done <habit_name>")
        return

    name = " ".join(args)
    data = load_data()

    if name not in data["habits"]:
        print(f"Habit '{name}' not found. Use 'habits list' to see your habits.")
        return

    today = today_str()
    if today in data["habits"][name]["completions"]:
        print(f"'{name}' already completed today!")
        return

    data["habits"][name]["completions"].append(today)
    save_data(data)

    streak = calculate_streak(data["habits"][name]["completions"])
    print(f"Completed '{name}' for today!")

    # Streak celebration
    if streak >= 7:
        print(f"\033[33m{'*' * 20}\033[0m")
        print(f"\033[33m  {streak} DAY STREAK!\033[0m")
        print(f"\033[33m{'*' * 20}\033[0m")
    else:
        print(f"Current streak: {streak} day{'s' if streak != 1 else ''}")

def cmd_list(args):
    """List all habits with their streaks."""
    data = load_data()

    if not data["habits"]:
        print("No habits yet! Add one with: habits add <name>")
        return

    today = today_str()
    print("\n\033[1mYour Habits\033[0m")
    print("-" * 50)

    for name, habit in sorted(data["habits"].items()):
        streak = calculate_streak(habit["completions"])
        done_today = today in habit["completions"]
        total = len(habit["completions"])

        status = "\033[32m[*]\033[0m" if done_today else "[ ]"
        streak_display = f"\033[33m{streak}\033[0m" if streak >= 7 else str(streak)

        print(f"{status} {name}")
        print(f"    Streak: {streak_display} days | Total: {total} completions")

    print()

def cmd_view(args):
    """View detailed stats and calendar for a habit."""
    if not args:
        print("Usage: habits view <habit_name>")
        return

    name = " ".join(args)
    data = load_data()

    if name not in data["habits"]:
        print(f"Habit '{name}' not found.")
        return

    habit = data["habits"][name]
    completions = set(habit["completions"])
    streak = calculate_streak(completions)

    print(f"\n\033[1m{name}\033[0m")
    print("=" * 40)
    print(f"Created: {habit['created']}")
    print(f"Current streak: {streak} days")
    print(f"Total completions: {len(completions)}")

    if completions:
        # Calculate completion rate (last 30 days)
        last_30 = set(date_range((datetime.now() - timedelta(days=29)).strftime("%Y-%m-%d"), 30))
        completed_last_30 = len(completions & last_30)
        rate = (completed_last_30 / 30) * 100
        print(f"Last 30 days: {completed_last_30}/30 ({rate:.0f}%)")

    print(f"\n\033[1mActivity (last 4 weeks):\033[0m")
    print(render_calendar(completions))
    print()

def cmd_remove(args):
    """Remove a habit."""
    if not args:
        print("Usage: habits remove <habit_name>")
        return

    name = " ".join(args)
    data = load_data()

    if name not in data["habits"]:
        print(f"Habit '{name}' not found.")
        return

    del data["habits"][name]
    save_data(data)
    print(f"Removed habit: {name}")

def cmd_undo(args):
    """Undo today's completion for a habit."""
    if not args:
        print("Usage: habits undo <habit_name>")
        return

    name = " ".join(args)
    data = load_data()

    if name not in data["habits"]:
        print(f"Habit '{name}' not found.")
        return

    today = today_str()
    if today not in data["habits"][name]["completions"]:
        print(f"'{name}' wasn't completed today.")
        return

    data["habits"][name]["completions"].remove(today)
    save_data(data)
    print(f"Undid completion of '{name}' for today.")

def cmd_help(args):
    """Show help message."""
    print("""
\033[1mHabit Tracker\033[0m - Track your daily habits

\033[1mCommands:\033[0m
  add <name>      Add a new habit to track
  done <name>     Mark a habit as done for today
  undo <name>     Undo today's completion
  list            List all habits with streaks
  view <name>     View detailed stats and calendar
  remove <name>   Remove a habit
  help            Show this help message

\033[1mExamples:\033[0m
  habits add Exercise
  habits done Exercise
  habits view Exercise
""")

def main():
    commands = {
        "add": cmd_add,
        "done": cmd_done,
        "list": cmd_list,
        "view": cmd_view,
        "remove": cmd_remove,
        "undo": cmd_undo,
        "help": cmd_help,
    }

    if len(sys.argv) < 2:
        cmd_list([])
        return

    cmd = sys.argv[1].lower()
    args = sys.argv[2:]

    if cmd in commands:
        commands[cmd](args)
    else:
        print(f"Unknown command: {cmd}")
        print("Use 'habits help' for available commands.")

if __name__ == "__main__":
    main()
