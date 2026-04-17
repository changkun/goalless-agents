#!/usr/bin/env python3
"""Conway's Game of Life in the terminal. No dependencies."""
import os
import random
import shutil
import sys
import time

ALIVE = "█"
DEAD = " "
TRAIL = "·"

PATTERNS = {
    "glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "pulsar": [
        (2, 4), (2, 5), (2, 6), (2, 10), (2, 11), (2, 12),
        (4, 2), (5, 2), (6, 2), (4, 7), (5, 7), (6, 7),
        (4, 9), (5, 9), (6, 9), (4, 14), (5, 14), (6, 14),
        (7, 4), (7, 5), (7, 6), (7, 10), (7, 11), (7, 12),
        (9, 4), (9, 5), (9, 6), (9, 10), (9, 11), (9, 12),
        (10, 2), (11, 2), (12, 2), (10, 7), (11, 7), (12, 7),
        (10, 9), (11, 9), (12, 9), (10, 14), (11, 14), (12, 14),
        (14, 4), (14, 5), (14, 6), (14, 10), (14, 11), (14, 12),
    ],
    "gosper": [
        (5, 1), (5, 2), (6, 1), (6, 2),
        (5, 11), (6, 11), (7, 11), (4, 12), (8, 12),
        (3, 13), (9, 13), (3, 14), (9, 14), (6, 15),
        (4, 16), (8, 16), (5, 17), (6, 17), (7, 17), (6, 18),
        (3, 21), (4, 21), (5, 21), (3, 22), (4, 22), (5, 22),
        (2, 23), (6, 23), (1, 25), (2, 25), (6, 25), (7, 25),
        (3, 35), (4, 35), (3, 36), (4, 36),
    ],
}


def make_grid(w, h, pattern=None, density=0.25):
    g = [[0] * w for _ in range(h)]
    if pattern and pattern in PATTERNS:
        cy, cx = h // 2, w // 2
        cells = PATTERNS[pattern]
        oy = cy - max(r for r, _ in cells) // 2
        ox = cx - max(c for _, c in cells) // 2
        for r, c in cells:
            y, x = oy + r, ox + c
            if 0 <= y < h and 0 <= x < w:
                g[y][x] = 1
    else:
        for y in range(h):
            for x in range(w):
                g[y][x] = 1 if random.random() < density else 0
    return g


def step(g, w, h):
    new = [[0] * w for _ in range(h)]
    for y in range(h):
        for x in range(w):
            n = 0
            for dy in (-1, 0, 1):
                for dx in (-1, 0, 1):
                    if dy == 0 and dx == 0:
                        continue
                    n += g[(y + dy) % h][(x + dx) % w]
            if g[y][x] and n in (2, 3):
                new[y][x] = 1
            elif not g[y][x] and n == 3:
                new[y][x] = 1
    return new


def render(g, prev, w, h, gen, pop):
    out = [f"\x1b[H\x1b[2m gen {gen:>5}   pop {pop:>5}   {w}x{h}   ctrl-c to exit\x1b[0m\n"]
    for y in range(h):
        row = []
        for x in range(w):
            if g[y][x]:
                row.append(f"\x1b[92m{ALIVE}\x1b[0m")
            elif prev and prev[y][x]:
                row.append(f"\x1b[90m{TRAIL}\x1b[0m")
            else:
                row.append(DEAD)
        out.append("".join(row))
    sys.stdout.write("\n".join(out))
    sys.stdout.flush()


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "random"
    cols, rows = shutil.get_terminal_size((80, 24))
    w, h = cols, rows - 2
    g = make_grid(w, h, pattern if pattern != "random" else None)
    prev = None
    gen = 0
    sys.stdout.write("\x1b[2J\x1b[?25l")
    try:
        while True:
            pop = sum(sum(row) for row in g)
            render(g, prev, w, h, gen, pop)
            if pop == 0:
                time.sleep(1)
                g = make_grid(w, h, None)
                gen = 0
                continue
            prev = g
            g = step(g, w, h)
            gen += 1
            time.sleep(0.06)
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("\x1b[?25h\x1b[0m\n")


if __name__ == "__main__":
    main()
