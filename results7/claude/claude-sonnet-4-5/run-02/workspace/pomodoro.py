#!/usr/bin/env python3
"""
Pomodoro Timer CLI - Track your focused work sessions
"""
import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional


@dataclass
class PomodoroSession:
    type: str  # 'work' or 'break'
    duration_minutes: int
    start_time: str
    completed: bool
    interrupted: bool = False


class PomodoroTimer:
    def __init__(self, data_file: str = None):
        self.data_file = data_file or os.path.expanduser("~/.pomodoro_history.json")
        self.state_file = os.path.expanduser("~/.pomodoro_state.json")
        self.work_duration = 25
        self.short_break = 5
        self.long_break = 15
        self.sessions_until_long_break = 4

    def load_history(self) -> List[PomodoroSession]:
        if not os.path.exists(self.data_file):
            return []
        with open(self.data_file, 'r') as f:
            data = json.load(f)
            return [PomodoroSession(**session) for session in data]

    def save_history(self, sessions: List[PomodoroSession]):
        with open(self.data_file, 'w') as f:
            json.dump([asdict(s) for s in sessions], f, indent=2)

    def load_state(self) -> Optional[dict]:
        if not os.path.exists(self.state_file):
            return None
        with open(self.state_file, 'r') as f:
            return json.load(f)

    def save_state(self, state: dict):
        with open(self.state_file, 'w') as f:
            json.dump(state, f, indent=2)

    def clear_state(self):
        if os.path.exists(self.state_file):
            os.remove(self.state_file)

    def notify(self, title: str, message: str):
        try:
            subprocess.run(['notify-send', title, message],
                         capture_output=True, timeout=5)
        except (subprocess.SubprocessError, FileNotFoundError):
            pass

    def start_timer(self, session_type: str = 'work', duration: int = None):
        if self.load_state():
            print("⚠️  A timer is already running! Use 'pomodoro status' to check or 'pomodoro stop' to end it.")
            return

        if duration is None:
            duration = self.work_duration if session_type == 'work' else self.short_break

        state = {
            'type': session_type,
            'duration_minutes': duration,
            'start_time': datetime.now().isoformat(),
            'end_time': (datetime.now() + timedelta(minutes=duration)).isoformat()
        }
        self.save_state(state)

        emoji = "🍅" if session_type == 'work' else "☕"
        print(f"{emoji} {session_type.capitalize()} session started for {duration} minutes")
        print(f"⏰ Will complete at {datetime.fromisoformat(state['end_time']).strftime('%H:%M:%S')}")
        print(f"\nUse 'pomodoro status' to check progress")
        print(f"Use 'pomodoro stop' to end early")

    def status(self):
        state = self.load_state()
        if not state:
            print("💤 No timer running")
            history = self.load_history()
            completed_today = [s for s in history
                             if s.completed and s.type == 'work'
                             and datetime.fromisoformat(s.start_time).date() == datetime.now().date()]
            if completed_today:
                print(f"✅ Completed {len(completed_today)} pomodoros today")
            return

        start = datetime.fromisoformat(state['start_time'])
        end = datetime.fromisoformat(state['end_time'])
        now = datetime.now()

        if now >= end:
            emoji = "🎉" if state['type'] == 'work' else "✨"
            print(f"{emoji} {state['type'].capitalize()} session completed!")
            print(f"⏱️  Duration: {state['duration_minutes']} minutes")

            session = PomodoroSession(
                type=state['type'],
                duration_minutes=state['duration_minutes'],
                start_time=state['start_time'],
                completed=True
            )
            history = self.load_history()
            history.append(session)
            self.save_history(history)
            self.clear_state()

            self.notify("Pomodoro Complete!",
                       f"{state['type'].capitalize()} session finished!")

            if state['type'] == 'work':
                completed_work = len([s for s in history if s.type == 'work' and s.completed])
                if completed_work % self.sessions_until_long_break == 0:
                    print(f"\n💡 Time for a long break! ({self.long_break} min)")
                else:
                    print(f"\n💡 Time for a short break! ({self.short_break} min)")
        else:
            elapsed = (now - start).total_seconds() / 60
            remaining = (end - now).total_seconds() / 60
            progress = (elapsed / state['duration_minutes']) * 100

            emoji = "🍅" if state['type'] == 'work' else "☕"
            print(f"{emoji} {state['type'].capitalize()} session in progress")
            print(f"⏱️  Elapsed: {int(elapsed)} min | Remaining: {int(remaining)} min")
            print(f"📊 Progress: [{'=' * int(progress/5)}{' ' * (20-int(progress/5))}] {int(progress)}%")
            print(f"⏰ Completes at: {end.strftime('%H:%M:%S')}")

    def stop(self):
        state = self.load_state()
        if not state:
            print("💤 No timer running")
            return

        session = PomodoroSession(
            type=state['type'],
            duration_minutes=state['duration_minutes'],
            start_time=state['start_time'],
            completed=False,
            interrupted=True
        )

        history = self.load_history()
        history.append(session)
        self.save_history(history)
        self.clear_state()

        print(f"⏹️  {state['type'].capitalize()} session stopped")

    def stats(self, days: int = 7):
        history = self.load_history()
        if not history:
            print("📊 No sessions recorded yet")
            return

        cutoff = datetime.now() - timedelta(days=days)
        recent = [s for s in history
                 if datetime.fromisoformat(s.start_time) >= cutoff]

        completed_work = [s for s in recent if s.type == 'work' and s.completed]
        interrupted_work = [s for s in recent if s.type == 'work' and s.interrupted]
        total_minutes = sum(s.duration_minutes for s in completed_work)

        print(f"📊 Pomodoro Statistics (Last {days} days)")
        print("=" * 50)
        print(f"✅ Completed work sessions: {len(completed_work)}")
        print(f"⏹️  Interrupted sessions: {len(interrupted_work)}")
        print(f"⏱️  Total focused time: {total_minutes} minutes ({total_minutes/60:.1f} hours)")

        if completed_work:
            completion_rate = len(completed_work) / (len(completed_work) + len(interrupted_work)) * 100
            print(f"🎯 Completion rate: {completion_rate:.1f}%")

            by_day = {}
            for session in completed_work:
                date = datetime.fromisoformat(session.start_time).date()
                by_day[date] = by_day.get(date, 0) + 1

            print(f"\n📅 Daily breakdown:")
            for date in sorted(by_day.keys(), reverse=True)[:7]:
                count = by_day[date]
                bar = "🍅" * count
                print(f"  {date}: {bar} ({count})")


