# TASQ - Task Manager CLI

A lightweight, efficient command-line task manager with project organization, priority levels, and persistent storage.

## Features

- ✨ **Simple & Fast** - Minimal overhead, instant task management
- 📁 **Projects** - Organize tasks by project
- ⚡ **Priorities** - Tag tasks as high, normal, or low priority
- 💾 **Persistent** - All tasks stored locally in `~/.tasq_tasks.json`
- 📊 **Statistics** - View progress across projects and priorities
- 🔍 **Filtering** - Filter by project, status, and sort by creation date or priority

## Installation

1. Clone or download the repository
2. Make the script executable:
   ```bash
   chmod +x tasq.py
   ```
3. Optionally, add to your PATH for global access:
   ```bash
   ln -s $(pwd)/tasq.py /usr/local/bin/tasq
   ```

## Usage

### Add a task
```bash
./tasq.py add "Buy groceries"
./tasq.py add "Implement auth" --project backend --priority high
./tasq.py add "Fix typo" --project docs --priority low
```

### List tasks
```bash
./tasq.py list                                    # Show all tasks
./tasq.py list --project backend                 # Filter by project
./tasq.py list --status pending                  # Show only pending tasks
./tasq.py list --status done                     # Show only completed tasks
./tasq.py list --sort priority                   # Sort by priority (high to low)
./tasq.py list --project backend --status pending # Combine filters
```

### Complete a task
```bash
./tasq.py done 1    # Mark task #1 as complete
```

### Delete a task
```bash
./tasq.py delete 1  # Delete task #1
```

### View statistics
```bash
./tasq.py stats     # Show progress and breakdown by project/priority
```

## Data Storage

All tasks are stored in `~/.tasq_tasks.json` as a simple JSON file. You can backup, share, or edit this file directly if needed.

## Why TASQ?

- **No cloud dependency** - All data stays on your machine
- **Fast** - No network latency, instant operations
- **Scriptable** - Easy to integrate with shell scripts and automation
- **Transparent** - Plain JSON format you can inspect anytime
- **Minimal** - ~200 lines of pure Python, no dependencies
