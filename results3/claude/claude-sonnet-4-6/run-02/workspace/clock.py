#!/usr/bin/env python3
"""Live ASCII art clock — displays current time in large block digits.

Modes:
  (default)            Live clock showing current time
  --stopwatch / -s     Stopwatch counting up; Space = pause/resume, r = reset
  --timer HH:MM:SS     Countdown timer; alerts when it reaches zero
"""

import argparse
import os
import select
import signal
import sys
import termios
import time
import tty

DIGITS = {
    "0": [
        " ██████ ",
        "██    ██",
        "██    ██",
        "██    ██",
        " ██████ ",
    ],
    "1": [
        "   ██   ",
        "  ███   ",
        "   ██   ",
        "   ██   ",
        " ██████ ",
    ],
    "2": [
        "███████ ",
        "     ██ ",
        " █████  ",
        "██      ",
        "████████",
    ],
    "3": [
        "███████ ",
        "      ██",
        " ██████ ",
        "      ██",
        "███████ ",
    ],
    "4": [
        "██    ██",
        "██    ██",
        "████████",
        "      ██",
        "      ██",
    ],
    "5": [
        "████████",
        "██      ",
        "███████ ",
        "      ██",
        "███████ ",
    ],
    "6": [
        " ██████ ",
        "██      ",
        "███████ ",
        "██    ██",
        " ██████ ",
    ],
    "7": [
        "████████",
        "     ██ ",
        "    ██  ",
        "   ██   ",
        "   ██   ",
    ],
    "8": [
        " ██████ ",
        "██    ██",
        " ██████ ",
        "██    ██",
        " ██████ ",
    ],
    "9": [
        " ██████ ",
        "██    ██",
        " ███████",
        "      ██",
        " ██████ ",
    ],
    ":": [
        "        ",
        "   ██   ",
        "        ",
        "   ██   ",
        "        ",
    ],
    " ": [
        "        ",
        "        ",
        "        ",
        "        ",
        "        ",
    ],
}

DIGIT_HEIGHT = 5
DIGIT_WIDTH = 8
GAP = " "

# ANSI colors
RESET   = "\033[0m"
BOLD    = "\033[1m"
CYAN    = "\033[96m"
YELLOW  = "\033[93m"
GREEN   = "\033[92m"
MAGENTA = "\033[95m"
RED     = "\033[91m"
DIM     = "\033[2m"

HOUR_COLOR   = CYAN
COLON_COLOR  = YELLOW
MINUTE_COLOR = GREEN
SECOND_COLOR = MAGENTA


def render_time(t: str, color_override: str | None = None) -> list[str]:
    """Convert a time string like '12:34:56' into lines of ASCII art."""
    rows = [""] * DIGIT_HEIGHT
    for i, ch in enumerate(t):
        glyph = DIGITS.get(ch, DIGITS[" "])
        if color_override:
            color = color_override
        elif i < 2:
            color = HOUR_COLOR
        elif i == 2:
            color = COLON_COLOR
        elif i < 5:
            color = MINUTE_COLOR
        elif i == 5:
            color = COLON_COLOR
        else:
            color = SECOND_COLOR
        for row_idx, line in enumerate(glyph):
            rows[row_idx] += BOLD + color + line + RESET + GAP
    return rows


def get_terminal_width() -> int:
    try:
        return os.get_terminal_size().columns
    except OSError:
        return 80


def center_pad(line: str, visible_width: int, terminal_width: int) -> str:
    pad = max(0, (terminal_width - visible_width) // 2)
    return " " * pad + line


def seconds_to_hms(total: int) -> str:
    total = max(0, total)
    h = total // 3600
    m = (total % 3600) // 60
    s = total % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def parse_duration(s: str) -> int:
    """Parse HH:MM:SS or MM:SS into total seconds."""
    parts = s.strip().split(":")
    try:
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return int(parts[0])
    except ValueError:
        raise argparse.ArgumentTypeError(f"Invalid duration '{s}'. Use HH:MM:SS or MM:SS.")


# ── terminal raw-mode helpers ──────────────────────────────────────────────────

class RawTerminal:
    """Context manager: put stdin in raw, non-blocking mode."""

    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.old = termios.tcgetattr(self.fd)
        tty.setraw(self.fd)
        return self

    def __exit__(self, *_):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.old)

    def read_char(self, timeout: float = 0.05) -> str | None:
        """Return a single keypress if available within *timeout* seconds."""
        r, _, _ = select.select([self.fd], [], [], timeout)
        if r:
            return os.read(self.fd, 1).decode("utf-8", errors="ignore")
        return None


# ── shared render loop helpers ─────────────────────────────────────────────────

def setup_exit(restore_fn):
    signal.signal(signal.SIGINT, lambda *_: restore_fn())
    signal.signal(signal.SIGTERM, lambda *_: restore_fn())


