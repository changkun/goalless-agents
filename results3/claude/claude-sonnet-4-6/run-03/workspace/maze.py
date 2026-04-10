#!/usr/bin/env python3
"""
Terminal Maze Generator & Solver
Generates mazes with recursive backtracking (DFS), solves with A*.
Animated visualization in the terminal.
Interactive player mode: navigate with arrow keys or WASD.
"""

import sys
import os
import tty
import termios
import time
import random
import argparse
import heapq
from collections import deque


# ANSI color codes
class C:
    RESET   = "\033[0m"
    WALL    = "\033[38;5;240m"      # dark gray
    PATH    = "\033[38;5;255m"      # white
    START   = "\033[38;5;46m"       # bright green
    END     = "\033[38;5;196m"      # bright red
    VISITED = "\033[38;5;27m"       # blue
    SOLVE   = "\033[38;5;226m"      # yellow
    FINAL   = "\033[38;5;208m"      # orange
    GEN     = "\033[38;5;93m"       # purple
    TITLE   = "\033[1;38;5;51m"     # bold cyan
    DIM     = "\033[38;5;238m"      # very dark
    BOLD    = "\033[1m"


WALL    = 0
PASSAGE = 1
START   = 2
END     = 3

WALL_CHARS = {
    # (N, E, S, W) -> char
    (True,  True,  True,  True ): "┼",
    (True,  True,  True,  False): "├",
    (True,  True,  False, True ): "┴",
    (True,  True,  False, False): "└",
    (True,  False, True,  True ): "┤",
    (True,  False, True,  False): "│",
    (True,  False, False, True ): "┘",
    (True,  False, False, False): "╵",
    (False, True,  True,  True ): "┬",
    (False, True,  True,  False): "┌",
    (False, True,  False, True ): "─",
    (False, True,  False, False): "╶",
    (False, False, True,  True ): "┐",
    (False, False, True,  False): "╷",
    (False, False, False, True ): "╴",
    (False, False, False, False): " ",
}


