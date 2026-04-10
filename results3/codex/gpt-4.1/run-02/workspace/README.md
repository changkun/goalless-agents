# Python Todo CLI App

A minimal command-line todo list manager using only the Python standard library. Items are stored in `~/.todo_items.json`.

## Usage

```sh
cd todo_app
python3 cli.py add "Buy groceries"
python3 cli.py list
python3 cli.py done 1
python3 cli.py list
```

- `add <task>`: Adds a new todo item
- `list`: Lists all todo items
- `done <number>`: Marks the numbered item as complete

## Extending
You can add features (delete, search, categories) by editing the Python files.
