import subprocess
import sys
import unittest

from terrain_cli import TerrainConfig, generate_heightmap, render_ascii


class TerrainTests(unittest.TestCase):
    def test_seed_is_deterministic(self) -> None:
        first = render_ascii(generate_heightmap(TerrainConfig(width=16, height=8, seed=7)))
        second = render_ascii(generate_heightmap(TerrainConfig(width=16, height=8, seed=7)))
        self.assertEqual(first, second)

    def test_different_seeds_change_output(self) -> None:
        first = render_ascii(generate_heightmap(TerrainConfig(width=16, height=8, seed=7)))
        second = render_ascii(generate_heightmap(TerrainConfig(width=16, height=8, seed=8)))
        self.assertNotEqual(first, second)

    def test_cli_renders_expected_dimensions(self) -> None:
        result = subprocess.run(
            [sys.executable, "terrain_cli.py", "--width", "12", "--height", "6", "--seed", "5"],
            check=True,
            capture_output=True,
            text=True,
        )
        lines = result.stdout.strip().splitlines()
        self.assertEqual(len(lines), 6)
        self.assertTrue(all(len(line) == 12 for line in lines))

    def test_small_dimensions_are_rejected(self) -> None:
        result = subprocess.run(
            [sys.executable, "terrain_cli.py", "--width", "3", "--height", "6"],
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("at least 4", result.stderr)


if __name__ == "__main__":
    unittest.main()
