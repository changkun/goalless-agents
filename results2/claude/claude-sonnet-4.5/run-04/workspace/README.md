# smartask 🎯

A smart CLI task manager with natural language parsing. Manage your tasks using everyday language!

## Features

- **Natural Language Input**: Add tasks using phrases like "buy milk tomorrow at 3pm"
- **Smart Date Parsing**: Understands "today", "tomorrow", day names, "in 3 days", "next week"
- **Time Parsing**: Extracts times like "at 3pm", "15:00", "3:30pm"
- **Priority Levels**: Automatically detects high/medium/low priority from keywords
- **Clean CLI**: Simple commands with pretty output
- **Persistent Storage**: Tasks saved to `~/.smartask.json`

## Installation

```bash
chmod +x smartask.py
# Optional: link to make it globally available
sudo ln -s $(pwd)/smartask.py /usr/local/bin/smartask
```

## Usage

### Add Tasks

```bash
# Simple task
./smartask.py add buy groceries

# With due date
./smartask.py add buy milk tomorrow

# With time
./smartask.py add meeting with team tomorrow at 3pm

# With priority
./smartask.py add fix critical bug urgent

# Complex example
./smartask.py add finish project report by Friday at 5pm high priority
```

### List Tasks

```bash
# List all active tasks
./smartask.py list

# Include completed tasks
./smartask.py list --all

# Show only today's tasks
./smartask.py list --today

# Show only overdue tasks
./smartask.py list --overdue
```

### Complete Tasks

```bash
# Mark task 0 as complete
./smartask.py complete 0
```

### Delete Tasks

```bash
# Delete task 1
./smartask.py delete 1
```

## Natural Language Examples

The parser understands:

- **Dates**: today, tomorrow, Monday-Sunday, in 3 days, next week
- **Times**: at 3pm, 15:00, 3:30pm, at 10am
- **Priority**: urgent, important, high, critical (→ high), low, maybe, someday (→ low)

## Examples

```bash
./smartask.py add call dentist tomorrow at 2pm
./smartask.py add review PR urgent
./smartask.py add vacation planning maybe
./smartask.py add team standup Monday at 10am
./smartask.py add submit taxes in 5 days important
```

## Storage

Tasks are stored in `~/.smartask.json` as JSON for easy backup and portability.
