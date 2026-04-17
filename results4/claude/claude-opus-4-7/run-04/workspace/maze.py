#!/usr/bin/env python3
"""
maze.py — animated terminal maze generator & solver.

Generation algorithms:
  - dfs     : recursive backtracker (classic twisty maze)
  - prim    : randomised Prim's (lots of short dead ends)
  - wilson  : Wilson's loop-erased random walk (uniform spanning tree)

Solvers:
  - bfs     : breadth-first search, shortest path; animates wavefront
  - astar   : A* with Manhattan heuristic; animates frontier

Run `python3 maze.py --help` for flags.
"""
from __future__ import annotations

import argparse
import heapq
import os
import random
import sys
import time
from collections import deque
from dataclasses import dataclass, field
from typing import Callable, Iterable

# ---------- cell / grid model -----------------------------------------------

# Walls are bitflags on a cell. A cell knows which of its four sides are
# currently blocked. Two neighbouring cells share a wall; we keep them in sync.
N, E, S, W = 1, 2, 4, 8
DX = {N: 0, S: 0, E: 1, W: -1}
DY = {N: -1, S: 1, E: 0, W: 0}
OPP = {N: S, S: N, E: W, W: E}
DIRS = (N, E, S, W)


@dataclass
class Grid:
    width: int
    height: int
    walls: list[int] = field(init=False)

    def __post_init__(self) -> None:
        # Every cell starts fully walled off.
        self.walls = [N | E | S | W] * (self.width * self.height)

    def idx(self, x: int, y: int) -> int:
        return y * self.width + x

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def neighbours(self, x: int, y: int) -> Iterable[tuple[int, int, int]]:
        for d in DIRS:
            nx, ny = x + DX[d], y + DY[d]
            if self.in_bounds(nx, ny):
                yield nx, ny, d

    def has_wall(self, x: int, y: int, d: int) -> bool:
        return bool(self.walls[self.idx(x, y)] & d)

    def carve(self, x: int, y: int, d: int) -> None:
        """Remove the wall between (x,y) and its neighbour in direction d."""
        nx, ny = x + DX[d], y + DY[d]
        if not self.in_bounds(nx, ny):
            return
        self.walls[self.idx(x, y)] &= ~d
        self.walls[self.idx(nx, ny)] &= ~OPP[d]

    def passable(self, x: int, y: int, d: int) -> bool:
        return not self.has_wall(x, y, d)


# ---------- renderer --------------------------------------------------------

# Each logical cell is drawn as a 2x1 block with a trailing right wall
# and a bottom wall on its own line. That gives a rectangular look that
# fills a typical terminal better than the square-per-cell variant.
#
# Layout for cell (x, y):
#   top-left corner | top edge | top-right corner
#   left edge       | body     | right edge
#   (bottom handled by the next row)

# Unicode box-drawing: ┌ ┐ └ ┘ ─ │ etc. We pick the right corner glyph
# depending on which of the four surrounding walls are present.
CORNERS = {
    # (N, E, S, W) wall mask around a corner -> glyph
    (0, 0, 0, 0): " ",
    (1, 0, 0, 0): "╵",
    (0, 1, 0, 0): "╶",
    (0, 0, 1, 0): "╷",
    (0, 0, 0, 1): "╴",
    (1, 1, 0, 0): "└",
    (0, 1, 1, 0): "┌",
    (0, 0, 1, 1): "┐",
    (1, 0, 0, 1): "┘",
    (1, 0, 1, 0): "│",
    (0, 1, 0, 1): "─",
    (1, 1, 1, 0): "├",
    (0, 1, 1, 1): "┬",
    (1, 0, 1, 1): "┤",
    (1, 1, 0, 1): "┴",
    (1, 1, 1, 1): "┼",
}

