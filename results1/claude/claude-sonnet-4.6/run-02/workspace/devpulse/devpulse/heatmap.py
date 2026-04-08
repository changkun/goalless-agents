"""GitHub-style commit activity heatmap (last 52 weeks)."""

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from .git import Commit
from .render import (
    RESET, BOLD, DIM, BRIGHT_WHITE, BRIGHT_CYAN, YELLOW, GREEN,
    BG_BLACK, BG_GREEN_1, BG_GREEN_2, BG_GREEN_3, BG_GREEN_4, BG_GREEN_5,
    NO_COLOR, c, h1, muted,
)

DAY_LABELS = ["Mon", "   ", "Wed", "   ", "Fri", "   ", "   "]
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

# Heat levels: (min_commits, bg_color, char)
HEAT_LEVELS = [
    (0,  BG_BLACK,   "  "),
    (1,  BG_GREEN_1, "  "),
    (3,  BG_GREEN_2, "  "),
    (6,  BG_GREEN_3, "  "),
    (10, BG_GREEN_4, "  "),
    (15, BG_GREEN_5, "  "),
]


def _heat_cell(n: int) -> str:
    """Return the colored cell string for n commits."""
    level = HEAT_LEVELS[0]
    for threshold, bg, ch in HEAT_LEVELS:
        if n >= threshold:
            level = (threshold, bg, ch)
    _, bg, ch = level
    if NO_COLOR:
        return "██" if n > 0 else "░░"
    return f"{bg}{ch}{RESET}"


def render_heatmap(commits: list[Commit]) -> list[str]:
    """
    Return a list of strings forming the heatmap block.
    Layout: 7 rows (Mon–Sun), 53 columns (weeks), newest on the right.
    """
    now = datetime.now(tz=timezone.utc)
    # Align to the most recent Sunday so the rightmost column ends today
    today_weekday = now.weekday()  # 0=Mon … 6=Sun
    # We want columns to be Sun-started weeks (like GitHub)
    # Adjust so the last column ends on the coming Saturday (or today)
    end = now.replace(hour=23, minute=59, second=59)
    # go to end of the current week (Saturday)
    days_to_saturday = (5 - today_weekday) % 7
    end += timedelta(days=days_to_saturday)

    WEEKS = 53
    start = end - timedelta(weeks=WEEKS)

    # Count commits per calendar date
    counts: dict[tuple[int, int, int], int] = defaultdict(int)
    for commit in commits:
        d = commit.timestamp.astimezone(timezone.utc)
        counts[(d.year, d.month, d.day)] += 1

    # Build a 7-row × WEEKS-col grid
    # col 0 = oldest week, col WEEKS-1 = newest
    grid: list[list[int]] = [[0] * WEEKS for _ in range(7)]
    month_markers: dict[int, str] = {}  # col -> month label

    for col in range(WEEKS):
        for row in range(7):  # 0=Sun, 1=Mon, … 6=Sat
            day_offset = col * 7 + row
            d = start + timedelta(days=day_offset)
            if d > end:
                continue
            grid[row][col] = counts.get((d.year, d.month, d.day), 0)
            # Track month transitions for header
            if d.day <= 7 and col not in month_markers:
                month_markers[col] = MONTH_ABBR[d.month - 1]

    # ── Build output lines ──────────────────────────────────────────────────
    lines: list[str] = []

    # Month header row
    header = "     "  # indent for day labels (4 chars + space)
    prev_label_end = -1
    for col in range(WEEKS):
        label = month_markers.get(col, "")
        if label and col > prev_label_end:
            header += c(BRIGHT_CYAN, label)
            prev_label_end = col + 3
        elif col > prev_label_end:
            header += "  "  # 2-char wide cell
        # else skip (we're inside a label)
    lines.append(header)

    # Day rows (7 rows: Sun=0 … Sat=6)
    DOW_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    for row in range(7):
        label = c(DIM, DOW_LABELS[row]) if row in (1, 3, 5) else "   "
        row_str = label + " "
        for col in range(WEEKS):
            row_str += _heat_cell(grid[row][col])
        lines.append(row_str)

    # Legend
    legend = "     " + c(DIM, "Less ")
    for threshold, bg, ch in HEAT_LEVELS:
        legend += _heat_cell(threshold)
    legend += c(DIM, " More")
    lines.append("")
    lines.append(legend)

    # Stats line
    total = sum(counts.values())
    active_days = sum(1 for v in counts.values() if v > 0)
    streak = _max_streak(counts, end)
    stats = (
        f"     {c(BOLD, str(total))} commits over "
        f"{c(BOLD, str(active_days))} active days  "
        f"longest streak: {c(BRIGHT_CYAN, str(streak))} days"
    )
    lines.append(stats)

    return lines


def _max_streak(counts: dict, end: datetime) -> int:
    """Compute the longest consecutive-day commit streak."""
    streak = 0
    best = 0
    d = end
    while True:
        key = (d.year, d.month, d.day)
        if counts.get(key, 0) > 0:
            streak += 1
            best = max(best, streak)
        else:
            streak = 0
        d -= timedelta(days=1)
        if d < end - timedelta(days=365 * 2):
            break
    return best
