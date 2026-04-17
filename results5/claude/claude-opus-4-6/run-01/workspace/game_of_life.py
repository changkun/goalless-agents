#!/usr/bin/env python3
"""Conway's Game of Life — interactive terminal edition."""

import curses
import time
import copy
import random
import sys

PATTERNS = {
    "glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "blinker": [(0, 0), (0, 1), (0, 2)],
    "toad": [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)],
    "beacon": [(0, 0), (0, 1), (1, 0), (2, 3), (3, 2), (3, 3)],
    "pulsar": [
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
    "gosper_gun": [
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
    "lwss": [
        (0, 1), (0, 4),
        (1, 0),
        (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "pentadecathlon": [
        (0, 1), (1, 1), (2, 0), (2, 2), (3, 1), (4, 1),
        (5, 1), (6, 1), (7, 0), (7, 2), (8, 1), (9, 1),
    ],
    "r_pentomino": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    "acorn": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
}

PATTERN_NAMES = list(PATTERNS.keys())

SPEEDS = [
    ("Slowest", 1.0),
    ("Slow", 0.5),
    ("Medium", 0.2),
    ("Fast", 0.1),
    ("Fastest", 0.03),
]


class GameOfLife:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[False] * cols for _ in range(rows)]
        self.generation = 0
        self.population = 0

    def set_cell(self, r, c, alive=True):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = alive

    def toggle_cell(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = not self.grid[r][c]

    def count_neighbors(self, r, c):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = (r + dr) % self.rows, (c + dc) % self.cols
                if self.grid[nr][nc]:
                    count += 1
        return count

    def step(self):
        new_grid = [[False] * self.cols for _ in range(self.rows)]
        pop = 0
        for r in range(self.rows):
            for c in range(self.cols):
                n = self.count_neighbors(r, c)
                if self.grid[r][c]:
                    new_grid[r][c] = n in (2, 3)
                else:
                    new_grid[r][c] = n == 3
                if new_grid[r][c]:
                    pop += 1
        self.grid = new_grid
        self.generation += 1
        self.population = pop

    def clear(self):
        self.grid = [[False] * self.cols for _ in range(self.rows)]
        self.generation = 0
        self.population = 0

    def randomize(self, density=0.3):
        self.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.grid[r][c] = True
        self._count_population()

    def place_pattern(self, name, offset_r, offset_c):
        if name not in PATTERNS:
            return
        for dr, dc in PATTERNS[name]:
            self.set_cell(offset_r + dr, offset_c + dc, True)
        self._count_population()

    def _count_population(self):
        self.population = sum(sum(row) for row in self.grid)


ALIVE_CHAR = "\u2588\u2588"
DEAD_CHAR = "  "
CURSOR_ALIVE = "\u2593\u2593"
CURSOR_DEAD = "\u2591\u2591"


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)
        curses.init_pair(2, curses.COLOR_CYAN, -1)
        curses.init_pair(3, curses.COLOR_YELLOW, -1)
        curses.init_pair(4, curses.COLOR_RED, -1)
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(6, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(7, curses.COLOR_MAGENTA, -1)

    max_y, max_x = stdscr.getmaxyx()
    grid_rows = max_y - 4
    grid_cols = (max_x - 1) // 2

    if grid_rows < 10 or grid_cols < 20:
        stdscr.addstr(0, 0, "Terminal too small! Need at least 41x14.")
        stdscr.refresh()
        stdscr.nodelay(False)
        stdscr.getch()
        return

    game = GameOfLife(grid_rows, grid_cols)

    cursor_r, cursor_c = grid_rows // 2, grid_cols // 2
    running = False
    speed_idx = 2
    pattern_idx = 0
    last_step_time = 0
    show_help = True

    while True:
        now = time.time()

        if running and now - last_step_time >= SPEEDS[speed_idx][1]:
            game.step()
            last_step_time = now

        key = stdscr.getch()

        if key == ord('q') or key == 27:
            break
        elif key == ord(' '):
            if not running:
                game.toggle_cell(cursor_r, cursor_c)
                game._count_population()
        elif key == curses.KEY_ENTER or key == 10 or key == 13:
            running = not running
            if running:
                last_step_time = now
        elif key == ord('s') or key == ord('n'):
            if not running:
                game.step()
        elif key == ord('c'):
            game.clear()
            running = False
        elif key == ord('r'):
            game.randomize()
            running = False
        elif key == ord('p'):
            name = PATTERN_NAMES[pattern_idx]
            game.place_pattern(name, cursor_r, cursor_c)
        elif key == ord('[') or key == ord('{'):
            pattern_idx = (pattern_idx - 1) % len(PATTERN_NAMES)
        elif key == ord(']') or key == ord('}'):
            pattern_idx = (pattern_idx + 1) % len(PATTERN_NAMES)
        elif key == ord('-') or key == ord('_'):
            speed_idx = max(0, speed_idx - 1)
        elif key == ord('=') or key == ord('+'):
            speed_idx = min(len(SPEEDS) - 1, speed_idx + 1)
        elif key == ord('?'):
            show_help = not show_help
        elif key == curses.KEY_UP or key == ord('k'):
            cursor_r = (cursor_r - 1) % grid_rows
        elif key == curses.KEY_DOWN or key == ord('j'):
            cursor_r = (cursor_r + 1) % grid_rows
        elif key == curses.KEY_LEFT or key == ord('h'):
            cursor_c = (cursor_c - 1) % grid_cols
        elif key == curses.KEY_RIGHT or key == ord('l'):
            cursor_c = (cursor_c + 1) % grid_cols

        stdscr.erase()

        for r in range(grid_rows):
            for c in range(grid_cols):
                alive = game.grid[r][c]
                is_cursor = r == cursor_r and c == cursor_c

                if is_cursor:
                    ch = CURSOR_ALIVE if alive else CURSOR_DEAD
                    attr = curses.color_pair(3) | curses.A_BOLD
                else:
                    if alive:
                        ch = ALIVE_CHAR
                        attr = curses.color_pair(1) | curses.A_BOLD
                    else:
                        ch = DEAD_CHAR
                        attr = 0

                try:
                    stdscr.addstr(r, c * 2, ch, attr)
                except curses.error:
                    pass

        status_y = grid_rows
        separator = "\u2500" * (max_x - 1)
        try:
            stdscr.addstr(status_y, 0, separator, curses.color_pair(2))
        except curses.error:
            pass

        state_str = "\u25B6 RUNNING" if running else "\u23F8 PAUSED"
        state_color = curses.color_pair(1) if running else curses.color_pair(4)
        status = f" {state_str}  Gen: {game.generation}  Pop: {game.population}  Speed: {SPEEDS[speed_idx][0]}  Pattern: {PATTERN_NAMES[pattern_idx]}"
        try:
            stdscr.addstr(status_y + 1, 0, status[:max_x - 1], state_color | curses.A_BOLD)
        except curses.error:
            pass

        pos_info = f" Cursor: ({cursor_r},{cursor_c})  Grid: {grid_rows}x{grid_cols}"
        try:
            stdscr.addstr(status_y + 2, 0, pos_info[:max_x - 1], curses.color_pair(2))
        except curses.error:
            pass

        if show_help:
            help_text = " [Enter]Play/Pause [Space]Toggle [s]Step [p]Place [[]Prev/[]]Next pattern [-/+]Speed [r]Random [c]Clear [hjkl/Arrows]Move [?]Help [q]Quit"
            try:
                stdscr.addstr(status_y + 3, 0, help_text[:max_x - 1], curses.color_pair(7))
            except curses.error:
                pass

        stdscr.refresh()


if __name__ == "__main__":
    curses.wrapper(main)
