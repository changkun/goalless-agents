# 🍅 Pomodoro Task Manager

A beautiful terminal-based productivity tool that combines task management with the Pomodoro Technique.

```
╭─────────────────────────────╮
│ 🍅 Pomodoro Task Manager    │
│ Stay focused, get things!   │
╰─────────────────────────────╯

         📋 Your Tasks         
╭────┬────────┬──────────────┬────╮
│ ID │ Status │ Task         │ 🍅 │
├────┼────────┼──────────────┼────┤
│ 1  │   ✓    │ Write code   │ 3  │
│ 2  │   ○    │ Write docs   │ 1  │
╰────┴────────┴──────────────┴────╯

🍅 Pomodoros completed today: 4
```

## Features

- ✅ **Task Management**: Add, complete, and delete tasks
- 🍅 **Pomodoro Timer**: 25-minute focus sessions with 5-minute breaks
- 📊 **Progress Tracking**: Track pomodoros per task and daily totals
- 💾 **Persistent Storage**: Tasks and stats saved automatically
- 🎨 **Beautiful UI**: Rich terminal interface with colors and progress bars
- 🔔 **Desktop Notifications**: Get notified when sessions complete, even in other apps

## The Pomodoro Technique

1. Pick a task to work on
2. Work for 25 minutes (one "pomodoro")
3. Take a 5-minute break
4. After 4 pomodoros, take a longer 15-30 minute break

## Quick Start

```bash
# Easy setup (recommended)
./setup.sh

# Then activate and run
source venv/bin/activate
python pomodoro.py
```

Or manually:
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the app
python pomodoro.py
```

## Usage

1. **Add tasks** - Create your todo list
2. **Start a pomodoro** - Pick a task and focus for 25 minutes
3. **Take breaks** - Rest during breaks to maintain productivity
4. **Complete tasks** - Mark them done when finished
5. **Track progress** - See how many pomodoros you've completed

## Commands

- `a` - Add a new task
- `s` - Start a pomodoro (work session)
- `c` - Complete a task
- `d` - Delete a task
- `q` - Quit

## Data Storage

Tasks and stats are stored in `~/.pomodoro_tasks.json`

## Desktop Notifications

Desktop notifications work out-of-the-box on most systems:
- **Windows**: Native notification support
- **macOS**: Native notification center
- **Linux**: Requires `notify-send` (usually pre-installed on desktop environments)

If notifications don't appear, the app will continue to work normally with audio alerts.

## Tips for Success

- 🎯 Be specific with task descriptions
- 🔕 Eliminate distractions during work sessions
- ☕ Actually take the breaks - they help you stay fresh
- 📈 Track your daily pomodoro count to measure productivity
- 🔁 Adjust task size if it takes too many pomodoros

## Example Workflow

```
1. Add task: "Write project proposal"
2. Start pomodoro on task #1
3. Work focused for 25 minutes
4. Take 5 minute break
5. Repeat until task is done
6. Complete task #1
```

Stay focused and productive! 🚀
