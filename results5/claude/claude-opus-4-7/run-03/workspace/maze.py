#!/usr/bin/env python3
"""Animated terminal maze: recursive-backtracker carving, then A* solving."""

import argparse
import heapq
import random
import shutil
import sys
import time

WALL, OPEN, FRONTIER, PATH, HEAD, GOAL = 0, 1, 2, 3, 4, 5

# 24-bit ANSI colors keyed by cell state.
COLORS = {
    WALL:     (40, 40, 55),
    OPEN:     (200, 200, 210),
    FRONTIER: (255, 180, 60),
    PATH:     (90, 200, 255),
    HEAD:     (255, 90, 120),
    GOAL:     (120, 255, 140),
}

GLYPH = {
    WALL:     "██",
    OPEN:     "  ",
    FRONTIER: "▓▓",
    PATH:     "••",
    HEAD:     "◆◆",
    GOAL:     "★★",
}


def ansi(r, g, b, ch):
    return f"\x1b[38;2;{r};{g};{b}m{ch}\x1b[0m"


def render(grid, frame_delay):
    sys.stdout.write("\x1b[H")
    out = []
    for row in grid:
        for c in row:
            r, g, b = COLORS[c]
            out.append(ansi(r, g, b, GLYPH[c]))
        out.append("\n")
    sys.stdout.write("".join(out))
    sys.stdout.flush()
    if frame_delay:
        time.sleep(frame_delay)


def carve(grid, w, h, frame_delay, animate_every):
    sx, sy = 1, 1
    grid[sy][sx] = OPEN
    stack = [(sx, sy)]
    steps = 0
    while stack:
        x, y = stack[-1]
        neighbors = []
        for dx, dy in ((2, 0), (-2, 0), (0, 2), (0, -2)):
            nx, ny = x + dx, y + dy
            if 0 < nx < w - 1 and 0 < ny < h - 1 and grid[ny][nx] == WALL:
                neighbors.append((nx, ny, dx, dy))
        if not neighbors:
            stack.pop()
            continue
        nx, ny, dx, dy = random.choice(neighbors)
        grid[y + dy // 2][x + dx // 2] = OPEN
        grid[ny][nx] = OPEN
        grid[ny][nx] = FRONTIER
        stack.append((nx, ny))
        steps += 1
        if steps % animate_every == 0:
            render(grid, frame_delay)
        grid[ny][nx] = OPEN
    # Clean stragglers.
    for row in grid:
        for i, c in enumerate(row):
            if c == FRONTIER:
                row[i] = OPEN


def astar(grid, start, goal, w, h, frame_delay, animate_every):
    def heur(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    open_heap = [(heur(start, goal), 0, start, None)]
    came_from = {}
    g_score = {start: 0}
    steps = 0
    while open_heap:
        _, g, cur, parent = heapq.heappop(open_heap)
        if cur in came_from:
            continue
        came_from[cur] = parent
        if cur == goal:
            break
        cx, cy = cur
        if grid[cy][cx] not in (HEAD, GOAL):
            grid[cy][cx] = PATH
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < w and 0 <= ny < h and grid[ny][nx] != WALL:
                ng = g + 1
                if ng < g_score.get((nx, ny), 1 << 30):
                    g_score[(nx, ny)] = ng
                    heapq.heappush(open_heap, (ng + heur((nx, ny), goal), ng, (nx, ny), cur))
        steps += 1
        if steps % animate_every == 0:
            render(grid, frame_delay)
    # Reconstruct.
    path = []
    cur = goal
    while cur is not None and cur in came_from:
        path.append(cur)
        cur = came_from[cur]
    # Wipe explored cells, then draw final path.
    for row in grid:
        for i, c in enumerate(row):
            if c == PATH:
                row[i] = OPEN
    for x, y in reversed(path):
        grid[y][x] = HEAD if (x, y) != goal else GOAL
        render(grid, frame_delay)
        if (x, y) != goal:
            grid[y][x] = PATH


def fit_to_terminal(req_w, req_h):
    cols, rows = shutil.get_terminal_size((80, 24))
    # Each cell prints two chars wide; reserve a row for the cursor.
    max_w = max(11, (cols // 2) - 1)
    max_h = max(7, rows - 2)
    w = min(req_w, max_w)
    h = min(req_h, max_h)
    if w % 2 == 0:
        w -= 1
    if h % 2 == 0:
        h -= 1
    return w, h


def main():
    parser = argparse.ArgumentParser(description="Animated maze generator + A* solver.")
    parser.add_argument("--width", type=int, default=61)
    parser.add_argument("--height", type=int, default=25)
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--carve-delay", type=float, default=0.005)
    parser.add_argument("--solve-delay", type=float, default=0.012)
    parser.add_argument("--carve-every", type=int, default=2,
                        help="Render every N carving steps (lower = smoother, slower).")
    parser.add_argument("--solve-every", type=int, default=1)
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    w, h = fit_to_terminal(args.width, args.height)
    grid = [[WALL] * w for _ in range(h)]

    sys.stdout.write("\x1b[?25l\x1b[2J")  # hide cursor, clear screen
    try:
        render(grid, 0)
        carve(grid, w, h, args.carve_delay, args.carve_every)
        start = (1, 1)
        goal = (w - 2 if (w - 2) % 2 == 1 else w - 3,
                h - 2 if (h - 2) % 2 == 1 else h - 3)
        grid[goal[1]][goal[0]] = GOAL
        render(grid, 0.4)
        astar(grid, start, goal, w, h, args.solve_delay, args.solve_every)
        render(grid, 0)
        sys.stdout.write("\nSolved.\n")
    finally:
        sys.stdout.write("\x1b[?25h")  # show cursor
        sys.stdout.flush()


if __name__ == "__main__":
    main()
