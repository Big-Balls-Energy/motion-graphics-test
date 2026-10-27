#!/usr/bin/env python3
"""
Banda sonora original para el spot "Meta Ads 2026 · Atlas Path".

Música electrónica corporativa / future tech a 96 BPM, sintetizada desde cero
(sin samples de terceros) y sincronizada con los mismos frames que usa la
animación (src/timeline.json). Genera public/audio/soundtrack.wav (48 kHz, estéreo).

Estructura (1 compás = 2.5 s, 2 compases por escena):
  S1      intro filtrada + impactos del gancho
  S2–S5   groove completo (kick, clap, hats, bajo con sidechain, pad, arpegio)
  S6      breakdown (exclusividad): pad, sub y ticks por cada lugar
  S7      regreso del groove con impacto en el precio
  S8      cierre: impacto en el logotipo y acorde final que se desvanece
"""
import json
import os

import numpy as np
from scipy import signal

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TL = json.load(open(os.path.join(ROOT, "src", "timeline.json")))

SR = 48000
FPS = TL["fps"]
DUR = TL["durationInFrames"] / FPS  # 40.0 s
N = int(round(DUR * SR))
BPM = TL["bpm"]
BEAT = 60.0 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(2026)


def fr(f):
    return f / FPS


def buf():
    return np.zeros((2, N))


def place(dst, x, t, gain=1.0, pan=0.0):
    """Suma la señal x (mono o estéreo) en el instante t con paneo."""
    i = int(round(t * SR))
    if x.ndim == 1:
        l = np.cos((pan + 1) * np.pi / 4)
        r = np.sin((pan + 1) * np.pi / 4)
        x = np.vstack([x * l * np.sqrt(2), x * r * np.sqrt(2)])
    if i >= N:
        return
    if i < 0:
        x = x[:, -i:]
        i = 0
    n = min(x.shape[1], N - i)
    dst[:, i : i + n] += gain * x[:, :n]


def tt(d):
    return np.arange(int(d * SR)) / SR


def env_ad(d, a=0.002, decay=0.2):
    t = tt(d)
    e = np.exp(-t / decay)
    na = max(1, int(a * SR))
    e[:na] *= np.linspace(0, 1, na)
    return e


def lp(x, fc, order=2):
    sos = signal.butter(order, fc, "low", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=-1)


def hp(x, fc, order=2):
    sos = signal.butter(order, fc, "high", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=-1)


def bp(x, lo, hi, order=2):
    sos = signal.butter(order, [lo, hi], "band", fs=SR, output="sos")
    return signal.sosfilt(sos, x, axis=-1)


def saw(freq, t, phase=0.0):
    return 2.0 * ((freq * t + phase) % 1.0) - 1.0


def note(n):
    """Número MIDI a Hz."""
    return 440.0 * 2 ** ((n - 69) / 12)


def sweep_noise(d, f0, f1, width=0.5, seed=0):
    """Ruido con filtro paso banda que barre de f0 a f1 (dominio STFT)."""
    r = np.random.default_rng(seed)
    x = r.standard_normal(int(d * SR))
    f, t, Z = signal.stft(x, SR, nperseg=1024)
    fc = np.geomspace(f0, f1, Z.shape[1])
    lf = np.log2(np.maximum(f, 1))[:, None]
    mask = np.exp(-0.5 * ((lf - np.log2(fc)[None, :]) / width) ** 2)
    _, y = signal.istft(Z * mask, SR, nperseg=1024)
    y = y[: len(x)]
    return y / (np.abs(y).max() + 1e-9)


# ---------------------------------------------------------------- instrumentos
def kick():
    d = 0.55
    t = tt(d)
    f = 45 + 95 * np.exp(-t / 0.045)
    ph = 2 * np.pi * np.cumsum(f) / SR
    body = np.sin(ph) * np.exp(-t / 0.22)
    click = hp(rng.standard_normal(len(t)), 2500) * np.exp(-t / 0.004) * 0.25
    return np.tanh(1.6 * (body + click))


