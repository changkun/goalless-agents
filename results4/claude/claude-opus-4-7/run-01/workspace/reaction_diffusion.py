#!/usr/bin/env python3
"""
Gray-Scott reaction-diffusion simulator for the terminal.

Two virtual chemicals U and V react and diffuse on a toroidal grid:

    dU/dt =  Du * Laplacian(U) - U*V*V + F*(1 - U)
    dV/dt =  Dv * Laplacian(V) + U*V*V - (F + k)*V

Tiny parameter tweaks produce dramatically different emergent patterns:
spots, stripes, waves, coral-like growth, dividing "cells" (mitosis),
turbulent chaos. This implementation renders V to the terminal using
ANSI 24-bit color and the upper-half-block character so each text row
shows two rows of the simulation grid.

Controls (while running):
    space    pause / resume
    r        reseed the grid with the current preset
    n / p    next / previous preset
    1..8     jump to preset N
    +/-      increase / decrease simulation steps per frame
    q        quit

Run:
    python3 reaction_diffusion.py [preset]

No third-party dependencies — pure stdlib.
"""

from __future__ import annotations

import array
import math
import os
import random
import select
import signal
import sys
import termios
import time
import tty

# -----------------------------------------------------------------------------
# Presets.  (Du, Dv) are diffusion coefficients; (F, k) are feed / kill rates.
# Du and Dv are fixed across classic Gray-Scott; F and k pick the regime.
# -----------------------------------------------------------------------------
PRESETS = [
    ("coral",    0.0545, 0.062),   # branching coral-like growth
    ("spots",    0.0367, 0.0649),  # self-replicating spots
    ("mitosis",  0.0367, 0.0649),  # same regime, different seed -> division
    ("stripes",  0.022,  0.051),   # labyrinthine stripes
    ("waves",    0.014,  0.045),   # traveling spiral waves
    ("zebra",    0.035,  0.060),   # thick zebra bands
    ("pulsate",  0.025,  0.0547),  # breathing, pulsing blobs
    ("chaos",    0.026,  0.051),   # turbulent, ever-changing
]

DU = 0.16
DV = 0.08
DT = 1.0

# -----------------------------------------------------------------------------
# Grid and simulation
# -----------------------------------------------------------------------------

class Field:
    """A pair of concentration grids updated in lockstep."""

    __slots__ = ("w", "h", "u", "v", "u2", "v2", "_xl", "_xr", "_yu", "_yd")

    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        size = w * h
        self.u = array.array("d", [1.0]) * size
        self.v = array.array("d", [0.0]) * size
        self.u2 = array.array("d", [0.0]) * size
        self.v2 = array.array("d", [0.0]) * size
        # Precomputed wrapped-neighbor tables to avoid % in the hot loop.
        self._xl = array.array("i", [(x - 1) % w for x in range(w)])
        self._xr = array.array("i", [(x + 1) % w for x in range(w)])
        self._yu = array.array("i", [((y - 1) % h) * w for y in range(h)])
        self._yd = array.array("i", [((y + 1) % h) * w for y in range(h)])

    def seed(self, kind: str) -> None:
        """Reset to a uniform U=1, V=0 state then inject perturbations."""
        w, h = self.w, self.h
        u, v = self.u, self.v
        for i in range(w * h):
            u[i] = 1.0
            v[i] = 0.0

        rng = random.Random()

        if kind == "mitosis":
            # one small dense square -- will split and split again
            cx, cy = w // 2, h // 2
            for dy in range(-3, 4):
                for dx in range(-3, 4):
                    x = (cx + dx) % w
                    y = (cy + dy) % h
                    idx = y * w + x
                    u[idx] = 0.5
                    v[idx] = 0.25
        elif kind == "waves":
            # a single off-center blob tends to spawn spirals
            cx, cy = w // 3, h // 2
            for dy in range(-4, 5):
                for dx in range(-4, 5):
                    if dx * dx + dy * dy <= 16:
                        x = (cx + dx) % w
                        y = (cy + dy) % h
                        idx = y * w + x
                        u[idx] = 0.5
                        v[idx] = 0.25
        elif kind == "stripes" or kind == "zebra":
            # a horizontal strip seeds parallel bands
            cy = h // 2
            for dy in range(-2, 3):
                for x in range(w):
                    y = (cy + dy) % h
                    idx = y * w + x
                    u[idx] = 0.5
                    v[idx] = 0.25
        else:
            # scatter several patches -- generic good seed
            patches = 7
            for _ in range(patches):
                cx = rng.randrange(w)
                cy = rng.randrange(h)
                r = rng.randint(3, 6)
                r2 = r * r
                for dy in range(-r, r + 1):
                    for dx in range(-r, r + 1):
                        if dx * dx + dy * dy <= r2:
                            x = (cx + dx) % w
                            y = (cy + dy) % h
                            idx = y * w + x
                            u[idx] = 0.5
                            v[idx] = 0.25

        # add a little noise everywhere so chaotic regimes don't stay
        # perfectly symmetric forever
        for i in range(w * h):
            u[i] += (rng.random() - 0.5) * 0.02
            v[i] += (rng.random() - 0.5) * 0.02
            if v[i] < 0.0:
                v[i] = 0.0

    def step(self, F: float, k: float) -> None:
        """Advance the simulation by one Euler step with toroidal boundaries."""
        w, h = self.w, self.h
        u, v = self.u, self.v
        u2, v2 = self.u2, self.v2
        du, dv, dt = DU, DV, DT
        xl_tbl = self._xl; xr_tbl = self._xr
        yu_tbl = self._yu; yd_tbl = self._yd
        Fk = F + k  # hoist the constant combination

        for y in range(h):
            row = y * w
            up = yu_tbl[y]
            dn = yd_tbl[y]
            for x in range(w):
                c = row + x
                lxl = row + xl_tbl[x]
                lxr = row + xr_tbl[x]
                uxc = up + x
                dxc = dn + x
                uc = u[c]; vc = v[c]
                # 5-point Laplacian, neighbors/4 - center.
                lu = (u[lxl] + u[lxr] + u[uxc] + u[dxc]) * 0.25 - uc
                lv = (v[lxl] + v[lxr] + v[uxc] + v[dxc]) * 0.25 - vc
                uvv = uc * vc * vc
                u2[c] = uc + (du * lu - uvv + F * (1.0 - uc)) * dt
                v2[c] = vc + (dv * lv + uvv - Fk * vc) * dt

        # Swap buffers.
        self.u, self.u2 = self.u2, self.u
        self.v, self.v2 = self.v2, self.v


