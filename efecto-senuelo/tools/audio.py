"""Genera música lo-fi (120 BPM, 30 compases = 60 s exactos, en bucle) y efectos de sonido sintetizados.
Lee tiempos de efectos y volumen de música desde player/timeline.js.
Salida: musica.wav (ya con volumen 10-17 %), efectos.wav y mezcla.wav en el directorio indicado."""
import json, subprocess, sys, os
import numpy as np
from scipy.signal import butter, sosfilt
from scipy.io import wavfile

SR = 48000
DUR = 60.0
N = int(SR * DUR)
rng = np.random.default_rng(7)
HERE = os.path.dirname(os.path.abspath(__file__))
out_dir = sys.argv[1] if len(sys.argv) > 1 else '.'

tl = json.loads(subprocess.check_output(['node', '-e', f"""
global.window={{}}; require('{HERE}/../player/timeline.js'); console.log(JSON.stringify(window.TIMELINE));"""]))

def lp(x, f, order=2): return sosfilt(butter(order, f, 'low', fs=SR, output='sos'), x)
def hp(x, f, order=2): return sosfilt(butter(order, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi, order=2): return sosfilt(butter(order, [lo, hi], 'band', fs=SR, output='sos'), x)
def env(n, a, d):
    t = np.arange(n) / SR
    return np.minimum(1, t / max(a, 1e-4)) * np.exp(-t / d)
def add(buf, sig, t0):
    i = int(round(t0 * SR)) % len(buf)
    end = i + len(sig)
    if end <= len(buf): buf[i:end] += sig
    else:  # envuelve al inicio para que el bucle sea continuo
        k = len(buf) - i; buf[i:] += sig[:k]; buf[:len(sig) - k] += sig[k:]
def midi(m): return 440 * 2 ** ((m - 69) / 12)

# ---------------- MÚSICA ----------------
BPM = 120; beat = 60 / BPM; bar = beat * 4
music_L = np.zeros(N); music_R = np.zeros(N)
drums = np.zeros(N)

def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 45 + 95 * np.exp(-t * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 7) * 0.95 + 0.15 * lp(rng.standard_normal(n), 3000) * np.exp(-t * 80)
def snare():
    n = int(0.3 * SR); t = np.arange(n) / SR
    nz = bp(rng.standard_normal(n), 900, 6000) * np.exp(-t * 18) * 0.55
    tone = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 25) * 0.3
    return nz + tone
def hat(open_=False):
    n = int((0.25 if open_ else 0.06) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7000) * np.exp(-t * (14 if open_ else 70)) * 0.22

K, S_, H, HO = kick(), snare(), hat(), hat(True)
nbars = int(DUR / bar)
for b in range(nbars):
    t0 = b * bar
    for k in [0, 2.5] + ([3.75] if b % 4 == 3 else []):
        add(drums, K, t0 + k * beat)
    for s in [1, 3]: add(drums, S_, t0 + s * beat)
    for e in range(8):
        sw = 0.04 if e % 2 else 0  # swing
        add(drums, HO if e == 7 and b % 2 else H * (0.7 if e % 2 else 1), t0 + e * beat / 2 + sw)

# progresión lo-fi: Fmaj7 - Em7 - Dm7 - Cmaj7
chords = [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]]
roots = [41, 40, 38, 36]
def epiano(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 3) + 0.12 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 6))
    s *= env(n, 0.008, 1.1) * (1 + 0.08 * np.sin(2 * np.pi * 5 * t))
    tail = int(0.08 * SR); s[-tail:] *= np.linspace(1, 0, tail)
    return s * 0.16
def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    s *= env(n, 0.01, 0.7); tail = int(0.05 * SR); s[-tail:] *= np.linspace(1, 0, tail)
    return s * 0.42
keys = np.zeros(N); bas = np.zeros(N); lead = np.zeros(N)
for b in range(nbars):
    t0 = b * bar; c = chords[b % 4]
    for hit, ln in [(0, 1.5), (1.5, 1.0), (2.5, 1.5)]:
        for j, m in enumerate(c):
            add(keys, epiano(midi(m + 12), ln * beat * 0.95), t0 + hit * beat + j * 0.012)
    for hit, ln, oct_ in [(0, 1.5, 0), (1.5, 0.5, 0), (2.5, 1.0, 0), (3.5, 0.5, 12)]:
        add(bas, bass(midi(roots[b % 4] + oct_), ln * beat), t0 + hit * beat)
    # pequeño motivo de campanita cada 2 compases
    if b % 2 == 1:
        for i, m in enumerate([c[3] + 24, c[2] + 24, c[1] + 24]):
            n = int(0.5 * SR); tt = np.arange(n) / SR
            add(lead, np.sin(2 * np.pi * midi(m) * tt) * np.exp(-tt * 7) * 0.07, t0 + (3 + i / 3) * beat)
