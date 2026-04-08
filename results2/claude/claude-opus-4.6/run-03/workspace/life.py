#!/usr/bin/env python3
"""
Conway's Game of Life — Interactive Terminal Simulator

Controls:
  Arrow keys / hjkl  Move cursor / pan viewport
  t / Enter(on cell)  Toggle cell under cursor
  Space               Step one generation
  Enter               Run / Pause
  + / -               Speed up / slow down
  r                   Random fill
  c                   Clear grid
  p                   Pattern menu
  ?                   Toggle help
  q                   Quit
  Mouse click         Toggle cell
"""

import argparse
import curses
import random
import time

# ── Patterns ────────────────────────────────────────────────────────────────

PATTERNS = {
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "LWSS": [(0, 1), (0, 4), (1, 0), (2, 0), (2, 4), (3, 0), (3, 1), (3, 2), (3, 3)],
    "Block": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "Beehive": [(0, 1), (0, 2), (1, 0), (1, 3), (2, 1), (2, 2)],
    "Loaf": [(0, 1), (0, 2), (1, 0), (1, 3), (2, 1), (2, 3), (3, 2)],
    "Blinker": [(0, 0), (0, 1), (0, 2)],
    "Toad": [(0, 1), (0, 2), (0, 3), (1, 0), (1, 1), (1, 2)],
    "Pulsar": [
        (r, c)
        for r, c in (
            # top-left quadrant reflected to all four
            *[(r, c) for r in (-1, -2, -3) for c in (2, 3, 4)],
            *[(r, c) for r in (-1, -2, -3) for c in (-2, -3, -4)],
            *[(r, c) for r in (1, 2, 3) for c in (2, 3, 4)],
            *[(r, c) for r in (1, 2, 3) for c in (-2, -3, -4)],
            *[(-4, c) for c in (-1, 1)],
            *[(4, c) for c in (-1, 1)],
            *[(-4, c) for c in (-1, 1)],
            *[(0, c) for c in (2, 3, 4, -2, -3, -4)],
        )
    ],
    "Pentadecathlon": [(0, c) for c in range(10)]
    + [(-1, 1), (1, 1), (-1, 6), (1, 6)],  # approximate
    "R-pentomino": [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)],
    "Diehard": [(0, 6), (1, 0), (1, 1), (2, 1), (2, 5), (2, 6), (2, 7)],
    "Acorn": [(0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)],
    "Gosper Glider Gun": [
        (0, 24),
        (1, 22), (1, 24),
        (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
        (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
        (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
        (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17), (5, 22), (5, 24),
        (6, 10), (6, 16), (6, 24),
        (7, 11), (7, 15),
        (8, 12), (8, 13),
    ],
}

# Normalize pulsar so that it has proper symmetry
_pulsar = set()
for dr in (-6, -1, 1, 6):
    for dc in (-4, -3, -2, 2, 3, 4):
        pass  # handled inline above
# Actually let's just use a well-known definition:
PATTERNS["Pulsar"] = []
_p = set()
for r, c in [
    (2, 4), (2, 5), (2, 6), (2, 10), (2, 11), (2, 12),
    (4, 2), (4, 7), (4, 9), (4, 14),
    (5, 2), (5, 7), (5, 9), (5, 14),
    (6, 2), (6, 7), (6, 9), (6, 14),
    (7, 4), (7, 5), (7, 6), (7, 10), (7, 11), (7, 12),
    (9, 4), (9, 5), (9, 6), (9, 10), (9, 11), (9, 12),
    (10, 2), (10, 7), (10, 9), (10, 14),
    (11, 2), (11, 7), (11, 9), (11, 14),
    (12, 2), (12, 7), (12, 9), (12, 14),
    (14, 4), (14, 5), (14, 6), (14, 10), (14, 11), (14, 12),
]:
    _p.add((r, c))
PATTERNS["Pulsar"] = sorted(_p)

# Fix pentadecathlon with the correct period-15 oscillator
PATTERNS["Pentadecathlon"] = [
    (0, 1), (1, 1), (2, 0), (2, 2), (3, 1), (4, 1),
    (5, 1), (6, 1), (7, 0), (7, 2), (8, 1), (9, 1),
]

PATTERN_NAMES = list(PATTERNS.keys())


# ── Grid ────────────────────────────────────────────────────────────────────

class Grid:
    """Toroidal Game of Life grid using a set of alive cells."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.alive: set[tuple[int, int]] = set()
        self.generation = 0

    def _wrap(self, r: int, c: int) -> tuple[int, int]:
        return r % self.height, c % self.width

    def toggle(self, r: int, c: int):
        cell = self._wrap(r, c)
        if cell in self.alive:
            self.alive.discard(cell)
        else:
            self.alive.add(cell)

    def set_alive(self, r: int, c: int):
        self.alive.add(self._wrap(r, c))

    def tick(self):
        """Advance one generation."""
        neighbor_count: dict[tuple[int, int], int] = {}
        for r, c in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nb = self._wrap(r + dr, c + dc)
                    neighbor_count[nb] = neighbor_count.get(nb, 0) + 1
        new_alive: set[tuple[int, int]] = set()
        for cell, cnt in neighbor_count.items():
            if cnt == 3 or (cnt == 2 and cell in self.alive):
                new_alive.add(cell)
        self.alive = new_alive
        self.generation += 1

    def stamp(self, pattern_name: str, origin_r: int, origin_c: int):
        """Place a named pattern at the given origin."""
        for dr, dc in PATTERNS[pattern_name]:
            self.set_alive(origin_r + dr, origin_c + dc)

    def randomize(self, density: float = 0.2):
        self.alive.clear()
        self.generation = 0
        for r in range(self.height):
            for c in range(self.width):
                if random.random() < density:
                    self.alive.add((r, c))

    def clear(self):
        self.alive.clear()
        self.generation = 0

    def population(self) -> int:
        return len(self.alive)


# ── TUI ─────────────────────────────────────────────────────────────────────

ALIVE_CH = "\u2588"  # full block
DEAD_CH = " "

SPEEDS = [2.0, 1.0, 0.5, 0.25, 0.1, 0.05, 0.02]
SPEED_LABELS = ["0.5x", "1x", "2x", "4x", "10x", "20x", "50x"]


class App:
    def __init__(self, stdscr, width: int, height: int):
        self.stdscr = stdscr
        self.grid = Grid(width, height)
        self.running = False
        self.speed_idx = 2  # default 2x
        self.cursor_r = height // 2
        self.cursor_c = width // 2
        self.view_r = 0  # top-left of viewport in grid coords
        self.view_c = 0
        self.show_help = False
        self.show_patterns = False
        self.pattern_idx = 0
        self.last_tick = 0.0

        curses.curs_set(0)
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(1, curses.COLOR_GREEN, -1)   # alive
        curses.init_pair(2, curses.COLOR_YELLOW, -1)   # cursor
        curses.init_pair(3, curses.COLOR_CYAN, -1)     # UI
        curses.init_pair(4, curses.COLOR_BLACK, curses.COLOR_WHITE)  # status bar
        curses.init_pair(5, curses.COLOR_WHITE, curses.COLOR_BLUE)   # menu
        curses.init_pair(6, curses.COLOR_YELLOW, curses.COLOR_BLUE)  # menu highlight
        self.stdscr.nodelay(True)
        curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)

    @property
    def view_h(self) -> int:
        return max(1, curses.LINES - 2)  # leave room for status bar

    @property
    def view_w(self) -> int:
        return max(1, curses.COLS)

    def _center_view(self):
        self.view_r = self.cursor_r - self.view_h // 2
        self.view_c = self.cursor_c - self.view_w // 2

    def draw(self):
        self.stdscr.erase()
        vh, vw = self.view_h, self.view_w
        alive = self.grid.alive

        # Draw cells
        for sr in range(vh):
            gr = (self.view_r + sr) % self.grid.height
            for sc in range(vw):
                gc = (self.view_c + sc) % self.grid.width
                is_cursor = (gr == self.cursor_r and gc == self.cursor_c)
                is_alive = (gr, gc) in alive
                if is_cursor:
                    ch = ALIVE_CH if is_alive else "\u2591"
                    try:
                        self.stdscr.addstr(sr, sc, ch, curses.color_pair(2) | curses.A_BOLD)
                    except curses.error:
                        pass
                elif is_alive:
                    try:
                        self.stdscr.addstr(sr, sc, ALIVE_CH, curses.color_pair(1))
                    except curses.error:
                        pass

        # Status bar
        status_row = curses.LINES - 1
        state = "RUNNING" if self.running else "PAUSED"
        speed = SPEED_LABELS[self.speed_idx]
        status = (
            f" Gen: {self.grid.generation}  "
            f"Pop: {self.grid.population()}  "
            f"[{state}]  "
            f"Speed: {speed}  "
            f"Cursor: ({self.cursor_r},{self.cursor_c})  "
            f"Grid: {self.grid.width}x{self.grid.height}  "
            f"? help"
        )
        status = status.ljust(curses.COLS)[:curses.COLS]
        try:
            self.stdscr.addstr(status_row, 0, status[:curses.COLS - 1], curses.color_pair(4))
        except curses.error:
            pass

        # Help overlay
        if self.show_help:
            self._draw_help()

        # Pattern selector overlay
        if self.show_patterns:
            self._draw_pattern_menu()

        self.stdscr.refresh()

    def _draw_help(self):
        lines = [
            "=== Controls ===",
            "",
            "Arrows/hjkl  Move cursor",
            "t            Toggle cell",
            "Space        Step one generation",
            "Enter        Run / Pause",
            "+/-          Speed up / down",
            "r            Random fill",
            "c            Clear",
            "p            Pattern menu",
            "?            Toggle this help",
            "q            Quit",
            "Mouse click  Toggle cell",
            "",
            "Press any key to close",
        ]
        self._draw_overlay(lines)

    def _draw_pattern_menu(self):
        lines = ["=== Patterns (Enter to place, Esc to cancel) ===", ""]
        for i, name in enumerate(PATTERN_NAMES):
            marker = " > " if i == self.pattern_idx else "   "
            lines.append(f"{marker}{name}")
        lines.append("")
        lines.append("Up/Down to select, Enter to stamp at cursor")
        self._draw_overlay(lines)

    def _draw_overlay(self, lines: list[str]):
        max_w = max(len(l) for l in lines) + 4
        box_h = len(lines) + 2
        start_r = max(0, (curses.LINES - box_h) // 2)
        start_c = max(0, (curses.COLS - max_w) // 2)
        for i in range(box_h):
            r = start_r + i
            if r >= curses.LINES - 1:
                break
            if i == 0 or i == box_h - 1:
                text = ("+" + "-" * (max_w - 2) + "+")[:curses.COLS - start_c]
            else:
                content = lines[i - 1] if (i - 1) < len(lines) else ""
                text = ("| " + content.ljust(max_w - 4) + " |")[:curses.COLS - start_c]
            pair = curses.color_pair(6) if (self.show_patterns and 2 <= i < box_h - 1 and i - 2 == self.pattern_idx) else curses.color_pair(5)
            try:
                self.stdscr.addstr(r, start_c, text, pair)
            except curses.error:
                pass

    def handle_input(self):
        try:
            key = self.stdscr.getch()
        except curses.error:
            return True
        if key == -1:
            return True

        # Help overlay intercepts all keys
        if self.show_help:
            self.show_help = False
            return True

        # Pattern menu mode
        if self.show_patterns:
            return self._handle_pattern_input(key)

        if key == ord("q"):
            return False
        elif key == ord("?"):
            self.show_help = True
        elif key == ord("p"):
            self.show_patterns = True
            self.pattern_idx = 0
        elif key == ord(" "):
            self.grid.tick()
        elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            self.running = not self.running
        elif key in (ord("+"), ord("=")):
            self.speed_idx = min(self.speed_idx + 1, len(SPEEDS) - 1)
        elif key in (ord("-"), ord("_")):
            self.speed_idx = max(self.speed_idx - 1, 0)
        elif key == ord("r"):
            self.grid.randomize()
        elif key == ord("c"):
            self.grid.clear()
        elif key == ord("t"):
            self.grid.toggle(self.cursor_r, self.cursor_c)
        elif key in (curses.KEY_UP, ord("k")):
            self.cursor_r = (self.cursor_r - 1) % self.grid.height
            self._adjust_viewport()
        elif key in (curses.KEY_DOWN, ord("j")):
            self.cursor_r = (self.cursor_r + 1) % self.grid.height
            self._adjust_viewport()
        elif key in (curses.KEY_LEFT, ord("h")):
            self.cursor_c = (self.cursor_c - 1) % self.grid.width
            self._adjust_viewport()
        elif key in (curses.KEY_RIGHT, ord("l")):
            self.cursor_c = (self.cursor_c + 1) % self.grid.width
            self._adjust_viewport()
        elif key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, _ = curses.getmouse()
                if my < self.view_h:
                    gr = (self.view_r + my) % self.grid.height
                    gc = (self.view_c + mx) % self.grid.width
                    self.grid.toggle(gr, gc)
                    self.cursor_r = gr
                    self.cursor_c = gc
            except curses.error:
                pass
        return True

    def _handle_pattern_input(self, key: int) -> bool:
        if key in (curses.KEY_UP, ord("k")):
            self.pattern_idx = (self.pattern_idx - 1) % len(PATTERN_NAMES)
        elif key in (curses.KEY_DOWN, ord("j")):
            self.pattern_idx = (self.pattern_idx + 1) % len(PATTERN_NAMES)
        elif key in (ord("\n"), ord("\r"), curses.KEY_ENTER):
            name = PATTERN_NAMES[self.pattern_idx]
            self.grid.stamp(name, self.cursor_r, self.cursor_c)
            self.show_patterns = False
        elif key == 27:  # Escape
            self.show_patterns = False
        elif key == ord("q"):
            return False
        return True

    def _adjust_viewport(self):
        margin = 3
        vh, vw = self.view_h, self.view_w
        # Vertical
        screen_r = (self.cursor_r - self.view_r) % self.grid.height
        if screen_r < margin:
            self.view_r = (self.cursor_r - margin) % self.grid.height
        elif screen_r >= vh - margin:
            self.view_r = (self.cursor_r - vh + margin + 1) % self.grid.height
        # Horizontal
        screen_c = (self.cursor_c - self.view_c) % self.grid.width
        if screen_c < margin:
            self.view_c = (self.cursor_c - margin) % self.grid.width
        elif screen_c >= vw - margin:
            self.view_c = (self.cursor_c - vw + margin + 1) % self.grid.width

    def run(self):
        self._center_view()
        while True:
            if not self.handle_input():
                break

            now = time.monotonic()
            if self.running and (now - self.last_tick) >= SPEEDS[self.speed_idx]:
                self.grid.tick()
                self.last_tick = now

            self.draw()
            time.sleep(0.016)  # ~60 fps cap


def main():
    parser = argparse.ArgumentParser(description="Conway's Game of Life — Terminal Edition")
    parser.add_argument("--width", "-W", type=int, default=200, help="Grid width (default: 200)")
    parser.add_argument("--height", "-H", type=int, default=100, help="Grid height (default: 100)")
    args = parser.parse_args()

    def _run(stdscr):
        app = App(stdscr, args.width, args.height)
        app.run()

    curses.wrapper(_run)


if __name__ == "__main__":
    main()
