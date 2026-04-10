#!/usr/bin/env python3
"""Conway's Game of Life — Interactive Terminal Edition."""

import os
import sys
import time
import random
import select
import termios
import tty

# ── ANSI helpers ─────────────────────────────────────────────────────────────

ESC = "\033"
HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"
CLEAR = f"{ESC}[2J"
HOME = f"{ESC}[H"
RESET = f"{ESC}[0m"

def move(r, c):
    return f"{ESC}[{r};{c}H"

def fg(code):
    return f"{ESC}[38;5;{code}m"

def bg(code):
    return f"{ESC}[48;5;{code}m"

# Color gradient for cell age (white → green → cyan → blue)
AGE_COLORS = [15, 156, 120, 84, 48, 42, 36, 30, 24, 18]

# ── Grid ─────────────────────────────────────────────────────────────────────

class Grid:
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.cells = [[0] * cols for _ in range(rows)]  # 0=dead, >0=age
        self.generation = 0

    def clear(self):
        self.cells = [[0] * self.cols for _ in range(self.rows)]
        self.generation = 0

    def randomize(self, density=0.3):
        self.clear()
        for r in range(self.rows):
            for c in range(self.cols):
                self.cells[r][c] = 1 if random.random() < density else 0

    def set_pattern(self, pattern, offset_r=None, offset_c=None):
        """Place a pattern (list of (r,c) tuples) centered on the grid."""
        if not pattern:
            return
        pr = [p[0] for p in pattern]
        pc = [p[1] for p in pattern]
        ph = max(pr) - min(pr) + 1
        pw = max(pc) - min(pc) + 1
        if offset_r is None:
            offset_r = (self.rows - ph) // 2 - min(pr)
        if offset_c is None:
            offset_c = (self.cols - pw) // 2 - min(pc)
        for r, c in pattern:
            nr, nc = (r + offset_r) % self.rows, (c + offset_c) % self.cols
            self.cells[nr][nc] = 1

    def count_neighbors(self, r, c):
        n = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                if self.cells[nr][nc] > 0:
                    n += 1
        return n

    def step(self):
        new = [[0] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                n = self.count_neighbors(r, c)
                alive = self.cells[r][c] > 0
                if alive and n in (2, 3):
                    new[r][c] = min(self.cells[r][c] + 1, len(AGE_COLORS))
                elif not alive and n == 3:
                    new[r][c] = 1
        self.cells = new
        self.generation += 1

    def population(self):
        return sum(1 for r in range(self.rows) for c in range(self.cols) if self.cells[r][c] > 0)


# ── Patterns ─────────────────────────────────────────────────────────────────

PATTERNS = {
    "1: Glider": [(0,1),(1,2),(2,0),(2,1),(2,2)],
    "2: Gosper Gun": [
        (0,24),(1,22),(1,24),(2,12),(2,13),(2,20),(2,21),(2,34),(2,35),
        (3,11),(3,15),(3,20),(3,21),(3,34),(3,35),(4,0),(4,1),(4,10),
        (4,16),(4,20),(4,21),(5,0),(5,1),(5,10),(5,14),(5,16),(5,17),
        (5,22),(5,24),(6,10),(6,16),(6,24),(7,11),(7,15),(8,12),(8,13),
    ],
    "3: Pulsar": [],
    "4: R-pentomino": [(0,1),(0,2),(1,0),(1,1),(2,1)],
    "5: Spaceship": [(0,1),(0,4),(1,0),(2,0),(2,4),(3,0),(3,1),(3,2),(3,3)],
}

# Generate pulsar programmatically
def _pulsar():
    pts = []
    for sign_r in (-1, 1):
        for sign_c in (-1, 1):
            for r, c in [(1,2),(1,3),(1,4),(2,6),(3,6),(4,6),(6,2),(6,3),(6,4)]:
                pts.append((6 + sign_r * r, 6 + sign_c * c))
    return pts

PATTERNS["3: Pulsar"] = _pulsar()

# ── Renderer ─────────────────────────────────────────────────────────────────

ALIVE_CHAR = "  "  # Two spaces with background color
DEAD_CHAR = "  "

def render(grid, paused, speed):
    buf = [HOME]
    for r in range(grid.rows):
        row_buf = []
        for c in range(grid.cols):
            age = grid.cells[r][c]
            if age > 0:
                ci = min(age - 1, len(AGE_COLORS) - 1)
                row_buf.append(f"{bg(AGE_COLORS[ci])}{ALIVE_CHAR}{RESET}")
            else:
                row_buf.append(f"{bg(234)}{DEAD_CHAR}{RESET}")
        buf.append("".join(row_buf))
        buf.append("\n")

    status = (
        f" Gen {grid.generation:<6} "
        f"Pop {grid.population():<6} "
        f"Speed {speed:.1f}x "
        f"{'|| PAUSED' if paused else '>> RUNNING'}  "
    )
    controls = " [Space]Pause [R]andom [C]lear [1-5]Pattern [+/-]Speed [Q]uit"
    buf.append(f"\n{fg(226)}{status}{RESET}")
    buf.append(f"\n{fg(245)}{controls}{RESET}")

    sys.stdout.write("".join(buf))
    sys.stdout.flush()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    # Determine grid size from terminal
    try:
        cols, rows = os.get_terminal_size()
    except OSError:
        cols, rows = 80, 24
    grid_cols = cols // 2       # Each cell is 2 chars wide
    grid_rows = rows - 4        # Leave room for status lines
    grid_cols = max(grid_cols, 20)
    grid_rows = max(grid_rows, 10)

    grid = Grid(grid_rows, grid_cols)
    grid.randomize()

    paused = False
    speed = 1.0
    base_delay = 0.1

    # Set terminal to raw mode
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setraw(sys.stdin.fileno())
        sys.stdout.write(HIDE_CURSOR + CLEAR)
        sys.stdout.flush()

        last_step = time.monotonic()

        while True:
            # Non-blocking input
            if select.select([sys.stdin], [], [], 0.02)[0]:
                key = sys.stdin.read(1)
                if key in ("q", "Q", "\x03"):  # q or Ctrl-C
                    break
                elif key == " ":
                    paused = not paused
                elif key in ("r", "R"):
                    grid.randomize()
                elif key in ("c", "C"):
                    grid.clear()
                elif key == "+":
                    speed = min(speed + 0.5, 10.0)
                elif key == "-":
                    speed = max(speed - 0.5, 0.5)
                elif key in "12345":
                    grid.clear()
                    names = sorted(PATTERNS.keys())
                    idx = int(key) - 1
                    if idx < len(names):
                        grid.set_pattern(PATTERNS[names[idx]])

            now = time.monotonic()
            delay = base_delay / speed

            if not paused and (now - last_step) >= delay:
                grid.step()
                last_step = now

            render(grid, paused, speed)

    finally:
        # Restore terminal
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        sys.stdout.write(SHOW_CURSOR + RESET + CLEAR + HOME)
        sys.stdout.flush()
        print("Thanks for playing Life!")


if __name__ == "__main__":
    main()
