# Todo CLI

A fast, lightweight command-line todo manager with persistent JSON storage.

## Features

- ✅ Add, complete, and remove todos
- 📊 View statistics and progress
- 🔍 Filter todos (pending/completed)
- 💾 Persistent storage in `~/.todos/todos.json`
- 📝 Simple, fast CLI interface

## Installation

```bash
npm install
npm run build
npm link
```

Then use `todo` from anywhere.

## Usage

```bash
# Add a todo
todo add "Buy milk"
todo add "Finish project report"

# List all todos
todo list

# List only pending todos
todo list pending

# List only completed todos
todo list completed
todo list done

# Mark a todo as completed
todo done <id>

# Remove a todo
todo rm <id>

# View statistics
todo stats

# Clear all completed todos
todo clear --confirm

# Get help
todo help
```

## Examples

```bash
$ todo add "Fix bug #123"
✓ Added: "Fix bug #123" (1713432891234)

$ todo list
  ☐ Buy milk (1713432891230)
  ☐ Fix bug #123 (1713432891234)

$ todo done 1713432891230
✓ Completed: "Buy milk"

$ todo list pending
  ☐ Fix bug #123 (1713432891234)

$ todo list completed
  ☑ Buy milk (1713432891230)

$ todo stats

Stats:
  Total: 2
  Pending: 1
  Completed: 1
  Progress: 50%
```

## Storage

Todos are stored in JSON format at `~/.todos/todos.json`. Each todo includes:
- `id`: Unique timestamp-based identifier
- `text`: The todo description
- `completed`: Boolean status
- `createdAt`: ISO timestamp of creation
- `completedAt`: ISO timestamp of completion (if completed)

## Development

```bash
npm run dev <command>  # Run with tsx for rapid development
npm run build          # Compile TypeScript
npm test              # Run tests
```
