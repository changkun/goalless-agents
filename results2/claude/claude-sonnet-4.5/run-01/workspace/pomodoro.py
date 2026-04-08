#!/usr/bin/env python3
"""
Pomodoro Timer - A terminal-based productivity timer
Tracks focus sessions and breaks with statistics
"""

import json
import time
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal

# ANSI color codes
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
MAGENTA = '\033[95m'
CYAN = '\033[96m'
RESET = '\033[0m'
BOLD = '\033[1m'
CLEAR_LINE = '\033[K'

# Timer settings (in seconds for testing, change to minutes * 60 for production)
FOCUS_TIME = 25 * 60  # 25 minutes
BREAK_TIME = 5 * 60   # 5 minutes
LONG_BREAK_TIME = 15 * 60  # 15 minutes
SESSIONS_BEFORE_LONG_BREAK = 4

DATA_FILE = Path.home() / '.pomodoro_data.json'


class PomodoroTimer:
    def __init__(self):
        self.data = self.load_data()
        self.running = False
        self.paused = False
        self.current_session = None

    def load_data(self):
        """Load session data from JSON file"""
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {'sessions': []}

    def save_data(self):
        """Save session data to JSON file"""
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def add_session(self, duration, session_type='focus'):
        """Record a completed session"""
        session = {
            'type': session_type,
            'duration': duration,
            'completed_at': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        self.data['sessions'].append(session)
        self.save_data()

    def get_stats(self):
        """Calculate statistics from session data"""
        today = datetime.now().strftime('%Y-%m-%d')
        week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')

        sessions = self.data['sessions']
        focus_sessions = [s for s in sessions if s['type'] == 'focus']

        today_sessions = [s for s in focus_sessions if s['date'] == today]
        week_sessions = [s for s in focus_sessions if s['date'] >= week_start]

        return {
            'total': len(focus_sessions),
            'today': len(today_sessions),
            'this_week': len(week_sessions),
            'total_minutes': sum(s['duration'] for s in focus_sessions) // 60
        }

    def format_time(self, seconds):
        """Format seconds as MM:SS"""
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def clear_screen(self):
        """Clear the terminal screen"""
        os.system('clear' if os.name != 'nt' else 'cls')

    def show_stats(self):
        """Display session statistics"""
        stats = self.get_stats()
        print(f"\n{BOLD}{CYAN}📊 Pomodoro Statistics{RESET}")
        print(f"{YELLOW}{'─' * 40}{RESET}")
        print(f"{GREEN}Today:{RESET}          {stats['today']} sessions")
        print(f"{GREEN}This Week:{RESET}      {stats['this_week']} sessions")
        print(f"{GREEN}All Time:{RESET}       {stats['total']} sessions")
        print(f"{GREEN}Total Focus:{RESET}    {stats['total_minutes']} minutes")
        print(f"{YELLOW}{'─' * 40}{RESET}\n")

    def countdown(self, duration, session_type='focus'):
        """Run a countdown timer"""
        start_time = time.time()
        end_time = start_time + duration

        session_emoji = '🍅' if session_type == 'focus' else '☕'
        session_name = 'FOCUS SESSION' if session_type == 'focus' else 'BREAK TIME'
        color = RED if session_type == 'focus' else GREEN

        self.running = True
        self.paused = False

        try:
            while time.time() < end_time and self.running:
                if not self.paused:
                    remaining = int(end_time - time.time())
                    if remaining < 0:
                        remaining = 0

                    # Display timer
                    sys.stdout.write('\r' + CLEAR_LINE)
                    sys.stdout.write(
                        f"{color}{BOLD}{session_emoji} {session_name}{RESET} - "
                        f"{color}{BOLD}{self.format_time(remaining)}{RESET} "
                        f"{YELLOW}[p]ause [s]kip [q]uit{RESET}"
                    )
                    sys.stdout.flush()
                    time.sleep(0.1)
                else:
                    sys.stdout.write('\r' + CLEAR_LINE)
                    sys.stdout.write(
                        f"{YELLOW}{BOLD}⏸️  PAUSED{RESET} - "
                        f"{YELLOW}[r]esume [s]kip [q]uit{RESET}"
                    )
                    sys.stdout.flush()
                    time.sleep(0.1)

            if self.running:
                # Session completed successfully
                print(f"\n{GREEN}{BOLD}✓ {session_name} Complete!{RESET}")
                self.add_session(duration, session_type)
                self.play_notification(session_type)
                return True
            else:
                print(f"\n{YELLOW}Session skipped{RESET}")
                return False

        except KeyboardInterrupt:
            print(f"\n{YELLOW}Session interrupted{RESET}")
            return False

    def play_notification(self, session_type):
        """Play a notification sound (terminal bell)"""
        print('\a')  # Terminal bell

    def run(self):
        """Main timer loop"""
        self.clear_screen()
        print(f"{BOLD}{MAGENTA}🍅 Pomodoro Timer{RESET}\n")
        self.show_stats()

        session_count = 0

        print(f"{CYAN}Starting Pomodoro sessions...{RESET}")
        print(f"{YELLOW}Press Ctrl+C at any time to exit{RESET}\n")
        time.sleep(1)

        try:
            while True:
                session_count += 1

                # Focus session
                print(f"\n{RED}{BOLD}Session {session_count} - Focus Time!{RESET}")
                completed = self.countdown(FOCUS_TIME, 'focus')

                if not completed or not self.running:
                    break

                # Determine break type
                if session_count % SESSIONS_BEFORE_LONG_BREAK == 0:
                    print(f"\n{GREEN}{BOLD}Long Break Time!{RESET}")
                    self.countdown(LONG_BREAK_TIME, 'break')
                else:
                    print(f"\n{GREEN}{BOLD}Short Break Time!{RESET}")
                    self.countdown(BREAK_TIME, 'break')

                if not self.running:
                    break

        except KeyboardInterrupt:
            print(f"\n\n{YELLOW}Timer stopped{RESET}")

        self.show_stats()
        print(f"{MAGENTA}Great work! 🎉{RESET}\n")


def handle_input(timer):
    """Handle keyboard input in a separate thread"""
    while timer.running:
        try:
            char = input()
            if char.lower() == 'q':
                timer.running = False
            elif char.lower() == 'p':
                timer.paused = True
            elif char.lower() == 'r':
                timer.paused = False
            elif char.lower() == 's':
                timer.running = False
        except:
            pass


def main():
    """Main entry point"""
    timer = PomodoroTimer()

    if len(sys.argv) > 1:
        if sys.argv[1] == 'stats':
            timer.show_stats()
            return
        elif sys.argv[1] == 'reset':
            if DATA_FILE.exists():
                DATA_FILE.unlink()
                print(f"{GREEN}Statistics reset!{RESET}")
            return

    # Start input handler thread
    # input_thread = threading.Thread(target=handle_input, args=(timer,), daemon=True)
    # input_thread.start()

    timer.run()


if __name__ == '__main__':
    main()
