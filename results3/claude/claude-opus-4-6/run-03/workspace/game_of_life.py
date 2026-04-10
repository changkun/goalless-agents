#!/usr/bin/env python3
"""
Conway's Game of Life — Interactive Terminal Simulator

Controls:
  SPACE     Pause / Resume
  N         Step one generation (while paused)
  C         Clear the grid
  R         Randomize the grid
  E         Toggle edit mode (click cells to toggle)
  Arrow keys / WASD  Move cursor (in edit mode)
  ENTER     Toggle cell under cursor (in edit mode)
  +/-       Speed up / slow down
  1-7       Load preset pattern at cursor
  H         Toggle help overlay
  Q         Quit

Presets (placed at cursor position):
  1  Glider            2  Lightweight Spaceship (LWSS)
  3  Pulsar            4  Gosper Glider Gun
  5  R-pentomino       6  Diehard
  7  Acorn
"""

import curses
import random
import time
from typing import Set, Tuple, List

Cell = Tuple[int, int]

# ── Patterns ──────────────────────────────────────────────────────────────────

PATTERNS: dict[str, List[Cell]] = {
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "LWSS": [(0, 1), (0, 4), (1, 0), (2, 0), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3)],
    "Pulsar": [
        # Top-left quadrant (mirrored to all four)
        (r, c)
        for dr, dc in [
            (1, 2), (1, 3), (1, 4),
            (2, 1), (3, 1), (4, 1),
            (2, 6), (3, 6), (4, 6),
            (6, 2), (6, 3), (6, 4),
        ]
        for r, c in [
            (dr, dc), (dr, -dc + 12), (-dr + 12, dc), (-dr + 12, -dc + 12)
        ]
    ],
    "Gosper Glider Gun": [
        (4, 0), (4, 1), (5, 0), (5, 1),
        (4, 10), (5, 10), (6, 10), (3, 11), (7, 11), (2, 12), (8, 12),
        (2, 13), (8, 13), (5, 14), (3, 15), (7, 15), (4, 16), (5, 16),
        (6, 16), (5, 17),
        (2, 20), (3, 20), (4, 20), (2, 21), (3, 21), (4, 21),
        (1, 22), (5, 22), (0, 24), (1, 24), (5, 24), (6, 24),
        (2, 34), (3, 34), (2, 35), (3, 35),
    ],
    "R-pentomino": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    "Diehard": [(0, 6), (1, 0), (1, 1), (2, 1), (2, 5), (2, 6), (2, 7)],
    "Acorn": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
}

PATTERN_KEYS = list(PATTERNS.keys())

# ── Colors for cell age ──────────────────────────────────────────────────────

AGE_COLORS = [
    curses.COLOR_WHITE,
    curses.COLOR_CYAN,
    curses.COLOR_GREEN,
    curses.COLOR_YELLOW,
    curses.COLOR_RED,
    curses.COLOR_MAGENTA,
]


# ── Game Logic ────────────────────────────────────────────────────────────────

