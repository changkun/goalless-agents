#!/usr/bin/env python3
"""Conway's Game of Life in the terminal. No deps. Ctrl-C to quit."""
import argparse
import os
import random
import shutil
import sys
import time

ALIVE = "█"
DEAD = " "

PATTERNS = {
    "glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "gosper": [
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
}


def make_grid(rows, cols, pattern=None, density=0.25):
    grid = [[0] * cols for _ in range(rows)]
    if pattern and pattern in PATTERNS:
        cells = PATTERNS[pattern]
        pr = max(r for r, _ in cells) + 1
        pc = max(c for _, c in cells) + 1
        off_r = max(0, (rows - pr) // 2)
        off_c = max(0, (cols - pc) // 2)
        for r, c in cells:
            if 0 <= off_r + r < rows and 0 <= off_c + c < cols:
                grid[off_r + r][off_c + c] = 1
    else:
        for r in range(rows):
            for c in range(cols):
                grid[r][c] = 1 if random.random() < density else 0
    return grid


def step(grid, rows, cols):
    new = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            n = 0
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = (r + dr) % rows, (c + dc) % cols
                    n += grid[nr][nc]
            if grid[r][c] and n in (2, 3):
                new[r][c] = 1
            elif not grid[r][c] and n == 3:
                new[r][c] = 1
    return new


def render(grid):
    return "\n".join("".join(ALIVE if cell else DEAD for cell in row) for row in grid)


def main():
    ap = argparse.ArgumentParser(description="Conway's Game of Life")
    ap.add_argument("--pattern", choices=list(PATTERNS) + ["random"], default="random")
    ap.add_argument("--fps", type=float, default=15)
    ap.add_argument("--density", type=float, default=0.25)
    ap.add_argument("--generations", type=int, default=0, help="0 = forever")
    args = ap.parse_args()

    size = shutil.get_terminal_size((80, 24))
    cols = size.columns
    rows = size.lines - 2

    pattern = None if args.pattern == "random" else args.pattern
    grid = make_grid(rows, cols, pattern=pattern, density=args.density)

    gen = 0
    delay = 1.0 / max(args.fps, 0.1)
    try:
        sys.stdout.write("\x1b[?25l")  # hide cursor
        while True:
            alive = sum(sum(row) for row in grid)
            sys.stdout.write("\x1b[H\x1b[2J")
            sys.stdout.write(render(grid))
            sys.stdout.write(f"\n gen={gen}  alive={alive}  pattern={args.pattern}  (Ctrl-C to quit)")
            sys.stdout.flush()
            time.sleep(delay)
            grid = step(grid, rows, cols)
            gen += 1
            if args.generations and gen >= args.generations:
                break
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[?25h\n")  # show cursor
        sys.stdout.flush()


if __name__ == "__main__":
    main()
