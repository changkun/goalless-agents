#!/usr/bin/env python3
"""
TaskMan - A simple terminal-based task manager
"""
import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional


class Colors:
    """ANSI color codes for terminal output"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'


class TaskManager:
    def __init__(self, storage_path: str = "~/.taskman.json"):
        self.storage_path = Path(storage_path).expanduser()
        self.tasks = self._load_tasks()

    def _load_tasks(self) -> List[Dict]:
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                return json.load(f)
        return []

    def _save_tasks(self):
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.storage_path, 'w') as f:
            json.dump(self.tasks, f, indent=2)

    def _next_id(self) -> int:
        return max([t['id'] for t in self.tasks], default=0) + 1

    def add_task(self, description: str, priority: str = "medium", tags: Optional[List[str]] = None):
        task = {
            'id': self._next_id(),
            'description': description,
            'priority': priority,
            'tags': tags or [],
            'completed': False,
            'created_at': datetime.now().isoformat(),
            'completed_at': None
        }
        self.tasks.append(task)
        self._save_tasks()
        print(f"{Colors.GREEN}✓{Colors.RESET} Task added with ID {Colors.BOLD}{task['id']}{Colors.RESET}")

    def list_tasks(self, show_completed: bool = False, priority: Optional[str] = None, tag: Optional[str] = None):
        filtered_tasks = self.tasks

        if not show_completed:
            filtered_tasks = [t for t in filtered_tasks if not t['completed']]

        if priority:
            filtered_tasks = [t for t in filtered_tasks if t['priority'] == priority]

        if tag:
            filtered_tasks = [t for t in filtered_tasks if tag in t['tags']]

        if not filtered_tasks:
            print(f"{Colors.YELLOW}No tasks found.{Colors.RESET}")
            return

        print(f"\n{Colors.BOLD}{'ID':<5} {'Priority':<10} {'Status':<12} {'Description':<40} {'Tags'}{Colors.RESET}")
        print("─" * 90)

        for task in filtered_tasks:
            priority_color = {
                'high': Colors.RED,
                'medium': Colors.YELLOW,
                'low': Colors.BLUE
            }.get(task['priority'], Colors.RESET)

            status = f"{Colors.GREEN}✓ Complete{Colors.RESET}" if task['completed'] else f"{Colors.CYAN}○ Pending{Colors.RESET}"
            tags_str = f"{Colors.MAGENTA}{', '.join(task['tags'])}{Colors.RESET}" if task['tags'] else ""

            print(f"{task['id']:<5} {priority_color}{task['priority']:<10}{Colors.RESET} {status:<22} {task['description'][:40]:<40} {tags_str}")

        print()

    def complete_task(self, task_id: int):
        for task in self.tasks:
            if task['id'] == task_id:
                if task['completed']:
                    print(f"{Colors.YELLOW}Task {task_id} is already completed.{Colors.RESET}")
                    return
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self._save_tasks()
                print(f"{Colors.GREEN}✓{Colors.RESET} Task {task_id} marked as complete!")
                return
        print(f"{Colors.RED}✗{Colors.RESET} Task {task_id} not found.")

    def delete_task(self, task_id: int):
        for i, task in enumerate(self.tasks):
            if task['id'] == task_id:
                self.tasks.pop(i)
                self._save_tasks()
                print(f"{Colors.GREEN}✓{Colors.RESET} Task {task_id} deleted.")
                return
        print(f"{Colors.RED}✗{Colors.RESET} Task {task_id} not found.")

    def stats(self):
        total = len(self.tasks)
        completed = sum(1 for t in self.tasks if t['completed'])
        pending = total - completed

        print(f"\n{Colors.BOLD}Task Statistics{Colors.RESET}")
        print("─" * 30)
        print(f"Total tasks:     {total}")
        print(f"{Colors.GREEN}Completed:{Colors.RESET}       {completed}")
        print(f"{Colors.CYAN}Pending:{Colors.RESET}         {pending}")

        if pending > 0:
            by_priority = {}
            for task in self.tasks:
                if not task['completed']:
                    by_priority[task['priority']] = by_priority.get(task['priority'], 0) + 1

            print(f"\n{Colors.BOLD}Pending by priority:{Colors.RESET}")
            for priority in ['high', 'medium', 'low']:
                if priority in by_priority:
                    color = {
                        'high': Colors.RED,
                        'medium': Colors.YELLOW,
                        'low': Colors.BLUE
                    }[priority]
                    print(f"  {color}{priority.capitalize()}:{Colors.RESET} {by_priority[priority]}")
        print()


def main():
    parser = argparse.ArgumentParser(
        description="TaskMan - A simple terminal task manager",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Add command
    add_parser = subparsers.add_parser('add', help='Add a new task')
    add_parser.add_argument('description', help='Task description')
    add_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                           default='medium', help='Task priority (default: medium)')
    add_parser.add_argument('-t', '--tags', nargs='+', help='Task tags')

    # List command
    list_parser = subparsers.add_parser('list', help='List tasks')
    list_parser.add_argument('-a', '--all', action='store_true', help='Show completed tasks')
    list_parser.add_argument('-p', '--priority', choices=['low', 'medium', 'high'],
                            help='Filter by priority')
    list_parser.add_argument('-t', '--tag', help='Filter by tag')

    # Complete command
    complete_parser = subparsers.add_parser('complete', help='Mark a task as complete')
    complete_parser.add_argument('id', type=int, help='Task ID')

    # Delete command
    delete_parser = subparsers.add_parser('delete', help='Delete a task')
    delete_parser.add_argument('id', type=int, help='Task ID')

    # Stats command
    subparsers.add_parser('stats', help='Show task statistics')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    tm = TaskManager()

    if args.command == 'add':
        tm.add_task(args.description, args.priority, args.tags)
    elif args.command == 'list':
        tm.list_tasks(show_completed=args.all, priority=args.priority, tag=args.tag)
    elif args.command == 'complete':
        tm.complete_task(args.id)
    elif args.command == 'delete':
        tm.delete_task(args.id)
    elif args.command == 'stats':
        tm.stats()


if __name__ == '__main__':
    main()
