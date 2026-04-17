#!/usr/bin/env python3
"""Conway's Game of Life — terminal edition."""

import os
import sys
import time
import random

ALIVE = "█"
DEAD = " "

def make_grid(rows, cols, density=0.3):
    return [[random.random() < density for c in range(cols)] for r in range(rows)]

def neighbors(grid, r, c, rows, cols):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = (r + dr) % rows, (c + dc) % cols
            count += grid[nr][nc]
    return count

def step(grid, rows, cols):
    new = [[False] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            n = neighbors(grid, r, c, rows, cols)
            if grid[r][c]:
                new[r][c] = n in (2, 3)
            else:
                new[r][c] = n == 3
    return new

def render(grid, gen, population):
    lines = []
    for row in grid:
        lines.append("".join(ALIVE if cell else DEAD for cell in row))
    frame = "\n".join(lines)
    return f"\033[H\033[J{frame}\n\n  Gen {gen}  |  Pop {population}  |  Ctrl-C to quit"

def main():
    try:
        size = os.get_terminal_size()
        cols = size.columns - 1
        rows = size.lines - 4
    except OSError:
        cols, rows = 60, 30

    rows = max(rows, 10)
    cols = max(cols, 20)

    grid = make_grid(rows, cols)
    gen = 0

    print("\033[?25l", end="", flush=True)  # hide cursor
    try:
        while True:
            population = sum(sum(row) for row in grid)
            print(render(grid, gen, population), end="", flush=True)
            time.sleep(0.1)
            grid = step(grid, rows, cols)
            gen += 1
    except KeyboardInterrupt:
        pass
    finally:
        print("\033[?25h")  # show cursor
        print(f"\n  Ran for {gen} generations. Life finds a way.\n")

if __name__ == "__main__":
    main()
