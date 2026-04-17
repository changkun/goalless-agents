#!/usr/bin/env python3
"""Terminal boids flocking simulation.

Controls:
  q          quit
  space      scatter (random kick)
  + / -      add / remove boids
  s / S      separation weight down / up
  a / A      alignment  weight down / up
  c / C      cohesion   weight down / up
  r          reset
  p          pause/resume
"""

import math
import os
import random
import select
import signal
import sys
import termios
import time
import tty

# --- Terminal helpers --------------------------------------------------------

CSI = "\x1b["
HIDE_CUR = CSI + "?25l"
SHOW_CUR = CSI + "?25h"
ALT_ON   = CSI + "?1049h"
ALT_OFF  = CSI + "?1049l"
CLEAR    = CSI + "2J"
HOME     = CSI + "H"
RESET    = CSI + "0m"

def term_size():
    sz = os.get_terminal_size()
    return sz.columns, sz.lines

def rgb(r, g, b):
    return f"{CSI}38;2;{r};{g};{b}m"

# --- Boid --------------------------------------------------------------------

class Boid:
    __slots__ = ("x", "y", "vx", "vy")
    def __init__(self, w, h):
        self.x = random.uniform(0, w)
        self.y = random.uniform(0, h)
        angle = random.uniform(0, math.tau)
        speed = random.uniform(0.8, 1.4)
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed * 0.5  # chars are taller than wide

# --- Simulation --------------------------------------------------------------

class Sim:
    def __init__(self, w, h, n=120):
        self.w, self.h = w, h
        self.boids = [Boid(w, h) for _ in range(n)]
        self.w_sep = 1.6
        self.w_ali = 1.0
        self.w_coh = 0.8
        self.view_sep = 3.0
        self.view_flock = 8.0
        self.max_speed = 1.6
        self.paused = False

    def resize(self, w, h):
        self.w, self.h = w, h
        for b in self.boids:
            b.x = min(max(b.x, 0), w - 1)
            b.y = min(max(b.y, 0), h - 1)

    def set_count(self, n):
        n = max(1, min(2000, n))
        while len(self.boids) < n:
            self.boids.append(Boid(self.w, self.h))
        if len(self.boids) > n:
            self.boids = self.boids[:n]

    def scatter(self):
        for b in self.boids:
            a = random.uniform(0, math.tau)
            s = random.uniform(1.5, 3.0)
            b.vx += math.cos(a) * s
            b.vy += math.sin(a) * s * 0.5

    def step(self):
        if self.paused:
            return
        # Spatial hash for O(n) neighborhood queries.
        cell = self.view_flock
        grid = {}
        for i, b in enumerate(self.boids):
            key = (int(b.x / cell), int(b.y / cell))
            grid.setdefault(key, []).append(i)

        new = [(b.vx, b.vy) for b in self.boids]
        vs2 = self.view_sep * self.view_sep
        vf2 = self.view_flock * self.view_flock

        for i, b in enumerate(self.boids):
            cx, cy = int(b.x / cell), int(b.y / cell)
            sep_x = sep_y = 0.0
            ali_x = ali_y = 0.0
            coh_x = coh_y = 0.0
            n_flock = 0
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for j in grid.get((cx + dx, cy + dy), ()):
                        if j == i:
                            continue
                        o = self.boids[j]
                        ox, oy = o.x - b.x, (o.y - b.y) * 2.0  # aspect correction
                        d2 = ox*ox + oy*oy
                        if d2 < vf2 and d2 > 0:
                            n_flock += 1
                            ali_x += o.vx; ali_y += o.vy
                            coh_x += o.x;  coh_y += o.y
                            if d2 < vs2:
                                sep_x -= ox / d2
                                sep_y -= oy / d2
            ax = ay = 0.0
            if n_flock > 0:
                ali_x /= n_flock; ali_y /= n_flock
                coh_x = coh_x / n_flock - b.x
                coh_y = coh_y / n_flock - b.y
                ax += self.w_ali * (ali_x - b.vx) * 0.08
                ay += self.w_ali * (ali_y - b.vy) * 0.08
                ax += self.w_coh * coh_x * 0.006
                ay += self.w_coh * coh_y * 0.006
            ax += self.w_sep * sep_x * 0.6
            ay += self.w_sep * sep_y * 0.6

            vx = b.vx + ax
            vy = b.vy + ay
            sp = math.hypot(vx, vy)
            if sp > self.max_speed:
                vx = vx / sp * self.max_speed
                vy = vy / sp * self.max_speed
            elif sp < 0.3:
                vx = vx / (sp + 1e-9) * 0.3
                vy = vy / (sp + 1e-9) * 0.3
            new[i] = (vx, vy)

        for b, (vx, vy) in zip(self.boids, new):
            b.vx, b.vy = vx, vy
            b.x = (b.x + vx) % self.w
            b.y = (b.y + vy) % self.h

# --- Rendering ---------------------------------------------------------------

