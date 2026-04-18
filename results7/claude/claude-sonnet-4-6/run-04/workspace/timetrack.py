#!/usr/bin/env python3
"""
timetrack — a minimal terminal time tracker.

Usage:
  timetrack start <task name>   Begin tracking a task
  timetrack stop                Stop the current task
  timetrack status              Show what's running right now
  timetrack log [days]          Show a summary (default: today)
  timetrack edit <id> <name>    Rename an entry by its ID
  timetrack delete <id>         Delete an entry by its ID
  timetrack clear               Wipe all data (asks for confirmation)
"""

import sys
import json
import os
import time
from datetime import datetime, date, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".timetrack.json"

# ANSI colors
R = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
CYAN = "\033[36m"
MAGENTA = "\033[35m"
RED = "\033[31m"
BLUE = "\033[34m"
WHITE = "\033[97m"

BAR_COLORS = [CYAN, MAGENTA, YELLOW, GREEN, BLUE]


def load() -> dict:
    if DATA_FILE.exists():
        with open(DATA_FILE) as f:
            return json.load(f)
    return {"entries": [], "active": None}


def save(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def fmt_duration(seconds: float) -> str:
    seconds = int(seconds)
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}h {m:02d}m"
    if m:
        return f"{m}m {s:02d}s"
    return f"{s}s"


def bar(fraction: float, width: int = 24, color: str = CYAN) -> str:
    filled = round(fraction * width)
    return color + "█" * filled + DIM + "░" * (width - filled) + R


def cmd_start(data: dict, task: str):
    if data["active"]:
        # auto-stop previous task
        _stop_active(data)
    entry = {
        "id": len(data["entries"]) + 1,
        "task": task,
        "start": time.time(),
        "end": None,
    }
    data["active"] = entry
    save(data)
    now = datetime.now().strftime("%H:%M")
    print(f"{GREEN}▶{R} {BOLD}{task}{R}  {DIM}started at {now}{R}")


def _stop_active(data: dict) -> dict | None:
    active = data["active"]
    if not active:
        return None
    active["end"] = time.time()
    active["duration"] = active["end"] - active["start"]
    data["entries"].append(active)
    data["active"] = None
    return active


def cmd_stop(data: dict):
    entry = _stop_active(data)
    if not entry:
        print(f"{YELLOW}No task is running.{R}")
        return
    save(data)
    d = fmt_duration(entry["duration"])
    print(f"{RED}■{R} {BOLD}{entry['task']}{R}  {DIM}stopped — {d}{R}")


def cmd_status(data: dict):
    active = data["active"]
    if not active:
        print(f"{DIM}Nothing running.{R}")
        return
    elapsed = time.time() - active["start"]
    started = datetime.fromtimestamp(active["start"]).strftime("%H:%M")
    print(
        f"{GREEN}▶{R} {BOLD}{active['task']}{R}  "
        f"{CYAN}{fmt_duration(elapsed)}{R}  {DIM}since {started}{R}"
    )


