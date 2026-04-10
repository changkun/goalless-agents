# 🍅 Pomodoro Timer

A beautiful terminal-based Pomodoro timer to boost your productivity!

## Features

- ⏱️  **Classic Pomodoro**: 25-min work sessions with 5-min breaks
- 🎨 **Visual Progress**: Animated progress bar with colorful display
- 📊 **Session Tracking**: Automatic history logging
- 🔔 **Audio Alerts**: Terminal bell notifications
- ⏸️  **Pause/Resume**: Press Ctrl+C once to pause, twice to quit
- 📈 **Statistics**: View your daily and total productivity stats

## Usage

### Start a Pomodoro session:
```bash
python3 pomodoro.py
```

### View your statistics:
```bash
python3 pomodoro.py stats
```

## How It Works

1. **Work Session**: Focus for 25 minutes 🍅
2. **Short Break**: Rest for 5 minutes ☕
3. **Repeat**: After 4 work sessions, take a 15-minute long break
4. **Track**: All sessions are saved to `~/.pomodoro_history.json`

## Controls

- **During timer**: Press `Ctrl+C` once to pause, press `Enter` to resume
- **To quit**: Press `Ctrl+C` twice

## Customization

Create a config file at `~/.pomodoro.config.json` to customize durations:

```json
{
  "work_duration_minutes": 25,
  "break_duration_minutes": 5,
  "long_break_duration_minutes": 15,
  "sessions_until_long_break": 4
}
```

See `.pomodoro.config.example.json` for a template.

## Installation

Make the script executable:
```bash
chmod +x pomodoro.py
```

Optionally, move it to your PATH:
```bash
sudo cp pomodoro.py /usr/local/bin/pomodoro
```

Then run it from anywhere:
```bash
pomodoro
```

## The Pomodoro Technique

The Pomodoro Technique is a time management method that uses a timer to break work into focused intervals (traditionally 25 minutes) separated by short breaks. This helps maintain high levels of focus and prevents burnout.

Happy focusing! 🚀
