package main

import (
	"encoding/json"
	"fmt"
	"os"
	"strconv"
	"text/tabwriter"
	"time"
)

type Task struct {
	ID        int       `json:"id"`
	Content   string    `json:"content"`
	Completed bool      `json:"completed"`
	CreatedAt time.Time `json:"created_at"`
}

type TaskList struct {
	Tasks  []Task `json:"tasks"`
	NextID int    `json:"next_id"`
}

const dbFile = "tasks.json"

func main() {
	if len(os.Args) < 2 {
		printHelp()
		return
	}

	list := loadTasks()

	switch os.Args[1] {
	case "add":
		if len(os.Args) < 3 {
			fmt.Println("Error: Missing task content")
			return
		}
		list.Tasks = append(list.Tasks, Task{
			ID:        list.NextID,
			Content:   os.Args[2],
			Completed: false,
			CreatedAt: time.Now(),
		})
		list.NextID++
		saveTasks(list)
		fmt.Printf("Added task #%d\n", list.NextID-1)

	case "list":
		w := tabwriter.NewWriter(os.Stdout, 0, 0, 3, ' ', 0)
		fmt.Fprintln(w, "ID\tSTATUS\tTASK\tCREATED")
		for _, t := range list.Tasks {
			status := "○"
			if t.Completed {
				status = "✓"
			}
			fmt.Fprintf(w, "%d\t%s\t%s\t%s\n", t.ID, status, t.Content, t.CreatedAt.Format("2006-01-02 15:04"))
		}
		w.Flush()

	case "done":
		if len(os.Args) < 3 {
			fmt.Println("Error: Missing task ID")
			return
		}
		id, _ := strconv.Atoi(os.Args[2])
		found := false
		for i, t := range list.Tasks {
			if t.ID == id {
				list.Tasks[i].Completed = true
				found = true
				break
			}
		}
		if found {
			saveTasks(list)
			fmt.Printf("Marked task #%d as done\n", id)
		} else {
			fmt.Printf("Task #%d not found\n", id)
		}

	case "rm":
		if len(os.Args) < 3 {
			fmt.Println("Error: Missing task ID")
			return
		}
		id, _ := strconv.Atoi(os.Args[2])
		newTasks := []Task{}
		found := false
		for _, t := range list.Tasks {
			if t.ID == id {
				found = true
				continue
			}
			newTasks = append(newTasks, t)
		}
		if found {
			list.Tasks = newTasks
			saveTasks(list)
			fmt.Printf("Deleted task #%d\n", id)
		} else {
			fmt.Printf("Task #%d not found\n", id)
		}

	default:
		printHelp()
	}
}

func printHelp() {
	fmt.Println("GoTask - A simple CLI task manager")
	fmt.Println("\nUsage:")
	fmt.Println("  add \"task content\"  Add a new task")
	fmt.Println("  list                List all tasks")
	fmt.Println("  done <id>           Mark a task as completed")
	fmt.Println("  rm <id>             Remove a task")
}

func loadTasks() TaskList {
	var list TaskList
	data, err := os.ReadFile(dbFile)
	if err != nil {
		return TaskList{Tasks: []Task{}, NextID: 1}
	}
	json.Unmarshal(data, &list)
	return list
}

func saveTasks(list TaskList) {
	data, _ := json.MarshalIndent(list, "", "  ")
	os.WriteFile(dbFile, data, 0644)
}
