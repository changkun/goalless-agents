#!/usr/bin/env python3
"""
Conway's Game of Life — interactive terminal simulator.

Controls:
  SPACE  pause / resume       r  randomize grid
  s      single step          c  clear grid
  +/-    speed up / slow down q  quit
  1-7    load preset pattern  w  toggle wrapping

Patterns:
  1 Glider   2 LWSS   3 Pulsar   4 Pentadecathlon
  5 Gosper Glider Gun  6 R-pentomino  7 Acorn
"""

import sys
import os
import time
import random
import select
import termios
import tty
from typing import Set, Tuple

Cell = Tuple[int, int]

# ── Patterns ─────────────────────────────────────────────────────────

PATTERNS: dict[str, list[Cell]] = {
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "LWSS": [
        (0, 1), (0, 4), (1, 0), (2, 0), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "Pulsar": [
        # One quarter, mirrored four ways below
        (1, 2), (1, 3), (1, 4), (1, 8), (1, 9), (1, 10),
        (2, 0), (2, 5), (2, 7), (2, 12),
        (3, 0), (3, 5), (3, 7), (3, 12),
        (4, 0), (4, 5), (4, 7), (4, 12),
        (5, 2), (5, 3), (5, 4), (5, 8), (5, 9), (5, 10),
        (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (7, 10),
        (8, 0), (8, 5), (8, 7), (8, 12),
        (9, 0), (9, 5), (9, 7), (9, 12),
        (10, 0), (10, 5), (10, 7), (10, 12),
        (11, 2), (11, 3), (11, 4), (11, 8), (11, 9), (11, 10),
    ],
    "Pentadecathlon": [
        (0, 1), (1, 1), (2, 0), (2, 2), (3, 1), (4, 1),
        (5, 1), (6, 1), (7, 0), (7, 2), (8, 1), (9, 1),
    ],
    "Gosper Glider Gun": [
        (0, 24),
        (1, 22), (1, 24),
        (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
        (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
        (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
        (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17), (5, 22), (5, 24),
        (6, 10), (6, 16), (6, 24),
        (7, 11), (7, 15),
        (8, 12), (8, 13),
    ],
    "R-pentomino": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    "Acorn": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
}

PATTERN_KEYS = list(PATTERNS.keys())

# ── Grid Engine ──────────────────────────────────────────────────────


class Grid:
    def __init__(self, rows: int, cols: int, wrap: bool = True):
        self.rows = rows
        self.cols = cols
        self.wrap = wrap
        self.alive: Set[Cell] = set()
        self.generation = 0

    def clear(self):
        self.alive.clear()
        self.generation = 0

    def randomize(self, density: float = 0.2):
        self.alive.clear()
        self.generation = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.alive.add((r, c))

    def place_pattern(self, name: str):
        """Place a named pattern centred on the grid."""
        cells = PATTERNS[name]
        max_r = max(r for r, c in cells)
        max_c = max(c for r, c in cells)
        off_r = (self.rows - max_r) // 2
        off_c = (self.cols - max_c) // 2
        for r, c in cells:
            self.alive.add((r + off_r, c + off_c))

    def _neighbours(self, r: int, c: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = r + dr, c + dc
                if self.wrap:
                    nr %= self.rows
                    nc %= self.cols
                elif not (0 <= nr < self.rows and 0 <= nc < self.cols):
                    continue
                if (nr, nc) in self.alive:
                    count += 1
        return count

    def step(self):
        """Advance one generation using standard B3/S23 rules."""
        candidates: dict[Cell, int] = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr, nc = r + dr, c + dc
                    if self.wrap:
                        nr %= self.rows
                        nc %= self.cols
                    elif not (0 <= nr < self.rows and 0 <= nc < self.cols):
                        continue
                    if (nr, nc) not in candidates:
                        candidates[(nr, nc)] = 0
                    # Don't count the cell itself
                    if not (dr == 0 and dc == 0):
                        candidates[(nr, nc)] += 1
        # We need to recount properly — rebuild
        neighbour_count: dict[Cell, int] = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if self.wrap:
                        nr %= self.rows
                        nc %= self.cols
                    elif not (0 <= nr < self.rows and 0 <= nc < self.cols):
                        continue
                    neighbour_count[(nr, nc)] = neighbour_count.get((nr, nc), 0) + 1

        new_alive: Set[Cell] = set()
        # Check all candidates (alive cells + their neighbours)
        all_candidates = self.alive | set(neighbour_count.keys())
        for cell in all_candidates:
            n = neighbour_count.get(cell, 0)
            if cell in self.alive:
                if n in (2, 3):
                    new_alive.add(cell)
            else:
                if n == 3:
                    new_alive.add(cell)
        self.alive = new_alive
        self.generation += 1


# ── Terminal I/O ─────────────────────────────────────────────────────

BLOCK_FULL = "\u2588\u2588"
BLOCK_EMPTY = "  "
# Use half-block characters for denser display (2 rows per line)
UPPER_HALF = "\u2580"
LOWER_HALF = "\u2584"
FULL_BLOCK = "\u2588"
EMPTY = " "

CSI = "\033["


def hide_cursor():
    sys.stdout.write(f"{CSI}?25l")


def show_cursor():
    sys.stdout.write(f"{CSI}?25h")


def move_to(row: int, col: int):
    sys.stdout.write(f"{CSI}{row};{col}H")


def clear_screen():
    sys.stdout.write(f"{CSI}2J")


def set_color(fg: int):
    sys.stdout.write(f"{CSI}38;5;{fg}m")


def reset_color():
    sys.stdout.write(f"{CSI}0m")


def render(grid: Grid, paused: bool, speed: float, wrap: bool):
    """Render the grid using half-block technique: each terminal row = 2 grid rows."""
    buf: list[str] = []
    buf.append(f"{CSI}1;1H")  # move to top-left

    # Header
    status = "PAUSED" if paused else "RUNNING"
    pop = len(grid.alive)
    header = (
        f" Gen {grid.generation:<6}  Pop {pop:<6}  "
        f"Speed {speed:.2f}s  Wrap {'ON' if wrap else 'OFF'}  [{status}]"
    )
    buf.append(f"{CSI}7m{header:<{grid.cols}}{CSI}0m\n")

    # Grid — use half-block rendering for compactness
    for row_pair in range(0, grid.rows, 2):
        line_parts: list[str] = []
        for c in range(grid.cols):
            top = (row_pair, c) in grid.alive
            bot = (row_pair + 1, c) in grid.alive if row_pair + 1 < grid.rows else False
            if top and bot:
                line_parts.append(f"{CSI}38;5;48m{FULL_BLOCK}")
            elif top:
                line_parts.append(f"{CSI}38;5;48m{UPPER_HALF}")
            elif bot:
                line_parts.append(f"{CSI}38;5;48m{LOWER_HALF}")
            else:
                line_parts.append(" ")
        buf.append("".join(line_parts))
        buf.append(f"{CSI}0m\n")

    # Footer with controls
    footer = " SPC:pause  s:step  r:rand  c:clear  +/-:speed  1-7:pattern  w:wrap  q:quit"
    buf.append(f"{CSI}2m{footer}{CSI}0m")

    sys.stdout.write("".join(buf))
    sys.stdout.flush()


def get_key() -> str | None:
    """Non-blocking single character read from stdin."""
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


# ── Main Loop ────────────────────────────────────────────────────────


def main():
    # Determine grid size from terminal
    term_size = os.get_terminal_size()
    cols = term_size.columns
    # Each terminal row shows 2 grid rows (half-block), reserve 2 lines for header+footer
    rows = (term_size.lines - 2) * 2

    grid = Grid(rows, cols, wrap=True)
    grid.randomize(0.15)

    speed = 0.10  # seconds between generations
    paused = False
    wrap = True

    # Save terminal state
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())
        hide_cursor()
        clear_screen()

        last_step = time.monotonic()

        while True:
            # Handle input
            key = get_key()
            if key:
                if key == "q":
                    break
                elif key == " ":
                    paused = not paused
                elif key == "s":
                    grid.step()
                elif key == "r":
                    grid.randomize(0.15)
                elif key == "c":
                    grid.clear()
                elif key == "+":
                    speed = max(0.01, speed - 0.02)
                elif key == "-":
                    speed = min(2.0, speed + 0.02)
                elif key == "w":
                    wrap = not wrap
                    grid.wrap = wrap
                elif key in "1234567":
                    idx = int(key) - 1
                    if idx < len(PATTERN_KEYS):
                        grid.clear()
                        grid.place_pattern(PATTERN_KEYS[idx])

            # Step simulation
            now = time.monotonic()
            if not paused and now - last_step >= speed:
                grid.step()
                last_step = now

            render(grid, paused, speed, wrap)

            # Small sleep to avoid busy-waiting
            time.sleep(0.016)

    except KeyboardInterrupt:
        pass
    finally:
        show_cursor()
        reset_color()
        clear_screen()
        move_to(1, 1)
        sys.stdout.flush()
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print("Thanks for playing Life!")


if __name__ == "__main__":
    main()
