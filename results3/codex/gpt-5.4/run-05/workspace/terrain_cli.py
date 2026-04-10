#!/usr/bin/env python3

from __future__ import annotations

import argparse
import random
from dataclasses import dataclass

TERRAIN_BANDS = (
    (0.18, "~"),
    (0.32, "."),
    (0.5, ","),
    (0.68, "^"),
    (0.84, "A"),
    (1.01, "M"),
)


@dataclass(frozen=True)
class TerrainConfig:
    width: int
    height: int
    seed: int
    waterline: float = 0.18


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def generate_heightmap(config: TerrainConfig) -> list[list[float]]:
    rng = random.Random(config.seed)
    grid = [
        [_clamp(rng.random() * 0.65 + (y / max(1, config.height - 1)) * 0.25) for _ in range(config.width)]
        for y in range(config.height)
    ]

    for _ in range(3):
        smoothed: list[list[float]] = []
        for y in range(config.height):
            row: list[float] = []
            for x in range(config.width):
                samples = []
                for yy in range(max(0, y - 1), min(config.height, y + 2)):
                    for xx in range(max(0, x - 1), min(config.width, x + 2)):
                        samples.append(grid[yy][xx])
                ridge_bias = 0.08 if x == config.width // 2 else 0.0
                row.append(_clamp(sum(samples) / len(samples) + ridge_bias))
            smoothed.append(row)
        grid = smoothed

    return grid


def render_ascii(heightmap: list[list[float]]) -> str:
    rows = []
    for row in heightmap:
        chars = []
        for value in row:
            for ceiling, marker in TERRAIN_BANDS:
                if value < ceiling:
                    chars.append(marker)
                    break
        rows.append("".join(chars))
    return "\n".join(rows)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate a deterministic ASCII terrain map from a numeric seed."
    )
    parser.add_argument("--width", type=int, default=48, help="Map width in characters.")
    parser.add_argument("--height", type=int, default=18, help="Map height in rows.")
    parser.add_argument("--seed", type=int, default=42, help="Numeric seed for deterministic output.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.width < 4 or args.height < 4:
        raise SystemExit("width and height must both be at least 4")

    config = TerrainConfig(width=args.width, height=args.height, seed=args.seed)
    print(render_ascii(generate_heightmap(config)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
