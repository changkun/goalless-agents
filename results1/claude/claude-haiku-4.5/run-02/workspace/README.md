# Code Analyzer

A fast, lightweight CLI tool for analyzing source code statistics. Perfect for understanding codebases, generating reports, and integrating with development workflows.

## Features

- **Multi-language support**: Analyzes Go, Rust, Python, JavaScript, TypeScript, Java, C/C++, Ruby, PHP, Shell, and more
- **Detailed statistics**: Tracks lines of code, comments, blank lines, functions, and imports
- **Smart filtering**: Automatically skips vendor directories, hidden folders, and binary files
- **Dual output formats**: Human-readable tables or machine-parseable JSON
- **Fast**: Single-pass analysis with minimal overhead

## Installation

Build from source:

```bash
go build -o code-analyzer
```

## Usage

Basic analysis with pretty output:

```bash
./code-analyzer <directory>
```

Example:
```bash
./code-analyzer /path/to/project
```

Output in JSON format:

```bash
./code-analyzer /path/to/project --json
```

## Example Output

### Table Format

```
📊 CODE ANALYSIS REPORT
════════════════════════════════════════════
Total Files:        15
Total Lines:        3,245
Code Lines:         2,812
Comment Lines:      187
────────────────────────────────────────────
Languages:
  Go                8 files
  Python            4 files
  Markdown          3 files
════════════════════════════════════════════

📁 TOP FILES BY LINES:
────────────────────────────────────────────
 487 lines | /path/to/project/main.go
 234 lines | /path/to/project/handler.go
 198 lines | /path/to/project/utils.go
```

### JSON Format

```json
{
  "files": 15,
  "total_lines": 3245,
  "total_code": 2812,
  "total_comments": 187,
  "languages": {
    "Go": 8,
    "Python": 4,
    "Markdown": 3
  },
  "files_stats": [...]
}
```

## Supported Languages

- Go (`.go`)
- Rust (`.rs`)
- Python (`.py`)
- JavaScript (`.js`)
- TypeScript (`.ts`)
- JSX (`.jsx`)
- TSX (`.tsx`)
- Java (`.java`)
- C/C++ (`.c`, `.cpp`, `.h`)
- Ruby (`.rb`)
- PHP (`.php`)
- Shell (`.sh`)
- YAML (`.yaml`, `.yml`)
- JSON (`.json`)
- Markdown (`.md`)
- Common files: `Makefile`, `Dockerfile`, `.gitignore`

## What Gets Analyzed

The tool:
- ✅ Counts code lines (excluding comments and blanks)
- ✅ Identifies function/method definitions
- ✅ Counts import statements
- ✅ Detects single-line and block comments
- ✅ Tracks blank lines

The tool automatically skips:
- Hidden directories (`.git`, `.vscode`, etc.)
- Dependency directories (`vendor/`, `node_modules/`, `__pycache__/`)
- Binary files
- Non-text files

## Use Cases

1. **Project Understanding**: Quickly understand the structure and size of unfamiliar codebases
2. **Team Reporting**: Generate statistics for sprint reviews or project planning
3. **CI/CD Integration**: Export JSON and process metrics programmatically
4. **Code Review**: Identify unexpectedly large or complex files
5. **Developer Tools**: Integrate with other development utilities

## License

MIT
