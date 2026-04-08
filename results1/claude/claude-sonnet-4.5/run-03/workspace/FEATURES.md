# GW Features & Design

## Core Philosophy

**Minimize keystrokes, maximize clarity**

GW reduces common git workflows from 5+ commands to 1-2, while being transparent about what it does.

## Feature Comparison

### Standard Git vs GW

| Task | Standard Git | GW | Savings |
|------|-------------|-----|---------|
| Quick checkpoint | `git add . && git commit -m "wip"` | `gw save` | 75% |
| Sync with remote | `git pull origin main && git push origin main` | `gw sync` | 80% |
| Create branch | `git checkout -b feature-x` | `gw new feature-x` | 50% |
| Switch branch | `git checkout main` | `gw to main` | 45% |
| Check status | `git status` | `gw` | 60% |
| Commit changes | `git add file.txt && git commit -m "Update file.txt"` | `gw add && gw commit` | 55% |

## Smart Features

### 1. Auto-Generated Commit Messages

GW generates context-aware commit messages:

```bash
# Single file
git add config.json
gw commit
# → "Update config.json"

# Few files
git add src/app.py src/utils.py
gw commit
# → "Update src/app.py, src/utils.py"

# Many files
git add src/
gw commit
# → "Update 15 files"
```

### 2. Enhanced Status

Shows both status and recent commits:

```bash
$ gw
🌿 Branch: feature-x
📝 Changes:
 M src/app.py
?? test.py

📜 Recent commits:
   a1b2c3d Add user authentication
   e4f5g6h Update database schema
   h7i8j9k Fix login bug
```

### 3. Safe Branch Cleanup

Only deletes branches that are fully merged:

```bash
$ gw cleanup
🧹 Cleaning up 3 merged branch(es):
   Deleting old-feature
   Deleting bugfix-123
   Deleting hotfix-db
✅ Cleaned up
```

### 4. Smart Sync

Handles pull and push together, with error handling:

```bash
$ gw sync
🔄 Syncing branch 'main'...
⬇️  Pulling...
⬆️  Pushing...
✅ Synced
```

### 5. Quick Save

Fastest way to checkpoint work:

```bash
$ gw save
📦 Staging changes...
✅ Staged 5 file(s)
💾 Quick save: 2026-04-08 10:30:00
✅ Saved
```

## Design Decisions

### Why These Commands?

- **`gw` (no args)**: Most frequent operation - checking status
- **`gw save`**: Fastest checkpoint during active development
- **`gw add`/`gw commit`**: More deliberate commits
- **`gw sync`**: One command for two-way remote sync
- **`gw new`/`gw to`**: Shortest branch operations
- **`gw cleanup`**: Housekeeping made easy

### What GW Doesn't Do

GW focuses on common operations. For complex git operations, use git directly:

- Interactive rebasing
- Cherry-picking
- Stash management
- Submodules
- Complex merges
- History rewriting

GW and git work perfectly together.

### Error Handling

GW is non-destructive and clear about errors:

```bash
$ gw commit
❌ No staged files. Use 'gw add' or 'git add' first.

$ gw sync
⚠️  Pull had conflicts, resolve manually
```

### Visual Design

- 🌿 Branches
- 📝 Changes
- 💾 Saves/commits
- 🔄 Sync operations
- ✅ Success
- ❌ Errors
- ⚠️  Warnings
- 🧹 Cleanup

Clear visual indicators make scanning output fast.

## Performance

GW is a thin Python wrapper around git - negligible overhead:

- Typical command: < 50ms added latency
- No background processes
- No configuration files to parse
- Direct git command execution

## Future Ideas

Potential enhancements (not yet implemented):

- `gw undo`: Undo last commit (keep changes)
- `gw amend`: Amend last commit
- `gw wip`: Work-in-progress commit
- `gw sync --all`: Sync all branches
- `gw log`: Enhanced git log
- `gw diff`: Enhanced git diff
- Template support for commit messages
- Hook support for custom workflows

## Why Not Use Git Aliases?

Git aliases are great, but limited:

1. **No complex logic**: Aliases can't generate smart commit messages
2. **No error handling**: Aliases can't provide helpful error messages  
3. **No state checking**: Aliases can't adapt based on repo state
4. **Limited composition**: Aliases can't easily combine multiple operations

GW provides a richer scripting environment while staying simple.

## Compatibility

- **Git version**: 2.0+
- **Python**: 3.6+
- **OS**: Linux, macOS, Windows (via WSL or Git Bash)
- **Works with**: Any git repository
- **Conflicts with**: None - uses standard git commands

## Installation Options

```bash
# Local use
chmod +x gw
./gw

# Global install
sudo cp gw /usr/local/bin/
gw

# Per-project
cp gw ~/projects/myproject/
cd ~/projects/myproject
./gw

# Alias (in ~/.bashrc or ~/.zshrc)
alias gw='/path/to/gw'
```

## Testing

```bash
# Run the demo
./demo.sh

# Manual testing
cd /tmp
mkdir test-repo
cd test-repo
/path/to/gw init
echo "test" > file.txt
/path/to/gw save
/path/to/gw
```

## Contributing Ideas

While this is a simple tool, potential contributions:

- Better commit message templates
- Configuration file support
- Plugin system
- Integration with GitHub CLI
- Emoji toggles for different preferences
- Color scheme options
- Windows native support
