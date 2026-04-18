#!/usr/bin/env python3
"""
Pomodoro Timer with Task Tracking
A terminal-based productivity tool for time management
"""

import time
import json
import os
import sys
from datetime import datetime
from pathlib import Path

class PomodoroTimer:
    def __init__(self, data_file=".pomodoro_data.json"):
        self.data_file = Path.home() / data_file
        self.work_duration = 25 * 60  # 25 minutes
        self.short_break = 5 * 60     # 5 minutes
        self.long_break = 15 * 60     # 15 minutes
        self.sessions_until_long_break = 4
        self.load_data()

    def load_data(self):
        """Load task history from JSON file"""
        if self.data_file.exists():
            with open(self.data_file, 'r') as f:
                self.data = json.load(f)
        else:
            self.data = {"tasks": [], "total_pomodoros": 0}

    def save_data(self):
        """Save task history to JSON file"""
        with open(self.data_file, 'w') as f:
            json.dump(self.data, f, indent=2)

    def clear_line(self):
        """Clear current terminal line"""
        sys.stdout.write('\r' + ' ' * 80 + '\r')
        sys.stdout.flush()

    def format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def countdown(self, duration, label):
        """Display countdown timer"""
        end_time = time.time() + duration

        try:
            while True:
                remaining = end_time - time.time()
                if remaining <= 0:
                    break

                self.clear_line()
                progress = 1 - (remaining / duration)
                bar_length = 30
                filled = int(bar_length * progress)
                bar = '█' * filled + '░' * (bar_length - filled)

                sys.stdout.write(f"{label} [{bar}] {self.format_time(remaining)}")
                sys.stdout.flush()
                time.sleep(0.1)

            self.clear_line()
            print(f"{label} [{'█' * bar_length}] Complete! ✓")

        except KeyboardInterrupt:
            self.clear_line()
            print(f"\n{label} interrupted")
            raise

    def start_session(self, task_name):
        """Start a Pomodoro session"""
        print(f"\n🍅 Starting Pomodoro: {task_name}")
        print(f"Focus for {self.work_duration // 60} minutes\n")

        session_count = 0
        try:
            while True:
                session_count += 1

                # Work session
                self.countdown(self.work_duration, f"Work #{session_count}")
                self.data["total_pomodoros"] += 1

                # Determine break type
                if session_count % self.sessions_until_long_break == 0:
                    break_duration = self.long_break
                    break_label = "Long Break"
                else:
                    break_duration = self.short_break
                    break_label = "Short Break"

                print(f"\n✨ Great work! Time for a {break_duration // 60} minute break")

                # Ask if user wants to continue
                response = input(f"Take {break_label.lower()}? (y/n/q to quit): ").lower()
                if response == 'q':
                    break
                elif response == 'y':
                    self.countdown(break_duration, break_label)
                    print("\n🔔 Break over! Ready for next session?")
                    continue_response = input("Continue? (y/n): ").lower()
                    if continue_response != 'y':
                        break
                else:
                    break

        except KeyboardInterrupt:
            print("\n\nSession stopped by user")

        # Save task record
        task_record = {
            "name": task_name,
            "pomodoros": session_count,
            "timestamp": datetime.now().isoformat(),
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        self.data["tasks"].append(task_record)
        self.save_data()

        print(f"\n📊 Session complete: {session_count} pomodoro(s) on '{task_name}'")

    def show_stats(self):
        """Display usage statistics"""
        print("\n📈 Pomodoro Statistics")
        print("=" * 50)
        print(f"Total Pomodoros: {self.data['total_pomodoros']}")
        print(f"Total Tasks: {len(self.data['tasks'])}")

        if self.data['tasks']:
            # Group by date
            by_date = {}
            for task in self.data['tasks']:
                date = task['date']
                if date not in by_date:
                    by_date[date] = []
                by_date[date].append(task)

            print(f"\nRecent Activity:")
            for date in sorted(by_date.keys(), reverse=True)[:7]:
                daily_pomodoros = sum(t['pomodoros'] for t in by_date[date])
                print(f"  {date}: {daily_pomodoros} pomodoros, {len(by_date[date])} tasks")

            print(f"\nLast 5 Tasks:")
            for task in self.data['tasks'][-5:]:
                timestamp = datetime.fromisoformat(task['timestamp']).strftime("%Y-%m-%d %H:%M")
                print(f"  [{timestamp}] {task['name']} - {task['pomodoros']} pomodoro(s)")

        print()

    def show_help(self):
        """Display help information"""
        print("\n🍅 Pomodoro Timer - Help")
        print("=" * 50)
        print("Usage: python pomodoro.py [command]")
        print("\nCommands:")
        print("  start <task>  - Start a Pomodoro session for a task")
        print("  stats         - Show usage statistics")
        print("  help          - Show this help message")
        print("\nExample:")
        print("  python pomodoro.py start 'Write documentation'")
        print()

def main():
    timer = PomodoroTimer()

    if len(sys.argv) < 2:
        timer.show_help()
        return

    command = sys.argv[1].lower()

    if command == "start":
        if len(sys.argv) < 3:
            print("Error: Please provide a task name")
            print("Usage: python pomodoro.py start <task>")
            return
        task_name = " ".join(sys.argv[2:])
        timer.start_session(task_name)

    elif command == "stats":
        timer.show_stats()

    elif command == "help":
        timer.show_help()

    else:
        print(f"Unknown command: {command}")
        timer.show_help()

if __name__ == "__main__":
    main()
