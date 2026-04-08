#!/usr/bin/env python3
"""
sysmon.py — live terminal system monitor
Displays CPU, memory, disk, and network stats, refreshing every second.
Requires: psutil  (pip install psutil)
"""

import curses
import time
import psutil
import datetime
import sys

REFRESH_INTERVAL = 1.0  # seconds
BAR_WIDTH = 40


def bar(pct, width=BAR_WIDTH, filled="█", empty="░"):
    filled_n = int(round(pct / 100 * width))
    return filled * filled_n + empty * (width - filled_n)


def color_for_pct(pct):
    if pct >= 90:
        return curses.color_pair(3)   # red
    if pct >= 70:
        return curses.color_pair(2)   # yellow
    return curses.color_pair(1)       # green


def fmt_bytes(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} PB"


def fmt_uptime(seconds):
    d, rem = divmod(int(seconds), 86400)
    h, rem = divmod(rem, 3600)
    m, s = divmod(rem, 60)
    parts = []
    if d:
        parts.append(f"{d}d")
    if h or d:
        parts.append(f"{h}h")
    parts.append(f"{m}m {s}s")
    return " ".join(parts)


class Monitor:
    def __init__(self):
        self._prev_net = psutil.net_io_counters()
        self._prev_time = time.time()
        self._net_rx_rate = 0.0
        self._net_tx_rate = 0.0

    def snapshot(self):
        now = time.time()
        dt = max(now - self._prev_time, 0.001)

        cpu_pcts = psutil.cpu_percent(percpu=True)
        cpu_total = psutil.cpu_percent()
        mem = psutil.virtual_memory()
        swap = psutil.swap_memory()
        disk = psutil.disk_usage("/")
        net = psutil.net_io_counters()

        self._net_rx_rate = (net.bytes_recv - self._prev_net.bytes_recv) / dt
        self._net_tx_rate = (net.bytes_sent - self._prev_net.bytes_sent) / dt
        self._prev_net = net
        self._prev_time = now

        try:
            temps = psutil.sensors_temperatures()
        except AttributeError:
            temps = {}

        load = psutil.getloadavg()
        boot_time = psutil.boot_time()
        uptime = time.time() - boot_time

        return {
            "time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "cpu_total": cpu_total,
            "cpu_pcts": cpu_pcts,
            "mem": mem,
            "swap": swap,
            "disk": disk,
            "net_rx": self._net_rx_rate,
            "net_tx": self._net_tx_rate,
            "net_total_rx": net.bytes_recv,
            "net_total_tx": net.bytes_sent,
            "temps": temps,
            "load": load,
            "uptime": uptime,
        }