def clap():
    d = 0.35
    t = tt(d)
    n = bp(rng.standard_normal(len(t)), 900, 5000)
    e = np.zeros_like(t)
    for k, o in enumerate([0, 0.011, 0.022]):
        i = int(o * SR)
        e[i:] += np.exp(-(t[: len(t) - i]) / (0.012 if k < 2 else 0.13))
    return n * e * 0.8


def hat(open_=False):
    d = 0.25 if open_ else 0.06
    t = tt(d)
    n = hp(rng.standard_normal(len(t)), 7500, 4)
    return n * np.exp(-t / (0.07 if open_ else 0.012))


def pluck(freq, d=0.32):
    t = tt(d)
    x = 0.6 * saw(freq, t) + 0.4 * np.sign(np.sin(2 * np.pi * freq * 2 * t))
    x = lp(x, 3200)
    return x * env_ad(d, 0.002, 0.09)


def pad_chord(freqs, d, cutoff=1800):
    t = tt(d)
    L = np.zeros_like(t)
    R = np.zeros_like(t)
    for fq in freqs:
        for k, det in enumerate([-0.11, -0.04, 0.0, 0.05, 0.12]):
            ph = rng.random()
            s = saw(fq * 2 ** (det / 12), t, ph)
            if k % 2:
                L += s
            else:
                R += s
            if k == 2:
                L += s * 0.5
                R += s * 0.5
    x = np.vstack([L, R]) / (len(freqs) * 3.5)
    x = lp(x, cutoff, 2)
    a = np.minimum(1, t / 0.35)
    rel = np.minimum(1, (d - t) / 0.4)
    return x * a * np.clip(rel, 0, 1)


def bass_note(freq, d):
    t = tt(d)
    x = saw(freq, t) * 0.7 + np.sin(2 * np.pi * freq * t) * 0.6
    x = lp(x, 520, 2)
    return np.tanh(1.4 * x) * env_ad(d, 0.004, 0.5) * np.clip((d - t) / 0.02, 0, 1)


def impact(big=1.0):
    d = 2.4
    t = tt(d)
    f = 38 + 70 * np.exp(-t / 0.08)
    boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / (0.55 * big))
    noise = lp(rng.standard_normal(len(t)), 2200) * np.exp(-t / 0.12) * 0.55
    crack = hp(rng.standard_normal(len(t)), 3000) * np.exp(-t / 0.02) * 0.3
    return np.tanh(1.3 * (boom + noise + crack))


def whoosh(d=0.9, up=True, seed=1):
    x = sweep_noise(d, 300 if up else 5000, 6000 if up else 250, 0.55, seed)
    t = tt(d)[: len(x)]
    e = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2.2
    return x * e


def riser(d, seed=3):
    x = sweep_noise(d, 200, 9000, 0.6, seed)
    t = tt(d)[: len(x)]
    e = (t / d) ** 2.2
    tone = np.sin(2 * np.pi * np.cumsum(np.geomspace(220, 1760, len(t))) / SR) * 0.25
    return (x * 0.8 + tone) * e


def blip(freq, d=0.09, fm=0.0):
    t = tt(d)
    m = np.sin(2 * np.pi * freq * 2 * t) * fm
    return np.sin(2 * np.pi * freq * t + m) * env_ad(d, 0.001, d / 4)


def ui_click():
    t = tt(0.05)
    return (np.sin(2 * np.pi * 2600 * t) * 0.6 + hp(rng.standard_normal(len(t)), 4000) * 0.3) * np.exp(-t / 0.008)


def bell(freq, d=1.4):
    t = tt(d)
    x = sum(a * np.sin(2 * np.pi * freq * m * t) * np.exp(-t / (d * dd)) for m, a, dd in [(1, 1, 0.35), (2.01, 0.45, 0.2), (3.0, 0.25, 0.12), (4.2, 0.12, 0.08)])
    return x * np.minimum(1, t / 0.002)


def reverb(x, secs=2.4, mix=0.3, seed=9):
    r = np.random.default_rng(seed)
    n = int(secs * SR)
    t = np.arange(n) / SR
    ir = r.standard_normal((2, n)) * np.exp(-t / (secs / 5.5))
    ir = lp(ir, 6000)
    ir[:, : int(0.012 * SR)] = 0
    ir /= np.sqrt((ir**2).sum(axis=1, keepdims=True))
    wet = np.vstack([signal.fftconvolve(x[c], ir[c])[:N] for c in range(2)])
    return x + mix * wet


