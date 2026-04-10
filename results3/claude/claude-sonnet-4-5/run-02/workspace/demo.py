#!/usr/bin/env python3
"""
Quick demo of the Pomodoro timer (shortened durations for demo purposes)
"""

import time
import sys
sys.path.insert(0, '/workspace')

from pomodoro import PomodoroTimer

def demo():
    print("\n🎬 POMODORO TIMER DEMO")
    print("=" * 50)
    print("Running a quick 10-second demo session...\n")

    timer = PomodoroTimer()
    # Override durations for demo
    timer.work_duration = 5
    timer.break_duration = 3

    try:
        # Demo work session
        timer.countdown(timer.work_duration, "🍅 WORK SESSION #1", "\033[91m")
        timer.save_session('work')

        print("\n✨ Work session complete! Time for a break.\n")
        time.sleep(1)

        # Demo break session
        timer.countdown(timer.break_duration, "☕ SHORT BREAK", "\033[92m")
        timer.save_session('break')

        print("\n\n🎉 Demo complete! Run 'python3 pomodoro.py' to start a real session.")
        print("Or run 'python3 pomodoro.py stats' to see your productivity stats.\n")

    except KeyboardInterrupt:
        print("\n\nDemo interrupted!")

if __name__ == '__main__':
    demo()
