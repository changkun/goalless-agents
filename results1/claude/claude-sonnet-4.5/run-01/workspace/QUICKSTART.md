# SmartCommit Quick Start

Get started with SmartCommit in 60 seconds!

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd smartcommit

# Make executable
chmod +x smartcommit.py

# Verify it works
python3 test_smartcommit.py
```

## Your First Smart Commit

### 1. Make some changes in a git repository

```bash
# Edit a file
echo "def hello(): return 'Hello, World!'" >> app.py

# Stage the changes
git add app.py
```

### 2. Generate a commit message

```bash
# Run SmartCommit
./smartcommit.py
```

**Output:**
```
🔍 Analyzing staged changes...
📊 Found 1 file(s) changed
   +1 -0 lines

🤖 Generating commit message...

============================================================
feat(app): add app implementation

- Modify app.py
- Add 1 lines
============================================================

ℹ️  Use --commit to commit with this message
   Use --interactive to edit before committing
```

### 3. Commit with the generated message

```bash
# Option 1: Automatically commit
./smartcommit.py --commit

# Option 2: Edit before committing
./smartcommit.py --interactive

# Option 3: Copy the message manually
./smartcommit.py  # Copy output and use: git commit -m "..."
```

## Try the Demo

Run the included demo to see SmartCommit in action:

```bash
./demo.sh
```

This creates a sample repository and demonstrates:
- Adding new features
- Fixing bugs
- Adding tests
- Updating documentation

## Common Usage Patterns

### Quick commit workflow

```bash
git add .
./smartcommit.py --commit
```

### Review before committing

```bash
git add .
./smartcommit.py --interactive
# Edit in your $EDITOR, save, and exit
```

### Preview what will be analyzed

```bash
git add .
./smartcommit.py --dry-run
```

## Understanding the Output

SmartCommit follows [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

- Detail 1
- Detail 2
```

**Types:**
- `feat` - New features
- `fix` - Bug fixes
- `docs` - Documentation changes
- `test` - Test additions/updates
- `refactor` - Code refactoring
- `perf` - Performance improvements
- `build` - Build system changes
- `ci` - CI/CD changes

**Scope:** The component/module being changed (auto-detected from file paths)

**Description:** A concise summary of what changed

## Tips for Best Results

1. **Stage related changes together**
   ```bash
   git add auth/*.py  # Group authentication changes
   ```

2. **Make focused commits**
   - One feature per commit
   - One bugfix per commit
   - SmartCommit works best with clear, single-purpose changes

3. **Review generated messages**
   - Always review before committing
   - Use `--interactive` to add context

4. **Use conventional commit types**
   - SmartCommit auto-detects, but you can guide it
   - Add keywords like "fix bug" or "add feature" in code comments

## Next Steps

- Read [README.md](README.md) for full documentation
- Check [EXAMPLES.md](EXAMPLES.md) for more examples
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Star the repo if you find it useful!

## Troubleshooting

**No staged changes found**
```bash
# Make sure you've staged files
git add <files>
git status  # Should show "Changes to be committed"
```

**Not a git repository**
```bash
# Initialize git first
git init
```

**Permission denied**
```bash
# Make the script executable
chmod +x smartcommit.py
```

## Questions?

Open an issue on GitHub or check the documentation!

Happy committing! 🚀
