"""Terminal boids flocking simulation.

Reynolds' three rules (separation, alignment, cohesion) with a user-controlled
predator. Arrow keys or h/j/k/l move the hawk; r resets; q quits. Space toggles
trails.
"""

from __future__ import annotations

import curses
import math
import random
import time
from dataclasses import dataclass


# Directional glyphs picked by the angle of the velocity vector.
# 8 sectors of 45 degrees starting from east going counter-clockwise.
DIR_GLYPHS = ["►", "◥", "▲", "◤", "◄", "◣", "▼", "◢"]

NUM_BOIDS = 80
MAX_SPEED = 1.4
MIN_SPEED = 0.3
NEIGHBOR_R = 6.0
SEPARATION_R = 1.8
PREDATOR_R = 10.0
W_SEP = 0.9
W_ALI = 0.08
W_COH = 0.006
W_FLEE = 0.35
FRAME_DT = 1.0 / 30.0


@dataclass
class Boid:
    x: float
    y: float
    vx: float
    vy: float

    def glyph(self) -> str:
        angle = math.atan2(-self.vy, self.vx)  # screen y grows downward
        sector = int(round((angle + math.pi) / (math.pi / 4))) % 8
        # Rotate so east=0 corresponds to ► (which is DIR_GLYPHS[0]).
        return DIR_GLYPHS[(sector + 4) % 8]


def clamp_speed(vx: float, vy: float) -> tuple[float, float]:
    s = math.hypot(vx, vy)
    if s > MAX_SPEED:
        k = MAX_SPEED / s
        return vx * k, vy * k
    if s < MIN_SPEED and s > 0:
        k = MIN_SPEED / s
        return vx * k, vy * k
    if s == 0:
        return MIN_SPEED, 0.0
    return vx, vy


def wrap(v: float, hi: float) -> float:
    if v < 0:
        return v + hi
    if v >= hi:
        return v - hi
    return v


def toroidal_delta(a: float, b: float, hi: float) -> float:
    d = a - b
    if d > hi / 2:
        d -= hi
    elif d < -hi / 2:
        d += hi
    return d


def step(boids: list[Boid], W: float, H: float, hawk: tuple[float, float] | None) -> None:
    new_vels: list[tuple[float, float]] = []
    for b in boids:
        sep_x = sep_y = 0.0
        ali_x = ali_y = 0.0
        coh_x = coh_y = 0.0
        n = 0
        for o in boids:
            if o is b:
                continue
            dx = toroidal_delta(o.x, b.x, W)
            dy = toroidal_delta(o.y, b.y, H)
            d2 = dx * dx + dy * dy
            if d2 > NEIGHBOR_R * NEIGHBOR_R:
                continue
            n += 1
            ali_x += o.vx
            ali_y += o.vy
            coh_x += dx
            coh_y += dy
            if d2 < SEPARATION_R * SEPARATION_R and d2 > 0:
                sep_x -= dx / d2
                sep_y -= dy / d2

        vx, vy = b.vx, b.vy
        if n:
            ali_x = ali_x / n - b.vx
            ali_y = ali_y / n - b.vy
            coh_x /= n
            coh_y /= n
            vx += W_SEP * sep_x + W_ALI * ali_x + W_COH * coh_x
            vy += W_SEP * sep_y + W_ALI * ali_y + W_COH * coh_y

        if hawk is not None:
            hdx = toroidal_delta(b.x, hawk[0], W)
            hdy = toroidal_delta(b.y, hawk[1], H)
            hd2 = hdx * hdx + hdy * hdy
            if 0 < hd2 < PREDATOR_R * PREDATOR_R:
                vx += W_FLEE * hdx / math.sqrt(hd2)
                vy += W_FLEE * hdy / math.sqrt(hd2)

        vx, vy = clamp_speed(vx, vy)
        new_vels.append((vx, vy))

    for b, (vx, vy) in zip(boids, new_vels):
        b.vx, b.vy = vx, vy
        b.x = wrap(b.x + vx, W)
        b.y = wrap(b.y + vy, H)


