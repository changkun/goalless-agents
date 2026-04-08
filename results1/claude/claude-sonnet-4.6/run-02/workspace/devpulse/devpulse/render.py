"""Terminal rendering utilities — ANSI colors, boxes, bars."""

import os
import shutil
import textwrap

# ── ANSI helpers ────────────────────────────────────────────────────────────

RESET = "\033[0m"
BOLD  = "\033[1m"
DIM   = "\033[2m"

# Foreground colors
BLACK   = "\033[30m"
RED     = "\033[31m"
GREEN   = "\033[32m"
YELLOW  = "\033[33m"
BLUE    = "\033[34m"
MAGENTA = "\033[35m"
CYAN    = "\033[36m"
WHITE   = "\033[37m"

# Bright foreground
BRIGHT_RED     = "\033[91m"
BRIGHT_GREEN   = "\033[92m"
BRIGHT_YELLOW  = "\033[93m"
BRIGHT_BLUE    = "\033[94m"
BRIGHT_MAGENTA = "\033[95m"
BRIGHT_CYAN    = "\033[96m"
BRIGHT_WHITE   = "\033[97m"

# Background (for heatmap cells)
BG_BLACK   = "\033[40m"
BG_GREEN_1 = "\033[48;5;22m"   # very dark green
BG_GREEN_2 = "\033[48;5;28m"   # dark green
BG_GREEN_3 = "\033[48;5;34m"   # medium green
BG_GREEN_4 = "\033[48;5;40m"   # bright green
BG_GREEN_5 = "\033[48;5;46m"   # vivid green

NO_COLOR = not os.isatty(1)


def c(code: str, text: str) -> str:
    """Wrap text in ANSI code if stdout is a tty."""
    if NO_COLOR:
        return text
    return f"{code}{text}{RESET}"


def term_width() -> int:
    return shutil.get_terminal_size((100, 40)).columns


# ── Layout primitives ────────────────────────────────────────────────────────

def section(title: str) -> str:
    width = term_width()
    bar = "─" * (width - len(title) - 4)
    return c(BOLD + BRIGHT_CYAN, f"┌─ {title} {bar}┐")


def section_end() -> str:
    return c(BRIGHT_CYAN, "└" + "─" * (term_width() - 2) + "┘")


def h1(text: str) -> str:
    return c(BOLD + BRIGHT_WHITE, text)


def h2(text: str) -> str:
    return c(BOLD + YELLOW, text)


def muted(text: str) -> str:
    return c(DIM, text)


def bar(value: int, max_val: int, width: int = 30, filled: str = "█", empty: str = "░") -> str:
    if max_val == 0:
        ratio = 0.0
    else:
        ratio = min(value / max_val, 1.0)
    filled_n = round(ratio * width)
    bar_str = filled * filled_n + empty * (width - filled_n)
    pct = ratio * 100
    color = BRIGHT_GREEN if pct >= 66 else (YELLOW if pct >= 33 else RED)
    return c(color, bar_str) + c(DIM, f" {pct:5.1f}%")


def num(n: int, color: str = BRIGHT_WHITE) -> str:
    """Format a number with thousands separator."""
    return c(color, f"{n:,}")


def truncate(s: str, max_len: int) -> str:
    if len(s) <= max_len:
        return s
    return s[: max_len - 1] + "…"