keys = lp(keys, 3200)
vinyl = lp(rng.standard_normal(N), 4000) * 0.004 + (rng.random(N) > 0.99985) * rng.standard_normal(N) * 0.08
music = drums * 0.8 + keys + bas + lead + vinyl
# sidechain suave con el bombo
side = np.ones(N)
for b in range(nbars):
    for k in [0, 2.5]:
        i = int((b * bar + k * beat) * SR); n = int(0.25 * SR)
        side[i:i + n] = np.minimum(side[i:i + n], 1 - 0.35 * np.exp(-np.arange(min(n, N - i)) / SR * 14))
music = lp(music * side, 9000)
music /= np.max(np.abs(music)) * 1.02  # pista normalizada a ~0 dBFS

# envolvente de volumen (con rampas de 0.3 s)
tt = np.arange(N) / SR
gain = np.zeros(N)
for a, b, g in tl['musicGain']: gain[(tt >= a) & (tt < b)] = g
k = int(0.3 * SR); gain = np.convolve(np.pad(gain, (k, k), mode='wrap'), np.ones(k) / k, mode='same')[k:-k]
music_final = music * gain

# ---------------- EFECTOS ----------------
def sfx_pop():
    n = int(0.12 * SR); t = np.arange(n) / SR
    f = 900 * np.exp(-t * 30) + 250
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.002, 0.035) * 0.55
def sfx_thud():
    n = int(0.35 * SR); t = np.arange(n) / SR
    f = 40 + 120 * np.exp(-t * 25)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9) + lp(rng.standard_normal(n), 800) * np.exp(-t * 30) * 0.4) * 0.8
def sfx_whoosh():
    n = int(0.45 * SR); t = np.arange(n) / SR
    nz = rng.standard_normal(n)
    low, high = bp(nz, 300, 1200), bp(nz, 1500, 7000)
    p = np.clip(t / 0.45, 0, 1); x = np.sin(np.pi * p) ** 2
    return (low * (1 - x) + high * x) * x * 0.6
def sfx_ding():
    n = int(1.2 * SR); t = np.arange(n) / SR
    f = 1568
    s = np.sin(2 * np.pi * f * t) + 0.5 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t * 6) + 0.25 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t * 12)
    return s * env(n, 0.002, 0.35) * 0.33
def sfx_sparkle():
    out = np.zeros(int(0.8 * SR))
    for i, m in enumerate([84, 88, 91, 96, 100]):
        n = int(0.4 * SR); t = np.arange(n) / SR
        s = np.sin(2 * np.pi * midi(m) * t) * env(n, 0.002, 0.1) * 0.12
        j = int(i * 0.05 * SR); out[j:j + n] += s
    return out
def sfx_poof():
    n = int(0.6 * SR); t = np.arange(n) / SR
    nz = lp(rng.standard_normal(n), 1800) * env(n, 0.01, 0.12)
    low = np.sin(2 * np.pi * np.cumsum(120 * np.exp(-t * 5) + 50) / SR) * np.exp(-t * 10) * 0.4
    return (nz * 0.9 + low) * 0.7
def sfx_click():
    n = int(0.05 * SR); t = np.arange(n) / SR
    return (hp(rng.standard_normal(n), 2000) * np.exp(-t * 300) * 0.6 + np.sin(2 * np.pi * 2200 * t) * np.exp(-t * 200) * 0.4) * 0.9
def sfx_drop():
    n = int(0.6 * SR); t = np.arange(n) / SR
    f = 1100 * np.exp(-t * 4.5) + 120
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env(n, 0.005, 0.25) * 0.32
def sfx_tick():
    # ticks rápidos durante el conteo (0.6 s)
    out = np.zeros(int(0.65 * SR))
    for i in range(12):
        n = int(0.02 * SR); t = np.arange(n) / SR
        s = np.sin(2 * np.pi * (1800 + i * 60) * t) * np.exp(-t * 300) * 0.18
        j = int(0.6 * (1 - (1 - i / 12) ** 2) * SR); out[j:j + n] += s
    return out
SFX = {'pop': sfx_pop, 'thud': sfx_thud, 'whoosh': sfx_whoosh, 'ding': sfx_ding, 'sparkle': sfx_sparkle,
       'poof': sfx_poof, 'click': sfx_click, 'drop': sfx_drop, 'tick': sfx_tick}
cache = {k: f() for k, f in SFX.items()}
sfx = np.zeros(N)
for t0, kind in tl['sfx']:
    lead_in = 0.2 if kind == 'whoosh' else 0  # el whoosh culmina en el corte
    add(sfx, cache[kind], t0 - lead_in)
sfx *= 0.85

mix = music_final + sfx
peak = np.max(np.abs(mix))
if peak > 0.98: mix *= 0.98 / peak; print('limit', peak)

def save(name, x):
    st = np.stack([x, x], 1) if x.ndim == 1 else x
    wavfile.write(os.path.join(out_dir, name), SR, (np.clip(st, -1, 1) * 32767).astype(np.int16))
save('musica.wav', music_final)
save('efectos.wav', sfx)
save('mezcla.wav', mix)
print('ok', 'music rms', np.sqrt(np.mean(music_final ** 2)), 'peak mix', np.max(np.abs(mix)))
