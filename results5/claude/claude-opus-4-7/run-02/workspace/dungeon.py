#!/usr/bin/env python3
"""Procedural dungeon generator using Binary Space Partitioning."""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass, field


WALL = "#"
FLOOR = "."
CORRIDOR = "+"
DOOR = "D"
EMPTY = " "

# ANSI colors
RESET = "\x1b[0m"
DIM = "\x1b[2m"
BOLD = "\x1b[1m"
GREY = "\x1b[38;5;240m"
STONE = "\x1b[38;5;247m"
SAND = "\x1b[38;5;180m"
BROWN = "\x1b[38;5;130m"
GOLD = "\x1b[38;5;220m"
RED = "\x1b[38;5;160m"
GREEN = "\x1b[38;5;34m"
BLUE = "\x1b[38;5;39m"


@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def x2(self) -> int:
        return self.x + self.w

    @property
    def y2(self) -> int:
        return self.y + self.h

    @property
    def cx(self) -> int:
        return self.x + self.w // 2

    @property
    def cy(self) -> int:
        return self.y + self.h // 2


@dataclass
class Leaf:
    rect: Rect
    left: "Leaf | None" = None
    right: "Leaf | None" = None
    room: Rect | None = None
    corridors: list[Rect] = field(default_factory=list)

    MIN = 7

    def split(self, rng: random.Random) -> bool:
        if self.left or self.right:
            return False
        # Decide split direction
        wide = self.rect.w / self.rect.h >= 1.25
        tall = self.rect.h / self.rect.w >= 1.25
        horizontal = rng.random() < 0.5
        if wide:
            horizontal = False
        elif tall:
            horizontal = True

        max_dim = self.rect.h - self.MIN if horizontal else self.rect.w - self.MIN
        if max_dim <= self.MIN:
            return False

        split_at = rng.randint(self.MIN, max_dim)
        if horizontal:
            self.left = Leaf(Rect(self.rect.x, self.rect.y, self.rect.w, split_at))
            self.right = Leaf(
                Rect(self.rect.x, self.rect.y + split_at, self.rect.w, self.rect.h - split_at)
            )
        else:
            self.left = Leaf(Rect(self.rect.x, self.rect.y, split_at, self.rect.h))
            self.right = Leaf(
                Rect(self.rect.x + split_at, self.rect.y, self.rect.w - split_at, self.rect.h)
            )
        return True

    def iter_leaves(self):
        if self.left or self.right:
            if self.left:
                yield from self.left.iter_leaves()
            if self.right:
                yield from self.right.iter_leaves()
        else:
            yield self

    def create_room(self, rng: random.Random) -> None:
        pad = 1
        rw = rng.randint(4, max(4, self.rect.w - 2 * pad))
        rh = rng.randint(3, max(3, self.rect.h - 2 * pad))
        rx = self.rect.x + rng.randint(pad, max(pad, self.rect.w - rw - pad))
        ry = self.rect.y + rng.randint(pad, max(pad, self.rect.h - rh - pad))
        self.room = Rect(rx, ry, rw, rh)


def build_tree(rect: Rect, rng: random.Random, max_depth: int = 6) -> Leaf:
    root = Leaf(rect)
    stack = [(root, 0)]
    while stack:
        node, depth = stack.pop()
        if depth >= max_depth:
            continue
        # Bias toward splitting larger regions
        area = node.rect.w * node.rect.h
        if area < 120 and rng.random() < 0.3:
            continue
        if node.split(rng):
            stack.append((node.left, depth + 1))
            stack.append((node.right, depth + 1))
    return root


def carve_rooms(root: Leaf, rng: random.Random) -> list[Rect]:
    rooms: list[Rect] = []
    for leaf in root.iter_leaves():
        leaf.create_room(rng)
        if leaf.room:
            rooms.append(leaf.room)
    return rooms


def connect(a: Rect, b: Rect, rng: random.Random) -> list[tuple[int, int, int, int]]:
    """Return L-shaped corridor segments between centers of a and b."""
    ax, ay = a.cx, a.cy
    bx, by = b.cx, b.cy
    segments = []
    if rng.random() < 0.5:
        segments.append((min(ax, bx), ay, max(ax, bx), ay))  # horizontal
        segments.append((bx, min(ay, by), bx, max(ay, by)))  # vertical
    else:
        segments.append((ax, min(ay, by), ax, max(ay, by)))
        segments.append((min(ax, bx), by, max(ax, bx), by))
    return segments


def connect_tree(node: Leaf, rng: random.Random, grid: list[list[str]]) -> Rect | None:
    if node.room:
        return node.room
    left_room = connect_tree(node.left, rng, grid) if node.left else None
    right_room = connect_tree(node.right, rng, grid) if node.right else None
    if left_room and right_room:
        for x1, y1, x2, y2 in connect(left_room, right_room, rng):
            carve_corridor(grid, x1, y1, x2, y2)
        return left_room if rng.random() < 0.5 else right_room
    return left_room or right_room


