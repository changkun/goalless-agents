# 🍅 Pomodoro Timer with Task Tracking

A beautiful terminal-based Pomodoro timer to boost your productivity. Track your focus sessions, take regular breaks, and build better work habits.

## Features

- ⏱️  **25-minute focus sessions** with visual progress bar
- ☕ **Automatic break scheduling** (5min short, 15min long breaks)
- 📊 **Task tracking and statistics** - see your productivity over time
- 💾 **Persistent history** - all sessions saved automatically
- 🎨 **Clean terminal UI** with progress visualization

## Quick Start

```bash
# Start a Pomodoro session
python3 pomodoro.py start "Write documentation"

# View your statistics
python3 pomodoro.py stats

# Get help
python3 pomodoro.py help
```

## How It Works

1. **Focus**: Work for 25 minutes on your task
2. **Break**: Take a 5-minute break after each session
3. **Long Break**: Every 4 sessions, take a 15-minute break
4. **Track**: All sessions are automatically saved

## Example Session

```
🍅 Starting Pomodoro: Write documentation
Focus for 25 minutes

Work #1 [██████████████████████████████] 00:00 Complete! ✓

✨ Great work! Time for a 5 minute break
Take short break? (y/n/q to quit): y
Short Break [██████████████████████████████] Complete! ✓

📊 Session complete: 1 pomodoro(s) on 'Write documentation'
```

## Statistics

Track your productivity with built-in stats:
- Total Pomodoros completed
- Tasks completed by date
- Recent activity timeline
- Task history

## Data Storage

All data is stored in `~/.pomodoro_data.json` for persistence across sessions.

## Tips

- Use descriptive task names to track what you're working on
- Press Ctrl+C to stop early if needed
- Review your stats regularly to see your progress
- Take breaks seriously - they improve focus!

---

Built with ❤️ for focused work
