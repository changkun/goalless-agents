"""Contributor, time-of-day, and summary statistics."""

from collections import defaultdict
from datetime import timezone

from .git import Commit
from .render import (
    BOLD, DIM, RESET,
    BRIGHT_WHITE, BRIGHT_CYAN, BRIGHT_GREEN, BRIGHT_YELLOW, BRIGHT_RED,
    YELLOW, GREEN, RED,
    c, bar, num, truncate, term_width,
)

# 24-wide sparkline characters (block elements)
SPARK_CHARS = " ▁▂▃▄▅▆▇█"

HOUR_LABELS = [
    "12am", "1", "2", "3", "4", "5",
    "6am",  "7", "8", "9", "10", "11",
    "12pm", "1", "2", "3", "4", "5",
    "6pm",  "7", "8", "9", "10", "11",
]


def render_contributors(commits: list[Commit], top_n: int = 10) -> list[str]:
    """Return lines for the contributors panel."""
    author_commits: dict[str, int] = defaultdict(int)
    author_lines: dict[str, int] = defaultdict(int)
    for c_ in commits:
        key = c_.author
        author_commits[key] += 1
        author_lines[key] += c_.insertions + c_.deletions

    if not author_commits:
        return [c(DIM, "  No contributor data.")]

    sorted_authors = sorted(author_commits.items(), key=lambda x: x[1], reverse=True)
    max_commits = sorted_authors[0][1]
    total_commits = sum(v for _, v in sorted_authors)

    lines: list[str] = []
    header = f"  {'Author':<28}  {'Commits':>8}  {'Share':>6}  {'Lines':>10}"
    lines.append(c(DIM, header))
    lines.append(c(DIM, "  " + "─" * (term_width() - 4)))

    for author, commits_n in sorted_authors[:top_n]:
        pct = commits_n / total_commits * 100
        lines_n = author_lines[author]
        bar_len = round(commits_n / max_commits * 20)
        bar_str = c(BRIGHT_GREEN, "█" * bar_len) + c(DIM, "░" * (20 - bar_len))
        lines.append(
            f"  {c(BRIGHT_WHITE, truncate(author, 28)): <28}"
            f"  {c(BRIGHT_CYAN,  f'{commits_n:>8,}')}"
            f"  {c(YELLOW,       f'{pct:>5.1f}%')}"
            f"  {c(DIM,          f'{lines_n:>10,}')}"
            f"  {bar_str}"
        )

    if len(sorted_authors) > top_n:
        lines.append(c(DIM, f"\n  … and {len(sorted_authors) - top_n} more contributors"))
    return lines


def render_time_heatmap(commits: list[Commit]) -> list[str]:
    """
    Show a sparkline of commits by hour of day (24h),
    plus a day-of-week distribution.
    """
    hour_counts: list[int] = [0] * 24
    dow_counts: list[int] = [0] * 7  # 0=Mon … 6=Sun

    for commit in commits:
        local = commit.timestamp.astimezone()  # system local tz
        hour_counts[local.hour] += 1
        dow_counts[local.weekday()] += 1

    max_hour = max(hour_counts) if hour_counts else 1
    max_dow = max(dow_counts) if dow_counts else 1

    lines: list[str] = []

    # ── Hour sparkline ────────────────────────────────────────────────────
    lines.append(c(DIM, "  Commits by hour of day:"))
    spark = "  "
    for h, count in enumerate(hour_counts):
        level = round(count / max_hour * (len(SPARK_CHARS) - 1)) if max_hour else 0
        ch = SPARK_CHARS[level]
        color = BRIGHT_GREEN if count == max_hour else (BRIGHT_CYAN if count > max_hour * 0.5 else DIM)
        spark += c(color, ch * 2)
    lines.append(spark)

    # Hour axis labels (every 6 hours)
    axis = "  "
    for h in range(24):
        if h % 6 == 0:
            label = HOUR_LABELS[h]
            axis += c(DIM, f"{label:<12}")
    lines.append(axis)
    lines.append("")

    # ── Day-of-week bar chart ─────────────────────────────────────────────
    DOW = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    lines.append(c(DIM, "  Commits by day of week:"))
    for i, (day, count) in enumerate(zip(DOW, dow_counts)):
        is_weekend = i >= 5
        bar_len = round(count / max_dow * 30) if max_dow else 0
        bar_color = DIM if is_weekend else BRIGHT_GREEN
        bar_str = c(bar_color, "█" * bar_len) + c(DIM, "░" * (30 - bar_len))
        lines.append(
            f"  {c(DIM if is_weekend else BRIGHT_WHITE, day)}"
            f"  {bar_str}"
            f"  {c(BRIGHT_CYAN, f'{count:>5,}')}"
        )
    return lines


def render_summary(commits: list[Commit]) -> list[str]:
    """Return a compact summary row."""
    if not commits:
        return [c(DIM, "  No commits found.")]

    total_commits = len(commits)
    total_insertions = sum(c_.insertions for c_ in commits)
    total_deletions = sum(c_.deletions for c_ in commits)
    unique_authors = len({c_.email for c_ in commits})

    # Commits per day
    days_span = max(
        (commits[0].timestamp - commits[-1].timestamp).days, 1
    )
    cpm = total_commits / max(days_span, 1)

    lines = [
        f"  {c(BOLD + BRIGHT_WHITE, f'{total_commits:,}')} commits  "
        f"{c(BRIGHT_GREEN,  f'+{total_insertions:,}')} insertions  "
        f"{c(BRIGHT_RED,    f'-{total_deletions:,}')} deletions  "
        f"{c(BRIGHT_CYAN,   f'{unique_authors}')} contributors  "
        f"{c(YELLOW,        f'{cpm:.1f}')} commits/day"
    ]
    return lines