# ------------------------------------------------------------------- arreglo
drums = buf()
music = buf()
sfx = buf()
send = buf()  # bus de reverb

# Progresión Am – F – C – G (un acorde por compás)
CHORDS = [
    [57, 60, 64],  # Am
    [53, 57, 60],  # F
    [55, 60, 64],  # C
    [55, 59, 62],  # G
]
ROOTS = [45, 41, 48, 43]
N_BARS = int(round(DUR / BAR))  # 16

KICK, CLAP, HC, HO = kick(), clap(), hat(False), hat(True)

def bar_t(b):
    return b * BAR


groove_bars = set(range(2, 10)) | {12, 13, 14}
intro_bars = {0, 1}
break_bars = {10, 11}
kick_times = []

for b in range(N_BARS):
    t0 = bar_t(b)
    ch = CHORDS[b % 4]
    root = ROOTS[b % 4]
    # Pad en todo el tema (más abierto en el groove)
    cut = 1100 if b in intro_bars else (900 if b in break_bars else 2200)
    if b == 15:
        pad = pad_chord([note(n) for n in ch] + [note(ch[0] + 12)], BAR + 3.0, 1600)
        place(music, pad, t0, 0.5)
        place(send, pad, t0, 0.3)
    else:
        pad = pad_chord([note(n) for n in ch], BAR + 0.4, cut)
        place(music, pad, t0, 0.42)
        place(send, pad, t0, 0.2)

    for s16 in range(16):
        t = t0 + s16 * BEAT / 4
        beat_i = s16 // 4
        # Batería
        if b in groove_bars or (b == 1) or (b == 15 and t < fr(1104)):
            if s16 % 4 == 0:
                place(drums, KICK, t, 0.95 if b != 1 else 0.6)
                kick_times.append(t)
            if s16 in (4, 12) and b != 1:
                place(drums, CLAP, t, 0.42, 0.05)
                place(send, CLAP, t, 0.15)
            if s16 % 4 == 2:
                place(drums, HO, t, 0.16, 0.25)
            if b != 1:
                place(drums, HC, t, 0.09 + 0.05 * (s16 % 2 == 0), -0.3 if s16 % 2 else 0.3)
        # Bajo en corcheas (groove)
        if (b in groove_bars or (b == 15 and t < fr(1104))) and s16 % 2 == 0:
            place(music, bass_note(note(root - 12 + (12 if s16 % 4 == 2 else 0)), BEAT / 2 * 0.95), t, 0.42)
        # Arpegio pluck en semicorcheas
        if b not in break_bars and b < 15:
            seq = ch + [ch[0] + 12]
            n_ = seq[[0, 1, 2, 3, 2, 1, 2, 3][s16 % 8]] + 12
            g = 0.10 if b in intro_bars else 0.13
            pan = -0.45 if s16 % 2 else 0.45
            p = pluck(note(n_))
            place(music, p, t, g, pan)
            place(send, p, t, 0.08)
            # eco a corchea con puntillo
            place(music, p, t + BEAT * 0.75, g * 0.35, -pan)
    # Sub drone en intro y breakdown
    if b in intro_bars | break_bars:
        d = BAR
        t = tt(d)
        sub = np.sin(2 * np.pi * note(root - 12) * t) * np.minimum(1, t / 0.3) * np.clip((d - t) / 0.3, 0, 1)
        place(music, sub, t0, 0.35)

# Sidechain: el kick “bombea” la música
env = np.ones(N)
for kt in kick_times:
    i = int(kt * SR)
    L = int(0.32 * SR)
    seg = 1 - 0.62 * np.exp(-np.arange(L) / SR / 0.09)
    n = min(L, N - i)
    env[i : i + n] = np.minimum(env[i : i + n], seg[:n])
music *= env

# Intro filtrada (S1): se abre al llegar a S2
cut_env = np.ones(N)
i2 = int(fr(150) * SR)
music_lp = lp(music, 900)
xf = np.clip((np.arange(N) - int(fr(96) * SR)) / (i2 - int(fr(96) * SR)), 0, 1) ** 2
music = music_lp * (1 - xf) + music * xf

