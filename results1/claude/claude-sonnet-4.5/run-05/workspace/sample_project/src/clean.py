"""
Clean module - this one has no issues!
"""


def add(a: int, b: int) -> int:
    """Add two numbers."""
    return a + b


def greet(name: str) -> str:
    """Greet a person."""
    return f"Hello, {name}!"


class Calculator:
    """Simple calculator class."""

    def multiply(self, x: float, y: float) -> float:
        """Multiply two numbers."""
        return x * y

    def divide(self, x: float, y: float) -> float:
        """Divide two numbers."""
        if y == 0:
            raise ValueError("Cannot divide by zero")
        return x / y
