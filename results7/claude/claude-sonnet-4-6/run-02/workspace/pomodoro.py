#!/usr/bin/env python3
"""Pomodoro timer with session history and stats."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, date
from pathlib import Path

HISTORY_FILE = Path.home() / ".pomodoro_sessions.json"

# ANSI colors
RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
BLUE   = "\033[94m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

BAR_WIDTH = 40


def supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def colorize(text: str, *codes: str) -> str:
    if not supports_color():
        return text
    return "".join(codes) + text + RESET


def load_history() -> list[dict]:
    if not HISTORY_FILE.exists():
        return []
    try:
        return json.loads(HISTORY_FILE.read_text())
    except (json.JSONDecodeError, OSError):
        return []


def save_session(kind: str, duration_minutes: int, completed: bool) -> None:
    history = load_history()
    history.append({
        "date": datetime.now().isoformat(),
        "kind": kind,
        "duration_minutes": duration_minutes,
        "completed": completed,
    })
    try:
        HISTORY_FILE.write_text(json.dumps(history, indent=2))
    except OSError as e:
        print(colorize(f"Warning: could not save session: {e}", YELLOW), file=sys.stderr)


def render_bar(elapsed: float, total: float) -> str:
    pct = min(elapsed / total, 1.0)
    filled = int(BAR_WIDTH * pct)
    empty = BAR_WIDTH - filled
    bar = colorize("█" * filled, GREEN) + colorize("░" * empty, DIM)
    pct_str = colorize(f"{int(pct * 100):3d}%", BOLD)
    return f"[{bar}] {pct_str}"


def format_time(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def run_timer(label: str, kind: str, duration_minutes: int) -> bool:
    total = duration_minutes * 60
    start = time.monotonic()

    color = GREEN if kind == "work" else CYAN
    header = colorize(f"\n  {label}", BOLD + color)
    print(header)
    print(colorize(f"  Duration: {duration_minutes} min  |  Press Ctrl+C to stop early\n", DIM))

    completed = False
    try:
        while True:
            elapsed = time.monotonic() - start
            remaining = total - elapsed

            if remaining <= 0:
                completed = True
                break

            bar = render_bar(elapsed, total)
            time_str = colorize(format_time(remaining), BOLD)
            line = f"\r  {bar}  {time_str} remaining  "
            sys.stdout.write(line)
            sys.stdout.flush()
            time.sleep(0.5)

    except KeyboardInterrupt:
        elapsed = time.monotonic() - start
        print(f"\n\n  {colorize('Stopped early', YELLOW)} after {format_time(elapsed)}.")

    print()
    return completed


def cmd_work(args: argparse.Namespace) -> None:
    completed = run_timer("Work Session", "work", args.minutes)
    save_session("work", args.minutes, completed)
    if completed:
        print(colorize("  Session complete! Take a break.", BOLD + GREEN))
    print()


def cmd_break(args: argparse.Namespace) -> None:
    completed = run_timer("Break", "break", args.minutes)
    save_session("break", args.minutes, completed)
    if completed:
        print(colorize("  Break over. Back to work!", BOLD + CYAN))
    print()


def cmd_stats(args: argparse.Namespace) -> None:
    history = load_history()
    if not history:
        print(colorize("\n  No sessions recorded yet. Run: pomodoro work\n", DIM))
        return

    today_str = date.today().isoformat()
    today_sessions = [s for s in history if s["date"].startswith(today_str)]

    work_all   = [s for s in history if s["kind"] == "work" and s["completed"]]
    work_today = [s for s in today_sessions if s["kind"] == "work" and s["completed"]]

    total_work_min_all   = sum(s["duration_minutes"] for s in work_all)
    total_work_min_today = sum(s["duration_minutes"] for s in work_today)

    # streak: count consecutive days with at least one completed work session
    days_with_work = sorted({s["date"][:10] for s in work_all}, reverse=True)
    streak = 0
    prev = date.today()
    for d in days_with_work:
        day = date.fromisoformat(d)
        if (prev - day).days <= 1:
            streak += 1
            prev = day
        else:
            break

    print(colorize("\n  Pomodoro Stats", BOLD + BLUE))
    print(colorize("  " + "─" * 36, DIM))
    print(f"  Today:       {colorize(str(len(work_today)), BOLD)} sessions  "
          f"({colorize(f'{total_work_min_today} min', BOLD)} focused)")
    print(f"  All time:    {colorize(str(len(work_all)), BOLD)} sessions  "
          f"({colorize(f'{total_work_min_all} min', BOLD)} focused)")
    print(f"  Day streak:  {colorize(str(streak), BOLD + YELLOW)} {'day' if streak == 1 else 'days'}")
    print(colorize("  " + "─" * 36, DIM))

    # last 5 sessions
    recent = history[-5:][::-1]
    print(colorize("\n  Recent sessions:", DIM))
    for s in recent:
        ts   = s["date"][11:16]
        kind = s["kind"].capitalize()
        dur  = s["duration_minutes"]
        done = colorize("✓", GREEN) if s["completed"] else colorize("✗", RED)
        print(f"    {done}  {colorize(ts, DIM)}  {kind:<6} {dur} min")
    print()


def cmd_clear(args: argparse.Namespace) -> None:
    if not HISTORY_FILE.exists():
        print("No history to clear.")
        return
    confirm = input(colorize("  Clear all session history? [y/N] ", YELLOW))
    if confirm.strip().lower() == "y":
        HISTORY_FILE.unlink()
        print(colorize("  History cleared.", GREEN))
    else:
        print("  Aborted.")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="pomodoro",
        description="Pomodoro timer with session history",
    )
    sub = parser.add_subparsers(dest="command", metavar="COMMAND")

    p_work = sub.add_parser("work", help="Start a work session (default 25 min)")
    p_work.add_argument("-m", "--minutes", type=int, default=25,
                        metavar="N", help="Duration in minutes")
    p_work.set_defaults(func=cmd_work)

    p_break = sub.add_parser("break", help="Start a break (default 5 min)")
    p_break.add_argument("-m", "--minutes", type=int, default=5,
                         metavar="N", help="Duration in minutes")
    p_break.set_defaults(func=cmd_break)

    p_stats = sub.add_parser("stats", help="Show session statistics")
    p_stats.set_defaults(func=cmd_stats)

    p_clear = sub.add_parser("clear", help="Clear session history")
    p_clear.set_defaults(func=cmd_clear)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        sys.exit(0)

    args.func(args)


if __name__ == "__main__":
    main()
