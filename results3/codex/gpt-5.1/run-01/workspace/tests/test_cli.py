import subprocess
import sys
from pathlib import Path


def run_cli(*args: str, input_text: str | None = None) -> subprocess.CompletedProcess:
    cmd = [sys.executable, "-m", "miniwc.cli", *args]
    return subprocess.run(
        cmd,
        input=input_text.encode() if input_text is not None else None,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_stdin_only(tmp_path: Path):
    proc = run_cli(input_text="one two three\n")
    assert proc.returncode == 0
    # Expect 1 line, 3 words, some bytes
    out = proc.stdout.decode().strip()
    assert "1" in out and "3" in out


def test_single_file(tmp_path: Path):
    p = tmp_path / "sample.txt"
    p.write_text("alpha beta\ngamma\n")

    proc = run_cli(str(p))
    assert proc.returncode == 0
    out = proc.stdout.decode().strip()
    assert "2" in out  # lines
    assert "3" in out  # words
    assert "sample.txt" in out


def test_multiple_files_show_total(tmp_path: Path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("one two\n")
    b.write_text("three four five\n")

    proc = run_cli(str(a), str(b))
    assert proc.returncode == 0
    out_lines = proc.stdout.decode().strip().splitlines()
    assert len(out_lines) == 3
    assert "a.txt" in out_lines[0]
    assert "b.txt" in out_lines[1]
    assert "total" in out_lines[2]

