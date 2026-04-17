#!/usr/bin/env python3
"""Terminal Boids — Reynolds' flocking simulation in ASCII.

Three rules drive each boid's steering:
  separation  — veer away from neighbors that are too close
  alignment   — match the average heading of nearby boids
  cohesion    — drift toward the center of mass of nearby boids

Run:  python3 boids.py            (default: 60 boids)
      python3 boids.py -n 120     (more boids)
      python3 boids.py --help
Quit: q or Ctrl-C.
"""

import argparse
import curses
import math
import random
import time
from dataclasses import dataclass

# 8-way arrows for boid headings (index = round(angle / 45) mod 8).
# Order: E, NE, N, NW, W, SW, S, SE  (mathematical angle, y-up).
HEADING_GLYPHS = ["»", "◢", "▲", "◣", "«", "◣", "▼", "◢"]
# Better visual set: directional triangles.
HEADING_GLYPHS = ["▶", "◥", "▲", "◤", "◀", "◣", "▼", "◢"]


@dataclass
class Boid:
    x: float
    y: float
    vx: float
    vy: float

    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def glyph(self) -> str:
        angle = math.atan2(-self.vy, self.vx)  # y-up for direction picking
        idx = int(round(angle / (math.pi / 4))) % 8
        return HEADING_GLYPHS[idx]


class Flock:
    def __init__(self, n: int, w: int, h: int, *, seed: int | None = None):
        self.w = w
        self.h = h
        rng = random.Random(seed)
        self.boids: list[Boid] = []
        for _ in range(n):
            angle = rng.uniform(0, 2 * math.pi)
            speed = rng.uniform(0.4, 0.8)
            self.boids.append(
                Boid(
                    x=rng.uniform(0, w),
                    y=rng.uniform(0, h),
                    vx=math.cos(angle) * speed,
                    vy=math.sin(angle) * speed,
                )
            )

        # Tunables. Terminals are wider than tall (~2:1 char aspect),
        # so we treat x distance as half-weight when measuring neighbors
        # to keep flocks visually round rather than horizontally stretched.
        self.neighbor_radius = 6.0
        self.separation_radius = 2.0
        self.max_speed = 0.9
        self.min_speed = 0.35
        self.w_sep = 0.06
        self.w_ali = 0.04
        self.w_coh = 0.008

    def _wrap_delta(self, a: float, b: float, span: float) -> float:
        d = a - b
        if d > span / 2:
            d -= span
        elif d < -span / 2:
            d += span
        return d

    def step(self) -> None:
        new_v: list[tuple[float, float]] = []
        for i, b in enumerate(self.boids):
            sep_x = sep_y = 0.0
            ali_x = ali_y = 0.0
            coh_x = coh_y = 0.0
            n_neigh = 0

            for j, other in enumerate(self.boids):
                if i == j:
                    continue
                dx = self._wrap_delta(other.x, b.x, self.w)
                dy = self._wrap_delta(other.y, b.y, self.h)
                # Distance with terminal aspect correction (x half-weight).
                d2 = (dx * 0.5) ** 2 + dy ** 2
                if d2 > self.neighbor_radius ** 2:
                    continue
                d = math.sqrt(d2) or 1e-6
                if d < self.separation_radius:
                    # Push away, stronger as we get closer.
                    sep_x -= dx / d
                    sep_y -= dy / d
                ali_x += other.vx
                ali_y += other.vy
                coh_x += dx
                coh_y += dy
                n_neigh += 1

            vx, vy = b.vx, b.vy
            if n_neigh:
                ali_x /= n_neigh
                ali_y /= n_neigh
                coh_x /= n_neigh
                coh_y /= n_neigh
                vx += self.w_sep * sep_x
                vy += self.w_sep * sep_y
                vx += self.w_ali * (ali_x - b.vx)
                vy += self.w_ali * (ali_y - b.vy)
                vx += self.w_coh * coh_x
                vy += self.w_coh * coh_y

            speed = math.hypot(vx, vy)
            if speed > self.max_speed:
                vx *= self.max_speed / speed
                vy *= self.max_speed / speed
            elif speed < self.min_speed:
                if speed < 1e-6:
                    angle = random.uniform(0, 2 * math.pi)
                    vx, vy = math.cos(angle) * self.min_speed, math.sin(angle) * self.min_speed
                else:
                    vx *= self.min_speed / speed
                    vy *= self.min_speed / speed
            new_v.append((vx, vy))

        for b, (vx, vy) in zip(self.boids, new_v):
            b.vx, b.vy = vx, vy
            b.x = (b.x + vx) % self.w
            b.y = (b.y + vy) % self.h


