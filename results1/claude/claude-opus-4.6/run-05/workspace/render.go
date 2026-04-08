package main

import (
	"bytes"
	"fmt"
	"io"
	"strings"

	"github.com/alecthomas/chroma/v2"
	"github.com/alecthomas/chroma/v2/formatters"
	"github.com/alecthomas/chroma/v2/lexers"
	"github.com/alecthomas/chroma/v2/styles"
	"github.com/yuin/goldmark/ast"
	east "github.com/yuin/goldmark/extension/ast"
)

const (
	reset     = "\033[0m"
	bold      = "\033[1m"
	dim       = "\033[2m"
	italic    = "\033[3m"
	underline = "\033[4m"
	strike    = "\033[9m"

	red     = "\033[31m"
	green   = "\033[32m"
	yellow  = "\033[33m"
	blue    = "\033[34m"
	magenta = "\033[35m"
	cyan    = "\033[36m"
	white   = "\033[37m"

	bgGray = "\033[48;5;236m"
)

var headingColors = []string{magenta, blue, cyan, green, yellow, red}

type listState struct {
	ordered bool
	index   int
}

type Renderer struct {
	w              io.Writer
	source         []byte
	listDepth      int
	listStack      []listState
	blockquoteDepth int
}

func NewRenderer(w io.Writer, source []byte) *Renderer {
	return &Renderer{w: w, source: source}
}

func (r *Renderer) Render(node ast.Node) {
	r.walk(node)
}

func (r *Renderer) walk(node ast.Node) {
	r.enter(node)
	for child := node.FirstChild(); child != nil; child = child.NextSibling() {
		r.walk(child)
	}
	r.leave(node)
}

func (r *Renderer) bqPrefix() string {
	if r.blockquoteDepth <= 0 {
		return ""
	}
	return green + strings.Repeat("  | ", r.blockquoteDepth) + reset
}

func (r *Renderer) enter(node ast.Node) {
	switch n := node.(type) {
	case *ast.Heading:
		level := n.Level
		if level < 1 {
			level = 1
		}
		if level > 6 {
			level = 6
		}
		color := headingColors[level-1]
		prefix := strings.Repeat("#", level)
		fmt.Fprintf(r.w, "\n%s%s%s%s ", r.bqPrefix(), bold, color, prefix)

	case *ast.Blockquote:
		r.blockquoteDepth++

	case *ast.FencedCodeBlock:
		lang := string(n.Language(r.source))
		code := r.codeBlockContent(n)
		highlighted := highlightCode(code, lang)
		lines := strings.Split(highlighted, "\n")
		fmt.Fprintln(r.w)
		bq := r.bqPrefix()
		for _, line := range lines {
			fmt.Fprintf(r.w, "%s  %s%s%s\n", bq, bgGray, line, reset)
		}

	case *ast.CodeBlock:
		code := r.codeBlockContent(n)
		lines := strings.Split(code, "\n")
		fmt.Fprintln(r.w)
		bq := r.bqPrefix()
		for _, line := range lines {
			fmt.Fprintf(r.w, "%s  %s%s%s\n", bq, bgGray, line, reset)
		}

	case *ast.List:
		r.listDepth++
		st := listState{ordered: n.IsOrdered(), index: int(n.Start)}
		r.listStack = append(r.listStack, st)
		if r.listDepth == 1 {
			fmt.Fprintln(r.w)
		}

	case *ast.ListItem:
		st := &r.listStack[len(r.listStack)-1]
		pad := r.bqPrefix() + strings.Repeat("  ", r.listDepth-1)
		if st.ordered {
			fmt.Fprintf(r.w, "%s%s%d.%s ", pad, yellow, st.index, reset)
			st.index++
		} else {
			fmt.Fprintf(r.w, "%s%s%s%s ", pad, yellow, bulletChar(r.listDepth), reset)
		}

	case *ast.ThematicBreak:
		fmt.Fprintf(r.w, "\n%s%s%s%s\n", r.bqPrefix(), dim, strings.Repeat("─", 60), reset)

	case *ast.CodeSpan:
		fmt.Fprintf(r.w, "%s%s", bgGray, cyan)

	case *ast.Emphasis:
		if n.Level == 2 {
			fmt.Fprint(r.w, bold)
		} else {
			fmt.Fprint(r.w, italic)
		}

	case *east.Strikethrough:
		fmt.Fprint(r.w, strike+dim)

	case *ast.AutoLink:
		url := string(n.URL(r.source))
		fmt.Fprintf(r.w, "%s%s%s", underline+blue, url, reset)

	case *ast.Image:
		alt := string(n.Text(r.source))
		dest := string(n.Destination)
		fmt.Fprintf(r.w, "%s[image: %s]%s (%s)", dim, alt, reset, dest)

	case *ast.Text:
		text := n.Segment.Value(r.source)
		r.w.Write(text)
		if n.HardLineBreak() || n.SoftLineBreak() {
			fmt.Fprintln(r.w)
		}

	case *ast.String:
		r.w.Write(n.Value)

	case *ast.HTMLBlock:
		for i := 0; i < n.Lines().Len(); i++ {
			seg := n.Lines().At(i)
			fmt.Fprintf(r.w, "%s%s%s", dim, seg.Value(r.source), reset)
		}

	case *ast.RawHTML:
		for i := 0; i < n.Segments.Len(); i++ {
			seg := n.Segments.At(i)
			fmt.Fprintf(r.w, "%s%s%s", dim, seg.Value(r.source), reset)
		}

	case *east.Table:
		fmt.Fprintln(r.w)

	case *east.TableCell:
		if n.Parent().Kind() == east.KindTableHeader {
			fmt.Fprintf(r.w, "%s", bold+underline)
		}
	}
}

