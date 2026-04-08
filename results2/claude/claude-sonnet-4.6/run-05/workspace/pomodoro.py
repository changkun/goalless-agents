#!/usr/bin/env python3
"""
Pomodoro Timer - Terminal productivity timer with session tracking.

Usage:
    python pomodoro.py work           # 25-min work session
    python pomodoro.py break          # 5-min short break
    python pomodoro.py longbreak      # 15-min long break
    python pomodoro.py stats          # show productivity stats
    python pomodoro.py work -m 45     # custom duration
"""

import argparse
import json
import math
import os
import signal
import sys
import time
from datetime import datetime, date, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".pomodoro_sessions.json"

DURATIONS = {
    "work": 25,
    "break": 5,
    "longbreak": 15,
}

LABELS = {
    "work": "Work",
    "break": "Short Break",
    "longbreak": "Long Break",
}

COLORS = {
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "cyan": "\033[36m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "reset": "\033[0m",
}


def c(color: str, text: str) -> str:
    if not sys.stdout.isatty():
        return text
    return f"{COLORS[color]}{text}{COLORS['reset']}"


def bold(text: str) -> str:
    return c("bold", text)


def load_sessions() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    try:
        return json.loads(DATA_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def save_session(session_type: str, minutes: int, completed: bool) -> None:
    sessions = load_sessions()
    sessions.append({
        "type": session_type,
        "minutes": minutes,
        "completed": completed,
        "timestamp": datetime.now().isoformat(),
    })
    try:
        DATA_FILE.write_text(json.dumps(sessions, indent=2))
    except OSError as e:
        print(c("yellow", f"Warning: could not save session: {e}"), file=sys.stderr)


def bar(fraction: float, width: int = 30) -> str:
    filled = math.floor(fraction * width)
    empty = width - filled
    return c("green", "█" * filled) + c("dim", "░" * empty)


def clear_line() -> None:
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def run_timer(session_type: str, minutes: int) -> bool:
    label = LABELS.get(session_type, session_type.title())
    total_seconds = minutes * 60
    elapsed = 0
    completed = False

    interrupted = False

    def handle_interrupt(sig, frame):
        nonlocal interrupted
        interrupted = True

    original_handler = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, handle_interrupt)

    print(f"\n  {bold(label)} — {minutes} min")
    print(f"  Press Ctrl+C to stop early.\n")

    try:
        while elapsed <= total_seconds and not interrupted:
            remaining = total_seconds - elapsed
            mins, secs = divmod(remaining, 60)
            fraction = elapsed / total_seconds if total_seconds > 0 else 1.0

            timer_str = c("cyan", f"{mins:02d}:{secs:02d}")
            progress = bar(fraction)

            clear_line()
            sys.stdout.write(f"  {progress}  {timer_str} remaining ")
            sys.stdout.flush()

            time.sleep(1)
            elapsed += 1

        if not interrupted:
            completed = True
            clear_line()
            bell = "\a"
            print(f"  {bar(1.0)}  {c('green', '00:00')} done! {bell}")
            print(f"\n  {c('green', bold('✓'))} {label} complete! Great work.\n")
        else:
            remaining = total_seconds - elapsed
            mins, secs = divmod(remaining, 60)
            clear_line()
            print(f"\n  {c('yellow', 'Session stopped')} with {mins:02d}:{secs:02d} remaining.\n")

    finally:
        signal.signal(signal.SIGINT, original_handler)

    return completed


def stats() -> None:
    sessions = load_sessions()
    if not sessions:
        print(f"\n  {c('dim', 'No sessions recorded yet. Run a timer to get started!')}\n")
        return

    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    def parse_date(ts: str) -> date:
        return datetime.fromisoformat(ts).date()

    work_sessions = [s for s in sessions if s["type"] == "work"]
    completed_work = [s for s in work_sessions if s.get("completed")]

    today_work = [s for s in completed_work if parse_date(s["timestamp"]) == today]
    week_work = [s for s in completed_work if parse_date(s["timestamp"]) >= week_start]

    total_work_min = sum(s["minutes"] for s in completed_work)
    today_min = sum(s["minutes"] for s in today_work)
    week_min = sum(s["minutes"] for s in week_work)

    def fmt_time(mins: int) -> str:
        h, m = divmod(mins, 60)
        if h:
            return f"{h}h {m}m"
        return f"{m}m"

    print(f"\n  {bold('Pomodoro Stats')}\n")
    print(f"  {'Today':20s}  {c('cyan', str(len(today_work)))} sessions  ({c('cyan', fmt_time(today_min))})")
    print(f"  {'This week':20s}  {c('cyan', str(len(week_work)))} sessions  ({c('cyan', fmt_time(week_min))})")
    print(f"  {'All time':20s}  {c('cyan', str(len(completed_work)))} sessions  ({c('cyan', fmt_time(total_work_min))})")

    # Streak
    if completed_work:
        days_worked = sorted({parse_date(s["timestamp"]) for s in completed_work}, reverse=True)
        streak = 1
        for i in range(1, len(days_worked)):
            if (days_worked[i - 1] - days_worked[i]).days == 1:
                streak += 1
            else:
                break
        if days_worked[0] < today:
            streak = 0
        print(f"  {'Current streak':20s}  {c('yellow', str(streak))} day{'s' if streak != 1 else ''}")

    # Daily breakdown (last 7 days)
    print(f"\n  {bold('Last 7 days')}\n")
    for i in range(6, -1, -1):
        d = today - timedelta(days=i)
        day_sessions = [s for s in completed_work if parse_date(s["timestamp"]) == d]
        day_min = sum(s["minutes"] for s in day_sessions)
        count = len(day_sessions)
        label = "Today" if d == today else d.strftime("%a %b %-d")
        blocks = min(count, 8)
        block_str = c("green", "■" * blocks) + c("dim", "□" * (8 - blocks))
        time_str = c("dim", fmt_time(day_min)) if count else c("dim", "—")
        print(f"  {label:12s}  {block_str}  {time_str}")

    print()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pomodoro Timer — stay focused, track progress.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  %(prog)s work             # 25-min work session\n"
            "  %(prog)s break            # 5-min break\n"
            "  %(prog)s longbreak        # 15-min break\n"
            "  %(prog)s work -m 45       # custom 45-min session\n"
            "  %(prog)s stats            # show productivity stats\n"
        ),
    )
    parser.add_argument(
        "command",
        choices=["work", "break", "longbreak", "stats"],
        help="Timer type or stats view",
    )
    parser.add_argument(
        "-m", "--minutes",
        type=int,
        default=None,
        help="Override duration in minutes",
    )

    args = parser.parse_args()

    if args.command == "stats":
        stats()
        return

    minutes = args.minutes if args.minutes is not None else DURATIONS[args.command]
    if minutes <= 0:
        parser.error("Duration must be a positive number of minutes.")

    completed = run_timer(args.command, minutes)
    save_session(args.command, minutes, completed)


if __name__ == "__main__":
    main()
