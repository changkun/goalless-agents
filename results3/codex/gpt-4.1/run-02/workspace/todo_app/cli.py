import sys
from todo_storage import add_item, list_items, complete_item

def print_usage():
    print("Usage:")
    print("  python3 cli.py add <task>")
    print("  python3 cli.py list")
    print("  python3 cli.py done <number>")

def main():
    if len(sys.argv) < 2:
        print_usage()
        return
    cmd = sys.argv[1]
    if cmd == "add" and len(sys.argv) > 2:
        task = " ".join(sys.argv[2:])
        add_item(task)
        print(f"Added: {task}")
    elif cmd == "list":
        items = list_items()
        if not items:
            print("No todo items.\n")
            return
        for i, item in enumerate(items):
            status = "[x]" if item["done"] else "[ ]"
            print(f"{i+1}. {status} {item['task']}")
    elif cmd == "done" and len(sys.argv) == 3 and sys.argv[2].isdigit():
        idx = int(sys.argv[2]) - 1
        if complete_item(idx):
            print(f"Marked item {sys.argv[2]} as complete.")
        else:
            print("Invalid item number.")
    else:
        print_usage()

if __name__ == "__main__":
    main()