def draw_frame(time_str: str, subtitle: str, hint: str,
               color_override: str | None = None, first: bool = False):
    lines = render_time(time_str, color_override)
    term_w = get_terminal_width()
    visible_width = len("HH:MM:SS") * (DIGIT_WIDTH + len(GAP)) - len(GAP)
    total_lines = DIGIT_HEIGHT + 5  # blank + digits + blank + subtitle + hint

    if first:
        sys.stdout.write("\033[2J\033[H")
    else:
        sys.stdout.write(f"\033[{total_lines}A\033[0J")

    output = [""]
    for line in lines:
        output.append(center_pad(line, visible_width, term_w))
    output.append("")
    output.append(center_pad(DIM + subtitle + RESET, len(subtitle), term_w))
    output.append(center_pad(DIM + hint + RESET, len(hint), term_w))
    output.append("")

    sys.stdout.write("\n".join(output) + "\n")
    sys.stdout.flush()


# ── modes ──────────────────────────────────────────────────────────────────────

def run_clock():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    def restore(sig=None, frame=None):
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
        sys.exit(0)

    setup_exit(restore)
    visible_width = len("HH:MM:SS") * (DIGIT_WIDTH + len(GAP)) - len(GAP)
    first = True

    while True:
        now = time.localtime()
        time_str = time.strftime("%H:%M:%S", now)
        date_str = time.strftime("%A, %B %-d %Y", now)
        term_w = get_terminal_width()
        lines = render_time(time_str)
        total_lines = DIGIT_HEIGHT + 4

        if first:
            sys.stdout.write("\033[2J\033[H")
            first = False
        else:
            sys.stdout.write(f"\033[{total_lines}A\033[0J")

        output = [""]
        for line in lines:
            output.append(center_pad(line, visible_width, term_w))
        output.append("")
        date_line = DIM + date_str + RESET
        output.append(center_pad(date_line, len(date_str), term_w))
        output.append("")

        sys.stdout.write("\n".join(output) + "\n")
        sys.stdout.flush()
        time.sleep(1)


def run_stopwatch():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    elapsed = 0.0
    running = True
    start_mono = time.monotonic()
    first = True

    def restore():
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
        sys.exit(0)

    setup_exit(restore)

    with RawTerminal() as term:
        while True:
            key = term.read_char(timeout=0.05)
            if key == "q":
                restore()
            elif key == " ":
                if running:
                    elapsed += time.monotonic() - start_mono
                    running = False
                else:
                    start_mono = time.monotonic()
                    running = True
            elif key in ("r", "R"):
                elapsed = 0.0
                start_mono = time.monotonic()
                running = True

            if running:
                total = elapsed + (time.monotonic() - start_mono)
            else:
                total = elapsed

            display = seconds_to_hms(int(total))
            status = "running" if running else "paused "
            hint = f"[{status}]  Space=pause/resume  r=reset  q=quit"
            color = GREEN if running else YELLOW
            draw_frame(display, "", hint, color_override=color, first=first)
            first = False


def run_timer(total_seconds: int):
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

    remaining = float(total_seconds)
    start_mono = time.monotonic()
    running = True
    done = False
    first = True
    blink_state = True
    blink_tick = 0

    def restore():
        sys.stdout.write("\033[?25h\n")
        sys.stdout.flush()
        sys.exit(0)

    setup_exit(restore)

    with RawTerminal() as term:
        while True:
            key = term.read_char(timeout=0.05)
            if key == "q":
                restore()
            elif key == " " and not done:
                if running:
                    remaining -= time.monotonic() - start_mono
                    running = False
                else:
                    start_mono = time.monotonic()
                    running = True
            elif key in ("r", "R"):
                remaining = float(total_seconds)
                start_mono = time.monotonic()
                running = True
                done = False

            if running and not done:
                secs_left = remaining - (time.monotonic() - start_mono)
                if secs_left <= 0:
                    secs_left = 0
                    done = True
                    running = False
            else:
                secs_left = max(0.0, remaining)

            display = seconds_to_hms(int(secs_left))

            if done:
                blink_tick += 1
                if blink_tick % 12 == 0:
                    blink_state = not blink_state
                color = RED if blink_state else YELLOW
                subtitle = "*** TIME IS UP ***"
                hint = "r=restart  q=quit"
            elif running:
                color = CYAN if secs_left > 10 else YELLOW
                subtitle = "counting down"
                hint = "Space=pause  r=restart  q=quit"
            else:
                color = YELLOW
                subtitle = "paused"
                hint = "Space=resume  r=restart  q=quit"

            draw_frame(display, subtitle, hint, color_override=color, first=first)
            first = False


# ── entry point ────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="ASCII art clock, stopwatch, and countdown timer."
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "-s", "--stopwatch",
        action="store_true",
        help="Run as a stopwatch (counts up).",
    )
    group.add_argument(
        "-t", "--timer",
        metavar="DURATION",
        help="Run as a countdown timer. DURATION format: HH:MM:SS or MM:SS.",
    )
    args = parser.parse_args()

    if args.stopwatch:
        run_stopwatch()
    elif args.timer:
        secs = parse_duration(args.timer)
        if secs <= 0:
            parser.error("Timer duration must be greater than zero.")
        run_timer(secs)
    else:
        run_clock()


if __name__ == "__main__":
    main()
