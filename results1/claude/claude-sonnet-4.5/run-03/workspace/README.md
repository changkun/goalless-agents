# GW - Git Workflow

A smart CLI tool that simplifies common git workflows with intelligent defaults and minimal typing.

## Installation

```bash
# Make executable
chmod +x gw

# Optional: Add to PATH
sudo cp gw /usr/local/bin/
```

## Features

- 🚀 **Smart commits** - Automatically generates commit messages based on changed files
- 💾 **Quick save** - One command to stage and commit everything
- 🔄 **Easy sync** - Pull and push in one command
- 🌿 **Branch management** - Create, switch, and cleanup branches effortlessly
- 📊 **Enhanced status** - See status and recent commits at a glance

## Quick Start

```bash
# Show status with recent commits
./gw

# Quick save (stages all and commits with timestamp)
./gw save

# Smart add and commit
./gw add
./gw commit

# Sync with remote
./gw sync

# Branch operations
./gw new feature-name
./gw to main
./gw cleanup
```

## Commands

### Status & Info
```bash
gw                  # Show status and recent commits
gw help             # Show help
gw version          # Show version
```

### Working with Changes
```bash
gw add              # Stage all changes
gw commit           # Commit with auto-generated message
gw save             # Stage all + commit with timestamp (fastest)
gw sync             # Pull and push current branch
```

### Branch Management
```bash
gw new <name>       # Create and switch to new branch
gw to [name]        # Switch to branch (shows list if no name)
gw cleanup          # Delete all merged branches
```

### Repository Setup
```bash
gw init             # Initialize new git repo with .gitignore
```

## Examples

### Daily Workflow
```bash
# Start your day
./gw                # Check status

# Work on feature
./gw new feature-x  # Create feature branch
# ... make changes ...
./gw save           # Quick save
./gw sync           # Push to remote

# Go back to main
./gw to main
./gw cleanup        # Clean up merged branches
```

### Smart Commit Messages
```bash
# Edit single file
git add config.json
./gw commit
# → "Update config.json"

# Edit multiple files
git add src/main.py src/utils.py
./gw commit
# → "Update src/main.py, src/utils.py"

# Edit many files
git add src/
./gw commit
# → "Update 15 files"
```

### Quick Operations
```bash
./gw save          # Fastest way to save work
./gw sync          # Fastest way to sync
./gw to main       # Fastest way to switch
```

## Why GW?

**Standard Git:**
```bash
git status
git add .
git commit -m "Update some files"
git pull origin main
git push origin main
```

**With GW:**
```bash
gw save
gw sync
```

## Philosophy

- **Minimal typing**: Common operations in 2-3 keystrokes
- **Smart defaults**: Reasonable behavior without configuration
- **Non-destructive**: Never loses work, safe to use
- **No magic**: Clear about what it's doing
- **Git-compatible**: Works alongside regular git commands

## Requirements

- Python 3.6+
- Git

## Tips

1. Use `gw` (no args) frequently to check status
2. Use `gw save` for quick checkpoints during development
3. Use `gw commit` when you want descriptive messages
4. Use `gw sync` to stay in sync with remote
5. Use `gw cleanup` regularly to keep branches tidy

## License

MIT
