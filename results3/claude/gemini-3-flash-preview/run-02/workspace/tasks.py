import json
import os
import sys

TASKS_FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_tasks(tasks):
    with open(TASKS_FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task(description):
    tasks = load_tasks()
    tasks.append({"description": description, "completed": False})
    save_tasks(tasks)
    print(f"Added task: {description}")

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print("No tasks found.")
        return
    for i, task in enumerate(tasks):
        status = "✓" if task["completed"] else " "
        print(f"{i + 1}. [{status}] {task['description']}")

def complete_task(index):
    tasks = load_tasks()
    try:
        tasks[index - 1]["completed"] = True
        save_tasks(tasks)
        print(f"Completed task: {tasks[index - 1]['description']}")
    except IndexError:
        print("Invalid task number.")

def delete_task(index):
    tasks = load_tasks()
    try:
        removed = tasks.pop(index - 1)
        save_tasks(tasks)
        print(f"Deleted task: {removed['description']}")
    except IndexError:
        print("Invalid task number.")

def main():
    if len(sys.argv) < 2:
        print("Usage: python tasks.py [add|list|complete|delete] [args]")
        return

    command = sys.argv[1]

    if command == "add":
        add_task(" ".join(sys.argv[2:]))
    elif command == "list":
        list_tasks()
    elif command == "complete":
        complete_task(int(sys.argv[2]))
    elif command == "delete":
        delete_task(int(sys.argv[2]))
    else:
        print("Unknown command.")

if __name__ == "__main__":
    main()
