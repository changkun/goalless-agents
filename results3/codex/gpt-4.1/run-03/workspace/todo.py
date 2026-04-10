#!/usr/bin/env python3
import sys, os

TODO_FILE = 'tasks.txt'

def load_tasks():
    if not os.path.exists(TODO_FILE):
        return []
    with open(TODO_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def save_tasks(tasks):
    with open(TODO_FILE, 'w') as f:
        for task in tasks:
            f.write(task + '\n')

def list_tasks():
    tasks = load_tasks()
    if not tasks:
        print('No tasks!')
        return
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task}")

def add_task(task):
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    print(f'Added: {task}')

def remove_task(idx):
    tasks = load_tasks()
    if idx < 1 or idx > len(tasks):
        print('Invalid task number.')
        return
    removed = tasks.pop(idx-1)
    save_tasks(tasks)
    print(f'Removed: {removed}')

def print_help():
    print("""Usage:
  python todo.py add <task>      Add a new task
  python todo.py list            List all tasks
  python todo.py remove <num>    Remove task number <num>
""")

def main():
    if len(sys.argv) < 2:
        print_help()
        return
    cmd = sys.argv[1]
    if cmd == 'add' and len(sys.argv) > 2:
        add_task(' '.join(sys.argv[2:]))
    elif cmd == 'list':
        list_tasks()
    elif cmd == 'remove' and len(sys.argv) == 3 and sys.argv[2].isdigit():
        remove_task(int(sys.argv[2]))
    else:
        print_help()

if __name__ == "__main__":
    main()
