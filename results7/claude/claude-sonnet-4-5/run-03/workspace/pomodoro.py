#!/usr/bin/env python3
"""
Pomodoro Timer - A beautiful CLI productivity tool
"""
import time
import sys
from datetime import datetime, timedelta
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
from rich.layout import Layout
from rich.text import Text
import argparse

console = Console()

class PomodoroTimer:
    def __init__(self, work_mins=25, break_mins=5, long_break_mins=15):
        self.work_duration = work_mins * 60
        self.break_duration = break_mins * 60
        self.long_break_duration = long_break_mins * 60
        self.sessions_completed = 0
        self.is_work_session = True

    def format_time(self, seconds):
        """Format seconds into MM:SS"""
        mins, secs = divmod(int(seconds), 60)
        return f"{mins:02d}:{secs:02d}"

    def create_display(self, remaining, total, session_type):
        """Create the rich display panel"""
        layout = Layout()

        # Calculate progress
        progress_pct = ((total - remaining) / total) * 100 if total > 0 else 100

        # Session type with emoji
        emoji = "🍅" if session_type == "WORK" else "☕"
        session_style = "bold yellow" if session_type == "WORK" else "bold green"

        # Time remaining
        time_str = self.format_time(remaining)
        time_style = "bold red" if remaining < 60 else "bold cyan"

        # Progress bar
        bar_length = 40
        filled = int(bar_length * progress_pct / 100)
        bar = "█" * filled + "░" * (bar_length - filled)
        bar_style = "yellow" if session_type == "WORK" else "green"

        # Combine everything
        content = Text()
        content.append(f"{emoji} {session_type} SESSION", style=session_style)
        content.append("\n\n")
        content.append(time_str, style=time_style)
        content.append("\n\n")
        content.append(bar, style=bar_style)
        content.append("\n\n")
        content.append(f"Sessions completed: {self.sessions_completed}", style="dim")

        panel = Panel(
            content,
            title="🍅 Pomodoro Timer",
            border_style="bright_magenta",
            padding=(1, 2),
        )

        return panel

    def run_session(self, duration, session_type):
        """Run a single pomodoro session"""
        start_time = time.time()
        end_time = start_time + duration

        try:
            with Live(self.create_display(duration, duration, session_type),
                     refresh_per_second=4, console=console) as live:
                while time.time() < end_time:
                    remaining = end_time - time.time()
                    if remaining < 0:
                        remaining = 0

                    live.update(self.create_display(remaining, duration, session_type))
                    time.sleep(0.25)

        except KeyboardInterrupt:
            console.print("\n[yellow]Session paused. Press Ctrl+C again to quit.[/yellow]")
            time.sleep(0.5)
            raise

    def celebrate(self, session_type):
        """Show celebration message"""
        if session_type == "WORK":
            console.print("\n[bold green]✨ Work session complete! Time for a break! ✨[/bold green]\n")
        else:
            console.print("\n[bold yellow]⚡ Break over! Ready to focus! ⚡[/bold yellow]\n")

    def start(self, sessions=4):
        """Start the pomodoro timer loop"""
        console.clear()
        console.print("[bold magenta]🍅 Pomodoro Timer Started[/bold magenta]")
        console.print(f"Work: {self.work_duration//60} mins | Short break: {self.break_duration//60} mins | Long break: {self.long_break_duration//60} mins\n")

        try:
            while True:
                # Work session
                self.is_work_session = True
                self.run_session(self.work_duration, "WORK")
                self.sessions_completed += 1
                self.celebrate("WORK")
                time.sleep(2)

                # Determine break type
                if self.sessions_completed % sessions == 0:
                    # Long break after N sessions
                    self.is_work_session = False
                    self.run_session(self.long_break_duration, "LONG BREAK")
                    self.celebrate("LONG BREAK")
                else:
                    # Short break
                    self.is_work_session = False
                    self.run_session(self.break_duration, "BREAK")
                    self.celebrate("BREAK")

                time.sleep(2)

        except KeyboardInterrupt:
            console.print(f"\n\n[bold cyan]Timer stopped. You completed {self.sessions_completed} session(s)! 🎉[/bold cyan]")
            sys.exit(0)


def main():
    parser = argparse.ArgumentParser(description="🍅 Pomodoro Timer - Stay focused and productive!")
    parser.add_argument("-w", "--work", type=int, default=25, help="Work session duration in minutes (default: 25)")
    parser.add_argument("-b", "--break", type=int, default=5, dest="short_break", help="Short break duration in minutes (default: 5)")
    parser.add_argument("-l", "--long-break", type=int, default=15, help="Long break duration in minutes (default: 15)")
    parser.add_argument("-s", "--sessions", type=int, default=4, help="Sessions before long break (default: 4)")

    args = parser.parse_args()

    timer = PomodoroTimer(
        work_mins=args.work,
        break_mins=args.short_break,
        long_break_mins=args.long_break
    )

    timer.start(sessions=args.sessions)


if __name__ == "__main__":
    main()
