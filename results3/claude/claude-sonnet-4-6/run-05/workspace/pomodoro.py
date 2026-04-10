#!/usr/bin/env python3
"""
ASCII Pomodoro Timer — terminal-based focus timer with session tracking.

Usage:
  python3 pomodoro.py           # default: 25m work, 5m short break, 15m long break
  python3 pomodoro.py --work 45 --short 10 --long 20
  python3 pomodoro.py --stats   # show session history
"""

import argparse
import datetime
import json
import math
import os
import select
import signal
import sys
import termios
import time
import tty

HISTORY_FILE = os.path.expanduser("~/.pomodoro_history.json")

DIGITS = {
    "0": ["█████", "█   █", "█   █", "█   █", "█████"],
    "1": ["  █  ", "  █  ", "  █  ", "  █  ", "  █  "],
    "2": ["█████", "    █", "█████", "█    ", "█████"],
    "3": ["█████", "    █", "█████", "    █", "█████"],
    "4": ["█   █", "█   █", "█████", "    █", "    █"],
    "5": ["█████", "█    ", "█████", "    █", "█████"],
    "6": ["█████", "█    ", "█████", "█   █", "█████"],
    "7": ["█████", "    █", "    █", "    █", "    █"],
    "8": ["█████", "█   █", "█████", "█   █", "█████"],
    "9": ["█████", "█   █", "█████", "    █", "█████"],
    ":": ["     ", "  █  ", "     ", "  █  ", "     "],
}

