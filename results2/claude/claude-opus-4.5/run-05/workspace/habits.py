#!/usr/bin/env python3
"""
Habit Tracker - A CLI tool to track daily habits and maintain streaks.
"""

import sqlite3
import argparse
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path.home() / ".habits.db"


def get_db():
    """Get database connection, creating tables if needed."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habits (
            id INTEGER PRIMARY KEY,
            name TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS completions (
            id INTEGER PRIMARY KEY,
            habit_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            FOREIGN KEY (habit_id) REFERENCES habits(id),
            UNIQUE(habit_id, date)
        )
    """)
    conn.commit()
    return conn


def add_habit(name: str):
    """Add a new habit to track."""
    conn = get_db()
    try:
        conn.execute(
            "INSERT INTO habits (name, created_at) VALUES (?, ?)",
            (name, datetime.now().isoformat())
        )
        conn.commit()
        print(f"Added habit: {name}")
    except sqlite3.IntegrityError:
        print(f"Habit '{name}' already exists")
    conn.close()


def remove_habit(name: str):
    """Remove a habit and its history."""
    conn = get_db()
    cursor = conn.execute("SELECT id FROM habits WHERE name = ?", (name,))
    row = cursor.fetchone()
    if row:
        conn.execute("DELETE FROM completions WHERE habit_id = ?", (row["id"],))
        conn.execute("DELETE FROM habits WHERE id = ?", (row["id"],))
        conn.commit()
        print(f"Removed habit: {name}")
    else:
        print(f"Habit '{name}' not found")
    conn.close()


def check_habit(name: str, date: str = None):
    """Mark a habit as complete for a date (default: today)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.execute("SELECT id FROM habits WHERE name = ?", (name,))
    row = cursor.fetchone()
    if not row:
        print(f"Habit '{name}' not found")
        conn.close()
        return

    try:
        conn.execute(
            "INSERT INTO completions (habit_id, date) VALUES (?, ?)",
            (row["id"], date)
        )
        conn.commit()
        print(f"Checked off '{name}' for {date}")
    except sqlite3.IntegrityError:
        print(f"'{name}' already checked for {date}")
    conn.close()


def uncheck_habit(name: str, date: str = None):
    """Unmark a habit for a date (default: today)."""
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    conn = get_db()
    cursor = conn.execute("SELECT id FROM habits WHERE name = ?", (name,))
    row = cursor.fetchone()
    if not row:
        print(f"Habit '{name}' not found")
        conn.close()
        return

    conn.execute(
        "DELETE FROM completions WHERE habit_id = ? AND date = ?",
        (row["id"], date)
    )
    conn.commit()
    print(f"Unchecked '{name}' for {date}")
    conn.close()


def get_streak(conn, habit_id: int) -> tuple[int, int]:
    """Calculate current streak and longest streak for a habit."""
    cursor = conn.execute(
        "SELECT date FROM completions WHERE habit_id = ? ORDER BY date DESC",
        (habit_id,)
    )
    dates = [row["date"] for row in cursor.fetchall()]

    if not dates:
        return 0, 0

    # Current streak
    current = 0
    today = datetime.now().date()
    check_date = today

    for d in dates:
        date_obj = datetime.strptime(d, "%Y-%m-%d").date()
        if date_obj == check_date:
            current += 1
            check_date -= timedelta(days=1)
        elif date_obj == check_date - timedelta(days=1):
            # Allow checking yesterday if today not yet done
            if check_date == today:
                check_date = date_obj
                current += 1
                check_date -= timedelta(days=1)
            else:
                break
        else:
            break

    # Longest streak
    longest = 0
    if dates:
        dates_sorted = sorted(dates)
        streak = 1
        for i in range(1, len(dates_sorted)):
            prev = datetime.strptime(dates_sorted[i-1], "%Y-%m-%d").date()
            curr = datetime.strptime(dates_sorted[i], "%Y-%m-%d").date()
            if (curr - prev).days == 1:
                streak += 1
            else:
                longest = max(longest, streak)
                streak = 1
        longest = max(longest, streak)

    return current, longest


def list_habits():
    """List all habits with today's status and streaks."""
    conn = get_db()
    today = datetime.now().strftime("%Y-%m-%d")

    cursor = conn.execute("SELECT id, name FROM habits ORDER BY name")
    habits = cursor.fetchall()

    if not habits:
        print("No habits yet. Add one with: habits add <name>")
        conn.close()
        return

    print(f"\n{'Habit':<20} {'Today':<8} {'Streak':<10} {'Best':<10}")
    print("-" * 50)

    for habit in habits:
        # Check if done today
        cursor = conn.execute(
            "SELECT 1 FROM completions WHERE habit_id = ? AND date = ?",
            (habit["id"], today)
        )
        done_today = cursor.fetchone() is not None

        current, longest = get_streak(conn, habit["id"])

        status = "[x]" if done_today else "[ ]"
        streak_display = f"{current} days" if current > 0 else "-"
        best_display = f"{longest} days" if longest > 0 else "-"

        print(f"{habit['name']:<20} {status:<8} {streak_display:<10} {best_display:<10}")

    print()
    conn.close()


