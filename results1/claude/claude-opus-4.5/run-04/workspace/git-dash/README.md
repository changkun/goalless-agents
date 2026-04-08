# git-dash

Compact git repository dashboard. Shows branch, status, sync state, and recent activity in minimal output.

## Install

```bash
pip install -e .
# or just run directly
python git_dash.py
```

## Usage

```bash
git-dash           # Full dashboard
git-dash -o        # One-line summary
git-dash -j        # JSON output
```

## Output

```
main  origin/main
  +2 ~1 ?3  1/0
  Fix login validation  alice, 2 hours ago
  847 commits, 12 contributors
```

**Status symbols:**
- `+N` staged files
- `~N` modified files  
- `?N` untracked files
- `$N` stashes
- `↑N/↓M` ahead/behind upstream

## Why

Standard `git status` is verbose. This gives you the essential info in 4 lines, optimized for quick scanning and token efficiency when used with AI assistants.
