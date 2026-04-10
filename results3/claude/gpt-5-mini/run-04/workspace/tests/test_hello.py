import sys
import subprocess
from hello import greet


def test_greet_with_name():
    assert greet("Alice") == "Hello, Alice!"


def test_greet_default():
    # behavior when called with the default
    assert greet("world") == "Hello, world!"


def test_cli_invocation():
    # Run the CLI and check output
    proc = subprocess.run([sys.executable, "hello.py", "Bob"], capture_output=True, text=True)
    assert proc.returncode == 0
    assert proc.stdout.strip() == "Hello, Bob!"
