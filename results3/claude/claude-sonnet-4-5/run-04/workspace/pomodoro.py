#!/usr/bin/env python3
"""
Pomodoro Timer CLI - A productivity tool for focused work sessions
"""
import time
import json
import os
import sys
import platform
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

DATA_FILE = Path.home() / ".pomodoro_data.json"

class PomodoroTimer:
    def __init__(self):
        self.work_duration = 25 * 60  # 25 minutes
        self.short_break = 5 * 60     # 5 minutes
        self.long_break = 15 * 60     # 15 minutes
        self.sessions_until_long_break = 4
        self.data = self.load_data()

    def load_data(self):
        if DATA_FILE.exists():
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        return {
            'tasks': [],
            'completed_sessions': [],
            'current_task': None,
            'sessions_completed': 0
        }

    def save_data(self):
        with open(DATA_FILE, 'w') as f:
            json.dump(self.data, f, indent=2)

    def send_notification(self, title, message):
        """Send a desktop notification using system-native tools"""
        try:
            system = platform.system()

            if system == 'Linux':
                # Use notify-send on Linux
                subprocess.run(['notify-send', title, message],
                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == 'Darwin':
                # Use osascript on macOS
                script = f'display notification "{message}" with title "{title}"'
                subprocess.run(['osascript', '-e', script],
                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif system == 'Windows':
                # Use PowerShell on Windows
                ps_script = f'''
                [Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] > $null
                $template = [Windows.UI.Notifications.ToastNotificationManager]::GetTemplateContent([Windows.UI.Notifications.ToastTemplateType]::ToastText02)
                $toastXml = [xml] $template.GetXml()
                $toastXml.GetElementsByTagName("text")[0].AppendChild($toastXml.CreateTextNode("{title}")) > $null
                $toastXml.GetElementsByTagName("text")[1].AppendChild($toastXml.CreateTextNode("{message}")) > $null
                $xml = New-Object Windows.Data.Xml.Dom.XmlDocument
                $xml.LoadXml($toastXml.OuterXml)
                $toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
                [Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier("Pomodoro Timer").Show($toast)
                '''
                subprocess.run(['powershell', '-Command', ps_script],
                             check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            # Silently fail if notifications aren't available
            pass

    def add_task(self, task_name):
        task = {
            'id': len(self.data['tasks']) + 1,
            'name': task_name,
            'created_at': datetime.now().isoformat(),
            'completed': False,
            'pomodoros': 0
        }
        self.data['tasks'].append(task)
        self.save_data()
        print(f"✓ Task added: {task_name}")

    def list_tasks(self):
        tasks = [t for t in self.data['tasks'] if not t['completed']]
        if not tasks:
            print("No active tasks. Add one with: pomodoro add <task>")
            return

        print("\n📝 Active Tasks:")
        for task in tasks:
            status = "→" if task['id'] == self.data.get('current_task') else " "
            print(f"  {status} [{task['id']}] {task['name']} ({task['pomodoros']} 🍅)")
        print()

    def complete_task(self, task_id):
        for task in self.data['tasks']:
            if task['id'] == task_id:
                task['completed'] = True
                task['completed_at'] = datetime.now().isoformat()
                self.save_data()
                print(f"✓ Task completed: {task['name']}")
                return
        print(f"Task {task_id} not found")

    def set_current_task(self, task_id):
        for task in self.data['tasks']:
            if task['id'] == task_id and not task['completed']:
                self.data['current_task'] = task_id
                self.save_data()
                print(f"→ Working on: {task['name']}")
                return
        print(f"Task {task_id} not found or already completed")

    def display_timer(self, seconds_left, total_seconds, session_type):
        minutes, seconds = divmod(seconds_left, 60)
        bar_width = 40
        progress = (total_seconds - seconds_left) / total_seconds
        filled = int(bar_width * progress)
        bar = '█' * filled + '░' * (bar_width - filled)

        sys.stdout.write('\r')
        sys.stdout.write(f"{session_type} [{bar}] {minutes:02d}:{seconds:02d}")
        sys.stdout.flush()

    def run_timer(self, duration, session_type):
        start_time = time.time()
        end_time = start_time + duration

        try:
            while time.time() < end_time:
                seconds_left = int(end_time - time.time())
                self.display_timer(seconds_left, duration, session_type)
                time.sleep(0.1)

            sys.stdout.write('\r' + ' ' * 80 + '\r')
            return True
        except KeyboardInterrupt:
            sys.stdout.write('\r' + ' ' * 80 + '\r')
            print("⏸  Timer paused")
            return False

    def start_session(self):
        session_count = self.data['sessions_completed']

        # Work session
        print(f"\n🍅 Pomodoro #{session_count + 1} - Focus time!")
        if self.data.get('current_task'):
            task = next((t for t in self.data['tasks'] if t['id'] == self.data['current_task']), None)
            if task:
                print(f"   Working on: {task['name']}")

        completed = self.run_timer(self.work_duration, "🍅 FOCUS")

        if not completed:
            return

        # Log completed session
        self.data['sessions_completed'] += 1
        session_count += 1

        session_log = {
            'timestamp': datetime.now().isoformat(),
            'type': 'work',
            'task_id': self.data.get('current_task')
        }
        self.data['completed_sessions'].append(session_log)

        # Update task pomodoro count
        if self.data.get('current_task'):
            for task in self.data['tasks']:
                if task['id'] == self.data['current_task']:
                    task['pomodoros'] += 1
                    break

        self.save_data()

        print("✓ Pomodoro completed!")
        self.send_notification("🍅 Pomodoro Complete!",
                             "Great work! Time for a break.")

        # Break time
        if session_count % self.sessions_until_long_break == 0:
            print(f"\n☕ Long break time! ({self.long_break // 60} minutes)")
            break_completed = self.run_timer(self.long_break, "☕ LONG BREAK")
        else:
            print(f"\n☕ Short break time! ({self.short_break // 60} minutes)")
            break_completed = self.run_timer(self.short_break, "☕ SHORT BREAK")

        if break_completed:
            print("✓ Break complete! Ready for the next session.\n")
            self.send_notification("☕ Break Complete!",
                                 "Time to start your next pomodoro!")
        else:
            print()

    def show_stats(self):
        total_sessions = len(self.data['completed_sessions'])
        total_minutes = total_sessions * (self.work_duration // 60)

        today = datetime.now().date()
        today_sessions = [
            s for s in self.data['completed_sessions']
            if datetime.fromisoformat(s['timestamp']).date() == today
        ]

        completed_tasks = [t for t in self.data['tasks'] if t['completed']]

        print("\n📊 Pomodoro Statistics")
        print("=" * 40)
        print(f"Total sessions completed: {total_sessions} 🍅")
        print(f"Total focused time: {total_minutes} minutes")
        print(f"Today's sessions: {len(today_sessions)} 🍅")
        print(f"Tasks completed: {len(completed_tasks)}")

        if completed_tasks:
            print("\n✓ Completed Tasks:")
            for task in completed_tasks[-5:]:
                print(f"  • {task['name']} ({task['pomodoros']} 🍅)")
        print()

def main():
    timer = PomodoroTimer()

    if len(sys.argv) < 2:
        print("Pomodoro Timer CLI")
        print("\nUsage:")
        print("  pomodoro.py start              - Start a pomodoro session")
        print("  pomodoro.py add <task>         - Add a new task")
        print("  pomodoro.py list               - List active tasks")
        print("  pomodoro.py work <task_id>     - Set current task")
        print("  pomodoro.py done <task_id>     - Mark task as complete")
        print("  pomodoro.py stats              - Show statistics")
        return

    command = sys.argv[1]

    if command == "start":
        timer.start_session()
    elif command == "add" and len(sys.argv) > 2:
        task_name = ' '.join(sys.argv[2:])
        timer.add_task(task_name)
    elif command == "list":
        timer.list_tasks()
    elif command == "work" and len(sys.argv) > 2:
        timer.set_current_task(int(sys.argv[2]))
    elif command == "done" and len(sys.argv) > 2:
        timer.complete_task(int(sys.argv[2]))
    elif command == "stats":
        timer.show_stats()
    else:
        print(f"Unknown command: {command}")
        print("Run without arguments to see usage")

if __name__ == "__main__":
    main()