ARROWS = {
    0: "→", 1: "↘", 2: "↓", 3: "↙",
    4: "←", 5: "↖", 6: "↑", 7: "↗",
}

def arrow_for(vx, vy):
    # map angle to one of 8 arrow glyphs; note y flipped since row grows downward
    a = math.atan2(vy, vx)
    idx = int(round(a / (math.pi / 4))) % 8
    return ARROWS[idx]

def render(sim, status):
    w, h = sim.w, sim.h
    # grid of (glyph, color) or None
    cells = [None] * (w * h)
    for b in sim.boids:
        x = int(b.x); y = int(b.y)
        if 0 <= x < w and 0 <= y < h:
            sp = math.hypot(b.vx, b.vy)
            # color by speed: slow=blue, fast=orange/red
            t = max(0.0, min(1.0, (sp - 0.3) / (sim.max_speed - 0.3 + 1e-9)))
            r = int(60 + 195 * t)
            g = int(140 + 60 * (1 - abs(0.5 - t) * 2))
            bl = int(230 - 200 * t)
            cells[y * w + x] = (arrow_for(b.vx, b.vy), (r, g, bl))

    out = [HOME]
    for y in range(h - 1):
        row_parts = []
        last_color = None
        for x in range(w):
            c = cells[y * w + x]
            if c is None:
                if last_color is not None:
                    row_parts.append(RESET)
                    last_color = None
                row_parts.append(" ")
            else:
                glyph, color = c
                if color != last_color:
                    row_parts.append(rgb(*color))
                    last_color = color
                row_parts.append(glyph)
        if last_color is not None:
            row_parts.append(RESET)
        out.append("".join(row_parts))
        out.append("\n")
    # status line
    out.append(RESET + CSI + "7m" + status.ljust(w)[:w] + RESET)
    sys.stdout.write("".join(out))
    sys.stdout.flush()

# --- Input -------------------------------------------------------------------

def read_key():
    r, _, _ = select.select([sys.stdin], [], [], 0)
    if r:
        try:
            return sys.stdin.read(1)
        except (IOError, OSError):
            return None
    return None

# --- Main --------------------------------------------------------------------

def main():
    if not sys.stdout.isatty():
        print("boids: stdout is not a TTY. Run in an interactive terminal.", file=sys.stderr)
        sys.exit(2)

    w, h = term_size()
    sim = Sim(w, h - 1, n=140)

    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    resized = {"flag": False}
    def on_winch(*_):
        resized["flag"] = True
    signal.signal(signal.SIGWINCH, on_winch)

    try:
        tty.setcbreak(fd)
        sys.stdout.write(ALT_ON + HIDE_CUR + CLEAR)
        sys.stdout.flush()

        target_dt = 1 / 30.0
        last = time.monotonic()
        frames = 0
        fps = 0.0
        fps_t = last

        while True:
            if resized["flag"]:
                resized["flag"] = False
                nw, nh = term_size()
                sim.resize(nw, nh - 1)
                sys.stdout.write(CLEAR)

            k = read_key()
            if k:
                if k == "q":
                    break
                elif k == " ":
                    sim.scatter()
                elif k == "+" or k == "=":
                    sim.set_count(len(sim.boids) + 20)
                elif k == "-" or k == "_":
                    sim.set_count(len(sim.boids) - 20)
                elif k == "s":
                    sim.w_sep = max(0, sim.w_sep - 0.2)
                elif k == "S":
                    sim.w_sep += 0.2
                elif k == "a":
                    sim.w_ali = max(0, sim.w_ali - 0.2)
                elif k == "A":
                    sim.w_ali += 0.2
                elif k == "c":
                    sim.w_coh = max(0, sim.w_coh - 0.2)
                elif k == "C":
                    sim.w_coh += 0.2
                elif k == "p":
                    sim.paused = not sim.paused
                elif k == "r":
                    sim.boids = [Boid(sim.w, sim.h) for _ in range(len(sim.boids))]

            sim.step()

            frames += 1
            now = time.monotonic()
            if now - fps_t >= 0.5:
                fps = frames / (now - fps_t)
                frames = 0
                fps_t = now

            status = (
                f" boids  n={len(sim.boids):<4d}  "
                f"sep={sim.w_sep:.1f}  ali={sim.w_ali:.1f}  coh={sim.w_coh:.1f}  "
                f"fps={fps:4.1f}  "
                f"{'[PAUSED] ' if sim.paused else ''}"
                f"[q]uit [space]scatter [+/-]count [s/a/c]ooling [S/A/C]up [p]ause [r]eset "
            )
            render(sim, status)

            # pace to target fps
            dt = time.monotonic() - last
            if dt < target_dt:
                time.sleep(target_dt - dt)
            last = time.monotonic()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)
        sys.stdout.write(SHOW_CUR + ALT_OFF + RESET)
        sys.stdout.flush()

if __name__ == "__main__":
    main()
