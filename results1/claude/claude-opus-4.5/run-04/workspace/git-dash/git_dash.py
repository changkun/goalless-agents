#!/usr/bin/env python3
"""git-dash: Compact git repository dashboard for token-efficient output."""

import subprocess
import sys
import os
from dataclasses import dataclass
from typing import Optional

COLORS = {
    'reset': '\033[0m',
    'bold': '\033[1m',
    'red': '\033[31m',
    'green': '\033[32m',
    'yellow': '\033[33m',
    'blue': '\033[34m',
    'cyan': '\033[36m',
    'dim': '\033[2m',
}

def c(text: str, *styles: str) -> str:
    """Apply color/style to text."""
    if not sys.stdout.isatty():
        return text
    codes = ''.join(COLORS.get(s, '') for s in styles)
    return f"{codes}{text}{COLORS['reset']}"


def run(cmd: list[str], default: str = '') -> str:
    """Run git command, return stdout or default on failure."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() if result.returncode == 0 else default
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return default


@dataclass
class RepoInfo:
    branch: str
    upstream: Optional[str]
    ahead: int
    behind: int
    staged: int
    modified: int
    untracked: int
    stashes: int
    last_commit: str
    last_author: str
    last_time: str
    total_commits: int
    contributors: int
    remote_url: str


def get_repo_info() -> Optional[RepoInfo]:
    """Gather repository information."""
    # Check if in git repo
    if run(['git', 'rev-parse', '--git-dir']) == '':
        return None

    branch = run(['git', 'branch', '--show-current']) or run(
        ['git', 'rev-parse', '--short', 'HEAD'], 'detached'
    )

    # Upstream tracking
    upstream = run(['git', 'rev-parse', '--abbrev-ref', '@{u}'])
    ahead = behind = 0
    if upstream:
        ab = run(['git', 'rev-list', '--left-right', '--count', f'{branch}...@{{u}}'])
        if ab:
            parts = ab.split()
            ahead, behind = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0

    # Status counts
    status = run(['git', 'status', '--porcelain'])
    staged = modified = untracked = 0
    for line in status.splitlines():
        if len(line) >= 2:
            x, y = line[0], line[1]
            if x in 'MADRC':
                staged += 1
            if y in 'MD':
                modified += 1
            if x == '?':
                untracked += 1

    stashes = len(run(['git', 'stash', 'list']).splitlines()) if run(['git', 'stash', 'list']) else 0

    # Last commit
    last_commit = run(['git', 'log', '-1', '--format=%s'])[:50]
    last_author = run(['git', 'log', '-1', '--format=%an'])
    last_time = run(['git', 'log', '-1', '--format=%ar'])

    # Stats
    total_commits = int(run(['git', 'rev-list', '--count', 'HEAD'], '0'))
    contributors = len(set(run(['git', 'log', '--format=%ae']).splitlines())) if total_commits else 0

    remote_url = run(['git', 'remote', 'get-url', 'origin'])

    return RepoInfo(
        branch=branch,
        upstream=upstream or None,
        ahead=ahead,
        behind=behind,
        staged=staged,
        modified=modified,
        untracked=untracked,
        stashes=stashes,
        last_commit=last_commit,
        last_author=last_author,
        last_time=last_time,
        total_commits=total_commits,
        contributors=contributors,
        remote_url=remote_url,
    )


def format_status_line(info: RepoInfo) -> str:
    """Format working tree status."""
    parts = []
    if info.staged:
        parts.append(c(f'+{info.staged}', 'green'))
    if info.modified:
        parts.append(c(f'~{info.modified}', 'yellow'))
    if info.untracked:
        parts.append(c(f'?{info.untracked}', 'dim'))
    if info.stashes:
        parts.append(c(f'${info.stashes}', 'cyan'))
    return ' '.join(parts) if parts else c('clean', 'green')


def format_sync_status(info: RepoInfo) -> str:
    """Format ahead/behind status."""
    if not info.upstream:
        return c('no upstream', 'dim')
    parts = []
    if info.ahead:
        parts.append(c(f'{info.ahead}', 'green', 'bold'))
    if info.behind:
        parts.append(c(f'{info.behind}', 'red', 'bold'))
    if not parts:
        return c('synced', 'green')
    return '/'.join(parts)


def print_dashboard(info: RepoInfo) -> None:
    """Print the compact dashboard."""
    # Header with branch
    branch_display = c(info.branch, 'cyan', 'bold')
    if info.upstream:
        branch_display += c(f'  {info.upstream}', 'dim')
    print(branch_display)

    # Status line
    status = format_status_line(info)
    sync = format_sync_status(info)
    print(f"  {status}  {sync}")

    # Last commit
    if info.last_commit:
        commit_line = f"  {c(info.last_commit, 'bold')}"
        meta = f"{info.last_author}, {info.last_time}"
        print(f"{commit_line}  {c(meta, 'dim')}")

    # Stats
    stats = f"  {info.total_commits} commits"
    if info.contributors > 1:
        stats += f", {info.contributors} contributors"
    print(c(stats, 'dim'))


def print_help():
    print("""git-dash: Compact git repository dashboard

Usage: git-dash [options]

Options:
  -h, --help     Show this help
  -j, --json     Output as JSON
  -o, --oneline  Single line output

Status symbols:
  +N  staged files     ~N  modified files
  ?N  untracked        $N  stashes
  /  ahead/behind upstream""")


def print_oneline(info: RepoInfo) -> None:
    """Print single-line summary."""
    parts = [c(info.branch, 'cyan')]
    if info.staged or info.modified or info.untracked:
        status = []
        if info.staged: status.append(f'+{info.staged}')
        if info.modified: status.append(f'~{info.modified}')
        if info.untracked: status.append(f'?{info.untracked}')
        parts.append(''.join(status))
    if info.ahead or info.behind:
        sync = ''
        if info.ahead: sync += f'{info.ahead}'
        if info.behind: sync += f'{info.behind}'
        parts.append(sync)
    print(' '.join(parts))


def print_json(info: RepoInfo) -> None:
    """Print JSON output."""
    import json
    print(json.dumps({
        'branch': info.branch,
        'upstream': info.upstream,
        'ahead': info.ahead,
        'behind': info.behind,
        'staged': info.staged,
        'modified': info.modified,
        'untracked': info.untracked,
        'stashes': info.stashes,
        'last_commit': info.last_commit,
        'last_author': info.last_author,
        'last_time': info.last_time,
        'total_commits': info.total_commits,
        'contributors': info.contributors,
    }, indent=2))


def main():
    args = sys.argv[1:]

    if '-h' in args or '--help' in args:
        print_help()
        return

    info = get_repo_info()
    if not info:
        print(c('Not a git repository', 'red'))
        sys.exit(1)

    if '-j' in args or '--json' in args:
        print_json(info)
    elif '-o' in args or '--oneline' in args:
        print_oneline(info)
    else:
        print_dashboard(info)


if __name__ == '__main__':
    main()
