"""Git repository analysis — extract commits, diffs, and file changes."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Commit:
    sha: str
    short_sha: str
    author: str
    date: str
    subject: str
    body: str


@dataclass
class FileChange:
    path: str
    status: str  # A=added, M=modified, D=deleted, R=renamed
    additions: int
    deletions: int


@dataclass
class RepoSnapshot:
    repo_path: str
    branch: str
    commits: list[Commit]
    file_changes: list[FileChange]
    diff_summary: str       # stat-only diff (always included)
    diff_patch: str         # full patch, may be truncated
    patch_truncated: bool


_MAX_PATCH_BYTES = 80_000  # ~20k tokens — leave room for system prompt + response


def _run(args: list[str], cwd: str) -> str:
    result = subprocess.run(
        args,
        cwd=cwd,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0 and result.stderr:
        raise RuntimeError(f"git error: {result.stderr.strip()}")
    return result.stdout


def _current_branch(cwd: str) -> str:
    try:
        return _run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd).strip()
    except RuntimeError:
        return "HEAD"


def _commits(cwd: str, since: str | None, until: str | None, max_commits: int) -> list[Commit]:
    sep = "\x1f"
    fmt = f"%H{sep}%h{sep}%an{sep}%ad{sep}%s{sep}%b\x1e"
    args = ["git", "log", f"--format={fmt}", "--date=short"]
    if since:
        args += [f"--since={since}"]
    if until:
        args += [f"--until={until}"]
    args += [f"-{max_commits}"]

    raw = _run(args, cwd)
    commits = []
    for record in raw.split("\x1e"):
        record = record.strip()
        if not record:
            continue
        parts = record.split(sep, 5)
        if len(parts) < 5:
            continue
        commits.append(Commit(
            sha=parts[0],
            short_sha=parts[1],
            author=parts[2],
            date=parts[3],
            subject=parts[4],
            body=parts[5].strip() if len(parts) > 5 else "",
        ))
    return commits


def _file_changes(cwd: str, since_ref: str, until_ref: str | None = None) -> list[FileChange]:
    range_arg = f"{since_ref}..{until_ref}" if until_ref else f"{since_ref}..HEAD"
    try:
        numstat = _run(
            ["git", "diff", "--numstat", range_arg],
            cwd,
        )
        name_status = _run(
            ["git", "diff", "--name-status", range_arg],
            cwd,
        )
    except RuntimeError:
        return []

    statuses: dict[str, str] = {}
    for line in name_status.splitlines():
        parts = line.split("\t", 2)
        if len(parts) >= 2:
            status_code = parts[0][0]  # First char: A/M/D/R/C
            path = parts[-1]            # Last part handles renames (old\tnew)
            statuses[path] = status_code

    changes = []
    for line in numstat.splitlines():
        parts = line.split("\t", 2)
        if len(parts) < 3:
            continue
        try:
            add = int(parts[0]) if parts[0] != "-" else 0
            delete = int(parts[1]) if parts[1] != "-" else 0
        except ValueError:
            add = delete = 0
        path = parts[2]
        status = statuses.get(path, "M")
        changes.append(FileChange(
            path=path,
            status=status,
            additions=add,
            deletions=delete,
        ))

    # Sort by impact (most changed first)
    changes.sort(key=lambda c: c.additions + c.deletions, reverse=True)
    return changes


def _diff_stat(cwd: str, range_arg: str) -> str:
    try:
        return _run(["git", "diff", "--stat", range_arg], cwd)
    except RuntimeError:
        return ""


def _diff_patch(cwd: str, range_arg: str) -> tuple[str, bool]:
    try:
        patch = _run(
            ["git", "diff",
             "--unified=3",
             "--no-color",
             range_arg],
            cwd,
        )
    except RuntimeError:
        return "", False

    encoded = patch.encode("utf-8", errors="replace")
    if len(encoded) <= _MAX_PATCH_BYTES:
        return patch, False

    truncated = encoded[:_MAX_PATCH_BYTES].decode("utf-8", errors="replace")
    # Trim to last complete line
    last_newline = truncated.rfind("\n")
    if last_newline > 0:
        truncated = truncated[:last_newline]
    return truncated, True


def analyze(
    repo_path: str,
    since: str | None = None,
    until: str | None = None,
    max_commits: int = 50,
) -> RepoSnapshot:
    """Analyze a git repository and return a snapshot of recent changes."""
    path = Path(repo_path).resolve()
    if not path.exists():
        raise ValueError(f"Path does not exist: {repo_path}")

    cwd = str(path)

    # Validate it's a git repo
    try:
        _run(["git", "rev-parse", "--git-dir"], cwd)
    except RuntimeError as e:
        raise ValueError(f"Not a git repository: {repo_path}") from e

    branch = _current_branch(cwd)
    commits = _commits(cwd, since, until, max_commits)

    if not commits:
        return RepoSnapshot(
            repo_path=str(path),
            branch=branch,
            commits=[],
            file_changes=[],
            diff_summary="No commits found in the specified range.",
            diff_patch="",
            patch_truncated=False,
        )

    oldest_sha = commits[-1].sha
    newest_sha = commits[0].sha

    # Determine the base ref: parent of oldest commit, or empty-tree if it's the root commit.
    # git's well-known empty tree SHA works as a diff base against the very first commit.
    _EMPTY_TREE = "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    try:
        _run(["git", "rev-parse", "--verify", f"{oldest_sha}^"], cwd)
        base_ref = f"{oldest_sha}^"
    except RuntimeError:
        base_ref = _EMPTY_TREE

    range_arg = f"{base_ref}..{newest_sha}"

    file_changes = _file_changes(cwd, base_ref, newest_sha)
    diff_summary = _diff_stat(cwd, range_arg)
    diff_patch, patch_truncated = _diff_patch(cwd, range_arg)

    return RepoSnapshot(
        repo_path=str(path),
        branch=branch,
        commits=commits,
        file_changes=file_changes,
        diff_summary=diff_summary,
        diff_patch=diff_patch,
        patch_truncated=patch_truncated,
    )
