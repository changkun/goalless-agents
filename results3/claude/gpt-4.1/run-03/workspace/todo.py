#!/usr/bin/env python3
import sys
import json
import os

TODO_FILE = "todos.json"
def load_todos():
    if os.path.exists(TODO_FILE):
        with open(TODO_FILE, "r") as f:
            return json.load(f)
    return []

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def add_todo(item):
    todos = load_todos()
    todos.append({"task": item})
    save_todos(todos)
    print(f"Added: {item}")

def list_todos():
    todos = load_todos()
    if not todos:
        print("No todos yet.")
        return
    for idx, todo in enumerate(todos, 1):
        print(f"{idx}. {todo['task']}")

def remove_todo(idx):
    todos = load_todos()
    if 0 < idx <= len(todos):
        removed = todos.pop(idx-1)
        save_todos(todos)
        print(f"Removed: {removed['task']}")
    else:
        print("Invalid index.")

def usage():
    print("Usage:")
    print("  todo.py add <task>")
    print("  todo.py list")
    print("  todo.py remove <index>")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1] == "add" and len(sys.argv) > 2:
        add_todo(" ".join(sys.argv[2:]))
    elif sys.argv[1] == "list":
        list_todos()
    elif sys.argv[1] == "remove" and len(sys.argv) == 3 and sys.argv[2].isdigit():
        remove_todo(int(sys.argv[2]))
    else:
        usage()
