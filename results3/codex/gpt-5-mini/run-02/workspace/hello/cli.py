def greet(name: str) -> str:
    """Return a greeting for . Strips whitespace and capitalizes name."""
    if name is None:
        raise TypeError("name must be a string")
    s = str(name).strip()
    if not s:
        return "Hello!"
    return f"Hello, {s[0].upper() + s[1:]}!"

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        print(greet(sys.argv[1]))
    else:
        print(greet())
