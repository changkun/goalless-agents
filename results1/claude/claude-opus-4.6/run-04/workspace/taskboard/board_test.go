package main

import (
	"encoding/json"
	"os"
	"path/filepath"
	"testing"
)

func tempBoard(t *testing.T) *Board {
	t.Helper()
	dir := t.TempDir()
	b := &Board{
		Name:   "test",
		NextID: 1,
		path:   filepath.Join(dir, "test.json"),
	}
	return b
}

func TestAddAndFind(t *testing.T) {
	b := tempBoard(t)

	task := b.Add("My task", 2, []string{"work"})
	if task.ID != 1 {
		t.Errorf("expected ID 1, got %d", task.ID)
	}
	if task.Column != Todo {
		t.Errorf("expected column todo, got %s", task.Column)
	}
	if b.NextID != 2 {
		t.Errorf("expected NextID 2, got %d", b.NextID)
	}

	found := b.FindTask(1)
	if found == nil {
		t.Fatal("expected to find task 1")
	}
	if found.Title != "My task" {
		t.Errorf("expected title 'My task', got %q", found.Title)
	}
}

func TestMove(t *testing.T) {
	b := tempBoard(t)
	b.Add("Task 1", 1, nil)

	if err := b.Move(1, Doing); err != nil {
		t.Fatal(err)
	}
	if b.FindTask(1).Column != Doing {
		t.Error("expected column to be doing")
	}

	if err := b.Move(1, Done); err != nil {
		t.Fatal(err)
	}
	if b.FindTask(1).Column != Done {
		t.Error("expected column to be done")
	}

	if err := b.Move(999, Done); err == nil {
		t.Error("expected error for nonexistent task")
	}
}

func TestDelete(t *testing.T) {
	b := tempBoard(t)
	b.Add("Task 1", 1, nil)
	b.Add("Task 2", 2, nil)

	if err := b.Delete(1); err != nil {
		t.Fatal(err)
	}
	if len(b.Tasks) != 1 {
		t.Errorf("expected 1 task, got %d", len(b.Tasks))
	}
	if b.Tasks[0].ID != 2 {
		t.Errorf("expected remaining task ID 2, got %d", b.Tasks[0].ID)
	}

	if err := b.Delete(999); err == nil {
		t.Error("expected error for nonexistent task")
	}
}

func TestSaveAndLoad(t *testing.T) {
	b := tempBoard(t)
	b.Add("Persistent task", 3, []string{"important"})
	b.Move(1, Doing)

	if err := b.Save(); err != nil {
		t.Fatal(err)
	}

	// Verify file exists
	if _, err := os.Stat(b.path); err != nil {
		t.Fatal("board file should exist after save")
	}

	// Load into new board struct
	loaded := &Board{path: b.path}
	data, err := os.ReadFile(b.path)
	if err != nil {
		t.Fatal(err)
	}
	if err := json.Unmarshal(data, loaded); err != nil {
		t.Fatal(err)
	}

	if len(loaded.Tasks) != 1 {
		t.Fatalf("expected 1 task, got %d", len(loaded.Tasks))
	}
	if loaded.Tasks[0].Title != "Persistent task" {
		t.Errorf("wrong title: %q", loaded.Tasks[0].Title)
	}
	if loaded.Tasks[0].Column != Doing {
		t.Errorf("expected column doing, got %s", loaded.Tasks[0].Column)
	}
}

func TestTasksByColumn(t *testing.T) {
	b := tempBoard(t)
	b.Add("T1", 1, nil)
	b.Add("T2", 2, nil)
	b.Add("T3", 3, nil)
	b.Move(2, Doing)
	b.Move(3, Done)

	todo := b.TasksByColumn(Todo)
	if len(todo) != 1 {
		t.Errorf("expected 1 todo task, got %d", len(todo))
	}

	doing := b.TasksByColumn(Doing)
	if len(doing) != 1 {
		t.Errorf("expected 1 doing task, got %d", len(doing))
	}

	done := b.TasksByColumn(Done)
	if len(done) != 1 {
		t.Errorf("expected 1 done task, got %d", len(done))
	}
}
