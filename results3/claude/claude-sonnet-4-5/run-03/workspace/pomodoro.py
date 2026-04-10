#!/usr/bin/env python3
"""
Pomodoro Task Manager - A beautiful terminal-based productivity tool
Combines task management with the Pomodoro Technique (25min work, 5min break)
"""

import json
import time
import sys
import os
from datetime import datetime
from pathlib import Path

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.live import Live
    from rich import box
except ImportError:
    print("Installing required dependencies...")
    os.system("pip install rich")
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.live import Live
    from rich import box

# Desktop notifications support
try:
    from plyer import notification
    NOTIFICATIONS_AVAILABLE = True
except ImportError:
    NOTIFICATIONS_AVAILABLE = False

console = Console()

DATA_FILE = Path.home() / ".pomodoro_tasks.json"
WORK_DURATION = 25 * 60  # 25 minutes
BREAK_DURATION = 5 * 60  # 5 minutes


class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks()
        self.pomodoros_today = 0
        self.load_stats()

    def load_tasks(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                return data.get('tasks', [])
        return []

    def load_stats(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                data = json.load(f)
                stats = data.get('stats', {})
                today = datetime.now().strftime('%Y-%m-%d')
                if stats.get('date') == today:
                    self.pomodoros_today = stats.get('pomodoros', 0)

    def save_tasks(self):
        today = datetime.now().strftime('%Y-%m-%d')
        data = {
            'tasks': self.tasks,
            'stats': {
                'date': today,
                'pomodoros': self.pomodoros_today
            }
        }
        with open(DATA_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def add_task(self, description):
        task = {
            'id': len(self.tasks) + 1,
            'description': description,
            'completed': False,
            'pomodoros': 0,
            'created': datetime.now().isoformat()
        }
        self.tasks.append(task)
        self.save_tasks()
        console.print(f"✓ Added task: {description}", style="green")

    def complete_task(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['completed'] = True
                self.save_tasks()
                console.print(f"✓ Completed: {task['description']}", style="green")
                return
        console.print(f"Task {task_id} not found", style="red")

    def delete_task(self, task_id):
        self.tasks = [t for t in self.tasks if t['id'] != task_id]
        self.save_tasks()
        console.print(f"✓ Deleted task {task_id}", style="yellow")

    def increment_pomodoro(self, task_id):
        for task in self.tasks:
            if task['id'] == task_id:
                task['pomodoros'] += 1
                break
        self.pomodoros_today += 1
        self.save_tasks()

    def show_tasks(self):
        if not self.tasks:
            console.print("\n[yellow]No tasks yet. Add one to get started![/yellow]\n")
            return

        table = Table(title="📋 Your Tasks", box=box.ROUNDED)
        table.add_column("ID", style="cyan", justify="center")
        table.add_column("Status", justify="center")
        table.add_column("Task", style="white")
        table.add_column("🍅", justify="center", style="red")

        for task in self.tasks:
            status = "✓" if task['completed'] else "○"
            status_style = "green" if task['completed'] else "yellow"
            table.add_row(
                str(task['id']),
                f"[{status_style}]{status}[/{status_style}]",
                task['description'],
                str(task['pomodoros'])
            )

        console.print(table)
        console.print(f"\n🍅 Pomodoros completed today: [bold red]{self.pomodoros_today}[/bold red]\n")


def send_notification(title, message):
    """Send desktop notification if available"""
    if NOTIFICATIONS_AVAILABLE:
        try:
            notification.notify(
                title=title,
                message=message,
                app_name="Pomodoro Timer",
                timeout=10
            )
        except Exception as e:
            # Silently fail if notifications don't work
            pass


def run_pomodoro(duration, task_manager, task_id=None, is_break=False):
    """Run a pomodoro timer with a progress bar"""
    title = "☕ Break Time" if is_break else "🍅 Focus Time"
    color = "green" if is_break else "red"

    with Progress(
        TextColumn("[bold blue]{task.description}"),
        BarColumn(bar_width=40),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeRemainingColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"[{color}]{title}", total=duration)

        try:
            for _ in range(duration):
                time.sleep(1)
                progress.update(task, advance=1)

            # Completed successfully
            if not is_break and task_id:
                task_manager.increment_pomodoro(task_id)

            console.print(f"\n✨ {title} complete!", style=f"bold {color}")

            # Send desktop notification
            if is_break:
                send_notification("Break Complete! ☕", "Time to get back to work!")
            else:
                send_notification("Pomodoro Complete! 🍅", "Great work! Time for a break.")

            # Play a sound (try different methods)
            try:
                os.system('printf "\a"')
            except:
                pass

            return True

        except KeyboardInterrupt:
            console.print("\n⏸️  Timer paused", style="yellow")
            return False


def main_menu(task_manager):
    """Display main menu and handle user input"""
    while True:
        console.clear()
        console.print(Panel.fit(
            "[bold red]🍅 Pomodoro Task Manager[/bold red]\n"
            "Stay focused, get things done!",
            border_style="red"
        ))

        task_manager.show_tasks()

        console.print("[bold cyan]Commands:[/bold cyan]")
        console.print("  [green]a[/green] - Add task")
        console.print("  [green]s[/green] - Start pomodoro")
        console.print("  [green]c[/green] - Complete task")
        console.print("  [green]d[/green] - Delete task")
        console.print("  [green]q[/green] - Quit")

        choice = Prompt.ask("\n🎯 What would you like to do?", choices=['a', 's', 'c', 'd', 'q'])

        if choice == 'a':
            description = Prompt.ask("📝 Task description")
            if description:
                task_manager.add_task(description)
                time.sleep(1)

        elif choice == 's':
            if not task_manager.tasks:
                console.print("[red]Add a task first![/red]")
                time.sleep(2)
                continue

            task_id = Prompt.ask("🍅 Task ID to work on", default="1")
            try:
                task_id = int(task_id)
                if run_pomodoro(WORK_DURATION, task_manager, task_id):
                    # Offer break
                    if Confirm.ask("Take a 5-minute break?", default=True):
                        run_pomodoro(BREAK_DURATION, task_manager, is_break=True)
            except ValueError:
                console.print("[red]Invalid task ID[/red]")
                time.sleep(1)

        elif choice == 'c':
            task_id = Prompt.ask("✓ Task ID to complete")
            try:
                task_manager.complete_task(int(task_id))
                time.sleep(1)
            except ValueError:
                console.print("[red]Invalid task ID[/red]")
                time.sleep(1)

        elif choice == 'd':
            task_id = Prompt.ask("🗑️  Task ID to delete")
            try:
                if Confirm.ask(f"Delete task {task_id}?"):
                    task_manager.delete_task(int(task_id))
                time.sleep(1)
            except ValueError:
                console.print("[red]Invalid task ID[/red]")
                time.sleep(1)

        elif choice == 'q':
            console.print("\n[green]Stay productive! 🚀[/green]\n")
            break


if __name__ == "__main__":
    try:
        tm = TaskManager()
        main_menu(tm)
    except KeyboardInterrupt:
        console.print("\n\n[yellow]Goodbye! 👋[/yellow]\n")
        sys.exit(0)
