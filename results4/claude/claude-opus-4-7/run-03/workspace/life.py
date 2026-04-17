#!/usr/bin/env python3
"""
life.py — Conway's Game of Life in the terminal.

A polished, colorful implementation featuring:
  * A library of famous patterns (glider, pulsar, Gosper glider gun, ...)
  * ANSI 256-color rendering where cells age from hot to cool
  * Live HUD with generation, population, births/deaths
  * Stagnation & period detection (auto-stops when the pattern stalls or loops)
  * Torus topology (edges wrap) — unless --no-wrap is passed

Usage:
    python3 life.py                      # random soup, auto-sized to terminal
    python3 life.py --pattern gosper     # Gosper glider gun
    python3 life.py --list               # show available patterns
    python3 life.py --pattern pulsar --fps 8 --generations 200
"""

from __future__ import annotations

import argparse
import os
import random
import shutil
import signal
import sys
import time
from collections import deque
from typing import Iterable


# ---------------------------------------------------------------------------
# Pattern library.
#
# Each pattern is a list of (row, col) offsets of live cells, anchored so
# the shape is easy to read here. Centering is handled at placement time.
# ---------------------------------------------------------------------------

def _cells_from_art(art: str) -> list[tuple[int, int]]:
    """Parse a block of text where '#' / 'O' / '*' mean alive."""
    cells: list[tuple[int, int]] = []
    for r, line in enumerate(art.strip("\n").splitlines()):
        for c, ch in enumerate(line):
            if ch in "#O*":
                cells.append((r, c))
    return cells


PATTERNS: dict[str, list[tuple[int, int]]] = {
    "glider": _cells_from_art(
        """
        .#.
        ..#
        ###
        """.replace(" ", "")
    ),
    "blinker": _cells_from_art("###"),
    "toad": _cells_from_art(
        """
        .###
        ###.
        """.replace(" ", "")
    ),
    "beacon": _cells_from_art(
        """
        ##..
        ##..
        ..##
        ..##
        """.replace(" ", "")
    ),
    "pulsar": _cells_from_art(
        """
        ..###...###..
        .............
        #....#.#....#
        #....#.#....#
        #....#.#....#
        ..###...###..
        .............
        ..###...###..
        #....#.#....#
        #....#.#....#
        #....#.#....#
        .............
        ..###...###..
        """.replace(" ", "")
    ),
    "lwss": _cells_from_art(  # lightweight spaceship
        """
        .####
        #...#
        ....#
        #..#.
        """.replace(" ", "")
    ),
    "pentadecathlon": _cells_from_art(
        """
        ..#....#..
        ##.####.##
        ..#....#..
        """.replace(" ", "")
    ),
    # The classic Gosper glider gun — emits gliders forever.
    "gosper": _cells_from_art(
        """
        ........................#...........
        ......................#.#...........
        ............##......##............##
        ...........#...#....##............##
        ##........#.....#...##..............
        ##........#...#.##....#.#...........
        ..........#.....#.......#...........
        ...........#...#....................
        ............##......................
        """.replace(" ", "")
    ),
    "acorn": _cells_from_art(
        """
        .#.....
        ...#...
        ##..###
        """.replace(" ", "")
    ),
    "rpentomino": _cells_from_art(
        """
        .##
        ##.
        .#.
        """.replace(" ", "")
    ),
    "diehard": _cells_from_art(
        """
        ......#.
        ##......
        .#...###
        """.replace(" ", "")
    ),
}


# ---------------------------------------------------------------------------
# Engine.
# ---------------------------------------------------------------------------

