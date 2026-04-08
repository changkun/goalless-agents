package main

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"sort"
	"strings"
)

type FileStats struct {
	Path        string `json:"path"`
	Language    string `json:"language"`
	Lines       int    `json:"lines"`
	Code        int    `json:"code"`
	Comments    int    `json:"comments"`
	Blank       int    `json:"blank"`
	Functions   int    `json:"functions"`
	Imports     int    `json:"imports"`
}

type ProjectStats struct {
	Files       int        `json:"files"`
	TotalLines  int        `json:"total_lines"`
	TotalCode   int        `json:"total_code"`
	TotalComments int      `json:"total_comments"`
	Languages   map[string]int `json:"languages"`
	FileStats   []FileStats `json:"files_stats"`
}

var languageExts = map[string]string{
	".go": "Go",
	".rs": "Rust",
	".py": "Python",
	".js": "JavaScript",
	".ts": "TypeScript",
	".jsx": "JSX",
	".tsx": "TSX",
	".c": "C",
	".cpp": "C++",
	".h": "C Header",
	".java": "Java",
	".rb": "Ruby",
	".php": "PHP",
	".sh": "Shell",
	".md": "Markdown",
	".json": "JSON",
	".yaml": "YAML",
	".yml": "YAML",
}

func getLanguage(path string) string {
	ext := filepath.Ext(path)
	if lang, ok := languageExts[ext]; ok {
		return lang
	}
	return "Unknown"
}

func analyzeFile(path string) (*FileStats, error) {
	content, err := os.ReadFile(path)
	if err != nil {
		return nil, err
	}

	stats := &FileStats{
		Path:     path,
		Language: getLanguage(path),
	}

	lines := strings.Split(string(content), "\n")
	stats.Lines = len(lines)

	inBlockComment := false
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)

		// Handle block comments
		if strings.Contains(trimmed, "/*") {
			inBlockComment = true
		}
		if strings.Contains(trimmed, "*/") {
			inBlockComment = false
			stats.Comments++
			continue
		}

		if inBlockComment {
			stats.Comments++
			continue
		}

		// Empty lines
		if trimmed == "" {
			stats.Blank++
			continue
		}

		// Single-line comments
		if strings.HasPrefix(trimmed, "//") || strings.HasPrefix(trimmed, "#") ||
			strings.HasPrefix(trimmed, "--") || strings.HasPrefix(trimmed, ";") {
			stats.Comments++
			continue
		}

		// Count functions
		if strings.Contains(trimmed, "func ") || strings.Contains(trimmed, "def ") ||
			strings.Contains(trimmed, "function ") {
			stats.Functions++
		}

		// Count imports
		if strings.Contains(trimmed, "import ") || strings.Contains(trimmed, "require ") ||
			strings.Contains(trimmed, "use ") || strings.Contains(trimmed, "from ") {
			stats.Imports++
		}

		stats.Code++
	}

	return stats, nil
}

func walkDirectory(root string) ([]FileStats, error) {
	var results []FileStats

	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil
		}

		// Skip hidden directories and vendor/node_modules
		if info.IsDir() {
			if strings.HasPrefix(info.Name(), ".") || info.Name() == "vendor" ||
				info.Name() == "node_modules" || info.Name() == "__pycache__" {
				return filepath.SkipDir
			}
			return nil
		}

		// Skip binary files
		if !isTextFile(path) {
			return nil
		}

		stats, err := analyzeFile(path)
		if err == nil && stats.Lines > 0 {
			results = append(results, *stats)
		}

		return nil
	})

	return results, err
}

func isTextFile(path string) bool {
	// Check by extension
	for ext := range languageExts {
		if strings.HasSuffix(path, ext) {
			return true
		}
	}

	// Common text files without extensions
	base := filepath.Base(path)
	textFiles := []string{"Makefile", "Dockerfile", "README", "LICENSE", ".gitignore"}
	for _, f := range textFiles {
		if base == f || strings.HasPrefix(base, f) {
			return true
		}
	}

	return false
}

func aggregateStats(files []FileStats) ProjectStats {
	stats := ProjectStats{
		Files:     len(files),
		Languages: make(map[string]int),
		FileStats: files,
	}

	sort.Slice(files, func(i, j int) bool {
		return files[i].Lines > files[j].Lines
	})

	for _, f := range files {
		stats.TotalLines += f.Lines
		stats.TotalCode += f.Code
		stats.TotalComments += f.Comments
		stats.Languages[f.Language]++
	}

	return stats
}

func printTable(stats ProjectStats) {
	fmt.Printf("\n📊 CODE ANALYSIS REPORT\n")
	fmt.Printf("════════════════════════════════════════════\n")
	fmt.Printf("Total Files:        %d\n", stats.Files)
	fmt.Printf("Total Lines:        %d\n", stats.TotalLines)
	fmt.Printf("Code Lines:         %d\n", stats.TotalCode)
	fmt.Printf("Comment Lines:      %d\n", stats.TotalComments)
	fmt.Printf("────────────────────────────────────────────\n")
	fmt.Printf("Languages:\n")

	languages := make([]string, 0, len(stats.Languages))
	for lang := range stats.Languages {
		languages = append(languages, lang)
	}
	sort.Strings(languages)

	for _, lang := range languages {
		fmt.Printf("  %-15s %3d files\n", lang, stats.Languages[lang])
	}

	fmt.Printf("════════════════════════════════════════════\n")
	fmt.Printf("\n📁 TOP FILES BY LINES:\n")
	fmt.Printf("────────────────────────────────────────────\n")

	for i, f := range stats.FileStats {
		if i >= 10 {
			break
		}
		fmt.Printf("%3d lines | %s\n", f.Lines, f.Path)
	}

	fmt.Printf("════════════════════════════════════════════\n\n")
}

func main() {
	if len(os.Args) < 2 {
		fmt.Fprintf(os.Stderr, "Usage: %s <directory> [--json]\n", os.Args[0])
		os.Exit(1)
	}

	targetDir := os.Args[1]
	jsonOutput := len(os.Args) > 2 && os.Args[2] == "--json"

	// Check if directory exists
	info, err := os.Stat(targetDir)
	if err != nil {
		log.Fatalf("Error: Cannot access directory: %v\n", err)
	}

	if !info.IsDir() {
		log.Fatalf("Error: %s is not a directory\n", targetDir)
	}

	// Analyze files
	files, err := walkDirectory(targetDir)
	if err != nil {
		log.Fatalf("Error scanning directory: %v\n", err)
	}

	if len(files) == 0 {
		fmt.Fprintf(os.Stderr, "No source files found in %s\n", targetDir)
		os.Exit(1)
	}

	stats := aggregateStats(files)

	// Output
	if jsonOutput {
		output, _ := json.MarshalIndent(stats, "", "  ")
		fmt.Println(string(output))
	} else {
		printTable(stats)
	}
}
