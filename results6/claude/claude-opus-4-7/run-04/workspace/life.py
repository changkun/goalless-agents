#!/usr/bin/env python3
"""Conway's Game of Life — terminal edition.

Usage: python3 life.py [pattern] [--size WxH] [--fps N] [--steps N]
Patterns: glider, gun, pulsar, acorn, random (default)
"""
import argparse
import os
import random
import shutil
import sys
import time

PATTERNS = {
    "glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "pulsar": [
        (0, 2), (0, 3), (0, 4), (0, 8), (0, 9), (0, 10),
        (2, 0), (3, 0), (4, 0), (2, 5), (3, 5), (4, 5),
        (2, 7), (3, 7), (4, 7), (2, 12), (3, 12), (4, 12),
        (5, 2), (5, 3), (5, 4), (5, 8), (5, 9), (5, 10),
        (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (7, 10),
        (8, 0), (9, 0), (10, 0), (8, 5), (9, 5), (10, 5),
        (8, 7), (9, 7), (10, 7), (8, 12), (9, 12), (10, 12),
        (12, 2), (12, 3), (12, 4), (12, 8), (12, 9), (12, 10),
    ],
    "acorn": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
    "gun": [  # Gosper glider gun
        (4, 0), (4, 1), (5, 0), (5, 1),
        (4, 10), (5, 10), (6, 10), (3, 11), (7, 11),
        (2, 12), (8, 12), (2, 13), (8, 13), (5, 14),
        (3, 15), (7, 15), (4, 16), (5, 16), (6, 16), (5, 17),
        (2, 20), (3, 20), (4, 20), (2, 21), (3, 21), (4, 21),
        (1, 22), (5, 22), (0, 24), (1, 24), (5, 24), (6, 24),
        (2, 34), (3, 34), (2, 35), (3, 35),
    ],
}


def make_grid(w, h, pattern, seed=None):
    grid = [[0] * w for _ in range(h)]
    if pattern == "random":
        rng = random.Random(seed)
        for y in range(h):
            for x in range(w):
                grid[y][x] = 1 if rng.random() < 0.25 else 0
        return grid
    cells = PATTERNS[pattern]
    ph = max(r for r, _ in cells) + 1
    pw = max(c for _, c in cells) + 1
    oy, ox = (h - ph) // 2, (w - pw) // 2
    for r, c in cells:
        y, x = oy + r, ox + c
        if 0 <= y < h and 0 <= x < w:
            grid[y][x] = 1
    return grid


def step(grid, w, h):
    new = [[0] * w for _ in range(h)]
    for y in range(h):
        yu, yd = (y - 1) % h, (y + 1) % h
        for x in range(w):
            xl, xr = (x - 1) % w, (x + 1) % w
            n = (grid[yu][xl] + grid[yu][x] + grid[yu][xr]
                 + grid[y][xl] + grid[y][xr]
                 + grid[yd][xl] + grid[yd][x] + grid[yd][xr])
            new[y][x] = 1 if n == 3 or (grid[y][x] and n == 2) else 0
    return new


def render(grid, w, h, gen, pattern):
    # Two rows per character using half-block glyphs for square cells.
    out = [f"\x1b[H\x1b[2J\x1b[38;5;46m"]  # home, clear, green
    for y in range(0, h, 2):
        row = []
        for x in range(w):
            top = grid[y][x]
            bot = grid[y + 1][x] if y + 1 < h else 0
            row.append(("█" if top and bot else "▀" if top else "▄" if bot else " "))
        out.append("".join(row))
        out.append("\n")
    out.append(f"\x1b[0m pattern={pattern}  gen={gen}  {w}x{h}  Ctrl-C to quit")
    sys.stdout.write("".join(out))
    sys.stdout.flush()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("pattern", nargs="?", default="random",
                   choices=["random", *PATTERNS.keys()])
    p.add_argument("--size", default=None, help="WxH, e.g. 80x40")
    p.add_argument("--fps", type=float, default=15)
    p.add_argument("--steps", type=int, default=0, help="0 = infinite")
    p.add_argument("--seed", type=int, default=None)
    args = p.parse_args()

    if args.size:
        w, h = (int(v) for v in args.size.lower().split("x"))
    else:
        ts = shutil.get_terminal_size((80, 24))
        w, h = ts.columns, (ts.lines - 2) * 2

    grid = make_grid(w, h, args.pattern, args.seed)
    delay = 1.0 / args.fps
    gen = 0
    sys.stdout.write("\x1b[?25l")  # hide cursor
    try:
        while True:
            render(grid, w, h, gen, args.pattern)
            if args.steps and gen >= args.steps:
                break
            time.sleep(delay)
            grid = step(grid, w, h)
            gen += 1
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[?25h\n")


if __name__ == "__main__":
    main()
