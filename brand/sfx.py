# Synthesised sound layer (whoosh / chime / shimmer). Only ADDED on top of the original voice.
import numpy as np, wave

SR = 48000
LEVEL = {"whoosh": -27.0, "chime": -25.0, "shimmer": -29.0}     # peak dBFS of each sound


def _whoosh(rng):
    n = int(0.42 * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n)
    # sweep a resonant band from low to high: cheap state-variable filter
    f = 300 + 2600 * (t / t[-1]) ** 1.6
    lp = bp = 0.0; out = np.empty(n)
    for i in range(n):
        F = 2 * np.sin(np.pi * f[i] / SR); q = 0.35
        hp = x[i] - lp - q * bp; bp += F * hp; lp += F * bp; out[i] = bp
    env = np.sin(np.pi * np.clip(t / t[-1], 0, 1)) ** 2.2
    return out * env


def _chime(rng):
    n = int(1.1 * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for f, a, d in [(1568, 1.0, 0.35), (2349, 0.55, 0.25), (3136, 0.35, 0.18), (4699, 0.18, 0.12)]:
        y += a * np.sin(2 * np.pi * f * t) * np.exp(-t / d)
    return y * np.minimum(1, t / 0.004)


def _shimmer(rng):
    n = int(1.4 * SR); t = np.arange(n) / SR
    y = np.zeros(n)
    for k in range(9):
        t0 = 0.08 * k + rng.uniform(0, 0.03); f = rng.uniform(2600, 5200)
        m = t >= t0; tt = t[m] - t0
        y[m] += 0.6 * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.22) * np.minimum(1, tt / 0.003)
    return y


GEN = {"whoosh": _whoosh, "chime": _chime, "shimmer": _shimmer}


def render_layer(events, dur, path):
    rng = np.random.default_rng(7)
    out = np.zeros((int(dur * SR) + SR, 2))
    for name, t in events:
        s = GEN[name](rng); s = s / (np.abs(s).max() + 1e-9) * 10 ** (LEVEL[name] / 20)
        st = int(max(0, t) * SR); e = min(len(out), st + len(s))
        out[st:e, 0] += s[:e - st]; out[st:e, 1] += s[:e - st]
    out = out[:int(dur * SR)]
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(out, -1, 1) * 32767).astype(np.int16).tobytes())
