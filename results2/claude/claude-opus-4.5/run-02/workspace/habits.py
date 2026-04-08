#!/usr/bin/env python3
"""
Habit Tracker CLI - Track your daily habits with streaks and progress visualization.
"""

import argparse
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".habits.json"

def load_data():
    """Load habit data from file."""
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"habits": {}}

def save_data(data):
    """Save habit data to file."""
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

def today_str():
    """Get today's date as string."""
    return datetime.now().strftime("%Y-%m-%d")

def add_habit(name):
    """Add a new habit to track."""
    data = load_data()
    if name in data["habits"]:
        print(f"❌ Habit '{name}' already exists.")
        return
    data["habits"][name] = {"created": today_str(), "completions": []}
    save_data(data)
    print(f"✅ Added habit: {name}")

def remove_habit(name):
    """Remove a habit."""
    data = load_data()
    if name not in data["habits"]:
        print(f"❌ Habit '{name}' not found.")
        return
    del data["habits"][name]
    save_data(data)
    print(f"🗑️  Removed habit: {name}")

def complete_habit(name):
    """Mark a habit as complete for today."""
    data = load_data()
    if name not in data["habits"]:
        print(f"❌ Habit '{name}' not found.")
        return
    today = today_str()
    if today in data["habits"][name]["completions"]:
        print(f"⚡ Already completed '{name}' today!")
        return
    data["habits"][name]["completions"].append(today)
    save_data(data)
    streak = calculate_streak(data["habits"][name]["completions"])
    print(f"🎉 Completed '{name}'! Current streak: {streak} day(s)")

def calculate_streak(completions):
    """Calculate current streak for a habit."""
    if not completions:
        return 0

    completions_set = set(completions)
    today = datetime.now().date()
    streak = 0
    current = today

    # Check if today or yesterday is completed (allow for not-yet-done today)
    if today.strftime("%Y-%m-%d") not in completions_set:
        current = today - timedelta(days=1)
        if current.strftime("%Y-%m-%d") not in completions_set:
            return 0

    while current.strftime("%Y-%m-%d") in completions_set:
        streak += 1
        current -= timedelta(days=1)

    return streak

def render_progress_bar(completed, total, width=20):
    """Render a progress bar."""
    if total == 0:
        return "░" * width
    filled = int((completed / total) * width)
    return "█" * filled + "░" * (width - filled)

def render_week_view(completions):
    """Render last 7 days as a mini calendar."""
    today = datetime.now().date()
    completions_set = set(completions)
    days = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        if day_str in completions_set:
            days.append("●")
        else:
            days.append("○")
    return " ".join(days)

def list_habits():
    """List all habits with their stats."""
    data = load_data()
    habits = data["habits"]

    if not habits:
        print("No habits yet. Add one with: habits add <name>")
        return

    print("\n╔══════════════════════════════════════════════════════════════╗")
    print("║                     🌟 HABIT TRACKER 🌟                      ║")
    print("╠══════════════════════════════════════════════════════════════╣")

    today = today_str()

    for name, info in habits.items():
        completions = info["completions"]
        streak = calculate_streak(completions)
        total = len(completions)
        done_today = today in completions

        status = "✅" if done_today else "⬜"
        week = render_week_view(completions)

        # Habit name and status
        print(f"║ {status} {name:<20} Streak: {streak:>3}🔥  Total: {total:>4}    ║")
        print(f"║    Last 7 days: {week}                          ║")
        print("╠══════════════════════════════════════════════════════════════╣")

    print("╚══════════════════════════════════════════════════════════════╝")

    # Summary
    completed_today = sum(1 for h in habits.values() if today in h["completions"])
    total_habits = len(habits)
    progress = render_progress_bar(completed_today, total_habits, 30)
    print(f"\n  Today's Progress: [{progress}] {completed_today}/{total_habits}")
    print()

def show_stats(name=None):
    """Show detailed statistics."""
    data = load_data()
    habits = data["habits"]

    if name:
        if name not in habits:
            print(f"❌ Habit '{name}' not found.")
            return
        habits = {name: habits[name]}

    print("\n📊 DETAILED STATISTICS")
    print("=" * 50)

    for habit_name, info in habits.items():
        completions = info["completions"]
        streak = calculate_streak(completions)
        total = len(completions)
        created = info["created"]

        # Calculate days since created
        created_date = datetime.strptime(created, "%Y-%m-%d").date()
        days_tracked = (datetime.now().date() - created_date).days + 1
        completion_rate = (total / days_tracked * 100) if days_tracked > 0 else 0

        print(f"\n  {habit_name}")
        print(f"  ├─ Created: {created}")
        print(f"  ├─ Current Streak: {streak} days 🔥")
        print(f"  ├─ Total Completions: {total}")
        print(f"  ├─ Days Tracked: {days_tracked}")
        print(f"  └─ Completion Rate: {completion_rate:.1f}%")

        # Monthly view (last 30 days)
        print(f"\n  Last 30 days:")
        completions_set = set(completions)
        today = datetime.now().date()

        row = "  "
        for i in range(29, -1, -1):
            day = today - timedelta(days=i)
            if day.strftime("%Y-%m-%d") in completions_set:
                row += "█"
            else:
                row += "░"
        print(row)

    print()

def main():
    parser = argparse.ArgumentParser(
        description="🌟 Habit Tracker - Build better habits, one day at a time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  habits add "Exercise"      Add a new habit
  habits done "Exercise"     Mark habit complete for today
  habits list                View all habits and progress
  habits stats               Show detailed statistics
  habits remove "Exercise"   Remove a habit
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", help="Name of the habit")

    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a habit")
    remove_parser.add_argument("name", help="Name of the habit")

    # Done command
    done_parser = subparsers.add_parser("done", help="Mark habit as complete today")
    done_parser.add_argument("name", help="Name of the habit")

    # List command
    subparsers.add_parser("list", help="List all habits")

    # Stats command
    stats_parser = subparsers.add_parser("stats", help="Show detailed statistics")
    stats_parser.add_argument("name", nargs="?", help="Habit name (optional)")

    args = parser.parse_args()

    if args.command == "add":
        add_habit(args.name)
    elif args.command == "remove":
        remove_habit(args.name)
    elif args.command == "done":
        complete_habit(args.name)
    elif args.command == "list":
        list_habits()
    elif args.command == "stats":
        show_stats(args.name)
    else:
        # Default to list if no command
        list_habits()

if __name__ == "__main__":
    main()
