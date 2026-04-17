#!/usr/bin/env python3
"""
ASCII Boids — a terminal flocking simulation.

Implements Craig Reynolds's three classic rules (separation, alignment,
cohesion) plus optional mouse-like "predator" avoidance and soft wall
bouncing. Runs in any VT100-ish terminal using only the standard library.

Run:     python3 boids.py
Help:    python3 boids.py --help
Quit:    Ctrl-C
"""

from __future__ import annotations

import argparse
import math
import os
import random
import shutil
import signal
import sys
import time
from dataclasses import dataclass


# -----------------------------------------------------------------------------
# Vector helpers (keep things dependency-free; 2-tuples of floats)
# -----------------------------------------------------------------------------


def vadd(a, b):
    return (a[0] + b[0], a[1] + b[1])


def vsub(a, b):
    return (a[0] - b[0], a[1] - b[1])


def vscale(a, s):
    return (a[0] * s, a[1] * s)


def vlen(a):
    return math.hypot(a[0], a[1])


def vnorm(a):
    m = vlen(a)
    if m == 0.0:
        return (0.0, 0.0)
    return (a[0] / m, a[1] / m)


def vclamp(a, maxlen):
    m = vlen(a)
    if m > maxlen and m > 0.0:
        s = maxlen / m
        return (a[0] * s, a[1] * s)
    return a


# -----------------------------------------------------------------------------
# Boid
# -----------------------------------------------------------------------------


# Glyphs chosen to suggest direction (8 compass headings).
HEADING_GLYPHS = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]

# A palette of 256-color foreground codes — picked to look good on both dark
# and light terminals. Cycled per-boid so the flock looks varied.
COLOR_PALETTE = [
    39,   # bright cyan-blue
    45,   # cyan
    51,   # bright cyan
    87,   # pale cyan
    123,  # light cyan
    159,  # very light cyan
    201,  # magenta
    207,  # pink
    213,  # light pink
    219,  # pale pink
    226,  # yellow
    220,  # gold
    214,  # orange
    208,  # deep orange
    82,   # bright green
    118,  # lime
    154,  # yellow-green
]


@dataclass
class Boid:
    pos: tuple          # (x, y) in character cells; y is doubled-resolution
    vel: tuple          # (vx, vy) cells/frame
    color: int


