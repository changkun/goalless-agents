# Pomodoro Timer CLI

A terminal-based productivity timer using the Pomodoro Technique. Features work sessions, breaks, task tracking, and persistent history.

## Usage

```bash
# Start a pomodoro session
python3 pomodoro.py

# Start with a task name
python3 pomodoro.py -t "Write documentation"

# View session history (last 7 days)
python3 pomodoro.py history

# View history for last 30 days
python3 pomodoro.py history -d 30

# View all-time statistics
python3 pomodoro.py stats

# Demo mode (shortened timers for testing)
python3 pomodoro.py --demo
```

## How It Works

- **Work sessions**: 25 minutes of focused work
- **Short breaks**: 5 minutes after each work session
- **Long breaks**: 15 minutes after every 4 pomodoros
- Press `Ctrl+C` to stop at any time

## Features

- Visual progress bar with countdown
- Terminal bell notifications when sessions end
- Persistent history saved to `~/.pomodoro_history.json`
- Task tracking and statistics
- Streak tracking for daily productivity

## Requirements

Python 3.10+ (no external dependencies)
