# Pomodoro CLI

A simple command-line Pomodoro timer with session tracking and statistics.

## Usage

```bash
# Start a 25-minute pomodoro (default)
python pomodoro.py start

# Start with custom duration and tag
python pomodoro.py start -d 50 -t "deep-work"

# View statistics for the last 7 days
python pomodoro.py stats

# View statistics for the last 30 days
python pomodoro.py stats -d 30

# Clear all session data
python pomodoro.py clear
```

## Features

- Visual progress bar with countdown
- Session persistence (saves to `~/.pomodoro_sessions.json`)
- Tag-based categorization
- Statistics by time period and tag
- Tracks both completed and cancelled sessions
