#!/usr/bin/env python3
"""CLI Pomodoro timer with session tracking and statistics."""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".pomodoro_sessions.json"

def load_sessions():
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_session(duration_mins, completed, tag=None):
    sessions = load_sessions()
    sessions.append({
        "timestamp": datetime.now().isoformat(),
        "duration": duration_mins,
        "completed": completed,
        "tag": tag
    })
    with open(DATA_FILE, "w") as f:
        json.dump(sessions, f, indent=2)

def format_time(seconds):
    mins, secs = divmod(int(seconds), 60)
    return f"{mins:02d}:{secs:02d}"

def run_timer(duration_mins, tag=None):
    total_seconds = duration_mins * 60
    remaining = total_seconds
    start_time = time.time()

    print(f"\n🍅 Pomodoro started: {duration_mins} minutes")
    if tag:
        print(f"   Tag: {tag}")
    print("   Press Ctrl+C to cancel\n")

    try:
        while remaining > 0:
            elapsed = time.time() - start_time
            remaining = max(0, total_seconds - elapsed)
            progress = int((elapsed / total_seconds) * 30)
            bar = "█" * progress + "░" * (30 - progress)

            sys.stdout.write(f"\r   [{bar}] {format_time(remaining)} remaining")
            sys.stdout.flush()
            time.sleep(0.5)

        print("\n\n✅ Pomodoro complete! Time for a break.")
        save_session(duration_mins, completed=True, tag=tag)
        return True

    except KeyboardInterrupt:
        elapsed_mins = (time.time() - start_time) / 60
        print(f"\n\n⏹️  Cancelled after {elapsed_mins:.1f} minutes")
        if elapsed_mins >= 1:
            save_session(round(elapsed_mins), completed=False, tag=tag)
        return False

def show_stats(days=7):
    sessions = load_sessions()
    cutoff = datetime.now() - timedelta(days=days)

    recent = [s for s in sessions
              if datetime.fromisoformat(s["timestamp"]) > cutoff]

    if not recent:
        print(f"\nNo sessions in the last {days} days.")
        return

    completed = [s for s in recent if s["completed"]]
    total_mins = sum(s["duration"] for s in completed)

    print(f"\n📊 Statistics (last {days} days)")
    print(f"   Sessions completed: {len(completed)}/{len(recent)}")
    print(f"   Total focus time: {total_mins} minutes ({total_mins/60:.1f} hours)")

    tags = {}
    for s in completed:
        t = s.get("tag") or "untagged"
        tags[t] = tags.get(t, 0) + s["duration"]

    if tags:
        print("\n   By tag:")
        for tag, mins in sorted(tags.items(), key=lambda x: -x[1]):
            print(f"     {tag}: {mins} min")

def main():
    parser = argparse.ArgumentParser(description="Pomodoro timer with tracking")
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    start_parser = subparsers.add_parser("start", help="Start a pomodoro")
    start_parser.add_argument("-d", "--duration", type=int, default=25,
                              help="Duration in minutes (default: 25)")
    start_parser.add_argument("-t", "--tag", help="Tag for this session")

    stats_parser = subparsers.add_parser("stats", help="Show statistics")
    stats_parser.add_argument("-d", "--days", type=int, default=7,
                              help="Number of days to show (default: 7)")

    subparsers.add_parser("clear", help="Clear all session data")

    args = parser.parse_args()

    if args.command == "start":
        run_timer(args.duration, args.tag)
    elif args.command == "stats":
        show_stats(args.days)
    elif args.command == "clear":
        if DATA_FILE.exists():
            DATA_FILE.unlink()
            print("Session data cleared.")
        else:
            print("No data to clear.")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
