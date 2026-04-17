#!/usr/bin/env python3
"""Conway's Game of Life — terminal edition."""

import os
import sys
import time
import random

WIDTH = 60
HEIGHT = 30
ALIVE = "█"
DEAD = " "


def make_grid():
    return [[random.random() < 0.3 for _ in range(WIDTH)] for _ in range(HEIGHT)]


def neighbors(grid, r, c):
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr, nc = (r + dr) % HEIGHT, (c + dc) % WIDTH
            count += grid[nr][nc]
    return count


def step(grid):
    new = [[False] * WIDTH for _ in range(HEIGHT)]
    for r in range(HEIGHT):
        for c in range(WIDTH):
            n = neighbors(grid, r, c)
            if grid[r][c]:
                new[r][c] = n in (2, 3)
            else:
                new[r][c] = n == 3
    return new


def render(grid, gen, pop):
    buf = [f"\033[H\033[J\033[1;36m{'═' * WIDTH}\033[0m"]
    for row in grid:
        buf.append("".join(ALIVE if c else DEAD for c in row))
    buf.append(f"\033[1;36m{'═' * WIDTH}\033[0m")
    buf.append(f"\033[1mGen {gen:>5}  Pop {pop:>4}\033[0m  (Ctrl+C to quit)")
    sys.stdout.write("\n".join(buf) + "\n")
    sys.stdout.flush()


def main():
    grid = make_grid()
    gen = 0
    os.system("clear" if os.name != "nt" else "cls")
    try:
        while True:
            pop = sum(sum(row) for row in grid)
            render(grid, gen, pop)
            time.sleep(0.1)
            grid = step(grid)
            gen += 1
    except KeyboardInterrupt:
        print("\n\033[1;32mSimulation ended.\033[0m")


if __name__ == "__main__":
    main()