RESET = "\033[0m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR = "\033[2J\033[H"
HOME = "\033[H"


def rgb(r: int, g: int, b: int) -> str:
    return f"\033[38;2;{r};{g};{b}m"


def rgb_bg(r: int, g: int, b: int) -> str:
    return f"\033[48;2;{r};{g};{b}m"


@dataclass
class Palette:
    wall: str = rgb(120, 120, 130)
    empty: str = ""
    frontier: str = rgb_bg(80, 60, 20)  # warm amber for BFS/A* wavefront
    visited: str = rgb_bg(30, 30, 60)  # cool indigo trail
    path: str = rgb_bg(40, 160, 90)  # green final path
    cursor: str = rgb_bg(200, 50, 100)  # generator head
    start: str = rgb_bg(50, 120, 200)
    end: str = rgb_bg(200, 120, 50)


class Renderer:
    """Renders a Grid plus cell-state overlays to the terminal."""

    # state codes for the overlay
    EMPTY = 0
    CURSOR = 1
    FRONTIER = 2
    VISITED = 3
    PATH = 4
    START = 5
    END = 6

    def __init__(self, grid: Grid, palette: Palette, color: bool = True):
        self.grid = grid
        self.palette = palette
        self.color = color
        self.state = [self.EMPTY] * (grid.width * grid.height)

    # --- overlay helpers -----------------------------------------------------

    def set_state(self, x: int, y: int, s: int) -> None:
        self.state[self.grid.idx(x, y)] = s

    def clear_state(self, keep: tuple[int, ...] = ()) -> None:
        for i, s in enumerate(self.state):
            if s not in keep:
                self.state[i] = self.EMPTY

    # --- rendering -----------------------------------------------------------

    def _bg_for(self, x: int, y: int) -> str:
        if not self.color:
            return ""
        s = self.state[self.grid.idx(x, y)]
        p = self.palette
        return {
            self.EMPTY: "",
            self.CURSOR: p.cursor,
            self.FRONTIER: p.frontier,
            self.VISITED: p.visited,
            self.PATH: p.path,
            self.START: p.start,
            self.END: p.end,
        }[s]

    def _corner(self, x: int, y: int) -> str:
        """Pick a ┼-family glyph for the lattice corner at the top-left of (x,y)."""
        g = self.grid

        def vseg(cx: int, cy: int) -> int:
            """Vertical wall segment between cells (cx-1, cy) and (cx, cy) — 0 if outside maze rows."""
            if cy < 0 or cy >= g.height:
                return 0
            if 0 <= cx < g.width:
                return 1 if g.has_wall(cx, cy, W) else 0
            if 0 <= cx - 1 < g.width:
                return 1 if g.has_wall(cx - 1, cy, E) else 0
            return 0

        def hseg(cx: int, cy: int) -> int:
            """Horizontal wall segment between cells (cx, cy-1) and (cx, cy) — 0 if outside maze cols."""
            if cx < 0 or cx >= g.width:
                return 0
            if 0 <= cy < g.height:
                return 1 if g.has_wall(cx, cy, N) else 0
            if 0 <= cy - 1 < g.height:
                return 1 if g.has_wall(cx, cy - 1, S) else 0
            return 0

        n = vseg(x, y - 1)
        s = vseg(x, y)
        w = hseg(x - 1, y)
        e = hseg(x, y)
        return CORNERS[(n, e, s, w)]

    def draw(self, out=None) -> None:
        if out is None:
            out = sys.stdout
        g = self.grid
        wall_color = self.palette.wall if self.color else ""
        buf: list[str] = [HOME]

        # Top border: y = 0 row of corners + horizontals
        for row in range(g.height + 1):
            # corner + top-edge line
            line_parts: list[str] = []
            for col in range(g.width + 1):
                line_parts.append(wall_color + self._corner(col, row) + RESET if self.color else self._corner(col, row))
                if col < g.width:
                    if row == g.height:
                        wall_here = g.has_wall(col, row - 1, S)
                    else:
                        wall_here = g.has_wall(col, row, N)
                    glyph = "──" if wall_here else "  "
                    line_parts.append(wall_color + glyph + RESET if self.color and wall_here else glyph)
            buf.append("".join(line_parts))
            buf.append("\n")

            if row == g.height:
                break

            # body line: vertical walls + cell interiors
            body_parts: list[str] = []
            for col in range(g.width + 1):
                if col == g.width:
                    # rightmost vertical: right wall of last cell
                    wall_here = g.has_wall(col - 1, row, E)
                    body_parts.append(wall_color + "│" + RESET if self.color and wall_here else ("│" if wall_here else " "))
                    continue
                wall_here = g.has_wall(col, row, W)
                body_parts.append(wall_color + "│" + RESET if self.color and wall_here else ("│" if wall_here else " "))
                bg = self._bg_for(col, row)
                body_parts.append(bg + "  " + RESET if bg else "  ")
            buf.append("".join(body_parts))
            buf.append("\n")

        out.write("".join(buf))
        out.flush()


# ---------- generation algorithms -------------------------------------------

Callback = Callable[[], None] | None


def gen_dfs(grid: Grid, rng: random.Random, step: Callback = None,
            mark: Callable[[int, int, int], None] | None = None) -> None:
    """Recursive backtracker. Iterative to avoid Python recursion limits on big mazes."""
    start = (rng.randrange(grid.width), rng.randrange(grid.height))
    visited = {start}
    stack = [start]
    while stack:
        x, y = stack[-1]
        if mark:
            mark(x, y, Renderer.CURSOR)
        nbrs = [(nx, ny, d) for nx, ny, d in grid.neighbours(x, y) if (nx, ny) not in visited]
        if not nbrs:
            stack.pop()
            if mark:
                mark(x, y, Renderer.EMPTY)
            if step:
                step()
            continue
        nx, ny, d = rng.choice(nbrs)
        grid.carve(x, y, d)
        visited.add((nx, ny))
        stack.append((nx, ny))
        if step:
            step()


def gen_prim(grid: Grid, rng: random.Random, step: Callback = None,
             mark: Callable[[int, int, int], None] | None = None) -> None:
    """Randomised Prim's: grow a tree by picking a random frontier wall each step."""
    sx, sy = rng.randrange(grid.width), rng.randrange(grid.height)
    in_tree = {(sx, sy)}
    # frontier = (from_x, from_y, direction into new cell)
    frontier: list[tuple[int, int, int]] = [(sx, sy, d) for _, _, d in grid.neighbours(sx, sy)]
    while frontier:
        i = rng.randrange(len(frontier))
        fx, fy, d = frontier[i]
        frontier[i] = frontier[-1]
        frontier.pop()
        nx, ny = fx + DX[d], fy + DY[d]
        if (nx, ny) in in_tree:
            continue
        grid.carve(fx, fy, d)
        in_tree.add((nx, ny))
        if mark:
            mark(nx, ny, Renderer.CURSOR)
        for _, _, nd in grid.neighbours(nx, ny):
            tx, ty = nx + DX[nd], ny + DY[nd]
            if (tx, ty) not in in_tree:
                frontier.append((nx, ny, nd))
        if step:
            step()
        if mark:
            mark(nx, ny, Renderer.EMPTY)


def gen_wilson(grid: Grid, rng: random.Random, step: Callback = None,
               mark: Callable[[int, int, int], None] | None = None) -> None:
    """Wilson's algorithm: loop-erased random walk. Produces uniform spanning trees."""
    all_cells = [(x, y) for y in range(grid.height) for x in range(grid.width)]
    rng.shuffle(all_cells)
    in_tree: set[tuple[int, int]] = {all_cells.pop()}

    for target in all_cells:
        if target in in_tree:
            continue
        # random walk from target until we hit the tree, recording the direction chosen at each cell
        path_dir: dict[tuple[int, int], int] = {}
        cur = target
        walk_cells: list[tuple[int, int]] = [cur]
        while cur not in in_tree:
            if mark:
                mark(cur[0], cur[1], Renderer.CURSOR)
            nbrs = list(grid.neighbours(*cur))
            nx, ny, d = rng.choice(nbrs)
            path_dir[cur] = d
            cur = (nx, ny)
            # loop erase: if we've been here, chop back to that point
            if cur in path_dir and cur not in in_tree:
                # find cur in walk_cells and truncate
                while walk_cells and walk_cells[-1] != cur:
                    last = walk_cells.pop()
                    path_dir.pop(last, None)
                    if mark:
                        mark(last[0], last[1], Renderer.EMPTY)
            else:
                walk_cells.append(cur)
            if step:
                step()
        # now carve from target following recorded directions until we hit the tree
        cur = target
        while cur not in in_tree:
            d = path_dir[cur]
            nx, ny = cur[0] + DX[d], cur[1] + DY[d]
            grid.carve(cur[0], cur[1], d)
            in_tree.add(cur)
            if mark:
                mark(cur[0], cur[1], Renderer.EMPTY)
            cur = (nx, ny)
            if step:
                step()


GENERATORS = {"dfs": gen_dfs, "prim": gen_prim, "wilson": gen_wilson}


# ---------- solvers ---------------------------------------------------------

def solve_bfs(grid: Grid, start: tuple[int, int], end: tuple[int, int],
              step: Callback = None,
              mark: Callable[[int, int, int], None] | None = None) -> list[tuple[int, int]]:
    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    q: deque[tuple[int, int]] = deque([start])
    while q:
        x, y = q.popleft()
        if (x, y) == end:
            break
        if mark and (x, y) != start:
            mark(x, y, Renderer.VISITED)
        for d in DIRS:
            if grid.passable(x, y, d):
                nx, ny = x + DX[d], y + DY[d]
                if (nx, ny) in came_from:
                    continue
                came_from[(nx, ny)] = (x, y)
                if mark and (nx, ny) != end:
                    mark(nx, ny, Renderer.FRONTIER)
                q.append((nx, ny))
        if step:
            step()
    return _reconstruct(came_from, start, end)


def solve_astar(grid: Grid, start: tuple[int, int], end: tuple[int, int],
                step: Callback = None,
                mark: Callable[[int, int, int], None] | None = None) -> list[tuple[int, int]]:
    def h(p: tuple[int, int]) -> int:
        return abs(p[0] - end[0]) + abs(p[1] - end[1])

    came_from: dict[tuple[int, int], tuple[int, int] | None] = {start: None}
    g_score: dict[tuple[int, int], int] = {start: 0}
    counter = 0
    heap: list[tuple[int, int, tuple[int, int]]] = [(h(start), counter, start)]
    while heap:
        _, _, (x, y) = heapq.heappop(heap)
        if (x, y) == end:
            break
        if mark and (x, y) != start:
            mark(x, y, Renderer.VISITED)
        for d in DIRS:
            if grid.passable(x, y, d):
                nx, ny = x + DX[d], y + DY[d]
                tentative = g_score[(x, y)] + 1
                if tentative < g_score.get((nx, ny), 10**9):
                    came_from[(nx, ny)] = (x, y)
                    g_score[(nx, ny)] = tentative
                    counter += 1
                    heapq.heappush(heap, (tentative + h((nx, ny)), counter, (nx, ny)))
                    if mark and (nx, ny) != end:
                        mark(nx, ny, Renderer.FRONTIER)
        if step:
            step()
    return _reconstruct(came_from, start, end)


def _reconstruct(came_from: dict[tuple[int, int], tuple[int, int] | None],
                 start: tuple[int, int], end: tuple[int, int]) -> list[tuple[int, int]]:
    if end not in came_from:
        return []
    path: list[tuple[int, int]] = []
    cur: tuple[int, int] | None = end
    while cur is not None:
        path.append(cur)
        cur = came_from[cur]
    path.reverse()
    return path


SOLVERS = {"bfs": solve_bfs, "astar": solve_astar}


# ---------- driver ----------------------------------------------------------

def term_size() -> tuple[int, int]:
    try:
        sz = os.get_terminal_size()
        return sz.columns, sz.lines
    except OSError:
        return 80, 24


def pick_size(requested_w: int | None, requested_h: int | None) -> tuple[int, int]:
    cols, lines = term_size()
    # Each cell takes 2 cols + a divider, plus one extra col for the rightmost wall.
    # Each cell takes 1 row + a divider, plus one extra row for the bottom.
    max_w = max(5, (cols - 1) // 3)
    max_h = max(5, (lines - 3) // 2)
    w = requested_w or max_w
    h = requested_h or max_h
    return max(2, w), max(2, h)


def run(args: argparse.Namespace) -> int:
    rng = random.Random(args.seed)
    w, h = pick_size(args.width, args.height)
    grid = Grid(w, h)
    palette = Palette()
    renderer = Renderer(grid, palette, color=not args.no_color)

    interactive = sys.stdout.isatty() and not args.no_animate
    frame_every = max(1, args.frame_every)
    frame_counter = [0]
    last_draw_time = [0.0]
    frame_interval = 1.0 / max(1.0, args.fps)

    def tick() -> None:
        if not interactive:
            return
        frame_counter[0] += 1
        if frame_counter[0] % frame_every:
            return
        now = time.monotonic()
        if now - last_draw_time[0] < frame_interval:
            return
        last_draw_time[0] = now
        renderer.draw()

    def mark(x: int, y: int, s: int) -> None:
        renderer.set_state(x, y, s)

    if interactive:
        sys.stdout.write(HIDE_CURSOR + CLEAR)
        sys.stdout.flush()

    try:
        # generate
        GENERATORS[args.gen](grid, rng, step=tick if interactive else None,
                             mark=mark if interactive else None)
        if interactive:
            renderer.clear_state()
            renderer.draw()

        if args.solve:
            start = (0, 0)
            end = (w - 1, h - 1)
            renderer.set_state(*start, Renderer.START)
            renderer.set_state(*end, Renderer.END)
            if interactive:
                renderer.draw()

            path = SOLVERS[args.solve](grid, start, end,
                                       step=tick if interactive else None,
                                       mark=mark if interactive else None)
            # paint final path
            for (x, y) in path:
                if (x, y) not in (start, end):
                    renderer.set_state(x, y, Renderer.PATH)
            renderer.set_state(*start, Renderer.START)
            renderer.set_state(*end, Renderer.END)
            if interactive or args.no_animate:
                renderer.draw()
            if args.print_length:
                sys.stdout.write(f"\npath length: {len(path)} cells\n")
        else:
            if not interactive:
                renderer.draw()
    finally:
        if interactive:
            sys.stdout.write(SHOW_CURSOR)
            sys.stdout.flush()

    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="animated terminal maze generator & solver")
    p.add_argument("--gen", choices=sorted(GENERATORS), default="dfs",
                   help="generation algorithm (default: dfs)")
    p.add_argument("--solve", choices=sorted(SOLVERS), nargs="?", const="bfs", default=None,
                   help="also solve the maze (default solver: bfs)")
    p.add_argument("-W", "--width", type=int, default=None, help="maze width in cells")
    p.add_argument("-H", "--height", type=int, default=None, help="maze height in cells")
    p.add_argument("--seed", type=int, default=None, help="RNG seed (for reproducible mazes)")
    p.add_argument("--fps", type=float, default=120.0, help="max animation frames/sec (default 120)")
    p.add_argument("--frame-every", type=int, default=1,
                   help="draw one frame every N algorithm steps (higher = faster)")
    p.add_argument("--no-animate", action="store_true", help="skip animation; draw final state only")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colour")
    p.add_argument("--print-length", action="store_true",
                   help="print the solved path length after rendering")
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv if argv is not None else sys.argv[1:])
    try:
        return run(args)
    except KeyboardInterrupt:
        sys.stdout.write(SHOW_CURSOR + "\n")
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
