# commitlint-lite

A tiny, dependency-free CLI tool to lint commit messages against a small subset of the Conventional Commits spec.

## Installation

From this directory:

```bash
python -m pip install .
```

## Usage

Lint a commit message passed as an argument:

```bash
commitlint-lite "feat(parser): add new option"
```

Or read from stdin (e.g. for use as a Git hook):

```bash
echo "fix: correct typo" | commitlint-lite
```

Exit codes:

- `0` when the commit message is valid
- `1` when the commit message is invalid
- `2` on unexpected internal errors

## Rules enforced

- Format: `<type>(<scope>)?: <description>`
- Allowed `type` values: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `chore`, `build`, `ci`
- Optional `scope` must be a non-empty, alphanumeric/`-`/`_` string
- Description must:
  - be non-empty
  - start with a lowercase letter or digit
  - not end with a period

