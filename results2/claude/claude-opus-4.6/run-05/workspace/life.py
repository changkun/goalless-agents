#!/usr/bin/env python3
"""
Interactive Conway's Game of Life — Terminal Edition

Controls:
  Space     Pause / Resume
  Arrow keys / WASD  Pan the viewport
  +/-       Speed up / slow down
  r         Randomize grid
  c         Clear grid
  d         Toggle draw mode (click cells with mouse)
  1-7       Load preset pattern at cursor
  n         Step one generation (while paused)
  q         Quit

Preset patterns (placed at center):
  1  Glider             5  Lightweight Spaceship
  2  Gosper Glider Gun  6  Pentadecathlon
  3  Pulsar             7  R-pentomino
  4  Beacon
"""

import curses
import random
import time
import sys
from typing import Set, Tuple

Cell = Tuple[int, int]

# ── Preset patterns ──────────────────────────────────────────────────────────
# Each pattern is a list of (row, col) offsets from the placement origin.

PATTERNS: dict[str, list[Cell]] = {}

PATTERNS["Glider"] = [
    (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
]

PATTERNS["Gosper Glider Gun"] = [
    (0, 24),
    (1, 22), (1, 24),
    (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
    (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
    (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
    (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17), (5, 22), (5, 24),
    (6, 10), (6, 16), (6, 24),
    (7, 11), (7, 15),
    (8, 12), (8, 13),
]

PATTERNS["Pulsar"] = []
_pulsar_quarter = [
    (1, 2), (1, 3), (1, 4),
    (2, 1), (2, 6),
    (3, 1), (3, 6),
    (4, 1), (4, 6),
    (6, 1), (6, 6),
    (7, 1), (7, 6),
    (8, 1), (8, 6),
    (9, 2), (9, 3), (9, 4),
]
# Mirror to all four quadrants
for r, c in _pulsar_quarter:
    PATTERNS["Pulsar"].append((r, c))
    PATTERNS["Pulsar"].append((r, -c))
    PATTERNS["Pulsar"].append((-r, c))
    PATTERNS["Pulsar"].append((-r, -c))
# Deduplicate
PATTERNS["Pulsar"] = list(set(PATTERNS["Pulsar"]))

PATTERNS["Beacon"] = [
    (0, 0), (0, 1),
    (1, 0), (1, 1),
    (2, 2), (2, 3),
    (3, 2), (3, 3),
]

PATTERNS["LWSS"] = [
    (0, 1), (0, 4),
    (1, 0),
    (2, 0), (2, 4),
    (3, 0), (3, 1), (3, 2), (3, 3),
]

PATTERNS["Pentadecathlon"] = [
    (0, 0), (1, 0), (2, -1), (2, 1),
    (3, 0), (4, 0), (5, 0), (6, 0),
    (7, -1), (7, 1), (8, 0), (9, 0),
]

PATTERNS["R-pentomino"] = [
    (0, 1), (0, 2),
    (1, 0), (1, 1),
    (2, 1),
]

PATTERN_KEYS = [
    "Glider", "Gosper Glider Gun", "Pulsar", "Beacon",
    "LWSS", "Pentadecathlon", "R-pentomino",
]


# ── Core engine ──────────────────────────────────────────────────────────────

class GameOfLife:
    """Sparse-set implementation of Conway's Game of Life (infinite grid)."""

    def __init__(self) -> None:
        self.alive: Set[Cell] = set()
        self.generation: int = 0

    def clear(self) -> None:
        self.alive.clear()
        self.generation = 0

    def randomize(self, rows: int, cols: int, density: float = 0.3) -> None:
        self.alive.clear()
        self.generation = 0
        for r in range(rows):
            for c in range(cols):
                if random.random() < density:
                    self.alive.add((r, c))

    def place_pattern(self, name: str, origin_r: int, origin_c: int) -> None:
        cells = PATTERNS.get(name)
        if cells is None:
            return
        for dr, dc in cells:
            self.alive.add((origin_r + dr, origin_c + dc))

    def step(self) -> None:
        """Advance one generation using standard B3/S23 rules."""
        neighbor_counts: dict[Cell, int] = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nb = (r + dr, c + dc)
                    neighbor_counts[nb] = neighbor_counts.get(nb, 0) + 1
        new_alive: Set[Cell] = set()
        for cell, cnt in neighbor_counts.items():
            if cnt == 3 or (cnt == 2 and cell in self.alive):
                new_alive.add(cell)
        self.alive = new_alive
        self.generation += 1


# ── Terminal UI ──────────────────────────────────────────────────────────────

SPEED_LEVELS = [1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01]
SPEED_NAMES = ["1 gen/s", "2 gen/s", "5 gen/s", "10 gen/s", "20 gen/s", "50 gen/s", "100 gen/s"]

# Characters for rendering — use half-block for denser look
ALIVE_CHAR = "\u2588"  # █
DEAD_CHAR = " "


def main(stdscr: curses.window) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    curses.start_color()
    curses.use_default_colors()

    # Color pairs
    curses.init_pair(1, curses.COLOR_GREEN, -1)   # alive cells
    curses.init_pair(2, curses.COLOR_CYAN, -1)    # HUD text
    curses.init_pair(3, curses.COLOR_YELLOW, -1)  # status highlight
    curses.init_pair(4, curses.COLOR_RED, -1)     # draw-mode indicator
    curses.init_pair(5, curses.COLOR_WHITE, -1)   # help text

    # Enable mouse for draw mode
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    game = GameOfLife()
    max_y, max_x = stdscr.getmaxyx()
    view_h = max_y - 2  # leave 2 rows for HUD
    view_w = max_x

    # Start with a Gosper Glider Gun in the centre
    game.place_pattern("Gosper Glider Gun", view_h // 2 - 5, view_w // 2 - 18)

    # Viewport offset (top-left corner of the view in world coords)
    cam_r, cam_c = 0, 0

    paused = False
    draw_mode = False
    speed_idx = 3  # default 10 gen/s
    last_step = time.monotonic()

    while True:
        now = time.monotonic()

        # ── Input ────────────────────────────────────────────────────────
        try:
            key = stdscr.getch()
        except Exception:
            key = -1

        if key == ord("q"):
            return
        elif key == ord(" "):
            paused = not paused
        elif key == ord("n") and paused:
            game.step()
        elif key == ord("r"):
            game.randomize(view_h, view_w, 0.3)
            cam_r, cam_c = 0, 0
        elif key == ord("c"):
            game.clear()
        elif key == ord("d"):
            draw_mode = not draw_mode
        elif key in (ord("+"), ord("=")):
            speed_idx = min(speed_idx + 1, len(SPEED_LEVELS) - 1)
        elif key in (ord("-"), ord("_")):
            speed_idx = max(speed_idx - 1, 0)
        # Pan: arrow keys and WASD
        elif key in (curses.KEY_UP, ord("w")):
            cam_r -= 3
        elif key in (curses.KEY_DOWN, ord("s")):
            cam_r += 3
        elif key in (curses.KEY_LEFT, ord("a")):
            cam_c -= 5
        elif key in (curses.KEY_RIGHT, ord("e")):  # 'e' instead of 'd' (d=draw)
            cam_c += 5
        # Preset patterns 1-7 placed at viewport center
        elif ord("1") <= key <= ord("7"):
            idx = key - ord("1")
            if idx < len(PATTERN_KEYS):
                game.place_pattern(
                    PATTERN_KEYS[idx],
                    cam_r + view_h // 2,
                    cam_c + view_w // 2,
                )
        # Mouse: toggle cell in draw mode
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()
                if my < view_h and mx < view_w:
                    cell = (cam_r + my, cam_c + mx)
                    if cell in game.alive:
                        game.alive.discard(cell)
                    else:
                        game.alive.add(cell)
            except Exception:
                pass

        # ── Step simulation ──────────────────────────────────────────────
        interval = SPEED_LEVELS[speed_idx]
        if not paused and (now - last_step) >= interval:
            game.step()
            last_step = now

        # ── Render ───────────────────────────────────────────────────────
        # Recalculate size in case of resize
        try:
            max_y, max_x = stdscr.getmaxyx()
        except Exception:
            pass
        view_h = max(max_y - 2, 1)
        view_w = max(max_x, 1)

        stdscr.erase()

        # Draw alive cells in viewport
        cell_color = curses.color_pair(1) | curses.A_BOLD
        for r, c in game.alive:
            vr = r - cam_r
            vc = c - cam_c
            if 0 <= vr < view_h and 0 <= vc < view_w - 1:
                try:
                    stdscr.addstr(vr, vc, ALIVE_CHAR, cell_color)
                except curses.error:
                    pass

        # ── HUD ──────────────────────────────────────────────────────────
        hud_y = max_y - 2
        if hud_y < 0:
            hud_y = 0

        # Separator line
        try:
            stdscr.addstr(hud_y, 0, "\u2500" * (view_w - 1), curses.color_pair(2))
        except curses.error:
            pass

        # Status bar
        status_parts = []
        state_str = "PAUSED" if paused else "RUNNING"
        state_color = curses.color_pair(3) | curses.A_BOLD
        pop = len(game.alive)
        status_parts.append(f"Gen {game.generation}  Pop {pop}")
        status_parts.append(f"Speed {SPEED_NAMES[speed_idx]}")
        if draw_mode:
            status_parts.append("DRAW")

        status_line = f" {state_str}  |  {'  |  '.join(status_parts)}  |  [q]uit [Space]pause [r]andom [c]lear [d]raw [+/-]speed [1-7]pattern"

        try:
            stdscr.addstr(hud_y + 1, 0, state_str, state_color)
            rest = status_line[len(state_str) + 1:]
            stdscr.addstr(hud_y + 1, len(state_str) + 1, rest[:view_w - len(state_str) - 2], curses.color_pair(5))
        except curses.error:
            pass

        stdscr.refresh()

        # Small sleep to avoid busy loop
        time.sleep(0.005)


if __name__ == "__main__":
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
