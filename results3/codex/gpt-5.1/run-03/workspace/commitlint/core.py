from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, List


ALLOWED_TYPES = (
    "feat",
    "fix",
    "docs",
    "style",
    "refactor",
    "perf",
    "test",
    "chore",
    "build",
    "ci",
)

FIRST_LINE_RE = re.compile(
    r"""
    ^
    (?P<type>[a-z]+)                # type
    (?:\((?P<scope>[a-zA-Z0-9_-]+)\))?  # optional scope
    :\s
    (?P<description>.+)             # description
    $
    """,
    re.VERBOSE,
)


@dataclass
class LintError:
    message: str


def lint_message(message: str) -> List[LintError]:
    """Validate a commit message and return a list of lint errors."""
    errors: List[LintError] = []

    if not message.strip():
        return [LintError("Commit message must not be empty.")]

    first_line = message.splitlines()[0].rstrip("\n")

    match = FIRST_LINE_RE.match(first_line)
    if not match:
        errors.append(
            LintError(
                "First line must match '<type>(<scope>)?: <description>' with lowercase type."
            )
        )
        return errors

    type_ = match.group("type")
    scope = match.group("scope")
    description = match.group("description")

    if type_ not in ALLOWED_TYPES:
        errors.append(
            LintError(
                f"Type '{type_}' is not allowed. Allowed types: {', '.join(ALLOWED_TYPES)}."
            )
        )

    if scope is not None and not scope.strip():
        errors.append(LintError("Scope, when present, must not be empty."))

    if not description.strip():
        errors.append(LintError("Description must not be empty."))
    else:
        if description[0].isupper():
            errors.append(
                LintError("Description should start with a lowercase letter or digit.")
            )
        if description.endswith("."):
            errors.append(LintError("Description should not end with a period."))

    return errors


def format_errors(errors: Iterable[LintError]) -> str:
    return "\n".join(f"- {e.message}" for e in errors)

