package model

import "time"

type Column string

const (
	Todo       Column = "todo"
	InProgress Column = "in_progress"
	Done       Column = "done"
)

var Columns = []Column{Todo, InProgress, Done}

func ColumnLabel(c Column) string {
	switch c {
	case Todo:
		return "To Do"
	case InProgress:
		return "In Progress"
	case Done:
		return "Done"
	default:
		return string(c)
	}
}

type Priority int

const (
	PriorityLow    Priority = 0
	PriorityMedium Priority = 1
	PriorityHigh   Priority = 2
)

func PriorityLabel(p Priority) string {
	switch p {
	case PriorityHigh:
		return "high"
	case PriorityMedium:
		return "medium"
	default:
		return "low"
	}
}

func ParsePriority(s string) Priority {
	switch s {
	case "high", "h", "2":
		return PriorityHigh
	case "medium", "med", "m", "1":
		return PriorityMedium
	default:
		return PriorityLow
	}
}

type Task struct {
	ID        int       `json:"id"`
	Title     string    `json:"title"`
	Column    Column    `json:"column"`
	Priority  Priority  `json:"priority"`
	Tags      []string  `json:"tags,omitempty"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`
}

type Board struct {
	Name  string `json:"name"`
	Tasks []Task `json:"tasks"`
	NextID int   `json:"next_id"`
}

func NewBoard(name string) *Board {
	return &Board{Name: name, NextID: 1}
}

func (b *Board) Add(title string, priority Priority, tags []string) *Task {
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
	b.Tasks = append(b.Tasks, t)
	b.NextID++
	return &b.Tasks[len(b.Tasks)-1]
}

func (b *Board) FindByID(id int) *Task {
	for i := range b.Tasks {
		if b.Tasks[i].ID == id {
			return &b.Tasks[i]
		}
	}
	return nil
}

func (b *Board) Move(id int, col Column) bool {
	t := b.FindByID(id)
	if t == nil {
		return false
	}
	t.Column = col
	t.UpdatedAt = time.Now()
	return true
}

func (b *Board) Delete(id int) bool {
	for i := range b.Tasks {
		if b.Tasks[i].ID == id {
			b.Tasks = append(b.Tasks[:i], b.Tasks[i+1:]...)
			return true
		}
	}
	return false
}

func (b *Board) TasksByColumn(col Column) []Task {
	var result []Task
	for _, t := range b.Tasks {
		if t.Column == col {
			result = append(result, t)
		}
	}
	return result
}