func (r *Renderer) leave(node ast.Node) {
	switch n := node.(type) {
	case *ast.Heading:
		fmt.Fprintf(r.w, "%s\n", reset)

	case *ast.Paragraph:
		parent := n.Parent()
		if parent != nil && parent.Kind() == ast.KindListItem {
			// no extra newline — ListItem leave handles it
		} else if parent != nil && parent.Kind() == ast.KindBlockquote {
			fmt.Fprintln(r.w)
		} else {
			fmt.Fprintf(r.w, "\n\n")
		}

	case *ast.Blockquote:
		r.blockquoteDepth--

	case *ast.ListItem:
		fmt.Fprintln(r.w)

	case *ast.List:
		r.listDepth--
		r.listStack = r.listStack[:len(r.listStack)-1]
		if r.listDepth == 0 {
			fmt.Fprintln(r.w)
		}

	case *ast.CodeSpan:
		fmt.Fprint(r.w, reset)

	case *ast.Emphasis:
		fmt.Fprint(r.w, reset)

	case *east.Strikethrough:
		fmt.Fprint(r.w, reset)

	case *ast.Link:
		dest := string(n.Destination)
		fmt.Fprintf(r.w, " %s(%s%s%s)%s", dim, underline+blue, dest, reset+dim, reset)

	case *east.TableCell:
		if n.Parent().Kind() == east.KindTableHeader {
			fmt.Fprintf(r.w, "%s\t", reset)
		} else {
			fmt.Fprint(r.w, "\t")
		}

	case *east.TableHeader:
		fmt.Fprintln(r.w)
		fmt.Fprintf(r.w, "%s%s%s\n", dim, strings.Repeat("─", 60), reset)

	case *east.TableRow:
		fmt.Fprintln(r.w)
	}
}

func (r *Renderer) codeBlockContent(node ast.Node) string {
	var buf bytes.Buffer
	lines := node.Lines()
	for i := 0; i < lines.Len(); i++ {
		seg := lines.At(i)
		buf.Write(seg.Value(r.source))
	}
	return strings.TrimRight(buf.String(), "\n")
}

func bulletChar(depth int) string {
	chars := []string{"*", "◦", "▸", "▹"}
	return chars[(depth-1)%len(chars)]
}

func highlightCode(code, lang string) string {
	lexer := lexers.Get(lang)
	if lexer == nil {
		lexer = lexers.Fallback
	}
	lexer = chroma.Coalesce(lexer)

	style := styles.Get("monokai")
	formatter := formatters.Get("terminal256")

	iterator, err := lexer.Tokenise(nil, code)
	if err != nil {
		return code
	}

	var buf bytes.Buffer
	if err := formatter.Format(&buf, style, iterator); err != nil {
		return code
	}
	return buf.String()
}
