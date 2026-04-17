"""Headless smoke test: step the simulator, confirm values stay in range,
check the render output doesn't explode."""
import sys, time
sys.path.insert(0, "/workspace")
from reaction_diffusion import Field, render, PRESETS

# Small grid so the test runs quickly.
f = Field(60, 40)
f.seed("coral")
F, k = PRESETS[0][1], PRESETS[0][2]

t0 = time.perf_counter()
for i in range(50):
    f.step(F, k)
t1 = time.perf_counter()

u_min = min(f.u); u_max = max(f.u)
v_min = min(f.v); v_max = max(f.v)
print(f"after 50 steps on 60x40: {t1 - t0:.3f}s total, "
      f"{(t1 - t0) / 50 * 1000:.2f} ms/step")
print(f"U range: [{u_min:.4f}, {u_max:.4f}]")
print(f"V range: [{v_min:.4f}, {v_max:.4f}]")

# Values must be finite and bounded.
assert all(0.0 <= u <= 1.2 for u in f.u), "U out of range"
assert all(-0.1 <= v <= 0.6 for v in f.v), "V out of range"
assert v_max > 0.05, "V did not develop any structure"

# Render should produce non-empty, ANSI-laden output.
buf = []
out = render(f, buf)
assert "\x1b[" in out and "\u2580" in out
print(f"render OK: {len(out)} bytes")

# Also verify each preset seeds without crashing.
for name, Fp, kp in PRESETS:
    g = Field(40, 30)
    g.seed(name)
    for _ in range(5):
        g.step(Fp, kp)
    assert all(0.0 <= u <= 1.2 for u in g.u), f"{name}: U blew up"
    print(f"  preset {name:<8} seeds + steps cleanly")
print("SMOKE OK")
