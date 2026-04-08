package main

import (
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"time"
)

// Column represents a kanban column status
type Column string

const (
	Todo  Column = "todo"
	Doing Column = "doing"
	Done  Column = "done"
)

var AllColumns = []Column{Todo, Doing, Done}

// Task represents a single task on the board
type Task struct {
	ID        int       `json:"id"`
	Title     string    `json:"title"`
	Column    Column    `json:"column"`
	Priority  int       `json:"priority"` // 1=low, 2=medium, 3=high
	Tags      []string  `json:"tags,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

// Board holds all tasks and metadata
type Board struct {
	Name    string `json:"name"`
	NextID  int    `json:"next_id"`
	Tasks   []Task `json:"tasks"`
	path    string
}

func dataDir() string {
	home, err := os.UserHomeDir()
	if err != nil {
		home = "."
	}
	return filepath.Join(home, ".taskboard")
}

func boardPath(name string) string {
	return filepath.Join(dataDir(), name+".json")
}

// LoadBoard loads a board from disk, or creates a new one
func LoadBoard(name string) (*Board, error) {
	path := boardPath(name)
	b := &Board{Name: name, NextID: 1, path: path}

	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return b, nil
		}
		return nil, fmt.Errorf("reading board: %w", err)
	}

	if err := json.Unmarshal(data, b); err != nil {
		return nil, fmt.Errorf("parsing board: %w", err)
	}
	b.path = path
	return b, nil
}

// Save writes the board to disk
func (b *Board) Save() error {
	if err := os.MkdirAll(filepath.Dir(b.path), 0755); err != nil {
		return err
	}
	data, err := json.MarshalIndent(b, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(b.path, data, 0644)
}

// Add creates a new task in the Todo column
func (b *Board) Add(title string, priority int, tags []string) Task {
	now := time.Now()
	t := Task{
		ID:        b.NextID,
		Title:     title,
		Column:    Todo,
		Priority:  priority,
		Tags:      tags,
		CreatedAt: now,
		UpdatedAt: now,
	}
	b.NextID++
	b.Tasks = append(b.Tasks, t)
	return t
}

// FindTask returns a pointer to the task with the given ID
func (b *Board) FindTask(id int) *Task {
	for i := range b.Tasks {
		if b.Tasks[i].ID == id {
			return &b.Tasks[i]
		}
	}
	return nil
}

// Move changes a task's column
func (b *Board) Move(id int, col Column) error {
	t := b.FindTask(id)
	if t == nil {
		return fmt.Errorf("task %d not found", id)
	}
	t.Column = col
	t.UpdatedAt = time.Now()
	return nil
}

// Delete removes a task by ID
func (b *Board) Delete(id int) error {
	for i, t := range b.Tasks {
		if t.ID == id {
			b.Tasks = append(b.Tasks[:i], b.Tasks[i+1:]...)
			return nil
		}
	}
	return fmt.Errorf("task %d not found", id)
}

// TasksByColumn returns tasks filtered by column
func (b *Board) TasksByColumn(col Column) []Task {
	var result []Task
	for _, t := range b.Tasks {
		if t.Column == col {
			result = append(result, t)
		}
	}
	return result
}
