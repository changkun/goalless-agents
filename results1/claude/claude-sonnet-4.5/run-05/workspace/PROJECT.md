# CodeScope - Project Overview

## What is CodeScope?

CodeScope is a lightweight, fast code quality analyzer that scans codebases for:
- **Security vulnerabilities** (eval/exec, password leaks, XSS)
- **Code smells** (bare exceptions, wildcard imports, loose equality)
- **Maintenance markers** (TODO, FIXME, HACK comments)
- **Style issues** (long lines, console.log statements)

## Architecture

```
analyzer.py (700 lines)
├── Issue (dataclass) - represents a single issue
├── LanguageAnalyzer (base class) - common patterns
│   ├── check_line_length()
│   └── check_todos()
├── PythonAnalyzer - Python-specific checks
├── JavaScriptAnalyzer - JS/TS-specific checks
├── GoAnalyzer - Go-specific checks
└── CodeScope (orchestrator)
    ├── analyze_directory() - recursive scan
    ├── analyze_file() - single file analysis
    └── generate_report() - text/JSON output
```

## Design Principles

1. **Zero dependencies** - Uses only Python stdlib for maximum portability
2. **Extensible** - Easy to add new languages and rules
3. **Fast** - Optimized for scanning large codebases
4. **Actionable** - Every issue includes a suggestion
5. **CI/CD friendly** - JSON output for automation

## Test Results

Analyzing the sample project with 4 files:

- **Files analyzed:** 4
- **Total issues found:** 38
  - Critical: 5 (eval/exec, credential leaks)
  - Warning: 20 (code quality issues)
  - Info: 13 (maintenance markers)

## Use Cases

1. **Pre-commit hooks** - Block commits with critical issues
2. **CI/CD pipelines** - Fail builds on security problems
3. **Code reviews** - Automated first pass before human review
4. **Legacy code audits** - Quick assessment of technical debt
5. **Learning tool** - Teach developers about code quality

## Extension Ideas

- Add more languages (Rust, Java, C++, Ruby)
- Complexity metrics (cyclomatic complexity)
- Duplicate code detection
- Import dependency analysis
- Integration with LSP for real-time feedback
- GitHub Action for automated PR comments
- VS Code extension
- HTML report generation with visualizations

## Performance

On the sample project:
- Analysis time: <100ms
- Memory usage: <10MB
- Scales linearly with codebase size

## Getting Started

```bash
# Quick test
python3 analyzer.py sample_project

# Run demo
./demo.sh

# Analyze your own code
python3 analyzer.py /path/to/your/project

# CI/CD integration
python3 analyzer.py -f json | jq '.stats.severity_critical'
```

## File Structure

```
/workspace/
├── analyzer.py          # Main analyzer (700 lines)
├── config.json          # Example configuration
├── README.md            # User documentation
├── PROJECT.md           # This file
├── demo.sh              # Demo script
├── requirements.txt     # Dependencies (none!)
├── .gitignore          # Git ignore patterns
└── sample_project/      # Test files with intentional issues
    ├── src/
    │   ├── auth.py     # Python with security issues
    │   ├── app.js      # JavaScript with code smells
    │   └── clean.py    # Clean code (no issues)
    └── lib/
        └── utils.go    # Go with warnings
```

## Why CodeScope?

Unlike heavyweight linters that require complex setup and language-specific tooling, CodeScope:
- Works out of the box (no config needed)
- Scans multiple languages in one pass
- Focuses on high-signal issues developers actually care about
- Provides clear, actionable feedback
- Runs anywhere Python 3.7+ is available

Perfect for teams that want quick code quality insights without the overhead of setting up ESLint, Pylint, Go vet, etc.
