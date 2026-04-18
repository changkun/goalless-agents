# Quick Task — Lightweight CLI Task Manager

A fast, simple command-line task manager for your terminal. Store tasks with priorities and due dates, search them instantly, and track progress.

## Install

```bash
chmod +x task.py
# Optional: Link to your PATH
ln -s $(pwd)/task.py ~/.local/bin/task
```

## Usage

### Add tasks
```bash
./task.py add 'Buy groceries'
./task.py add 'Fix critical bug' --priority high
./task.py add 'Call mom' --due 2026-05-15
```

### View tasks
```bash
./task.py list              # Show all pending tasks
./task.py list --priority high
./task.py list --all        # Include completed tasks
```

### Manage tasks
```bash
./task.py complete 1        # Mark task #1 complete
./task.py delete 2          # Delete task #2
./task.py search 'bug'      # Find tasks matching "bug"
```

## Features

- ✨ Minimal, focused CLI
- 💾 Persistent JSON storage in `~/.tasks.json`
- 🎯 Priorities: low, medium, high
- 📅 Due dates (YYYY-MM-DD format)
- 🔍 Search by keyword
- 📊 Auto-sort by priority and completion status
- ⚡ No dependencies, pure Python

## Data Format

Tasks are stored in `~/.tasks.json`:
```json
{
  "id": 1,
  "title": "Buy groceries",
  "priority": "medium",
  "due_date": "2026-05-01",
  "completed": false,
  "created": "2026-04-18T10:15:30.123456"
}
```
