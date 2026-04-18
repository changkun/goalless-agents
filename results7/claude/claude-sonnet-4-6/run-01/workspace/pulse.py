#!/usr/bin/env python3
"""pulse — live system health monitor using only /proc and stdlib."""

import os
import sys
import time
import signal
import shutil
from collections import deque

HISTORY = 30
INTERVAL = 1.0

RESET  = "\033[0m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RED    = "\033[31m"
GREEN  = "\033[32m"
YELLOW = "\033[33m"
BLUE   = "\033[34m"
CYAN   = "\033[36m"
WHITE  = "\033[37m"
BG_DARK = "\033[48;5;234m"
HIDE_CURSOR = "\033[?25l"
SHOW_CURSOR = "\033[?25h"
CLEAR_SCREEN = "\033[2J\033[H"

SPARKS = " ▁▂▃▄▅▆▇█"


def sparkline(values, width, lo=0.0, hi=100.0):
    """Render a sparkline from a sequence of floats."""
    out = []
    for v in list(values)[-width:]:
        norm = (v - lo) / (hi - lo) if hi > lo else 0.0
        idx = int(norm * (len(SPARKS) - 1))
        idx = max(0, min(len(SPARKS) - 1, idx))
        out.append(SPARKS[idx])
    return "".join(out).ljust(width)


def color_pct(pct):
    if pct >= 90:
        return RED
    if pct >= 70:
        return YELLOW
    return GREEN


def read_proc(path):
    with open(path) as f:
        return f.read()


# ── CPU ──────────────────────────────────────────────────────────────────────

def parse_cpu_stats():
    lines = read_proc("/proc/stat").splitlines()
    cpus = {}
    for line in lines:
        if line.startswith("cpu"):
            parts = line.split()
            name = parts[0]
            vals = list(map(int, parts[1:]))
            idle = vals[3] + (vals[4] if len(vals) > 4 else 0)
            total = sum(vals)
            cpus[name] = (total, idle)
    return cpus


def cpu_percents(prev, curr):
    result = {}
    for name in curr:
        if name not in prev:
            continue
        dt = curr[name][0] - prev[name][0]
        di = curr[name][1] - prev[name][1]
        result[name] = 100.0 * (1.0 - di / dt) if dt > 0 else 0.0
    return result


# ── Memory ───────────────────────────────────────────────────────────────────

def parse_meminfo():
    info = {}
    for line in read_proc("/proc/meminfo").splitlines():
        parts = line.split()
        info[parts[0].rstrip(":")] = int(parts[1])
    total = info.get("MemTotal", 1)
    free  = info.get("MemFree", 0)
    buffers = info.get("Buffers", 0)
    cached  = info.get("Cached", 0) + info.get("SReclaimable", 0) - info.get("Shmem", 0)
    used = total - free - buffers - cached
    swap_total = info.get("SwapTotal", 1)
    swap_free  = info.get("SwapFree", 0)
    return {
        "total": total,
        "used": used,
        "pct": 100.0 * used / total if total > 0 else 0.0,
        "swap_total": swap_total,
        "swap_used": swap_total - swap_free,
        "swap_pct": 100.0 * (swap_total - swap_free) / swap_total if swap_total > 0 else 0.0,
    }


# ── Disk I/O ─────────────────────────────────────────────────────────────────

def parse_diskstats():
    stats = {}
    for line in read_proc("/proc/diskstats").splitlines():
        parts = line.split()
        if len(parts) < 14:
            continue
        name = parts[2]
        # skip partitions (sda1, nvme0n1p1, etc.)
        if any(c.isdigit() for c in name[-1:]) and not name.startswith("nvme"):
            continue
        if name.startswith("loop"):
            continue
        rd_sectors = int(parts[5])
        wr_sectors = int(parts[9])
        stats[name] = (rd_sectors, wr_sectors)
    return stats


def disk_bytes(prev, curr, elapsed):
    rd = wr = 0
    for name in curr:
        if name not in prev:
            continue
        drd = curr[name][0] - prev[name][0]
        dwr = curr[name][1] - prev[name][1]
        rd += drd * 512
        wr += dwr * 512
    scale = 1.0 / elapsed if elapsed > 0 else 1.0
    return rd * scale, wr * scale


# ── Network ──────────────────────────────────────────────────────────────────

def parse_netdev():
    stats = {}
    lines = read_proc("/proc/net/dev").splitlines()[2:]
    for line in lines:
        parts = line.split()
        name = parts[0].rstrip(":")
        if name == "lo":
            continue
        rx = int(parts[1])
        tx = int(parts[9])
        stats[name] = (rx, tx)
    return stats


def net_bytes(prev, curr, elapsed):
    rx = tx = 0
    for name in curr:
        if name not in prev:
            continue
        rx += curr[name][0] - prev[name][0]
        tx += curr[name][1] - prev[name][1]
    scale = 1.0 / elapsed if elapsed > 0 else 1.0
    return rx * scale, tx * scale


# ── Load / Uptime ────────────────────────────────────────────────────────────

def parse_loadavg():
    parts = read_proc("/proc/loadavg").split()
    return float(parts[0]), float(parts[1]), float(parts[2])


def parse_uptime():
    secs = float(read_proc("/proc/uptime").split()[0])
    d = int(secs // 86400)
    h = int((secs % 86400) // 3600)
    m = int((secs % 3600) // 60)
    s = int(secs % 60)
    if d:
        return f"{d}d {h:02d}:{m:02d}:{s:02d}"
    return f"{h:02d}:{m:02d}:{s:02d}"


# ── Formatting helpers ────────────────────────────────────────────────────────

def fmt_bytes(n, suffix="B/s"):
    for unit in ("", "K", "M", "G", "T"):
        if abs(n) < 1024.0:
            return f"{n:6.1f} {unit}{suffix}"
        n /= 1024.0
    return f"{n:6.1f} P{suffix}"


def fmt_mem(kb):
    mb = kb / 1024.0
    if mb >= 1024:
        return f"{mb/1024.0:.1f} GB"
    return f"{mb:.0f} MB"


def bar(pct, width=20):
    filled = int(pct / 100.0 * width)
    filled = max(0, min(width, filled))
    c = color_pct(pct)
    return f"{c}{'█' * filled}{DIM}{'░' * (width - filled)}{RESET}"


# ── Rendering ─────────────────────────────────────────────────────────────────

def render(state, cols):
    lines = []

    def add(text=""):
        lines.append(text)

    cpu_percents_map = state["cpu_percents"]
    mem = state["mem"]
    load = state["load"]
    disk_rd, disk_wr = state["disk_rates"]
    net_rx, net_tx = state["net_rates"]

    total_cpu = cpu_percents_map.get("cpu", 0.0)
    core_cpus = sorted(
        [(k, v) for k, v in cpu_percents_map.items() if k != "cpu"],
        key=lambda x: int(x[0][3:]) if x[0][3:].isdigit() else 0,
    )

    W = min(cols, 100)

    # ── Header ───────────────────────────────────────────────────────────────
    now = time.strftime("%Y-%m-%d %H:%M:%S")
    up  = parse_uptime()
    l1, l5, l15 = load
    header = f"{BOLD}{CYAN}pulse{RESET}  {DIM}{now}  up {up}{RESET}"
    load_str = f"load {YELLOW}{l1:.2f}{RESET} {l5:.2f} {l15:.2f}"
    pad = W - len(f"pulse  {now}  up {up}") - len(f"load {l1:.2f} {l5:.2f} {l15:.2f}") - 2
    add(header + " " * max(0, pad) + load_str)
    add(f"{DIM}{'─' * W}{RESET}")

    # ── CPU ──────────────────────────────────────────────────────────────────
    add(f"{BOLD}CPU{RESET}")
    c = color_pct(total_cpu)
    spark = state["cpu_history"]
    add(f"  Total   {bar(total_cpu, 24)} {c}{total_cpu:5.1f}%{RESET}  {DIM}{sparkline(spark, HISTORY)}{RESET}")

    # Per-core grid (2 columns)
    per_row = 2
    for i in range(0, len(core_cpus), per_row):
        row_parts = []
        for name, pct in core_cpus[i:i+per_row]:
            num = name[3:]
            c2 = color_pct(pct)
            row_parts.append(f"  core{num:<2}  {bar(pct, 12)} {c2}{pct:5.1f}%{RESET}")
        add("  ".join(row_parts))

    add()

    # ── Memory ───────────────────────────────────────────────────────────────
    add(f"{BOLD}Memory{RESET}")
    mp = mem["pct"]
    cm = color_pct(mp)
    mem_spark = state["mem_history"]
    add(f"  RAM     {bar(mp, 24)} {cm}{mp:5.1f}%{RESET}  {fmt_mem(mem['used'])} / {fmt_mem(mem['total'])}")
    add(f"          {DIM}{sparkline(mem_spark, HISTORY)}{RESET}")
    if mem["swap_total"] > 0:
        sp = mem["swap_pct"]
        cs = color_pct(sp)
        add(f"  Swap    {bar(sp, 24)} {cs}{sp:5.1f}%{RESET}  {fmt_mem(mem['swap_used'])} / {fmt_mem(mem['swap_total'])}")
    add()

    # ── Disk I/O ─────────────────────────────────────────────────────────────
    add(f"{BOLD}Disk I/O{RESET}")
    dr_spark = state["disk_rd_history"]
    dw_spark = state["disk_wr_history"]
    peak_rd = max(state["disk_rd_history"]) if state["disk_rd_history"] else 1
    peak_wr = max(state["disk_wr_history"]) if state["disk_wr_history"] else 1
    add(f"  Read    {GREEN}{fmt_bytes(disk_rd)}{RESET}   {DIM}peak {fmt_bytes(peak_rd)}{RESET}")
    add(f"          {GREEN}{sparkline(dr_spark, HISTORY, lo=0, hi=max(peak_rd,1))}{RESET}")
    add(f"  Write   {YELLOW}{fmt_bytes(disk_wr)}{RESET}   {DIM}peak {fmt_bytes(peak_wr)}{RESET}")
    add(f"          {YELLOW}{sparkline(dw_spark, HISTORY, lo=0, hi=max(peak_wr,1))}{RESET}")
    add()

    # ── Network ──────────────────────────────────────────────────────────────
    add(f"{BOLD}Network{RESET}")
    peak_rx = max(state["net_rx_history"]) if state["net_rx_history"] else 1
    peak_tx = max(state["net_tx_history"]) if state["net_tx_history"] else 1
    add(f"  ↓ RX    {CYAN}{fmt_bytes(net_rx)}{RESET}   {DIM}peak {fmt_bytes(peak_rx)}{RESET}")
    add(f"          {CYAN}{sparkline(state['net_rx_history'], HISTORY, lo=0, hi=max(peak_rx,1))}{RESET}")
    add(f"  ↑ TX    {BLUE}{fmt_bytes(net_tx)}{RESET}   {DIM}peak {fmt_bytes(peak_tx)}{RESET}")
    add(f"          {BLUE}{sparkline(state['net_tx_history'], HISTORY, lo=0, hi=max(peak_tx,1))}{RESET}")

    add()
    add(f"{DIM}q to quit · refreshes every {INTERVAL:.0f}s{RESET}")

    return lines


def move_home():
    sys.stdout.write("\033[H")


def clear_to_eos():
    sys.stdout.write("\033[J")


def main():
    # graceful exit
    running = [True]

    def handle_sig(sig, frame):
        running[0] = False

    signal.signal(signal.SIGINT, handle_sig)
    signal.signal(signal.SIGTERM, handle_sig)

    # initial snapshot
    prev_cpu  = parse_cpu_stats()
    prev_disk = parse_diskstats()
    prev_net  = parse_netdev()
    time.sleep(0.1)

    cpu_history    = deque([0.0] * HISTORY, maxlen=HISTORY)
    mem_history    = deque([0.0] * HISTORY, maxlen=HISTORY)
    disk_rd_history = deque([0.0] * HISTORY, maxlen=HISTORY)
    disk_wr_history = deque([0.0] * HISTORY, maxlen=HISTORY)
    net_rx_history  = deque([0.0] * HISTORY, maxlen=HISTORY)
    net_tx_history  = deque([0.0] * HISTORY, maxlen=HISTORY)

    # hide cursor, switch to alternate screen
    sys.stdout.write("\033[?1049h")  # alt screen
    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.write(CLEAR_SCREEN)
    sys.stdout.flush()

    # non-blocking stdin for 'q' key
    import tty, termios, select
    old_settings = termios.tcgetattr(sys.stdin)
    try:
        tty.setcbreak(sys.stdin.fileno())

        last_tick = time.monotonic()

        while running[0]:
            # check for 'q'
            r, _, _ = select.select([sys.stdin], [], [], 0)
            if r:
                ch = sys.stdin.read(1)
                if ch.lower() == "q":
                    break

            now = time.monotonic()
            elapsed = now - last_tick
            if elapsed < INTERVAL:
                time.sleep(0.05)
                continue
            last_tick = now

            curr_cpu  = parse_cpu_stats()
            curr_disk = parse_diskstats()
            curr_net  = parse_netdev()

            percents  = cpu_percents(prev_cpu, curr_cpu)
            mem       = parse_meminfo()
            rd, wr    = disk_bytes(prev_disk, curr_disk, elapsed)
            rx, tx    = net_bytes(prev_net, curr_net, elapsed)
            load      = parse_loadavg()

            cpu_history.append(percents.get("cpu", 0.0))
            mem_history.append(mem["pct"])
            disk_rd_history.append(rd)
            disk_wr_history.append(wr)
            net_rx_history.append(rx)
            net_tx_history.append(tx)

            state = {
                "cpu_percents":    percents,
                "mem":             mem,
                "disk_rates":      (rd, wr),
                "net_rates":       (rx, tx),
                "load":            load,
                "cpu_history":     cpu_history,
                "mem_history":     mem_history,
                "disk_rd_history": disk_rd_history,
                "disk_wr_history": disk_wr_history,
                "net_rx_history":  net_rx_history,
                "net_tx_history":  net_tx_history,
            }

            cols, _ = shutil.get_terminal_size((80, 24))

            move_home()
            output = "\n".join(render(state, cols))
            sys.stdout.write(output)
            clear_to_eos()
            sys.stdout.flush()

            prev_cpu  = curr_cpu
            prev_disk = curr_disk
            prev_net  = curr_net

    except Exception as e:
        # restore terminal before showing error
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write("\033[?1049l")  # exit alt screen
        sys.stdout.flush()
        print(f"Error: {e}", file=sys.stderr)
        raise
    finally:
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        sys.stdout.write(SHOW_CURSOR)
        sys.stdout.write("\033[?1049l")
        sys.stdout.flush()


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ("-h", "--help"):
        print("usage: pulse.py")
        print()
        print("Live system health monitor — CPU, memory, disk I/O, network.")
        print("Reads /proc directly. No dependencies beyond Python 3 stdlib.")
        print()
        print("  q          quit")
        print("  Ctrl-C     quit")
        sys.exit(0)
    main()
