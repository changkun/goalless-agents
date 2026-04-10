from src.cli import greet


def test_greet_caps():
    assert greet("alice", caps=True) == "HELLO, ALICE"


def test_greet_caps_excited():
    assert greet("bob", excited=True, caps=True) == "HELLO, BOB!"