def show_stats(days: int = 30):
    """Show completion statistics for the last N days."""
    conn = get_db()
    start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    cursor = conn.execute("SELECT id, name FROM habits ORDER BY name")
    habits = cursor.fetchall()

    if not habits:
        print("No habits yet.")
        conn.close()
        return

    print(f"\nStats for last {days} days:\n")
    print(f"{'Habit':<20} {'Completed':<12} {'Rate':<10}")
    print("-" * 45)

    for habit in habits:
        cursor = conn.execute(
            """SELECT COUNT(*) as count FROM completions
               WHERE habit_id = ? AND date >= ?""",
            (habit["id"], start_date)
        )
        count = cursor.fetchone()["count"]
        rate = (count / days) * 100

        print(f"{habit['name']:<20} {count:<12} {rate:.0f}%")

    print()
    conn.close()


def show_calendar(name: str, weeks: int = 4):
    """Show a calendar view of habit completions."""
    conn = get_db()
    cursor = conn.execute("SELECT id FROM habits WHERE name = ?", (name,))
    row = cursor.fetchone()

    if not row:
        print(f"Habit '{name}' not found")
        conn.close()
        return

    habit_id = row["id"]
    today = datetime.now().date()
    start = today - timedelta(days=weeks * 7 - 1)

    cursor = conn.execute(
        """SELECT date FROM completions
           WHERE habit_id = ? AND date >= ?""",
        (habit_id, start.strftime("%Y-%m-%d"))
    )
    completed = {row["date"] for row in cursor.fetchall()}

    print(f"\nCalendar for '{name}' (last {weeks} weeks):\n")
    print("Mon Tue Wed Thu Fri Sat Sun")

    # Align to Monday
    current = start - timedelta(days=start.weekday())

    while current <= today:
        week = []
        for _ in range(7):
            if current < start or current > today:
                week.append("   ")
            elif current.strftime("%Y-%m-%d") in completed:
                week.append(" # ")
            else:
                week.append(" . ")
            current += timedelta(days=1)
        print("".join(week))

    print("\n# = completed, . = missed\n")
    conn.close()


def main():
    parser = argparse.ArgumentParser(
        description="Track daily habits and maintain streaks",
        prog="habits"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # add
    add_parser = subparsers.add_parser("add", help="Add a new habit")
    add_parser.add_argument("name", help="Name of the habit")

    # remove
    rm_parser = subparsers.add_parser("remove", help="Remove a habit")
    rm_parser.add_argument("name", help="Name of the habit")

    # check
    check_parser = subparsers.add_parser("check", help="Mark habit done")
    check_parser.add_argument("name", help="Name of the habit")
    check_parser.add_argument("--date", "-d", help="Date (YYYY-MM-DD)")

    # uncheck
    uncheck_parser = subparsers.add_parser("uncheck", help="Unmark habit")
    uncheck_parser.add_argument("name", help="Name of the habit")
    uncheck_parser.add_argument("--date", "-d", help="Date (YYYY-MM-DD)")

    # list
    subparsers.add_parser("list", help="List all habits")

    # stats
    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("--days", "-d", type=int, default=30)

    # calendar
    cal_parser = subparsers.add_parser("calendar", help="Show calendar view")
    cal_parser.add_argument("name", help="Name of the habit")
    cal_parser.add_argument("--weeks", "-w", type=int, default=4)

    args = parser.parse_args()

    if args.command == "add":
        add_habit(args.name)
    elif args.command == "remove":
        remove_habit(args.name)
    elif args.command == "check":
        check_habit(args.name, args.date)
    elif args.command == "uncheck":
        uncheck_habit(args.name, args.date)
    elif args.command == "list":
        list_habits()
    elif args.command == "stats":
        show_stats(args.days)
    elif args.command == "calendar":
        show_calendar(args.name, args.weeks)
    else:
        # Default: show list
        list_habits()


if __name__ == "__main__":
    main()
