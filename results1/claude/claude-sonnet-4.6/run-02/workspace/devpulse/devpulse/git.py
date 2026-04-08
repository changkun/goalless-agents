"""Git data extraction — runs git commands and parses their output."""

import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class Commit:
    sha: str
    author: str
    email: str
    timestamp: datetime
    subject: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0


@dataclass
class FileChurn:
    path: str
    changes: int = 0
    insertions: int = 0
    deletions: int = 0
    last_commit: datetime | None = None
    authors: set[str] = field(default_factory=set)


def _run(args: list[str], cwd: Path) -> str:
    try:
        result = subprocess.run(
            args,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"[devpulse] git error: {e.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("[devpulse] git not found in PATH", file=sys.stderr)
        sys.exit(1)


def get_root(path: Path) -> Path:
    """Return the git repo root, or exit if not a git repo."""
    try:
        root = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            cwd=path,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
        return Path(root)
    except subprocess.CalledProcessError:
        print(f"[devpulse] {path} is not inside a git repository", file=sys.stderr)
        sys.exit(1)


def get_commits(repo: Path, since_days: int = 365) -> list[Commit]:
    """Return commits from the last `since_days` days, newest first."""
    since = f"--since={since_days} days ago"
    log = _run(
        [
            "git", "log",
            "--format=%H\x1f%an\x1f%ae\x1f%at\x1f%s",
            since,
        ],
        cwd=repo,
    )
    commits = []
    for line in log.splitlines():
        if not line.strip():
            continue
        parts = line.split("\x1f", 4)
        if len(parts) < 5:
            continue
        sha, author, email, ts, subject = parts
        try:
            dt = datetime.fromtimestamp(int(ts), tz=timezone.utc)
        except ValueError:
            continue
        commits.append(Commit(sha=sha, author=author, email=email, timestamp=dt, subject=subject))

    # Fetch numstat for all commits in one pass to avoid N+1 git calls
    if not commits:
        return commits

    numstat_raw = _run(
        [
            "git", "log",
            "--format=COMMIT %H",
            "--numstat",
            "--date=format:%s",
            since,
        ],
        cwd=repo,
    )

    # Index commits by sha for fast lookup
    by_sha: dict[str, Commit] = {c.sha: c for c in commits}
    current_sha = None
    for line in numstat_raw.splitlines():
        if line.startswith("COMMIT "):
            current_sha = line[7:].strip()
        elif current_sha and line.strip():
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, _ = parts
                c = by_sha.get(current_sha)
                if c:
                    try:
                        c.insertions += int(added) if added != "-" else 0
                        c.deletions += int(deleted) if deleted != "-" else 0
                        c.files_changed += 1
                    except ValueError:
                        pass

    return commits


def get_file_churn(repo: Path, since_days: int = 365) -> list[FileChurn]:
    """Return per-file churn stats, sorted by change count descending."""
    since = f"--since={since_days} days ago"
    raw = _run(
        [
            "git", "log",
            "--format=COMMIT %H %ae %at",
            "--numstat",
            since,
        ],
        cwd=repo,
    )

    files: dict[str, FileChurn] = {}
    current_email = ""
    current_ts: datetime | None = None

    for line in raw.splitlines():
        if line.startswith("COMMIT "):
            parts = line.split(" ", 3)
            current_email = parts[2] if len(parts) > 2 else ""
            try:
                current_ts = datetime.fromtimestamp(int(parts[3]), tz=timezone.utc)
            except (ValueError, IndexError):
                current_ts = None
        elif line.strip():
            parts = line.split("\t")
            if len(parts) == 3:
                added, deleted, path = parts
                if path not in files:
                    files[path] = FileChurn(path=path)
                fc = files[path]
                fc.changes += 1
                try:
                    fc.insertions += int(added) if added != "-" else 0
                    fc.deletions += int(deleted) if deleted != "-" else 0
                except ValueError:
                    pass
                if current_email:
                    fc.authors.add(current_email)
                if current_ts and (fc.last_commit is None or current_ts > fc.last_commit):
                    fc.last_commit = current_ts

    return sorted(files.values(), key=lambda f: f.changes, reverse=True)
