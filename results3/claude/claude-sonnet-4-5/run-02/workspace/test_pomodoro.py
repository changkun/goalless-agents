#!/usr/bin/env python3
"""Quick test of Pomodoro timer functionality"""

import sys
sys.path.insert(0, '/workspace')

from pomodoro import PomodoroTimer

def test_timer():
    timer = PomodoroTimer()

    # Test time formatting
    assert timer.format_time(0) == "00:00"
    assert timer.format_time(60) == "01:00"
    assert timer.format_time(125) == "02:05"
    assert timer.format_time(1500) == "25:00"

    print("✓ Time formatting works")

    # Test timer initialization
    assert timer.work_duration == 1500
    assert timer.break_duration == 300
    assert timer.long_break_duration == 900

    print("✓ Timer durations correct")

    # Test session tracking
    timer.save_session('work')
    print("✓ Session saving works")

    timer.show_stats()
    print("✓ Stats display works")

    print("\n🎉 All tests passed!")

if __name__ == '__main__':
    test_timer()
