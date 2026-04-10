import pytest

from hello import greet, main


def test_greet():
    assert greet("Alice") == "Hello, Alice!"


def test_greet_empty():
    with pytest.raises(ValueError):
        greet("")


def test_main_success(capsys):
    rc = main(["Bob"])
    captured = capsys.readouterr()
    assert rc == 0
    assert "Hello, Bob!" in captured.out


def test_main_usage(capsys):
    rc = main([])
    captured = capsys.readouterr()
    assert rc == 2
    assert "Usage:" in captured.out

