#!/usr/bin/env python3
"""Conway's Game of Life in the terminal."""
import os, time, random, sys

W, H = os.get_terminal_size().columns, os.get_terminal_size().lines - 1
grid = {(x, y) for x in range(W) for y in range(H) if random.random() < 0.2}

def neighbors(x, y):
    return sum((x+dx, y+dy) in grid for dx in (-1,0,1) for dy in (-1,0,1) if (dx,dy) != (0,0))

def step(g):
    candidates = set()
    for (x, y) in g:
        for dx in (-1,0,1):
            for dy in (-1,0,1):
                candidates.add((x+dx, y+dy))
    new = set()
    for (x, y) in candidates:
        n = sum((x+dx, y+dy) in g for dx in (-1,0,1) for dy in (-1,0,1) if (dx,dy) != (0,0))
        if n == 3 or (n == 2 and (x, y) in g):
            if 0 <= x < W and 0 <= y < H:
                new.add((x, y))
    return new

gen = 0
try:
    while True:
        buf = []
        for y in range(H):
            row = ""
            for x in range(W):
                row += "\u2588" if (x, y) in grid else " "
            buf.append(row)
        sys.stdout.write("\033[H" + "\n".join(buf))
        sys.stdout.write(f"\033[{H+1};1H Gen {gen} | Cells {len(grid)} | Ctrl+C to quit")
        sys.stdout.flush()
        grid = step(grid)
        gen += 1
        time.sleep(0.08)
except KeyboardInterrupt:
    print("\033[2J\033[H")
