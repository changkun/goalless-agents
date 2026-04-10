from projman import __version__
from projman.cli import main
import io
import sys


def capture_output(func, *args):
    old_out = sys.stdout
    try:
        sys.stdout = io.StringIO()
        code = func(*args)
        return code, sys.stdout.getvalue()
    finally:
        sys.stdout = old_out


def test_version_flag():
    code, out = capture_output(main, ["--version"])
    assert code == 0
    assert __version__ in out.strip()


def test_default_greeting():
    code, out = capture_output(main, [])
    assert code == 0
    assert "Hello, world!" in out


def test_init_creates_project(tmp_path, monkeypatch):
    project_dir = tmp_path / "demo"
    # call main with init command
    code, out = capture_output(main, ["init", str(project_dir)])
    assert code == 0
    assert "Project" in out
    # directory should exist
    assert project_dir.exists()
    assert (project_dir / "README.md").exists()
    assert (project_dir / "pyproject.toml").exists()
