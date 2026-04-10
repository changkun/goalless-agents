# Small CLI demo

This repository contains a minimal Python CLI tool `sayhello` that prints a greeting and supports a `--name` option and `--version`.

Files:
- `sayhello.py` - CLI entrypoint
- `pyproject.toml` - simple project metadata
- `tests/test_cli.py` - pytest tests

To run tests:

```
python -m pip install -r requirements.txt
pytest -q
```
