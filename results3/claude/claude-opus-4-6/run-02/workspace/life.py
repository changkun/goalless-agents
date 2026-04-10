#!/usr/bin/env python3
"""
Conway's Game of Life — Interactive Terminal Simulator

Controls:
  SPACE    Pause / Resume
  S        Step one generation (while paused)
  R        Randomize the grid
  C        Clear the grid
  1-5      Load preset pattern (1=Glider, 2=Pulsar, 3=Gosper Gun, 4=LWSS, 5=Pentadecathlon)
  +/-      Speed up / slow down
  Arrow keys  Pan the viewport
  Q        Quit
"""

import curses
import random
import time
import sys


# ── Core Engine ──────────────────────────────────────────────────────────────

class Grid:
    """Sparse set-based grid for unbounded Game of Life."""

    def __init__(self):
        self.alive = set()  # set of (row, col) tuples

    def clear(self):
        self.alive.clear()

    def toggle(self, r, c):
        cell = (r, c)
        if cell in self.alive:
            self.alive.discard(cell)
        else:
            self.alive.add(cell)

    def set_alive(self, r, c):
        self.alive.add((r, c))

    def step(self):
        """Advance one generation using standard B3/S23 rules."""
        neighbor_counts = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nb = (r + dr, c + dc)
                    neighbor_counts[nb] = neighbor_counts.get(nb, 0) + 1

        new_alive = set()
        for cell, count in neighbor_counts.items():
            if count == 3 or (count == 2 and cell in self.alive):
                new_alive.add(cell)
        self.alive = new_alive

    def randomize(self, rows, cols, density=0.3):
        self.alive.clear()
        for r in range(rows):
            for c in range(cols):
                if random.random() < density:
                    self.alive.add((r, c))

    def population(self):
        return len(self.alive)

    def bounding_box(self):
        if not self.alive:
            return (0, 0, 0, 0)
        rs = [r for r, c in self.alive]
        cs = [c for r, c in self.alive]
        return (min(rs), min(cs), max(rs), max(cs))

    def place_pattern(self, pattern, offset_r=0, offset_c=0):
        """Place a list of (r, c) relative coords onto the grid."""
        for r, c in pattern:
            self.alive.add((r + offset_r, c + offset_c))


# ── Preset Patterns ──────────────────────────────────────────────────────────

PATTERNS = {}

