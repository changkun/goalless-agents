#!/usr/bin/env python3
"""
commitcraft — Generate conventional commit messages from staged git diffs using Claude.

Usage:
    python commitcraft.py                  # Generate and print commit message
    python commitcraft.py --commit         # Generate and run git commit
    python commitcraft.py --verbose        # Show Claude's thinking
    python commitcraft.py --amend         # Amend last commit instead
    python commitcraft.py --body          # Include detailed body in commit message
"""

import argparse
import subprocess
import sys
import os
import anthropic


SYSTEM_PROMPT = """You are an expert software engineer who writes excellent git commit messages.
Your job is to analyze a git diff and produce a precise, informative commit message following the
Conventional Commits specification (https://www.conventionalcommits.org/).

Rules:
- Format: <type>(<optional scope>): <short description>
- Types: feat, fix, docs, style, refactor, perf, test, build, ci, chore, revert
- Subject line: imperative mood, no period, max 72 chars
- If asked for a body: add a blank line after subject, then wrap lines at 72 chars
- Focus on WHAT changed and WHY, not HOW
- Be specific — reference file names or function names when useful
- Never add generic fluff like "This commit..." or "Updated code to..."

Output ONLY the commit message — no preamble, no explanation, no markdown fences."""


def get_staged_diff() -> str:
    """Get the staged git diff."""
    result = subprocess.run(
        ["git", "diff", "--staged", "--stat", "--patch"],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"Error: {result.stderr.strip()}", file=sys.stderr)
        sys.exit(1)
    return result.stdout.strip()


def get_repo_context() -> str:
    """Get brief repo context: recent commits and branch name."""
    parts = []

    # Branch name
    branch = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"],
        capture_output=True, text=True,
    )
    if branch.returncode == 0:
        parts.append(f"Current branch: {branch.stdout.strip()}")

    # Last 5 commit subjects (for style reference)
    log = subprocess.run(
        ["git", "log", "--oneline", "-5"],
        capture_output=True, text=True,
    )
    if log.returncode == 0 and log.stdout.strip():
        parts.append(f"Recent commits:\n{log.stdout.strip()}")

    return "\n\n".join(parts)


def generate_commit_message(diff: str, include_body: bool, verbose: bool) -> str:
    """Stream a commit message from Claude."""
    client = anthropic.Anthropic()

    context = get_repo_context()
    body_instruction = " Include a blank line followed by a detailed body explaining the motivation and changes." if include_body else ""

    user_message = f"""Analyze this staged git diff and write a conventional commit message.{body_instruction}

{context}

--- DIFF ---
{diff}
"""

    if verbose:
        print("\n\033[2m[Claude is thinking...]\033[0m", file=sys.stderr)

    message_parts = []
    thinking_shown = False

    with client.messages.stream(
        model="claude-opus-4-6",
        max_tokens=1024,
        thinking={"type": "adaptive"},
        system=SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        for event in stream:
            if event.type == "content_block_start":
                if event.content_block.type == "thinking" and verbose:
                    print("\n\033[2m--- Thinking ---\033[0m", file=sys.stderr)
                    thinking_shown = True
                elif event.content_block.type == "text" and thinking_shown and verbose:
                    print("\033[2m--- End Thinking ---\033[0m\n", file=sys.stderr)
                    thinking_shown = False

            elif event.type == "content_block_delta":
                if event.delta.type == "thinking_delta" and verbose:
                    print(f"\033[2m{event.delta.thinking}\033[0m",
                          end="", flush=True, file=sys.stderr)
                elif event.delta.type == "text_delta":
                    message_parts.append(event.delta.text)
                    # Stream the commit message to stderr so stdout stays clean
                    if verbose:
                        print(event.delta.text, end="", flush=True, file=sys.stderr)

    return "".join(message_parts).strip()


def run_git_commit(message: str, amend: bool) -> None:
    """Run git commit with the generated message."""
    cmd = ["git", "commit", "-m", message]
    if amend:
        cmd.insert(2, "--amend")

    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def print_colored(text: str, color_code: str) -> str:
    """Wrap text in ANSI color if stdout is a tty."""
    if sys.stdout.isatty():
        return f"\033[{color_code}m{text}\033[0m"
    return text


def main():
    parser = argparse.ArgumentParser(
        description="Generate conventional commit messages from staged git diffs using Claude.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python commitcraft.py                  Print a suggested commit message
  python commitcraft.py --commit         Commit with the generated message
  python commitcraft.py --body           Include a detailed body paragraph
  python commitcraft.py --verbose        Show Claude's reasoning process
  python commitcraft.py --commit --amend Amend the last commit
        """,
    )
    parser.add_argument(
        "--commit", "-c",
        action="store_true",
        help="Run 'git commit' with the generated message",
    )
    parser.add_argument(
        "--amend", "-a",
        action="store_true",
        help="Pass --amend to git commit (requires --commit)",
    )
    parser.add_argument(
        "--body", "-b",
        action="store_true",
        help="Ask Claude to include a detailed body in the commit message",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show Claude's thinking process",
    )
    args = parser.parse_args()

    if args.amend and not args.commit:
        parser.error("--amend requires --commit")

    # Check for ANTHROPIC_API_KEY
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print(
            "Error: ANTHROPIC_API_KEY environment variable is not set.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Get staged diff
    diff = get_staged_diff()
    if not diff:
        print(
            "No staged changes found. Stage your changes with 'git add' first.",
            file=sys.stderr,
        )
        sys.exit(1)

    # Warn about large diffs
    diff_lines = diff.count("\n")
    if diff_lines > 2000:
        print(
            f"Warning: Large diff ({diff_lines} lines). Truncating to 2000 lines.",
            file=sys.stderr,
        )
        diff = "\n".join(diff.split("\n")[:2000]) + "\n[... diff truncated ...]"

    print(print_colored("Analyzing your diff with Claude...", "2"), file=sys.stderr)

    # Generate the commit message
    commit_message = generate_commit_message(diff, args.body, args.verbose)

    if not commit_message:
        print("Error: Claude returned an empty response.", file=sys.stderr)
        sys.exit(1)

    # Display the result
    separator = "─" * 60
    print(f"\n{print_colored(separator, '2')}", file=sys.stderr)
    print(print_colored("Suggested commit message:", "1;36"), file=sys.stderr)
    print(f"{print_colored(separator, '2')}\n", file=sys.stderr)

    # Print the actual commit message to stdout (clean, pipeable)
    print(commit_message)

    print(f"\n{print_colored(separator, '2')}", file=sys.stderr)

    # Optionally commit
    if args.commit:
        action = "Amending last commit" if args.amend else "Committing"
        print(f"\n{print_colored(action + '...', '1;33')}", file=sys.stderr)
        run_git_commit(commit_message, args.amend)
    else:
        print(
            print_colored(
                "Tip: Run with --commit to commit directly, or copy the message above.",
                "2",
            ),
            file=sys.stderr,
        )


if __name__ == "__main__":
    main()
