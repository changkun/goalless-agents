# 🍅 Pomodoro Timer

A terminal-based Pomodoro timer to boost your productivity. Track your focus sessions, take regular breaks, and build better work habits.

## Features

- **25-minute work sessions** with visual countdown
- **5-minute short breaks** and **15-minute long breaks**
- **Progress tracking** with session history
- **Daily and total statistics**
- **Visual progress bar** and clean terminal UI
- **Persistent data** - your stats are saved between sessions

## Installation

No dependencies required! Just Python 3.6+

```bash
chmod +x pomodoro.py
```

## Usage

Run the timer:

```bash
python3 pomodoro.py
```

Or make it executable and run directly:

```bash
./pomodoro.py
```

### Main Menu Options

1. **Start Work Session** - Begin a 25-minute focus session
2. **Start Short Break** - Take a 5-minute break
3. **Start Long Break** - Take a 15-minute break
4. **View Statistics** - See your productivity stats
5. **Reset Statistics** - Clear all tracked data
6. **Quit** - Exit the application

### During a Session

- Watch the progress bar fill up
- See your countdown timer
- View your daily and total session counts
- Press `Ctrl+C` to pause and return to menu

## The Pomodoro Technique

The Pomodoro Technique is a time management method:

1. Work for 25 minutes (one "Pomodoro")
2. Take a 5-minute break
3. After 4 Pomodoros, take a 15-minute long break
4. Repeat!

This helps maintain focus and prevents burnout.

## Data Storage

Statistics are stored in `~/.pomodoro/stats.json`:
- Completed session count
- Total focus time
- Daily session count
- Session history (last 100 sessions)

## Tips

- 🎯 Focus on one task during each Pomodoro
- 📱 Minimize distractions (phone, notifications)
- ☕ Actually take your breaks - they're important!
- 📊 Track your progress to stay motivated
- 🔄 Build consistency - aim for a few sessions daily

## Example Session

```
==================================================
🍅  POMODORO TIMER - WORK
==================================================

  [████████████████████████░░░░░░░░░░░░░░░░] 60%

  Time Remaining: 10:00

  Today's Sessions: 3
  Total Sessions: 47
  Total Focus Time: 1175 minutes

==================================================
  Press Ctrl+C to pause/quit
==================================================
```

Happy focusing! 🚀