def run(stdscr, args: argparse.Namespace) -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(0)
    if curses.has_colors():
        curses.start_color()
        curses.use_default_colors()
        # Cycle a few colors so dense flocks look layered.
        for i, c in enumerate(
            [curses.COLOR_CYAN, curses.COLOR_GREEN, curses.COLOR_YELLOW, curses.COLOR_MAGENTA]
        ):
            curses.init_pair(i + 1, c, -1)

    h, w = stdscr.getmaxyx()
    # Reserve bottom row for status.
    sim_h = max(5, h - 1)
    sim_w = max(10, w - 1)

    flock = Flock(args.n, sim_w, sim_h, seed=args.seed)

    target_dt = 1.0 / max(1, args.fps)
    paused = False
    frame = 0
    t_start = time.perf_counter()

    while True:
        t0 = time.perf_counter()

        # Handle input.
        try:
            ch = stdscr.getch()
        except curses.error:
            ch = -1
        if ch != -1:
            if ch in (ord("q"), 27):  # q or Esc
                return
            if ch == ord(" "):
                paused = not paused
            elif ch == ord("+") or ch == ord("="):
                flock.boids.append(_random_boid(sim_w, sim_h))
            elif ch == ord("-") and flock.boids:
                flock.boids.pop()
            elif ch == ord("r"):
                flock = Flock(len(flock.boids), sim_w, sim_h)

        # React to terminal resize.
        nh, nw = stdscr.getmaxyx()
        if (nh, nw) != (h, w):
            h, w = nh, nw
            sim_h = max(5, h - 1)
            sim_w = max(10, w - 1)
            flock.w, flock.h = sim_w, sim_h
            for b in flock.boids:
                b.x %= sim_w
                b.y %= sim_h

        if not paused:
            flock.step()
            frame += 1

        # Render.
        stdscr.erase()
        for b in flock.boids:
            x = int(b.x)
            y = int(b.y)
            if 0 <= x < sim_w and 0 <= y < sim_h:
                attr = 0
                if curses.has_colors():
                    # Color by heading bucket so direction changes are visible.
                    angle = math.atan2(-b.vy, b.vx)
                    bucket = int(round(angle / (math.pi / 4))) % 8
                    attr = curses.color_pair((bucket % 4) + 1)
                try:
                    stdscr.addstr(y, x, b.glyph(), attr)
                except curses.error:
                    pass

        elapsed = time.perf_counter() - t_start
        fps = frame / elapsed if elapsed > 0 else 0.0
        status = (
            f" boids={len(flock.boids):4d}  fps={fps:5.1f}  "
            f"{'PAUSED' if paused else 'RUNNING'}  "
            f"[space pause | +/- add/remove | r reset | q quit] "
        )
        try:
            stdscr.addnstr(h - 1, 0, status, w - 1, curses.A_REVERSE)
        except curses.error:
            pass
        stdscr.refresh()

        # Frame pacing.
        dt = time.perf_counter() - t0
        if dt < target_dt:
            time.sleep(target_dt - dt)


def _random_boid(w: int, h: int) -> Boid:
    angle = random.uniform(0, 2 * math.pi)
    speed = random.uniform(0.4, 0.8)
    return Boid(
        x=random.uniform(0, w),
        y=random.uniform(0, h),
        vx=math.cos(angle) * speed,
        vy=math.sin(angle) * speed,
    )


def main() -> None:
    p = argparse.ArgumentParser(description="Terminal Boids — flocking in ASCII.")
    p.add_argument("-n", type=int, default=60, help="number of boids (default: 60)")
    p.add_argument("--fps", type=int, default=30, help="target frames/sec (default: 30)")
    p.add_argument("--seed", type=int, default=None, help="random seed for reproducibility")
    args = p.parse_args()
    if args.n < 1:
        p.error("-n must be >= 1")
    try:
        curses.wrapper(run, args)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
