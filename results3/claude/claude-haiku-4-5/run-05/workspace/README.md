# Task Manager CLI

A simple, powerful command-line task manager to organize your work.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Add a task
```bash
python task_manager.py add "Buy groceries" -p high
python task_manager.py add "Review PR" -p medium --due 2026-04-10
```

### List tasks
```bash
# Show all tasks
python task_manager.py list

# Filter by status
python task_manager.py list --status pending
python task_manager.py list --status done

# Filter by priority
python task_manager.py list --priority high

# Sort by priority or due date
python task_manager.py list --sort priority
python task_manager.py list --sort due
```

### Complete a task
```bash
python task_manager.py complete 1
```

### Delete a task
```bash
python task_manager.py delete 1
```

### Search tasks
```bash
python task_manager.py search "groceries"
```

### View task details
```bash
python task_manager.py show 1
```

### Statistics
```bash
python task_manager.py stats
```

## Features

- **Add tasks** with priority (low/medium/high) and optional due dates
- **List** all tasks with filtering by status and priority
- **Complete** tasks and track progress
- **Delete** tasks you no longer need
- **Search** by title to find specific tasks
- **View detailed** information about any task
- **Statistics** to see your progress at a glance
- **Local storage** - all data saved in `~/.task_manager.json`
- **Sorting** options for better organization

## Task States

- `pending` - Not yet completed
- `done` - Completed task

## Priority Levels

- `low` - Low priority
- `medium` - Medium priority (default)
- `high` - High priority
