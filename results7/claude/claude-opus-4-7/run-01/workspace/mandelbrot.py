#!/usr/bin/env python3
"""Render the Mandelbrot set as ASCII art."""

WIDTH, HEIGHT = 80, 30
MAX_ITER = 80
PALETTE = " .:-=+*#%@"


def escape(c: complex) -> int:
    z = 0j
    for i in range(MAX_ITER):
        if abs(z) > 2:
            return i
        z = z * z + c
    return MAX_ITER


def render(cx=-0.5, cy=0.0, zoom=1.2):
    aspect = 0.5  # terminal chars are ~2x taller than wide
    rows = []
    for py in range(HEIGHT):
        y = cy + (py - HEIGHT / 2) / (HEIGHT / 2) * zoom * aspect
        row = []
        for px in range(WIDTH):
            x = cx + (px - WIDTH / 2) / (WIDTH / 2) * zoom
            n = escape(complex(x, y))
            if n == MAX_ITER:
                row.append(" ")
            else:
                row.append(PALETTE[n * (len(PALETTE) - 1) // MAX_ITER])
        rows.append("".join(row))
    return "\n".join(rows)


if __name__ == "__main__":
    print(render())
