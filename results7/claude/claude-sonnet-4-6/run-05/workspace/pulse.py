#!/usr/bin/env python3
"""pulse — real-time Linux system monitor with ASCII charts. Zero dependencies."""

import os
import sys
import time
import signal
import shutil
import collections

REFRESH = 1.0
HIST_LEN = 60  # seconds of history

# ── terminal helpers ──────────────────────────────────────────────────────────

ESC = "\033"
HIDE_CURSOR = f"{ESC}[?25l"
SHOW_CURSOR = f"{ESC}[?25h"
CLEAR_SCREEN = f"{ESC}[2J{ESC}[H"
RESET = f"{ESC}[0m"
BOLD = f"{ESC}[1m"

def color(r, g, b):
    return f"{ESC}[38;2;{r};{g};{b}m"

def bg(r, g, b):
    return f"{ESC}[48;2;{r};{g};{b}m"

# palette
C_TITLE  = color(120, 200, 255)
C_LABEL  = color(180, 180, 180)
C_VALUE  = color(255, 255, 255)
C_LOW    = color(80,  220, 120)
C_MID    = color(255, 200,  60)
C_HIGH   = color(255,  80,  80)
C_DIM    = color(90,  90,  90)
C_BORDER = color(60,  80, 100)

def heat(pct):
    """Color based on percentage."""
    if pct < 60:
        return C_LOW
    if pct < 85:
        return C_MID
    return C_HIGH

def move(row, col):
    return f"{ESC}[{row};{col}H"

# ── /proc readers ─────────────────────────────────────────────────────────────

def _read(path):
    try:
        with open(path) as f:
            return f.read()
    except OSError:
        return ""

_prev_cpu = None

def cpu_percent():
    global _prev_cpu
    data = _read("/proc/stat")
    line = next(l for l in data.splitlines() if l.startswith("cpu "))
    vals = list(map(int, line.split()[1:]))
    idle = vals[3] + vals[4]          # idle + iowait
    total = sum(vals)
    if _prev_cpu is None:
        _prev_cpu = (total, idle)
        return 0.0
    dt = total - _prev_cpu[0]
    di = idle  - _prev_cpu[1]
    _prev_cpu = (total, idle)
    return 100.0 * (1 - di / dt) if dt else 0.0

def per_core_pct():
    global _prev_cores
    data   = _read("/proc/stat")
    lines  = [l for l in data.splitlines() if l.startswith("cpu") and l[3].isdigit()]
    result = []
    prev   = getattr(per_core_pct, "_prev", {})
    nxt    = {}
    for line in lines:
        parts = line.split()
        name  = parts[0]
        vals  = list(map(int, parts[1:]))
        idle  = vals[3] + vals[4]
        total = sum(vals)
        nxt[name] = (total, idle)
        if name in prev:
            dt = total - prev[name][0]
            di = idle  - prev[name][1]
            result.append(100.0 * (1 - di / dt) if dt else 0.0)
        else:
            result.append(0.0)
    per_core_pct._prev = nxt
    return result

def mem_info():
    data = _read("/proc/meminfo")
    kv   = {}
    for line in data.splitlines():
        parts = line.split()
        if len(parts) >= 2:
            kv[parts[0].rstrip(":")] = int(parts[1])
    total   = kv.get("MemTotal", 1)
    free    = kv.get("MemFree",  0)
    buffers = kv.get("Buffers",  0)
    cached  = kv.get("Cached",   0) + kv.get("SReclaimable", 0)
    swap_t  = kv.get("SwapTotal", 0)
    swap_f  = kv.get("SwapFree",  0)
    used    = total - free - buffers - cached
    return {
        "total":   total,
        "used":    used,
        "cached":  cached + buffers,
        "pct":     100.0 * used / total if total else 0,
        "swap_t":  swap_t,
        "swap_u":  swap_t - swap_f,
        "swap_pct": 100.0 * (swap_t - swap_f) / swap_t if swap_t else 0,
    }

_prev_net = None

def net_io():
    global _prev_net
    data  = _read("/proc/net/dev")
    rx = tx = 0
    for line in data.splitlines()[2:]:
        parts = line.split()
        if len(parts) < 10 or parts[0].startswith("lo"):
            rx += int(parts[1])
            tx += int(parts[9])
    if _prev_net is None:
        _prev_net = (rx, tx, time.time())
        return 0.0, 0.0
    dt = time.time() - _prev_net[2]
    drx = (rx - _prev_net[0]) / dt if dt else 0
    dtx = (tx - _prev_net[1]) / dt if dt else 0
    _prev_net = (rx, tx, time.time())
    return drx, dtx

_prev_disk = None

