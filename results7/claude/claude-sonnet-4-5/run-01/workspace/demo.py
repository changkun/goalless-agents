#!/usr/bin/env python3
"""
Quick demo of the Pomodoro timer (shortened durations for testing)
"""

import sys
import os

# Temporarily modify the PomodoroTimer class for demo
import pomodoro

# Create a custom timer with shorter durations
class DemoTimer(pomodoro.PomodoroTimer):
    def __init__(self):
        super().__init__(data_file=".pomodoro_demo_data.json")
        self.work_duration = 10  # 10 seconds instead of 25 minutes
        self.short_break = 5     # 5 seconds instead of 5 minutes
        self.long_break = 8      # 8 seconds instead of 15 minutes

if __name__ == "__main__":
    print("🍅 Pomodoro Timer Demo (shortened for testing)")
    print("=" * 50)
    print("Work sessions: 10 seconds")
    print("Short breaks: 5 seconds")
    print("Long breaks: 8 seconds")
    print()

    timer = DemoTimer()
    timer.start_session("Demo Task")