class Life:
    """A sparse-set Game of Life grid. Torus if `wrap`, else bounded."""

    def __init__(self, rows: int, cols: int, wrap: bool = True) -> None:
        self.rows = rows
        self.cols = cols
        self.wrap = wrap
        self.alive: set[tuple[int, int]] = set()
        self.age: dict[tuple[int, int], int] = {}
        self.generation = 0
        self.births = 0
        self.deaths = 0

    def seed(self, cells: Iterable[tuple[int, int]]) -> None:
        for rc in cells:
            if 0 <= rc[0] < self.rows and 0 <= rc[1] < self.cols:
                self.alive.add(rc)
                self.age[rc] = 0

    def seed_random(self, density: float = 0.25, rng: random.Random | None = None) -> None:
        rng = rng or random.Random()
        for r in range(self.rows):
            for c in range(self.cols):
                if rng.random() < density:
                    self.alive.add((r, c))
                    self.age[(r, c)] = 0

    def place_pattern(self, name: str, anchor: tuple[int, int] | None = None) -> None:
        if name not in PATTERNS:
            raise KeyError(f"Unknown pattern: {name!r}")
        cells = PATTERNS[name]
        max_r = max(r for r, _ in cells)
        max_c = max(c for _, c in cells)
        if anchor is None:
            # Center the pattern.
            r0 = (self.rows - max_r) // 2
            c0 = (self.cols - max_c) // 2
        else:
            r0, c0 = anchor
        self.seed((r0 + r, c0 + c) for r, c in cells)

    def step(self) -> None:
        """Advance one generation."""
        # Count neighbors of every cell that is alive or adjacent to alive.
        counts: dict[tuple[int, int], int] = {}
        R, C = self.rows, self.cols
        wrap = self.wrap
        for (r, c) in self.alive:
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = r + dr, c + dc
                    if wrap:
                        nr %= R
                        nc %= C
                    elif nr < 0 or nr >= R or nc < 0 or nc >= C:
                        continue
                    counts[(nr, nc)] = counts.get((nr, nc), 0) + 1

        new_alive: set[tuple[int, int]] = set()
        births = 0
        for pos, n in counts.items():
            if pos in self.alive:
                if n == 2 or n == 3:
                    new_alive.add(pos)
            elif n == 3:
                new_alive.add(pos)
                births += 1

        # Survivors also include alive cells with no entry in counts only if
        # they had 2 or 3 neighbors — but those are already captured above.
        deaths = len(self.alive) - (len(new_alive) - births)

        # Update ages: living cells that survived age one tick, new cells
        # start at age 0, dead cells are forgotten.
        new_age: dict[tuple[int, int], int] = {}
        for pos in new_alive:
            if pos in self.alive:
                new_age[pos] = self.age.get(pos, 0) + 1
            else:
                new_age[pos] = 0

        self.alive = new_alive
        self.age = new_age
        self.generation += 1
        self.births = births
        self.deaths = deaths


# ---------------------------------------------------------------------------
# Rendering.
# ---------------------------------------------------------------------------

# A hot-to-cool color ramp (xterm-256). Index = cell age clamped to len-1.
# Yellow -> orange -> red -> magenta -> purple -> blue -> cyan -> teal.
COLOR_RAMP = [226, 220, 214, 208, 202, 196, 161, 127, 93, 57, 27, 33, 39, 45, 51, 87]

CSI = "\x1b["
HIDE_CURSOR = CSI + "?25l"
SHOW_CURSOR = CSI + "?25h"
CLEAR = CSI + "2J"
HOME = CSI + "H"
RESET = CSI + "0m"


def color_for_age(age: int) -> str:
    idx = min(age, len(COLOR_RAMP) - 1)
    return f"{CSI}38;5;{COLOR_RAMP[idx]}m"


def render(life: Life, info: str, use_color: bool) -> str:
    """Build a full-screen frame as a single string."""
    # Pre-build grid of characters. We render 2 vertical cells per row using
    # the half-block trick so each terminal row holds 2 Life rows — doubling
    # vertical resolution.
    rows, cols = life.rows, life.cols
    out: list[str] = [HOME]
    # Top border / HUD
    out.append(info + CSI + "K\n")  # clear to end of line
    for r in range(0, rows, 2):
        line: list[str] = []
        last_color = None
        for c in range(cols):
            top = (r, c) in life.alive
            bot = (r + 1, c) in life.alive if r + 1 < rows else False
            if not top and not bot:
                if last_color is not None:
                    line.append(RESET)
                    last_color = None
                line.append(" ")
                continue
            if use_color:
                # Choose the hotter (younger) of the two cells for fg color.
                ages = []
                if top:
                    ages.append(life.age.get((r, c), 0))
                if bot:
                    ages.append(life.age.get((r + 1, c), 0))
                age = min(ages)
                col = color_for_age(age)
                if col != last_color:
                    line.append(col)
                    last_color = col
            if top and bot:
                line.append("\u2588")  # full block
            elif top:
                line.append("\u2580")  # upper half
            else:
                line.append("\u2584")  # lower half
        if last_color is not None:
            line.append(RESET)
        line.append(CSI + "K")  # clear to end of line
        out.append("".join(line) + "\n")
    out.append(CSI + "J")  # clear from cursor down
    return "".join(out)


