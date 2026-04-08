#!/usr/bin/env python3

import argparse
import json
import os

TODO_FILE = os.path.join(os.path.expanduser("~"), ".todo_list.json")

def get_todos():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, "r") as f:
        return json.load(f)

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=4)

def add_task(task):
    todos = get_todos()
    todos.append({"task": task, "completed": False})
    save_todos(todos)
    print(f"Added task: \"{task}\"")

def list_tasks():
    todos = get_todos()
    if not todos:
        print("No tasks found.")
        return
    for i, todo in enumerate(todos):
        status = "[x]" if todo["completed"] else "[ ]"
        print(f"{i + 1}. {status} {todo['task']}")

def complete_task(task_number):
    todos = get_todos()
    if 0 < task_number <= len(todos):
        todos[task_number - 1]["completed"] = True
        save_todos(todos)
        print(f"Completed task: \"{todos[task_number - 1]['task']}\"")
    else:
        print("Invalid task number.")

def main():
    parser = argparse.ArgumentParser(description="A simple command-line todo list.")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new task.")
    add_parser.add_argument("task", type=str, help="The task to add.")

    list_parser = subparsers.add_parser("list", help="List all tasks.")

    complete_parser = subparsers.add_parser("complete", help="Complete a task.")
    complete_parser.add_argument("task_number", type=int, help="The number of the task to complete.")

    args = parser.parse_args()

    if args.command == "add":
        add_task(args.task)
    elif args.command == "list":
        list_tasks()
    elif args.command == "complete":
        complete_task(args.task_number)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