# ------------------------------------------------------------------- efectos
S = TL["sfx"]
for f in S["impact"]:
    big = 1.4 if f in (0, 937, 1104) else 1.0
    x = impact(big)
    place(sfx, x, fr(f), 0.75 if f != 1104 else 0.95)
    place(send, x, fr(f), 0.35)
for f in S["thud"]:
    t = tt(0.3)
    x = np.sin(2 * np.pi * (70 + 60 * np.exp(-t / 0.03)) * t) * np.exp(-t / 0.08)
    place(sfx, x, fr(f), 0.4)
for k, f in enumerate(S["pulse"]):
    x = blip(660 * 2 ** (k * 2 / 12), 0.16, 1.2)
    place(sfx, x, fr(f), 0.22, -0.3 + 0.2 * k)
    place(send, x, fr(f), 0.2)
for k, f in enumerate(S["ping"]):
    x = blip(note(76 + [0, 3, 5, 7, 12][k]), 0.22, 0.4)
    place(sfx, x, fr(f), 0.2, -0.5 + k * 0.25)
    place(send, x, fr(f), 0.25)
for k, f in enumerate(S["ui"]):
    place(sfx, ui_click(), fr(f), 0.3, 0.35 if k % 2 else -0.35)
for k, f in enumerate(S["ticks"]):
    x = bell(note(72 + [0, 2, 4, 7, 9, 12, 14, 16, 19, 21][k]), 0.9)
    place(sfx, x, fr(f), 0.16, -0.6 + k * 0.13)
    place(send, x, fr(f), 0.35)
for f in S["digits"]:
    t = tt(0.04)
    x = hp(rng.standard_normal(len(t)), 2000) * np.exp(-t / 0.006) + np.sin(2 * np.pi * 1800 * t) * np.exp(-t / 0.01) * 0.5
    place(sfx, x, fr(f), 0.35)
for f in S["confirm"]:
    a = bell(note(88), 1.2)
    b_ = bell(note(93), 1.6)
    place(sfx, a, fr(f), 0.2, -0.2)
    place(sfx, b_, fr(f) + 0.11, 0.22, 0.2)
    place(send, a, fr(f), 0.3)
    place(send, b_, fr(f) + 0.11, 0.3)
for f in S["strike"]:
    x = whoosh(0.22, True, 11)
    place(sfx, x, fr(f), 0.12)
for k, (a, b) in enumerate(S["riser"]):
    d = fr(b - a)
    x = riser(d, 20 + k)
    place(sfx, x, fr(a), 0.22)
    place(send, x, fr(a), 0.15)
for k, f in enumerate(S["whoosh"]):
    d = 0.8
    x = whoosh(d, k % 2 == 0, 30 + k)
    st = np.vstack([x, np.roll(x, 240)])
    place(sfx, st, fr(f) - d * 0.55, 0.42)
    place(send, st, fr(f) - d * 0.55, 0.2)
for f in S["sweep"]:
    x = whoosh(1.1, False, 50)
    place(sfx, x, fr(f), 0.35)
    place(send, x, fr(f), 0.3)

# ------------------------------------------------------------------- mezcla
mix = drums * 0.9 + music * 0.95 + sfx
mix = mix + (reverb(send, 2.6, 1.0) - send) * 0.35  # sólo la cola húmeda del bus
mix = hp(mix, 28)

# Cola final: desvanecimiento en el último segundo
t = np.arange(N) / SR
fade = np.clip((DUR - t) / 1.6, 0, 1) ** 1.5
fade[t < DUR - 1.6] = 1
mix *= fade
mix[:, :48] *= np.linspace(0, 1, 48)

# Limitador suave + normalización
mix = mix / (np.abs(mix).max() + 1e-9) * 1.4
mix = np.tanh(mix) / np.tanh(1.4)
mix *= 10 ** (-2.2 / 20) / (np.abs(mix).max() + 1e-9)  # ≈ -14 LUFS integrados

out = os.path.join(ROOT, "public", "audio", "soundtrack.wav")
from scipy.io import wavfile

wavfile.write(out, SR, (mix.T * 32767).astype(np.int16))
print("ok", out, mix.shape, DUR)
