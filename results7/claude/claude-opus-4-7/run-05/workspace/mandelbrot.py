import sys

SHADES = " .·:-=+*#%@"
W, H = 100, 38
CX, CY, ZOOM = -0.75, 0.0, 1.3
MAX_ITER = 80

def mandel(c):
    z = 0j
    for i in range(MAX_ITER):
        z = z * z + c
        if (z.real * z.real + z.imag * z.imag) > 4:
            # smooth coloring
            return i + 1 - (abs(z).bit_length() if False else 0)
    return MAX_ITER

def main():
    scale = 3.0 / ZOOM
    y_scale = scale * (H / W) * 2.0
    for py in range(H):
        row = []
        for px in range(W):
            x = CX + (px / W - 0.5) * scale
            y = CY + (py / H - 0.5) * y_scale
            n = mandel(complex(x, y))
            if n >= MAX_ITER:
                row.append(SHADES[-1])
            else:
                idx = int((n / MAX_ITER) ** 0.35 * (len(SHADES) - 2))
                row.append(SHADES[idx])
        sys.stdout.write("".join(row) + "\n")

if __name__ == "__main__":
    main()
