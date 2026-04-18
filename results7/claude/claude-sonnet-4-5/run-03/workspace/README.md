# 🍅 Pomodoro Timer

A beautiful CLI-based Pomodoro Timer to boost your productivity with the proven Pomodoro Technique.

## Features

- ✨ Beautiful terminal UI with real-time progress visualization
- 🍅 Classic 25-minute work sessions
- ☕ 5-minute short breaks
- 🌴 15-minute long breaks after every 4 sessions
- 📊 Session tracking
- ⚙️ Customizable durations
- 🎨 Color-coded sessions (work vs break)

## Installation

```bash
pip install -r requirements.txt
```

Or use the convenience wrapper (handles venv automatically):
```bash
./pomo
```

## Usage

### Basic usage (default: 25 min work, 5 min break)
```bash
./pomo
# or
python pomodoro.py
```

### Custom durations
```bash
# 50 minute work sessions, 10 minute breaks
python pomodoro.py --work 50 --break 10

# 25 minute work, 5 min break, 20 min long break
python pomodoro.py -w 25 -b 5 -l 20
```

### Options

- `-w, --work`: Work session duration in minutes (default: 25)
- `-b, --break`: Short break duration in minutes (default: 5)
- `-l, --long-break`: Long break duration in minutes (default: 15)
- `-s, --sessions`: Number of sessions before long break (default: 4)

## The Pomodoro Technique

1. Choose a task
2. Work for 25 minutes (one Pomodoro)
3. Take a 5-minute break
4. After 4 Pomodoros, take a longer 15-minute break
5. Repeat!

## Controls

- `Ctrl+C` - Pause/Stop the timer

## Example

```bash
$ python pomodoro.py
╭─ 🍅 Pomodoro Timer ─────────────────────────╮
│                                             │
│  🍅 WORK SESSION                            │
│                                             │
│            24:53                            │
│                                             │
│  ████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░  │
│                                             │
│  Sessions completed: 0                      │
│                                             │
╰─────────────────────────────────────────────╯
```

Stay focused! 🚀
