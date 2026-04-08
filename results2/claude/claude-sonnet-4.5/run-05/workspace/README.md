# TaskMan - Terminal Task Manager

A simple, powerful CLI task manager with local JSON storage.

## Features

- ✅ Add tasks with priorities (low/medium/high) and tags
- 📋 List tasks with filtering by status, priority, or tags
- ✓ Mark tasks as complete
- 🗑️ Delete tasks
- 📊 View task statistics
- 🎨 Color-coded terminal output

## Installation

```bash
# Make the script executable
chmod +x taskman.py

# Optional: Create an alias in your shell config
alias taskman='python3 /path/to/taskman.py'
```

## Usage

### Add a task
```bash
./taskman.py add "Write project documentation"
./taskman.py add "Fix bug in login" -p high
./taskman.py add "Refactor API" -p low -t backend refactor
```

### List tasks
```bash
./taskman.py list                  # Show pending tasks
./taskman.py list -a               # Show all tasks (including completed)
./taskman.py list -p high          # Show only high priority tasks
./taskman.py list -t backend       # Show tasks with 'backend' tag
```

### Complete a task
```bash
./taskman.py complete 1
```

### Delete a task
```bash
./taskman.py delete 2
```

### View statistics
```bash
./taskman.py stats
```

## Storage

Tasks are stored in `~/.taskman.json` by default.

## Examples

```bash
# Add some tasks
./taskman.py add "Deploy to production" -p high -t deployment urgent
./taskman.py add "Update dependencies" -p medium -t maintenance
./taskman.py add "Write tests" -p high -t testing

# View pending tasks
./taskman.py list

# Complete a task
./taskman.py complete 1

# Check stats
./taskman.py stats
```
