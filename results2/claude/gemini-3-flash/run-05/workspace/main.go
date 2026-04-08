package main

import (
	"flag"
	"fmt"
	"log"
	"os"
	"os/exec"
	"time"
)

func main() {
	interval := flag.Duration("i", 5*time.Second, "Interval between task executions (e.g., 5s, 1m)")
	threshold := flag.Duration("t", 10*time.Second, "Alert threshold for task execution time (e.g., 10s)")
	flag.Parse()

	args := flag.Args()
	if len(args) == 0 {
		fmt.Println("Usage: task-monitor [-i interval] [-t threshold] <command> [args...]")
		os.Exit(1)
	}

	command := args[0]
	cmdArgs := args[1:]

	fmt.Printf("Monitoring: %s %v\n", command, cmdArgs)
	fmt.Printf("Interval: %v, Alert Threshold: %v\n", *interval, *threshold)
	fmt.Println("---")

	for {
		start := time.Now()
		cmd := exec.Command(command, cmdArgs...)
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr

		err := cmd.Run()
		duration := time.Since(start)

		if err != nil {
			log.Printf("[ERROR] Command failed after %v: %v\n", duration, err)
		} else {
			log.Printf("[SUCCESS] Command finished in %v\n", duration)
		}

		if duration > *threshold {
			log.Printf("[ALERT] Task execution took %v (threshold: %v)\n", duration, *threshold)
		}

		time.Sleep(*interval)
	}
}
