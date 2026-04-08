package store

import (
	"encoding/json"
	"os"
	"path/filepath"

	"github.com/user/kb/internal/model"
)

const defaultFile = ".kb.json"

func DefaultPath() string {
	return filepath.Join(".", defaultFile)
}

func Load(path string) (*model.Board, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		if os.IsNotExist(err) {
			return model.NewBoard("default"), nil
		}
		return nil, err
	}
	var b model.Board
	if err := json.Unmarshal(data, &b); err != nil {
		return nil, err
	}
	return &b, nil
}

func Save(path string, b *model.Board) error {
	data, err := json.MarshalIndent(b, "", "  ")
	if err != nil {
		return err
	}
	return os.WriteFile(path, data, 0644)
}
