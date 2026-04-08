#!/usr/bin/env python3
"""gitdash — A beautiful git repository analytics dashboard."""

import subprocess
import sys
import os
from collections import defaultdict, Counter
from datetime import datetime, timedelta
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.columns import Columns
from rich.text import Text
from rich import box
from rich.align import Align


console = Console()


def run_git(args: list[str], cwd: str) -> str:
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""


def get_repo_root(path: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def parse_log(root: str) -> list[dict]:
    """Parse git log into structured records."""
    fmt = "%H\x1f%ae\x1f%an\x1f%ai\x1f%s"
    raw = run_git(
        ["log", "--pretty=format:" + fmt, "--no-merges"],
        root,
    )
    if not raw:
        return []
    commits = []
    for line in raw.splitlines():
        parts = line.split("\x1f", 4)
        if len(parts) < 5:
            continue
        sha, email, name, date_str, subject = parts
        try:
            dt = datetime.fromisoformat(date_str)
        except ValueError:
            continue
        commits.append({"sha": sha, "email": email, "name": name, "date": dt, "subject": subject})
    return commits


def commit_heatmap(commits: list[dict]) -> list[str]:
    """Build a 13-week (91-day) contribution-style heatmap, Sun→Sat rows."""
    today = datetime.now().date()
    start = today - timedelta(days=90)

    # Count per day
    counts: dict = defaultdict(int)
    for c in commits:
        d = c["date"].date()
        if start <= d <= today:
            counts[d] += 1

    max_count = max(counts.values(), default=1)

    # Colour thresholds (5 levels)
    def level(n: int) -> str:
        if n == 0:
            return "grey23"
        pct = n / max_count
        if pct < 0.25:
            return "dark_green"
        if pct < 0.5:
            return "green3"
        if pct < 0.75:
            return "green1"
        return "bright_green"

    # Grid: rows = weekday (Mon=0..Sun=6), cols = weeks
    # Start on Monday of the week containing `start`
    grid_start = start - timedelta(days=start.weekday())  # Monday
    num_weeks = ((today - grid_start).days // 7) + 2

    prev_month = None
    month_row = ""
    for w in range(num_weeks):
        d = grid_start + timedelta(weeks=w)
        m = d.strftime("%b")
        if m != prev_month:
            month_row += m[:3] + " "
            prev_month = m
        else:
            month_row += "    "

    lines = []
    day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    for wd in range(7):
        row = Text(day_names[wd] + " ")
        for w in range(num_weeks):
            d = grid_start + timedelta(weeks=w, days=wd)
            if d > today or d < start:
                row.append("  ", style="")
            else:
                n = counts.get(d, 0)
                row.append("█ ", style=level(n))
        lines.append(row)

    return lines, month_row.rstrip()


def top_authors(commits: list[dict], n: int = 8) -> Table:
    counts: Counter = Counter(c["name"] for c in commits)
    total = sum(counts.values())

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("Author", style="white")
    table.add_column("Commits", justify="right", style="green")
    table.add_column("Share", justify="right", style="dim")
    table.add_column("", width=20)

    for rank, (name, count) in enumerate(counts.most_common(n), 1):
        pct = count / total if total else 0
        bar_len = int(pct * 18)
        bar = "█" * bar_len + "░" * (18 - bar_len)
        table.add_row(
            str(rank),
            name[:30],
            str(count),
            f"{pct*100:.1f}%",
            Text(bar, style="cyan"),
        )
    return table


def hot_files(root: str, n: int = 10) -> Table:
    raw = run_git(
        ["log", "--no-merges", "--name-only", "--pretty=format:"],
        root,
    )
    counts: Counter = Counter()
    for line in raw.splitlines():
        line = line.strip()
        if line:
            counts[line] += 1

    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("#", style="dim", width=3)
    table.add_column("File", style="white", no_wrap=True)
    table.add_column("Changes", justify="right", style="yellow")
    table.add_column("", width=18)

    total = max(counts.values(), default=1)
    for rank, (path, count) in enumerate(counts.most_common(n), 1):
        bar_len = int(count / total * 16)
        bar = "█" * bar_len + "░" * (16 - bar_len)
        # Truncate long paths nicely
        display = path if len(path) <= 42 else "…" + path[-41:]
        table.add_row(str(rank), display, str(count), Text(bar, style="yellow"))
    return table


def language_breakdown(root: str) -> Table:
    raw = run_git(["ls-files"], root)
    ext_count: Counter = Counter()
    for f in raw.splitlines():
        suffix = Path(f).suffix.lower()
        if suffix:
            ext_count[suffix] += 1
        else:
            ext_count["(none)"] += 1

    ext_labels = {
        ".py": "Python", ".rs": "Rust", ".js": "JavaScript", ".ts": "TypeScript",
        ".go": "Go", ".rb": "Ruby", ".java": "Java", ".c": "C", ".cpp": "C++",
        ".h": "C/C++ Header", ".sh": "Shell", ".md": "Markdown", ".toml": "TOML",
        ".yaml": "YAML", ".yml": "YAML", ".json": "JSON", ".html": "HTML",
        ".css": "CSS", ".scss": "SCSS", ".sql": "SQL", ".tf": "Terraform",
        ".tsx": "TSX", ".jsx": "JSX", ".kt": "Kotlin", ".swift": "Swift",
        ".ex": "Elixir", ".exs": "Elixir", ".hs": "Haskell", ".lua": "Lua",
    }

    lang_count: Counter = Counter()
    for ext, cnt in ext_count.items():
        label = ext_labels.get(ext, ext)
        lang_count[label] += cnt

    total = sum(lang_count.values()) or 1
    colours = ["cyan", "green", "yellow", "magenta", "blue", "red", "white"]

    table = Table(box=box.SIMPLE, show_header=False, padding=(0, 1))
    table.add_column("Lang", style="white", min_width=14)
    table.add_column("Files", justify="right", style="dim", width=6)
    table.add_column("%", justify="right", width=6)
    table.add_column("", width=20)

    for i, (lang, count) in enumerate(lang_count.most_common(10)):
        pct = count / total
        bar_len = int(pct * 18)
        bar = "█" * bar_len + "░" * (18 - bar_len)
        col = colours[i % len(colours)]
        table.add_row(lang, str(count), f"{pct*100:.1f}%", Text(bar, style=col))

    return table


def recent_commits(commits: list[dict], n: int = 12) -> Table:
    table = Table(box=box.SIMPLE, show_header=True, header_style="bold cyan", padding=(0, 1))
    table.add_column("SHA", style="dim", width=7)
    table.add_column("Date", style="dim", width=11)
    table.add_column("Author", style="cyan", width=16)
    table.add_column("Message", style="white")

    for c in commits[:n]:
        sha = c["sha"][:7]
        date = c["date"].strftime("%Y-%m-%d")
        author = c["name"][:15]
        subject = c["subject"][:60] + ("…" if len(c["subject"]) > 60 else "")
        table.add_row(sha, date, author, subject)

    return table


def activity_by_hour(commits: list[dict]) -> list:
    """Return 24 bar segments for commits by hour of day."""
    hour_counts = Counter(c["date"].hour for c in commits)
    peak = max(hour_counts.values(), default=1)
    bars = []
    for h in range(24):
        n = hour_counts.get(h, 0)
        height = int(n / peak * 7)
        bars.append((h, n, height))
    return bars


def render_hour_chart(bars: list) -> list[Text]:
    """Render a vertical bar chart for 24 hours."""
    height = 8
    chars = " ▁▂▃▄▅▆▇█"
    lines = []
    for row in range(height - 1, -1, -1):
        line = Text()
        for h, n, bar_h in bars:
            if bar_h > row:
                line.append("█", style="magenta")
            else:
                line.append(" ")
            if h % 6 == 5:
                line.append(" ")
        lines.append(line)
    # x-axis labels
    axis = Text()
    for h, _, _ in bars:
        label = str(h) if h % 6 == 0 else " "
        axis.append(label)
        if h % 6 == 5:
            axis.append(" ")
    lines.append(axis)
    return lines


def streak_info(commits: list[dict]) -> tuple[int, int]:
    """Return (current_streak, longest_streak) in days."""
    if not commits:
        return 0, 0
    dates = sorted({c["date"].date() for c in commits}, reverse=True)
    today = datetime.now().date()

    # Current streak
    current = 0
    check = today
    for d in dates:
        if d == check or d == check - timedelta(days=1):
            if d < check:
                check = d
            current += 1
            check = d - timedelta(days=1)
        elif d < check - timedelta(days=1):
            break

    # Longest streak
    longest = 1
    run = 1
    for i in range(1, len(dates)):
        if dates[i] == dates[i - 1] - timedelta(days=1):
            run += 1
            longest = max(longest, run)
        else:
            run = 1

    return current, longest


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "."
    path = os.path.abspath(path)

    if not os.path.exists(path):
        console.print(f"[red]Path does not exist:[/red] {path}")
        sys.exit(1)

    root = get_repo_root(path)
    if not root:
        console.print("[red]Not a git repository:[/red]", path)
        sys.exit(1)

    repo_name = os.path.basename(root)
    remote = run_git(["remote", "get-url", "origin"], root) or "(no remote)"
    branch = run_git(["rev-parse", "--abbrev-ref", "HEAD"], root)
    total_commits_raw = run_git(["rev-list", "--count", "HEAD"], root)
    total_commits = int(total_commits_raw) if total_commits_raw.isdigit() else 0

    console.print()
    console.rule(f"[bold white] gitdash [/bold white][dim]—[/dim][bold cyan] {repo_name} [/bold cyan]", style="bright_blue")
    console.print()

    # ── Summary bar ─────────────────────────────────────────────────────────
    commits = parse_log(root)
    authors = len({c["email"] for c in commits})
    first_date = min(c["date"] for c in commits).strftime("%Y-%m-%d") if commits else "—"
    last_date = max(c["date"] for c in commits).strftime("%Y-%m-%d") if commits else "—"
    current_streak, longest_streak = streak_info(commits)

    def stat(label: str, value: str, colour: str = "cyan") -> Text:
        t = Text()
        t.append(f"{value}\n", style=f"bold {colour}")
        t.append(label, style="dim")
        return t

    row1 = Table(box=None, show_header=False, padding=(0, 2))
    for _ in range(3):
        row1.add_column(justify="center", min_width=12)
    row1.add_row(
        stat("commits", f"{total_commits:,}"),
        stat("authors", str(authors), "green"),
        stat("branch", branch, "yellow"),
    )

    row2 = Table(box=None, show_header=False, padding=(0, 2))
    for _ in range(3):
        row2.add_column(justify="center", min_width=12)
    row2.add_row(
        stat("first commit", first_date, "magenta"),
        stat("last commit", last_date, "magenta"),
        stat("streak cur/best", f"{current_streak}d/{longest_streak}d", "red"),
    )

    console.print(Align.center(row1))
    console.print(Align.center(row2))
    console.print(f"  [dim]remote:[/dim] {remote}", highlight=False)
    console.print()

    # ── Heatmap ──────────────────────────────────────────────────────────────
    heatmap_lines, month_row = commit_heatmap(commits)
    heatmap_panel_lines = [Text("     " + month_row, style="dim")]
    heatmap_panel_lines.extend(heatmap_lines)
    legend = Text("     less ")
    for col in ["grey23", "dark_green", "green3", "green1", "bright_green"]:
        legend.append("█ ", style=col)
    legend.append("more", style="dim")
    heatmap_panel_lines.append(legend)

    heatmap_content = Text("\n").join(heatmap_panel_lines)
    console.print(Panel(heatmap_content, title="[bold]Commit Activity (90 days)[/bold]", border_style="bright_blue"))
    console.print()

    # ── Hour-of-day chart + Authors side-by-side ─────────────────────────────
    hour_bars = activity_by_hour(commits)
    hour_chart_lines = render_hour_chart(hour_bars)

    hour_text = Text()
    hour_text.append("  hour of day (24h)\n\n", style="dim")
    for line in hour_chart_lines:
        hour_text.append("  ")
        hour_text.append_text(line)
        hour_text.append("\n")

    hour_panel = Panel(hour_text, title="[bold]Commits by Hour[/bold]", border_style="magenta")
    authors_panel = Panel(top_authors(commits), title="[bold]Top Authors[/bold]", border_style="green")

    console.print(Columns([hour_panel, authors_panel]))
    console.print()

    # ── Hot files + Language breakdown ───────────────────────────────────────
    files_panel = Panel(hot_files(root), title="[bold]Most Changed Files[/bold]", border_style="yellow")
    lang_panel = Panel(language_breakdown(root), title="[bold]Language Breakdown[/bold]", border_style="cyan")

    console.print(Columns([files_panel, lang_panel]))
    console.print()

    # ── Recent commits ────────────────────────────────────────────────────────
    console.print(Panel(recent_commits(commits), title="[bold]Recent Commits[/bold]", border_style="white"))
    console.print()

    # ── Weekly velocity (last 12 weeks) ──────────────────────────────────────
    today = datetime.now().date()
    weeks: dict = defaultdict(int)
    for c in commits:
        d = c["date"].date()
        week_num = (today - d).days // 7
        if week_num < 12:
            weeks[week_num] += 1

    peak = max(weeks.values(), default=1)
    velocity_text = Text()
    velocity_text.append("  weeks ago  12  11  10   9   8   7   6   5   4   3   2   1  now\n", style="dim")
    velocity_text.append("  commits  ")
    for w in range(11, -1, -1):
        n = weeks.get(w, 0)
        bar_h = int(n / peak * 5) if peak else 0
        chars = " ▁▂▃▄▅"
        col = "bright_green" if w < 2 else ("green3" if w < 5 else "dim")
        velocity_text.append(f" {chars[bar_h]:>3}", style=col)
    velocity_text.append("\n  count    ")
    for w in range(11, -1, -1):
        n = weeks.get(w, 0)
        velocity_text.append(f" {n:>3}", style="dim")

    console.print(Panel(velocity_text, title="[bold]Weekly Velocity[/bold]", border_style="bright_blue"))
    console.print()


if __name__ == "__main__":
    main()
