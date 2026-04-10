# Quick Start Guide

## 1. Install Dependencies

```bash
npm install
```

## 2. Set Up Your API Key

Get your Anthropic API key from [console.anthropic.com](https://console.anthropic.com), then:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## 3. Review Your Code

```bash
node src/cli.js path/to/your/file.js
```

## Examples

Try reviewing the included examples:

```bash
# Review a buggy JavaScript file
node src/cli.js examples/buggy.js

# Review a Python database module
node src/cli.js examples/database.py
```

## What You'll Get

The reviewer analyzes your code for:

- **Bugs & Logic Issues**: Unguarded null pointers, error handling gaps, security issues
- **Performance**: Inefficient algorithms, memory leaks, unnecessary computations
- **Code Quality**: Readability, maintainability, design patterns
- **Best Practices**: Language idioms, modern features, industry standards
- **Security**: Input validation, injection risks, safe defaults

## Supported File Types

- JavaScript (.js)
- TypeScript (.ts)
- Python (.py)
- Java (.java)
- C/C++ (.c, .cpp)
- Go (.go)
- Ruby (.rb)
- PHP (.php)
- Rust (.rs)
- And many more!

## Tips

- The tool works best with complete, context-containing files
- For very large files (>2000 lines), consider reviewing sections separately
- Pair this with other tools like linters (ESLint, Pylint) for comprehensive analysis
