tasklog
=======

`tasklog` is a tiny Python CLI to log timestamped tasks into a local text file and review what you did today.

Usage
-----

- Add a task:

  `python tasklog.py add Write project proposal`

- List today’s tasks:

  `python tasklog.py list`

- Show tasks per day:

  `python tasklog.py stats`

By default, entries are stored in `~/.tasklog/tasks.log`. Use `--log-file` to point at a different file if you prefer.

