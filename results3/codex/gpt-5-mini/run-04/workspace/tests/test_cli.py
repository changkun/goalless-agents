import subprocess
import sys
from pathlib import Path


def run(args):
    p = subprocess.run([sys.executable, str(Path(__file__).parent.parent / "sayhello.py")] + args,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return p.returncode, p.stdout.strip(), p.stderr.strip()


def test_default_greeting():
    rc, out, err = run([])
    assert rc == 0
    assert out == "Hello, World!"


def test_name_greeting():
    rc, out, err = run(["--name", "Alice"])
    assert rc == 0
    assert out == "Hello, Alice!"


def test_version():
    rc, out, err = run(["--version"])
    assert rc == 0
    assert out == "0.1.0"