def disk_io():
    global _prev_disk
    data = _read("/proc/diskstats")
    r = w = 0
    for line in data.splitlines():
        parts = line.split()
        if len(parts) < 14:
            continue
        name = parts[2]
        if name.startswith(("sd", "vd", "hd", "nvme")) and not name[-1].isdigit():
            r += int(parts[5])  # sectors read
            w += int(parts[9])  # sectors written
    if _prev_disk is None:
        _prev_disk = (r, w, time.time())
        return 0.0, 0.0
    dt   = time.time() - _prev_disk[2]
    dr   = (r - _prev_disk[0]) * 512 / dt if dt else 0
    dw   = (w - _prev_disk[1]) * 512 / dt if dt else 0
    _prev_disk = (r, w, time.time())
    return dr, dw

def load_avg():
    return list(map(float, _read("/proc/loadavg").split()[:3]))

def uptime_str():
    secs = float(_read("/proc/uptime").split()[0])
    h, r = divmod(int(secs), 3600)
    m, s = divmod(r, 60)
    if h >= 24:
        d, h = divmod(h, 24)
        return f"{d}d {h:02d}h {m:02d}m"
    return f"{h:02d}h {m:02d}m {s:02d}s"

def process_count():
    try:
        return len([e for e in os.listdir("/proc") if e.isdigit()])
    except OSError:
        return 0

def hostname():
    return _read("/proc/sys/kernel/hostname").strip()

# ── formatting helpers ────────────────────────────────────────────────────────

UNITS = ["B", "K", "M", "G", "T"]

def fmt_bytes(b, per_sec=False):
    v = float(b)
    u = 0
    while v >= 1024 and u < len(UNITS) - 1:
        v /= 1024
        u += 1
    suffix = "/s" if per_sec else ""
    return f"{v:6.1f}{UNITS[u]}{suffix}"

def fmt_mem(kb):
    mb = kb / 1024
    if mb >= 1024:
        return f"{mb/1024:.2f}G"
    return f"{mb:.0f}M"

# ── ASCII chart renderers ─────────────────────────────────────────────────────

SPARK_CHARS = " ▁▂▃▄▅▆▇█"

def sparkline(history, width, max_val=100.0):
    """Render a sparkline from a deque of floats."""
    samples = list(history)[-width:]
    if not samples:
        return C_DIM + "─" * width + RESET
    out = []
    for v in samples:
        idx = int((v / max_val) * (len(SPARK_CHARS) - 1))
        idx = max(0, min(len(SPARK_CHARS) - 1, idx))
        c   = heat(v) if max_val == 100.0 else C_LOW
        out.append(c + SPARK_CHARS[idx])
    # pad left with dim dashes
    pad = width - len(out)
    result = C_DIM + "─" * pad + RESET + "".join(out) + RESET
    return result

def bar(pct, width=20):
    filled = int(pct / 100 * width)
    filled = max(0, min(width, filled))
    empty  = width - filled
    h      = heat(pct)
    return h + "█" * filled + C_DIM + "░" * empty + RESET

def mini_bar(pct, width=8):
    filled = int(pct / 100 * width)
    filled = max(0, min(width, filled))
    return heat(pct) + "█" * filled + C_DIM + "░" * (width - filled) + RESET

# ── layout renderer ───────────────────────────────────────────────────────────

