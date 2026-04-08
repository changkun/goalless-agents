# 🍅 Pomodoro Timer

A beautiful terminal-based Pomodoro timer with session tracking and statistics.

## Features

- ⏱️  **Classic Pomodoro Technique**: 25-minute focus sessions, 5-minute breaks
- 📊 **Session Tracking**: Automatically saves completed sessions
- 📈 **Statistics**: View today's, weekly, and all-time session counts
- 🎨 **Colorful Interface**: Beautiful terminal UI with emojis and colors
- ⏸️  **Pause/Resume**: Full control over your sessions
- 🔔 **Notifications**: Audio alert when sessions complete

## Installation

```bash
chmod +x pomodoro.py
```

## Usage

### Start a Pomodoro session
```bash
./pomodoro.py
```

### View statistics
```bash
./pomodoro.py stats
```

### Reset all data
```bash
./pomodoro.py reset
```

## Controls

While the timer is running:
- `p` - Pause current session
- `r` - Resume paused session
- `s` - Skip current session
- `q` - Quit timer
- `Ctrl+C` - Exit immediately

## How It Works

1. **Focus Session** (25 minutes) - Deep work time 🍅
2. **Short Break** (5 minutes) - Rest and recharge ☕
3. After 4 focus sessions, take a **Long Break** (15 minutes)

All completed sessions are saved to `~/.pomodoro_data.json` for statistics tracking.

## Statistics

Track your productivity with automatic statistics:
- Sessions completed today
- Sessions completed this week
- Total sessions all time
- Total focus time in minutes

## Customization

Edit `pomodoro.py` to adjust:
- `FOCUS_TIME` - Duration of focus sessions (default: 25 minutes)
- `BREAK_TIME` - Duration of short breaks (default: 5 minutes)
- `LONG_BREAK_TIME` - Duration of long breaks (default: 15 minutes)
- `SESSIONS_BEFORE_LONG_BREAK` - Sessions before long break (default: 4)

## Data Storage

Session data is stored in JSON format at `~/.pomodoro_data.json`

## Requirements

- Python 3.6+
- Terminal with ANSI color support

## License

MIT
