# SmartCommit

An AI-powered git commit message generator that analyzes your staged changes and creates meaningful, conventional commit messages.

## Features

- 🤖 AI-powered analysis of code changes
- 📝 Generates conventional commit messages (feat, fix, refactor, etc.)
- 🎯 Understands context from diffs
- ⚡ Fast and simple CLI interface
- 🔧 Configurable commit types and scopes

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
# Generate commit message for staged changes
python smartcommit.py

# Review and edit before committing
python smartcommit.py --interactive

# Direct commit with generated message
python smartcommit.py --commit

# Show what would be analyzed (dry run)
python smartcommit.py --dry-run
```

## How It Works

1. Analyzes `git diff --cached` to understand staged changes
2. Identifies the type of change (feature, fix, refactor, etc.)
3. Extracts key modifications and their impact
4. Generates a clear, conventional commit message
5. Optionally commits with the generated message

## Commit Message Format

Follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Examples

**Input**: Added user authentication with JWT tokens
```
feat(auth): implement JWT-based user authentication

- Add login and registration endpoints
- Create JWT token generation and validation
- Add authentication middleware
```

**Input**: Fixed memory leak in cache implementation
```
fix(cache): resolve memory leak in cleanup routine

Previously, cache entries were not properly released when expired.
Now properly clears references and triggers garbage collection.
```

## License

MIT
