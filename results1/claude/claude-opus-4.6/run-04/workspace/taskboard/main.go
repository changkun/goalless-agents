package main

import (
	"fmt"
	"os"
	"strconv"
	"strings"
)

const usage = `%staskboard%s — terminal kanban board

%sUsage:%s
  taskboard                          Show the board
  taskboard add <title> [flags]      Add a task
  taskboard move <id> <column>       Move task (todo|doing|done)
  taskboard done <id>                Shortcut: move task to done
  taskboard start <id>               Shortcut: move task to doing
  taskboard delete <id>              Remove a task
  taskboard list [column]            List tasks (optionally filtered)
  taskboard boards                   List all boards
  taskboard help                     Show this help

%sFlags:%s
  -p, --priority <1|2|3>    Priority: 1=low, 2=medium, 3=high (default: 2)
  -t, --tag <tag>            Add tag (repeatable)
  -b, --board <name>         Board name (default: "default")

%sExamples:%s
  taskboard add "Fix login bug" -p 3 -t auth -t urgent
  taskboard start 1
  taskboard done 1
  taskboard -b work add "Write quarterly report"
`

func main() {
	args := os.Args[1:]

	boardName := "default"
	// Extract board flag
	args = extractFlag(args, "-b", "--board", &boardName)

	if len(args) == 0 {
		showBoard(boardName)
		return
	}

	cmd := args[0]
	args = args[1:]

	switch cmd {
	case "add":
		cmdAdd(boardName, args)
	case "move":
		cmdMove(boardName, args)
	case "start":
		cmdQuickMove(boardName, args, Doing)
	case "done":
		cmdQuickMove(boardName, args, Done)
	case "delete", "rm":
		cmdDelete(boardName, args)
	case "list", "ls":
		cmdList(boardName, args)
	case "boards":
		cmdBoards()
	case "help", "--help", "-h":
		fmt.Printf(usage, Bold, Reset, Bold, Reset, Bold, Reset, Bold, Reset)
	default:
		fmt.Fprintf(os.Stderr, "Unknown command: %s\nRun 'taskboard help' for usage.\n", cmd)
		os.Exit(1)
	}
}

func showBoard(name string) {
	b, err := LoadBoard(name)
	exitOnErr(err)
	RenderBoard(b)
}

func cmdAdd(boardName string, args []string) {
	if len(args) == 0 {
		fatal("Usage: taskboard add <title> [-p priority] [-t tag ...]")
	}

	priority := 2
	var tags []string
	var titleParts []string

	for i := 0; i < len(args); i++ {
		switch args[i] {
		case "-p", "--priority":
			i++
			if i < len(args) {
				p, err := strconv.Atoi(args[i])
				if err != nil || p < 1 || p > 3 {
					fatal("Priority must be 1, 2, or 3")
				}
				priority = p
			}
		case "-t", "--tag":
			i++
			if i < len(args) {
				tags = append(tags, args[i])
			}
		default:
			titleParts = append(titleParts, args[i])
		}
	}

	title := strings.Join(titleParts, " ")
	if title == "" {
		fatal("Task title cannot be empty")
	}

	b, err := LoadBoard(boardName)
	exitOnErr(err)
	t := b.Add(title, priority, tags)
	exitOnErr(b.Save())

	fmt.Printf("%s✓%s Added task #%d: %s\n", Green, Reset, t.ID, t.Title)
}

func cmdMove(boardName string, args []string) {
	if len(args) < 2 {
		fatal("Usage: taskboard move <id> <todo|doing|done>")
	}

	id, err := strconv.Atoi(args[0])
	if err != nil {
		fatal("Invalid task ID: " + args[0])
	}

	col, err := parseColumn(args[1])
	if err != nil {
		fatal(err.Error())
	}

	b, err := LoadBoard(boardName)
	exitOnErr(err)
	exitOnErr(b.Move(id, col))
	exitOnErr(b.Save())

	fmt.Printf("%s✓%s Moved task #%d → %s\n", Green, Reset, id, col)
}

