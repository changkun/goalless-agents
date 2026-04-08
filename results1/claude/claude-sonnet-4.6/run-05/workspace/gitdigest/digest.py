"""Claude API integration — generate an intelligent digest from a RepoSnapshot."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import anthropic

from .git import RepoSnapshot

_MODEL = "claude-opus-4-6"  # Override with GITDIGEST_MODEL env var if needed

_SYSTEM = """\
You are an expert software engineer writing concise, accurate digests of git repository changes.
Your audience is the developer team — engineers who want a quick, clear summary for standups,
release notes, or PR context. Focus on what changed and why it matters. Be specific and concrete.
"""


def _build_prompt(snap: RepoSnapshot, focus: str | None) -> str:
    repo_name = Path(snap.repo_path).name
    n = len(snap.commits)

    lines: list[str] = []
    lines.append(f"# Repository: {repo_name}")
    lines.append(f"Branch: {snap.branch}")
    lines.append(f"Commits analyzed: {n}")
    lines.append("")

    if snap.commits:
        first_date = snap.commits[-1].date
        last_date = snap.commits[0].date
        date_range = f"{first_date}" if first_date == last_date else f"{first_date} → {last_date}"
        lines.append(f"Date range: {date_range}")
        lines.append("")

    # Commit log
    lines.append("## Commits (newest first)")
    for c in snap.commits:
        body_preview = f"\n   {c.body[:120]}..." if c.body and len(c.body) > 10 else (f"\n   {c.body}" if c.body else "")
        lines.append(f"- [{c.short_sha}] {c.date} {c.author}: {c.subject}{body_preview}")
    lines.append("")

    # File change summary
    if snap.file_changes:
        lines.append("## Files Changed (by impact)")
        status_labels = {"A": "added", "M": "modified", "D": "deleted", "R": "renamed", "C": "copied"}
        for fc in snap.file_changes[:40]:  # cap at 40 files
            label = status_labels.get(fc.status, fc.status)
            lines.append(f"- {fc.path} ({label}, +{fc.additions} -{fc.deletions})")
        if len(snap.file_changes) > 40:
            lines.append(f"... and {len(snap.file_changes) - 40} more files")
        lines.append("")

    # Diff stat
    if snap.diff_summary:
        lines.append("## Diff Summary")
        lines.append("```")
        lines.append(snap.diff_summary.strip())
        lines.append("```")
        lines.append("")

    # Full patch (may be truncated)
    if snap.diff_patch:
        truncation_note = "\n[PATCH TRUNCATED — showing first ~80KB of changes]" if snap.patch_truncated else ""
        lines.append(f"## Patch{truncation_note}")
        lines.append("```diff")
        lines.append(snap.diff_patch.strip())
        lines.append("```")
        lines.append("")

    if focus:
        lines.append(f"## Focus Area")
        lines.append(focus)
        lines.append("")

    lines.append("---")
    lines.append("")
    lines.append(
        "Please generate a clear, well-structured digest of these changes. Include:\n"
        "1. **Summary** — 2-4 sentence overview of what changed and the overall scope\n"
        "2. **Key Changes** — bullet list of the most significant changes (with file references)\n"
        "3. **Areas Touched** — grouped by functional area (e.g., API, tests, docs, infra)\n"
        "4. **Notable Details** — anything worth calling out (breaking changes, refactors, "
        "new dependencies, performance impacts, security considerations)\n"
        "5. **Standup Summary** — one or two sentences suitable for a daily standup\n\n"
        "Skip any section that isn't applicable. Be concrete; don't pad with filler."
    )

    return "\n".join(lines)


def generate(
    snap: RepoSnapshot,
    focus: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    stream_callback: "callable[[str], None] | None" = None,
) -> str:
    """Generate a digest for the given snapshot. Streams output to stream_callback if provided."""
    key = api_key or os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        raise ValueError(
            "ANTHROPIC_API_KEY not set. Set the environment variable or pass --api-key."
        )

    resolved_model = model or os.environ.get("GITDIGEST_MODEL") or _MODEL
    client = anthropic.Anthropic(api_key=key)
    prompt = _build_prompt(snap, focus)

    collected: list[str] = []

    with client.messages.stream(
        model=resolved_model,
        max_tokens=4096,
        thinking={"type": "adaptive"},
        system=_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_delta":
                if event.delta.type == "text_delta":
                    chunk = event.delta.text
                    collected.append(chunk)
                    if stream_callback:
                        stream_callback(chunk)

    return "".join(collected)
