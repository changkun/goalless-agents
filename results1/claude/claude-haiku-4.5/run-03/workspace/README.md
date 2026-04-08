# TaskMan - CLI Task Manager

A modern, fast command-line task manager built with TypeScript. Manage your tasks directly from the terminal with support for priorities, due dates, and persistent storage.

## Installation

Clone the repository and install dependencies:

```bash
npm install
npm run build
```

## Usage

### Add a Task

```bash
npm run start -- add "Task title" [options]
```

Options:
- `-d, --description <text>` - Add a task description
- `-p, --priority <level>` - Set priority: `low`, `medium`, `high` (default: `medium`)
- `-u, --due <date>` - Set due date in YYYY-MM-DD format

Examples:
```bash
npm run start -- add "Buy groceries" -p low
npm run start -- add "Project deadline" -p high -u 2026-04-20
npm run start -- add "Review PR" -d "Check the authentication changes" -p medium
```

### List Tasks

```bash
npm run start -- list [options]
```

Options:
- `--all` - Show all tasks including completed ones (default: show only pending)

Examples:
```bash
npm run start -- list
npm run start -- list --all
```

### Complete a Task

```bash
npm run start -- complete <index>
```

Marks a task as complete. Use the list command to see task indices.

Example:
```bash
npm run start -- complete 0
```

### Delete a Task

```bash
npm run start -- delete <index>
```

Permanently removes a task.

Example:
```bash
npm run start -- delete 2
```

### Clear Completed Tasks

```bash
npm run start -- clear
```

Removes all completed tasks from the list.

## Data Storage

Tasks are stored in `~/.taskman/tasks.json` in JSON format, allowing easy backup and portability.

## Development

Run TypeScript files directly:

```bash
npm run dev -- list
```

Watch mode compilation:

```bash
npm run build
```

## Features

- ✅ Add tasks with priorities and due dates
- ✅ Color-coded priority levels (Red: high, Yellow: medium, Gray: low)
- ✅ Mark tasks complete/incomplete
- ✅ Delete individual tasks or clear all completed
- ✅ Persistent storage in user home directory
- ✅ Full TypeScript type safety
- ✅ Clean CLI interface with helpful error messages
