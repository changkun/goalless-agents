package model

import "testing"

func TestNewBoard(t *testing.T) {
	b := NewBoard("test")
	if b.Name != "test" {
		t.Errorf("expected name 'test', got %q", b.Name)
	}
	if b.NextID != 1 {
		t.Errorf("expected NextID 1, got %d", b.NextID)
	}
	if len(b.Tasks) != 0 {
		t.Errorf("expected 0 tasks, got %d", len(b.Tasks))
	}
}

func TestAdd(t *testing.T) {
	b := NewBoard("test")
	task := b.Add("my task", PriorityHigh, []string{"go"})

	if task.ID != 1 {
		t.Errorf("expected ID 1, got %d", task.ID)
	}
	if task.Title != "my task" {
		t.Errorf("expected title 'my task', got %q", task.Title)
	}
	if task.Column != Todo {
		t.Errorf("expected column Todo, got %q", task.Column)
	}
	if task.Priority != PriorityHigh {
		t.Errorf("expected high priority, got %d", task.Priority)
	}
	if len(task.Tags) != 1 || task.Tags[0] != "go" {
		t.Errorf("expected tags [go], got %v", task.Tags)
	}
	if b.NextID != 2 {
		t.Errorf("expected NextID 2, got %d", b.NextID)
	}
}

func TestFindByID(t *testing.T) {
	b := NewBoard("test")
	b.Add("first", PriorityLow, nil)
	b.Add("second", PriorityLow, nil)

	found := b.FindByID(2)
	if found == nil || found.Title != "second" {
		t.Error("expected to find 'second'")
	}

	notFound := b.FindByID(99)
	if notFound != nil {
		t.Error("expected nil for missing ID")
	}
}

func TestMove(t *testing.T) {
	b := NewBoard("test")
	b.Add("task", PriorityLow, nil)

	if !b.Move(1, InProgress) {
		t.Error("expected Move to return true")
	}
	task := b.FindByID(1)
	if task.Column != InProgress {
		t.Errorf("expected InProgress, got %q", task.Column)
	}

	if b.Move(99, Done) {
		t.Error("expected Move to return false for missing ID")
	}
}

func TestDelete(t *testing.T) {
	b := NewBoard("test")
	b.Add("task1", PriorityLow, nil)
	b.Add("task2", PriorityLow, nil)

	if !b.Delete(1) {
		t.Error("expected Delete to return true")
	}
	if len(b.Tasks) != 1 {
		t.Errorf("expected 1 task, got %d", len(b.Tasks))
	}
	if b.Tasks[0].ID != 2 {
		t.Errorf("expected remaining task ID 2, got %d", b.Tasks[0].ID)
	}

	if b.Delete(99) {
		t.Error("expected Delete to return false for missing ID")
	}
}

func TestTasksByColumn(t *testing.T) {
	b := NewBoard("test")
	b.Add("todo1", PriorityLow, nil)
	b.Add("todo2", PriorityLow, nil)
	b.Move(2, InProgress)

	todos := b.TasksByColumn(Todo)
	if len(todos) != 1 {
		t.Errorf("expected 1 todo, got %d", len(todos))
	}

	wip := b.TasksByColumn(InProgress)
	if len(wip) != 1 {
		t.Errorf("expected 1 in-progress, got %d", len(wip))
	}

	done := b.TasksByColumn(Done)
	if len(done) != 0 {
		t.Errorf("expected 0 done, got %d", len(done))
	}
}

func TestParsePriority(t *testing.T) {
	tests := []struct {
		input string
		want  Priority
	}{
		{"high", PriorityHigh},
		{"h", PriorityHigh},
		{"2", PriorityHigh},
		{"medium", PriorityMedium},
		{"med", PriorityMedium},
		{"m", PriorityMedium},
		{"1", PriorityMedium},
		{"low", PriorityLow},
		{"anything", PriorityLow},
	}
	for _, tt := range tests {
		got := ParsePriority(tt.input)
		if got != tt.want {
			t.Errorf("ParsePriority(%q) = %d, want %d", tt.input, got, tt.want)
		}
	}
}
