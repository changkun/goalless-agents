# TASQ Examples

Real-world examples of using TASQ for different workflows.

## Basic Task Management

### Morning standup - what am I working on today?

```bash
$ tasq list --status pending
```

Shows all tasks you haven't completed yet.

## Project-Based Workflow

### Organize tasks by project

```bash
# Add tasks to different projects
$ tasq add "Design API schema" --project backend --priority high
$ tasq add "Create React component library" --project frontend
$ tasq add "Write integration tests" --project qa --priority high
```

### View backend tasks only

```bash
$ tasq list --project backend
```

### Mark backend tasks as done

```bash
$ tasq done 1
$ tasq done 2
```

## Priority-Based Workflow

### Add tasks with different priorities

```bash
$ tasq add "Fix critical bug" --priority high
$ tasq add "Refactor old code" --priority low
$ tasq add "Review PR" --priority normal
```

### Sort by priority to see what's urgent

```bash
$ tasq list --sort priority
```

Output shows high priority tasks first, making it clear what needs attention.

## Sprint/Milestone Planning

### Create tasks for a sprint

```bash
$ tasq add "API endpoint - user auth" --project sprint-5 --priority high
$ tasq add "Database migrations" --project sprint-5 --priority high
$ tasq add "Frontend form validation" --project sprint-5 --priority normal
$ tasq add "Update documentation" --project sprint-5 --priority low
```

### Track sprint progress

```bash
$ tasq stats
```

Shows completion percentage across all projects, helping you see sprint health at a glance.

### Clear completed sprint tasks

```bash
$ tasq list --project sprint-5 --status done
$ tasq delete 5
$ tasq delete 8
$ tasq delete 12
```

## Integration Examples

### Count pending tasks from shell scripts

```bash
#!/bin/bash
pending=$(python3 tasq.py list --status pending | tail -1 | grep -oP 'Pending: \K\d+')
echo "You have $pending pending tasks"
```

### Add task from anywhere in your shell

```bash
alias t="python3 /path/to/tasq.py add"
t "Remember this idea"
t "Call the dentist"
```

### Backup your tasks

```bash
# One-time backup
cp ~/.tasq_tasks.json ~/backups/tasks-$(date +%Y%m%d).json

# Restore from backup
cp ~/backups/tasks-20260101.json ~/.tasq_tasks.json
```

## Daily Workflow Example

```bash
# Morning: See what you need to do
$ tasq list --status pending --sort priority

# Add new urgent task
$ tasq add "Fix production issue" --priority high

# During day: Mark tasks complete as you finish them
$ tasq done 7
$ tasq done 12

# Evening: Review progress
$ tasq stats
```

## Cleanup

### Remove completed tasks you no longer need

```bash
$ tasq list --status done
$ tasq delete 1
$ tasq delete 3
```

### Clear old completed tasks from a project

```bash
# See what's in the project
$ tasq list --project old-project

# Delete completed ones manually
$ tasq delete 15
```