def render(state, term_w, term_h):
    lines = []

    def ln(s=""):
        lines.append(s)

    cpu   = state["cpu"]
    mem   = state["mem"]
    drx, dtx   = state["net"]
    ddisk_r, ddisk_w = state["disk"]
    load  = state["load"]
    cores = state["cores"]
    cpu_h = state["cpu_hist"]
    mem_h = state["mem_hist"]
    net_h = state["net_hist"]

    # ── header ──
    host  = hostname()
    up    = uptime_str()
    procs = process_count()
    now   = time.strftime("%H:%M:%S")

    header_left  = f"{BOLD}{C_TITLE}⚡ pulse{RESET}  {C_LABEL}{host}{RESET}"
    header_right = f"{C_LABEL}up {up}  {procs} procs  {now}{RESET}"
    pad = term_w - 26 - len(host) - len(up) - len(str(procs)) - len(now)
    ln(header_left + " " * max(1, pad) + header_right)
    ln(C_BORDER + "─" * term_w + RESET)

    spark_w = max(10, term_w - 42)

    # ── CPU ──
    ln(f"{BOLD}{C_TITLE}CPU{RESET}  {bar(cpu, 22)}  {heat(cpu)}{cpu:5.1f}%{RESET}  "
       f"load {C_VALUE}{load[0]:.2f} {load[1]:.2f} {load[2]:.2f}{RESET}")
    ln(f"     {sparkline(cpu_h, spark_w)}")

    # per-core row (compact)
    if cores:
        n = min(len(cores), (term_w - 6) // 12)
        core_str = "  ".join(
            f"c{i} {mini_bar(cores[i], 6)}{heat(cores[i])}{cores[i]:4.0f}%{RESET}"
            for i in range(n)
        )
        ln(f"     {C_LABEL}{core_str}")

    ln()

    # ── Memory ──
    mpct  = mem["pct"]
    ln(f"{BOLD}{C_TITLE}MEM{RESET}  {bar(mpct, 22)}  {heat(mpct)}{mpct:5.1f}%{RESET}  "
       f"{C_VALUE}{fmt_mem(mem['used'])}{C_LABEL}/{fmt_mem(mem['total'])}{RESET}  "
       f"{C_DIM}cache {fmt_mem(mem['cached'])}{RESET}")
    ln(f"     {sparkline(mem_h, spark_w)}")

    # swap
    if mem["swap_t"]:
        sp = mem["swap_pct"]
        ln(f"     {C_LABEL}swap {bar(sp, 12)}  {heat(sp)}{sp:4.1f}%{RESET}  "
           f"{C_DIM}{fmt_mem(mem['swap_u'])}/{fmt_mem(mem['swap_t'])}{RESET}")
    ln()

    # ── Network ──
    net_max = max(1, max((x for x in net_h if x), default=1))
    ln(f"{BOLD}{C_TITLE}NET{RESET}  "
       f"{C_LOW}▲ {fmt_bytes(dtx, True)}{RESET}  "
       f"{C_MID}▼ {fmt_bytes(drx, True)}{RESET}")
    ln(f"     {sparkline(net_h, spark_w, max_val=net_max)}")
    ln()

    # ── Disk ──
    if ddisk_r + ddisk_w > 0:
        ln(f"{BOLD}{C_TITLE}DISK{RESET} "
           f"{C_LOW}R {fmt_bytes(ddisk_r, True)}{RESET}  "
           f"{C_MID}W {fmt_bytes(ddisk_w, True)}{RESET}")
        ln()

    # ── footer ──
    ln(C_BORDER + "─" * term_w + RESET)
    ln(f"{C_DIM}  q quit   Ctrl-C quit   refresh {REFRESH:.0f}s{RESET}")

    return lines

# ── main loop ────────────────────────────────────────────────────────────────

def main():
    cpu_hist = collections.deque(maxlen=HIST_LEN)
    mem_hist = collections.deque(maxlen=HIST_LEN)
    net_hist = collections.deque(maxlen=HIST_LEN)

    running = True

    def stop(*_):
        nonlocal running
        running = False

    signal.signal(signal.SIGINT,  stop)
    signal.signal(signal.SIGTERM, stop)

    sys.stdout.write(HIDE_CURSOR)
    sys.stdout.flush()

    # warm-up reads so first diff is meaningful
    cpu_percent()
    per_core_pct()
    net_io()
    disk_io()
    time.sleep(0.2)

    try:
        while running:
            tw, th = shutil.get_terminal_size((80, 24))

            cpu   = cpu_percent()
            mem   = mem_info()
            cores = per_core_pct()
            drx, dtx  = net_io()
            ddisk = disk_io()
            load  = load_avg()

            cpu_hist.append(cpu)
            mem_hist.append(mem["pct"])
            net_hist.append(drx + dtx)

            state = {
                "cpu":      cpu,
                "mem":      mem,
                "cores":    cores,
                "net":      (drx, dtx),
                "disk":     ddisk,
                "load":     load,
                "cpu_hist": cpu_hist,
                "mem_hist": mem_hist,
                "net_hist": net_hist,
            }

            lines = render(state, tw, th)

            out = [CLEAR_SCREEN]
            for line in lines[:th - 1]:
                out.append(line + "\n")

            sys.stdout.write("".join(out))
            sys.stdout.flush()

            # non-blocking keyboard check (best-effort)
            try:
                import select, tty, termios
                old = termios.tcgetattr(sys.stdin.fileno())
                try:
                    tty.setcbreak(sys.stdin.fileno())
                    r, _, _ = select.select([sys.stdin], [], [], REFRESH)
                    if r:
                        ch = sys.stdin.read(1)
                        if ch in ("q", "Q"):
                            running = False
                finally:
                    termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
            except Exception:
                time.sleep(REFRESH)

    finally:
        sys.stdout.write(SHOW_CURSOR + CLEAR_SCREEN)
        sys.stdout.flush()
        print("pulse stopped.")


if __name__ == "__main__":
    main()
