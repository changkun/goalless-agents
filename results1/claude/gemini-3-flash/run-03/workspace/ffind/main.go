package main

import (
	"flag"
	"fmt"
	"os"
	"path/filepath"
	"regexp"
	"runtime"
	"strings"
	"sync"
)

func main() {
	pattern := flag.String("p", "", "Regex pattern to search for in filenames")
	startDir := flag.String("d", ".", "Root directory to start search")
	workers := flag.Int("w", runtime.NumCPU()*2, "Number of parallel workers")
	ignoreDirs := flag.String("i", ".git,node_modules,vendor,target", "Comma-separated directories to ignore")
	flag.Parse()

	if *pattern == "" {
		fmt.Println("Usage: ffind -p <regex> [-d <dir>] [-w <workers>] [-i <ignore_dirs>]")
		os.Exit(1)
	}

	re, err := regexp.Compile(*pattern)
	if err != nil {
		fmt.Printf("Invalid regex: %v\n", err)
		os.Exit(1)
	}

	ignoreList := strings.Split(*ignoreDirs, ",")
	shouldIgnore := func(name string) bool {
		for _, ignore := range ignoreList {
			if name == ignore {
				return true
			}
		}
		return false
	}

	jobs := make(chan string, 5000)
	var wg sync.WaitGroup

	// Start worker pool
	for i := 0; i < *workers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for path := range jobs {
				if re.MatchString(filepath.Base(path)) {
					fmt.Println(path)
				}
			}
		}()
	}

	// Walk the filesystem
	err = filepath.Walk(*startDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return nil // Skip files we can't access
		}
		if info.IsDir() {
			if shouldIgnore(info.Name()) {
				return filepath.SkipDir
			}
			return nil
		}
		jobs <- path
		return nil
	})

	close(jobs)
	wg.Wait()

	if err != nil {
		fmt.Printf("Error walking directory: %v\n", err)
	}
}
