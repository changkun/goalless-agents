# 🍅 Pomodoro Timer CLI

A beautiful command-line Pomodoro timer with built-in task management and productivity statistics.

## Features

- **⏱️ Classic Pomodoro Technique**: 25-minute focus sessions, 5-minute short breaks, 15-minute long breaks (every 4 sessions)
- **📝 Task Management**: Add, list, and track tasks with pomodoro counts
- **📊 Statistics**: Track your productivity with session counts and completion rates
- **💾 Persistent Storage**: All data saved automatically to `~/.pomodoro_data.json`
- **🔔 Desktop Notifications**: Get notified when sessions and breaks complete (works on Linux, macOS, and Windows)
- **🎨 Beautiful CLI**: Progress bars and emoji indicators for a pleasant experience

## Installation

Simply make the script executable:

```bash
chmod +x pomodoro.py
```

Or create a symlink for easy access:

```bash
ln -s /workspace/pomodoro.py /usr/local/bin/pomodoro
```

## Usage

### Start a Pomodoro Session
```bash
./pomodoro.py start
```

The timer will run through:
1. 25 minutes of focused work
2. A short break (5 min) or long break (15 min after 4 sessions)
3. Automatically track your progress

Press `Ctrl+C` to pause the timer at any time.

### Add a Task
```bash
./pomodoro.py add "Write project documentation"
```

### List Active Tasks
```bash
./pomodoro.py list
```

Output example:
```
📝 Active Tasks:
  → [1] Write project documentation (3 🍅)
    [2] Code review for PR #42 (1 🍅)
    [3] Refactor authentication module (0 🍅)
```

The `→` indicates your current active task.

### Set Current Task
```bash
./pomodoro.py work 2
```

This sets task #2 as your current focus. Pomodoros will be counted toward this task.

### Complete a Task
```bash
./pomodoro.py done 1
```

### View Statistics
```bash
./pomodoro.py stats
```

Output example:
```
📊 Pomodoro Statistics
========================================
Total sessions completed: 12 🍅
Total focused time: 300 minutes
Today's sessions: 4 🍅
Tasks completed: 3

✓ Completed Tasks:
  • Write project documentation (3 🍅)
  • Code review for PR #42 (2 🍅)
```

## The Pomodoro Technique

The Pomodoro Technique is a time management method:

1. **Choose a task** you want to work on
2. **Set the timer** for 25 minutes (one "Pomodoro")
3. **Work** on the task until the timer rings
4. **Take a short break** (5 minutes)
5. Every 4 Pomodoros, take a **longer break** (15 minutes)

## Data Storage

All your tasks and session history are stored in `~/.pomodoro_data.json`. This includes:
- Task list with pomodoro counts
- Completed session timestamps
- Current task selection
- Task completion history

## Tips for Maximum Productivity

- 🎯 **Start your day** by listing 3-5 key tasks
- 🔕 **Eliminate distractions** during focus time
- ✅ **Track progress** with the stats command
- 🎉 **Celebrate** completed pomodoros and tasks
- 📈 **Review your stats** weekly to see improvements

## Example Workflow

```bash
# Morning: Plan your day
./pomodoro.py add "Write feature specification"
./pomodoro.py add "Implement user authentication"
./pomodoro.py add "Write unit tests"
./pomodoro.py list

# Start working on first task
./pomodoro.py work 1
./pomodoro.py start

# After completing that task
./pomodoro.py done 1

# End of day: Review progress
./pomodoro.py stats
```

## Requirements

- Python 3.6 or higher
- No external dependencies required!

### Desktop Notifications

Desktop notifications work out-of-the-box on:
- **Linux**: Uses `notify-send` (pre-installed on most distributions)
- **macOS**: Uses `osascript` (built-in)
- **Windows**: Uses PowerShell notifications (built-in on Windows 10+)

If notifications aren't available on your system, the timer will continue to work normally without them.

## License

MIT License - Feel free to use and modify as needed!
