#!/usr/bin/env python3
"""
Pomodoro Timer - A terminal-based productivity timer
"""

import time
import sys
import json
import os
from datetime import datetime
from pathlib import Path


class PomodoroTimer:
    def __init__(self):
        self.config_file = Path.home() / '.pomodoro.config.json'
        self.load_config()
        self.history_file = Path.home() / '.pomodoro_history.json'
        self.completed_sessions = 0

    def load_config(self):
        """Load configuration from file or use defaults"""
        defaults = {
            'work_duration_minutes': 25,
            'break_duration_minutes': 5,
            'long_break_duration_minutes': 15,
            'sessions_until_long_break': 4
        }

        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    config = json.load(f)
                    defaults.update(config)
            except:
                pass

        self.work_duration = defaults['work_duration_minutes'] * 60
        self.break_duration = defaults['break_duration_minutes'] * 60
        self.long_break_duration = defaults['long_break_duration_minutes'] * 60
        self.sessions_until_long_break = defaults['sessions_until_long_break']

    def clear_line(self):
        """Clear the current line in terminal"""
        sys.stdout.write('\r\033[K')
        sys.stdout.flush()

    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"

    def countdown(self, duration, label, color_code):
        """Display a countdown timer"""
        print(f"\n{color_code}━━━ {label} ━━━\033[0m")

        for remaining in range(duration, 0, -1):
            self.clear_line()
            time_str = self.format_time(remaining)

            # Progress bar
            progress = (duration - remaining) / duration
            bar_length = 40
            filled = int(bar_length * progress)
            bar = '█' * filled + '░' * (bar_length - filled)

            sys.stdout.write(f"{color_code}{time_str} [{bar}]\033[0m")
            sys.stdout.flush()

            try:
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n\n⏸️  Timer paused. Press Enter to resume or Ctrl+C again to quit...")
                try:
                    input()
                    print("Resuming...")
                except KeyboardInterrupt:
                    print("\n\n👋 Exiting Pomodoro Timer")
                    sys.exit(0)

        self.clear_line()
        print(f"{color_code}{label} complete! ✓\033[0m")
        self.ring_bell()

    def ring_bell(self):
        """Ring the terminal bell"""
        print('\a', end='', flush=True)

    def save_session(self, session_type):
        """Save completed session to history"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r') as f:
                    history = json.load(f)
            except:
                history = []

        history.append({
            'type': session_type,
            'timestamp': datetime.now().isoformat(),
            'duration': self.work_duration if session_type == 'work' else self.break_duration
        })

        with open(self.history_file, 'w') as f:
            json.dump(history, f, indent=2)

    def show_stats(self):
        """Display session statistics"""
        if not self.history_file.exists():
            print("\n📊 No sessions completed yet!")
            return

        try:
            with open(self.history_file, 'r') as f:
                history = json.load(f)
        except:
            print("\n📊 No sessions completed yet!")
            return

        today = datetime.now().date()
        today_sessions = [s for s in history
                         if datetime.fromisoformat(s['timestamp']).date() == today
                         and s['type'] == 'work']

        total_work_sessions = sum(1 for s in history if s['type'] == 'work')

        print("\n" + "━" * 50)
        print("📊 POMODORO STATISTICS")
        print("━" * 50)
        print(f"🍅 Today: {len(today_sessions)} sessions")
        print(f"🎯 Total: {total_work_sessions} sessions")
        print(f"⏱️  Total focus time: {total_work_sessions * 25} minutes")
        print("━" * 50)

    def run(self):
        """Main timer loop"""
        print("\n")
        print("  ╔═══════════════════════════════════════════════╗")
        print("  ║           🍅  POMODORO TIMER  🍅              ║")
        print("  ╚═══════════════════════════════════════════════╝")
        print()
        print(f"  Work: {self.work_duration//60} min | Break: {self.break_duration//60} min | Long break: {self.long_break_duration//60} min")
        print("  Press Ctrl+C during timer to pause/quit")
        print("  " + "━" * 50)

        session_count = 0

        try:
            while True:
                session_count += 1

                # Work session
                self.countdown(self.work_duration,
                             f"🍅 WORK SESSION #{session_count}",
                             "\033[91m")  # Red
                self.save_session('work')
                self.completed_sessions += 1

                # Decide break type
                if session_count % self.sessions_until_long_break == 0:
                    break_duration = self.long_break_duration
                    break_label = "☕ LONG BREAK"
                else:
                    break_duration = self.break_duration
                    break_label = "☕ SHORT BREAK"

                print(f"\n✨ Great work! Time for a break.")
                print(f"   Sessions completed: {self.completed_sessions}")

                # Break session
                self.countdown(break_duration, break_label, "\033[92m")  # Green
                self.save_session('break')

                print("\n🔄 Ready for the next session?\n")

        except KeyboardInterrupt:
            print("\n\n👋 Exiting Pomodoro Timer")
            self.show_stats()


def main():
    if len(sys.argv) > 1 and sys.argv[1] == 'stats':
        timer = PomodoroTimer()
        timer.show_stats()
    else:
        timer = PomodoroTimer()
        timer.run()


if __name__ == '__main__':
    main()
