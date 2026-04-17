#!/usr/bin/env python3
"""
dungen — a procedural dungeon generator.

Generates a dungeon using Binary Space Partitioning (BSP):
  1. Recursively split the grid into smaller and smaller regions.
  2. Place a room inside each leaf region.
  3. Connect sibling regions with L-shaped corridors.
  4. Drop in an entrance, exit, a handful of monsters and loot.

Then renders the dungeon with Unicode box-drawing walls and ANSI colors.

Usage:
    python3 dungen.py                       # random 70x22 dungeon
    python3 dungen.py --seed 1337           # reproducible
    python3 dungen.py --width 100 --height 30
    python3 dungen.py --gallery             # 2x2 grid of dungeons
    python3 dungen.py --no-color            # plain ASCII
"""

from __future__ import annotations

import argparse
import random
import sys
from dataclasses import dataclass, field
from typing import Iterable

# ---- Tile glyphs ----------------------------------------------------------

FLOOR = "."
WALL = "#"          # replaced with box-drawing on render
CORRIDOR = ","
DOOR = "+"
ENTRANCE = ">"
EXIT = "<"
EMPTY = " "

MONSTERS = list("gokrbz")   # goblin, orc, kobold, rat, bat, zombie
LOOT = list("$!?*")         # gold, potion, scroll, gem


# ---- ANSI coloring --------------------------------------------------------

class Ink:
    """Tiny ANSI wrapper. Set .enabled = False to disable."""
    enabled = True

    RESET = "\x1b[0m"
    DIM = "\x1b[2m"
    BOLD = "\x1b[1m"

    @classmethod
    def c(cls, code: str, text: str) -> str:
        return f"{code}{text}{cls.RESET}" if cls.enabled else text

    # 256-color palette picks — muted, dungeon-y
    STONE = "\x1b[38;5;244m"
    FLOOR_C = "\x1b[38;5;137m"       # warm sand
    CORRIDOR_C = "\x1b[38;5;94m"     # dim brown
    DOOR_C = "\x1b[38;5;214m"        # amber
    ENTRANCE_C = "\x1b[38;5;118m"    # bright green
    EXIT_C = "\x1b[38;5;196m"        # red
    MONSTER_C = "\x1b[38;5;203m"     # salmon red
    LOOT_C = "\x1b[38;5;226m"        # gold


# ---- Data structures ------------------------------------------------------

@dataclass
class Rect:
    x: int
    y: int
    w: int
    h: int

    @property
    def x2(self) -> int: return self.x + self.w - 1
    @property
    def y2(self) -> int: return self.y + self.h - 1
    @property
    def cx(self) -> int: return self.x + self.w // 2
    @property
    def cy(self) -> int: return self.y + self.h // 2

    def cells(self) -> Iterable[tuple[int, int]]:
        for yy in range(self.y, self.y + self.h):
            for xx in range(self.x, self.x + self.w):
                yield xx, yy


@dataclass
class BSPNode:
    region: Rect
    left: "BSPNode | None" = None
    right: "BSPNode | None" = None
    room: Rect | None = None

    @property
    def is_leaf(self) -> bool:
        return self.left is None and self.right is None

    def leaves(self) -> Iterable["BSPNode"]:
        if self.is_leaf:
            yield self
        else:
            if self.left:
                yield from self.left.leaves()
            if self.right:
                yield from self.right.leaves()


# ---- Generation -----------------------------------------------------------

@dataclass
class DungeonConfig:
    width: int = 70
    height: int = 22
    min_leaf: int = 8        # minimum region size before splitting stops
    min_room: int = 4        # minimum room dimension
    room_padding: int = 1    # gap between room and region edge
    monster_rate: float = 0.6   # monsters per room (expected)
    loot_rate: float = 0.4
    seed: int | None = None


