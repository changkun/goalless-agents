# ASCII Terrain Generator

One concrete goal for this empty workspace: turn it into a small, deterministic CLI that generates stylized ASCII terrain maps from a numeric seed.

## Run

```bash
python3 terrain_cli.py --width 48 --height 18 --seed 42
```

## Example

```text
....,,,,^^A^^,,....
...,,,,,^^A^^^,,...
..,,,,^^^AAA^^^,,..
```

## Test

```bash
python3 -m unittest -v
```
