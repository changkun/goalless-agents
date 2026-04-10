# Claude Code Reviewer

An AI-powered code review assistant that uses Claude API to provide intelligent, constructive feedback on your code.

## Features

- **Multi-language support**: JavaScript, TypeScript, Python, Java, C++, Go, Ruby, PHP, Rust, and more
- **Comprehensive reviews**: Analyzes code quality, readability, potential bugs, performance, and security
- **Simple CLI**: Easy-to-use command-line interface
- **Fast feedback**: Get detailed code reviews in seconds

## Installation

```bash
npm install
```

## Usage

```bash
node src/cli.js <file-path>
```

### Examples

```bash
# Review a JavaScript file
node src/cli.js examples/buggy.js

# Review a Python file
node src/cli.js app.py

# Review a Go file
node src/cli.js main.go
```

## Setup

1. Get your [Anthropic API key](https://console.anthropic.com/)
2. Set the environment variable:

```bash
export ANTHROPIC_API_KEY=your-api-key-here
```

## How It Works

1. The CLI reads your code file
2. Sends it to Claude API for analysis
3. Claude provides detailed, constructive feedback
4. Results are displayed in your terminal

## Supported Languages

- JavaScript/TypeScript
- Python
- Java
- C/C++
- Go
- Ruby
- PHP
- Rust
- Swift
- Kotlin
- C#

## Example Output

```
============================================================
CODE REVIEW
============================================================

Your code has several areas for improvement:

1. **Performance Issue**: The `fib()` function uses naive recursion which 
   causes exponential time complexity O(2^n). For n=40, this would require 
   millions of function calls.

2. **Global State**: The `cache` object is global and could lead to side 
   effects and testing difficulties. Consider using a closure or class.

3. **Missing Error Handling**: The `fetchUser()` function doesn't handle 
   network errors or invalid responses.

4. **Null Safety**: The `getUsername()` function doesn't check if `user`, 
   `profile`, or `name` exist, risking runtime errors.

5. **Modern JavaScript**: The code uses `var` style loops. Use `filter()` 
   instead of manual loops for better readability.
```

## License

MIT
