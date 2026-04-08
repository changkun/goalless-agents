#!/usr/bin/env python3
"""flux — terminal Pomodoro timer with session tracking."""

import json
import os
import sys
import time
from datetime import datetime, date
from pathlib import Path

import click
from rich.align import Align
from rich.console import Console
from rich import box
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, BarColumn
from rich.table import Table
from rich.text import Text

__version__ = "1.0.0"

console = Console()

# 5-row ASCII digit art (each char is 5 cols wide + 1 space separator)
DIGITS = {
    "0": ["▄███▄", "█   █", "█   █", "█   █", "▀███▀"],
    "1": [" ██  ", " ██  ", " ██  ", " ██  ", " ██  "],
    "2": ["▄███▄", "    █", " ███▀", "█    ", "▀███▀"],
    "3": ["▄███▄", "    █", " ████", "    █", "▀███▀"],
    "4": ["█   █", "█   █", "▀████", "    █", "    █"],
    "5": ["▀████", "█    ", "▀███▄", "    █", "▄███▀"],
    "6": ["▄███▄", "█    ", "▀███▄", "█   █", "▀███▀"],
    "7": ["▀████", "   █ ", "  █  ", " █   ", " █   "],
    "8": ["▄███▄", "█   █", "▄███▄", "█   █", "▀███▀"],
    "9": ["▄███▄", "█   █", "▀████", "    █", "▀███▀"],
    ":": ["     ", "  ▪  ", "     ", "  ▪  ", "     "],
}

DATA_DIR = Path.home() / ".flux"
SESSIONS_FILE = DATA_DIR / "sessions.json"


def ensure_data_dir():
    DATA_DIR.mkdir(exist_ok=True)
    if not SESSIONS_FILE.exists():
        SESSIONS_FILE.write_text("[]")


def load_sessions() -> list:
    ensure_data_dir()
    return json.loads(SESSIONS_FILE.read_text())


def save_session(session_type: str, duration_minutes: int, completed: bool, elapsed_seconds: int):
    sessions = load_sessions()
    sessions.append({
        "date": date.today().isoformat(),
        "time": datetime.now().isoformat(),
        "type": session_type,
        "duration": duration_minutes,
        "elapsed_seconds": elapsed_seconds,
        "completed": completed,
    })
    SESSIONS_FILE.write_text(json.dumps(sessions, indent=2))


def count_today_pomodoros() -> int:
    sessions = load_sessions()
    today = date.today().isoformat()
    return sum(1 for s in sessions if s["date"] == today and s["type"] == "work" and s["completed"])


def render_big_time(minutes: int, seconds: int, color: str) -> Text:
    time_str = f"{minutes:02d}:{seconds:02d}"
    rows = ["", "", "", "", ""]
    for i, char in enumerate(time_str):
        digit_rows = DIGITS.get(char, ["     "] * 5)
        for row_idx in range(5):
            rows[row_idx] += digit_rows[row_idx]
            if i < len(time_str) - 1:
                rows[row_idx] += " "
    result = Text()
    for i, row in enumerate(rows):
        result.append(row, style=f"bold {color}")
        if i < 4:
            result.append("\n")
    return result