class GameOfLife:
    def __init__(self, rows: int, cols: int):
        self.rows = rows
        self.cols = cols
        self.alive: Set[Cell] = set()
        self.age: dict[Cell, int] = {}
        self.generation = 0

    def clear(self):
        self.alive.clear()
        self.age.clear()
        self.generation = 0

    def randomize(self, density: float = 0.2):
        self.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.alive.add((r, c))
                    self.age[(r, c)] = 0

    def toggle(self, r: int, c: int):
        cell = (r, c)
        if cell in self.alive:
            self.alive.discard(cell)
            self.age.pop(cell, None)
        else:
            self.alive.add(cell)
            self.age[cell] = 0

    def place_pattern(self, name: str, origin_r: int, origin_c: int):
        if name not in PATTERNS:
            return
        for dr, dc in PATTERNS[name]:
            r = (origin_r + dr) % self.rows
            c = (origin_c + dc) % self.cols
            self.alive.add((r, c))
            self.age[(r, c)] = 0

    def _neighbor_count(self, r: int, c: int) -> int:
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                if (nr, nc) in self.alive:
                    count += 1
        return count

    def step(self):
        candidates: dict[Cell, int] = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    nr = (r + dr) % self.rows
                    nc = (c + dc) % self.cols
                    if (nr, nc) not in candidates:
                        candidates[(nr, nc)] = 0

        for cell in candidates:
            candidates[cell] = self._neighbor_count(*cell)

        new_alive: Set[Cell] = set()
        new_age: dict[Cell, int] = {}

        for cell, count in candidates.items():
            if cell in self.alive:
                if count in (2, 3):
                    new_alive.add(cell)
                    new_age[cell] = self.age.get(cell, 0) + 1
            else:
                if count == 3:
                    new_alive.add(cell)
                    new_age[cell] = 0

        self.alive = new_alive
        self.age = new_age
        self.generation += 1


# ── Terminal UI ───────────────────────────────────────────────────────────────

