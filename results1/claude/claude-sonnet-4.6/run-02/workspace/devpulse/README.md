# devpulse

Git repository analytics dashboard for the terminal. Zero dependencies — pure Python 3.11+.

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
┃                               devpulse v0.1.0                                 ┃
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  repo: /your/project   window: last 365 days   generated: 2026-04-08 09:00

┌─ Summary ──────────────────────────────────────────────────────────────────────
  1,432 commits  +89,201 insertions  -43,107 deletions  12 contributors  3.9/day
└────────────────────────────────────────────────────────────────────────────────

┌─ Commit Activity — last 52 weeks ──────────────────────────────────────────────
     AprMayJunJulAugSepOctNovDecJanFebMarApr
     ░░░░  ░░░░  ████  ████  ████  ████  ████
Mon  ░░░░  ████  ████  ████  ████  ████  ████
     ████  ████  ████  ████  ████  ████  ████
...
└────────────────────────────────────────────────────────────────────────────────
```

## What it shows

| Panel | Description |
|---|---|
| **Summary** | Total commits, lines added/deleted, contributors, velocity |
| **Commit Heatmap** | GitHub-style 52-week activity grid with heat intensity |
| **Commit Timing** | Hour-of-day sparkline + day-of-week bar chart |
| **Top Contributors** | Ranked by commits with share percentage |
| **Hottest Files** | Files that change most frequently (churn) |
| **Language Breakdown** | Change distribution by file extension |
| **Recent Commits** | Last 20 commits with age, diff size, and author |

## Usage

```bash
# Analyse current directory
python -m devpulse

# Analyse a specific repo
python -m devpulse /path/to/repo

# Look back further (default is 365 days)
python -m devpulse --days 730

# Skip the heatmap (faster, cleaner output)
python -m devpulse --no-heatmap

# Output JSON for scripting
python -m devpulse --json | jq .summary
```

## Install

```bash
# Run directly
python -m devpulse [path]

# Or install as a command
pip install -e /path/to/devpulse
devpulse [path]
```

## How it works

devpulse makes two git log passes over your history:

1. **Commit metadata pass** — `git log --format=...` to get SHA, author, timestamp, subject
2. **Numstat pass** — `git log --numstat` to count lines added/deleted per file

Both passes are bounded by `--since=N days ago` so even large repos with years of history analyse quickly.

All rendering uses ANSI escape codes and block characters — no third-party libraries needed.
