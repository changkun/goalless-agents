package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/user/kb/internal/model"
	"github.com/user/kb/internal/store"
	"github.com/user/kb/internal/tui"
)

func main() {
	path := store.DefaultPath()
	if envPath := os.Getenv("KB_FILE"); envPath != "" {
		path = envPath
	}

	args := os.Args[1:]
	if len(args) == 0 {
		runBoard(path)
		return
	}

	switch args[0] {
	case "add", "a":
		cmdAdd(path, args[1:])
	case "list", "ls":
		cmdList(path, args[1:])
	case "move", "mv":
		cmdMove(path, args[1:])
	case "done":
		cmdDone(path, args[1:])
	case "start":
		cmdStart(path, args[1:])
	case "delete", "rm":
		cmdDelete(path, args[1:])
	case "board", "b":
		runBoard(path)
	case "help", "--help", "-h":
		printUsage()
	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\n", args[0])
		printUsage()
		os.Exit(1)
	}
}

func loadBoard(path string) *model.Board {
	b, err := store.Load(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error loading board: %v\n", err)
		os.Exit(1)
	}
	return b
}

func saveBoard(path string, b *model.Board) {
	if err := store.Save(path, b); err != nil {
		fmt.Fprintf(os.Stderr, "Error saving board: %v\n", err)
		os.Exit(1)
	}
}

func cmdAdd(path string, args []string) {
	if len(args) == 0 {
		fmt.Fprintln(os.Stderr, "Usage: kb add <title> [-p high|med|low] [-t tag1,tag2]")
		os.Exit(1)
	}

	var title []string
	priority := model.PriorityLow
	var tags []string

	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "-p", "--priority":
			if i+1 < len(args) {
				i++
				priority = model.ParsePriority(args[i])
			}
		case "-t", "--tags":
			if i+1 < len(args) {
				i++
				tags = strings.Split(args[i], ",")
			}
		default:
			title = append(title, args[i])
		}
	}

	if len(title) == 0 {
		fmt.Fprintln(os.Stderr, "Task title required")
		os.Exit(1)
	}

	b := loadBoard(path)
	t := b.Add(strings.Join(title, " "), priority, tags)
	saveBoard(path, b)
	fmt.Printf("Created task #%d: %s\n", t.ID, t.Title)
}

func cmdList(path string, args []string) {
	b := loadBoard(path)

	var filterCol *model.Column
	if len(args) > 0 {
		col := parseColumn(args[0])
		if col != "" {
			filterCol = &col
		}
	}

	for _, col := range model.Columns {
		if filterCol != nil && *filterCol != col {
			continue
		}
		tasks := b.TasksByColumn(col)
		fmt.Printf("\n  %s (%d)\n", model.ColumnLabel(col), len(tasks))
		if len(tasks) == 0 {
			fmt.Println("    (empty)")
			continue
		}
		for _, t := range tasks {
			pri := priorityIcon(t.Priority)
			tagStr := ""
			if len(t.Tags) > 0 {
				tagStr = " [" + strings.Join(t.Tags, ",") + "]"
			}
			fmt.Printf("    %s #%-3d %s%s\n", pri, t.ID, t.Title, tagStr)
		}
	}
	fmt.Println()
}

func cmdMove(path string, args []string) {
	if len(args) < 2 {
		fmt.Fprintln(os.Stderr, "Usage: kb move <id> <todo|progress|done>")
		os.Exit(1)
	}

	id := parseID(args[0])
	col := parseColumn(args[1])
	if col == "" {
		fmt.Fprintf(os.Stderr, "Invalid column: %s (use: todo, progress, done)\n", args[1])
		os.Exit(1)
	}

	b := loadBoard(path)
	if !b.Move(id, col) {
		fmt.Fprintf(os.Stderr, "Task #%d not found\n", id)
		os.Exit(1)
	}
	saveBoard(path, b)
	fmt.Printf("Moved #%d → %s\n", id, model.ColumnLabel(col))
}

func cmdDone(path string, args []string) {
	if len(args) < 1 {
		fmt.Fprintln(os.Stderr, "Usage: kb done <id>")
		os.Exit(1)
	}
	id := parseID(args[0])
	b := loadBoard(path)
	if !b.Move(id, model.Done) {
		fmt.Fprintf(os.Stderr, "Task #%d not found\n", id)
		os.Exit(1)
	}
	saveBoard(path, b)
	fmt.Printf("Completed #%d ✓\n", id)
}

func cmdStart(path string, args []string) {
	if len(args) < 1 {
		fmt.Fprintln(os.Stderr, "Usage: kb start <id>")
		os.Exit(1)
	}
	id := parseID(args[0])
	b := loadBoard(path)
	if !b.Move(id, model.InProgress) {
		fmt.Fprintf(os.Stderr, "Task #%d not found\n", id)
		os.Exit(1)
	}
	saveBoard(path, b)
	fmt.Printf("Started #%d →\n", id)
}

func cmdDelete(path string, args []string) {
	if len(args) < 1 {
		fmt.Fprintln(os.Stderr, "Usage: kb delete <id>")
		os.Exit(1)
	}
	id := parseID(args[0])
	b := loadBoard(path)
	t := b.FindByID(id)
	if t == nil {
		fmt.Fprintf(os.Stderr, "Task #%d not found\n", id)
		os.Exit(1)
	}
	title := t.Title
	b.Delete(id)
	saveBoard(path, b)
	fmt.Printf("Deleted #%d: %s\n", id, title)
}

func runBoard(path string) {
	b := loadBoard(path)
	if err := tui.Run(b, path); err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
}

func parseID(s string) int {
	s = strings.TrimPrefix(s, "#")
	id, err := strconv.Atoi(s)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Invalid task ID: %s\n", s)
		os.Exit(1)
	}
	return id
}

func parseColumn(s string) model.Column {
	switch strings.ToLower(s) {
	case "todo", "t", "backlog":
		return model.Todo
	case "progress", "wip", "doing", "in_progress", "inprogress", "start":
		return model.InProgress
	case "done", "d", "complete", "finished":
		return model.Done
	}
	return ""
}

func priorityIcon(p model.Priority) string {
	switch p {
	case model.PriorityHigh:
		return "!!!"
	case model.PriorityMedium:
		return " ! "
	default:
		return " . "
	}
}

func printUsage() {
	fmt.Print(`kb - Terminal Kanban Board

Usage:
  kb                     Open interactive board (TUI)
  kb add <title>         Add task  [-p high|med|low] [-t tag1,tag2]
  kb list [column]       List tasks (filter: todo, progress, done)
  kb start <id>          Move task to In Progress
  kb done <id>           Move task to Done
  kb move <id> <column>  Move task to column
  kb delete <id>         Delete a task
  kb help                Show this help

Keyboard shortcuts (TUI):
  h/l or ←/→     Navigate columns
  j/k or ↑/↓     Navigate tasks
  H/L             Move task between columns
  d               Delete task
  +/-             Change priority
  ?               Toggle help
  q               Quit

Environment:
  KB_FILE         Path to board file (default: .kb.json)
`)
}
