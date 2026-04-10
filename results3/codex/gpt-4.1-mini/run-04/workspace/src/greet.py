#!/usr/bin/env python3
import argparse

def greet(name: str) -> str:
    return f"Hello, {name}!"

def main():
    parser = argparse.ArgumentParser(description="Simple greeter CLI")
    parser.add_argument("name", help="Name to greet")
    args = parser.parse_args()
    greeting = greet(args.name)
    print(greeting)

if __name__ == "__main__":
    main()