def carve_corridor(grid, x1, y1, x2, y2):
    if x1 > x2:
        x1, x2 = x2, x1
    if y1 > y2:
        y1, y2 = y2, y1
    for y in range(y1, y2 + 1):
        for x in range(x1, x2 + 1):
            if 0 <= y < len(grid) and 0 <= x < len(grid[0]):
                if grid[y][x] == WALL or grid[y][x] == EMPTY:
                    grid[y][x] = CORRIDOR


def carve_room(grid, room: Rect):
    for y in range(room.y, room.y2):
        for x in range(room.x, room.x2):
            grid[y][x] = FLOOR


def surround_walls(grid):
    h, w = len(grid), len(grid[0])
    out = [row[:] for row in grid]
    for y in range(h):
        for x in range(w):
            if grid[y][x] in (FLOOR, CORRIDOR):
                for dy in (-1, 0, 1):
                    for dx in (-1, 0, 1):
                        ny, nx = y + dy, x + dx
                        if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] == EMPTY:
                            out[ny][nx] = WALL
    return out


def place_doors(grid, rooms):
    """Convert corridor tiles touching a room edge into doors."""
    h, w = len(grid), len(grid[0])
    for room in rooms:
        for y in range(room.y - 1, room.y2 + 1):
            for x in range(room.x - 1, room.x2 + 1):
                if not (0 <= y < h and 0 <= x < w):
                    continue
                if grid[y][x] != CORRIDOR:
                    continue
                # Corridor tile adjacent to a room floor → door
                on_edge = (
                    x == room.x - 1 or x == room.x2 or y == room.y - 1 or y == room.y2
                )
                if on_edge:
                    # Must be adjacent to exactly one room floor for a clean door
                    adj_floor = 0
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        nx, ny = x + dx, y + dy
                        if 0 <= ny < h and 0 <= nx < w and grid[ny][nx] == FLOOR:
                            adj_floor += 1
                    if adj_floor >= 1:
                        grid[y][x] = DOOR


def place_features(grid, rooms, rng):
    """Mark entrance '<', exit '>', and sprinkle some gold '$'."""
    if not rooms:
        return
    start = rooms[0]
    end = rooms[-1]
    # pick furthest pair for entrance/exit
    best = 0
    sx, sy = start.cx, start.cy
    ex, ey = end.cx, end.cy
    for a in rooms:
        for b in rooms:
            d = (a.cx - b.cx) ** 2 + (a.cy - b.cy) ** 2
            if d > best:
                best = d
                sx, sy = a.cx, a.cy
                ex, ey = b.cx, b.cy
    grid[sy][sx] = "<"
    grid[ey][ex] = ">"
    # sprinkle gold in ~20% of rooms
    for room in rooms:
        if (room.cx, room.cy) in ((sx, sy), (ex, ey)):
            continue
        if rng.random() < 0.25:
            gx = rng.randint(room.x, room.x2 - 1)
            gy = rng.randint(room.y, room.y2 - 1)
            if grid[gy][gx] == FLOOR:
                grid[gy][gx] = "$"


def render(grid, color: bool) -> str:
    lines = []
    for row in grid:
        if not color:
            lines.append("".join(row))
            continue
        buf = []
        for ch in row:
            if ch == WALL:
                buf.append(f"{STONE}{ch}{RESET}")
            elif ch == FLOOR:
                buf.append(f"{DIM}{SAND}{ch}{RESET}")
            elif ch == CORRIDOR:
                buf.append(f"{BROWN}{ch}{RESET}")
            elif ch == DOOR:
                buf.append(f"{BOLD}{BROWN}{ch}{RESET}")
            elif ch == "<":
                buf.append(f"{BOLD}{GREEN}<{RESET}")
            elif ch == ">":
                buf.append(f"{BOLD}{RED}>{RESET}")
            elif ch == "$":
                buf.append(f"{BOLD}{GOLD}${RESET}")
            else:
                buf.append(ch)
        lines.append("".join(buf))
    return "\n".join(lines)


def generate(width: int, height: int, seed: int) -> tuple[list[list[str]], list[Rect]]:
    rng = random.Random(seed)
    grid = [[EMPTY for _ in range(width)] for _ in range(height)]
    root = build_tree(Rect(0, 0, width, height), rng)
    rooms = carve_rooms(root, rng)
    for room in rooms:
        carve_room(grid, room)
    connect_tree(root, rng, grid)
    grid = surround_walls(grid)
    place_doors(grid, rooms)
    place_features(grid, rooms, rng)
    return grid, rooms


def main():
    ap = argparse.ArgumentParser(description="Procedural dungeon generator (BSP).")
    ap.add_argument("-W", "--width", type=int, default=80)
    ap.add_argument("-H", "--height", type=int, default=30)
    ap.add_argument("-s", "--seed", type=int, default=None)
    ap.add_argument("--no-color", action="store_true")
    ap.add_argument("-n", "--count", type=int, default=1, help="generate N dungeons")
    args = ap.parse_args()

    base_seed = args.seed if args.seed is not None else random.randrange(1 << 30)
    color = (not args.no_color) and sys.stdout.isatty()

    for i in range(args.count):
        seed = base_seed + i
        grid, rooms = generate(args.width, args.height, seed)
        print(f"-- dungeon seed={seed} rooms={len(rooms)} --")
        print(render(grid, color=color))
        print()


if __name__ == "__main__":
    main()