def main(stdscr: curses.window):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    # Init colors
    curses.start_color()
    curses.use_default_colors()
    for i, color in enumerate(AGE_COLORS):
        curses.init_pair(i + 1, color, -1)
    curses.init_pair(len(AGE_COLORS) + 1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # cursor
    curses.init_pair(len(AGE_COLORS) + 2, curses.COLOR_BLACK, curses.COLOR_CYAN)   # status bar
    curses.init_pair(len(AGE_COLORS) + 3, curses.COLOR_YELLOW, -1)                 # help text

    STATUS_PAIR = len(AGE_COLORS) + 2
    HELP_PAIR = len(AGE_COLORS) + 3
    CURSOR_PAIR = len(AGE_COLORS) + 1

    max_rows, max_cols = stdscr.getmaxyx()
    grid_rows = max_rows - 2  # reserve 2 lines for status
    grid_cols = max_cols // 2  # each cell takes 2 chars wide

    game = GameOfLife(grid_rows, grid_cols)

    # Seed with a glider gun in the center-ish area
    game.place_pattern("Gosper Glider Gun", grid_rows // 4, grid_cols // 4)

    paused = False
    edit_mode = False
    show_help = False
    cursor_r, cursor_c = grid_rows // 2, grid_cols // 2
    speed = 5  # 1-10, controls delay
    last_step = time.monotonic()

    def speed_delay() -> float:
        return 0.5 / speed

    while True:
        # ── Input ─────────────────────────────────────────────────────────
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('n') or key == ord('N'):
            if paused:
                game.step()
        elif key == ord('c') or key == ord('C'):
            game.clear()
        elif key == ord('r') or key == ord('R'):
            game.randomize()
        elif key == ord('e') or key == ord('E'):
            edit_mode = not edit_mode
            if edit_mode:
                paused = True
        elif key == ord('h') or key == ord('H'):
            show_help = not show_help
        elif key == ord('+') or key == ord('='):
            speed = min(10, speed + 1)
        elif key == ord('-') or key == ord('_'):
            speed = max(1, speed - 1)
        elif ord('1') <= key <= ord('7'):
            idx = key - ord('1')
            if idx < len(PATTERN_KEYS):
                game.place_pattern(PATTERN_KEYS[idx], cursor_r, cursor_c)
        elif key == 10 or key == 13:  # ENTER
            if edit_mode:
                game.toggle(cursor_r, cursor_c)
        # Cursor movement (arrow keys and WASD)
        elif key == curses.KEY_UP or key == ord('w') or key == ord('W'):
            cursor_r = (cursor_r - 1) % grid_rows
        elif key == curses.KEY_DOWN or key == ord('s') or key == ord('S'):
            if not (key == ord('s') or key == ord('S')):  # S is also speed-related? No, using +/-
                cursor_r = (cursor_r + 1) % grid_rows
            else:
                cursor_r = (cursor_r + 1) % grid_rows
        elif key == curses.KEY_LEFT or key == ord('a') or key == ord('A'):
            cursor_c = (cursor_c - 1) % grid_cols
        elif key == curses.KEY_RIGHT or key == ord('d') or key == ord('D'):
            cursor_c = (cursor_c + 1) % grid_cols

        # ── Simulation ────────────────────────────────────────────────────
        now = time.monotonic()
        if not paused and now - last_step >= speed_delay():
            game.step()
            last_step = now

        # ── Render ────────────────────────────────────────────────────────
        stdscr.erase()

        for r in range(grid_rows):
            for c in range(grid_cols):
                cell = (r, c)
                screen_c = c * 2
                is_cursor = edit_mode and r == cursor_r and c == cursor_c

                if cell in game.alive:
                    age = game.age.get(cell, 0)
                    color_idx = min(age, len(AGE_COLORS) - 1)
                    if is_cursor:
                        attr = curses.color_pair(CURSOR_PAIR) | curses.A_BOLD
                    else:
                        attr = curses.color_pair(color_idx + 1) | curses.A_BOLD
                    try:
                        stdscr.addstr(r, screen_c, "██", attr)
                    except curses.error:
                        pass
                elif is_cursor:
                    try:
                        stdscr.addstr(r, screen_c, "▒▒", curses.color_pair(CURSOR_PAIR))
                    except curses.error:
                        pass

        # ── Status Bar ────────────────────────────────────────────────────
        status_y = max_rows - 2
        state = "PAUSED" if paused else "RUNNING"
        mode = " [EDIT]" if edit_mode else ""
        pop = len(game.alive)
        status = (
            f" Gen: {game.generation}  Pop: {pop}  Speed: {speed}  "
            f"State: {state}{mode}  |  H=Help  Q=Quit "
        )
        status = status.ljust(max_cols - 1)
        try:
            stdscr.addstr(status_y, 0, status[:max_cols - 1], curses.color_pair(STATUS_PAIR))
        except curses.error:
            pass

        # Preset hint line
        hint_y = max_rows - 1
        hint = " 1:Glider 2:LWSS 3:Pulsar 4:GliderGun 5:R-pent 6:Diehard 7:Acorn  SPACE:Pause E:Edit R:Random"
        try:
            stdscr.addstr(hint_y, 0, hint[:max_cols - 1], curses.color_pair(STATUS_PAIR))
        except curses.error:
            pass

        # ── Help Overlay ──────────────────────────────────────────────────
        if show_help:
            help_lines = [
                "╔══════════════════════════════════════════════╗",
                "║    Conway's Game of Life — Controls          ║",
                "║                                              ║",
                "║  SPACE    Pause / Resume                     ║",
                "║  N        Step one generation (paused)       ║",
                "║  C        Clear grid                         ║",
                "║  R        Randomize grid                     ║",
                "║  E        Toggle edit mode                   ║",
                "║  Arrows   Move cursor (edit mode)            ║",
                "║  ENTER    Toggle cell (edit mode)            ║",
                "║  +/-      Adjust speed                       ║",
                "║  1-7      Place preset at cursor             ║",
                "║  H        Toggle this help                   ║",
                "║  Q        Quit                               ║",
                "║                                              ║",
                "║  Colors show cell age:                       ║",
                "║  White → Cyan → Green → Yellow → Red → Pink  ║",
                "║                                              ║",
                "║  Grid wraps around (toroidal topology)       ║",
                "╚══════════════════════════════════════════════╝",
            ]
            start_r = max(0, (grid_rows - len(help_lines)) // 2)
            start_c = max(0, (max_cols - len(help_lines[0])) // 2)
            for i, line in enumerate(help_lines):
                try:
                    stdscr.addstr(start_r + i, start_c, line, curses.color_pair(HELP_PAIR) | curses.A_BOLD)
                except curses.error:
                    pass

        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