@dataclass
class Dungeon:
    cfg: DungeonConfig
    grid: list[list[str]] = field(default_factory=list)
    root: BSPNode | None = None
    entrance: tuple[int, int] | None = None
    exit: tuple[int, int] | None = None

    def __post_init__(self) -> None:
        self.grid = [[EMPTY for _ in range(self.cfg.width)]
                     for _ in range(self.cfg.height)]

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.cfg.width and 0 <= y < self.cfg.height

    def set(self, x: int, y: int, ch: str) -> None:
        if self.in_bounds(x, y):
            self.grid[y][x] = ch

    def get(self, x: int, y: int) -> str:
        return self.grid[y][x] if self.in_bounds(x, y) else EMPTY


def split_bsp(node: BSPNode, cfg: DungeonConfig, rng: random.Random) -> None:
    r = node.region
    # Decide whether to split further
    too_small = r.w < cfg.min_leaf * 2 and r.h < cfg.min_leaf * 2
    if too_small:
        return

    # Pick split direction biased toward the longer axis.
    if r.w > r.h * 1.25:
        horizontal = False
    elif r.h > r.w * 1.25:
        horizontal = True
    else:
        horizontal = rng.random() < 0.5

    if horizontal:
        if r.h < cfg.min_leaf * 2:
            return
        split = rng.randint(cfg.min_leaf, r.h - cfg.min_leaf)
        node.left = BSPNode(Rect(r.x, r.y, r.w, split))
        node.right = BSPNode(Rect(r.x, r.y + split, r.w, r.h - split))
    else:
        if r.w < cfg.min_leaf * 2:
            return
        split = rng.randint(cfg.min_leaf, r.w - cfg.min_leaf)
        node.left = BSPNode(Rect(r.x, r.y, split, r.h))
        node.right = BSPNode(Rect(r.x + split, r.y, r.w - split, r.h))

    split_bsp(node.left, cfg, rng)
    split_bsp(node.right, cfg, rng)


def place_rooms(node: BSPNode, cfg: DungeonConfig, rng: random.Random) -> None:
    if node.is_leaf:
        r = node.region
        pad = cfg.room_padding
        max_w = max(cfg.min_room, r.w - pad * 2)
        max_h = max(cfg.min_room, r.h - pad * 2)
        w = rng.randint(cfg.min_room, max_w)
        h = rng.randint(cfg.min_room, max_h)
        x = rng.randint(r.x + pad, r.x + r.w - w - pad)
        y = rng.randint(r.y + pad, r.y + r.h - h - pad)
        node.room = Rect(x, y, w, h)
        return
    if node.left:
        place_rooms(node.left, cfg, rng)
    if node.right:
        place_rooms(node.right, cfg, rng)


def pick_room(node: BSPNode, rng: random.Random) -> Rect:
    """Return a representative room from this subtree."""
    if node.room is not None:
        return node.room
    # Pick one side, fall back to the other if empty
    first, second = (node.left, node.right) if rng.random() < 0.5 else (node.right, node.left)
    for child in (first, second):
        if child is not None:
            return pick_room(child, rng)
    raise RuntimeError("BSP node has neither room nor children")


def carve_corridor(d: Dungeon, a: tuple[int, int], b: tuple[int, int],
                   rng: random.Random) -> None:
    """L-shaped corridor between two points. Writes CORRIDOR over EMPTY only."""
    ax, ay = a
    bx, by = b
    if rng.random() < 0.5:
        # horizontal first
        for x in range(min(ax, bx), max(ax, bx) + 1):
            if d.get(x, ay) == EMPTY:
                d.set(x, ay, CORRIDOR)
        for y in range(min(ay, by), max(ay, by) + 1):
            if d.get(bx, y) == EMPTY:
                d.set(bx, y, CORRIDOR)
    else:
        for y in range(min(ay, by), max(ay, by) + 1):
            if d.get(ax, y) == EMPTY:
                d.set(ax, y, CORRIDOR)
        for x in range(min(ax, bx), max(ax, bx) + 1):
            if d.get(x, by) == EMPTY:
                d.set(x, by, CORRIDOR)


