#!/usr/bin/env python3
"""Conway's Game of Life in the terminal."""
import os, time, random, sys

W, H = os.get_terminal_size().columns, os.get_terminal_size().lines - 1
grid = [[random.random() < 0.3 for _ in range(W)] for _ in range(H)]

def step(g):
    new = [[False]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            n = sum(g[(y+dy)%H][(x+dx)%W] for dy in (-1,0,1) for dx in (-1,0,1)) - g[y][x]
            new[y][x] = n == 3 or (g[y][x] and n == 2)
    return new

try:
    while True:
        sys.stdout.write("\033[H" + "\n".join("".join("\u2588" if c else " " for c in row) for row in grid) + "\033[J")
        sys.stdout.flush()
        grid = step(grid)
        time.sleep(0.08)
except KeyboardInterrupt:
    print("\033[J")
