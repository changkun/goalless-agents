#!/usr/bin/env python3
"""
Pomodoro Timer - A terminal-based productivity timer
"""
import time
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
WORK_DURATION = 25 * 60  # 25 minutes in seconds
SHORT_BREAK = 5 * 60     # 5 minutes in seconds
LONG_BREAK = 15 * 60     # 15 minutes in seconds
SESSIONS_BEFORE_LONG_BREAK = 4

# Data file
DATA_DIR = Path.home() / ".pomodoro"
STATS_FILE = DATA_DIR / "stats.json"


class PomodoroTimer:
    def __init__(self):
        self.stats = self.load_stats()

    def load_stats(self):
        """Load statistics from file"""
        if STATS_FILE.exists():
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        return {
            'completed_sessions': 0,
            'total_focus_time': 0,
            'sessions_today': 0,
            'last_session_date': None,
            'history': []
        }

    def save_stats(self):
        """Save statistics to file"""
        DATA_DIR.mkdir(exist_ok=True)
        with open(STATS_FILE, 'w') as f:
            json.dump(self.stats, f, indent=2)

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def draw_timer(self, remaining, total, session_type):
        """Draw the timer display"""
        self.clear_screen()

        # Title
        print("\n" + "="*50)
        print(f"🍅  POMODORO TIMER - {session_type.upper()}")
        print("="*50 + "\n")

        # Progress bar
        progress = (total - remaining) / total
        bar_length = 40
        filled = int(bar_length * progress)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(f"  [{bar}] {int(progress * 100)}%\n")

        # Time remaining
        time_str = self.format_time(remaining)
        print(f"  Time Remaining: {time_str}")
        print()

        # Stats
        print(f"  Today's Sessions: {self.stats['sessions_today']}")
        print(f"  Total Sessions: {self.stats['completed_sessions']}")
        print(f"  Total Focus Time: {self.stats['total_focus_time'] // 60} minutes")
        print("\n" + "="*50)
        print("  Press Ctrl+C to pause/quit")
        print("="*50)

    def countdown(self, duration, session_type):
        """Run a countdown timer"""
        end_time = time.time() + duration

        try:
            while True:
                remaining = int(end_time - time.time())
                if remaining <= 0:
                    break

                self.draw_timer(remaining, duration, session_type)
                time.sleep(1)

            # Timer completed
            self.draw_timer(0, duration, session_type)
            return True

        except KeyboardInterrupt:
            print("\n\n⏸️  Timer paused!")
            return False

    def play_notification(self):
        """Play a notification sound"""
        # Use system bell
        print("\a" * 3)

    def record_session(self):
        """Record a completed work session"""
        today = datetime.now().strftime("%Y-%m-%d")

        # Reset daily counter if it's a new day
        if self.stats['last_session_date'] != today:
            self.stats['sessions_today'] = 0

        self.stats['completed_sessions'] += 1
        self.stats['sessions_today'] += 1
        self.stats['total_focus_time'] += WORK_DURATION
        self.stats['last_session_date'] = today

        # Add to history
        self.stats['history'].append({
            'date': datetime.now().isoformat(),
            'duration': WORK_DURATION
        })

        # Keep only last 100 sessions in history
        self.stats['history'] = self.stats['history'][-100:]

        self.save_stats()

    def show_completion(self, session_type):
        """Show completion message"""
        self.clear_screen()
        print("\n" + "="*50)
        if session_type == "work":
            print("✅  WORK SESSION COMPLETE!")
            print("\n  Great job! Time for a break.")
        else:
            print("✅  BREAK COMPLETE!")
            print("\n  Ready to focus again?")
        print("="*50 + "\n")
        self.play_notification()
        time.sleep(3)

    def run_work_session(self):
        """Run a work session"""
        print("\n🍅 Starting work session (25 minutes)...\n")
        time.sleep(2)

        if self.countdown(WORK_DURATION, "work"):
            self.show_completion("work")
            self.record_session()
            return True
        return False

    def run_break(self, long_break=False):
        """Run a break session"""
        duration = LONG_BREAK if long_break else SHORT_BREAK
        break_type = "long break" if long_break else "short break"

        print(f"\n☕ Starting {break_type} ({duration // 60} minutes)...\n")
        time.sleep(2)

        if self.countdown(duration, break_type):
            self.show_completion("break")
            return True
        return False

    def show_menu(self):
        """Show main menu"""
        self.clear_screen()
        print("\n" + "="*50)
        print("🍅  POMODORO TIMER")
        print("="*50 + "\n")
        print(f"  Sessions Today: {self.stats['sessions_today']}")
        print(f"  Total Sessions: {self.stats['completed_sessions']}")
        print(f"  Total Focus Time: {self.stats['total_focus_time'] // 60} minutes")
        print("\n" + "-"*50 + "\n")
        print("  1. Start Work Session (25 min)")
        print("  2. Start Short Break (5 min)")
        print("  3. Start Long Break (15 min)")
        print("  4. View Statistics")
        print("  5. Reset Statistics")
        print("  6. Quit")
        print("\n" + "="*50)

        choice = input("\n  Enter choice (1-6): ").strip()
        return choice

    def show_stats(self):
        """Show detailed statistics"""
        self.clear_screen()
        print("\n" + "="*50)
        print("📊  STATISTICS")
        print("="*50 + "\n")

        print(f"  Total Completed Sessions: {self.stats['completed_sessions']}")
        print(f"  Sessions Today: {self.stats['sessions_today']}")
        print(f"  Total Focus Time: {self.stats['total_focus_time'] // 60} minutes")

        if self.stats['history']:
            print("\n  Recent Sessions:")
            for session in self.stats['history'][-10:]:
                date = datetime.fromisoformat(session['date'])
                print(f"    • {date.strftime('%Y-%m-%d %H:%M')}")

        print("\n" + "="*50)
        input("\n  Press Enter to continue...")

    def reset_stats(self):
        """Reset all statistics"""
        confirm = input("\n  ⚠️  Reset all statistics? (yes/no): ").strip().lower()
        if confirm == 'yes':
            self.stats = {
                'completed_sessions': 0,
                'total_focus_time': 0,
                'sessions_today': 0,
                'last_session_date': None,
                'history': []
            }
            self.save_stats()
            print("\n  ✅ Statistics reset!")
            time.sleep(2)

    def run(self):
        """Main application loop"""
        while True:
            choice = self.show_menu()

            if choice == '1':
                self.run_work_session()
            elif choice == '2':
                self.run_break(long_break=False)
            elif choice == '3':
                self.run_break(long_break=True)
            elif choice == '4':
                self.show_stats()
            elif choice == '5':
                self.reset_stats()
            elif choice == '6':
                print("\n  👋 Goodbye! Stay productive!\n")
                break
            else:
                print("\n  ❌ Invalid choice. Try again.")
                time.sleep(1)


def main():
    """Main entry point"""
    timer = PomodoroTimer()
    try:
        timer.run()
    except KeyboardInterrupt:
        print("\n\n  👋 Goodbye! Stay productive!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