def connect(node: BSPNode, d: Dungeon, rng: random.Random) -> None:
    if node.is_leaf or not node.left or not node.right:
        return
    connect(node.left, d, rng)
    connect(node.right, d, rng)
    a = pick_room(node.left, rng)
    b = pick_room(node.right, rng)
    carve_corridor(d, (a.cx, a.cy), (b.cx, b.cy), rng)


def stamp_rooms(node: BSPNode, d: Dungeon) -> None:
    for leaf in node.leaves():
        if leaf.room:
            for x, y in leaf.room.cells():
                d.set(x, y, FLOOR)


def add_walls(d: Dungeon) -> None:
    """Every empty cell adjacent to floor/corridor/door becomes a wall."""
    w, h = d.cfg.width, d.cfg.height
    walkable = {FLOOR, CORRIDOR, DOOR}
    new_walls: list[tuple[int, int]] = []
    for y in range(h):
        for x in range(w):
            if d.grid[y][x] != EMPTY:
                continue
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0:
                        continue
                    nx, ny = x + dx, y + dy
                    if d.in_bounds(nx, ny) and d.grid[ny][nx] in walkable:
                        new_walls.append((x, y))
                        break
                else:
                    continue
                break
    for x, y in new_walls:
        d.set(x, y, WALL)


def add_doors(d: Dungeon, rng: random.Random) -> None:
    """Place doors where a corridor punches through a wall into a room.

    A corridor tile is a true doorway only if:
      - a neighbor in direction (dx,dy) is room FLOOR, AND
      - the opposite neighbor is corridor/empty (we came from outside), AND
      - both perpendicular neighbors are WALLs (we're in a wall gap).

    This prevents stamping doors all along a corridor that happens to
    skirt a room's edge.
    """
    for y in range(1, d.cfg.height - 1):
        for x in range(1, d.cfg.width - 1):
            if d.grid[y][x] != CORRIDOR:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                if d.grid[y + dy][x + dx] != FLOOR:
                    continue
                opp = d.grid[y - dy][x - dx]
                if opp not in (CORRIDOR, EMPTY):
                    continue
                # Perpendicular neighbors must both be walls (true gap).
                px, py = -dy, dx  # rotate 90°
                left = d.grid[y + py][x + px] if d.in_bounds(x + px, y + py) else EMPTY
                right = d.grid[y - py][x - px] if d.in_bounds(x - px, y - py) else EMPTY
                if left == WALL and right == WALL:
                    if rng.random() < 0.85:
                        d.set(x, y, DOOR)
                    break


def far_apart_rooms(node: BSPNode) -> tuple[Rect, Rect]:
    rooms = [leaf.room for leaf in node.leaves() if leaf.room]
    assert len(rooms) >= 2
    best = (rooms[0], rooms[1])
    best_d = -1
    for i, a in enumerate(rooms):
        for b in rooms[i + 1:]:
            dx = a.cx - b.cx
            dy = a.cy - b.cy
            dist = dx * dx + dy * dy
            if dist > best_d:
                best_d = dist
                best = (a, b)
    return best


def populate(d: Dungeon, node: BSPNode, rng: random.Random) -> None:
    entrance_room, exit_room = far_apart_rooms(node)

    ex, ey = entrance_room.cx, entrance_room.cy
    d.set(ex, ey, ENTRANCE)
    d.entrance = (ex, ey)

    xx, xy = exit_room.cx, exit_room.cy
    d.set(xx, xy, EXIT)
    d.exit = (xx, xy)

    for leaf in node.leaves():
        room = leaf.room
        if not room:
            continue
        if room is entrance_room or room is exit_room:
            # still allow loot
            if rng.random() < d.cfg.loot_rate:
                place_in(d, room, rng, LOOT)
            continue
        if rng.random() < d.cfg.monster_rate:
            place_in(d, room, rng, MONSTERS)
        if rng.random() < d.cfg.loot_rate:
            place_in(d, room, rng, LOOT)


