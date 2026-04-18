# Task Journal

A lightweight, fast command-line tool for logging tasks, organizing them with tags, and generating daily/weekly summaries. Keep your task log close by.

## Features

- **Quick task logging** - Add tasks with one command: `task add "description"`
- **Tag-based organization** - Assign multiple tags to categorize work
- **Smart search** - Find tasks by description or filter by tag
- **Progress reporting** - See daily/weekly completion rates and pending tasks
- **Persistent storage** - Tasks stored locally in `~/.task_journal/`
- **Simple, focused CLI** - No database setup, no dependencies beyond Python 3.7+

## Installation

### Option 1: Direct usage
```bash
python3 task_journal.py add "Your task" --tag work
```

### Option 2: Install globally
```bash
chmod +x task_journal.py
sudo cp task_journal.py /usr/local/bin/task
# Then use: task add "Your task" --tag work
```

### Option 3: Create alias (recommended)
```bash
alias task='python3 /path/to/task_journal.py'
# Add to ~/.bashrc or ~/.zshrc to persist
```

## Usage

### Add a task
```bash
task add "Fix authentication bug" --tag work --tag urgent
task add "Buy milk" --tag personal
```

### List all tasks (most recent first)
```bash
task list
task list --limit 5
```

### Search tasks
```bash
task search "bug"
task search "fix" --tag work
```

### Mark task as completed
```bash
task complete 1
```

### View progress reports
```bash
# Today's summary
task report

# Last 7 days, work tasks only
task report --days 7 --tag work

# Last 30 days
task report --days 30
```

## Task Format

Tasks are stored as JSON in `~/.task_journal/tasks.json`:

```json
{
  "id": 1,
  "description": "Fix authentication bug",
  "tags": ["work", "urgent"],
  "created_at": "2026-04-18T10:16:45.123456",
  "completed": false,
  "completed_at": null
}
```

You can manually edit this file, but it's easier to use the CLI.

## Examples

```bash
# Log tasks as you work
task add "Code review for PR #234" --tag work
task add "Update documentation" --tag work --tag docs
task add "Team standup" --tag work --tag meeting

# Check today's progress
task report

# Mark completed work
task complete 1

# See today's pending work
task report | grep "Pending"

# Find all urgent items
task search "" --tag urgent

# Plan next week
task report --days 7
```

## Storage

Data is stored in `~/.task_journal/tasks.json`. No cloud sync, no accounts—your data stays local.

To backup:
```bash
cp ~/.task_journal/tasks.json ~/backup/tasks.json
```

To share or migrate:
```bash
cp /workspace/task_journal.py ~/.local/bin/
```

## Performance

- Instant startup (no database overhead)
- Search across 1000+ tasks in milliseconds
- JSON storage is human-readable for debugging

## Future ideas

- Shell integration for command execution
- Recurring task templates
- Time tracking per task
- Export to CSV/JSON
- Statistics dashboard
