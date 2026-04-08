#!/usr/bin/env python3
"""Conway's Game of Life — terminal edition.

Controls:
  Space    Pause / Resume
  r        Random reset
  p        Next preset pattern
  +/=      Speed up
  -        Slow down
  c        Clear grid
  q / Esc  Quit
"""

import curses
import random
import time

PRESETS = {
    "Glider": [(0,1),(1,2),(2,0),(2,1),(2,2)],
    "Blinker": [(0,0),(0,1),(0,2)],
    "Beacon": [(0,0),(0,1),(1,0),(1,1),(2,2),(2,3),(3,2),(3,3)],
    "Toad": [(0,1),(0,2),(0,3),(1,0),(1,1),(1,2)],
    "Glider Gun": [
        (0,24),(1,22),(1,24),(2,12),(2,13),(2,20),(2,21),(2,34),(2,35),
        (3,11),(3,15),(3,20),(3,21),(3,34),(3,35),(4,0),(4,1),(4,10),
        (4,16),(4,20),(4,21),(5,0),(5,1),(5,10),(5,14),(5,16),(5,17),
        (5,22),(5,24),(6,10),(6,16),(6,24),(7,11),(7,15),(8,12),(8,13),
    ],
    "Pulsar": [
        (0,2),(0,3),(0,4),(0,8),(0,9),(0,10),
        (2,0),(2,5),(2,7),(2,12),(3,0),(3,5),(3,7),(3,12),
        (4,0),(4,5),(4,7),(4,12),(5,2),(5,3),(5,4),(5,8),(5,9),(5,10),
        (7,2),(7,3),(7,4),(7,8),(7,9),(7,10),
        (8,0),(8,5),(8,7),(8,12),(9,0),(9,5),(9,7),(9,12),
        (10,0),(10,5),(10,7),(10,12),(12,2),(12,3),(12,4),(12,8),(12,9),(12,10),
    ],
    "R-pentomino": [(0,1),(0,2),(1,0),(1,1),(2,1)],
    "LWSS": [(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)],
}

PRESET_NAMES = list(PRESETS.keys())


def make_grid(rows, cols):
    return [[False] * cols for _ in range(rows)]


def randomize(rows, cols, density=0.3):
    return [[random.random() < density for _ in range(cols)] for _ in range(rows)]


def place_preset(rows, cols, name):
    grid = make_grid(rows, cols)
    cells = PRESETS[name]
    max_r = max(r for r, c in cells)
    max_c = max(c for r, c in cells)
    or_ = (rows - max_r) // 2
    oc = (cols - max_c) // 2
    for r, c in cells:
        nr, nc = or_ + r, oc + c
        if 0 <= nr < rows and 0 <= nc < cols:
            grid[nr][nc] = True
    return grid


def step(grid, rows, cols):
    new = make_grid(rows, cols)
    for r in range(rows):
        for c in range(cols):
            alive = grid[r][c]
            neighbors = sum(
                grid[(r + dr) % rows][(c + dc) % cols]
                for dr in (-1, 0, 1)
                for dc in (-1, 0, 1)
                if (dr, dc) != (0, 0)
            )
            new[r][c] = neighbors == 3 or (alive and neighbors == 2)
    return new


def count_alive(grid):
    return sum(cell for row in grid for cell in row)


def draw(stdscr, grid, rows, cols, gen, alive, paused, speed, preset_idx):
    stdscr.erase()
    sh, sw = stdscr.getmaxyx()

    # Draw cells
    for r in range(min(rows, sh - 2)):
        for c in range(min(cols, sw)):
            if grid[r][c]:
                try:
                    stdscr.addch(r, c, ord('\u2588'), curses.color_pair(1))
                except curses.error:
                    pass

    # Status bar
    status = (
        f" Gen:{gen:>6}  Alive:{alive:>6}  Speed:{speed:>3}  "
        f"{'[PAUSED]' if paused else '[RUNNING]':10}  "
        f"Preset: {PRESET_NAMES[preset_idx]}  "
        f" [Space]Pause [r]Random [p]Preset [+/-]Speed [c]Clear [q]Quit "
    )
    try:
        stdscr.addstr(sh - 1, 0, status[:sw - 1], curses.color_pair(2) | curses.A_BOLD)
    except curses.error:
        pass

    stdscr.refresh()


def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_CYAN)

    sh, sw = stdscr.getmaxyx()
    rows, cols = sh - 2, sw

    grid = randomize(rows, cols)
    gen = 0
    paused = False
    speed = 10          # frames per second
    preset_idx = 0
    last_tick = time.monotonic()

    while True:
        key = stdscr.getch()

        if key in (ord('q'), ord('Q'), 27):   # q or Esc
            break
        elif key == ord(' '):
            paused = not paused
        elif key in (ord('r'), ord('R')):
            grid = randomize(rows, cols)
            gen = 0
        elif key in (ord('p'), ord('P')):
            preset_idx = (preset_idx + 1) % len(PRESET_NAMES)
            grid = place_preset(rows, cols, PRESET_NAMES[preset_idx])
            gen = 0
        elif key in (ord('+'), ord('=')):
            speed = min(60, speed + 5)
        elif key == ord('-'):
            speed = max(1, speed - 5)
        elif key in (ord('c'), ord('C')):
            grid = make_grid(rows, cols)
            gen = 0

        now = time.monotonic()
        if not paused and now - last_tick >= 1.0 / speed:
            grid = step(grid, rows, cols)
            gen += 1
            last_tick = now

        alive = count_alive(grid)
        draw(stdscr, grid, rows, cols, gen, alive, paused, speed, preset_idx)
        time.sleep(0.01)


if __name__ == "__main__":
    curses.wrapper(main)