class Maze:
    def __init__(self, width: int, height: int, seed: int | None = None):
        # Internal grid is (2*h+1) x (2*w+1) to represent walls between cells
        self.cols = width
        self.rows = height
        self.rng = random.Random(seed)
        self.grid = [[WALL] * (2 * width + 1) for _ in range(2 * height + 1)]
        self.start = (0, 0)               # cell coordinates
        self.end   = (height - 1, width - 1)
        self._gen_frames: list[list[list[int]]] = []
        self._solve_frames: list[list[list[int]]] = []

    # ── coordinate helpers ────────────────────────────────────────────────────

    def _cell_to_grid(self, r: int, c: int) -> tuple[int, int]:
        return (2 * r + 1, 2 * c + 1)

    def _wall_between(self, r1: int, c1: int, r2: int, c2: int) -> tuple[int, int]:
        gr1, gc1 = self._cell_to_grid(r1, c1)
        gr2, gc2 = self._cell_to_grid(r2, c2)
        return ((gr1 + gr2) // 2, (gc1 + gc2) // 2)

    def _neighbors(self, r: int, c: int) -> list[tuple[int, int]]:
        result = []
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                result.append((nr, nc))
        return result

    # ── generation: recursive backtracking ───────────────────────────────────

    def generate(self, animate: bool = False, delay: float = 0.01) -> None:
        visited = [[False] * self.cols for _ in range(self.rows)]
        stack: list[tuple[int, int]] = []

        sr, sc = self.start
        er, ec = self.end

        # open start cell
        gr, gc = self._cell_to_grid(sr, sc)
        self.grid[gr][gc] = PASSAGE
        visited[sr][sc] = True
        stack.append((sr, sc))

        frame_interval = max(1, (self.rows * self.cols) // 60)
        frame_count = 0

        while stack:
            r, c = stack[-1]
            gr, gc = self._cell_to_grid(r, c)
            self.grid[gr][gc] = PASSAGE

            unvisited = [(nr, nc) for nr, nc in self._neighbors(r, c)
                         if not visited[nr][nc]]

            if unvisited:
                nr, nc = self.rng.choice(unvisited)
                visited[nr][nc] = True
                wr, wc = self._wall_between(r, c, nr, nc)
                self.grid[wr][wc] = PASSAGE
                stack.append((nr, nc))
            else:
                stack.pop()

            frame_count += 1
            if animate and frame_count % frame_interval == 0:
                self._mark_endpoints()
                self._render_frame(delay)

        # open entrance and exit
        self.grid[1][0] = PASSAGE
        self.grid[2 * self.rows - 1][2 * self.cols] = PASSAGE

        self._mark_endpoints()
        if animate:
            self._render_frame(delay)

    # ── solving: A* ──────────────────────────────────────────────────────────

    def solve(self, animate: bool = False, delay: float = 0.02) -> list[tuple[int, int]]:
        sr, sc = self.start
        er, ec = self.end

        def h(r: int, c: int) -> int:
            return abs(r - er) + abs(c - ec)

        dist: dict[tuple[int, int], int] = {(sr, sc): 0}
        prev: dict[tuple[int, int], tuple[int, int] | None] = {(sr, sc): None}
        heap: list[tuple[int, int, int, int]] = [(h(sr, sc), 0, sr, sc)]
        visited_set: set[tuple[int, int]] = set()

        VISIT_MARK = 4
        SOLVE_MARK = 5

        frame_interval = max(1, (self.rows * self.cols) // 80)
        frame_count = 0

        while heap:
            _, d, r, c = heapq.heappop(heap)
            if (r, c) in visited_set:
                continue
            visited_set.add((r, c))

            # mark visited on grid for visualization
            gr, gc = self._cell_to_grid(r, c)
            if self.grid[gr][gc] not in (START, END):
                self.grid[gr][gc] = VISIT_MARK

            if (r, c) == (er, ec):
                break

            for nr, nc in self._neighbors(r, c):
                wr, wc = self._wall_between(r, c, nr, nc)
                if self.grid[wr][wc] in (PASSAGE, VISIT_MARK, START, END) and \
                        self.grid[wr][wc] != WALL:
                    # check wall is open
                    raw = self.grid[wr][wc]
                    if raw == WALL:
                        continue
                    nd = d + 1
                    if nd < dist.get((nr, nc), 10**9):
                        dist[(nr, nc)] = nd
                        prev[(nr, nc)] = (r, c)
                        heapq.heappush(heap, (nd + h(nr, nc), nd, nr, nc))

            frame_count += 1
            if animate and frame_count % frame_interval == 0:
                self._render_frame(delay)

        # reconstruct path
        path: list[tuple[int, int]] = []
        node: tuple[int, int] | None = (er, ec)
        while node is not None:
            path.append(node)
            node = prev.get(node)
        path.reverse()

        # mark solution path
        for pr, pc in path:
            gr, gc = self._cell_to_grid(pr, pc)
            if self.grid[gr][gc] not in (START, END):
                self.grid[gr][gc] = SOLVE_MARK
            # mark wall segments between path steps
        for i in range(len(path) - 1):
            r1, c1 = path[i]
            r2, c2 = path[i + 1]
            wr, wc = self._wall_between(r1, c1, r2, c2)
            if self.grid[wr][wc] not in (START, END):
                self.grid[wr][wc] = SOLVE_MARK

        if animate:
            self._render_frame(0)

        return path

    # ── rendering ─────────────────────────────────────────────────────────────

    def _mark_endpoints(self) -> None:
        sr, sc = self.start
        er, ec = self.end
        gr, gc = self._cell_to_grid(sr, sc)
        self.grid[gr][gc] = START
        gr, gc = self._cell_to_grid(er, ec)
        self.grid[gr][gc] = END

    def _wall_char(self, r: int, c: int) -> str:
        rows = len(self.grid)
        cols = len(self.grid[0])
        N = r > 0       and self.grid[r-1][c] == WALL
        S = r < rows-1  and self.grid[r+1][c] == WALL
        E = c < cols-1  and self.grid[r][c+1] == WALL
        W = c > 0       and self.grid[r][c-1] == WALL
        return WALL_CHARS.get((N, E, S, W), "█")

    def render(self) -> str:
        lines: list[str] = []
        VISIT_MARK = 4
        SOLVE_MARK = 5

        for r, row in enumerate(self.grid):
            line: list[str] = []
            for c, cell in enumerate(row):
                if cell == WALL:
                    ch = self._wall_char(r, c)
                    line.append(f"{C.WALL}{ch}{C.RESET}")
                elif cell == PASSAGE:
                    line.append(f"{C.PATH} {C.RESET}")
                elif cell == START:
                    line.append(f"{C.START}S{C.RESET}")
                elif cell == END:
                    line.append(f"{C.END}E{C.RESET}")
                elif cell == VISIT_MARK:
                    line.append(f"{C.VISITED}·{C.RESET}")
                elif cell == SOLVE_MARK:
                    line.append(f"{C.FINAL}█{C.RESET}")
                else:
                    line.append(" ")
            lines.append("".join(line))
        return "\n".join(lines)

    def _render_frame(self, delay: float) -> None:
        rendered = self.render()
        grid_h = len(self.grid)
        # move cursor up to overwrite previous frame
        sys.stdout.write(f"\033[{grid_h}A\r")
        sys.stdout.write(rendered)
        sys.stdout.flush()
        if delay > 0:
            time.sleep(delay)

    # ── interactive play ──────────────────────────────────────────────────────

    def play(self) -> None:
        """Let the user navigate the maze interactively with arrow keys / WASD."""
        pr, pc = self.start          # player cell position
        er, ec = self.end
        steps = 0
        visited: set[tuple[int, int]] = {(pr, pc)}
        start_time = time.time()

        PLAYER = 6   # value to mark player cell

        def _read_key() -> str:
            fd = sys.stdin.fileno()
            old = termios.tcgetattr(fd)
            try:
                tty.setraw(fd)
                ch = sys.stdin.read(1)
                if ch == "\x1b":
                    ch2 = sys.stdin.read(1)
                    ch3 = sys.stdin.read(1)
                    return ch + ch2 + ch3
                return ch
            finally:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

        def _render_play(player_r: int, player_c: int) -> str:
            lines: list[str] = []
            VISIT_MARK = 7
            for r, row in enumerate(self.grid):
                line: list[str] = []
                for c, cell in enumerate(row):
                    # Check if this grid cell is the player's cell position
                    if (r, c) == self._cell_to_grid(player_r, player_c):
                        line.append(f"{C.SOLVE}@{C.RESET}")
                    elif cell == WALL:
                        ch = self._wall_char(r, c)
                        line.append(f"{C.WALL}{ch}{C.RESET}")
                    elif cell == START:
                        line.append(f"{C.START}S{C.RESET}")
                    elif cell == END:
                        line.append(f"{C.END}E{C.RESET}")
                    elif cell == VISIT_MARK:
                        line.append(f"{C.VISITED}·{C.RESET}")
                    elif cell == PASSAGE:
                        line.append(f"{C.PATH} {C.RESET}")
                    else:
                        line.append(" ")
                lines.append("".join(line))
            return "\n".join(lines)

        def _mark_visited(r: int, c: int) -> None:
            gr, gc = self._cell_to_grid(r, c)
            if self.grid[gr][gc] == PASSAGE:
                self.grid[gr][gc] = 7   # VISIT_MARK for play mode
            # also mark the wall segment we came through (not needed here — handled on move)

        # Mark start as visited
        _mark_visited(pr, pc)

        ARROW = {
            "\x1b[A": (-1,  0),   # up
            "\x1b[B": ( 1,  0),   # down
            "\x1b[C": ( 0,  1),   # right
            "\x1b[D": ( 0, -1),   # left
        }
        WASD = {
            "w": (-1,  0), "k": (-1,  0),
            "s": ( 1,  0), "j": ( 1,  0),
            "d": ( 0,  1), "l": ( 0,  1),
            "a": ( 0, -1), "h": ( 0, -1),
        }

        grid_h = len(self.grid)

        # Initial draw
        sys.stdout.write(f"{C.TITLE}  Navigate: arrow keys or WASD/hjkl  │  q to quit{C.RESET}\n")
        sys.stdout.write("\n" * grid_h)

        def _redraw(elapsed: float) -> None:
            # Move cursor up to overwrite
            sys.stdout.write(f"\033[{grid_h}A\r")
            sys.stdout.write(_render_play(pr, pc))
            sys.stdout.flush()
            # Status line below the maze
            sys.stdout.write(
                f"\n  {C.BOLD}Steps:{C.RESET} {steps:<5} "
                f"{C.BOLD}Time:{C.RESET} {elapsed:.1f}s   \r"
            )
            sys.stdout.flush()

        _redraw(0.0)

        while True:
            elapsed = time.time() - start_time
            _redraw(elapsed)

            key = _read_key()

            if key in ("q", "Q", "\x03", "\x1b"):
                print(f"\n\n{C.DIM}  Quit after {steps} steps.{C.RESET}\n")
                return

            dr, dc = ARROW.get(key) or WASD.get(key.lower(), (0, 0))
            if dr == 0 and dc == 0:
                continue

            nr, nc = pr + dr, pc + dc
            if not (0 <= nr < self.rows and 0 <= nc < self.cols):
                continue

            # Check wall is open
            wr, wc = self._wall_between(pr, pc, nr, nc)
            if self.grid[wr][wc] == WALL:
                continue   # blocked

            # Valid move
            steps += 1
            pr, pc = nr, nc
            _mark_visited(pr, pc)

            if (pr, pc) == (er, ec):
                elapsed = time.time() - start_time
                _redraw(elapsed)
                print(f"\n\n{C.START}  YOU WIN!{C.RESET}  {C.BOLD}{steps} steps{C.RESET} in {C.BOLD}{elapsed:.2f}s{C.RESET}\n")
                return

    def stats(self, path: list[tuple[int, int]]) -> dict:
        total_cells = self.rows * self.cols
        passages = sum(
            1 for r in range(1, len(self.grid), 2)
              for c in range(1, len(self.grid[0]), 2)
        )
        return {
            "size":       f"{self.cols}×{self.rows}",
            "cells":      total_cells,
            "path_len":   len(path),
            "efficiency": f"{len(path)/total_cells*100:.1f}%",
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

def banner() -> None:
    print(f"""
{C.TITLE}╔══════════════════════════════════╗
║   MAZE GENERATOR & SOLVER  v1.0  ║
║   Recursive Backtracking + A*    ║
╚══════════════════════════════════╝{C.RESET}""")


def print_legend() -> None:
    print(
        f"  {C.START}S{C.RESET} start  "
        f"{C.END}E{C.RESET} end  "
        f"{C.FINAL}█{C.RESET} solution  "
        f"{C.VISITED}·{C.RESET} explored  "
        f"{C.WALL}█{C.RESET} wall\n"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Terminal maze generator and solver"
    )
    parser.add_argument("-W", "--width",   type=int, default=30,
                        help="Maze width in cells (default: 30)")
    parser.add_argument("-H", "--height",  type=int, default=15,
                        help="Maze height in cells (default: 15)")
    parser.add_argument("-s", "--seed",    type=int, default=None,
                        help="Random seed for reproducible mazes")
    parser.add_argument("--no-animate",   action="store_true",
                        help="Skip animations, show final result only")
    parser.add_argument("--gen-delay",    type=float, default=0.008,
                        help="Generation animation delay in seconds (default: 0.008)")
    parser.add_argument("--solve-delay",  type=float, default=0.015,
                        help="Solve animation delay in seconds (default: 0.015)")
    parser.add_argument("--play",         action="store_true",
                        help="Interactive mode: navigate the maze yourself")
    args = parser.parse_args()

    animate = not args.no_animate

    banner()
    print(f"  {C.BOLD}Size:{C.RESET} {args.width}×{args.height}  "
          f"{C.BOLD}Seed:{C.RESET} {args.seed if args.seed is not None else 'random'}\n")
    print_legend()

    maze = Maze(args.width, args.height, seed=args.seed)

    # ── generation phase ──────────────────────────────────────────────────────
    if args.play:
        print(f"{C.GEN}  Generating maze…{C.RESET}")
        maze.generate(animate=False)
        maze._mark_endpoints()
        print(maze.render())
        print()
        maze.play()
        return

    print(f"{C.GEN}  Generating…{C.RESET}")
    # print blank placeholder so animation can overwrite it
    grid_h = 2 * maze.rows + 1
    print("\n" * grid_h, end="")

    t0 = time.time()
    maze.generate(animate=animate, delay=args.gen_delay)
    gen_time = time.time() - t0

    if not animate:
        maze._mark_endpoints()
        print(maze.render())

    print(f"\n{C.GEN}  Generated in {gen_time*1000:.1f}ms{C.RESET}")

    # ── solve phase ────────────────────────────────────────────────────────────
    time.sleep(0.3)
    print(f"\n{C.SOLVE}  Solving with A*…{C.RESET}")
    print("\n" * grid_h, end="")

    t0 = time.time()
    path = maze.solve(animate=animate, delay=args.solve_delay)
    solve_time = time.time() - t0

    if not animate:
        print(maze.render())

    print(f"\n{C.SOLVE}  Solved  in {solve_time*1000:.1f}ms{C.RESET}")

    # ── stats ──────────────────────────────────────────────────────────────────
    s = maze.stats(path)
    print(f"""
{C.TITLE}  ── Stats ───────────────────────{C.RESET}
  Maze size   {C.BOLD}{s['size']}{C.RESET} ({s['cells']} cells)
  Path length {C.BOLD}{s['path_len']} steps{C.RESET}
  Efficiency  {C.BOLD}{s['efficiency']}{C.RESET} of cells on path
""")


if __name__ == "__main__":
    main()
