# mdcat-lite

A fast, zero-config terminal Markdown renderer written in Go. Renders Markdown files beautifully in your terminal with ANSI colors and syntax-highlighted code blocks.

## Features

- **Styled headings** — h1-h6 with distinct colors
- **Inline formatting** — bold, italic, strikethrough, inline code
- **Syntax-highlighted code blocks** — powered by Chroma (150+ languages)
- **Lists** — ordered, unordered, nested with distinct bullet styles
- **Links** — rendered with URL visible
- **Tables** — GFM table support with aligned headers
- **Blockquotes** — with green bar prefix
- **Horizontal rules** — clean separator lines
- **Stdin support** — pipe Markdown from other commands

## Install

```bash
go install github.com/mdcat-lite@latest
```

Or build from source:

```bash
git clone https://github.com/mdcat-lite
cd mdcat-lite
go build -o mdcat-lite .
```

## Usage

```bash
# Render a file
mdcat-lite README.md

# Pipe from stdin
cat notes.md | mdcat-lite
curl -s https://raw.githubusercontent.com/golang/go/master/README.md | mdcat-lite

# Help
mdcat-lite --help
```

## Dependencies

- [goldmark](https://github.com/yuin/goldmark) — Markdown parser (CommonMark + GFM)
- [chroma](https://github.com/alecthomas/chroma) — Syntax highlighting