def draw(stdscr, mon):
    curses.curs_set(0)
    curses.start_color()
    curses.use_default_colors()
    curses.init_pair(1, curses.COLOR_GREEN, -1)
    curses.init_pair(2, curses.COLOR_YELLOW, -1)
    curses.init_pair(3, curses.COLOR_RED, -1)
    curses.init_pair(4, curses.COLOR_CYAN, -1)
    curses.init_pair(5, curses.COLOR_WHITE, -1)
    curses.init_pair(6, curses.COLOR_MAGENTA, -1)

    stdscr.nodelay(True)
    stdscr.timeout(int(REFRESH_INTERVAL * 1000))

    while True:
        key = stdscr.getch()
        if key in (ord("q"), ord("Q"), 27):
            break

        data = mon.snapshot()
        stdscr.erase()
        rows, cols = stdscr.getmaxyx()
        row = 0

        def put(r, c, text, attr=curses.A_NORMAL, clip=True):
            if r < 0 or r >= rows:
                return
            if c < 0:
                return
            if clip and c + len(text) > cols:
                text = text[: cols - c]
            if not text:
                return
            try:
                stdscr.addstr(r, c, text, attr)
            except curses.error:
                pass

        # ── header ──────────────────────────────────────────────────────────
        title = "  SYSMON — live system monitor  "
        put(row, 0, title.center(cols), curses.color_pair(4) | curses.A_BOLD)
        row += 1
        time_str = f" {data['time']}   up {fmt_uptime(data['uptime'])}   load {data['load'][0]:.2f} {data['load'][1]:.2f} {data['load'][2]:.2f} "
        put(row, 0, time_str.center(cols), curses.color_pair(5))
        row += 1
        put(row, 0, "─" * cols, curses.color_pair(5))
        row += 1

        # ── CPU total ────────────────────────────────────────────────────────
        pct = data["cpu_total"]
        label = f" CPU  {pct:5.1f}%  "
        b = bar(pct)
        put(row, 0, label, curses.A_BOLD)
        put(row, len(label), f"[{b}]", color_for_pct(pct))
        row += 1

        # per-core
        cpu_pcts = data["cpu_pcts"]
        n_cores = len(cpu_pcts)
        cols_per_core = max(1, cols // max(n_cores, 1))
        bar_w = max(4, cols_per_core - 10)

        for i, cp in enumerate(cpu_pcts):
            col_start = i * cols_per_core
            if col_start + cols_per_core > cols:
                break
            core_label = f" C{i:<2} {cp:4.0f}% "
            b2 = bar(cp, width=bar_w)
            put(row, col_start, core_label, curses.A_DIM)
            put(row, col_start + len(core_label), b2, color_for_pct(cp) | curses.A_DIM)
        row += 1

        # ── temperature ──────────────────────────────────────────────────────
        all_temps = []
        for sensor_name, readings in data["temps"].items():
            for r in readings:
                all_temps.append((sensor_name, r.label or sensor_name, r.current))
        if all_temps:
            temp_str = "  ".join(f"{lbl}: {t:.0f}°C" for _, lbl, t in all_temps[:8])
            put(row, 0, f" Temp  {temp_str}", curses.color_pair(6))
            row += 1

        put(row, 0, "─" * cols, curses.color_pair(5))
        row += 1

        # ── Memory ───────────────────────────────────────────────────────────
        mem = data["mem"]
        mem_pct = mem.percent
        mem_label = f" MEM  {mem_pct:5.1f}%  "
        mem_detail = f"  {fmt_bytes(mem.used)} / {fmt_bytes(mem.total)}  avail {fmt_bytes(mem.available)}"
        b = bar(mem_pct)
        put(row, 0, mem_label, curses.A_BOLD)
        put(row, len(mem_label), f"[{b}]", color_for_pct(mem_pct))
        put(row, len(mem_label) + BAR_WIDTH + 2, mem_detail, curses.color_pair(5))
        row += 1

        swap = data["swap"]
        if swap.total > 0:
            sw_pct = swap.percent
            sw_label = f" SWP  {sw_pct:5.1f}%  "
            sw_detail = f"  {fmt_bytes(swap.used)} / {fmt_bytes(swap.total)}"
            b = bar(sw_pct)
            put(row, 0, sw_label, curses.A_BOLD)
            put(row, len(sw_label), f"[{b}]", color_for_pct(sw_pct))
            put(row, len(sw_label) + BAR_WIDTH + 2, sw_detail, curses.color_pair(5))
            row += 1

        put(row, 0, "─" * cols, curses.color_pair(5))
        row += 1

        # ── Disk ─────────────────────────────────────────────────────────────
        disk = data["disk"]
        dk_pct = disk.percent
        dk_label = f" DSK  {dk_pct:5.1f}%  "
        dk_detail = f"  {fmt_bytes(disk.used)} / {fmt_bytes(disk.total)}  free {fmt_bytes(disk.free)}"
        b = bar(dk_pct)
        put(row, 0, dk_label, curses.A_BOLD)
        put(row, len(dk_label), f"[{b}]", color_for_pct(dk_pct))
        put(row, len(dk_label) + BAR_WIDTH + 2, dk_detail, curses.color_pair(5))
        row += 1

        put(row, 0, "─" * cols, curses.color_pair(5))
        row += 1

        # ── Network ──────────────────────────────────────────────────────────
        rx = data["net_rx"]
        tx = data["net_tx"]
        rx_total = data["net_total_rx"]
        tx_total = data["net_total_tx"]
        put(row, 0, " NET", curses.A_BOLD)
        put(row, 5,
            f"  ↓ {fmt_bytes(rx):>10}/s   total recv {fmt_bytes(rx_total)}",
            curses.color_pair(1))
        row += 1
        put(row, 5,
            f"  ↑ {fmt_bytes(tx):>10}/s   total sent {fmt_bytes(tx_total)}",
            curses.color_pair(2))
        row += 1

        put(row, 0, "─" * cols, curses.color_pair(5))
        row += 1

        # ── footer ───────────────────────────────────────────────────────────
        put(rows - 1, 0, "  Press q to quit ".center(cols), curses.color_pair(5) | curses.A_DIM)

        stdscr.refresh()


def main():
    mon = Monitor()
    # warm up cpu_percent (first call always returns 0)
    psutil.cpu_percent(percpu=True)
    time.sleep(0.1)
    try:
        curses.wrapper(draw, mon)
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    # check dependency
    try:
        import psutil  # noqa: F401
    except ImportError:
        print("psutil is required. Install it with:  pip install psutil", file=sys.stderr)
        sys.exit(1)
    main()
