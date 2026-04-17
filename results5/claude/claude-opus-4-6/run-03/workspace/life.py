#!/usr/bin/env python3
"""Terminal-based Conway's Game of Life with interactive controls and pattern library."""

import curses
import time
import random
import sys
from collections import defaultdict


# ── Core Engine ──────────────────────────────────────────────────────────────

class Grid:
    """Sparse grid using a set of (row, col) for live cells."""

    def __init__(self):
        self.cells = set()

    def add(self, row, col):
        self.cells.add((row, col))

    def remove(self, row, col):
        self.cells.discard((row, col))

    def toggle(self, row, col):
        if (row, col) in self.cells:
            self.cells.discard((row, col))
        else:
            self.cells.add((row, col))

    def alive(self, row, col):
        return (row, col) in self.cells

    def clear(self):
        self.cells.clear()

    def population(self):
        return len(self.cells)

    def step(self):
        """Advance one generation using standard B3/S23 rules."""
        neighbor_count = defaultdict(int)
        for r, c in self.cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    neighbor_count[(r + dr, c + dc)] += 1

        new_cells = set()
        for pos, count in neighbor_count.items():
            if count == 3 or (count == 2 and pos in self.cells):
                new_cells.add(pos)
        self.cells = new_cells

    def place_pattern(self, pattern, row, col):
        """Place a pattern (list of (dr, dc) offsets) at the given position."""
        for dr, dc in pattern:
            self.cells.add((row + dr, col + dc))

    def randomize(self, rows, cols, density=0.3):
        self.cells.clear()
        for r in range(rows):
            for c in range(cols):
                if random.random() < density:
                    self.cells.add((r, c))


# ── Pattern Library ──────────────────────────────────────────────────────────

PATTERNS = {
    "glider": {
        "desc": "Classic diagonal spaceship",
        "cells": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    },
    "lwss": {
        "desc": "Lightweight spaceship",
        "cells": [
            (0, 1), (0, 4),
            (1, 0),
            (2, 0), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 3),
        ],
    },
    "pulsar": {
        "desc": "Period-3 oscillator",
        "cells": [
            # Top-left quadrant (reflected to all four)
            *[(r, c) for r, c in [
                (-6, -4), (-6, -3), (-6, -2),
                (-6, 2), (-6, 3), (-6, 4),
                (-4, -6), (-3, -6), (-2, -6),
                (-4, -1), (-3, -1), (-2, -1),
                (-4, 1), (-3, 1), (-2, 1),
                (-4, 6), (-3, 6), (-2, 6),
                (-1, -4), (-1, -3), (-1, -2),
                (-1, 2), (-1, 3), (-1, 4),
                (1, -4), (1, -3), (1, -2),
                (1, 2), (1, 3), (1, 4),
                (2, -6), (3, -6), (4, -6),
                (2, -1), (3, -1), (4, -1),
                (2, 1), (3, 1), (4, 1),
                (2, 6), (3, 6), (4, 6),
                (6, -4), (6, -3), (6, -2),
                (6, 2), (6, 3), (6, 4),
            ]],
        ],
    },
    "rpentomino": {
        "desc": "R-pentomino — chaotic methuselah",
        "cells": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    },
    "gosper_gun": {
        "desc": "Gosper glider gun — infinite growth",
        "cells": [
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
    },
    "diehard": {
        "desc": "Diehard — vanishes after 130 generations",
        "cells": [(0, 6), (1, 0), (1, 1), (2, 1), (2, 5), (2, 6), (2, 7)],
    },
    "acorn": {
        "desc": "Acorn — tiny seed, huge expansion",
        "cells": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
    },
    "beacon": {
        "desc": "Period-2 oscillator",
        "cells": [(0, 0), (0, 1), (1, 0), (2, 3), (3, 2), (3, 3)],
    },
    "toad": {
        "desc": "Period-2 oscillator",
        "cells": [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)],
    },
    "block": {
        "desc": "Still life — 2x2 block",
        "cells": [(0, 0), (0, 1), (1, 0), (1, 1)],
    },
}

PATTERN_KEYS = list(PATTERNS.keys())


# ── Terminal UI ──────────────────────────────────────────────────────────────

CELL_CHAR = "\u2588"  # full block
DEAD_CHAR = " "

