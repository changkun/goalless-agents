#!/usr/bin/env python3
"""Token Dashboard CLI application."""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.table import Table

from token_dashboard.storage import TokenStore
from token_dashboard.models import TokenUsage

console = Console()


@click.group()
def main():
    """Token Dashboard - Track and analyze Claude API token usage."""
    pass


@main.command()
@click.option("--days", default=7, help="Number of days to analyze (default: 7)")
@click.option("--model", default=None, help="Filter by model (optional)")
def report(days: int, model: Optional[str]):
    """Generate a usage report for recent operations."""
    store = TokenStore()
    usage_data = store.get_usage_summary(days, model)

    if not usage_data:
        console.print("[yellow]No usage data found for the specified period.[/yellow]")
        return

    table = Table(title=f"Token Usage Report (Last {days} days)")
    table.add_column("Model", style="cyan")
    table.add_column("Input Tokens", justify="right", style="green")
    table.add_column("Output Tokens", justify="right", style="blue")
    table.add_column("Total Tokens", justify="right", style="magenta")
    table.add_column("Operations", justify="right")

    total_input = 0
    total_output = 0

    for model_name, data in usage_data.items():
        table.add_row(
            model_name,
            str(data["input"]),
            str(data["output"]),
            str(data["total"]),
            str(data["count"]),
        )
        total_input += data["input"]
        total_output += data["output"]

    table.add_row(
        "[bold]TOTAL[/bold]",
        f"[bold]{total_input}[/bold]",
        f"[bold]{total_output}[/bold]",
        f"[bold]{total_input + total_output}[/bold]",
        "",
    )

    console.print(table)


@main.command()
def show():
    """Show current token dashboard."""
    store = TokenStore()
    stats = store.get_stats()

    console.print("\n[bold cyan]Token Dashboard[/bold cyan]\n")
    console.print(f"Total Operations: [green]{stats['total_operations']}[/green]")
    console.print(f"Total Input Tokens: [blue]{stats['total_input']}[/blue]")
    console.print(f"Total Output Tokens: [magenta]{stats['total_output']}[/magenta]")
    console.print(f"Total Tokens: [bold]{stats['total_tokens']}[/bold]")
    console.print(f"Avg Tokens per Op: {stats['avg_tokens_per_op']:.0f}")
    console.print(f"Last Operation: {stats['last_operation']}")


@main.command()
@click.argument("name")
@click.option("--input-tokens", default=0, help="Input tokens used")
@click.option("--output-tokens", default=0, help="Output tokens used")
@click.option("--model", default="claude-opus-4-6", help="Model used (default: claude-opus-4-6)")
def track(name: str, input_tokens: int, output_tokens: int, model: str):
    """Track a token usage event."""
    store = TokenStore()
    usage = TokenUsage(
        name=name,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        timestamp=datetime.now(),
    )
    store.add_usage(usage)
    console.print(
        f"[green]✓[/green] Tracked: {name} ({input_tokens} input + {output_tokens} output tokens)"
    )


@main.command()
def clear():
    """Clear all usage data."""
    if click.confirm("Are you sure you want to clear all usage data?"):
        store = TokenStore()
        store.clear()
        console.print("[green]✓[/green] Usage data cleared.")


if __name__ == "__main__":
    main()
