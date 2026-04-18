# Task Timer CLI

A lightweight terminal-based task timer with statistics and persistent storage. Track time spent on different tasks, view statistics, and analyze your productivity.

## Features

- ⏱️ Start and stop tasks with simple commands
- 📊 View detailed statistics per task (count, total time, average time)
- 💾 Persistent storage in `~/.task-timer/tasks.json`
- 🎨 Colored terminal output for better readability
- 📈 Quick overview of active and completed tasks

## Installation

```bash
npm install
npm run build
```

## Usage

### Quick Setup
For easier command-line usage, you can alias the CLI:
```bash
alias timer="./task-timer.sh"
```

Then use commands like:
```bash
timer start "Writing documentation"
timer stop
timer status
timer stats
timer list
```

### Full Usage

### Start a task
```bash
npm start -- start "Writing documentation"
./task-timer.sh start "Writing documentation"
```

### Stop the current task
```bash
npm start -- stop
./task-timer.sh stop
```

### View active task
```bash
npm start -- status
./task-timer.sh status
```

### View statistics
```bash
npm start -- stats
./task-timer.sh stats
```

### List recent sessions
```bash
npm start -- list
./task-timer.sh list
```

### Get help
```bash
npm start -- help
./task-timer.sh help
```

## Development

Run in development mode with hot reload:
```bash
npm run dev -- start "My task"
```

## Data Storage

All task data is stored in `~/.task-timer/tasks.json`. The file is automatically created on first use.
