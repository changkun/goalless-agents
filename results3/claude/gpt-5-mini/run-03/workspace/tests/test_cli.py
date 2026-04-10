from src.cli import greet


def test_greet_default():
    assert greet("") == "Hello, World"


def test_greet_name():
    assert greet("Alice") == "Hello, Alice"


def test_greet_excited():
    assert greet("Bob", excited=True) == "Hello, Bob!"
