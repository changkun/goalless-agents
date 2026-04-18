"""Conway's Game of Life in the terminal."""
import os, time, random

ROWS, COLS = 24, 60

def make_grid():
    return [[random.random() < 0.3 for _ in range(COLS)] for _ in range(ROWS)]

def neighbors(grid, r, c):
    return sum(
        grid[(r + dr) % ROWS][(c + dc) % COLS]
        for dr in (-1, 0, 1) for dc in (-1, 0, 1)
        if (dr, dc) != (0, 0)
    )

def step(grid):
    return [
        [n == 3 or (grid[r][c] and n == 2)
         for c, n in ((c, neighbors(grid, r, c)) for c in range(COLS))]
        for r in range(ROWS)
    ]

def render(grid, gen):
    os.system("clear")
    print(f"  Generation {gen}  (Ctrl+C to quit)\n")
    for row in grid:
        print("  " + "".join("\u2588\u2588" if cell else "  " for cell in row))

grid = make_grid()
gen = 0
try:
    while True:
        render(grid, gen)
        grid = step(grid)
        gen += 1
        time.sleep(0.15)
except KeyboardInterrupt:
    print("\n  Goodbye!")