# -----------------------------------------------------------------------------
# Rendering: map V in [0, ~0.4] -> ANSI 24-bit color + half-block row pairs
# -----------------------------------------------------------------------------

# A perceptually-nice gradient from deep indigo through magenta/orange to
# bright yellow; V=0 is black so the "background" fluid fades out.
_PALETTE_STOPS = [
    (0.00, (0,   0,   0)),
    (0.08, (20,  10,  60)),
    (0.20, (90,  20, 120)),
    (0.35, (200, 40,  80)),
    (0.55, (240, 120, 30)),
    (0.80, (255, 220, 60)),
    (1.00, (255, 255, 220)),
]


def _color(t: float) -> tuple[int, int, int]:
    if t <= 0.0:
        return _PALETTE_STOPS[0][1]
    if t >= 1.0:
        return _PALETTE_STOPS[-1][1]
    for i in range(1, len(_PALETTE_STOPS)):
        t1, c1 = _PALETTE_STOPS[i]
        if t <= t1:
            t0, c0 = _PALETTE_STOPS[i - 1]
            f = (t - t0) / (t1 - t0)
            return (
                int(c0[0] + (c1[0] - c0[0]) * f),
                int(c0[1] + (c1[1] - c0[1]) * f),
                int(c0[2] + (c1[2] - c0[2]) * f),
            )
    return _PALETTE_STOPS[-1][1]


def render(field: Field, out: list) -> str:
    """Build the frame string.  Uses ▀ (upper half block) so one text row
    encodes two grid rows: foreground = top, background = bottom."""
    w, h = field.w, field.h
    v = field.v
    out.clear()
    out.append("\x1b[H")  # cursor home (no clear => no flicker)

    # iterate rows in pairs
    # V values live roughly in [0, 0.4]; rescale for the palette.
    scale = 1.0 / 0.4
    # Run-length encode identical (fg, bg) pairs to shrink the escape-sequence
    # payload dramatically -- this is the single biggest perf win for stdout.
    prev_fg = None
    prev_bg = None
    for y in range(0, h, 2):
        row_top = y * w
        row_bot = ((y + 1) % h) * w
        for x in range(w):
            t_top = v[row_top + x] * scale
            t_bot = v[row_bot + x] * scale
            if t_top > 1.0:
                t_top = 1.0
            if t_bot > 1.0:
                t_bot = 1.0
            fg = _color(t_top)
            bg = _color(t_bot)
            if fg != prev_fg or bg != prev_bg:
                out.append(
                    f"\x1b[38;2;{fg[0]};{fg[1]};{fg[2]};48;2;{bg[0]};{bg[1]};{bg[2]}m"
                )
                prev_fg = fg
                prev_bg = bg
            out.append("\u2580")
        out.append("\x1b[0m\n")
        prev_fg = None
        prev_bg = None
    return "".join(out)


# -----------------------------------------------------------------------------
# Terminal I/O
# -----------------------------------------------------------------------------

