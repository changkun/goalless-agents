# CodePulse - Usage Examples

## Basic Usage

### Analyze current directory
```bash
python3 codepulse.py
```

### Analyze specific project
```bash
python3 codepulse.py ~/projects/myapp
python3 codepulse.py /path/to/repository
```

### Analyze single file
```bash
python3 codepulse.py script.py
python3 codepulse.py src/main.js
```

## Advanced Usage

### Detailed report with language breakdown
```bash
python3 codepulse.py --detailed
python3 codepulse.py ~/projects/myapp -d
```

### Exclude additional patterns
```bash
# Exclude cache and temp directories
python3 codepulse.py --exclude cache temp logs

# Multiple exclusions
python3 codepulse.py -e build dist coverage .pytest_cache
```

### Combine options
```bash
python3 codepulse.py ~/projects/myapp --detailed --exclude node_modules dist
```

## Common Workflows

### Pre-commit analysis
```bash
# Add to .git/hooks/pre-commit
python3 codepulse.py src/ --detailed
```

### CI/CD integration
```bash
# Generate report in CI pipeline
python3 codepulse.py . > code-report.txt

# Check complexity threshold
python3 codepulse.py . | grep "Average Complexity"
```

### Compare projects
```bash
# Analyze multiple projects
for proj in ~/projects/*; do
  echo "=== $proj ==="
  python3 codepulse.py "$proj"
done
```

### Monitor refactoring progress
```bash
# Before refactoring
python3 codepulse.py src/ > before.txt

# After refactoring
python3 codepulse.py src/ > after.txt

# Compare
diff before.txt after.txt
```

## Use Case Examples

### 1. Code Review Aid
```bash
# Analyze PR changes
git diff --name-only main | xargs python3 codepulse.py
```

### 2. Find Complex Code
```bash
# Get detailed report to see most complex files
python3 codepulse.py --detailed | grep "Most Complex"
```

### 3. Language Migration Tracking
```bash
# Monitor TypeScript adoption in JS project
python3 codepulse.py --detailed | grep -A3 "Languages:"
```

### 4. Documentation Coverage
```bash
# Check comment ratio per language
python3 codepulse.py --detailed | grep "Comment Ratio"
```

### 5. Onboarding New Developers
```bash
# Give overview of codebase structure
python3 codepulse.py . --detailed > CODEBASE_OVERVIEW.txt
```

## Tips & Tricks

### Create an alias
```bash
# Add to ~/.bashrc or ~/.zshrc
alias pulse='python3 /workspace/codepulse.py'

# Then use:
pulse .
pulse --detailed
```

### Use with watch for live updates
```bash
# Auto-refresh analysis every 5 seconds
watch -n 5 python3 codepulse.py src/
```

### Filter output with grep
```bash
# Show only Python files
python3 codepulse.py --detailed | grep -A4 "Python:"

# Check specific complexity
python3 codepulse.py . | grep "main.py"
```

### Pipe to less for scrolling
```bash
python3 codepulse.py large-project/ --detailed | less
```

## Integration Examples

### Make script
```makefile
.PHONY: analyze
analyze:
	python3 codepulse.py src/ --detailed

.PHONY: check-complexity
check-complexity:
	python3 codepulse.py src/ | grep "Average Complexity: [0-9]"
```

### npm script (package.json)
```json
{
  "scripts": {
    "analyze": "python3 codepulse.py src/",
    "analyze:detailed": "python3 codepulse.py src/ --detailed"
  }
}
```

### GitHub Actions
```yaml
- name: Code Analysis
  run: |
    python3 codepulse.py . --detailed
    python3 codepulse.py . > analysis.txt
- name: Upload Report
  uses: actions/upload-artifact@v2
  with:
    name: code-analysis
    path: analysis.txt
```

## Output Interpretation

### Complexity Levels
- **1-10**: Simple, maintainable code
- **11-20**: Moderate complexity (acceptable)
- **21-50**: High complexity (consider refactoring)
- **50+**: Very high (immediate attention needed)

### Healthy Ratios
- **Code Lines**: 60-80% (good balance)
- **Comment Lines**: 10-30% (well documented)
- **Blank Lines**: 10-20% (readable structure)

### When to Refactor
- Average complexity > 20
- Individual files > 50 complexity
- Comment ratio < 5% (undocumented)
- Single files > 1000 lines
