#!/usr/bin/env python3
"""
Interactive Mandelbrot Set Explorer
Controls: Arrow keys = pan, +/- = zoom, r = reset, q = quit, h = help
"""

import curses
import math
import sys


# ANSI 256-color palette indices that make a nice gradient
PALETTE = [
    # Black (inside the set)
    0,
    # Blues → cyans → greens → yellows → oranges → reds → purples
    17, 18, 19, 20, 21,
    27, 33, 39, 45, 51,
    50, 49, 48, 47, 46,
    82, 118, 154, 190, 226,
    220, 214, 208, 202, 196,
    197, 198, 199, 200, 201,
    165, 129, 93, 57, 21,
]

MAX_ITER = 128


def mandelbrot(cx: float, cy: float) -> int:
    """Return iteration count for point (cx, cy); 0 means inside the set."""
    zx, zy = 0.0, 0.0
    for i in range(1, MAX_ITER + 1):
        zx2, zy2 = zx * zx, zy * zy
        if zx2 + zy2 > 4.0:
            return i
        zx, zy = zx2 - zy2 + cx, 2.0 * zx * zy + cy
    return 0


def smooth_iter(cx: float, cy: float) -> float:
    """Return smooth (continuous) iteration count for coloring."""
    zx, zy = 0.0, 0.0
    for i in range(1, MAX_ITER + 1):
        zx2, zy2 = zx * zx, zy * zy
        if zx2 + zy2 > 4.0:
            log_zn = math.log(zx2 + zy2) / 2
            nu = math.log(log_zn / math.log(2)) / math.log(2)
            return i + 1 - nu
        zx, zy = zx2 - zy2 + cx, 2.0 * zx * zy + cy
    return 0.0


def iter_to_color(val: float) -> int:
    """Map smooth iteration value to a 256-color index."""
    if val == 0.0:
        return 0  # inside set → black
    n = len(PALETTE) - 1  # skip index 0 (black)
    t = (val % n)
    lo = int(t) % n + 1
    hi = (lo % n) + 1
    frac = t - int(t)
    # Simple nearest-neighbor (curses pairs don't interpolate well)
    return PALETTE[lo] if frac < 0.5 else PALETTE[hi]


def render(stdscr, cx: float, cy: float, zoom: float) -> None:
    h, w = stdscr.getmaxyx()
    plot_h = h - 2  # reserve 2 lines for status bar

    # Pixel-to-complex mapping (characters are ~2x taller than wide)
    x_scale = (3.5 / zoom) / max(w - 1, 1)
    y_scale = (2.0 / zoom) / max(plot_h - 1, 1)
    x_off = cx - (w / 2) * x_scale
    y_off = cy - (plot_h / 2) * y_scale

    # Pre-register needed color pairs (curses limit: 256 pairs)
    # Map color index → pair number (pair 0 is reserved)
    color_map: dict[int, int] = {}
    pair_id = 1

    def get_pair(color_idx: int) -> int:
        nonlocal pair_id
        if color_idx not in color_map:
            if pair_id < 255:
                curses.init_pair(pair_id, color_idx, color_idx)
                color_map[color_idx] = pair_id
                pair_id += 1
        return color_map.get(color_idx, 1)

    # Draw
    for row in range(plot_h):
        imag = y_off + row * y_scale
        for col in range(w - 1):
            real = x_off + col * x_scale
            val = smooth_iter(real, imag)
            cidx = iter_to_color(val)
            pair = get_pair(cidx)
            try:
                stdscr.addch(row, col, ' ', curses.color_pair(pair))
            except curses.error:
                pass

    # Status bar
    zoom_str = f"  Center: ({cx:.6f}, {cy:.6f}i)   Zoom: {zoom:.1f}x   "
    help_str = "[←→↑↓] pan  [+/-] zoom  [r] reset  [q] quit"
    status = (zoom_str + help_str)[:w - 1]
    try:
        stdscr.addstr(h - 2, 0, status.ljust(w - 1), curses.A_REVERSE)
        stdscr.addstr(h - 1, 0, "  Mandelbrot Set Explorer".ljust(w - 1),
                      curses.A_BOLD)
    except curses.error:
        pass


def main(stdscr) -> None:
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    stdscr.timeout(0)

    if not curses.has_colors() or curses.COLORS < 256:
        stdscr.addstr(0, 0, "Need a 256-color terminal. Set TERM=xterm-256color")
        stdscr.getch()
        return

    # Initial view
    cx, cy = -0.5, 0.0
    zoom = 1.0
    dirty = True

    while True:
        if dirty:
            stdscr.clear()
            render(stdscr, cx, cy, zoom)
            stdscr.refresh()
            dirty = False

        key = stdscr.getch()
        if key == -1:
            continue

        step = 0.3 / zoom
        if key in (ord('q'), ord('Q'), 27):
            break
        elif key == curses.KEY_LEFT:
            cx -= step; dirty = True
        elif key == curses.KEY_RIGHT:
            cx += step; dirty = True
        elif key == curses.KEY_UP:
            cy -= step; dirty = True
        elif key == curses.KEY_DOWN:
            cy += step; dirty = True
        elif key in (ord('+'), ord('=')):
            zoom *= 2.0; dirty = True
        elif key in (ord('-'), ord('_')):
            zoom = max(0.1, zoom / 2.0); dirty = True
        elif key in (ord('r'), ord('R')):
            cx, cy, zoom = -0.5, 0.0, 1.0; dirty = True
        elif key == curses.KEY_RESIZE:
            dirty = True


if __name__ == '__main__':
    try:
        curses.wrapper(main)
    except KeyboardInterrupt:
        pass
    print("Goodbye from the Mandelbrot explorer!")
