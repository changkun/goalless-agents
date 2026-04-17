#!/usr/bin/env python3
"""Conway's Game of Life — terminal edition."""

import os
import sys
import time
import random
import shutil

ALIVE_CHARS = ["█", "▓", "▒", "░"]
COLORS = [
    "\033[38;5;46m",   # green
    "\033[38;5;47m",   # light green
    "\033[38;5;48m",   # teal
    "\033[38;5;82m",   # lime
    "\033[38;5;118m",  # bright green
    "\033[38;5;154m",  # yellow-green
    "\033[38;5;190m",  # yellow
    "\033[38;5;226m",  # bright yellow
    "\033[38;5;214m",  # orange
    "\033[38;5;202m",  # red-orange
]
RESET = "\033[0m"
DIM = "\033[2m"

def make_grid(rows, cols, density=0.3):
    return [[random.random() < density for _ in range(cols)] for _ in range(rows)]

def seed_pattern(grid, rows, cols):
    patterns = [glider_gun, r_pentomino, acorn, diehard]
    if rows > 20 and cols > 40:
        random.choice(patterns)(grid, rows, cols)
    else:
        r_pentomino(grid, rows, cols)

def glider_gun(grid, rows, cols):
    cy, cx = rows // 2 - 5, cols // 4
    gun = [
        (4,0),(4,1),(5,0),(5,1),
        (4,10),(5,10),(6,10),(3,11),(7,11),(2,12),(8,12),(2,13),(8,13),
        (5,14),(3,15),(7,15),(4,16),(5,16),(6,16),(5,17),
        (2,20),(3,20),(4,20),(2,21),(3,21),(4,21),(1,22),(5,22),
        (0,24),(1,24),(5,24),(6,24),
        (2,34),(3,34),(2,35),(3,35),
    ]
    for dy, dx in gun:
        y, x = cy + dy, cx + dx
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = True

def r_pentomino(grid, rows, cols):
    cy, cx = rows // 2, cols // 2
    for dy, dx in [(-1,0),(-1,1),(0,-1),(0,0),(1,0)]:
        grid[cy+dy][cx+dx] = True

def acorn(grid, rows, cols):
    cy, cx = rows // 2, cols // 2 - 3
    for dy, dx in [(0,1),(1,3),(2,0),(2,1),(2,4),(2,5),(2,6)]:
        y, x = cy + dy, cx + dx
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = True

def diehard(grid, rows, cols):
    cy, cx = rows // 2, cols // 2 - 3
    for dy, dx in [(0,6),(1,0),(1,1),(2,1),(2,5),(2,6),(2,7)]:
        y, x = cy + dy, cx + dx
        if 0 <= y < rows and 0 <= x < cols:
            grid[y][x] = True

def count_neighbors(grid, rows, cols, y, x):
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dy == 0 and dx == 0:
                continue
            ny, nx = (y + dy) % rows, (x + dx) % cols
            count += grid[ny][nx]
    return count

def step(grid, rows, cols, age):
    new_grid = [[False] * cols for _ in range(rows)]
    new_age = [[0] * cols for _ in range(rows)]
    for y in range(rows):
        for x in range(cols):
            n = count_neighbors(grid, rows, cols, y, x)
            if grid[y][x]:
                if n in (2, 3):
                    new_grid[y][x] = True
                    new_age[y][x] = age[y][x] + 1
            else:
                if n == 3:
                    new_grid[y][x] = True
                    new_age[y][x] = 1
    return new_grid, new_age

def render(grid, age, rows, cols, gen, pop):
    lines = [f"\033[H\033[38;5;240m{'Game of Life':^{cols}}  Gen: {gen}  Pop: {pop}{RESET}"]
    for y in range(rows):
        row = []
        for x in range(cols):
            if grid[y][x]:
                a = min(age[y][x], len(COLORS) - 1)
                char_idx = min(age[y][x] // 3, len(ALIVE_CHARS) - 1)
                row.append(f"{COLORS[a]}{ALIVE_CHARS[char_idx]}{RESET}")
            else:
                row.append(" ")
        lines.append("".join(row))
    sys.stdout.write("\n".join(lines))
    sys.stdout.flush()

def main():
    term = shutil.get_terminal_size((80, 24))
    cols = term.columns
    rows = term.lines - 2

    grid = [[False] * cols for _ in range(rows)]
    age = [[0] * cols for _ in range(rows)]

    seed_pattern(grid, rows, cols)

    sys.stdout.write("\033[2J\033[?25l")

    try:
        gen = 0
        while True:
            pop = sum(sum(row) for row in grid)
            render(grid, age, rows, cols, gen, pop)
            grid, age = step(grid, rows, cols, age)
            gen += 1
            time.sleep(0.08)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write(f"\033[?25l\033[{rows+2};0H{RESET}\033[?25h\n")
        print(f"Ended after {gen} generations.")

if __name__ == "__main__":
    main()
