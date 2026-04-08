# mdcat-lite Demo

Welcome to **mdcat-lite**, a terminal Markdown renderer with *syntax highlighting*.

## Features

- Styled **headings** (h1-h6) with colors
- **Bold**, *italic*, and `inline code`
- Fenced code blocks with syntax highlighting
- Ordered and unordered lists
- [Hyperlinks](https://example.com)
- Horizontal rules
- Blockquotes
- GFM tables and ~~strikethrough~~

## Code Example

```go
package main

import "fmt"

func main() {
    names := []string{"Alice", "Bob", "Charlie"}
    for i, name := range names {
        fmt.Printf("%d: Hello, %s!\n", i+1, name)
    }
}
```

```python
def fibonacci(n: int) -> list[int]:
    """Generate the first n Fibonacci numbers."""
    fib = [0, 1]
    for _ in range(2, n):
        fib.append(fib[-1] + fib[-2])
    return fib[:n]

print(fibonacci(10))
```

### Ordered List

1. Parse Markdown with goldmark
2. Walk the AST tree
3. Emit ANSI escape sequences
4. Profit!

### A Table

| Language | Use Case        | Speed   |
|----------|-----------------|---------|
| Go       | CLI tools       | Fast    |
| Python   | Data science    | Medium  |
| Rust     | Systems         | Fastest |

---

> "Simplicity is the ultimate sophistication."
> — Leonardo da Vinci

#### Nested Lists

- Top level
  - Second level
    - Third level
  - Back to second

That's it! Run `mdcat-lite README.md` to render any Markdown file.
