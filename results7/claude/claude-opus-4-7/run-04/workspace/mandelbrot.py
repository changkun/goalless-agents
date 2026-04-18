#!/usr/bin/env python3
"""Render the Mandelbrot set as ASCII art."""

GRADIENT = " .:-=+*#%@"

def mandelbrot(c: complex, max_iter: int = 80) -> int:
    z = 0j
    for i in range(max_iter):
        if abs(z) > 2:
            return i
        z = z * z + c
    return max_iter


def render(width: int = 100, height: int = 36,
           xmin: float = -2.2, xmax: float = 1.0,
           ymin: float = -1.1, ymax: float = 1.1,
           max_iter: int = 80) -> str:
    rows = []
    for py in range(height):
        y = ymin + (ymax - ymin) * py / (height - 1)
        row = []
        for px in range(width):
            x = xmin + (xmax - xmin) * px / (width - 1)
            n = mandelbrot(complex(x, y), max_iter)
            if n == max_iter:
                row.append(" ")
            else:
                idx = int((n / max_iter) * (len(GRADIENT) - 1))
                row.append(GRADIENT[idx])
        rows.append("".join(row))
    return "\n".join(rows)


if __name__ == "__main__":
    print(render())
