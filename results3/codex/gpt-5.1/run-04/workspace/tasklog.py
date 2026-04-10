import argparse
import datetime as _dt
from pathlib import Path


DEFAULT_LOG_DIR = Path.home() / ".tasklog"
DEFAULT_LOG_FILE = DEFAULT_LOG_DIR / "tasks.log"


def _ensure_log_dir(path: Path) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)


def _log_entry(path: Path, description: str) -> None:
    _ensure_log_dir(path.parent)
    timestamp = _dt.datetime.now().isoformat(timespec="seconds")
    line = f"{timestamp}\t{description.strip()}\n"
    with path.open("a", encoding="utf-8") as f:
        f.write(line)


def _parse_line(line: str):
    try:
        ts_str, desc = line.rstrip("\n").split("\t", 1)
        ts = _dt.datetime.fromisoformat(ts_str)
        return ts, desc
    except ValueError:
        return None


def _iter_entries(path: Path):
    if not path.exists():
        return
    with path.open("r", encoding="utf-8") as f:
        for raw in f:
            parsed = _parse_line(raw)
            if parsed is not None:
                yield parsed


def cmd_add(args: argparse.Namespace) -> int:
    description = " ".join(args.description).strip()
    if not description:
        print("Nothing to add (empty description).")
        return 1
    _log_entry(args.log_file, description)
    print("Added:", description)
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    today = _dt.date.today()
    found = False
    for ts, desc in _iter_entries(args.log_file):
        if ts.date() == today:
            if not found:
                print(f"Tasks for {today.isoformat()}:")
                found = True
            time_str = ts.time().strftime("%H:%M:%S")
            print(f"- [{time_str}] {desc}")
    if not found:
        print(f"No tasks logged for {today.isoformat()}.")
    return 0


def cmd_stats(args: argparse.Namespace) -> int:
    by_date = {}
    for ts, _ in _iter_entries(args.log_file):
        d = ts.date().isoformat()
        by_date[d] = by_date.get(d, 0) + 1
    if not by_date:
        print("No tasks logged yet.")
        return 0
    print("Tasks per day:")
    for day in sorted(by_date.keys()):
        print(f"- {day}: {by_date[day]}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tasklog",
        description="Tiny CLI to log timestamped tasks to a local file.",
    )
    parser.add_argument(
        "--log-file",
        type=Path,
        default=DEFAULT_LOG_FILE,
        help=f"Path to task log file (default: {DEFAULT_LOG_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_add = subparsers.add_parser("add", help="Add a new task entry.")
    p_add.add_argument("description", nargs=argparse.REMAINDER, help="Task description.")
    p_add.set_defaults(func=cmd_add)

    p_list = subparsers.add_parser("list", help="List today’s tasks.")
    p_list.set_defaults(func=cmd_list)

    p_stats = subparsers.add_parser("stats", help="Show number of tasks per day.")
    p_stats.set_defaults(func=cmd_stats)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    func = getattr(args, "func", None)
    if func is None:
        parser.print_help()
        return 1
    return func(args)


if __name__ == "__main__":
    raise SystemExit(main())

