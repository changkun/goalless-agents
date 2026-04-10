import argparse
import time
from dataclasses import dataclass


@dataclass
class SessionConfig:
    focus_minutes: int
    short_break_minutes: int
    long_break_minutes: int
    sessions_before_long_break: int = 4


def humanize(seconds: int) -> str:
    minutes, secs = divmod(max(0, int(seconds)), 60)
    if minutes and secs:
        return f"{minutes}m {secs}s"
    if minutes:
        return f"{minutes}m"
    return f"{secs}s"


def countdown(label: str, seconds: int) -> None:
    print(f"{label} for {humanize(seconds)}")
    remaining = seconds
    while remaining > 0:
        mins, secs = divmod(int(remaining), 60)
        print(f"  {mins:02d}:{secs:02d} remaining", end="\r", flush=True)
        time.sleep(1)
        remaining -= 1
    print(f"\n{label} complete.")


def run_sessions(config: SessionConfig, total_sessions: int) -> None:
    for i in range(1, total_sessions + 1):
        print(f"\nSession {i}/{total_sessions}")
        countdown("Focus", config.focus_minutes * 60)
        if i == total_sessions:
            break

        if i % config.sessions_before_long_break == 0:
            countdown("Long break", config.long_break_minutes * 60)
        else:
            countdown("Short break", config.short_break_minutes * 60)


def parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="focus-timer",
        description="Simple Pomodoro-style focus timer for the terminal.",
    )
    parser.add_argument(
        "--focus-minutes",
        type=int,
        default=25,
        help="Length of a focus session in minutes (default: 25).",
    )
    parser.add_argument(
        "--short-break-minutes",
        type=int,
        default=5,
        help="Length of a short break in minutes (default: 5).",
    )
    parser.add_argument(
        "--long-break-minutes",
        type=int,
        default=15,
        help="Length of a long break in minutes (default: 15).",
    )
    parser.add_argument(
        "--sessions",
        type=int,
        default=4,
        help="Total number of focus sessions to run (default: 4).",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="Disable ANSI color output.",
    )
    return parser.parse_args(argv)


def main(argv=None) -> None:
    args = parse_args(argv)
    config = SessionConfig(
        focus_minutes=max(1, args.focus_minutes),
        short_break_minutes=max(1, args.short_break_minutes),
        long_break_minutes=max(1, args.long_break_minutes),
    )
    print("Focus Timer CLI")
    print(
        f"Focus {config.focus_minutes}m, "
        f"short break {config.short_break_minutes}m, "
        f"long break {config.long_break_minutes}m, "
        f"{args.sessions} sessions total."
    )
    run_sessions(config, args.sessions)


if __name__ == "__main__":
    main()

