#!/usr/bin/env python3
"""Render the Microcassette start/stop cues (DESIGN.md, "Sound") to WAV.

A dictaphone thumb slide: a short friction sweep, then a detent click. This is
the same synthesis as the design prototype's Web Audio `CUES['micro-*']`, done
offline so the files are reproducible: tweak a number here and re-run.

    python3 scripts/gen_microcassette_sounds.py

Writes src-tauri/resources/microcassette_{start,stop}.wav (48 kHz, 16-bit,
stereo, peak normalized to PEAK_DBFS).
"""

import math
import wave
from pathlib import Path

import numpy as np

SR = 48_000
PEAK_DBFS = -6.0  # about 6 dB under system alerts
SEED = 7  # fixed, so the noise (and the files) are identical on every run
OUT = Path(__file__).resolve().parent.parent / "src-tauri" / "resources"

rng = np.random.default_rng(SEED)


def bandpass(signal, centers, q):
    """RBJ constant-peak band-pass biquad; `centers` may vary per sample."""
    out = np.zeros_like(signal)
    x1 = x2 = y1 = y2 = 0.0
    for i, x in enumerate(signal):
        w0 = 2 * math.pi * centers[i] / SR
        alpha = math.sin(w0) / (2 * q)
        a0 = 1 + alpha
        b0, b2 = alpha / a0, -alpha / a0
        a1, a2 = -2 * math.cos(w0) / a0, (1 - alpha) / a0
        y = b0 * x + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, x, y1, y
        out[i] = y
    return out


def place(buf, at, part):
    start = int(at * SR)
    buf[start : start + len(part)] += part[: max(0, len(buf) - start)]


def slide(buf, at, f_from, f_to, length, gain):
    """Friction: band-passed noise sweeping f_from -> f_to, triangle envelope."""
    n = int(length * SR)
    t = np.arange(n) / SR
    centers = f_from * (f_to / f_from) ** (t / length)
    env = np.interp(t, [0, length * 0.5, length], [0, gain, 0])
    place(buf, at, bandpass(rng.uniform(-1, 1, n), centers, 2.2) * env)


def tick(buf, at, band, gain, length, q):
    """Detent contact: a band-passed noise burst with an exponential decay."""
    n = int((length + 0.004) * SR)
    t = np.arange(n) / SR
    env = gain * (0.0001 / gain) ** np.minimum(t / length, 1)
    place(buf, at, bandpass(rng.uniform(-1, 1, n), np.full(n, band), q) * env)


def thump(buf, at, freq, gain, length):
    """Body: a sine that drops from 1.7x to its pitch, 2ms attack, exp decay."""
    n = int(length * SR)
    t = np.arange(n) / SR
    f = np.where(t < length * 0.35, freq * 1.7 ** (1 - t / (length * 0.35)), freq)
    phase = 2 * math.pi * np.cumsum(f) / SR
    env = np.minimum(t / 0.002, 1) * (0.0001 / gain) ** (t / length) * gain
    place(buf, at, np.sin(phase) * env)


def render(name, build):
    buf = np.zeros(int(0.14 * SR))
    build(buf)
    tail = int(0.004 * SR)  # 4ms fade so nothing ends on a click
    buf[-tail:] *= np.linspace(1, 0, tail)
    buf *= 10 ** (PEAK_DBFS / 20) / np.abs(buf).max()
    pcm = (np.clip(buf, -1, 1) * 32767).astype("<i2")
    stereo = np.repeat(pcm[:, None], 2, axis=1)
    with wave.open(str(OUT / name), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(stereo.tobytes())
    print(f"wrote {OUT / name} ({len(buf) / SR * 1000:.0f} ms)")


def start(buf):
    slide(buf, 0.0, 1500, 3600, 0.040, 0.16)
    tick(buf, 0.038, 4300, 0.42, 0.003, 2)
    thump(buf, 0.038, 230, 0.20, 0.022)


def stop(buf):
    slide(buf, 0.0, 3600, 1400, 0.045, 0.15)
    tick(buf, 0.043, 3000, 0.40, 0.003, 2)
    thump(buf, 0.043, 190, 0.20, 0.024)


if __name__ == "__main__":
    render("microcassette_start.wav", start)
    render("microcassette_stop.wav", stop)