# ---------------------------------------------------------------------------
# Driver.
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Conway's Game of Life in the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Patterns: " + ", ".join(sorted(PATTERNS)),
    )
    p.add_argument("--pattern", "-p", help="Seed with a named pattern (see --list).")
    p.add_argument("--list", action="store_true", help="List available patterns and exit.")
    p.add_argument("--rows", type=int, default=0, help="Grid rows (default: fill terminal).")
    p.add_argument("--cols", type=int, default=0, help="Grid cols (default: fill terminal).")
    p.add_argument("--density", type=float, default=0.28,
                   help="Random soup density (0..1) when no pattern given.")
    p.add_argument("--fps", type=float, default=15.0, help="Frames per second.")
    p.add_argument("--generations", "-g", type=int, default=0,
                   help="Stop after this many generations (0 = unlimited).")
    p.add_argument("--seed", type=int, default=None, help="RNG seed for reproducibility.")
    p.add_argument("--no-wrap", action="store_true", help="Bounded grid instead of torus.")
    p.add_argument("--no-color", action="store_true", help="Disable ANSI colors.")
    p.add_argument("--no-hud", action="store_true", help="Hide the HUD header line.")
    return p


def auto_size(requested_rows: int, requested_cols: int) -> tuple[int, int]:
    ts = shutil.get_terminal_size(fallback=(80, 24))
    cols = requested_cols if requested_cols > 0 else ts.columns
    # Reserve 2 terminal rows: one for HUD, one for trailing cursor.
    # Each terminal row renders 2 Life rows via half-block glyphs.
    term_rows_available = max(ts.lines - 2, 3)
    rows = requested_rows if requested_rows > 0 else term_rows_available * 2
    # Clamp.
    rows = max(rows, 4)
    cols = max(cols, 4)
    return rows, cols


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.list:
        print("Available patterns:")
        for name in sorted(PATTERNS):
            print(f"  - {name}")
        return 0

    rows, cols = auto_size(args.rows, args.cols)
    life = Life(rows=rows, cols=cols, wrap=not args.no_wrap)

    rng = random.Random(args.seed)
    if args.pattern:
        if args.pattern not in PATTERNS:
            print(f"Unknown pattern: {args.pattern}. Try --list.", file=sys.stderr)
            return 2
        life.place_pattern(args.pattern)
    else:
        life.seed_random(density=args.density, rng=rng)

    use_color = (not args.no_color) and sys.stdout.isatty() and os.environ.get("TERM") != "dumb"
    frame_time = 1.0 / max(args.fps, 0.5)

    # Trap SIGINT cleanly.
    stop = {"flag": False}

    def _on_sigint(signum, frame):  # noqa: ARG001
        stop["flag"] = True

    signal.signal(signal.SIGINT, _on_sigint)

    # History of (population, hash) for stagnation / period detection.
    history: deque[tuple[int, int]] = deque(maxlen=64)
    stall_reason: str | None = None

    sys.stdout.write(HIDE_CURSOR + CLEAR + HOME)
    try:
        start = time.time()
        while True:
            pop = len(life.alive)
            sig = (pop, hash(frozenset(life.alive)))

            # Period / stagnation check before stepping.
            if sig in history:
                # Find period.
                for i, prior in enumerate(reversed(history), start=1):
                    if prior == sig:
                        if i == 1:
                            stall_reason = "still life"
                        else:
                            stall_reason = f"oscillator (period {i})"
                        break
            history.append(sig)

            elapsed = time.time() - start
            hud = (
                f" Life \u2022 gen {life.generation:>5}  pop {pop:>5}  "
                f"+{life.births:<3} -{life.deaths:<3}  "
                f"{life.rows}x{life.cols}  "
                f"{'torus' if life.wrap else 'bounded'}  "
                f"{elapsed:5.1f}s  "
                f"[Ctrl-C to quit]"
            )
            if args.no_hud:
                hud = ""

            sys.stdout.write(render(life, hud, use_color))
            sys.stdout.flush()

            if stop["flag"] or stall_reason:
                break
            if args.generations and life.generation >= args.generations:
                stall_reason = "generation limit reached"
                break
            if pop == 0:
                stall_reason = "extinction"
                break

            time.sleep(frame_time)
            life.step()
    finally:
        sys.stdout.write(RESET + SHOW_CURSOR + "\n")
        sys.stdout.flush()

    if stall_reason:
        print(f"Stopped: {stall_reason} at generation {life.generation}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
