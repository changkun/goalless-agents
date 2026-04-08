"""CLI entry point for gitdigest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .git import analyze
from .digest import generate


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="gitdigest",
        description="Generate an AI-powered digest of git repository changes using Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  gitdigest                          Digest last 20 commits in current repo
  gitdigest /path/to/repo            Digest a different repo
  gitdigest --since 2024-01-01       Changes since a date
  gitdigest --since "1 week ago"     Changes from the last week
  gitdigest --since "2 days ago" --max-commits 100
  gitdigest --focus "security"       Ask Claude to focus on security implications
  gitdigest --output digest.md       Save output to a file
  gitdigest --no-stream              Print full digest after generation (no streaming)

Requires ANTHROPIC_API_KEY environment variable.
""",
    )

    parser.add_argument(
        "repo",
        nargs="?",
        default=".",
        help="Path to the git repository (default: current directory)",
    )
    parser.add_argument(
        "--since",
        metavar="DATE",
        help="Show commits after this date/ref (e.g. '2024-01-01', '1 week ago', 'v1.2.3')",
    )
    parser.add_argument(
        "--until",
        metavar="DATE",
        help="Show commits before this date/ref (default: HEAD)",
    )
    parser.add_argument(
        "--max-commits",
        type=int,
        default=20,
        metavar="N",
        help="Maximum number of commits to analyze (default: 20)",
    )
    parser.add_argument(
        "--focus",
        metavar="TOPIC",
        help="Ask Claude to focus on a specific aspect (e.g. 'security', 'performance', 'API changes')",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Write digest to a file instead of stdout",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        help="Don't stream output; print everything at once when done",
    )
    parser.add_argument(
        "--no-patch",
        action="store_true",
        help="Skip the full diff patch (faster, cheaper, less detailed)",
    )
    parser.add_argument(
        "--api-key",
        metavar="KEY",
        help="Anthropic API key (default: ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--model",
        metavar="MODEL",
        help="Model to use (default: claude-opus-4-6, override with GITDIGEST_MODEL env var)",
    )

    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)

    # Resolve repo path
    repo = str(Path(args.repo).resolve())

    print(f"Analyzing {repo}...", file=sys.stderr)

    try:
        snap = analyze(
            repo_path=repo,
            since=args.since,
            until=args.until,
            max_commits=args.max_commits,
        )
    except (ValueError, RuntimeError) as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    if not snap.commits:
        print("No commits found in the specified range.", file=sys.stderr)
        return 0

    n = len(snap.commits)
    date_range = ""
    if snap.commits:
        first = snap.commits[-1].date
        last = snap.commits[0].date
        date_range = f" ({first})" if first == last else f" ({first} → {last})"

    print(f"Found {n} commit{'s' if n != 1 else ''}{date_range}.", file=sys.stderr)

    # Optionally strip the patch to save tokens
    if args.no_patch:
        snap = snap.__class__(
            repo_path=snap.repo_path,
            branch=snap.branch,
            commits=snap.commits,
            file_changes=snap.file_changes,
            diff_summary=snap.diff_summary,
            diff_patch="",
            patch_truncated=False,
        )

    print("Generating digest with Claude...\n", file=sys.stderr)

    output_file = None
    if args.output:
        output_file = open(args.output, "w", encoding="utf-8")  # noqa: WPS515

    try:
        if args.no_stream:
            digest = generate(
                snap,
                focus=args.focus,
                api_key=args.api_key,
                model=args.model,
            )
            dest = output_file or sys.stdout
            print(digest, file=dest)
        else:
            collected: list[str] = []

            def _print_chunk(chunk: str) -> None:
                collected.append(chunk)
                dest = output_file or sys.stdout
                dest.write(chunk)
                dest.flush()

            generate(
                snap,
                focus=args.focus,
                api_key=args.api_key,
                model=args.model,
                stream_callback=_print_chunk,
            )
            if output_file is None:
                print()  # trailing newline

        if output_file:
            output_file.close()
            print(f"\nDigest written to: {args.output}", file=sys.stderr)

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        if output_file:
            output_file.close()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
