#!/usr/bin/env python3
"""
smartask - A smart CLI task manager with natural language parsing
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List
import argparse


class Task:
    def __init__(self, description: str, due_date: Optional[datetime] = None,
                 priority: str = "medium", completed: bool = False, created_at: Optional[datetime] = None):
        self.description = description
        self.due_date = due_date
        self.priority = priority
        self.completed = completed
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        return {
            "description": self.description,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "priority": self.priority,
            "completed": self.completed,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            description=data["description"],
            due_date=datetime.fromisoformat(data["due_date"]) if data.get("due_date") else None,
            priority=data.get("priority", "medium"),
            completed=data.get("completed", False),
            created_at=datetime.fromisoformat(data["created_at"])
        )


class TaskStore:
    def __init__(self, storage_path: Path = Path.home() / ".smartask.json"):
        self.storage_path = storage_path
        self.tasks: List[Task] = []
        self.load()

    def load(self):
        if self.storage_path.exists():
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                self.tasks = [Task.from_dict(t) for t in data]

    def save(self):
        with open(self.storage_path, 'w') as f:
            json.dump([t.to_dict() for t in self.tasks], f, indent=2)

    def add_task(self, task: Task):
        self.tasks.append(task)
        self.save()

    def get_tasks(self, include_completed: bool = False):
        if include_completed:
            return self.tasks
        return [t for t in self.tasks if not t.completed]

    def complete_task(self, index: int):
        if 0 <= index < len(self.tasks):
            self.tasks[index].completed = True
            self.save()
            return True
        return False

    def delete_task(self, index: int):
        if 0 <= index < len(self.tasks):
            self.tasks.pop(index)
            self.save()
            return True
        return False


class NaturalLanguageParser:
    """Parse natural language task descriptions"""

    PRIORITY_KEYWORDS = {
        "high": ["urgent", "important", "asap", "critical", "high"],
        "low": ["low", "someday", "maybe", "whenever"]
    }

    def parse(self, text: str):
        """Extract task description, due date, and priority from text"""
        original_text = text
        priority = "medium"
        due_date = None

        # Extract priority
        text_lower = text.lower()
        for level, keywords in self.PRIORITY_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    priority = level
                    text = re.sub(rf'\b{keyword}\b', '', text, flags=re.IGNORECASE).strip()
                    break

        # Extract due date/time
        due_date, text = self._extract_date(text)

        # Clean up description
        description = re.sub(r'\s+', ' ', text).strip()

        return description, due_date, priority

    def _extract_date(self, text: str):
        """Extract date/time from text"""
        now = datetime.now()

        # Tomorrow
        if match := re.search(r'\btomorrow\b', text, re.IGNORECASE):
            date = now + timedelta(days=1)
            text = text[:match.start()] + text[match.end():]
            return self._extract_time(text, date)

        # Today
        if match := re.search(r'\btoday\b', text, re.IGNORECASE):
            date = now
            text = text[:match.start()] + text[match.end():]
            return self._extract_time(text, date)

        # Days of week
        days = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
        for i, day in enumerate(days):
            if match := re.search(rf'\b{day}\b', text, re.IGNORECASE):
                days_ahead = (i - now.weekday()) % 7
                if days_ahead == 0:
                    days_ahead = 7
                date = now + timedelta(days=days_ahead)
                text = text[:match.start()] + text[match.end():]
                return self._extract_time(text, date)

        # Relative days (in X days)
        if match := re.search(r'\bin (\d+) days?\b', text, re.IGNORECASE):
            days_count = int(match.group(1))
            date = now + timedelta(days=days_count)
            text = text[:match.start()] + text[match.end():]
            return self._extract_time(text, date)

        # Next week/month
        if match := re.search(r'\bnext week\b', text, re.IGNORECASE):
            date = now + timedelta(weeks=1)
            text = text[:match.start()] + text[match.end():]
            return date, text

        return None, text

    def _extract_time(self, text: str, base_date: datetime):
        """Extract time from text and combine with base date"""
        # Try formats: "at 3pm", "at 15:00", "3:30pm"
        time_patterns = [
            r'\bat (\d{1,2}):(\d{2})\s*(am|pm)?\b',
            r'\bat (\d{1,2})\s*(am|pm)\b',
            r'\b(\d{1,2}):(\d{2})\s*(am|pm)\b',
            r'\b(\d{1,2})\s*(am|pm)\b'
        ]

        for pattern in time_patterns:
            if match := re.search(pattern, text, re.IGNORECASE):
                text = text[:match.start()] + text[match.end():]

                if len(match.groups()) == 3:  # HH:MM am/pm
                    hour = int(match.group(1))
                    minute = int(match.group(2)) if match.group(2) else 0
                    period = match.group(3).lower() if match.group(3) else None
                elif len(match.groups()) == 2:  # HH am/pm
                    hour = int(match.group(1))
                    minute = 0
                    period = match.group(2).lower() if match.group(2) else None

                if period == 'pm' and hour != 12:
                    hour += 12
                elif period == 'am' and hour == 12:
                    hour = 0

                date = base_date.replace(hour=hour, minute=minute, second=0, microsecond=0)
                return date, text

        return base_date, text


def format_task(index: int, task: Task, show_index: bool = True):
    """Format a task for display"""
    prefix = f"[{index}] " if show_index else ""
    status = "✓" if task.completed else "○"

    priority_symbols = {"high": "⚡", "medium": "●", "low": "○"}
    priority_symbol = priority_symbols.get(task.priority, "●")

    due_str = ""
    if task.due_date:
        now = datetime.now()
        if task.due_date.date() == now.date():
            due_str = f" 📅 Today {task.due_date.strftime('%I:%M%p')}"
        elif task.due_date.date() == (now + timedelta(days=1)).date():
            due_str = f" 📅 Tomorrow {task.due_date.strftime('%I:%M%p')}"
        elif task.due_date < now:
            due_str = f" ⚠️  OVERDUE ({task.due_date.strftime('%b %d')})"
        else:
            due_str = f" 📅 {task.due_date.strftime('%b %d, %I:%M%p')}"

    return f"{prefix}{status} {priority_symbol} {task.description}{due_str}"


def cmd_add(args, store: TaskStore, parser: NaturalLanguageParser):
    """Add a new task"""
    text = ' '.join(args.text)
    description, due_date, priority = parser.parse(text)

    task = Task(description=description, due_date=due_date, priority=priority)
    store.add_task(task)

    print(f"✓ Added: {format_task(0, task, show_index=False)}")


def cmd_list(args, store: TaskStore):
    """List tasks"""
    tasks = store.get_tasks(include_completed=args.all)

    if not tasks:
        print("No tasks found. Add one with: smartask add <description>")
        return

    # Filter
    if args.today:
        today = datetime.now().date()
        tasks = [t for t in tasks if t.due_date and t.due_date.date() == today]
    elif args.overdue:
        now = datetime.now()
        tasks = [t for t in tasks if t.due_date and t.due_date < now and not t.completed]

    # Sort
    def sort_key(task):
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return (
            priority_order.get(task.priority, 1),
            task.due_date if task.due_date else datetime.max,
            task.created_at
        )

    tasks_sorted = sorted(tasks, key=sort_key)

    print(f"\n📋 Tasks ({len(tasks_sorted)}):\n")
    for i, task in enumerate(tasks_sorted):
        original_index = store.tasks.index(task)
        print(format_task(original_index, task))
    print()


def cmd_complete(args, store: TaskStore):
    """Mark task as complete"""
    if store.complete_task(args.index):
        print(f"✓ Completed task {args.index}")
    else:
        print(f"❌ Invalid task index: {args.index}")


def cmd_delete(args, store: TaskStore):
    """Delete a task"""
    if store.delete_task(args.index):
        print(f"✓ Deleted task {args.index}")
    else:
        print(f"❌ Invalid task index: {args.index}")


def main():
    parser_main = argparse.ArgumentParser(
        description="smartask - A smart CLI task manager",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  smartask add buy milk tomorrow at 3pm
  smartask add finish report by Friday high priority
  smartask add call mom urgent
  smartask list
  smartask list --today
  smartask complete 0
  smartask delete 1
        """
    )

    subparsers = parser_main.add_subparsers(dest='command', help='Commands')

    # Add command
    parser_add = subparsers.add_parser('add', help='Add a new task')
    parser_add.add_argument('text', nargs='+', help='Task description with optional date/time and priority')

    # List command
    parser_list = subparsers.add_parser('list', help='List tasks')
    parser_list.add_argument('--all', action='store_true', help='Include completed tasks')
    parser_list.add_argument('--today', action='store_true', help='Show only today\'s tasks')
    parser_list.add_argument('--overdue', action='store_true', help='Show only overdue tasks')

    # Complete command
    parser_complete = subparsers.add_parser('complete', help='Mark task as complete')
    parser_complete.add_argument('index', type=int, help='Task index')

    # Delete command
    parser_delete = subparsers.add_parser('delete', help='Delete a task')
    parser_delete.add_argument('index', type=int, help='Task index')

    args = parser_main.parse_args()

    if not args.command:
        parser_main.print_help()
        return

    store = TaskStore()
    nl_parser = NaturalLanguageParser()

    if args.command == 'add':
        cmd_add(args, store, nl_parser)
    elif args.command == 'list':
        cmd_list(args, store)
    elif args.command == 'complete':
        cmd_complete(args, store)
    elif args.command == 'delete':
        cmd_delete(args, store)


if __name__ == "__main__":
    main()