def place_in(d: Dungeon, room: Rect, rng: random.Random, pool: list[str]) -> None:
    # Try a few times to find a floor tile
    for _ in range(10):
        x = rng.randint(room.x, room.x + room.w - 1)
        y = rng.randint(room.y, room.y + room.h - 1)
        if d.grid[y][x] == FLOOR:
            d.set(x, y, rng.choice(pool))
            return


def generate(cfg: DungeonConfig) -> Dungeon:
    rng = random.Random(cfg.seed)
    d = Dungeon(cfg)
    d.root = BSPNode(Rect(0, 0, cfg.width, cfg.height))
    split_bsp(d.root, cfg, rng)
    place_rooms(d.root, cfg, rng)
    stamp_rooms(d.root, d)
    connect(d.root, d, rng)
    add_walls(d)
    add_doors(d, rng)
    populate(d, d.root, rng)
    return d


# ---- Rendering ------------------------------------------------------------

# Wall pieces keyed by (N, E, S, W) neighbor-is-wall bitmask.
# We map each 4-bit pattern to a box-drawing character.
WALL_GLYPHS = {
    0b0000: "·",  # isolated
    0b0001: "╴",  # W
    0b0010: "╷",  # S
    0b0011: "┐",  # S+W
    0b0100: "╶",  # E
    0b0101: "─",  # E+W
    0b0110: "┌",  # E+S
    0b0111: "┬",  # E+S+W
    0b1000: "╵",  # N
    0b1001: "┘",  # N+W
    0b1010: "│",  # N+S
    0b1011: "┤",  # N+S+W
    0b1100: "└",  # N+E
    0b1101: "┴",  # N+E+W
    0b1110: "├",  # N+E+S
    0b1111: "┼",  # all
}


def wall_glyph(d: Dungeon, x: int, y: int) -> str:
    def is_wall(nx: int, ny: int) -> bool:
        return d.in_bounds(nx, ny) and d.grid[ny][nx] == WALL

    n = is_wall(x, y - 1)
    e = is_wall(x + 1, y)
    s = is_wall(x, y + 1)
    w = is_wall(x - 1, y)
    mask = (int(n) << 3) | (int(e) << 2) | (int(s) << 1) | int(w)
    return WALL_GLYPHS[mask]


def render_rows(d: Dungeon) -> list[str]:
    rows: list[str] = []
    for y in range(d.cfg.height):
        buf: list[str] = []
        for x in range(d.cfg.width):
            ch = d.grid[y][x]
            if ch == EMPTY:
                buf.append(" ")
            elif ch == WALL:
                buf.append(Ink.c(Ink.STONE, wall_glyph(d, x, y)))
            elif ch == FLOOR:
                buf.append(Ink.c(Ink.FLOOR_C + Ink.DIM, "·"))
            elif ch == CORRIDOR:
                buf.append(Ink.c(Ink.CORRIDOR_C, "·"))
            elif ch == DOOR:
                buf.append(Ink.c(Ink.DOOR_C + Ink.BOLD, "+"))
            elif ch == ENTRANCE:
                buf.append(Ink.c(Ink.ENTRANCE_C + Ink.BOLD, ">"))
            elif ch == EXIT:
                buf.append(Ink.c(Ink.EXIT_C + Ink.BOLD, "<"))
            elif ch in MONSTERS:
                buf.append(Ink.c(Ink.MONSTER_C + Ink.BOLD, ch))
            elif ch in LOOT:
                buf.append(Ink.c(Ink.LOOT_C + Ink.BOLD, ch))
            else:
                buf.append(ch)
        rows.append("".join(buf))
    return rows


def render(d: Dungeon) -> str:
    return "\n".join(render_rows(d))


