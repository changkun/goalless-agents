# Taskly - A Lightweight Task Manager

A fast, minimalist CLI task manager with priorities, due dates, and persistent local storage.

## Features

- ✓ Add tasks with optional priority levels (high, medium, low)
- ✓ Set due dates for deadline tracking
- ✓ Mark tasks as complete
- ✓ Remove tasks
- ✓ Color-coded priority display
- ✓ Local storage (stored in `~/.taskly_tasks.json`)
- ✓ Sort by priority automatically

## Installation

```bash
npm install -g .
```

Or run locally:

```bash
npm start
```

## Usage

### Add a task
```bash
taskly add "Buy groceries"
taskly add "Learn Go" --priority high
taskly add "Research AI" --priority low --due 2026-12-31
```

### List all tasks
```bash
taskly list
```

### Mark a task as complete
```bash
taskly done 1
```

### Remove a task
```bash
taskly remove 2
```

### Clear all completed tasks
```bash
taskly clear
```

## Priority Levels

- **high** (red) - Urgent tasks
- **medium** (yellow) - Regular tasks (default)
- **low** (green) - Low priority tasks

Tasks are automatically sorted by priority when displayed.

## Data Storage

Tasks are stored in JSON format at `~/.taskly_tasks.json`. You can inspect or backup this file directly.

## Running Tests

```bash
npm test
```

All functionality is covered by automated tests including:
- Task creation and ID assignment
- Task completion tracking
- Priority sorting
- Due date handling
- Data persistence
- Error handling
