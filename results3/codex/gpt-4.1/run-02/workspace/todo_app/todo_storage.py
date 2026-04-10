# Simple file-based storage for todo items
import json
import os

TODO_FILE = os.path.expanduser("~/.todo_items.json")

def load_items():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, 'r') as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_items(items):
    with open(TODO_FILE, 'w') as f:
        json.dump(items, f, indent=2)

def add_item(task):
    items = load_items()
    items.append({"task": task, "done": False})
    save_items(items)

def list_items():
    return load_items()

def complete_item(index):
    items = load_items()
    if 0 <= index < len(items):
        items[index]["done"] = True
        save_items(items)
        return True
    return False
