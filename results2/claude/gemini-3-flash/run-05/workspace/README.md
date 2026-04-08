# Task Monitor

A simple Go-based CLI tool to monitor and alert on task execution time.

## Installation
Ensure you have Go installed. Clone this repository and run:
```bash
go build -o task-monitor main.go
```

## Usage
Run the monitor with a command of your choice:
```bash
./task-monitor [-i interval] [-t threshold] <command> [args...]
```

Example: Monitor if a `curl` request takes longer than 2 seconds:
```bash
./task-monitor -i 10s -t 2s curl -I https://example.com
```

- `-i`: Interval between task executions (default: 5s, e.g., 5s, 1m)
- `-t`: Alert threshold for task execution time (default: 10s, e.g., 10s)
