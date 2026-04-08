# devlog

A simple, fast CLI tool for developers to track their daily work, learnings, and decisions.

## Features

- **Quick logging**: Add entries with a single command
- **Tagging**: Organize entries with tags
- **Search**: Find entries by keyword
- **Daily summaries**: View today's activity
- **Statistics**: Track your logging habits

## Installation

```bash
# Make executable
chmod +x devlog.py

# Optional: Create symlink for easy access
ln -s $(pwd)/devlog.py /usr/local/bin/devlog
```

## Usage

### Add an entry
```bash
./devlog.py add "Fixed authentication bug in login flow" -t bug fix
./devlog.py add "Learned about Rust lifetimes" -t learning rust
```

### View today's entries
```bash
./devlog.py today
```

### List recent entries
```bash
./devlog.py list --limit 10
./devlog.py list --tag learning
```

### Search entries
```bash
./devlog.py search "authentication"
```

### View statistics
```bash
./devlog.py stats
```

## Storage

Entries are stored in `~/.devlog/entries.json` as JSON for easy backup and portability.

## Examples

```bash
# Morning standup prep
./devlog.py today

# Log a bug fix
./devlog.py add "Resolved memory leak in worker pool" -t bug performance

# Track learning
./devlog.py add "Read about PostgreSQL EXPLAIN ANALYZE" -t learning database

# End of day review
./devlog.py today

# Find all security-related work
./devlog.py list --tag security

# Search for specific work
./devlog.py search "API"
```

## Why devlog?

- **Accountability**: Track what you actually work on
- **Learning log**: Remember what you've learned
- **Decision journal**: Document why you made certain choices
- **Career development**: Review your growth over time
- **Standup prep**: Quickly recall yesterday's work

## License

MIT
