# 🍅 Pomodoro Timer CLI

A beautiful command-line Pomodoro timer to boost your productivity with the Pomodoro Technique.

## Features

- ⏱️ **Customizable timers** - Default 25-min work, 5-min breaks
- 📊 **Session tracking** - Automatically saves completed and interrupted sessions
- 📈 **Productivity stats** - View your focused work time and completion rates
- 🔔 **Desktop notifications** - Get notified when sessions complete
- 💾 **Persistent history** - All sessions saved to `~/.pomodoro_history.json`
- 🎯 **Simple interface** - Clean, emoji-rich CLI output

## Installation

```bash
chmod +x pomodoro.py
sudo ln -s $(pwd)/pomodoro.py /usr/local/bin/pomodoro
```

Or use it directly:
```bash
python3 pomodoro.py <command>
```

## Usage

### Start a work session (25 minutes)
```bash
pomodoro start
```

### Start a break (5 minutes)
```bash
pomodoro start --break
```

### Custom duration
```bash
pomodoro start --duration 45
```

### Check timer status
```bash
pomodoro status
```

### Stop current timer
```bash
pomodoro stop
```

### View statistics
```bash
# Last 7 days (default)
pomodoro stats

# Last 30 days
pomodoro stats --days 30
```

## How It Works

The Pomodoro Technique is a time management method:

1. 🍅 Work for 25 minutes (one "Pomodoro")
2. ☕ Take a 5-minute break
3. 🔁 Repeat
4. 🌴 After 4 Pomodoros, take a longer 15-minute break

This CLI helps you track and maintain this rhythm, building a history of your focused work time.

## Example Workflow

```bash
# Start your day
$ pomodoro start
🍅 Work session started for 25 minutes
⏰ Will complete at 14:30:00

# Check progress
$ pomodoro status
🍅 Work session in progress
⏱️  Elapsed: 15 min | Remaining: 10 min
📊 Progress: [============        ] 60%
⏰ Completes at: 14:30:00

# Session completes
$ pomodoro status
🎉 Work session completed!
⏱️  Duration: 25 minutes
💡 Time for a short break! (5 min)

# View your productivity
$ pomodoro stats
📊 Pomodoro Statistics (Last 7 days)
==================================================
✅ Completed work sessions: 12
⏹️  Interrupted sessions: 2
⏱️  Total focused time: 300 minutes (5.0 hours)
🎯 Completion rate: 85.7%

📅 Daily breakdown:
  2026-04-18: 🍅🍅🍅 (3)
  2026-04-17: 🍅🍅🍅🍅🍅 (5)
  2026-04-16: 🍅🍅🍅🍅 (4)
```

## Data Storage

- Session history: `~/.pomodoro_history.json`
- Active timer state: `~/.pomodoro_state.json`

Both files are human-readable JSON for easy inspection or backup.

## Requirements

- Python 3.7+
- `notify-send` (optional, for desktop notifications on Linux)

## License

MIT - Do whatever you want with it!