SPEEDS = [2.0, 1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
SPEED_NAMES = ["0.5x", "1x", "2x", "5x", "10x", "20x", "50x", "100x"]


def run(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(20)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_WHITE, -1)
        curses.init_pair(5, curses.COLOR_RED, -1)

    grid = Grid()
    paused = True
    generation = 0
    speed_idx = 3
    last_step = time.monotonic()

    cursor_r, cursor_c = 0, 0
    view_r, view_c = 0, 0  # viewport offset
    selected_pattern = 0
    show_help = True

    max_h, max_w = stdscr.getmaxyx()
    grid_h = max_h - 3
    grid_w = max_w

    # Start with a glider gun in the center
    center_r = grid_h // 2 - 4
    center_c = grid_w // 2 - 18
    grid.place_pattern(PATTERNS["gosper_gun"]["cells"], center_r, center_c)

    while True:
        max_h, max_w = stdscr.getmaxyx()
        grid_h = max_h - 3
        grid_w = max_w

        # ── Handle input ─────────────────────────────────────────────
        key = stdscr.getch()

        if key == ord("q"):
            break
        elif key == ord(" "):
            paused = not paused
        elif key == ord("s"):
            grid.step()
            generation += 1
        elif key == ord("c"):
            grid.clear()
            generation = 0
        elif key == ord("r"):
            grid.randomize(grid_h, grid_w, 0.25)
            generation = 0
            view_r, view_c = 0, 0
        elif key == ord("\n") or key == ord("\r"):
            pat = PATTERNS[PATTERN_KEYS[selected_pattern]]["cells"]
            grid.place_pattern(pat, cursor_r + view_r, cursor_c + view_c)
        elif key == ord("t"):
            grid.toggle(cursor_r + view_r, cursor_c + view_c)
        elif key == ord("["):
            speed_idx = max(0, speed_idx - 1)
        elif key == ord("]"):
            speed_idx = min(len(SPEEDS) - 1, speed_idx + 1)
        elif key == ord("p"):
            selected_pattern = (selected_pattern + 1) % len(PATTERN_KEYS)
        elif key == ord("P"):
            selected_pattern = (selected_pattern - 1) % len(PATTERN_KEYS)
        elif key == ord("?"):
            show_help = not show_help

        # Arrow keys / vim keys for cursor movement
        elif key == curses.KEY_UP or key == ord("k"):
            cursor_r = max(0, cursor_r - 1)
        elif key == curses.KEY_DOWN or key == ord("j"):
            cursor_r = min(grid_h - 1, cursor_r + 1)
        elif key == curses.KEY_LEFT or key == ord("h"):
            cursor_c = max(0, cursor_c - 1)
        elif key == curses.KEY_RIGHT or key == ord("l"):
            cursor_c = min(grid_w - 1, cursor_c + 1)

        # Shift+WASD for viewport panning
        elif key == ord("W"):
            view_r -= 5
        elif key == ord("A"):
            view_c -= 5
        elif key == ord("D"):
            view_c += 5
        elif key == ord("S"):
            view_r += 5

        # ── Step simulation ──────────────────────────────────────────
        now = time.monotonic()
        if not paused and (now - last_step) >= SPEEDS[speed_idx]:
            grid.step()
            generation += 1
            last_step = now

        # ── Draw ─────────────────────────────────────────────────────
        stdscr.erase()

        cell_color = curses.color_pair(1) if curses.has_colors() else curses.A_NORMAL

        for r in range(min(grid_h, max_h - 3)):
            row_buf = []
            for c in range(min(grid_w, max_w)):
                if grid.alive(r + view_r, c + view_c):
                    row_buf.append(CELL_CHAR)
                else:
                    row_buf.append(DEAD_CHAR)
            line = "".join(row_buf)
            try:
                stdscr.addstr(r, 0, line, cell_color)
            except curses.error:
                pass

        # Draw cursor
        if 0 <= cursor_r < grid_h and 0 <= cursor_c < grid_w:
            cursor_color = curses.color_pair(3) | curses.A_BOLD if curses.has_colors() else curses.A_REVERSE
            ch = CELL_CHAR if grid.alive(cursor_r + view_r, cursor_c + view_c) else "+"
            try:
                stdscr.addstr(cursor_r, cursor_c, ch, cursor_color)
            except curses.error:
                pass

        # Draw pattern preview at cursor
        if paused:
            pat = PATTERNS[PATTERN_KEYS[selected_pattern]]["cells"]
            preview_color = curses.color_pair(2) if curses.has_colors() else curses.A_DIM
            for dr, dc in pat:
                pr, pc = cursor_r + dr, cursor_c + dc
                if 0 <= pr < grid_h and 0 <= pc < grid_w:
                    try:
                        stdscr.addstr(pr, pc, CELL_CHAR, preview_color)
                    except curses.error:
                        pass

        # ── Status bar ───────────────────────────────────────────────
        status_y = max_h - 3
        bar_color = curses.color_pair(4) | curses.A_BOLD if curses.has_colors() else curses.A_REVERSE

        state = "PAUSED" if paused else "RUNNING"
        pat_name = PATTERN_KEYS[selected_pattern]
        pat_desc = PATTERNS[pat_name]["desc"]
        status = (
            f" {state} | Gen: {generation} | Pop: {grid.population()} | "
            f"Speed: {SPEED_NAMES[speed_idx]} | Pattern: {pat_name} ({pat_desc})"
        )
        status = status[:max_w - 1]
        try:
            stdscr.addstr(status_y, 0, status.ljust(max_w - 1), bar_color)
        except curses.error:
            pass

        # ── Help bar ─────────────────────────────────────────────────
        if show_help:
            help_color = curses.color_pair(2) if curses.has_colors() else curses.A_NORMAL
            help1 = " SPC:pause  s:step  r:random  c:clear  t:toggle cell  Enter:place pattern  p/P:cycle pattern  [/]:speed"
            help2 = " hjkl/Arrows:cursor  Shift+WASD:pan  ?:help  q:quit"
            try:
                stdscr.addstr(status_y + 1, 0, help1[:max_w - 1], help_color)
                stdscr.addstr(status_y + 2, 0, help2[:max_w - 1], help_color)
            except curses.error:
                pass

        stdscr.refresh()


def main():
    if "--list-patterns" in sys.argv:
        print("Available patterns:")
        for name, data in PATTERNS.items():
            print(f"  {name:15s} — {data['desc']}")
        return

    curses.wrapper(run)


if __name__ == "__main__":
    main()
