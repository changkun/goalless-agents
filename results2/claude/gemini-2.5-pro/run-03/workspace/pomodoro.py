import time
import argparse
import beepy

def countdown(minutes, label):
    """Counts down for a given number of minutes."""
    seconds = minutes * 60
    while seconds > 0:
        mins, secs = divmod(seconds, 60)
        timer_display = f"\r{label}: {mins:02d}:{secs:02d}"
        print(timer_display, end="")
        time.sleep(1)
        seconds -= 1
    print(f"\r{label}: Time's up!                 ")
    beepy.beep(sound=1)

def main():
    """Main function to run the Pomodoro timer."""
    parser = argparse.ArgumentParser(description="A simple command-line Pomodoro timer.")
    parser.add_argument("-w", "--work", type=int, default=25, help="Work interval in minutes (default: 25)")
    parser.add_argument("-b", "--break", type=int, default=5, help="Break interval in minutes (default: 5)")
    args = parser.parse_args()

    print("Pomodoro timer started!")
    try:
        while True:
            countdown(args.work, "Work")
            print("Good job! Take a break.")
            countdown(args.break, "Break")
            print("Time to get back to work!")
    except KeyboardInterrupt:
        print("\nPomodoro timer stopped.")

if __name__ == "__main__":
    main()
