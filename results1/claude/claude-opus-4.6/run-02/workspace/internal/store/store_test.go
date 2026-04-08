package store

import (
	"os"
	"path/filepath"
	"testing"

	"github.com/user/kb/internal/model"
)

func TestSaveAndLoad(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "test.json")

	b := model.NewBoard("test-board")
	b.Add("task one", model.PriorityHigh, []string{"go", "cli"})
	b.Add("task two", model.PriorityLow, nil)
	b.Move(1, model.InProgress)

	if err := Save(path, b); err != nil {
		t.Fatalf("Save error: %v", err)
	}

	loaded, err := Load(path)
	if err != nil {
		t.Fatalf("Load error: %v", err)
	}

	if loaded.Name != "test-board" {
		t.Errorf("expected name 'test-board', got %q", loaded.Name)
	}
	if loaded.NextID != 3 {
		t.Errorf("expected NextID 3, got %d", loaded.NextID)
	}
	if len(loaded.Tasks) != 2 {
		t.Fatalf("expected 2 tasks, got %d", len(loaded.Tasks))
	}
	if loaded.Tasks[0].Column != model.InProgress {
		t.Errorf("expected task 1 in InProgress, got %q", loaded.Tasks[0].Column)
	}
	if len(loaded.Tasks[0].Tags) != 2 {
		t.Errorf("expected 2 tags, got %d", len(loaded.Tasks[0].Tags))
	}
}

func TestLoadMissing(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "nonexistent.json")

	b, err := Load(path)
	if err != nil {
		t.Fatalf("Load missing file should not error: %v", err)
	}
	if b.Name != "default" {
		t.Errorf("expected default board name, got %q", b.Name)
	}
}

func TestLoadCorrupt(t *testing.T) {
	dir := t.TempDir()
	path := filepath.Join(dir, "bad.json")
	os.WriteFile(path, []byte("{not json"), 0644)

	_, err := Load(path)
	if err == nil {
		t.Error("expected error for corrupt JSON")
	}
}
