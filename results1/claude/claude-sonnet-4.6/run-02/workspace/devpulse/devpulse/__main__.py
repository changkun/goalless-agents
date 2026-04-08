"""devpulse — git repository analytics dashboard.

Usage:
    python -m devpulse [PATH] [--days N] [--no-heatmap] [--json]
    devpulse [PATH] [--days N]
"""

import argparse
import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from . import __version__
from .git import get_commits, get_file_churn, get_root
from .heatmap import render_heatmap
from .churn import render_churn, render_language_breakdown
from .stats import render_contributors, render_time_heatmap, render_summary
from .render import (
    BOLD, DIM, RESET, BRIGHT_WHITE, BRIGHT_CYAN, YELLOW, BRIGHT_GREEN,
    c, section, section_end, h1, h2, muted, term_width,
)


def _banner(repo: Path, days: int) -> None:
    width = term_width()
    title = f" devpulse v{__version__} "
    pad = (width - len(title) - 2) // 2
    print()
    print(c(BOLD + BRIGHT_CYAN, "━" * width))
    print(c(BOLD + BRIGHT_CYAN, "┃") + " " * pad + c(BOLD + BRIGHT_WHITE, title) + " " * (width - pad - len(title) - 2) + c(BOLD + BRIGHT_CYAN, "┃"))
    print(c(BOLD + BRIGHT_CYAN, "━" * width))
    print(
        c(DIM, f"  repo: {repo}")
        + "   "
        + c(DIM, f"window: last {days} days")
        + "   "
        + c(DIM, f"generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    )
    print()


def _section(title: str) -> None:
    print()
    width = term_width()
    bar = "─" * (width - len(title) - 5)
    print(c(BOLD + BRIGHT_CYAN, f"┌─ {title} ") + c(BRIGHT_CYAN, bar + "┐"))
    print()


def _section_end() -> None:
    print()
    width = term_width()
    print(c(BRIGHT_CYAN, "└" + "─" * (width - 2) + "┘"))


def _separator() -> None:
    print(c(DIM, "  " + "·" * (term_width() - 4)))


def run_dashboard(repo: Path, days: int, no_heatmap: bool = False) -> None:
    print(c(DIM, f"\n  Analyzing {repo} …"), end="", flush=True)
    t0 = time.monotonic()
    commits = get_commits(repo, since_days=days)
    files = get_file_churn(repo, since_days=days)
    elapsed = time.monotonic() - t0
    print(c(DIM, f" done in {elapsed:.1f}s"))

    _banner(repo, days)

    # ── Summary ───────────────────────────────────────────────────────────
    _section("Summary")
    for line in render_summary(commits):
        print(line)
    _section_end()

    # ── Commit Heatmap ────────────────────────────────────────────────────
    if not no_heatmap:
        _section("Commit Activity — last 52 weeks")
        for line in render_heatmap(commits):
            print(line)
        _section_end()

    # ── Commit Timing ─────────────────────────────────────────────────────
    _section("Commit Timing")
    for line in render_time_heatmap(commits):
        print(line)
    _section_end()

    # ── Contributors ──────────────────────────────────────────────────────
    _section("Top Contributors")
    for line in render_contributors(commits):
        print(line)
    _section_end()

    # ── File Churn ────────────────────────────────────────────────────────
    _section("Hottest Files (by change frequency)")
    for line in render_churn(files):
        print(line)
    _section_end()

    # ── Language Breakdown ────────────────────────────────────────────────
    _section("Language Breakdown")
    for line in render_language_breakdown(files):
        print(line)
    _section_end()

    # ── Recent commits ────────────────────────────────────────────────────
    _section("Recent Commits (last 20)")
    if commits:
        for commit in commits[:20]:
            age = datetime.now(tz=timezone.utc) - commit.timestamp
            if age.days > 0:
                age_str = f"{age.days}d ago"
            elif age.seconds >= 3600:
                age_str = f"{age.seconds // 3600}h ago"
            else:
                age_str = f"{age.seconds // 60}m ago"

            print(
                f"  {c(DIM, commit.sha[:7])}"
                f"  {c(DIM, f'{age_str:>7}')}"
                f"  {c(BRIGHT_GREEN, f'+{commit.insertions:<5}')}"
                f"  {c(BRIGHT_CYAN,  f'-{commit.deletions:<5}')}"
                f"  {c(BRIGHT_WHITE, commit.subject[:70])}"
                f"  {c(DIM, commit.author)}"
            )
    _section_end()
    print()


def run_json(repo: Path, days: int) -> None:
    """Emit a JSON summary for scripting."""
    commits = get_commits(repo, since_days=days)
    files = get_file_churn(repo, since_days=days)

    author_commits: dict[str, int] = {}
    for c_ in commits:
        author_commits[c_.author] = author_commits.get(c_.author, 0) + 1

    data = {
        "repo": str(repo),
        "days": days,
        "generated": datetime.now(tz=timezone.utc).isoformat(),
        "summary": {
            "total_commits": len(commits),
            "total_insertions": sum(c_.insertions for c_ in commits),
            "total_deletions": sum(c_.deletions for c_ in commits),
            "unique_contributors": len({c_.email for c_ in commits}),
        },
        "top_contributors": [
            {"author": a, "commits": n}
            for a, n in sorted(author_commits.items(), key=lambda x: x[1], reverse=True)[:10]
        ],
        "hottest_files": [
            {
                "path": f.path,
                "changes": f.changes,
                "insertions": f.insertions,
                "deletions": f.deletions,
                "authors": list(f.authors),
            }
            for f in files[:20]
        ],
    }
    print(json.dumps(data, indent=2))


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="devpulse",
        description="Git repository analytics dashboard",
    )
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Path to a git repository (default: current directory)",
    )
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        metavar="N",
        help="Number of days to look back (default: 365)",
    )
    parser.add_argument(
        "--no-heatmap",
        action="store_true",
        help="Skip the activity heatmap",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output JSON instead of the dashboard",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"devpulse {__version__}",
    )
    args = parser.parse_args()

    repo = get_root(Path(args.path).resolve())

    if args.json:
        run_json(repo, args.days)
    else:
        run_dashboard(repo, args.days, no_heatmap=args.no_heatmap)


if __name__ == "__main__":
    main()
