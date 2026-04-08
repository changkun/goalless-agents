#!/usr/bin/env python3
"""
Conway's Game of Life — Interactive Terminal Edition

Controls:
  Space     Pause / Resume
  S         Single step (while paused)
  R         Randomize grid
  C         Clear grid
  +/-       Speed up / slow down
  Arrow keys / WASD  Pan viewport
  1-9       Load preset pattern at cursor
  Tab       Open pattern browser
  Click     Toggle cell (if terminal supports mouse)
  Q / Esc   Quit
"""

import curses
import random
import time
import sys


# ─── Core Engine ────────────────────────────────────────────────────────────

class Grid:
    """Sparse-set implementation of an infinite Game of Life grid."""

    def __init__(self):
        self.alive: set[tuple[int, int]] = set()

    def clear(self):
        self.alive.clear()

    def toggle(self, r: int, c: int):
        cell = (r, c)
        if cell in self.alive:
            self.alive.discard(cell)
        else:
            self.alive.add(cell)

    def set_alive(self, r: int, c: int):
        self.alive.add((r, c))

    def is_alive(self, r: int, c: int) -> bool:
        return (r, c) in self.alive

    def step(self):
        """Advance one generation using standard B3/S23 rules."""
        neighbor_counts: dict[tuple[int, int], int] = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nb = (r + dr, c + dc)
                    neighbor_counts[nb] = neighbor_counts.get(nb, 0) + 1

        new_alive: set[tuple[int, int]] = set()
        # Cells that survive
        for cell in self.alive:
            cnt = neighbor_counts.get(cell, 0)
            if cnt in (2, 3):
                new_alive.add(cell)
        # Cells that are born
        for cell, cnt in neighbor_counts.items():
            if cnt == 3 and cell not in self.alive:
                new_alive.add(cell)

        self.alive = new_alive

    def population(self) -> int:
        return len(self.alive)

    def bounding_box(self):
        if not self.alive:
            return (0, 0, 0, 0)
        rows = [r for r, _ in self.alive]
        cols = [c for _, c in self.alive]
        return (min(rows), min(cols), max(rows), max(cols))

    def place_pattern(self, pattern: list[tuple[int, int]], origin_r: int, origin_c: int):
        for dr, dc in pattern:
            self.alive.add((origin_r + dr, origin_c + dc))

    def randomize(self, top: int, left: int, height: int, width: int, density: float = 0.3):
        self.alive.clear()
        for r in range(top, top + height):
            for c in range(left, left + width):
                if random.random() < density:
                    self.alive.add((r, c))


# ─── Patterns ───────────────────────────────────────────────────────────────

PATTERNS: dict[str, dict] = {
    "Glider": {
        "cells": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
        "desc": "The classic small spaceship",
    },
    "LWSS": {
        "cells": [(0, 1), (0, 4), (1, 0), (2, 0), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3)],
        "desc": "Lightweight spaceship",
    },
    "Blinker": {
        "cells": [(0, 0), (0, 1), (0, 2)],
        "desc": "Period-2 oscillator",
    },
    "Toad": {
        "cells": [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)],
        "desc": "Period-2 oscillator",
    },
    "Beacon": {
        "cells": [(0, 0), (0, 1), (1, 0), (2, 3), (3, 2), (3, 3)],
        "desc": "Period-2 oscillator",
    },
    "Pulsar": {
        "cells": [
            (0, 2), (0, 3), (0, 4), (0, 8), (0, 9), (0, 10),
            (2, 0), (2, 5), (2, 7), (2, 12),
            (3, 0), (3, 5), (3, 7), (3, 12),
            (4, 0), (4, 5), (4, 7), (4, 12),
            (5, 2), (5, 3), (5, 4), (5, 8), (5, 9), (5, 10),
            (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (7, 10),
            (8, 0), (8, 5), (8, 7), (8, 12),
            (9, 0), (9, 5), (9, 7), (9, 12),
            (10, 0), (10, 5), (10, 7), (10, 12),
            (12, 2), (12, 3), (12, 4), (12, 8), (12, 9), (12, 10),
        ],
        "desc": "Period-3 oscillator",
    },
    "Pentadecathlon": {
        "cells": [
            (0, 1), (1, 1), (2, 0), (2, 2), (3, 1), (4, 1),
            (5, 1), (6, 1), (7, 0), (7, 2), (8, 1), (9, 1),
        ],
        "desc": "Period-15 oscillator",
    },
    "Gosper Gun": {
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
        "desc": "Infinite glider generator",
    },
    "R-pentomino": {
        "cells": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
        "desc": "Long-lived methuselah (1103 gens)",
    },
    "Diehard": {
        "cells": [(0, 6), (1, 0), (1, 1), (2, 1), (2, 5), (2, 6), (2, 7)],
        "desc": "Vanishes after 130 generations",
    },
    "Acorn": {
        "cells": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
        "desc": "Methuselah — 5206 gens to stabilize",
    },
    "Block": {
        "cells": [(0, 0), (0, 1), (1, 0), (1, 1)],
        "desc": "Simplest still life",
    },
    "Beehive": {
        "cells": [(0, 1), (0, 2), (1, 0), (1, 3), (2, 1), (2, 2)],
        "desc": "Common still life",
    },
}