def render_gallery(cfgs: list[DungeonConfig], cols: int = 2) -> str:
    """Render multiple dungeons side-by-side in a grid."""
    rendered = [render_rows(generate(c)) for c in cfgs]
    gap = "  "
    lines: list[str] = []
    for i in range(0, len(rendered), cols):
        row = rendered[i:i + cols]
        max_h = max(len(r) for r in row)
        for y in range(max_h):
            pieces = []
            for panel in row:
                if y < len(panel):
                    pieces.append(panel[y])
                else:
                    # pad with spaces at the visual width of the panel
                    width = cfgs[0].width
                    pieces.append(" " * width)
            lines.append(gap.join(pieces))
        lines.append("")  # blank line between rows
    return "\n".join(lines)


# ---- Legend & stats -------------------------------------------------------

def legend() -> str:
    items = [
        (Ink.c(Ink.ENTRANCE_C + Ink.BOLD, ">"), "entrance"),
        (Ink.c(Ink.EXIT_C + Ink.BOLD, "<"), "exit"),
        (Ink.c(Ink.DOOR_C + Ink.BOLD, "+"), "door"),
        (Ink.c(Ink.MONSTER_C + Ink.BOLD, "g"), "monsters (gokrbz)"),
        (Ink.c(Ink.LOOT_C + Ink.BOLD, "$"), "loot ($!?*)"),
    ]
    return "  ".join(f"{g} {name}" for g, name in items)


def stats(d: Dungeon) -> str:
    rooms = sum(1 for leaf in d.root.leaves() if leaf.room) if d.root else 0
    floors = sum(row.count(FLOOR) for row in d.grid)
    corrs = sum(row.count(CORRIDOR) for row in d.grid)
    doors = sum(row.count(DOOR) for row in d.grid)
    monsters = sum(sum(1 for c in row if c in MONSTERS) for row in d.grid)
    loot = sum(sum(1 for c in row if c in LOOT) for row in d.grid)
    return (f"{rooms} rooms · {floors} floor · {corrs} corridor · "
            f"{doors} doors · {monsters} monsters · {loot} loot")


# ---- CLI ------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="dungen",
        description="Procedural dungeon generator (BSP) with Unicode rendering.",
    )
    p.add_argument("--width", type=int, default=70)
    p.add_argument("--height", type=int, default=22)
    p.add_argument("--seed", type=int, default=None,
                   help="Seed for reproducible dungeons")
    p.add_argument("--min-leaf", type=int, default=8,
                   help="Smallest BSP region before splitting stops")
    p.add_argument("--min-room", type=int, default=4,
                   help="Smallest room dimension")
    p.add_argument("--monsters", type=float, default=0.6,
                   help="Per-room probability of a monster")
    p.add_argument("--loot", type=float, default=0.4,
                   help="Per-room probability of loot")
    p.add_argument("--no-color", action="store_true",
                   help="Disable ANSI color output")
    p.add_argument("--gallery", action="store_true",
                   help="Render a 2x2 grid of four dungeons")
    p.add_argument("--no-legend", action="store_true",
                   help="Suppress the legend line")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.no_color or not sys.stdout.isatty():
        Ink.enabled = False

    cfg = DungeonConfig(
        width=args.width,
        height=args.height,
        min_leaf=args.min_leaf,
        min_room=args.min_room,
        monster_rate=args.monsters,
        loot_rate=args.loot,
        seed=args.seed,
    )

    if args.gallery:
        base = args.seed if args.seed is not None else random.randint(0, 10_000)
        cfgs = []
        for i in range(4):
            cfgs.append(DungeonConfig(
                width=cfg.width, height=cfg.height,
                min_leaf=cfg.min_leaf, min_room=cfg.min_room,
                monster_rate=cfg.monster_rate, loot_rate=cfg.loot_rate,
                seed=base + i,
            ))
        print(render_gallery(cfgs))
        if not args.no_legend:
            print(legend())
            print(f"gallery seeds: {base}..{base + 3}")
        return 0

    d = generate(cfg)
    print(render(d))
    if not args.no_legend:
        print(legend())
        print(stats(d) + (f"  seed={cfg.seed}" if cfg.seed is not None else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