def main():
    parser = argparse.ArgumentParser(
        description="Pomodoro Timer CLI - Track your focused work sessions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pomodoro start          Start a 25-minute work session
  pomodoro start -b       Start a 5-minute break
  pomodoro status         Check current timer
  pomodoro stop           Stop current timer
  pomodoro stats          View productivity statistics
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to execute')

    start_parser = subparsers.add_parser('start', help='Start a new timer')
    start_parser.add_argument('-b', '--break', action='store_true',
                             help='Start a break session instead of work')
    start_parser.add_argument('-d', '--duration', type=int,
                             help='Custom duration in minutes')

    subparsers.add_parser('status', help='Check current timer status')
    subparsers.add_parser('stop', help='Stop the current timer')

    stats_parser = subparsers.add_parser('stats', help='View statistics')
    stats_parser.add_argument('-d', '--days', type=int, default=7,
                             help='Number of days to include (default: 7)')

    args = parser.parse_args()

    timer = PomodoroTimer()

    if args.command == 'start':
        session_type = 'break' if getattr(args, 'break', False) else 'work'
        timer.start_timer(session_type, args.duration)
    elif args.command == 'status':
        timer.status()
    elif args.command == 'stop':
        timer.stop()
    elif args.command == 'stats':
        timer.stats(args.days)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