def spawn(W: float, H: float) -> list[Boid]:
    boids = []
    for _ in range(NUM_BOIDS):
        a = random.uniform(0, 2 * math.pi)
        s = random.uniform(MIN_SPEED, MAX_SPEED)
        boids.append(Boid(
            x=random.uniform(0, W),
            y=random.uniform(0, H),
            vx=math.cos(a) * s,
            vy=math.sin(a) * s,
        ))
    return boids


def run(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        for i, fg in enumerate([curses.COLOR_CYAN, curses.COLOR_GREEN,
                                curses.COLOR_YELLOW, curses.COLOR_MAGENTA,
                                curses.COLOR_WHITE, curses.COLOR_RED]):
            curses.init_pair(i + 1, fg, -1)

    H, W = stdscr.getmaxyx()
    world_w, world_h = float(W - 1), float(H - 1)
    boids = spawn(world_w, world_h)
    hawk_x, hawk_y = world_w / 2, world_h / 2
    hawk_active = False
    trails = False
    last = time.time()

    while True:
        # Handle input (drain all pending keys per frame).
        while True:
            c = stdscr.getch()
            if c == -1:
                break
            if c in (ord("q"), 27):
                return
            if c == ord("r"):
                boids = spawn(world_w, world_h)
            elif c == ord(" "):
                trails = not trails
            elif c in (curses.KEY_LEFT, ord("h")):
                hawk_x = wrap(hawk_x - 2, world_w); hawk_active = True
            elif c in (curses.KEY_RIGHT, ord("l")):
                hawk_x = wrap(hawk_x + 2, world_w); hawk_active = True
            elif c in (curses.KEY_UP, ord("k")):
                hawk_y = wrap(hawk_y - 1, world_h); hawk_active = True
            elif c in (curses.KEY_DOWN, ord("j")):
                hawk_y = wrap(hawk_y + 1, world_h); hawk_active = True
            elif c == ord("x"):
                hawk_active = False

        # Handle resize.
        new_h, new_w = stdscr.getmaxyx()
        if (new_h, new_w) != (H, W):
            H, W = new_h, new_w
            world_w, world_h = float(W - 1), float(H - 1)
            for b in boids:
                b.x = min(b.x, world_w - 0.01)
                b.y = min(b.y, world_h - 0.01)
            hawk_x = min(hawk_x, world_w - 0.01)
            hawk_y = min(hawk_y, world_h - 0.01)

        step(boids, world_w, world_h, (hawk_x, hawk_y) if hawk_active else None)

        if not trails:
            stdscr.erase()

        for b in boids:
            xi, yi = int(b.x), int(b.y)
            if 0 <= xi < W and 0 <= yi < H - 1:
                speed = math.hypot(b.vx, b.vy)
                pair = 1 if speed < 0.7 else 2 if speed < 1.1 else 3
                try:
                    stdscr.addstr(yi, xi, b.glyph(), curses.color_pair(pair))
                except curses.error:
                    pass

        if hawk_active:
            hx, hy = int(hawk_x), int(hawk_y)
            if 0 <= hx < W and 0 <= hy < H - 1:
                try:
                    stdscr.addstr(hy, hx, "✦",
                                  curses.color_pair(6) | curses.A_BOLD)
                except curses.error:
                    pass

        status = (
            f" boids:{len(boids)}  hawk:{'on' if hawk_active else 'off'}  "
            f"trails:{'on' if trails else 'off'}  "
            "[arrows/hjkl: hawk] [x: stow] [space: trails] [r: reset] [q: quit]"
        )
        try:
            stdscr.addstr(H - 1, 0, status[: W - 1].ljust(W - 1),
                          curses.color_pair(5) | curses.A_REVERSE)
        except curses.error:
            pass

        stdscr.refresh()

        now = time.time()
        sleep = FRAME_DT - (now - last)
        if sleep > 0:
            time.sleep(sleep)
        last = time.time()


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
