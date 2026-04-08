# CodePulse

A fast, language-agnostic code analysis tool that provides insights into your codebase's complexity, composition, and health metrics.

## Features

- **Multi-Language Support**: Analyzes Python, JavaScript, TypeScript, Go, Rust, C/C++, Java, Ruby, PHP, and more
- **Complexity Analysis**: Calculates cyclomatic complexity to identify complex code
- **Language Breakdown**: Shows code distribution across different languages
- **Comment Ratio**: Tracks documentation levels in your codebase
- **Visual Reports**: Clean, terminal-based reports with progress bars
- **Smart Exclusions**: Automatically skips common build/dependency directories

## Quick Start

```bash
# Analyze current directory
python3 codepulse.py

# Analyze specific directory
python3 codepulse.py /path/to/project

# Detailed analysis
python3 codepulse.py --detailed

# Exclude additional patterns
python3 codepulse.py --exclude cache temp logs
```

## Installation

```bash
# Make executable
chmod +x codepulse.py

# Optional: Create alias
alias codepulse='python3 /workspace/codepulse.py'
```

## Example Output

```
============================================================
  CODE PULSE - Code Analysis Report
============================================================

📊 Overview:
  Total Files:    142
  Total Lines:    15,234
  Code Lines:     11,892 (78.1%)
  Comment Lines:  1,823 (12.0%)
  Blank Lines:    1,519 (9.9%)

🔤 Languages:
  Python          45 files   8,234 lines  ████████████████░░░░
  JavaScript      38 files   4,512 lines  ██████░░░░░░░░░░░░░░
  TypeScript      22 files   1,892 lines  ███░░░░░░░░░░░░░░░░░
  CSS             12 files     456 lines  █░░░░░░░░░░░░░░░░░░░
  Markdown         8 files     140 lines  ░░░░░░░░░░░░░░░░░░░░

⚡ Complexity Analysis:
  Average Complexity: 12.4

  Most Complex Files:
     45 - src/parser/advanced.py
     38 - src/analyzer/core.py
     32 - utils/processor.py
     28 - src/main.py
     24 - tests/integration.py
============================================================
```

## Metrics Explained

### Cyclomatic Complexity
Approximates code complexity by counting control flow statements (if, for, while, etc.). Higher values indicate more complex code that may be harder to test and maintain.

- **1-10**: Simple, low risk
- **11-20**: Moderate complexity
- **21-50**: High complexity, consider refactoring
- **50+**: Very high, definitely refactor

### Comment Ratio
Percentage of comment lines vs total lines. Healthy ratios vary by language and team, but generally:
- **< 10%**: Potentially under-documented
- **10-30%**: Good balance
- **> 30%**: Possibly over-commented (or generated code)

## Use Cases

- **Code Reviews**: Quickly assess PR complexity and scope
- **Technical Debt**: Identify files that need refactoring
- **Project Health**: Track code quality metrics over time
- **Language Migration**: See language distribution during migrations
- **Onboarding**: Help new developers understand codebase composition

## Roadmap

- [ ] Export reports to JSON/CSV
- [ ] Historical tracking and trends
- [ ] Custom complexity rules per language
- [ ] Integration with git to analyze changes
- [ ] Function-level complexity analysis
- [ ] Duplicate code detection
- [ ] Dependency graph generation

## License

MIT - Use freely, modify as needed

## Contributing

This is a single-file tool designed for simplicity. Feel free to fork and extend!