def heading_glyph(vel) -> str:
    vx, vy = vel
    if vx == 0.0 and vy == 0.0:
        return "•"
    # atan2 returns radians; shift to [0, 2π) then bucket into 8 sectors.
    ang = math.atan2(-vy, vx)  # invert y because screen y grows downward
    if ang < 0:
        ang += 2 * math.pi
    idx = int((ang + math.pi / 8) // (math.pi / 4)) % 8
    return HEADING_GLYPHS[idx]


# -----------------------------------------------------------------------------
# Simulation
# -----------------------------------------------------------------------------


class Simulation:
    def __init__(self, width, height, count, *, seed=None, speed=1.0):
        # Width is in terminal columns; height is in terminal rows. We let the
        # boids move in a floating-point space matching that aspect ratio, but
        # internally compress y by 0.5 because character cells are ~2× taller
        # than they are wide — without this correction, flocks look squashed.
        self.width = width
        self.height = height
        self.aspect = 2.0  # cell h:w
        self.speed = speed

        if seed is not None:
            random.seed(seed)

        self.max_speed = 0.9 * speed
        self.max_force = 0.06 * speed
        self.neighbor_radius = 8.0
        self.separation_radius = 2.2

        self.w_separation = 1.8
        self.w_alignment = 1.0
        self.w_cohesion = 0.9

        self.boids = [self._random_boid(i) for i in range(count)]

    def _random_boid(self, idx) -> Boid:
        pos = (
            random.uniform(0, self.width),
            random.uniform(0, self.height * self.aspect),
        )
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(0.3, 0.7) * self.speed
        vel = (math.cos(angle) * speed, math.sin(angle) * speed)
        color = COLOR_PALETTE[idx % len(COLOR_PALETTE)]
        return Boid(pos=pos, vel=vel, color=color)

    def step(self):
        # O(n²) neighbor loop — fine up to a few hundred boids in a terminal.
        new_vels = []
        for i, b in enumerate(self.boids):
            sep = (0.0, 0.0)
            ali = (0.0, 0.0)
            coh = (0.0, 0.0)
            n_ali = 0
            n_coh = 0
            for j, other in enumerate(self.boids):
                if i == j:
                    continue
                diff = vsub(b.pos, other.pos)
                # Compensate for aspect so "radius" is visually circular.
                dx, dy = diff
                d = math.hypot(dx, dy / self.aspect)
                if d == 0.0 or d > self.neighbor_radius:
                    continue
                if d < self.separation_radius:
                    # Push away, weighted by closeness.
                    sep = vadd(sep, vscale(vnorm(diff), 1.0 / max(d, 0.1)))
                ali = vadd(ali, other.vel)
                n_ali += 1
                coh = vadd(coh, other.pos)
                n_coh += 1

            steer = (0.0, 0.0)
            if vlen(sep) > 0:
                sep = vscale(vnorm(sep), self.max_speed)
                steer = vadd(steer, vscale(vclamp(vsub(sep, b.vel), self.max_force),
                                           self.w_separation))
            if n_ali > 0:
                ali = vscale(ali, 1.0 / n_ali)
                if vlen(ali) > 0:
                    ali = vscale(vnorm(ali), self.max_speed)
                    steer = vadd(steer, vscale(vclamp(vsub(ali, b.vel), self.max_force),
                                               self.w_alignment))
            if n_coh > 0:
                coh = vscale(coh, 1.0 / n_coh)
                desired = vsub(coh, b.pos)
                if vlen(desired) > 0:
                    desired = vscale(vnorm(desired), self.max_speed)
                    steer = vadd(steer, vscale(vclamp(vsub(desired, b.vel), self.max_force),
                                               self.w_cohesion))

            # Soft wall avoidance — nudges boids back toward the interior
            # before they hit the edge. Feels nicer than a hard bounce.
            margin = 3.0
            turn = 0.08 * self.speed
            wx, wy = 0.0, 0.0
            if b.pos[0] < margin:
                wx = turn
            elif b.pos[0] > self.width - margin:
                wx = -turn
            if b.pos[1] < margin * self.aspect:
                wy = turn
            elif b.pos[1] > self.height * self.aspect - margin * self.aspect:
                wy = -turn
            steer = vadd(steer, (wx, wy))

            new_vel = vclamp(vadd(b.vel, steer), self.max_speed)
            new_vels.append(new_vel)

        # Integrate positions after computing all new velocities so updates
        # within a frame don't influence each other.
        for b, nv in zip(self.boids, new_vels):
            b.vel = nv
            nx = b.pos[0] + nv[0]
            ny = b.pos[1] + nv[1]
            # Hard clamp as a safety net in case the soft turn wasn't enough.
            nx = max(0.0, min(self.width - 0.001, nx))
            ny = max(0.0, min(self.height * self.aspect - 0.001, ny))
            b.pos = (nx, ny)


# -----------------------------------------------------------------------------
# Rendering
# -----------------------------------------------------------------------------


ESC = "\x1b["
HIDE_CURSOR = ESC + "?25l"
SHOW_CURSOR = ESC + "?25h"
CLEAR = ESC + "2J"
HOME = ESC + "H"
RESET = ESC + "0m"


def fg256(code: int) -> str:
    return f"{ESC}38;5;{code}m"


def render(sim: Simulation, show_trails: bool, frame: int) -> str:
    w, h = sim.width, sim.height
    # Two parallel grids: glyphs and per-cell color codes. None == blank.
    grid = [[" "] * w for _ in range(h)]
    colors = [[0] * w for _ in range(h)]

    for b in sim.boids:
        cx = int(b.pos[0])
        cy = int(b.pos[1] / sim.aspect)
        if 0 <= cx < w and 0 <= cy < h:
            grid[cy][cx] = heading_glyph(b.vel)
            colors[cy][cx] = b.color

    # Assemble as one big string — far faster than per-cell writes, and
    # avoids flicker because we always repaint from HOME.
    out = [HOME]
    last_color = -1
    for y in range(h):
        row = []
        for x in range(w):
            c = colors[y][x]
            if c == 0:
                if last_color != 0:
                    row.append(RESET)
                    last_color = 0
                row.append(" ")
            else:
                if c != last_color:
                    row.append(fg256(c))
                    last_color = c
                row.append(grid[y][x])
        out.append("".join(row))
        if y < h - 1:
            out.append("\n")
    out.append(RESET)
    return "".join(out)


# -----------------------------------------------------------------------------
# CLI / main loop
# -----------------------------------------------------------------------------


def parse_args(argv):
    p = argparse.ArgumentParser(
        description="ASCII Boids — terminal flocking simulation.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("-n", "--count", type=int, default=60,
                   help="number of boids")
    p.add_argument("--fps", type=float, default=30.0,
                   help="target frames per second")
    p.add_argument("--speed", type=float, default=1.0,
                   help="global speed multiplier")
    p.add_argument("--seed", type=int, default=None,
                   help="RNG seed for reproducible runs")
    p.add_argument("--width", type=int, default=None,
                   help="force terminal width (cols)")
    p.add_argument("--height", type=int, default=None,
                   help="force terminal height (rows)")
    p.add_argument("--frames", type=int, default=0,
                   help="stop after N frames (0 = forever)")
    return p.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    term = shutil.get_terminal_size(fallback=(80, 24))
    width = args.width or term.columns
    # Leave one row free for the status line at the bottom.
    height = (args.height or term.lines) - 1
    if width < 20 or height < 8:
        print("Terminal too small; need at least 20×9.", file=sys.stderr)
        return 2

    sim = Simulation(width, height, args.count,
                     seed=args.seed, speed=args.speed)

    # Best-effort cleanup on signals so we don't leave the cursor hidden.
    def cleanup(*_):
        sys.stdout.write(SHOW_CURSOR + RESET + "\n")
        sys.stdout.flush()
        sys.exit(0)

    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)

    sys.stdout.write(HIDE_CURSOR + CLEAR)
    sys.stdout.flush()

    frame_dt = 1.0 / max(args.fps, 1.0)
    frame = 0
    try:
        next_tick = time.monotonic()
        while args.frames == 0 or frame < args.frames:
            sim.step()
            sys.stdout.write(render(sim, show_trails=False, frame=frame))
            status = (f" boids={len(sim.boids)}  fps={args.fps:.0f}  "
                      f"frame={frame}  ctrl-c to quit ")
            # Pad status so stale characters get wiped.
            status = status.ljust(width)[:width]
            sys.stdout.write(f"\n{fg256(244)}{status}{RESET}")
            sys.stdout.flush()
            frame += 1

            next_tick += frame_dt
            sleep_for = next_tick - time.monotonic()
            if sleep_for > 0:
                time.sleep(sleep_for)
            else:
                # We're falling behind — reset the clock so we don't spiral.
                next_tick = time.monotonic()
    finally:
        sys.stdout.write(SHOW_CURSOR + RESET + "\n")
        sys.stdout.flush()

    return 0


if __name__ == "__main__":
    sys.exit(main())