def cmd_log(data: dict, days: int = 1):
    # Collect all entries (include active as in-progress)
    entries = list(data["entries"])
    if data["active"]:
        a = dict(data["active"])
        a["end"] = time.time()
        a["duration"] = a["end"] - a["start"]
        entries.append(a)

    cutoff = datetime.combine(date.today() - timedelta(days=days - 1), datetime.min.time())
    cutoff_ts = cutoff.timestamp()

    entries = [e for e in entries if e.get("end", 0) >= cutoff_ts]
    if not entries:
        label = "today" if days == 1 else f"last {days} days"
        print(f"{DIM}No entries for {label}.{R}")
        return

    # Aggregate by task name
    totals: dict[str, float] = {}
    for e in entries:
        totals[e["task"]] = totals.get(e["task"], 0) + e.get("duration", 0)

    total_all = sum(totals.values())
    label = "Today" if days == 1 else f"Last {days} days"
    print(f"\n{BOLD}{WHITE}{label} — {fmt_duration(total_all)} tracked{R}\n")

    sorted_tasks = sorted(totals.items(), key=lambda x: x[1], reverse=True)
    max_dur = sorted_tasks[0][1]
    name_w = max(len(t) for t, _ in sorted_tasks)

    for i, (task, dur) in enumerate(sorted_tasks):
        color = BAR_COLORS[i % len(BAR_COLORS)]
        pct = dur / total_all * 100
        b = bar(dur / max_dur, width=20, color=color)
        print(
            f"  {color}{BOLD}{task:<{name_w}}{R}  "
            f"{b}  {color}{fmt_duration(dur)}{R}  {DIM}{pct:.0f}%{R}"
        )

    # Per-day breakdown when multiple days requested
    if days > 1:
        print(f"\n{BOLD}{DIM}Daily breakdown:{R}")
        for d in range(days - 1, -1, -1):
            day = date.today() - timedelta(days=d)
            day_start = datetime.combine(day, datetime.min.time()).timestamp()
            day_end = day_start + 86400
            day_dur = sum(
                e.get("duration", 0)
                for e in entries
                if day_start <= e.get("end", 0) < day_end
            )
            if day_dur:
                day_label = "Today" if d == 0 else day.strftime("%a %b %d")
                b = bar(day_dur / total_all, width=16, color=CYAN)
                print(f"  {DIM}{day_label:<12}{R}  {b}  {CYAN}{fmt_duration(day_dur)}{R}")
    print()

    # Show raw entries
    print(f"{BOLD}{DIM}  {'#':>3}  {'Task':<{name_w}}  {'Start':>8}  {'Duration':>9}{R}")
    visible = [e for e in entries if e.get("end", 0) >= cutoff_ts]
    visible.sort(key=lambda e: e["start"])
    for e in visible:
        started = datetime.fromtimestamp(e["start"]).strftime("%H:%M")
        dur = fmt_duration(e.get("duration", 0))
        is_active = data["active"] and e["start"] == data["active"]["start"]
        marker = f"{GREEN}▶{R}" if is_active else f"{DIM} {R}"
        tid = e.get("id", "?")
        print(
            f"  {DIM}{tid:>3}{R}  {marker}{e['task']:<{name_w}}  "
            f"{DIM}{started:>8}{R}  {CYAN}{dur:>9}{R}"
        )
    print()


def cmd_edit(data: dict, entry_id: int, new_name: str):
    for e in data["entries"]:
        if e.get("id") == entry_id:
            old = e["task"]
            e["task"] = new_name
            save(data)
            print(f"{GREEN}✓{R} #{entry_id} renamed: {DIM}{old}{R} → {BOLD}{new_name}{R}")
            return
    if data["active"] and data["active"].get("id") == entry_id:
        old = data["active"]["task"]
        data["active"]["task"] = new_name
        save(data)
        print(f"{GREEN}✓{R} #{entry_id} renamed: {DIM}{old}{R} → {BOLD}{new_name}{R}")
        return
    print(f"{RED}Entry #{entry_id} not found.{R}")


def cmd_delete(data: dict, entry_id: int):
    for i, e in enumerate(data["entries"]):
        if e.get("id") == entry_id:
            name = e["task"]
            data["entries"].pop(i)
            save(data)
            print(f"{RED}✗{R} #{entry_id} {DIM}{name}{R} deleted.")
            return
    print(f"{RED}Entry #{entry_id} not found (cannot delete active task).{R}")


def cmd_clear(data: dict):
    ans = input(f"{YELLOW}Delete ALL data? Type 'yes' to confirm: {R}").strip()
    if ans == "yes":
        save({"entries": [], "active": None})
        print(f"{RED}✗{R} All data cleared.")
    else:
        print(f"{DIM}Aborted.{R}")


def usage():
    print(__doc__)


def main():
    args = sys.argv[1:]
    if not args:
        usage()
        return

    data = load()
    cmd = args[0].lower()

    if cmd == "start":
        if len(args) < 2:
            print(f"{RED}Usage: timetrack start <task name>{R}")
            sys.exit(1)
        cmd_start(data, " ".join(args[1:]))
    elif cmd == "stop":
        cmd_stop(data)
    elif cmd == "status":
        cmd_status(data)
    elif cmd == "log":
        days = int(args[1]) if len(args) > 1 else 1
        cmd_log(data, days)
    elif cmd == "edit":
        if len(args) < 3:
            print(f"{RED}Usage: timetrack edit <id> <new name>{R}")
            sys.exit(1)
        cmd_edit(data, int(args[1]), " ".join(args[2:]))
    elif cmd == "delete":
        if len(args) < 2:
            print(f"{RED}Usage: timetrack delete <id>{R}")
            sys.exit(1)
        cmd_delete(data, int(args[1]))
    elif cmd == "clear":
        cmd_clear(data)
    elif cmd in ("-h", "--help", "help"):
        usage()
    else:
        print(f"{RED}Unknown command: {cmd}{R}")
        usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
