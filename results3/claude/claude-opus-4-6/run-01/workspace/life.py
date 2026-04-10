#!/usr/bin/env python3
"""
Conway's Game of Life — Interactive Terminal Edition

Controls:
  SPACE  — pause / resume
  r      — randomize grid
  c      — clear grid
  +/-    — speed up / slow down
  1-7    — place preset pattern at center
  h      — toggle heatmap (age-based coloring)
  t      — toggle trails (ghost traces of dead cells)
  arrows — move cursor
  ENTER  — toggle cell at cursor (while paused)
  q      — quit

Presets:
  1: Glider          2: Lightweight Spaceship   3: Pulsar
  4: Gosper Glider Gun  5: R-pentomino         6: Diehard
  7: Acorn
"""

import curses
import random
import time
import copy


# ── Patterns ────────────────────────────────────────────────────────────────

PATTERNS = {
    "Glider": [
        (0, 1),
        (1, 2),
        (2, 0), (2, 1), (2, 2),
    ],
    "LWSS": [
        (0, 1), (0, 4),
        (1, 0),
        (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "Pulsar": [],  # built programmatically below
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
    "R-pentomino": [
        (0, 1), (0, 2),
        (1, 0), (1, 1),
        (2, 1),
    ],
    "Diehard": [
        (0, 6),
        (1, 0), (1, 1),
        (2, 1), (2, 5), (2, 6), (2, 7),
    ],
    "Acorn": [
        (0, 1),
        (1, 3),
        (2, 0), (2, 1), (2, 4), (2, 5), (2, 6),
    ],
}

# Build Pulsar (period-3 oscillator) symmetrically
_pulsar = []
for dr, dc in [(2, 4), (2, 5), (2, 6), (4, 2), (5, 2), (6, 2), (4, 7), (5, 7), (6, 7), (7, 4), (7, 5), (7, 6)]:
    _pulsar.append((dr, dc))
    _pulsar.append((dr, 12 - dc))
    _pulsar.append((12 - dr, dc))
    _pulsar.append((12 - dr, 12 - dc))
PATTERNS["Pulsar"] = list(set(_pulsar))

PATTERN_KEYS = ["Glider", "LWSS", "Pulsar", "Gosper Glider Gun", "R-pentomino", "Diehard", "Acorn"]


# ── Game Engine ─────────────────────────────────────────────────────────────

class GameOfLife:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [[0] * cols for _ in range(rows)]
        self.age = [[0] * cols for _ in range(rows)]    # consecutive gens alive
        self.trail = [[0] * cols for _ in range(rows)]   # gens since death (0=never lived)
        self.generation = 0
        self.population = 0

    def randomize(self, density=0.3):
        self.generation = 0
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() < density else 0
                self.age[r][c] = 1 if self.grid[r][c] else 0
                self.trail[r][c] = 0
        self._count_population()

    def clear(self):
        self.generation = 0
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.age = [[0] * self.cols for _ in range(self.rows)]
        self.trail = [[0] * self.cols for _ in range(self.rows)]
        self.population = 0

    def place_pattern(self, name, offset_r=None, offset_c=None):
        cells = PATTERNS.get(name, [])
        if not cells:
            return
        # center the pattern if no offset given
        min_r = min(r for r, c in cells)
        max_r = max(r for r, c in cells)
        min_c = min(c for r, c in cells)
        max_c = max(c for r, c in cells)
        if offset_r is None:
            offset_r = self.rows // 2 - (max_r - min_r) // 2
        if offset_c is None:
            offset_c = self.cols // 2 - (max_c - min_c) // 2
        for r, c in cells:
            nr, nc = r + offset_r - min_r, c + offset_c - min_c
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                self.grid[nr][nc] = 1
        self._count_population()

    def step(self):
        new = [[0] * self.cols for _ in range(self.rows)]
        new_age = [[0] * self.cols for _ in range(self.rows)]
        new_trail = [[0] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                n = self._neighbors(r, c)
                if self.grid[r][c]:
                    alive = n in (2, 3)
                else:
                    alive = n == 3
                new[r][c] = 1 if alive else 0
                if alive:
                    new_age[r][c] = self.age[r][c] + 1
                    new_trail[r][c] = 0
                else:
                    new_age[r][c] = 0
                    # trail decays: if cell was alive or had a trail, increment
                    if self.grid[r][c] or self.trail[r][c] > 0:
                        new_trail[r][c] = self.trail[r][c] + 1 if self.trail[r][c] > 0 else 1
                    else:
                        new_trail[r][c] = 0
        self.grid = new
        self.age = new_age
        self.trail = new_trail
        self.generation += 1
        self._count_population()

    def _neighbors(self, r, c):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                count += self.grid[nr][nc]
        return count

    def _count_population(self):
        self.population = sum(sum(row) for row in self.grid)

    def toggle(self, r, c):
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] ^= 1
            self.age[r][c] = 1 if self.grid[r][c] else 0
            self.trail[r][c] = 0
            self._count_population()


# ── Terminal UI ─────────────────────────────────────────────────────────────

SPEED_LEVELS = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
SPEED_NAMES = ["1x", "2x", "5x", "10x", "20x", "50x", "100x"]

CELL_ALIVE = "\u2588\u2588"  # ██
CELL_DEAD = "  "
CELL_CURSOR_ALIVE = "\u2593\u2593"  # ▓▓
CELL_CURSOR_DEAD = "\u2591\u2591"  # ░░


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(50)

    # init colors
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)    # alive cells / age 1
    curses.init_pair(2, curses.COLOR_WHITE, -1)    # dead cells
    curses.init_pair(3, curses.COLOR_YELLOW, -1)   # status bar
    curses.init_pair(4, curses.COLOR_CYAN, -1)     # help text
    curses.init_pair(5, curses.COLOR_RED, -1)      # cursor
    # heatmap age colors (6-9)
    curses.init_pair(6, curses.COLOR_GREEN, -1)    # newborn (1-3 gens)
    curses.init_pair(7, curses.COLOR_YELLOW, -1)   # young (4-10 gens)
    curses.init_pair(8, curses.COLOR_RED, -1)      # mature (11-30 gens)
    curses.init_pair(9, curses.COLOR_MAGENTA, -1)  # ancient (31+ gens)
    # trail colors (10-12)
    curses.init_pair(10, curses.COLOR_CYAN, -1)    # just died
    curses.init_pair(11, curses.COLOR_BLUE, -1)    # fading
    curses.init_pair(12, curses.COLOR_WHITE, -1)   # almost gone

    max_y, max_x = stdscr.getmaxyx()
    grid_rows = max_y - 3  # reserve 3 lines for UI
    grid_cols = max_x // 2  # each cell is 2 chars wide

    game = GameOfLife(grid_rows, grid_cols)
    game.randomize()

    paused = False
    speed_idx = 3  # start at 10x
    cursor_r, cursor_c = grid_rows // 2, grid_cols // 2
    last_step = time.time()
    message = ""
    message_time = 0
    heatmap = False
    trails = False

    TRAIL_CHARS = ["\u2593\u2593", "\u2592\u2592", "\u2591\u2591"]  # ▓▓ ▒▒ ░░
    TRAIL_MAX = 9  # trail fades over 9 generations

    while True:
        now = time.time()

        # ── Input ───────────────────────────────────────────────────────
        key = stdscr.getch()
        if key == ord('q'):
            break
        elif key == ord(' '):
            paused = not paused
            message = "PAUSED" if paused else "RUNNING"
            message_time = now
        elif key == ord('r'):
            game.randomize()
            message = "Randomized"
            message_time = now
        elif key == ord('c'):
            game.clear()
            message = "Cleared"
            message_time = now
        elif key in (ord('+'), ord('=')):
            speed_idx = min(speed_idx + 1, len(SPEED_LEVELS) - 1)
            message = f"Speed: {SPEED_NAMES[speed_idx]}"
            message_time = now
        elif key in (ord('-'), ord('_')):
            speed_idx = max(speed_idx - 1, 0)
            message = f"Speed: {SPEED_NAMES[speed_idx]}"
            message_time = now
        elif key == curses.KEY_UP:
            cursor_r = (cursor_r - 1) % grid_rows
        elif key == curses.KEY_DOWN:
            cursor_r = (cursor_r + 1) % grid_rows
        elif key == curses.KEY_LEFT:
            cursor_c = (cursor_c - 1) % grid_cols
        elif key == curses.KEY_RIGHT:
            cursor_c = (cursor_c + 1) % grid_cols
        elif key in (ord('\n'), ord('\r')):
            game.toggle(cursor_r, cursor_c)
        elif key == ord('h'):
            heatmap = not heatmap
            message = f"Heatmap: {'ON' if heatmap else 'OFF'}"
            message_time = now
        elif key == ord('t'):
            trails = not trails
            message = f"Trails: {'ON' if trails else 'OFF'}"
            message_time = now
        elif ord('1') <= key <= ord('7'):
            idx = key - ord('1')
            name = PATTERN_KEYS[idx]
            if paused:
                game.place_pattern(name, cursor_r, cursor_c)
                message = f"Placed {name} at cursor"
            else:
                game.clear()
                game.place_pattern(name)
                message = f"Loaded {name}"
            message_time = now

        # ── Simulation step ─────────────────────────────────────────────
        if not paused and (now - last_step) >= SPEED_LEVELS[speed_idx]:
            game.step()
            last_step = now

        # ── Render ──────────────────────────────────────────────────────
        try:
            stdscr.erase()

            # draw grid
            for r in range(min(grid_rows, max_y - 3)):
                for c in range(min(grid_cols, max_x // 2)):
                    is_cursor = (r == cursor_r and c == cursor_c)
                    alive = game.grid[r][c]
                    if is_cursor:
                        ch = CELL_CURSOR_ALIVE if alive else CELL_CURSOR_DEAD
                        stdscr.addstr(r, c * 2, ch, curses.color_pair(5) | curses.A_BOLD)
                    elif alive:
                        if heatmap:
                            a = game.age[r][c]
                            if a <= 3:
                                pair = 6
                            elif a <= 10:
                                pair = 7
                            elif a <= 30:
                                pair = 8
                            else:
                                pair = 9
                            stdscr.addstr(r, c * 2, CELL_ALIVE, curses.color_pair(pair))
                        else:
                            stdscr.addstr(r, c * 2, CELL_ALIVE, curses.color_pair(1))
                    elif trails and game.trail[r][c] > 0:
                        t = game.trail[r][c]
                        if t <= TRAIL_MAX:
                            ci = min(t - 1, 2)  # 0,1,2 → char index
                            ti = 10 if t <= 3 else (11 if t <= 6 else 12)
                            stdscr.addstr(r, c * 2, TRAIL_CHARS[ci],
                                          curses.color_pair(ti) | curses.A_DIM)
                    # dead cells with no trail are blank — skip for speed

            # status bar
            status_y = max_y - 3
            state = "PAUSED" if paused else "RUNNING"
            hm = "H" if heatmap else "-"
            tr = "T" if trails else "-"
            status = (
                f" Gen: {game.generation:>6}  |  Pop: {game.population:>5}  |  "
                f"Speed: {SPEED_NAMES[speed_idx]:>4}  |  [{hm}{tr}]  |  {state}  "
            )
            stdscr.addstr(status_y, 0, status.ljust(max_x - 1), curses.color_pair(3) | curses.A_BOLD)

            # message line
            if message and (now - message_time) < 2.0:
                stdscr.addstr(status_y + 1, 1, message, curses.color_pair(4))

            # help line
            help_text = " SPC:pause  r:random  c:clear  +/-:speed  1-7:patterns  h:heatmap  t:trails  arrows+ENTER:edit  q:quit"
            stdscr.addstr(max_y - 1, 0, help_text[:max_x - 1], curses.color_pair(4) | curses.A_DIM)

            stdscr.refresh()
        except curses.error:
            pass  # terminal too small momentarily


if __name__ == "__main__":
    curses.wrapper(main)
