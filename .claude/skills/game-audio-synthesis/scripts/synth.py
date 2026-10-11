"""Tiny pure-Python synthesizer for game sound effects and music. Standard library only (no numpy).

A "sound" is a plain list of floats in [-1, 1] sampled at SR. Build sounds by generating (tone / noise), shaping
(envelopes, filters, drive) and combining (mix), then call finish() and write_wav().
"""
import math, os, random, struct, wave

SR = 44100
TAU = 2 * math.pi


def frames(sec): return max(1, int(round(sec * SR)))


# ---------------------------------------------------------------- generators
def _wave(shape, ph, duty):
    if shape == 'sine': return math.sin(TAU * ph)
    if shape == 'square': return 1.0 if ph < duty else -1.0
    if shape == 'saw': return 2.0 * ph - 1.0
    if shape == 'tri': return 4.0 * abs(ph - 0.5) - 1.0
    raise ValueError(shape)


def tone(f0, dur, f1=None, shape='sine', duty=0.5, vibrato=(0.0, 0.0)):
    """Oscillator. Pitch glides exponentially from f0 to f1 over dur. vibrato = (rate Hz, depth as fraction)."""
    f1 = f0 if f1 is None else f1
    n = frames(dur); out = [0.0] * n; ph = 0.0; vr, vd = vibrato
    for i in range(n):
        f = f0 * (f1 / f0) ** (i / n)
        if vr: f *= 1.0 + vd * math.sin(TAU * vr * i / SR)
        ph = (ph + f / SR) % 1.0
        out[i] = _wave(shape, ph, duty)
    return out


def noise(dur, rng=None):
    rng = rng or random
    return [rng.uniform(-1.0, 1.0) for _ in range(frames(dur))]


# ---------------------------------------------------------------- filters
def lowpass(x, c0, c1=None, poles=2):
    """One-pole low-pass cascaded `poles` times (12 dB/oct each pair). Cutoff glides c0 -> c1 if given."""
    c1 = c0 if c1 is None else c1; n = len(x); y = list(x)
    for _ in range(poles):
        s = 0.0
        for i in range(n):
            fc = c0 * (c1 / c0) ** (i / n)
            a = 1.0 - math.exp(-TAU * fc / SR)
            s += a * (y[i] - s); y[i] = s
    return y


def highpass(x, c0, c1=None, poles=2):
    lp = lowpass(x, c0, c1, poles)
    return [a - b for a, b in zip(x, lp)]


def bandpass(x, lo, hi, poles=2):
    return highpass(lowpass(x, hi, poles=poles), lo, poles=poles)


# ---------------------------------------------------------------- shaping
def env_exp(x, tau, attack=0.003):
    """Fast attack then exponential decay (tau = seconds for the level to fall to 1/e)."""
    return [s * min(1.0, (i / SR) / attack) * math.exp(-(i / SR) / tau) for i, s in enumerate(x)]


def env_hump(x, power=2.0, peak=0.5):
    """Rise to a peak at `peak` (0..1 of the length) and fall again; good for whooshes."""
    n = len(x); out = [0.0] * n
    for i in range(n):
        u = i / n
        v = (u / peak) if u < peak else ((1.0 - u) / (1.0 - peak))
        out[i] = x[i] * math.sin(0.5 * math.pi * max(0.0, v)) ** power
    return out


def drive(x, amount=3.0):
    """Soft clipping (tanh): adds grit/growl. amount 1 = mild, 6 = heavy."""
    k = math.tanh(amount)
    return [math.tanh(amount * s) / k for s in x]


def crush(x, bits=6, hold=4):
    """Lo-fi: reduce bit depth and sample rate (hold = repeat each sample this many times)."""
    q = 2 ** (bits - 1); out = list(x)
    for i in range(0, len(x), hold):
        v = round(x[i] * q) / q
        for j in range(i, min(i + hold, len(x))): out[j] = v
    return out


def scale(x, g): return [s * g for s in x]


def mix(parts, length=None):
    """parts: list of (samples, gain, delay_seconds). Returns the sum, as long as the longest part."""
    ends = [frames(d) + len(s) for s, g, d in parts]
    out = [0.0] * (length or max(ends))
    for s, g, d in parts:
        o = frames(d) if d else 0
        for i, v in enumerate(s):
            if o + i < len(out): out[o + i] += v * g
    return out


def finish(x, peak=0.9, fade_in=0.002, fade_out=0.012):
    """Normalize to `peak` and apply tiny fades so the file starts/ends at zero (no clicks)."""
    m = max((abs(s) for s in x), default=0.0) or 1.0
    x = [s * peak / m for s in x]; n = len(x)
    fi, fo = min(n, frames(fade_in)), min(n, frames(fade_out))
    for i in range(fi): x[i] *= i / fi
    for i in range(fo): x[n - 1 - i] *= i / fo
    return x


# ---------------------------------------------------------------- notes / sequencing (used for music)
def midi_hz(m): return 440.0 * 2 ** ((m - 69) / 12.0)


def note(midi, dur, shape='square', duty=0.5, tau=None, vibrato=(0.0, 0.0)):
    """One note with a plucky decay (tau defaults to ~ the note length)."""
    return env_exp(tone(midi_hz(midi), dur, shape=shape, duty=duty, vibrato=vibrato), tau or dur * 0.7, attack=0.004)


def sequence(notes, bpm, steps_per_beat=2, length_steps=None, **note_kw):
    """notes: list of (step, midi, length_in_steps). Returns the rendered line (list of samples)."""
    step = 60.0 / bpm / steps_per_beat
    total = length_steps or max(s + l for s, m, l in notes)
    parts = [(note(m, l * step, **note_kw), 1.0, s * step) for s, m, l in notes]
    return mix(parts, length=frames(total * step))


# ---------------------------------------------------------------- output
def write_wav(path, x, sr=SR):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with wave.open(path, 'wb') as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes(b''.join(struct.pack('<h', int(max(-1.0, min(1.0, s)) * 32767)) for s in x))
