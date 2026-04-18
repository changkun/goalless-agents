"""Render the Mandelbrot set to the terminal in ASCII."""

import shutil

GRADIENT = " .`-':,^;~=+*#%@"


def mandelbrot(c: complex, max_iter: int = 80) -> int:
    z = 0j
    for i in range(max_iter):
        if abs(z) > 2:
            return i
        z = z * z + c
    return max_iter


def render(width: int, height: int, max_iter: int = 80) -> str:
    x_min, x_max = -2.1, 0.9
    y_min, y_max = -1.1, 1.1
    rows = []
    for py in range(height):
        y = y_min + (y_max - y_min) * py / (height - 1)
        row = []
        for px in range(width):
            x = x_min + (x_max - x_min) * px / (width - 1)
            n = mandelbrot(complex(x, y), max_iter)
            if n == max_iter:
                row.append(" ")
            else:
                idx = int((n / max_iter) * (len(GRADIENT) - 1))
                row.append(GRADIENT[idx])
        rows.append("".join(row))
    return "\n".join(rows)


if __name__ == "__main__":
    cols, lines = shutil.get_terminal_size((100, 40))
    print(render(cols, lines - 2))
