package main

import (
	"flag"
	"fmt"
	"io/fs"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

const (
	colorReset  = "\033[0m"
	colorBlue   = "\033[34m"
	colorCyan   = "\033[36m"
	colorYellow = "\033[33m"
	colorGreen  = "\033[32m"
	colorGray   = "\033[90m"
)

type Config struct {
	ShowHidden  bool
	MaxDepth    int
	ShowSize    bool
	DirsOnly    bool
	NoColor     bool
	SortBySize  bool
}

type Entry struct {
	Name    string
	Path    string
	IsDir   bool
	Size    int64
	Children []*Entry
}

func main() {
	cfg := Config{}
	flag.BoolVar(&cfg.ShowHidden, "a", false, "Show hidden files")
	flag.IntVar(&cfg.MaxDepth, "L", -1, "Max depth (-1 = unlimited)")
	flag.BoolVar(&cfg.ShowSize, "s", false, "Show file sizes")
	flag.BoolVar(&cfg.DirsOnly, "d", false, "List directories only")
	flag.BoolVar(&cfg.NoColor, "n", false, "No color output")
	flag.BoolVar(&cfg.SortBySize, "S", false, "Sort by size (largest first)")
	flag.Usage = func() {
		fmt.Fprintf(os.Stderr, "dirtree - fast directory tree with sizes\n\n")
		fmt.Fprintf(os.Stderr, "Usage: dirtree [options] [path]\n\n")
		fmt.Fprintf(os.Stderr, "Options:\n")
		flag.PrintDefaults()
	}
	flag.Parse()

	root := "."
	if flag.NArg() > 0 {
		root = flag.Arg(0)
	}

	info, err := os.Stat(root)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error: %v\n", err)
		os.Exit(1)
	}
	if !info.IsDir() {
		fmt.Fprintf(os.Stderr, "Error: %s is not a directory\n", root)
		os.Exit(1)
	}

	tree := buildTree(root, &cfg, 0)
	if cfg.SortBySize {
		sortBySize(tree)
	}

	dirs, files := countTree(tree)
	printTree(tree, "", true, &cfg)
	fmt.Printf("\n%d directories, %d files", dirs, files)
	if cfg.ShowSize {
		fmt.Printf(", %s total", formatSize(tree.Size))
	}
	fmt.Println()
}

func buildTree(path string, cfg *Config, depth int) *Entry {
	info, err := os.Stat(path)
	if err != nil {
		return nil
	}

	entry := &Entry{
		Name:  filepath.Base(path),
		Path:  path,
		IsDir: info.IsDir(),
		Size:  info.Size(),
	}

	if !info.IsDir() {
		return entry
	}

	if cfg.MaxDepth >= 0 && depth >= cfg.MaxDepth {
		entry.Size = calcDirSize(path)
		return entry
	}

	entries, err := os.ReadDir(path)
	if err != nil {
		return entry
	}

	for _, e := range entries {
		name := e.Name()
		if !cfg.ShowHidden && strings.HasPrefix(name, ".") {
			continue
		}
		if cfg.DirsOnly && !e.IsDir() {
			continue
		}

		child := buildTree(filepath.Join(path, name), cfg, depth+1)
		if child != nil {
			entry.Children = append(entry.Children, child)
			entry.Size += child.Size
		}
	}

	sort.Slice(entry.Children, func(i, j int) bool {
		if entry.Children[i].IsDir != entry.Children[j].IsDir {
			return entry.Children[i].IsDir
		}
		return strings.ToLower(entry.Children[i].Name) < strings.ToLower(entry.Children[j].Name)
	})

	return entry
}

func sortBySize(entry *Entry) {
	if entry == nil {
		return
	}
	sort.Slice(entry.Children, func(i, j int) bool {
		return entry.Children[i].Size > entry.Children[j].Size
	})
	for _, child := range entry.Children {
		sortBySize(child)
	}
}

func calcDirSize(path string) int64 {
	var size int64
	filepath.WalkDir(path, func(_ string, d fs.DirEntry, err error) error {
		if err != nil {
			return nil
		}
		if !d.IsDir() {
			if info, err := d.Info(); err == nil {
				size += info.Size()
			}
		}
		return nil
	})
	return size
}

func printTree(entry *Entry, prefix string, isRoot bool, cfg *Config) {
	if entry == nil {
		return
	}

	name := entry.Name
	if !cfg.NoColor {
		if entry.IsDir {
			name = colorBlue + name + colorReset
		} else {
			name = colorizeFile(entry.Name, cfg)
		}
	}

	sizeStr := ""
	if cfg.ShowSize {
		if cfg.NoColor {
			sizeStr = fmt.Sprintf(" [%s]", formatSize(entry.Size))
		} else {
			sizeStr = fmt.Sprintf(" %s[%s]%s", colorGray, formatSize(entry.Size), colorReset)
		}
	}

	fmt.Printf("%s%s%s\n", prefix, name, sizeStr)

	for i, child := range entry.Children {
		isLast := i == len(entry.Children)-1
		connector := "├── "
		extension := "│   "
		if isLast {
			connector = "└── "
			extension = "    "
		}
		printChild(child, prefix+connector, prefix+extension, cfg)
	}
}

func printChild(entry *Entry, linePrefix string, childPrefix string, cfg *Config) {
	if entry == nil {
		return
	}

	name := entry.Name
	if !cfg.NoColor {
		if entry.IsDir {
			name = colorBlue + name + colorReset
		} else {
			name = colorizeFile(entry.Name, cfg)
		}
	}

	sizeStr := ""
	if cfg.ShowSize {
		if cfg.NoColor {
			sizeStr = fmt.Sprintf(" [%s]", formatSize(entry.Size))
		} else {
			sizeStr = fmt.Sprintf(" %s[%s]%s", colorGray, formatSize(entry.Size), colorReset)
		}
	}

	fmt.Printf("%s%s%s\n", linePrefix, name, sizeStr)

	for i, child := range entry.Children {
		isLast := i == len(entry.Children)-1
		connector := "├── "
		extension := "│   "
		if isLast {
			connector = "└── "
			extension = "    "
		}
		printChild(child, childPrefix+connector, childPrefix+extension, cfg)
	}
}

func colorizeFile(name string, cfg *Config) string {
	ext := strings.ToLower(filepath.Ext(name))
	switch ext {
	case ".go", ".rs", ".py", ".js", ".ts", ".c", ".cpp", ".java":
		return colorGreen + name + colorReset
	case ".md", ".txt", ".json", ".yaml", ".yml", ".toml":
		return colorCyan + name + colorReset
	case ".exe", ".bin", ".sh", ".bash":
		return colorYellow + name + colorReset
	default:
		return name
	}
}

func formatSize(bytes int64) string {
	const unit = 1024
	if bytes < unit {
		return fmt.Sprintf("%dB", bytes)
	}
	div, exp := int64(unit), 0
	for n := bytes / unit; n >= unit; n /= unit {
		div *= unit
		exp++
	}
	return fmt.Sprintf("%.1f%c", float64(bytes)/float64(div), "KMGTPE"[exp])
}

func countTree(entry *Entry) (dirs, files int) {
	if entry == nil {
		return 0, 0
	}
	if entry.IsDir {
		dirs = 1
	} else {
		files = 1
	}
	for _, child := range entry.Children {
		d, f := countTree(child)
		dirs += d
		files += f
	}
	if entry.IsDir {
		dirs--
	}
	return dirs, files
}
