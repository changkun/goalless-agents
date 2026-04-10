#!/usr/bin/env python3
"""
Pomodoro Timer CLI - A terminal-based productivity timer with task tracking.

Features:
- 25-minute work sessions, 5-minute short breaks, 15-minute long breaks
- Visual progress bar and countdown
- Task tracking with session history
- Persistent history saved to JSON
- Terminal bell notifications
"""

import argparse
import json
import os
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional

# ANSI color codes
class Colors:
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

# Default durations (in minutes)
WORK_DURATION = 25
SHORT_BREAK = 5
LONG_BREAK = 15
POMODOROS_UNTIL_LONG_BREAK = 4

# Demo mode durations (in seconds, displayed as minutes for demo)
DEMO_WORK = 0.1  # 6 seconds
DEMO_SHORT_BREAK = 0.05  # 3 seconds
DEMO_LONG_BREAK = 0.08  # ~5 seconds

HISTORY_FILE = Path.home() / ".pomodoro_history.json"


@dataclass
class PomodoroSession:
    task: str
    start_time: str
    end_time: str
    duration_minutes: int
    completed: bool
    session_type: str  # "work", "short_break", "long_break"


def load_history() -> list[dict]:
    """Load session history from file."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def save_session(session: PomodoroSession) -> None:
    """Save a session to history."""
    history = load_history()
    history.append(asdict(session))
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def clear_line() -> None:
    """Clear the current line."""
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def ring_bell() -> None:
    """Ring terminal bell."""
    sys.stdout.write("\a")
    sys.stdout.flush()


def format_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def create_progress_bar(progress: float, width: int = 30) -> str:
    """Create a visual progress bar."""
    filled = int(width * progress)
    empty = width - filled
    bar = "█" * filled + "░" * empty
    return f"[{bar}]"


def display_timer(
    remaining: int,
    total: int,
    session_type: str,
    task: Optional[str] = None,
    pomodoro_count: int = 0,
) -> None:
    """Display the timer with progress bar."""
    progress = 1 - (remaining / total)
    progress_bar = create_progress_bar(progress)
    time_str = format_time(remaining)

    # Choose color based on session type
    if session_type == "work":
        color = Colors.RED
        icon = "🍅"
        label = "WORK"
    elif session_type == "short_break":
        color = Colors.GREEN
        icon = "☕"
        label = "SHORT BREAK"
    else:
        color = Colors.BLUE
        icon = "🌴"
        label = "LONG BREAK"

    clear_line()

    # Build display string
    display = f"{color}{Colors.BOLD}{icon} {label}{Colors.RESET}"
    display += f" {progress_bar} {Colors.BOLD}{time_str}{Colors.RESET}"

    if task and session_type == "work":
        display += f" | {Colors.CYAN}{task}{Colors.RESET}"

    if pomodoro_count > 0:
        tomatoes = "🍅" * pomodoro_count
        display += f" | {tomatoes}"

    sys.stdout.write(display)
    sys.stdout.flush()


def run_timer(
    duration_minutes: float,
    session_type: str,
    task: Optional[str] = None,
    pomodoro_count: int = 0,
) -> bool:
    """
    Run a timer for the specified duration.
    Returns True if completed, False if interrupted.
    """
    total_seconds = int(duration_minutes * 60)
    remaining = total_seconds
    start_time = datetime.now().isoformat()

    print()  # New line before timer

    try:
        while remaining > 0:
            display_timer(remaining, total_seconds, session_type, task, pomodoro_count)
            time.sleep(1)
            remaining -= 1

        # Timer completed
        display_timer(0, total_seconds, session_type, task, pomodoro_count)
        print()  # New line after completion

        # Ring bell 3 times
        for _ in range(3):
            ring_bell()
            time.sleep(0.3)

        # Save session
        session = PomodoroSession(
            task=task or "",
            start_time=start_time,
            end_time=datetime.now().isoformat(),
            duration_minutes=duration_minutes,
            completed=True,
            session_type=session_type,
        )
        save_session(session)

        return True

    except KeyboardInterrupt:
        print()
        elapsed = total_seconds - remaining

        # Save incomplete session
        session = PomodoroSession(
            task=task or "",
            start_time=start_time,
            end_time=datetime.now().isoformat(),
            duration_minutes=elapsed // 60,
            completed=False,
            session_type=session_type,
        )
        save_session(session)

        print(f"{Colors.YELLOW}Session interrupted after {format_time(elapsed)}{Colors.RESET}")
        return False


def print_header() -> None:
    """Print the application header."""
    print(f"""
{Colors.RED}{Colors.BOLD}╔══════════════════════════════════════╗
║      🍅 POMODORO TIMER CLI 🍅        ║
╚══════════════════════════════════════╝{Colors.RESET}
""")


def start_pomodoro_cycle(task: Optional[str] = None, demo: bool = False) -> None:
    """Start a full Pomodoro cycle."""
    print_header()

    if demo:
        print(f"{Colors.YELLOW}{Colors.BOLD}🎬 DEMO MODE - Using shortened timers{Colors.RESET}")
        work_time = DEMO_WORK
        short_break_time = DEMO_SHORT_BREAK
        long_break_time = DEMO_LONG_BREAK
    else:
        work_time = WORK_DURATION
        short_break_time = SHORT_BREAK
        long_break_time = LONG_BREAK

    if task:
        print(f"{Colors.CYAN}Task: {task}{Colors.RESET}")

    pomodoro_count = 0

    while True:
        # Work session
        print(f"\n{Colors.RED}{Colors.BOLD}Starting work session #{pomodoro_count + 1}...{Colors.RESET}")
        print(f"{Colors.DIM}Press Ctrl+C to stop{Colors.RESET}")

        if not run_timer(work_time, "work", task, pomodoro_count):
            break

        pomodoro_count += 1
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Pomodoro #{pomodoro_count} complete!{Colors.RESET}")

        # Determine break type
        if pomodoro_count % POMODOROS_UNTIL_LONG_BREAK == 0:
            print(f"\n{Colors.BLUE}{Colors.BOLD}Time for a long break! You've earned it.{Colors.RESET}")
            if not run_timer(long_break_time, "long_break", pomodoro_count=pomodoro_count):
                break
        else:
            print(f"\n{Colors.GREEN}{Colors.BOLD}Time for a short break!{Colors.RESET}")
            if not run_timer(short_break_time, "short_break", pomodoro_count=pomodoro_count):
                break

        print(f"\n{Colors.YELLOW}Break's over! Ready for the next session?{Colors.RESET}")
        try:
            input(f"{Colors.DIM}Press Enter to continue or Ctrl+C to quit...{Colors.RESET}")
        except KeyboardInterrupt:
            print()
            break

    # Summary
    print(f"\n{Colors.MAGENTA}{Colors.BOLD}═══ SESSION SUMMARY ═══{Colors.RESET}")
    print(f"Completed pomodoros: {Colors.RED}{'🍅' * pomodoro_count}{Colors.RESET} ({pomodoro_count})")
    print(f"Total focus time: {Colors.BOLD}{pomodoro_count * WORK_DURATION} minutes{Colors.RESET}")


def show_history(days: int = 7) -> None:
    """Show session history."""
    print_header()
    history = load_history()

    if not history:
        print(f"{Colors.YELLOW}No sessions recorded yet. Start your first pomodoro!{Colors.RESET}")
        return

    # Filter to recent sessions
    cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
    recent = [
        s for s in history
        if datetime.fromisoformat(s["start_time"]).timestamp() > cutoff
    ]

    if not recent:
        print(f"{Colors.YELLOW}No sessions in the last {days} days.{Colors.RESET}")
        return

    print(f"{Colors.BOLD}Sessions from the last {days} days:{Colors.RESET}\n")

    # Group by date
    by_date: dict[str, list] = {}
    for session in recent:
        date = datetime.fromisoformat(session["start_time"]).strftime("%Y-%m-%d")
        by_date.setdefault(date, []).append(session)

    total_work_minutes = 0
    total_pomodoros = 0

    for date in sorted(by_date.keys(), reverse=True):
        sessions = by_date[date]
        work_sessions = [s for s in sessions if s["session_type"] == "work" and s["completed"]]
        day_minutes = sum(s["duration_minutes"] for s in work_sessions)
        total_work_minutes += day_minutes
        total_pomodoros += len(work_sessions)

        tomatoes = "🍅" * len(work_sessions) if work_sessions else "—"
        print(f"{Colors.CYAN}{date}{Colors.RESET}: {tomatoes} ({day_minutes} min)")

        # Show tasks for this day
        tasks = set(s["task"] for s in work_sessions if s["task"])
        if tasks:
            for task in tasks:
                print(f"  {Colors.DIM}• {task}{Colors.RESET}")

    print(f"\n{Colors.MAGENTA}{Colors.BOLD}═══ TOTALS ═══{Colors.RESET}")
    print(f"Total pomodoros: {Colors.RED}{'🍅' * min(total_pomodoros, 20)}{Colors.RESET} ({total_pomodoros})")
    print(f"Total focus time: {Colors.BOLD}{total_work_minutes} minutes ({total_work_minutes // 60}h {total_work_minutes % 60}m){Colors.RESET}")


def show_stats() -> None:
    """Show productivity statistics."""
    print_header()
    history = load_history()

    if not history:
        print(f"{Colors.YELLOW}No sessions recorded yet. Start your first pomodoro!{Colors.RESET}")
        return

    work_sessions = [s for s in history if s["session_type"] == "work"]
    completed = [s for s in work_sessions if s["completed"]]

    total_minutes = sum(s["duration_minutes"] for s in completed)
    total_hours = total_minutes / 60

    print(f"{Colors.MAGENTA}{Colors.BOLD}═══ ALL-TIME STATISTICS ═══{Colors.RESET}\n")
    print(f"Total pomodoros completed: {Colors.BOLD}{len(completed)}{Colors.RESET}")
    print(f"Total focus time: {Colors.BOLD}{total_minutes} minutes ({total_hours:.1f} hours){Colors.RESET}")
    print(f"Completion rate: {Colors.BOLD}{len(completed) / len(work_sessions) * 100:.1f}%{Colors.RESET}")

    # Most productive day
    by_date: dict[str, int] = {}
    for session in completed:
        date = datetime.fromisoformat(session["start_time"]).strftime("%Y-%m-%d")
        by_date[date] = by_date.get(date, 0) + 1

    if by_date:
        best_day = max(by_date.items(), key=lambda x: x[1])
        print(f"Most productive day: {Colors.CYAN}{best_day[0]}{Colors.RESET} ({best_day[1]} pomodoros)")

    # Streak calculation
    dates = sorted(set(
        datetime.fromisoformat(s["start_time"]).strftime("%Y-%m-%d")
        for s in completed
    ), reverse=True)

    if dates:
        today = datetime.now().strftime("%Y-%m-%d")
        streak = 0
        check_date = datetime.now()

        for _ in range(len(dates)):
            date_str = check_date.strftime("%Y-%m-%d")
            if date_str in dates:
                streak += 1
                check_date = check_date.replace(day=check_date.day - 1)
            else:
                break

        if streak > 0:
            print(f"Current streak: {Colors.GREEN}{Colors.BOLD}🔥 {streak} days{Colors.RESET}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Pomodoro Timer CLI - A terminal-based productivity timer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pomodoro                    Start a pomodoro session
  pomodoro -t "Write report"  Start with a task name
  pomodoro history            Show recent session history
  pomodoro stats              Show productivity statistics
        """,
    )

    parser.add_argument(
        "command",
        nargs="?",
        default="start",
        choices=["start", "history", "stats"],
        help="Command to run (default: start)",
    )
    parser.add_argument(
        "-t", "--task",
        help="Name of the task to work on",
    )
    parser.add_argument(
        "-d", "--days",
        type=int,
        default=7,
        help="Number of days to show in history (default: 7)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run in demo mode with shortened timers (for testing)",
    )

    args = parser.parse_args()

    try:
        if args.command == "start":
            start_pomodoro_cycle(args.task, demo=args.demo)
        elif args.command == "history":
            show_history(args.days)
        elif args.command == "stats":
            show_stats()
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Goodbye! Keep being productive! 🍅{Colors.RESET}")
        sys.exit(0)


if __name__ == "__main__":
    main()
