#!/usr/bin/env python3
"""Pomodoro timer with session tracking and ASCII visualization."""

import time
import sys
import os
import json
import signal
import argparse
from datetime import datetime, date
from pathlib import Path

WORK_MINS = 25
SHORT_BREAK_MINS = 5
LONG_BREAK_MINS = 15
POMODOROS_BEFORE_LONG = 4
DATA_FILE = Path.home() / ".pomodoro_sessions.json"
BAR_WIDTH = 40

PHASE_LABELS = {
    "work": "FOCUS",
    "short_break": "SHORT BREAK",
    "long_break": "LONG BREAK",
}

PHASE_COLORS = {
    "work": "\033[91m",      # red
    "short_break": "\033[92m",  # green
    "long_break": "\033[94m",   # blue
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
}


def color(text, *keys):
    if not sys.stdout.isatty():
        return text
    prefix = "".join(PHASE_COLORS[k] for k in keys)
    return f"{prefix}{text}{PHASE_COLORS['reset']}"


def load_sessions():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"sessions": []}


def save_session(phase, duration_secs, completed):
    data = load_sessions()
    data["sessions"].append({
        "date": date.today().isoformat(),
        "time": datetime.now().strftime("%H:%M"),
        "phase": phase,
        "duration_secs": duration_secs,
        "completed": completed,
    })
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def today_stats():
    data = load_sessions()
    today = date.today().isoformat()
    today_sessions = [s for s in data["sessions"] if s["date"] == today]
    completed_pomodoros = sum(
        1 for s in today_sessions if s["phase"] == "work" and s["completed"]
    )
    total_focus_mins = sum(
        s["duration_secs"] for s in today_sessions if s["phase"] == "work" and s["completed"]
    ) // 60
    return completed_pomodoros, total_focus_mins


def render_bar(elapsed, total, phase):
    filled = int(BAR_WIDTH * elapsed / total) if total > 0 else 0
    filled = min(filled, BAR_WIDTH)
    empty = BAR_WIDTH - filled
    bar = color("█" * filled, phase.replace("_break", "_break") if "break" in phase else "work") + color("░" * empty, "dim")
    return f"[{bar}]"


def fmt_time(seconds):
    m, s = divmod(int(seconds), 60)
    return f"{m:02d}:{s:02d}"


def clear_line():
    sys.stdout.write("\r\033[K")
    sys.stdout.flush()


def bell():
    sys.stdout.write("\a")
    sys.stdout.flush()


def run_phase(phase, duration_mins, pomodoro_num, total_today):
    duration_secs = duration_mins * 60
    label = color(PHASE_LABELS[phase], "bold")
    phase_color = "work" if phase == "work" else ("short_break" if phase == "short_break" else "long_break")

    print(f"\n  {label}  — Pomodoro #{pomodoro_num}  |  Today: {total_today} completed")
    print()

    start = time.time()
    interrupted = False

    def handle_interrupt(sig, frame):
        nonlocal interrupted
        interrupted = True

    old_handler = signal.signal(signal.SIGINT, handle_interrupt)

    try:
        while True:
            elapsed = time.time() - start
            remaining = duration_secs - elapsed

            if remaining <= 0:
                break

            bar = render_bar(elapsed, duration_secs, phase_color)
            pct = int(100 * elapsed / duration_secs)
            time_str = color(fmt_time(remaining), "bold")
            clear_line()
            sys.stdout.write(f"  {bar}  {time_str}  {pct:3d}%")
            sys.stdout.flush()
            time.sleep(0.5)

            if interrupted:
                break

    finally:
        signal.signal(signal.SIGINT, old_handler)

    elapsed_secs = int(time.time() - start)
    completed = not interrupted

    clear_line()
    if completed:
        bell()
        print(f"  {color('✓ Done!', 'bold')}  ({fmt_time(elapsed_secs)} elapsed)")
    else:
        print(f"  {color('✗ Interrupted', 'dim')}  ({fmt_time(elapsed_secs)} elapsed)")

    save_session(phase, elapsed_secs, completed)
    return completed


def show_stats():
    data = load_sessions()
    sessions = data["sessions"]
    if not sessions:
        print("No sessions recorded yet.")
        return

    # Group by date
    by_date = {}
    for s in sessions:
        by_date.setdefault(s["date"], []).append(s)

    print(color("\n  Pomodoro History\n", "bold"))
    for day in sorted(by_date.keys(), reverse=True)[:7]:
        day_sessions = by_date[day]
        pomodoros = sum(1 for s in day_sessions if s["phase"] == "work" and s["completed"])
        focus_mins = sum(s["duration_secs"] for s in day_sessions if s["phase"] == "work" and s["completed"]) // 60
        dots = color("●" * pomodoros, "work") + color("○" * max(0, 8 - pomodoros), "dim")
        print(f"  {day}  {dots}  {pomodoros:2d} pomodoros  {focus_mins:3d} min focus")

    print()
    total_pomodoros = sum(1 for s in sessions if s["phase"] == "work" and s["completed"])
    total_mins = sum(s["duration_secs"] for s in sessions if s["phase"] == "work" and s["completed"]) // 60
    print(f"  All time: {color(str(total_pomodoros), 'bold')} pomodoros, {color(str(total_mins), 'bold')} min focus\n")


def main():
    parser = argparse.ArgumentParser(description="Pomodoro timer with session tracking")
    parser.add_argument("--stats", action="store_true", help="Show session history and exit")
    parser.add_argument("--work", type=int, default=WORK_MINS, metavar="MINS", help=f"Work duration (default {WORK_MINS})")
    parser.add_argument("--short-break", type=int, default=SHORT_BREAK_MINS, metavar="MINS", help=f"Short break (default {SHORT_BREAK_MINS})")
    parser.add_argument("--long-break", type=int, default=LONG_BREAK_MINS, metavar="MINS", help=f"Long break (default {LONG_BREAK_MINS})")
    parser.add_argument("--cycles", type=int, default=0, metavar="N", help="Stop after N pomodoros (0 = run forever)")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    print(color("\n  🍅 Pomodoro Timer", "bold"))
    print(color(f"  Work {args.work}m  |  Short break {args.short_break}m  |  Long break {args.long_break}m", "dim"))
    print(color("  Ctrl+C to skip/interrupt current phase\n", "dim"))

    pomodoro_count = 0
    cycle = 0

    try:
        while True:
            cycle += 1
            completed_today, _ = today_stats()

            completed = run_phase("work", args.work, cycle, completed_today)
            if completed:
                pomodoro_count += 1

            if args.cycles and pomodoro_count >= args.cycles:
                print(color(f"\n  Done! Completed {pomodoro_count} pomodoro(s).\n", "bold"))
                break

            if completed:
                completed_today, focus_mins = today_stats()
                print(color(f"  Today: {completed_today} pomodoros, {focus_mins} min focus", "dim"))

            if cycle % POMODOROS_BEFORE_LONG == 0:
                print(color("  Time for a long break!", "bold"))
                run_phase("long_break", args.long_break, cycle, completed_today)
            else:
                print(color("  Short break time.", "bold"))
                run_phase("short_break", args.short_break, cycle, completed_today)

            print(color("  Starting next pomodoro...", "dim"))
            time.sleep(1)

    except KeyboardInterrupt:
        completed_today, focus_mins = today_stats()
        print(color(f"\n\n  Session ended. Today: {completed_today} pomodoros, {focus_mins} min focus.\n", "bold"))


if __name__ == "__main__":
    main()