def run_timer(label: str, total_seconds: int, color: str, session_type: str) -> bool:
    remaining = total_seconds
    start_time = time.time()
    completed = False
    elapsed_secs = 0

    progress = Progress(
        "[progress.description]{task.description}",
        BarColumn(bar_width=44, complete_style=color, finished_style=color, pulse_style="dim"),
        "[{task.percentage:>3.0f}%]",
        console=console,
        expand=False,
    )
    task_id = progress.add_task(f"[{color}]{label}", total=total_seconds)

    def make_panel(secs: int) -> Panel:
        warn = secs <= 60 and secs % 2 == 0
        time_color = "bold red" if warn else f"bold {color}"
        time_display = render_big_time(secs // 60, secs % 60, time_color)
        progress.update(task_id, completed=total_seconds - secs)
        inner = Align.center(time_display)
        return Panel(
            inner,
            title=f"[bold {color}]  {label}  [/]",
            subtitle=f"[dim]ctrl+c to cancel[/]",
            border_style="red" if warn else color,
            padding=(1, 6),
        )

    try:
        with Live(make_panel(remaining), refresh_per_second=4, console=console) as live:
            while remaining > 0:
                time.sleep(0.25)
                elapsed_secs = int(time.time() - start_time)
                remaining = max(0, total_seconds - elapsed_secs)
                live.update(make_panel(remaining))
            completed = True
        # Bell on completion
        sys.stdout.write("\a")
        sys.stdout.flush()
        console.print(f"\n[bold {color}]  Session complete![/]\n")
    except KeyboardInterrupt:
        elapsed_secs = int(time.time() - start_time)
        mins, secs = elapsed_secs // 60, elapsed_secs % 60
        console.print(f"\n[dim]Cancelled after {mins}m {secs:02d}s[/]")
    finally:
        save_session(session_type, total_seconds // 60, completed, elapsed_secs)

    return completed


@click.group(invoke_without_command=True, context_settings={"help_option_names": ["-h", "--help"]})
@click.pass_context
@click.version_option(__version__, "-V", "--version")
@click.option("--minutes", "-m", default=25, show_default=True, help="Work session length in minutes.")
def cli(ctx, minutes):
    """flux — Pomodoro timer for focused work.

    \b
    Run `flux` to start a 25-minute work session.
    Run `flux break` for a short break.
    Run `flux stats` to see your progress.
    """
    if ctx.invoked_subcommand is None:
        completed = run_timer(
            label=f"WORK · {minutes}m",
            total_seconds=minutes * 60,
            color="green",
            session_type="work",
        )
        if completed:
            today_count = count_today_pomodoros()
            if today_count % 4 == 0:
                console.print(f"[dim]  {today_count} pomodoros today — take a [bold]long break[/]: flux break --long[/]\n")
            else:
                console.print(f"[dim]  {today_count} pomodoro{'s' if today_count != 1 else ''} today — take a break: flux break[/]\n")


@cli.command(name="break")
@click.option("--long", "-l", is_flag=True, help="Long break (15 min instead of 5).")
@click.option("--minutes", "-m", default=None, type=int, help="Custom break duration.")
def brk(long, minutes):
    """Take a break (5m short, 15m long)."""
    if minutes:
        duration = minutes
    elif long:
        duration = 15
    else:
        duration = 5
    session_type = "long_break" if (long or (minutes and minutes >= 10)) else "break"
    run_timer(
        label=f"BREAK · {duration}m",
        total_seconds=duration * 60,
        color="blue",
        session_type=session_type,
    )


@cli.command()
def stats():
    """Show focus statistics and recent history."""
    sessions = load_sessions()
    if not sessions:
        console.print("\n[dim]No sessions recorded yet. Run [bold green]flux[/] to get started!\n")
        return

    today = date.today().isoformat()
    work_sessions = [s for s in sessions if s["type"] == "work"]
    completed_work = [s for s in work_sessions if s["completed"]]
    today_work = [s for s in completed_work if s["date"] == today]

    # Day streak (consecutive days with at least one completed work session)
    all_work_dates = sorted(set(s["date"] for s in completed_work))
    streak = 0
    check_date = date.today()
    while check_date.isoformat() in all_work_dates:
        streak += 1
        check_date = date.fromordinal(check_date.toordinal() - 1)

    total_focus_mins = sum(s["duration"] for s in completed_work)
    total_count = len(completed_work)

    # Summary panel
    summary = Table(box=None, show_header=False, padding=(0, 3))
    summary.add_column("label", style="dim")
    summary.add_column("value", style="bold")

    today_mins = sum(s["duration"] for s in today_work)
    summary.add_row("today", f"[green]{len(today_work)} session{'s' if len(today_work) != 1 else ''}[/]  [dim]{today_mins}m focus[/]")
    summary.add_row("streak", f"[yellow]{streak} day{'s' if streak != 1 else ''}[/]")
    summary.add_row("all-time", f"[cyan]{total_count} sessions[/]  [dim]{total_focus_mins // 60}h {total_focus_mins % 60}m total[/]")

    # Last 7 days breakdown
    by_date: dict[str, list] = {}
    for s in completed_work:
        by_date.setdefault(s["date"], []).append(s)

    hist = Table(box=box.SIMPLE_HEAD, border_style="dim", show_header=True, padding=(0, 1))
    hist.add_column("date", style="dim")
    hist.add_column("sessions", justify="right", style="green")
    hist.add_column("focus", justify="right", style="cyan")
    hist.add_column("", style="green")

    max_sessions = max((len(v) for v in by_date.values()), default=1)
    for d in sorted(by_date)[-7:]:
        sess = by_date[d]
        mins = sum(s["duration"] for s in sess)
        bar_len = max(1, round(len(sess) / max_sessions * 20))
        bar = "█" * bar_len
        label = "[bold white]today[/]" if d == today else d
        hist.add_row(label, str(len(sess)), f"{mins}m", bar)

    console.print()
    console.print(Panel(summary, title="[bold green] flux stats [/]", border_style="green", padding=(1, 2)))
    if by_date:
        console.print(Panel(hist, title="[dim] last 7 days [/]", border_style="dim", padding=(0, 1)))
    console.print()


@cli.command()
def reset():
    """Clear all session data."""
    if not SESSIONS_FILE.exists():
        console.print("[dim]Nothing to reset.[/]")
        return
    count = len(load_sessions())
    if click.confirm(f"Delete {count} session record{'s' if count != 1 else ''}?", default=False):
        SESSIONS_FILE.write_text("[]")
        console.print("[dim]Session history cleared.[/]")


if __name__ == "__main__":
    cli()
