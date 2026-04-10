def greet(name: str) -> str:
    return f"Hello, {name}!"


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Simple greeting CLI")
    parser.add_argument("name", nargs="?", default="world", help="Name to greet")
    args = parser.parse_args()
    print(greet(args.name))


if __name__ == "__main__":
    main()
