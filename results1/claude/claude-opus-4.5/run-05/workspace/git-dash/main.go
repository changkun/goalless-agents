package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

const (
	reset   = "\033[0m"
	bold    = "\033[1m"
	red     = "\033[31m"
	green   = "\033[32m"
	yellow  = "\033[33m"
	blue    = "\033[34m"
	magenta = "\033[35m"
	cyan    = "\033[36m"
	dim     = "\033[2m"
)

func main() {
	if !isGitRepo() {
		fmt.Println(red + "Not a git repository" + reset)
		os.Exit(1)
	}

	printHeader()
	printBranchInfo()
	printStatus()
	printRecentCommits()
	printStashInfo()
}

func isGitRepo() bool {
	cmd := exec.Command("git", "rev-parse", "--git-dir")
	return cmd.Run() == nil
}

func runGit(args ...string) string {
	cmd := exec.Command("git", args...)
	out, _ := cmd.Output()
	return strings.TrimSpace(string(out))
}

func printHeader() {
	repoName := runGit("rev-parse", "--show-toplevel")
	if idx := strings.LastIndex(repoName, "/"); idx != -1 {
		repoName = repoName[idx+1:]
	}
	fmt.Printf("\n%s%s GIT DASH%s  %s%s%s\n", bold, cyan, reset, yellow, repoName, reset)
	fmt.Println(dim + strings.Repeat("─", 50) + reset)
}

func printBranchInfo() {
	branch := runGit("branch", "--show-current")
	if branch == "" {
		branch = runGit("rev-parse", "--short", "HEAD") + " (detached)"
	}

	// Upstream tracking info
	upstream := runGit("rev-parse", "--abbrev-ref", "@{upstream}")
	var trackingInfo string
	if upstream != "" {
		ahead := runGit("rev-list", "--count", "@{upstream}..HEAD")
		behind := runGit("rev-list", "--count", "HEAD..@{upstream}")
		if ahead != "0" || behind != "0" {
			trackingInfo = fmt.Sprintf(" %s[", dim)
			if ahead != "0" {
				trackingInfo += green + "↑" + ahead + reset + dim
			}
			if behind != "0" {
				if ahead != "0" {
					trackingInfo += " "
				}
				trackingInfo += red + "↓" + behind + reset + dim
			}
			trackingInfo += "]" + reset
		}
	}

	fmt.Printf("%sBranch:%s  %s%s%s%s\n", bold, reset, magenta, branch, reset, trackingInfo)
}

func printStatus() {
	status := runGit("status", "--porcelain")
	if status == "" {
		fmt.Printf("%sStatus:%s  %s✓ Clean%s\n", bold, reset, green, reset)
		return
	}

	var staged, modified, untracked int
	scanner := bufio.NewScanner(strings.NewReader(status))
	for scanner.Scan() {
		line := scanner.Text()
		if len(line) < 2 {
			continue
		}
		x, y := line[0], line[1]
		if x != ' ' && x != '?' {
			staged++
		}
		if y != ' ' && y != '?' {
			modified++
		}
		if x == '?' {
			untracked++
		}
	}

	fmt.Printf("%sStatus:%s  ", bold, reset)
	parts := []string{}
	if staged > 0 {
		parts = append(parts, fmt.Sprintf("%s%d staged%s", green, staged, reset))
	}
	if modified > 0 {
		parts = append(parts, fmt.Sprintf("%s%d modified%s", yellow, modified, reset))
	}
	if untracked > 0 {
		parts = append(parts, fmt.Sprintf("%s%d untracked%s", red, untracked, reset))
	}
	fmt.Println(strings.Join(parts, ", "))
}

func printRecentCommits() {
	fmt.Printf("\n%sRecent Commits:%s\n", bold, reset)

	format := "%h|%s|%cr|%an"
	log := runGit("log", "--oneline", "-5", "--pretty=format:"+format)
	if log == "" {
		fmt.Printf("  %s(no commits)%s\n", dim, reset)
		return
	}

	scanner := bufio.NewScanner(strings.NewReader(log))
	for scanner.Scan() {
		parts := strings.SplitN(scanner.Text(), "|", 4)
		if len(parts) < 4 {
			continue
		}
		hash, msg, time, author := parts[0], parts[1], parts[2], parts[3]
		if len(msg) > 40 {
			msg = msg[:37] + "..."
		}
		fmt.Printf("  %s%s%s %s %s(%s, %s)%s\n",
			yellow, hash, reset, msg, dim, author, time, reset)
	}
}

func printStashInfo() {
	stash := runGit("stash", "list")
	if stash == "" {
		return
	}
	count := strings.Count(stash, "\n") + 1
	fmt.Printf("\n%sStash:%s   %s%d entries%s\n", bold, reset, cyan, count, reset)
}