func cmdQuickMove(boardName string, args []string, col Column) {
	if len(args) < 1 {
		fatal("Usage: taskboard " + string(col) + " <id>")
	}

	id, err := strconv.Atoi(args[0])
	if err != nil {
		fatal("Invalid task ID: " + args[0])
	}

	b, err := LoadBoard(boardName)
	exitOnErr(err)
	exitOnErr(b.Move(id, col))
	exitOnErr(b.Save())

	label := map[Column]string{Doing: "Started", Done: "Completed"}
	fmt.Printf("%s✓%s %s task #%d\n", Green, Reset, label[col], id)
}

func cmdDelete(boardName string, args []string) {
	if len(args) < 1 {
		fatal("Usage: taskboard delete <id>")
	}

	id, err := strconv.Atoi(args[0])
	if err != nil {
		fatal("Invalid task ID: " + args[0])
	}

	b, err := LoadBoard(boardName)
	exitOnErr(err)
	exitOnErr(b.Delete(id))
	exitOnErr(b.Save())

	fmt.Printf("%s✓%s Deleted task #%d\n", Green, Reset, id)
}

func cmdList(boardName string, args []string) {
	b, err := LoadBoard(boardName)
	exitOnErr(err)

	var tasks []Task
	if len(args) > 0 {
		col, err := parseColumn(args[0])
		if err != nil {
			fatal(err.Error())
		}
		tasks = b.TasksByColumn(col)
	} else {
		tasks = b.Tasks
	}

	if len(tasks) == 0 {
		fmt.Println(Dim + "No tasks found." + Reset)
		return
	}

	for _, t := range tasks {
		icon := priorityIcon(t.Priority)
		colColor := columnColor(t.Column)
		tagStr := ""
		if len(t.Tags) > 0 {
			tagStr = Dim + " " + strings.Join(tagSlice(t.Tags), " ") + Reset
		}
		fmt.Printf("  %s #%-4d %s%-7s%s %s%s\n",
			icon, t.ID, colColor, t.Column, Reset, t.Title, tagStr)
	}
}

func cmdBoards() {
	dir := dataDir()
	entries, err := os.ReadDir(dir)
	if err != nil {
		if os.IsNotExist(err) {
			fmt.Println(Dim + "No boards yet. Create one with: taskboard add \"My first task\"" + Reset)
			return
		}
		exitOnErr(err)
	}

	fmt.Printf("\n  %s%sBoards:%s\n\n", Bold, Magenta, Reset)
	for _, e := range entries {
		if strings.HasSuffix(e.Name(), ".json") {
			name := strings.TrimSuffix(e.Name(), ".json")
			b, err := LoadBoard(name)
			if err != nil {
				continue
			}
			total := len(b.Tasks)
			done := len(b.TasksByColumn(Done))
			fmt.Printf("  • %s%-15s%s %d tasks (%d done)\n", Cyan, name, Reset, total, done)
		}
	}
	fmt.Println()
}

func parseColumn(s string) (Column, error) {
	switch strings.ToLower(s) {
	case "todo":
		return Todo, nil
	case "doing", "wip", "progress", "inprogress":
		return Doing, nil
	case "done", "complete", "finished":
		return Done, nil
	default:
		return "", fmt.Errorf("invalid column %q — use todo, doing, or done", s)
	}
}

func extractFlag(args []string, short, long string, value *string) []string {
	var result []string
	for i := 0; i < len(args); i++ {
		if (args[i] == short || args[i] == long) && i+1 < len(args) {
			*value = args[i+1]
			i++ // skip value
		} else {
			result = append(result, args[i])
		}
	}
	return result
}

func fatal(msg string) {
	fmt.Fprintf(os.Stderr, "%s✗%s %s\n", Red, Reset, msg)
	os.Exit(1)
}

func exitOnErr(err error) {
	if err != nil {
		fatal(err.Error())
	}
}
