# tiny-task (tt)

A minimalist, zero-dependency Node.js CLI task manager.

## Installation

```bash
# In the project directory
npm link
```

## Usage

```bash
# Add a task
tt add "Buy groceries"

# List tasks
tt ls

# Mark task as completed
tt done 1

# Remove task
tt rm 1
```

## Persistence

Tasks are saved in `~/.tt-tasks.json`.
