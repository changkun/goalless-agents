import argparse
import os
from . import __version__


def _create_project(name: str) -> None:
    """Create a minimal Python project skeleton in a directory named `name` or path.

    If `name` is a path (absolute or relative), the project directory created is that
    path and the package name is derived from the final path component.
    """
    dirpath = os.fspath(name)
    os.makedirs(dirpath, exist_ok=True)
    project_name = os.path.basename(os.path.normpath(dirpath)) or "project"

    # README
    readme_path = os.path.join(dirpath, "README.md")
    with open(readme_path, "w", encoding="utf-8") as f:
        f.write(f"# {project_name}\n\nCreated by projman.\n")

    # pyproject.toml
    pyproject_path = os.path.join(dirpath, "pyproject.toml")
    with open(pyproject_path, "w", encoding="utf-8") as f:
        f.write(f'''[project]
name = "{project_name}"
version = "0.1.0"
requires-python = ">=3.8"

[tool.pytest.ini_options]
minversion = "6.0"
''')

    # package directory with __init__.py
    pkg_dir = os.path.join(dirpath, project_name)
    os.makedirs(pkg_dir, exist_ok=True)
    with open(os.path.join(pkg_dir, "__init__.py"), "w", encoding="utf-8") as f:
        f.write(f'__version__ = "0.1.0"\n')

    # a basic .gitignore
    gitignore_path = os.path.join(dirpath, ".gitignore")
    with open(gitignore_path, "w", encoding="utf-8") as f:
        f.write("__pycache__/\n*.pyc\n.env\n")

    # done
    return


def main(args=None):
    """Entry point for the projman CLI.

    Returns 0 on success. Prints to stdout.
    """
    # support being called with an explicit args list (for tests)
    if args is None:
        import sys
        args = sys.argv[1:]

    # Simple subcommand detection to preserve the existing positional API.
    if args and args[0] == "init":
        if len(args) < 2:
            print("Usage: projman init <project_name>")
            return 2
        _create_project(args[1])
        print(f"Project '{args[1]}' created.")
        return 0

    # Fall back to the original single-command interface (greeting + --version).
    parser = argparse.ArgumentParser(prog="projman")
    parser.add_argument("--version", action="store_true", help="Show version and exit")
    parser.add_argument("name", nargs="?", default="world", help="Name to greet")
    ns = parser.parse_args(args)
    if ns.version:
        print(__version__)
        return 0
    print(f"Hello, {ns.name}!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
