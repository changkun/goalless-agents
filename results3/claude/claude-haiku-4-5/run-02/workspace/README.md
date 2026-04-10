# Noter - CLI Note Manager

A lightweight command-line application for managing notes with full-text search, tagging, and persistent local storage.

## Features

- **Create notes** with titles, content, and multiple tags
- **Full-text search** across title, content, and tags
- **Tag management** - organize notes by categories
- **Persistent storage** - notes stored in SQLite database at `~/.noter/notes.db`
- **Fast search** - indexed tag lookups for quick filtering

## Installation

```bash
npm install
npm start -- help
```

## Usage

### Create a note
```bash
node src/index.js create "Shopping List" "milk, eggs, bread" grocery
node src/index.js create "Meeting Notes" "Discuss Q2 goals" work
```

### List all notes
```bash
node src/index.js list
```

### Search notes
```bash
node src/index.js search "milk"
node src/index.js search "work"
```

### View a specific note
```bash
node src/index.js view 1
```

### View notes by tag
```bash
node src/index.js tag grocery
node src/index.js tag work
```

### List all tags
```bash
node src/index.js tags
```

### Delete a note
```bash
node src/index.js delete 1
```

## Database

Notes are stored in SQLite at `~/.noter/notes.db`. The database includes:
- `notes` table with id, title, content, tags, created_at, updated_at
- `note_tags` table for indexed tag lookups
- Full-text search across all fields

## Run Tests

```bash
npm test
```

## Project Structure

```
.
├── src/
│   ├── index.js      # CLI entry point
│   ├── cli.js        # Command handlers & formatting
│   ├── db.js         # Database operations
│   └── test.js       # Test suite
└── package.json
```

## Technologies

- **better-sqlite3** - Fast, embedded SQL database
- **chalk** - Terminal color output
- **Node.js** - Runtime