PATTERN_NAMES = list(PATTERNS.keys())


# ─── TUI ────────────────────────────────────────────────────────────────────

CELL_ALIVE = "\u2588\u2588"  # two full-block chars per cell for squarish look
CELL_DEAD = "  "

SPEED_LEVELS = [1.0, 0.5, 0.25, 0.12, 0.06, 0.03, 0.015, 0.007]
SPEED_NAMES = ["1 gen/s", "2 gen/s", "4 gen/s", "~8 gen/s", "~16 gen/s", "~33 gen/s", "~66 gen/s", "~140 gen/s"]


class App:
    def __init__(self, stdscr):
        self.scr = stdscr
        self.grid = Grid()
        self.generation = 0
        self.running = False
        self.speed_idx = 3
        self.cam_r = 0  # top-left of viewport in grid coords
        self.cam_c = 0
        self.cursor_r = 0  # cursor in grid coords
        self.cursor_c = 0
        self.show_help = False
        self.show_browser = False
        self.browser_sel = 0
        self.message = ""
        self.message_time = 0.0

    def flash(self, msg: str):
        self.message = msg
        self.message_time = time.monotonic()

    def grid_rows(self) -> int:
        return max(1, curses.LINES - 2)  # reserve 2 lines for status

    def grid_cols(self) -> int:
        return max(1, (curses.COLS) // 2)  # each cell is 2 chars wide

    def center_camera(self):
        self.cam_r = self.cursor_r - self.grid_rows() // 2
        self.cam_c = self.cursor_c - self.grid_cols() // 2

    def run(self):
        self._setup()
        self._place_initial()
        self._loop()

    def _setup(self):
        curses.curs_set(0)
        self.scr.nodelay(True)
        self.scr.keypad(True)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # alive cells
        curses.init_pair(2, curses.COLOR_CYAN, -1)     # cursor
        curses.init_pair(3, curses.COLOR_YELLOW, -1)   # status bar
        curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)  # browser
        curses.init_pair(5, curses.COLOR_BLACK, curses.COLOR_CYAN)  # browser selected
        curses.init_pair(6, curses.COLOR_RED, -1)      # paused indicator
        try:
            curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
        except Exception:
            pass

    def _place_initial(self):
        # Start with an R-pentomino near center
        self.grid.place_pattern(PATTERNS["R-pentomino"]["cells"], 0, 0)
        self.cursor_r, self.cursor_c = 1, 1
        self.center_camera()
        self.running = True
        self.flash("R-pentomino loaded — Space to pause, Tab for patterns, Q to quit")

    def _loop(self):
        last_step = time.monotonic()
        while True:
            now = time.monotonic()
            # Process input
            if self._handle_input():
                return

            # Step simulation
            if self.running:
                interval = SPEED_LEVELS[self.speed_idx]
                if now - last_step >= interval:
                    self.grid.step()
                    self.generation += 1
                    last_step = now

            # Render
            self._draw()

            # Don't burn CPU
            curses.napms(8)

    def _handle_input(self) -> bool:
        """Returns True to quit."""
        try:
            key = self.scr.getch()
        except Exception:
            return False

        if key == -1:
            return False

        # Quit
        if key in (ord('q'), ord('Q'), 27):  # 27 = Esc
            if self.show_browser:
                self.show_browser = False
                return False
            if self.show_help:
                self.show_help = False
                return False
            return True

        # Help toggle
        if key in (ord('?'), ord('h'), ord('H')):
            if not self.show_browser:
                self.show_help = not self.show_help
            return False

        # Pattern browser
        if key == ord('\t'):
            self.show_browser = not self.show_browser
            self.show_help = False
            return False

        if self.show_browser:
            return self._handle_browser_input(key)

        if self.show_help:
            return False  # any key closes help — handled above

        # Pause / Resume
        if key == ord(' '):
            self.running = not self.running
            self.flash("Running" if self.running else "Paused")

        # Single step
        elif key in (ord('s'), ord('S')):
            if not self.running:
                self.grid.step()
                self.generation += 1
                self.flash("Step")

        # Clear
        elif key in (ord('c'), ord('C')):
            self.grid.clear()
            self.generation = 0
            self.running = False
            self.flash("Cleared")

        # Randomize
        elif key in (ord('r'), ord('R')):
            h, w = self.grid_rows(), self.grid_cols()
            self.grid.randomize(self.cam_r, self.cam_c, h, w, density=0.3)
            self.generation = 0
            self.flash("Randomized")

        # Speed
        elif key in (ord('+'), ord('='), ord(']')):
            self.speed_idx = min(self.speed_idx + 1, len(SPEED_LEVELS) - 1)
            self.flash(f"Speed: {SPEED_NAMES[self.speed_idx]}")
        elif key in (ord('-'), ord('_'), ord('[')):
            self.speed_idx = max(self.speed_idx - 1, 0)
            self.flash(f"Speed: {SPEED_NAMES[self.speed_idx]}")

        # Movement (pan camera & cursor)
        elif key in (curses.KEY_UP, ord('w'), ord('W')):
            self.cursor_r -= 1
            self._clamp_camera()
        elif key in (curses.KEY_DOWN, ord('j'), ord('J')):
            self.cursor_r += 1
            self._clamp_camera()
        elif key in (curses.KEY_LEFT, ord('a'), ord('A')):
            self.cursor_c -= 1
            self._clamp_camera()
        elif key in (curses.KEY_RIGHT, ord('d'), ord('D')):
            self.cursor_c += 1
            self._clamp_camera()

        # Toggle cell at cursor
        elif key in (ord('\n'), ord('e'), ord('E'), ord('x'), ord('X')):
            self.grid.toggle(self.cursor_r, self.cursor_c)

        # Number keys: quick-load pattern 1-9
        elif ord('1') <= key <= ord('9'):
            idx = key - ord('1')
            if idx < len(PATTERN_NAMES):
                name = PATTERN_NAMES[idx]
                self.grid.place_pattern(PATTERNS[name]["cells"], self.cursor_r, self.cursor_c)
                self.flash(f"Placed {name}")

        # Fit camera to population
        elif key in (ord('f'), ord('F')):
            if self.grid.population() > 0:
                r1, c1, r2, c2 = self.grid.bounding_box()
                self.cursor_r = (r1 + r2) // 2
                self.cursor_c = (c1 + c2) // 2
                self.center_camera()
                self.flash("Centered on population")

        # Mouse click
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if bstate & curses.BUTTON1_CLICKED or bstate & curses.BUTTON1_PRESSED:
                    gr = self.cam_r + my
                    gc = self.cam_c + mx // 2
                    self.grid.toggle(gr, gc)
                    self.cursor_r, self.cursor_c = gr, gc
            except Exception:
                pass

        return False

    def _handle_browser_input(self, key) -> bool:
        if key == curses.KEY_UP or key in (ord('w'), ord('W'), ord('k'), ord('K')):
            self.browser_sel = (self.browser_sel - 1) % len(PATTERN_NAMES)
        elif key == curses.KEY_DOWN or key in (ord('s'), ord('S'), ord('j'), ord('J')):
            self.browser_sel = (self.browser_sel + 1) % len(PATTERN_NAMES)
        elif key in (ord('\n'), ord(' ')):
            name = PATTERN_NAMES[self.browser_sel]
            self.grid.place_pattern(PATTERNS[name]["cells"], self.cursor_r, self.cursor_c)
            self.show_browser = False
            self.flash(f"Placed {name} at cursor")
        return False

    def _clamp_camera(self):
        """Scroll camera so cursor stays in view."""
        margin = 3
        gr = self.grid_rows()
        gc = self.grid_cols()
        if self.cursor_r < self.cam_r + margin:
            self.cam_r = self.cursor_r - margin
        if self.cursor_r > self.cam_r + gr - margin - 1:
            self.cam_r = self.cursor_r - gr + margin + 1
        if self.cursor_c < self.cam_c + margin:
            self.cam_c = self.cursor_c - margin
        if self.cursor_c > self.cam_c + gc - margin - 1:
            self.cam_c = self.cursor_c - gc + margin + 1

    def _draw(self):
        self.scr.erase()
        rows = self.grid_rows()
        cols = self.grid_cols()

        # Draw grid
        for y in range(rows):
            line_parts = []
            for x in range(cols):
                gr = self.cam_r + y
                gc = self.cam_c + x
                is_cursor = (gr == self.cursor_r and gc == self.cursor_c)
                alive = self.grid.is_alive(gr, gc)

                if is_cursor:
                    ch = CELL_ALIVE if alive else "\u2591\u2591"
                    try:
                        self.scr.addstr(y, x * 2, ch, curses.color_pair(2) | curses.A_BOLD)
                    except curses.error:
                        pass
                elif alive:
                    try:
                        self.scr.addstr(y, x * 2, CELL_ALIVE, curses.color_pair(1))
                    except curses.error:
                        pass

        # Status bar
        status_y = curses.LINES - 2
        state = "RUNNING" if self.running else "PAUSED"
        state_color = curses.color_pair(3) if self.running else curses.color_pair(6) | curses.A_BOLD
        status = f" {state}  Gen: {self.generation}  Pop: {self.grid.population()}  Speed: {SPEED_NAMES[self.speed_idx]}  Pos: ({self.cursor_r},{self.cursor_c}) "
        try:
            self.scr.addstr(status_y, 0, status.ljust(curses.COLS), state_color | curses.A_REVERSE)
        except curses.error:
            pass

        # Message / help hint
        help_y = curses.LINES - 1
        now = time.monotonic()
        if self.message and now - self.message_time < 3.0:
            hint = f" {self.message}"
        else:
            hint = " Space:pause  Tab:patterns  +-:speed  Arrows:move  Enter:toggle  F:fit  ?:help  Q:quit"
        try:
            self.scr.addstr(help_y, 0, hint[:curses.COLS - 1], curses.color_pair(3))
        except curses.error:
            pass

        # Pattern browser overlay
        if self.show_browser:
            self._draw_browser()

        # Help overlay
        if self.show_help:
            self._draw_help()

        self.scr.refresh()

    def _draw_browser(self):
        bw = 42
        bh = min(len(PATTERN_NAMES) + 4, curses.LINES - 4)
        bx = max(0, (curses.COLS - bw) // 2)
        by = max(0, (curses.LINES - bh) // 2)

        # Border / background
        for y in range(bh):
            try:
                self.scr.addstr(by + y, bx, " " * bw, curses.color_pair(4))
            except curses.error:
                pass

        try:
            self.scr.addstr(by, bx + 2, " Pattern Browser ", curses.color_pair(4) | curses.A_BOLD)
            self.scr.addstr(by + 1, bx + 2, "\u2500" * (bw - 4), curses.color_pair(4))
        except curses.error:
            pass

        visible = bh - 4
        scroll = max(0, self.browser_sel - visible + 1)
        for i in range(min(visible, len(PATTERN_NAMES))):
            idx = scroll + i
            if idx >= len(PATTERN_NAMES):
                break
            name = PATTERN_NAMES[idx]
            desc = PATTERNS[name]["desc"]
            line = f" {idx+1}. {name:<16s} {desc}"
            if len(line) > bw - 2:
                line = line[:bw - 3] + "\u2026"
            attr = curses.color_pair(5) if idx == self.browser_sel else curses.color_pair(4)
            try:
                self.scr.addstr(by + 2 + i, bx + 1, line.ljust(bw - 2), attr)
            except curses.error:
                pass

        try:
            self.scr.addstr(by + bh - 1, bx + 2, "Enter:place  Esc:close", curses.color_pair(4))
        except curses.error:
            pass

    def _draw_help(self):
        lines = [
            "  Conway's Game of Life  ",
            "",
            "  Space       Pause / Resume",
            "  S           Single step (paused)",
            "  R           Randomize grid",
            "  C           Clear grid",
            "  + / -       Speed up / slow down",
            "  Arrows      Move cursor & pan",
            "  Enter / E   Toggle cell at cursor",
            "  1-9         Quick-place pattern",
            "  Tab         Pattern browser",
            "  F           Fit camera to population",
            "  Click       Toggle cell (mouse)",
            "  Q / Esc     Quit",
            "",
            "  Press any key to close",
        ]
        hw = max(len(l) for l in lines) + 4
        hh = len(lines) + 2
        hx = max(0, (curses.COLS - hw) // 2)
        hy = max(0, (curses.LINES - hh) // 2)

        for y in range(hh):
            try:
                self.scr.addstr(hy + y, hx, " " * hw, curses.color_pair(4))
            except curses.error:
                pass
        for i, line in enumerate(lines):
            try:
                self.scr.addstr(hy + 1 + i, hx + 2, line, curses.color_pair(4) | (curses.A_BOLD if i == 0 else 0))
            except curses.error:
                pass


def main(stdscr):
    app = App(stdscr)
    app.run()


if __name__ == "__main__":
    curses.wrapper(main)
