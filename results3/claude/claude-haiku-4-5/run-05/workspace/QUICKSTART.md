# Quick Start Guide

## Setup

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Optional: Install as a command
pip install -e .
```

## Common Workflows

### Today's Plan
```bash
python task_manager.py add "Review code" -p high
python task_manager.py add "Team standup" -p medium --due 2026-04-09
python task_manager.py add "Fix bug in auth" -p high
python task_manager.py list --priority high
```

### Check Progress
```bash
python task_manager.py stats
python task_manager.py list --status pending
```

### Clean Up
```bash
python task_manager.py complete 1
python task_manager.py delete 2
python task_manager.py list
```

### Find Something
```bash
python task_manager.py search "deploy"
```

## Tips

- **High priority tasks**: Use `-p high` for urgent items
- **Due dates**: Use `--due YYYY-MM-DD` to set deadlines
- **Organize**: Use `list --sort priority` to see most urgent first
- **Track progress**: Run `stats` regularly to see completion percentage
- **Data location**: All tasks stored in `~/.task_manager.json`

## Alias (Optional)

Add to your `.bashrc` or `.zshrc` for faster access:
```bash
alias task='python /path/to/task_manager.py'
```

Then use:
```bash
task add "New task" -p high
task list
task complete 1
```
