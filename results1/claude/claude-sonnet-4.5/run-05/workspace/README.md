# CodeScope

A fast, extensible code quality analyzer that detects code smells, security issues, and provides actionable suggestions.

## Features

- **Multi-language support**: Python, JavaScript/TypeScript, Go
- **Security checks**: Detects dangerous patterns like `eval()`, password leaks
- **Code quality**: Finds code smells, style issues, maintenance markers
- **Fast scanning**: Efficiently analyzes entire codebases
- **Flexible output**: Text reports or JSON for CI/CD integration
- **Configurable**: Customize rules and ignored paths

## Quick Start

```bash
# Analyze current directory
python analyzer.py

# Analyze specific directory
python analyzer.py /path/to/project

# Use custom config
python analyzer.py -c config.json

# Generate JSON report
python analyzer.py -f json -o report.json

# Analyze single file
python analyzer.py src/app.py
```

## What It Detects

### Python
- Bare except clauses
- Dangerous `eval()` and `exec()` usage
- Wildcard imports
- Password/token leaks in prints
- Linter suppressions

### JavaScript/TypeScript
- Legacy `var` declarations
- Loose equality (`==` instead of `===`)
- Console.log statements
- XSS vulnerabilities (innerHTML)
- Dangerous eval usage

### Go
- Panic usage (should return error)
- Linter suppressions
- Unformatted prints

### Universal
- TODO/FIXME/HACK comments
- Long lines (>120 chars)
- Code maintenance markers

## Configuration

Create a `config.json`:

```json
{
  "ignore": [
    "*.min.js",
    "coverage",
    "*.test.js"
  ],
  "max_line_length": 120
}
```

## Output Example

```
================================================================================
CodeScope Analysis Report
================================================================================

Files analyzed: 12
Total issues: 8

By severity:
  Critical: 1
  Warning: 4
  Info: 3

By category:
  code-quality: 5
  security: 1
  maintenance: 2

================================================================================
Issues
================================================================================

src/auth.py
-----------
  🔴 Line 45: Dangerous eval() usage
     → Use safer alternatives
  🟡 Line 78: Bare except clause
     → Specify exception type

src/app.js
----------
  🟡 Line 23: Use === for strict equality
     → Replace == with ===
  🔵 Line 156: Console log statement
     → Remove before production
```

## Integration

### CI/CD Pipeline

```yaml
# GitHub Actions example
- name: Run CodeScope
  run: |
    python analyzer.py -f json -o report.json
    python -c "import json; exit(1 if json.load(open('report.json'))['stats'].get('severity_critical', 0) > 0 else 0)"
```

### Pre-commit Hook

```bash
#!/bin/bash
python analyzer.py --format json | python -c "
import sys, json
data = json.load(sys.stdin)
if data['stats'].get('severity_critical', 0) > 0:
    print('Critical issues found!')
    sys.exit(1)
"
```

## Extending

Add new analyzers by subclassing `LanguageAnalyzer`:

```python
class RustAnalyzer(LanguageAnalyzer):
    def analyze_file(self, filepath: Path, content: str):
        self.check_line_length(filepath, content)
        # Add Rust-specific checks
```

Register in `CodeScope.ANALYZERS`:

```python
ANALYZERS = {
    '.rs': RustAnalyzer,
    # ...
}
```

## License

MIT