# 1 — Glider
PATTERNS["Glider"] = [
    (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
]

# 2 — Pulsar (period 3 oscillator)
_pulsar = []
for r, c in [
    (2, 4), (2, 5), (2, 6), (2, 10), (2, 11), (2, 12),
    (4, 2), (4, 7), (4, 9), (4, 14),
    (5, 2), (5, 7), (5, 9), (5, 14),
    (6, 2), (6, 7), (6, 9), (6, 14),
    (7, 4), (7, 5), (7, 6), (7, 10), (7, 11), (7, 12),
]:
    _pulsar.append((r, c))
    _pulsar.append((14 - r, c))  # vertical mirror
PATTERNS["Pulsar"] = list(set(_pulsar))

# 3 — Gosper Glider Gun
PATTERNS["Gosper Gun"] = [
    (5, 1), (5, 2), (6, 1), (6, 2),
    (5, 11), (6, 11), (7, 11),
    (4, 12), (8, 12),
    (3, 13), (9, 13), (3, 14), (9, 14),
    (6, 15),
    (4, 16), (8, 16),
    (5, 17), (6, 17), (7, 17),
    (6, 18),
    (3, 21), (4, 21), (5, 21),
    (3, 22), (4, 22), (5, 22),
    (2, 23), (6, 23),
    (1, 25), (2, 25), (6, 25), (7, 25),
    (3, 35), (4, 35), (3, 36), (4, 36),
]

# 4 — Lightweight Spaceship (LWSS)
PATTERNS["LWSS"] = [
    (0, 1), (0, 4),
    (1, 0),
    (2, 0), (2, 4),
    (3, 0), (3, 1), (3, 2), (3, 3),
]

# 5 — Pentadecathlon (period 15 oscillator)
PATTERNS["Pentadecathlon"] = [
    (0, 1), (1, 1), (2, 0), (2, 2), (3, 1), (4, 1),
    (5, 1), (6, 1), (7, 0), (7, 2), (8, 1), (9, 1),
]

PATTERN_KEYS = list(PATTERNS.keys())


# ── Rendering ────────────────────────────────────────────────────────────────

CELL_CHAR = "\u2588\u2588"  # two full-block chars per cell for square pixels
EMPTY_CHAR = "  "


def render(stdscr, grid, cam_r, cam_c, paused, generation, speed_ms):
    """Draw the grid and status bar."""
    max_y, max_x = stdscr.getmaxyx()
    draw_rows = max_y - 2  # leave 2 rows for status
    draw_cols = max_x // 2  # each cell is 2 chars wide

    stdscr.erase()

    for sr in range(draw_rows):
        for sc in range(draw_cols):
            gr = cam_r + sr
            gc = cam_c + sc
            if (gr, gc) in grid.alive:
                try:
                    stdscr.addstr(sr, sc * 2, CELL_CHAR, curses.color_pair(1))
                except curses.error:
                    pass

    # Status bar
    status_line = max_y - 2
    state = "PAUSED" if paused else "RUNNING"
    pop = grid.population()
    info = (
        f" {state}  |  Gen: {generation}  |  Pop: {pop}  |  "
        f"Speed: {speed_ms}ms  |  View: ({cam_r},{cam_c})"
    )
    help_line = " [SPACE]Pause [S]Step [R]Random [C]Clear [1-5]Pattern [+/-]Speed [Arrows]Pan [Q]Quit"

    try:
        stdscr.addstr(status_line, 0, info[:max_x - 1], curses.A_REVERSE | curses.A_BOLD)
        stdscr.addstr(status_line + 1, 0, help_line[:max_x - 1], curses.A_DIM)
    except curses.error:
        pass

    stdscr.refresh()


# ── Main Loop ────────────────────────────────────────────────────────────────

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)

    grid = Grid()
    generation = 0
    paused = True
    speed_ms = 100  # ms between generations
    cam_r, cam_c = 0, 0

    # Start with Gosper Glider Gun centered
    max_y, max_x = stdscr.getmaxyx()
    center_r = max_y // 4
    center_c = max_x // 8
    grid.place_pattern(PATTERNS["Gosper Gun"], center_r, center_c)

    last_step = time.monotonic()

    while True:
        # ── Input ────────────────────────────────────────────────────
        key = stdscr.getch()

        if key == ord('q') or key == ord('Q'):
            break
        elif key == ord(' '):
            paused = not paused
        elif key == ord('s') or key == ord('S'):
            if paused:
                grid.step()
                generation += 1
        elif key == ord('r') or key == ord('R'):
            rows = max_y - 2
            cols = max_x // 2
            grid.randomize(rows, cols)
            generation = 0
            cam_r, cam_c = 0, 0
        elif key == ord('c') or key == ord('C'):
            grid.clear()
            generation = 0
        elif key in (ord('1'), ord('2'), ord('3'), ord('4'), ord('5')):
            idx = key - ord('1')
            grid.clear()
            generation = 0
            name = PATTERN_KEYS[idx]
            max_y2, max_x2 = stdscr.getmaxyx()
            cr = (max_y2 - 2) // 4
            cc = max_x2 // 8
            cam_r, cam_c = 0, 0
            grid.place_pattern(PATTERNS[name], cr, cc)
        elif key == ord('+') or key == ord('='):
            speed_ms = max(10, speed_ms - 20)
        elif key == ord('-') or key == ord('_'):
            speed_ms = min(1000, speed_ms + 20)
        elif key == curses.KEY_UP:
            cam_r -= 3
        elif key == curses.KEY_DOWN:
            cam_r += 3
        elif key == curses.KEY_LEFT:
            cam_c -= 3
        elif key == curses.KEY_RIGHT:
            cam_c += 3

        # ── Simulation Step ──────────────────────────────────────────
        now = time.monotonic()
        if not paused and (now - last_step) * 1000 >= speed_ms:
            grid.step()
            generation += 1
            last_step = now

        # ── Render ───────────────────────────────────────────────────
        render(stdscr, grid, cam_r, cam_c, paused, generation, speed_ms)

        # Small sleep to avoid busy-looping
        time.sleep(0.016)  # ~60 fps cap


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
