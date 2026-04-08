package main

import (
	"fmt"
	"strings"
)

// ANSI color codes
const (
	Reset     = "\033[0m"
	Bold      = "\033[1m"
	Dim       = "\033[2m"

	Red       = "\033[31m"
	Green     = "\033[32m"
	Yellow    = "\033[33m"
	Blue      = "\033[34m"
	Magenta   = "\033[35m"
	Cyan      = "\033[36m"
	White     = "\033[37m"

	BgRed     = "\033[41m"
	BgGreen   = "\033[42m"
	BgYellow  = "\033[43m"
	BgBlue    = "\033[44m"
)

func columnColor(col Column) string {
	switch col {
	case Todo:
		return Cyan
	case Doing:
		return Yellow
	case Done:
		return Green
	default:
		return White
	}
}

func columnHeader(col Column) string {
	labels := map[Column]string{
		Todo:  "📋 TODO",
		Doing: "🔨 DOING",
		Done:  "✅ DONE",
	}
	return labels[col]
}

func priorityIcon(p int) string {
	switch p {
	case 3:
		return Red + "▲" + Reset     // high
	case 2:
		return Yellow + "■" + Reset  // medium
	default:
		return Dim + "▽" + Reset     // low
	}
}

func renderCard(t Task, width int) []string {
	var lines []string

	// ID + priority
	idLine := fmt.Sprintf(" %s #%-4d", priorityIcon(t.Priority), t.ID)
	lines = append(lines, padRight(idLine, width))

	// Title — word-wrap to width-2
	titleLines := wordWrap(t.Title, width-2)
	for _, tl := range titleLines {
		lines = append(lines, " "+padRight(tl, width-1))
	}

	// Tags
	if len(t.Tags) > 0 {
		tagStr := Dim + " " + strings.Join(tagSlice(t.Tags), " ") + Reset
		lines = append(lines, padRight(tagStr, width))
	}

	return lines
}

func tagSlice(tags []string) []string {
	out := make([]string, len(tags))
	for i, t := range tags {
		out[i] = "#" + t
	}
	return out
}

// RenderBoard prints the kanban board to stdout
func RenderBoard(b *Board) {
	colWidth := 30
	separator := Dim + "│" + Reset

	// Header
	fmt.Println()
	fmt.Printf("  %s%s Board: %s%s\n\n", Bold, Magenta, b.Name, Reset)

	// Column headers
	var headerParts []string
	for _, col := range AllColumns {
		color := columnColor(col)
		label := columnHeader(col)
		padded := padRight(" "+label, colWidth)
		headerParts = append(headerParts, color+Bold+padded+Reset)
	}
	fmt.Println("  " + strings.Join(headerParts, " "+separator+" "))

	// Divider
	divParts := make([]string, len(AllColumns))
	for i := range divParts {
		divParts[i] = strings.Repeat("─", colWidth)
	}
	fmt.Println("  " + Dim + strings.Join(divParts, "─┼─") + Reset)

	// Build card lines per column
	colCards := make([][]string, len(AllColumns))
	maxLines := 0
	for i, col := range AllColumns {
		tasks := b.TasksByColumn(col)
		var lines []string
		for j, t := range tasks {
			card := renderCard(t, colWidth)
			lines = append(lines, card...)
			if j < len(tasks)-1 {
				lines = append(lines, strings.Repeat(" ", colWidth)) // gap between cards
			}
		}
		if len(tasks) == 0 {
			lines = append(lines, padRight(Dim+"  (empty)"+Reset, colWidth))
		}
		colCards[i] = lines
		if len(lines) > maxLines {
			maxLines = len(lines)
		}
	}

	// Render rows side by side
	for row := 0; row < maxLines; row++ {
		var parts []string
		for i := range AllColumns {
			if row < len(colCards[i]) {
				parts = append(parts, padRight(colCards[i][row], colWidth))
			} else {
				parts = append(parts, strings.Repeat(" ", colWidth))
			}
		}
		fmt.Println("  " + strings.Join(parts, " "+separator+" "))
	}
	fmt.Println()

	// Summary
	total := len(b.Tasks)
	doing := len(b.TasksByColumn(Doing))
	done := len(b.TasksByColumn(Done))
	todo := len(b.TasksByColumn(Todo))
	fmt.Printf("  %s%d tasks%s — %s%d todo%s, %s%d in progress%s, %s%d done%s\n\n",
		Dim, total, Reset,
		Cyan, todo, Reset,
		Yellow, doing, Reset,
		Green, done, Reset,
	)
}

func padRight(s string, width int) string {
	// Count visible length (strip ANSI)
	visible := stripAnsi(s)
	pad := width - len(visible)
	if pad <= 0 {
		return s
	}
	return s + strings.Repeat(" ", pad)
}

func stripAnsi(s string) string {
	var out strings.Builder
	inEsc := false
	for _, r := range s {
		if r == '\033' {
			inEsc = true
			continue
		}
		if inEsc {
			if (r >= 'a' && r <= 'z') || (r >= 'A' && r <= 'Z') {
				inEsc = false
			}
			continue
		}
		out.WriteRune(r)
	}
	return out.String()
}

func wordWrap(s string, width int) []string {
	if len(s) <= width {
		return []string{s}
	}
	words := strings.Fields(s)
	var lines []string
	current := ""
	for _, w := range words {
		if current == "" {
			current = w
		} else if len(current)+1+len(w) <= width {
			current += " " + w
		} else {
			lines = append(lines, current)
			current = w
		}
	}
	if current != "" {
		lines = append(lines, current)
	}
	return lines
}
