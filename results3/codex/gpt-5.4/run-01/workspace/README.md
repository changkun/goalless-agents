# Next Goal

Make the workspace self-describing by adding a small tool that can inspect any
directory and emit a compact project snapshot.

## What was implemented

`tools/project_snapshot.py` is a zero-dependency CLI that reports:

- total file count
- total bytes
- whether the directory is empty
- file counts by language or file type
- the largest files in the tree

It skips common generated or vendor directories such as `node_modules`,
`dist`, `build`, `.git`, and `__pycache__`.

## Usage

```bash
python3 tools/project_snapshot.py . --pretty
```

You can also point it at another directory:

```bash
python3 tools/project_snapshot.py /some/project --limit 5 --pretty
```
