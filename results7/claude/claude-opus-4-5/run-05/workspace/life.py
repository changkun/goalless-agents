#!/usr/bin/env python3
"""Conway's Game of Life - Terminal Edition"""

import sys
import time
import random
import signal
import termios
import tty
import select
from dataclasses import dataclass


@dataclass
class Config:
    width: int = 60
    height: int = 25
    delay: float = 0.1
    density: float = 0.3


ALIVE = "\033[92m\u2588\033[0m"  # Green block
DEAD = "\033[90m\u00b7\033[0m"   # Gray dot
CLEAR = "\033[H\033[J"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"


class Grid:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.cells = [[False] * width for _ in range(height)]
        self.generation = 0

    def randomize(self, density: float = 0.3):
        for y in range(self.height):
            for x in range(self.width):
                self.cells[y][x] = random.random() < density
        self.generation = 0

    def count_neighbors(self, x: int, y: int) -> int:
        count = 0
        for dy in (-1, 0, 1):
            for dx in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                if self.cells[ny][nx]:
                    count += 1
        return count

    def step(self):
        new_cells = [[False] * self.width for _ in range(self.height)]
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                alive = self.cells[y][x]
                new_cells[y][x] = neighbors == 3 or (alive and neighbors == 2)
        self.cells = new_cells
        self.generation += 1

    def population(self) -> int:
        return sum(sum(row) for row in self.cells)

    def render(self) -> str:
        lines = []
        for row in self.cells:
            lines.append("".join(ALIVE if cell else DEAD for cell in row))
        return "\n".join(lines)

    def add_glider(self, x: int, y: int):
        pattern = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        for dx, dy in pattern:
            nx, ny = (x + dx) % self.width, (y + dy) % self.height
            self.cells[ny][nx] = True

    def add_blinker(self, x: int, y: int):
        for dx in range(3):
            nx = (x + dx) % self.width
            self.cells[y][nx] = True

    def clear(self):
        self.cells = [[False] * self.width for _ in range(self.height)]
        self.generation = 0


def get_key() -> str | None:
    if select.select([sys.stdin], [], [], 0)[0]:
        return sys.stdin.read(1)
    return None


def main():
    config = Config()
    grid = Grid(config.width, config.height)
    grid.randomize(config.density)

    paused = False
    running = True

    old_settings = termios.tcgetattr(sys.stdin)

    def cleanup(*_):
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        print(SHOW_CURSOR)
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    try:
        tty.setcbreak(sys.stdin.fileno())
        print(HIDE_CURSOR)

        while running:
            status = f"\033[1mGen: {grid.generation:5d} | Pop: {grid.population():4d}\033[0m"
            controls = "[SPACE] pause  [R] reset  [G] glider  [C] clear  [Q] quit"
            state = "\033[93m PAUSED \033[0m" if paused else ""

            output = f"{CLEAR}{grid.render()}\n\n{status} {state}\n{controls}"
            print(output, end="", flush=True)

            key = get_key()
            if key:
                k = key.lower()
                if k == "q":
                    running = False
                elif k == " ":
                    paused = not paused
                elif k == "r":
                    grid.randomize(config.density)
                elif k == "c":
                    grid.clear()
                elif k == "g":
                    grid.add_glider(random.randint(0, config.width - 1),
                                   random.randint(0, config.height - 1))

            if not paused:
                grid.step()

            time.sleep(config.delay)

    finally:
        cleanup()


if __name__ == "__main__":
    main()
