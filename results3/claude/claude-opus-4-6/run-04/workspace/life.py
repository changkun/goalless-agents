#!/usr/bin/env python3
"""
Conway's Game of Life — Interactive Terminal Edition
====================================================
Controls:
  SPACE      Pause / Resume
  S          Step one generation (while paused)
  C          Clear the grid
  R          Randomize the grid
  +/-        Speed up / slow down
  Arrow keys Move cursor
  ENTER      Toggle cell at cursor
  1-5        Load preset pattern at cursor
               1=Glider  2=Blinker  3=Pulsar  4=LWSS  5=Gosper Glider Gun
  A          Toggle age heatmap (green→yellow→red→magenta→white)
  H          Toggle help overlay
  Q          Quit
"""

import curses
import random
import time
import sys

# ── Preset Patterns (relative coords) ────────────────────────────────────────

PATTERNS = {
    "1": (
        "Glider",
        [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    ),
    "2": (
        "Blinker",
        [(0, 0), (0, 1), (0, 2)],
    ),
    "3": (
        "Pulsar",
        [
            # Pulsar is symmetric — list one quadrant's arms, mirror the rest.
            (r, c)
            for r, c in (
                (-6, -4), (-6, -3), (-6, -2), (-6, 2), (-6, 3), (-6, 4),
                (-4, -6), (-3, -6), (-2, -6), (-4, -1), (-3, -1), (-2, -1),
                (-4, 1), (-3, 1), (-2, 1), (-4, 6), (-3, 6), (-2, 6),
                (-1, -4), (-1, -3), (-1, -2), (-1, 2), (-1, 3), (-1, 4),
                (1, -4), (1, -3), (1, -2), (1, 2), (1, 3), (1, 4),
                (2, -6), (3, -6), (4, -6), (2, -1), (3, -1), (4, -1),
                (2, 1), (3, 1), (4, 1), (2, 6), (3, 6), (4, 6),
                (6, -4), (6, -3), (6, -2), (6, 2), (6, 3), (6, 4),
            )
        ],
    ),
    "4": (
        "LWSS",
        [(0, 1), (0, 4), (1, 0), (2, 0), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3)],
    ),
    "5": (
        "Gosper Glider Gun",
        [
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
    ),
}

# ── Simulation ────────────────────────────────────────────────────────────────

class Grid:
    """Toroidal grid for the Game of Life."""

    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.cells: set[tuple[int, int]] = set()
        self.age: dict[tuple[int, int], int] = {}  # how many gens each cell has been alive
        self.generation = 0

    def clear(self):
        self.cells.clear()
        self.age.clear()
        self.generation = 0

    def randomize(self, density: float = 0.2):
        self.cells.clear()
        self.age.clear()
        self.generation = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.cells.add((r, c))
                    self.age[(r, c)] = 0

    def toggle(self, r: int, c: int):
        coord = (r % self.rows, c % self.cols)
        if coord in self.cells:
            self.cells.discard(coord)
            self.age.pop(coord, None)
        else:
            self.cells.add(coord)
            self.age[coord] = 0

    def place_pattern(self, pattern_cells: list[tuple[int, int]], origin_r: int, origin_c: int):
        for dr, dc in pattern_cells:
            r = (origin_r + dr) % self.rows
            c = (origin_c + dc) % self.cols
            self.cells.add((r, c))
            self.age[(r, c)] = 0

    def step(self):
        """Advance one generation using classic B3/S23 rules."""
        neighbour_count: dict[tuple[int, int], int] = {}
        for r, c in self.cells:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr = (r + dr) % self.rows
                    nc = (c + dc) % self.cols
                    neighbour_count[(nr, nc)] = neighbour_count.get((nr, nc), 0) + 1

        new_cells: set[tuple[int, int]] = set()
        new_age: dict[tuple[int, int], int] = {}
        for coord, count in neighbour_count.items():
            if count == 3 or (count == 2 and coord in self.cells):
                new_cells.add(coord)
                new_age[coord] = self.age.get(coord, -1) + 1

        self.cells = new_cells
        self.age = new_age
        self.generation += 1

# ── TUI ───────────────────────────────────────────────────────────────────────

HELP_TEXT = __doc__.strip().split("\n")[3:]  # skip the title lines

SPEEDS = [1.0, 0.5, 0.25, 0.12, 0.06, 0.03, 0.015]
SPEED_LABELS = ["1x", "2x", "4x", "8x", "16x", "32x", "64x"]

CELL_CHAR = "\u2588\u2588"   # "██" — two chars wide so cells look square
EMPTY_CHAR = "  "

def main(stdscr: "curses.window"):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(30)

    # Colours
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)    # age 0 — newborn
    curses.init_pair(2, curses.COLOR_CYAN, -1)     # cursor
    curses.init_pair(3, curses.COLOR_YELLOW, -1)   # status bar
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLUE)  # help overlay
    curses.init_pair(5, curses.COLOR_YELLOW, -1)   # age 1-3
    curses.init_pair(6, curses.COLOR_RED, -1)      # age 4-9
    curses.init_pair(7, curses.COLOR_MAGENTA, -1)  # age 10-24
    curses.init_pair(8, curses.COLOR_WHITE, -1)    # age 25+ — ancient

    max_y, max_x = stdscr.getmaxyx()
    grid_rows = max_y - 2          # leave 2 rows for status
    grid_cols = (max_x - 1) // 2   # each cell is 2 chars wide

    grid = Grid(grid_rows, grid_cols)
    grid.randomize(0.15)

    cursor_r, cursor_c = grid_rows // 2, grid_cols // 2
    paused = False
    show_help = False
    age_colors = True
    speed_idx = 2  # start at 4x
    last_step = 0.0

    while True:
        now = time.monotonic()

        # ── Input ─────────────────────────────────────────────────────────
        try:
            key = stdscr.getch()
        except curses.error:
            key = -1

        if key == ord("q") or key == ord("Q"):
            break
        elif key == ord(" "):
            paused = not paused
        elif key == ord("s") or key == ord("S"):
            if paused:
                grid.step()
        elif key == ord("c") or key == ord("C"):
            grid.clear()
            paused = True
        elif key == ord("r") or key == ord("R"):
            grid.randomize(0.15)
            grid.generation = 0
        elif key == ord("a") or key == ord("A"):
            age_colors = not age_colors
        elif key == ord("h") or key == ord("H"):
            show_help = not show_help
        elif key == ord("+") or key == ord("="):
            speed_idx = min(speed_idx + 1, len(SPEEDS) - 1)
        elif key == ord("-") or key == ord("_"):
            speed_idx = max(speed_idx - 1, 0)
        elif key == curses.KEY_UP:
            cursor_r = (cursor_r - 1) % grid_rows
        elif key == curses.KEY_DOWN:
            cursor_r = (cursor_r + 1) % grid_rows
        elif key == curses.KEY_LEFT:
            cursor_c = (cursor_c - 1) % grid_cols
        elif key == curses.KEY_RIGHT:
            cursor_c = (cursor_c + 1) % grid_cols
        elif key in (curses.KEY_ENTER, 10, 13):
            grid.toggle(cursor_r, cursor_c)
        elif 0 <= key < 256 and chr(key) in PATTERNS:
            _, pat = PATTERNS[chr(key)]
            grid.place_pattern(pat, cursor_r, cursor_c)

        # ── Simulation step ───────────────────────────────────────────────
        interval = SPEEDS[speed_idx]
        if not paused and (now - last_step) >= interval:
            grid.step()
            last_step = now

        # ── Draw ──────────────────────────────────────────────────────────
        stdscr.erase()

        for r in range(grid_rows):
            for c in range(grid_cols):
                sx = c * 2
                sy = r
                if sy >= max_y - 2 or sx + 1 >= max_x:
                    continue
                is_cursor = (r == cursor_r and c == cursor_c)
                alive = (r, c) in grid.cells
                if is_cursor:
                    attr = curses.color_pair(2) | curses.A_BOLD
                    ch = CELL_CHAR if alive else "\u2591\u2591"
                elif alive:
                    if age_colors:
                        age = grid.age.get((r, c), 0)
                        if age < 1:
                            attr = curses.color_pair(1)            # green — newborn
                        elif age < 4:
                            attr = curses.color_pair(5)            # yellow — young
                        elif age < 10:
                            attr = curses.color_pair(6)            # red — mature
                        elif age < 25:
                            attr = curses.color_pair(7)            # magenta — old
                        else:
                            attr = curses.color_pair(8) | curses.A_BOLD  # white — ancient
                    else:
                        attr = curses.color_pair(1)
                    ch = CELL_CHAR
                else:
                    continue  # skip drawing empty cells for speed
                try:
                    stdscr.addstr(sy, sx, ch, attr)
                except curses.error:
                    pass

        # ── Status bar ────────────────────────────────────────────────────
        status_y = max_y - 2
        state = "PAUSED" if paused else "RUNNING"
        pop = len(grid.cells)
        heat = "ON" if age_colors else "OFF"
        status = (
            f" {state}  |  Gen {grid.generation}  |  Pop {pop}  "
            f"|  Speed {SPEED_LABELS[speed_idx]}  |  Heat {heat}  "
            f"|  Cursor ({cursor_r},{cursor_c})  "
            f"|  H=Help  Q=Quit "
        )
        status = status[:max_x - 1]
        try:
            stdscr.addstr(status_y, 0, status, curses.color_pair(3) | curses.A_BOLD)
        except curses.error:
            pass

        # ── Help overlay ──────────────────────────────────────────────────
        if show_help:
            box_w = 58
            box_h = len(HELP_TEXT) + 4
            start_y = max(0, (max_y - box_h) // 2)
            start_x = max(0, (max_x - box_w) // 2)
            for i in range(box_h):
                line_y = start_y + i
                if line_y >= max_y:
                    break
                if i == 0 or i == box_h - 1:
                    txt = "+" + "-" * (box_w - 2) + "+"
                elif i == 1:
                    title = " Conway's Game of Life — Help "
                    pad = box_w - 2 - len(title)
                    txt = "|" + " " * (pad // 2) + title + " " * (pad - pad // 2) + "|"
                elif i == 2:
                    txt = "|" + " " * (box_w - 2) + "|"
                else:
                    idx = i - 3
                    if idx < len(HELP_TEXT):
                        line = HELP_TEXT[idx]
                    else:
                        line = ""
                    line = line[:box_w - 4]
                    txt = "| " + line + " " * (box_w - 3 - len(line)) + "|"
                try:
                    stdscr.addstr(line_y, start_x, txt[:max_x - start_x], curses.color_pair(4))
                except curses.error:
                    pass

        stdscr.refresh()

    curses.curs_set(1)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