COLORS = {
    "reset":  "\033[0m",
    "bold":   "\033[1m",
    "red":    "\033[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "cyan":   "\033[96m",
    "blue":   "\033[94m",
    "magenta":"\033[95m",
    "dim":    "\033[2m",
    "white":  "\033[97m",
}

def c(color, text):
    return f"{COLORS[color]}{text}{COLORS['reset']}"

def clear():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()

def move(row, col):
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()

def hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def get_terminal_size():
    try:
        cols, rows = os.get_terminal_size()
        return rows, cols
    except Exception:
        return 24, 80

def render_big_time(mm, ss):
    """Render MM:SS in large ASCII block digits."""
    time_str = f"{mm:02d}:{ss:02d}"
    rows_out = [""] * 5
    for ch in time_str:
        for i, row in enumerate(DIGITS[ch]):
            rows_out[i] += row + "  "
    return rows_out

def center_text(text, width):
    visible = text
    for code in COLORS.values():
        visible = visible.replace(code, "")
    pad = max(0, (width - len(visible)) // 2)
    return " " * pad + text

def render_progress_bar(elapsed, total, width=40):
    fraction = min(elapsed / total, 1.0)
    filled = int(fraction * width)
    bar = "█" * filled + "░" * (width - filled)
    pct = int(fraction * 100)
    return bar, pct

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {"sessions": [], "total_pomodoros": 0, "total_focus_minutes": 0}

def save_session(history, session_type, duration_minutes, completed):
    history["sessions"].append({
        "date": datetime.datetime.now().isoformat(),
        "type": session_type,
        "duration_minutes": duration_minutes,
        "completed": completed,
    })
    if session_type == "work" and completed:
        history["total_pomodoros"] += 1
        history["total_focus_minutes"] += duration_minutes
    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except Exception:
        pass

def show_stats():
    history = load_history()
    sessions = history["sessions"]
    total = history["total_pomodoros"]
    focus = history["total_focus_minutes"]

    print(c("cyan", "\n  ╔══════════════════════════════╗"))
    print(c("cyan", "  ║") + c("bold", "    POMODORO SESSION STATS    ") + c("cyan", "║"))
    print(c("cyan", "  ╚══════════════════════════════╝"))
    print()
    print(f"  {c('yellow', 'Total Pomodoros:')}  {c('white', str(total))}")
    print(f"  {c('yellow', 'Total Focus Time:')} {c('white', f'{focus // 60}h {focus % 60}m')}")
    print()

    if not sessions:
        print(c("dim", "  No sessions recorded yet.\n"))
        return

    print(c("dim", "  Last 10 sessions:"))
    print(c("dim", "  " + "─" * 48))
    for s in sessions[-10:][::-1]:
        dt = datetime.datetime.fromisoformat(s["date"])
        tag = c("green", "✓") if s["completed"] else c("red", "✗")
        kind = s["type"].ljust(5)
        kind_colored = c("cyan", kind) if s["type"] == "work" else c("magenta", kind)
        dur = f"{s['duration_minutes']}m"
        ts = dt.strftime("%b %d %H:%M")
        print(f"  {tag} {c('dim', ts)}  {kind_colored}  {c('dim', dur)}")
    print()

def kbhit(timeout=0):
    """Non-blocking keyboard check."""
    return select.select([sys.stdin], [], [], timeout)[0]

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
    return ch

def run_timer(label, duration_sec, color, session_num, total_sessions, history):
    """Run a single timer phase. Returns True if completed, False if skipped/quit."""
    start = time.time()
    completed = False
    paused = False
    pause_start = 0
    paused_total = 0

    hide_cursor()
    old_settings = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())

    def restore():
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        show_cursor()

    signal.signal(signal.SIGINT, lambda *_: None)  # handle below

    try:
        while True:
            now = time.time()
            if paused:
                elapsed = pause_start - start - paused_total
            else:
                elapsed = now - start - paused_total

            remaining = max(0, duration_sec - elapsed)
            mm = int(remaining) // 60
            ss = int(remaining) % 60

            rows, cols = get_terminal_size()
            clear()

            # Header
            move(1, 1)
            header = f"  POMODORO  ·  Session {session_num}/{total_sessions}"
            sys.stdout.write(c("dim", header))

            # Phase label
            move(2, 1)
            phase_line = center_text(c(color, c("bold", f"◈  {label}  ◈")), cols)
            sys.stdout.write(phase_line)

            # Big clock
            time_rows = render_big_time(mm, ss)
            start_row = max(4, rows // 2 - 5)
            for i, row in enumerate(time_rows):
                move(start_row + i, 1)
                styled = c(color, row) if remaining > 60 else c("red", row)
                sys.stdout.write(center_text(styled, cols))

            # Progress bar
            bar, pct = render_progress_bar(elapsed, duration_sec, width=min(50, cols - 12))
            move(start_row + 6, 1)
            bar_line = center_text(c(color, bar) + c("dim", f" {pct}%"), cols)
            sys.stdout.write(bar_line)

            # Spinning indicator
            spinner = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"
            spin_ch = spinner[int(elapsed * 4) % len(spinner)] if not paused else "⏸"
            move(start_row + 7, 1)
            spin_line = center_text(c("dim", spin_ch), cols)
            sys.stdout.write(spin_line)

            # Controls
            move(rows - 2, 1)
            if paused:
                controls = c("dim", "  [r] resume  [s] skip  [q] quit")
            else:
                controls = c("dim", "  [p] pause  [s] skip  [q] quit")
            sys.stdout.write(controls)

            # Pause banner
            if paused:
                move(start_row + 4, 1)
                banner = center_text(c("yellow", c("bold", "  ⏸  PAUSED  ")), cols)
                sys.stdout.write(banner)

            sys.stdout.flush()

            if remaining <= 0:
                completed = True
                break

            # Check keypress (non-blocking)
            if select.select([sys.stdin], [], [], 0.1)[0]:
                ch = sys.stdin.read(1).lower()
                if ch == "q" or ch == "\x03":  # q or ctrl-c
                    break
                elif ch == "s":
                    break
                elif ch == "p" and not paused:
                    paused = True
                    pause_start = time.time()
                elif ch == "r" and paused:
                    paused_total += time.time() - pause_start
                    paused = False
            else:
                time.sleep(0.05)

    finally:
        restore()
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)
        signal.signal(signal.SIGINT, signal.SIG_DFL)

    return completed

def completion_screen(label, completed):
    rows, cols = get_terminal_size()
    clear()
    hide_cursor()
    time.sleep(0.1)

    if completed:
        lines = [
            "",
            c("green", c("bold", "  ✓ COMPLETE!")),
            "",
            c("white", f"  {label} session finished."),
            "",
            c("dim", "  Press any key to continue..."),
        ]
    else:
        lines = [
            "",
            c("yellow", "  ⏭  SKIPPED"),
            "",
            c("dim", "  Press any key to continue..."),
        ]

    start = rows // 2 - len(lines) // 2
    for i, line in enumerate(lines):
        move(start + i, 1)
        sys.stdout.write(center_text(line, cols))
    sys.stdout.flush()

    old = termios.tcgetattr(sys.stdin.fileno())
    tty.setraw(sys.stdin.fileno())
    try:
        sys.stdin.read(1)
    finally:
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
        show_cursor()

def run_pomodoro(work, short_break, long_break, cycles):
    history = load_history()

    # Build schedule: [work, short, work, short, ..., work, long]
    schedule = []
    for i in range(cycles):
        schedule.append(("work", work * 60, "green"))
        if i < cycles - 1:
            schedule.append(("short break", short_break * 60, "cyan"))
        else:
            schedule.append(("long break", long_break * 60, "magenta"))

    total = len(schedule)
    quit_requested = False

    for idx, (label, duration, color) in enumerate(schedule):
        if quit_requested:
            break

        rows, cols = get_terminal_size()
        clear()
        hide_cursor()

        # Upcoming screen
        move(rows // 2 - 1, 1)
        if label == "work":
            icon = "🍅" if sys.stdout.encoding and "UTF" in sys.stdout.encoding.upper() else "o"
            msg = c("green", c("bold", f"  ◈ Starting work session {idx // 2 + 1}/{cycles}"))
        elif "short" in label:
            msg = c("cyan", c("bold", "  ☕  Short break time!"))
        else:
            msg = c("magenta", c("bold", "  🌿  Long break — great work!"))

        sys.stdout.write(center_text(msg, cols))
        move(rows // 2 + 1, 1)
        sys.stdout.write(center_text(c("dim", "Starting in 2 seconds... [q to quit]"), cols))
        sys.stdout.flush()
        show_cursor()

        # 2s countdown with quit check
        old = termios.tcgetattr(sys.stdin.fileno())
        tty.setraw(sys.stdin.fileno())
        try:
            for _ in range(20):
                if select.select([sys.stdin], [], [], 0.1)[0]:
                    ch = sys.stdin.read(1).lower()
                    if ch in ("q", "\x03"):
                        quit_requested = True
                        break
        finally:
            termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
            hide_cursor()

        if quit_requested:
            break

        completed = run_timer(label, duration, color, idx + 1, total, history)
        save_session(history, label.split()[0], duration // 60, completed)

        if not completed:
            # Was it a quit (q) or skip (s)?  We can't distinguish easily,
            # but show completion screen briefly regardless.
            completion_screen(label, False)
        else:
            completion_screen(label, True)

    clear()
    show_cursor()
    print()
    print(c("cyan", "  Session complete!"))
    print()
    print(f"  {c('yellow', 'Total Pomodoros:')}  {c('white', str(history['total_pomodoros']))}")
    fm = history['total_focus_minutes']
    print(f"  {c('yellow', 'Total Focus Time:')} {c('white', f'{fm // 60}h {fm % 60}m')}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="ASCII Pomodoro Timer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--work",   type=int, default=25, help="Work duration in minutes (default: 25)")
    parser.add_argument("--short",  type=int, default=5,  help="Short break in minutes (default: 5)")
    parser.add_argument("--long",   type=int, default=15, help="Long break in minutes (default: 15)")
    parser.add_argument("--cycles", type=int, default=4,  help="Pomodoro cycles before long break (default: 4)")
    parser.add_argument("--stats",  action="store_true",  help="Show session history and stats")
    args = parser.parse_args()

    if args.stats:
        show_stats()
        return

    if not sys.stdin.isatty():
        print("Error: must be run in an interactive terminal.", file=sys.stderr)
        sys.exit(1)

    print(c("cyan", "\n  ╔══════════════════════════════╗"))
    print(c("cyan", "  ║") + c("bold", "       ASCII POMODORO ◈        ") + c("cyan", "║"))
    print(c("cyan", "  ╚══════════════════════════════╝"))
    print()
    print(f"  Work:        {c('green',   f'{args.work}m')}")
    print(f"  Short break: {c('cyan',    f'{args.short}m')}")
    print(f"  Long break:  {c('magenta', f'{args.long}m')}")
    print(f"  Cycles:      {c('white',   str(args.cycles))}")
    print()
    print(c("dim", "  Press Enter to start, or Ctrl-C to cancel..."))
    try:
        input()
    except KeyboardInterrupt:
        print("\n  Cancelled.")
        return

    run_pomodoro(args.work, args.short, args.long, args.cycles)


if __name__ == "__main__":
    main()
