import os, time, random

W, H = 60, 30
grid = [[random.random() < 0.3 for _ in range(W)] for _ in range(H)]

def step(g):
    new = [[False]*W for _ in range(H)]
    for y in range(H):
        for x in range(W):
            n = sum(g[(y+dy)%H][(x+dx)%W] for dy in (-1,0,1) for dx in (-1,0,1)) - g[y][x]
            new[y][x] = n == 3 or (g[y][x] and n == 2)
    return new

try:
    for gen in range(200):
        os.system("clear")
        print(f"  Conway's Game of Life  |  Generation {gen}")
        print("+" + "-"*W + "+")
        for row in grid:
            print("|" + "".join("\u2588" if c else " " for c in row) + "|")
        print("+" + "-"*W + "+")
        grid = step(grid)
        time.sleep(0.12)
except KeyboardInterrupt:
    pass
