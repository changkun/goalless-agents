"""End-to-end integration test using a PTY.

Drives reaction_diffusion.py with a pseudo-terminal, sends a sequence of
keys (switch presets, toggle pause, reseed, adjust speed, quit), and
verifies the program:
  - renders at least several frames
  - responds to input (HUD reflects preset + pause state)
  - cleanly restores the terminal on exit (alt-screen off, cursor visible)
"""
import os, pty, select, time, sys, re, signal

script = "/workspace/reaction_diffusion.py"

def run():
    pid, fd = pty.fork()
    if pid == 0:
        # child
        os.execvp("python3", ["python3", script, "spots"])
    # parent
    # Emulate a 80x30 terminal.
    import fcntl, termios, struct
    fcntl.ioctl(fd, termios.TIOCSWINSZ, struct.pack("HHHH", 30, 80, 0, 0))

    collected = bytearray()
    frames_after = {}
    script_steps = [
        (0.6, None,  "startup"),
        (0.1, b"n",  "next preset"),
        (0.6, None,  "settle"),
        (0.1, b"4",  "jump preset 4"),
        (0.5, None,  "settle"),
        (0.1, b" ",  "pause"),
        (0.3, None,  "paused idle"),
        (0.1, b" ",  "unpause"),
        (0.1, b"+",  "speed up"),
        (0.1, b"r",  "reseed"),
        (0.4, None,  "final"),
        (0.0, b"q",  "quit"),
    ]

    deadline = time.time() + 4.0
    for wait, key, label in script_steps:
        t_end = time.time() + wait
        while time.time() < t_end and time.time() < deadline:
            r, _, _ = select.select([fd], [], [], 0.05)
            if r:
                try:
                    chunk = os.read(fd, 65536)
                except OSError:
                    chunk = b""
                if not chunk:
                    break
                collected.extend(chunk)
        if key is not None:
            os.write(fd, key)
        frames_after[label] = len(collected)

    # wait for exit
    t_end = time.time() + 2.0
    while time.time() < t_end:
        r, _, _ = select.select([fd], [], [], 0.05)
        if r:
            try:
                chunk = os.read(fd, 65536)
                if not chunk: break
                collected.extend(chunk)
            except OSError:
                break
        try:
            waited, status = os.waitpid(pid, os.WNOHANG)
            if waited == pid:
                break
        except ChildProcessError:
            break

    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass

    data = bytes(collected)

    # --- assertions ---
    # Alt screen entered and exited.
    assert b"\x1b[?1049h" in data, "did not enter alt screen"
    assert b"\x1b[?1049l" in data, "did not exit alt screen"
    assert b"\x1b[?25l"   in data, "did not hide cursor"
    assert b"\x1b[?25h"   in data, "did not restore cursor"

    # Many half-blocks rendered.
    hb = data.count("\u2580".encode())
    assert hb > 500, f"too few half-blocks rendered: {hb}"

    # HUD shows several distinct preset names over the run.
    presets_seen = set()
    for name in (b"coral", b"spots", b"mitosis", b"stripes", b"waves",
                 b"zebra", b"pulsate", b"chaos"):
        if name in data:
            presets_seen.add(name.decode())
    assert len(presets_seen) >= 3, f"expected several presets, saw {presets_seen}"

    # HUD reflects pause state at some point.
    assert b"PAUSED" in data, "pause HUD never shown"

    # Multiple frames drawn (cursor-home repeats).
    home_count = data.count(b"\x1b[H")
    assert home_count > 10, f"only {home_count} frames drawn"

    print(f"frames drawn (cursor-home count): {home_count}")
    print(f"half-blocks: {hb}")
    print(f"presets seen in HUD: {sorted(presets_seen)}")
    print(f"output size: {len(data)} bytes")
    print("RUN TEST OK")

run()
