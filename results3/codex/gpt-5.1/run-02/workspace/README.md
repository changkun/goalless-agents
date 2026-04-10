# Focus Timer CLI

`focus-timer` is a tiny Pomodoro-style focus timer for the terminal.

## Install

From the repository root:

```bash
python -m pip install -e .
```

## Usage

Run a default cycle of four 25-minute focus sessions with 5-minute short breaks
and a 15-minute long break:

```bash
focus-timer
```

You can customize durations and number of sessions:

```bash
focus-timer --focus-minutes 30 --short-break-minutes 5 --long-break-minutes 20 --sessions 3
```

