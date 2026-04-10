#!/usr/bin/env python3
"""
Quick demo of the Pomodoro Task Manager functionality
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up environment for demo
os.environ['HOME'] = '/tmp'

from pomodoro import TaskManager, console
from rich.panel import Panel

def demo():
    console.print(Panel.fit(
        "[bold red]🍅 Pomodoro Task Manager Demo[/bold red]\n"
        "Demonstrating core functionality",
        border_style="red"
    ))

    # Create task manager
    tm = TaskManager()

    # Add some sample tasks
    console.print("\n[cyan]Adding sample tasks...[/cyan]")
    tm.add_task("Write project proposal")
    tm.add_task("Review pull requests")
    tm.add_task("Update documentation")

    # Display tasks
    console.print("\n[cyan]Current tasks:[/cyan]")
    tm.show_tasks()

    # Simulate completing a pomodoro
    console.print("\n[cyan]Simulating a completed pomodoro on task 1...[/cyan]")
    tm.increment_pomodoro(1)

    # Show updated stats
    console.print("\n[cyan]After one pomodoro:[/cyan]")
    tm.show_tasks()

    # Complete a task
    console.print("\n[cyan]Completing task 2...[/cyan]")
    tm.complete_task(2)

    # Show final state
    console.print("\n[cyan]Final state:[/cyan]")
    tm.show_tasks()

    console.print("\n[green]✅ Demo complete! The app is working correctly.[/green]")
    console.print("\n[yellow]Run 'python pomodoro.py' to use the interactive version![/yellow]\n")

if __name__ == "__main__":
    demo()