def _terminal_size() -> tuple[int, int]:
    try:
        ts = os.get_terminal_size()
        return ts.columns, ts.lines
    except OSError:
        return 80, 24


class RawInput:
    """Context manager: put stdin into cbreak so we can poll single keys."""

    def __enter__(self):
        self.fd = sys.stdin.fileno()
        self.saved = termios.tcgetattr(self.fd)
        tty.setcbreak(self.fd)
        return self

    def __exit__(self, *exc):
        termios.tcsetattr(self.fd, termios.TCSADRAIN, self.saved)

    def key(self) -> str | None:
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            return ch
        return None


# -----------------------------------------------------------------------------
# Main loop
# -----------------------------------------------------------------------------

def run(initial_preset: str | None) -> None:
    cols, rows = _terminal_size()
    # Leave one row for the HUD.  Each text row = 2 grid rows.
    grid_w = max(40, cols)
    grid_h = max(20, (rows - 2) * 2)
    # Round grid_h to even so half-block pairing works cleanly.
    if grid_h % 2:
        grid_h -= 1

    field = Field(grid_w, grid_h)

    names = [p[0] for p in PRESETS]
    if initial_preset and initial_preset in names:
        idx = names.index(initial_preset)
    else:
        idx = 0

    _, F, k = PRESETS[idx][0], PRESETS[idx][1], PRESETS[idx][2]
    field.seed(PRESETS[idx][0])

    # Adaptive default: small grid -> more steps/frame (cheap per step);
    # big grid -> fewer so we can keep the frame time under ~30 ms.
    cell_count = grid_w * grid_h
    if cell_count < 4000:
        steps_per_frame = 8
    elif cell_count < 10000:
        steps_per_frame = 5
    else:
        steps_per_frame = 3
    paused = False
    buf: list = []

    # Alt screen + hide cursor; restore on exit.
    sys.stdout.write("\x1b[?1049h\x1b[?25l\x1b[2J\x1b[H")
    sys.stdout.flush()

    def restore(*_):
        sys.stdout.write("\x1b[0m\x1b[?25h\x1b[?1049l")
        sys.stdout.flush()

    signal.signal(signal.SIGINT, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))

    try:
        with RawInput() as ri:
            frame = 0
            t_last = time.perf_counter()
            fps = 0.0
            while True:
                # -- handle input --
                while True:
                    ch = ri.key()
                    if ch is None:
                        break
                    if ch == "q" or ch == "\x03":
                        return
                    elif ch == " ":
                        paused = not paused
                    elif ch == "r":
                        field.seed(PRESETS[idx][0])
                    elif ch == "n":
                        idx = (idx + 1) % len(PRESETS)
                        F = PRESETS[idx][1]; k = PRESETS[idx][2]
                        field.seed(PRESETS[idx][0])
                    elif ch == "p":
                        idx = (idx - 1) % len(PRESETS)
                        F = PRESETS[idx][1]; k = PRESETS[idx][2]
                        field.seed(PRESETS[idx][0])
                    elif ch in "12345678":
                        n = int(ch) - 1
                        if n < len(PRESETS):
                            idx = n
                            F = PRESETS[idx][1]; k = PRESETS[idx][2]
                            field.seed(PRESETS[idx][0])
                    elif ch == "+" or ch == "=":
                        steps_per_frame = min(32, steps_per_frame + 1)
                    elif ch == "-" or ch == "_":
                        steps_per_frame = max(1, steps_per_frame - 1)

                # -- advance --
                if not paused:
                    for _ in range(steps_per_frame):
                        field.step(F, k)

                # -- draw --
                sys.stdout.write(render(field, buf))
                t_now = time.perf_counter()
                dt = t_now - t_last
                t_last = t_now
                if dt > 0:
                    fps = 0.85 * fps + 0.15 * (1.0 / dt)
                name = PRESETS[idx][0]
                hud = (
                    f"\x1b[0m  preset [{idx+1}/{len(PRESETS)}] {name:<8}  "
                    f"F={F:.4f} k={k:.4f}  steps/frame={steps_per_frame}  "
                    f"{fps:5.1f} fps  "
                    f"{'PAUSED' if paused else '      '}  "
                    "[space/r/n/p/1-8/+/-/q]\x1b[K\n"
                )
                sys.stdout.write(hud)
                sys.stdout.flush()
                frame += 1

                # Cap at ~30 fps so we don't chew CPU for nothing.
                target = 1.0 / 30.0
                elapsed = time.perf_counter() - t_now
                if elapsed < target:
                    time.sleep(target - elapsed)
    except KeyboardInterrupt:
        pass
    finally:
        restore()


def main() -> None:
    preset = sys.argv[1] if len(sys.argv) > 1 else None
    run(preset)


if __name__ == "__main__":
    main()
