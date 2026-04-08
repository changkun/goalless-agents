package main

import (
	"fmt"
	"io"
	"os"

	"github.com/yuin/goldmark"
	"github.com/yuin/goldmark/extension"
	"github.com/yuin/goldmark/parser"
	"github.com/yuin/goldmark/text"
)

const version = "0.1.0"

const usage = `mdcat-lite v%s — render Markdown beautifully in your terminal

Usage:
  mdcat-lite <file.md>       Render a Markdown file
  mdcat-lite                  Read from stdin (pipe or redirect)
  cat README.md | mdcat-lite  Pipe Markdown into mdcat-lite

Options:
  -h, --help       Show this help
  -v, --version    Show version
`

func main() {
	if len(os.Args) > 1 {
		switch os.Args[1] {
		case "-h", "--help":
			fmt.Printf(usage, version)
			return
		case "-v", "--version":
			fmt.Printf("mdcat-lite v%s\n", version)
			return
		}
	}

	source, err := readInput()
	if err != nil {
		fmt.Fprintf(os.Stderr, "error: %v\n", err)
		os.Exit(1)
	}

	if len(source) == 0 {
		fmt.Printf(usage, version)
		return
	}

	md := goldmark.New(
		goldmark.WithExtensions(
			extension.GFM,
			extension.Strikethrough,
		),
		goldmark.WithParserOptions(
			parser.WithAutoHeadingID(),
		),
	)

	reader := text.NewReader(source)
	doc := md.Parser().Parse(reader)

	renderer := NewRenderer(os.Stdout, source)
	renderer.Render(doc)
}

func readInput() ([]byte, error) {
	if len(os.Args) > 1 && os.Args[1] != "-" {
		return os.ReadFile(os.Args[1])
	}

	// Check if stdin has data
	stat, err := os.Stdin.Stat()
	if err != nil {
		return nil, err
	}
	if (stat.Mode() & os.ModeCharDevice) != 0 {
		// Interactive terminal with no file arg — no input
		return nil, nil
	}

	return io.ReadAll(os.Stdin)
}
