"""Tests for maze.py — focus on correctness invariants, not rendering."""
from __future__ import annotations

import io
import random
import sys
from collections import deque

import pytest

import maze
from maze import (
    DIRS,
    DX,
    DY,
    GENERATORS,
    Grid,
    OPP,
    SOLVERS,
    gen_dfs,
    gen_prim,
    gen_wilson,
    solve_astar,
    solve_bfs,
)


# ---------- generic helpers --------------------------------------------------


def reachable_cells(grid: Grid, start=(0, 0)) -> set[tuple[int, int]]:
    seen = {start}
    q = deque([start])
    while q:
        x, y = q.popleft()
        for d in DIRS:
            if grid.passable(x, y, d):
                nx, ny = x + DX[d], y + DY[d]
                if (nx, ny) not in seen:
                    seen.add((nx, ny))
                    q.append((nx, ny))
    return seen


def count_internal_open_walls(grid: Grid) -> int:
    """Number of distinct internal edges (between two cells) that have no wall."""
    opened = 0
    for y in range(grid.height):
        for x in range(grid.width):
            # only count E and S to avoid double-counting
            if x + 1 < grid.width and grid.passable(x, y, 2):  # E
                opened += 1
            if y + 1 < grid.height and grid.passable(x, y, 4):  # S
                opened += 1
    return opened


def walls_are_symmetric(grid: Grid) -> bool:
    """If cell (x,y) has its E wall removed, (x+1,y) must have its W wall removed."""
    for y in range(grid.height):
        for x in range(grid.width):
            for d in DIRS:
                nx, ny = x + DX[d], y + DY[d]
                if not grid.in_bounds(nx, ny):
                    continue
                if grid.has_wall(x, y, d) != grid.has_wall(nx, ny, OPP[d]):
                    return False
    return True


# ---------- Grid basics ------------------------------------------------------


def test_grid_starts_fully_walled():
    g = Grid(4, 3)
    for y in range(g.height):
        for x in range(g.width):
            for d in DIRS:
                assert g.has_wall(x, y, d)


def test_carve_is_symmetric():
    g = Grid(3, 3)
    g.carve(1, 1, 2)  # east
    assert not g.has_wall(1, 1, 2)
    assert not g.has_wall(2, 1, 8)  # west of neighbour
    # other walls untouched
    assert g.has_wall(1, 1, 1)
    assert g.has_wall(1, 1, 4)
    assert g.has_wall(1, 1, 8)


def test_carve_out_of_bounds_is_noop():
    g = Grid(2, 2)
    before = list(g.walls)
    g.carve(0, 0, 8)  # west off the edge
    g.carve(1, 1, 2)  # east off the edge
    assert g.walls == before


# ---------- generation algorithms are perfect mazes --------------------------


@pytest.mark.parametrize("name", sorted(GENERATORS))
@pytest.mark.parametrize("size", [(2, 2), (5, 5), (12, 8)])
def test_generators_produce_perfect_maze(name, size):
    """A perfect maze over N cells is a spanning tree: connected + exactly N-1 open edges."""
    w, h = size
    rng = random.Random(1234)
    g = Grid(w, h)
    GENERATORS[name](g, rng)
    assert walls_are_symmetric(g)
    assert len(reachable_cells(g)) == w * h, f"{name} left unreachable cells"
    assert count_internal_open_walls(g) == w * h - 1, f"{name} has loops or is disconnected"


@pytest.mark.parametrize("name", sorted(GENERATORS))
def test_generators_are_reproducible(name):
    w, h = 8, 6
    g1 = Grid(w, h)
    g2 = Grid(w, h)
    GENERATORS[name](g1, random.Random(42))
    GENERATORS[name](g2, random.Random(42))
    assert g1.walls == g2.walls


# ---------- solvers ----------------------------------------------------------


def _solved(grid: Grid, path: list[tuple[int, int]], start, end) -> bool:
    if not path or path[0] != start or path[-1] != end:
        return False
    for (ax, ay), (bx, by) in zip(path, path[1:]):
        dx, dy = bx - ax, by - ay
        # each step must be a single cardinal move through an open wall
        d = None
        for direction in DIRS:
            if (DX[direction], DY[direction]) == (dx, dy):
                d = direction
                break
        if d is None:
            return False
        if not grid.passable(ax, ay, d):
            return False
    return True


@pytest.mark.parametrize("solver_name", sorted(SOLVERS))
@pytest.mark.parametrize("gen_name", sorted(GENERATORS))
def test_solver_finds_valid_path(gen_name, solver_name):
    w, h = 10, 8
    g = Grid(w, h)
    GENERATORS[gen_name](g, random.Random(7))
    start, end = (0, 0), (w - 1, h - 1)
    path = SOLVERS[solver_name](g, start, end)
    assert _solved(g, path, start, end)


def test_bfs_and_astar_return_same_length():
    """On a perfect maze both give shortest paths, so path lengths must match."""
    w, h = 12, 9
    g = Grid(w, h)
    gen_dfs(g, random.Random(99))
    start, end = (0, 0), (w - 1, h - 1)
    assert len(solve_bfs(g, start, end)) == len(solve_astar(g, start, end))


def test_solver_on_unreachable_returns_empty():
    # construct a 2x1 grid and DON'T carve anything
    g = Grid(2, 1)
    assert solve_bfs(g, (0, 0), (1, 0)) == []
    assert solve_astar(g, (0, 0), (1, 0)) == []


# ---------- CLI / entry point ------------------------------------------------


def test_main_no_animate_writes_something(monkeypatch, capsys):
    """Smoke test: --no-animate --no-color on a small maze prints and exits 0."""
    rc = maze.main(["--gen", "dfs", "--no-animate", "--no-color", "-W", "6", "-H", "4", "--seed", "1"])
    assert rc == 0
    out = capsys.readouterr().out
    # Should contain unicode box characters.
    assert any(ch in out for ch in "┌┐└┘─│┼┬┴├┤")


def test_main_solve_prints_length(capsys):
    rc = maze.main([
        "--gen", "prim", "--solve", "bfs", "--no-animate", "--no-color",
        "-W", "6", "-H", "4", "--seed", "2", "--print-length",
    ])
    assert rc == 0
    out = capsys.readouterr().out
    assert "path length:" in out


def test_parse_args_solve_default_is_bfs():
    ns = maze.parse_args(["--solve"])
    assert ns.solve == "bfs"
