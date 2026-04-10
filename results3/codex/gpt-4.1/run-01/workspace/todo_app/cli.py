import argparse
import sys
from pathlib import Path

TODO_FILE = Path(__file__).parent.parent / "todos.txt"

def list_todos():
    if not TODO_FILE.exists() or TODO_FILE.stat().st_size == 0:
        print("No to-dos yet.")
        return
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        for idx, line in enumerate(f, 1):
            print(f"{idx}. {line.strip()}")

def add_todo(text):
    with open(TODO_FILE, "a", encoding="utf-8") as f:
        f.write(text.strip() + "\n")
    print(f'Added: {text.strip()}")

def remove_todo(index):
    if not TODO_FILE.exists():
        print("No to-do list found.")
        return
    with open(TODO_FILE, "r", encoding="utf-8") as f:
        todos = f.readlines()
    if 1 <= index <= len(todos):
        removed = todos.pop(index-1)
        with open(TODO_FILE, "w", encoding="utf-8") as f:
            f.writelines(todos)
        print(f"Removed: {removed.strip()}")
    else:
        print("Invalid index.")

def main():
    parser = argparse.ArgumentParser(description="Simple To-Do List CLI")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List all to-dos")
    parser_add = subparsers.add_parser("add", help="Add a new to-do")
    parser_add.add_argument("text", nargs='+', help="Text for the to-do")
    parser_rm = subparsers.add_parser("rm", help="Remove a to-do by index")
    parser_rm.add_argument("index", type=int, help="Index of task to remove")

    args = parser.parse_args()

    if args.command == "list":
        list_todos()
    elif args.command == "add":
        add_todo(' '.join(args.text))
    elif args.command == "rm":
        remove_todo(args.index)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
