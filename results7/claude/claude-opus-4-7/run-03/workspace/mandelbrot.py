#!/usr/bin/env python3
"""Tiny ASCII Mandelbrot renderer."""

PALETTE = " .:-=+*#%@"
W, H = 80, 30
X_MIN, X_MAX = -2.2, 1.0
Y_MIN, Y_MAX = -1.2, 1.2
MAX_ITER = len(PALETTE) * 8


def escape(cr: float, ci: float) -> int:
    zr = zi = 0.0
    for i in range(MAX_ITER):
        zr2, zi2 = zr * zr, zi * zi
        if zr2 + zi2 > 4.0:
            return i
        zr, zi = zr2 - zi2 + cr, 2 * zr * zi + ci
    return MAX_ITER


def render() -> str:
    rows = []
    for py in range(H):
        ci = Y_MIN + (Y_MAX - Y_MIN) * py / (H - 1)
        row = []
        for px in range(W):
            cr = X_MIN + (X_MAX - X_MIN) * px / (W - 1)
            n = escape(cr, ci)
            row.append(PALETTE[-1] if n == MAX_ITER else PALETTE[n % len(PALETTE)])
        rows.append("".join(row))
    return "\n".join(rows)


if __name__ == "__main__":
    print(render())
