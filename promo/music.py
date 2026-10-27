"""Banda sonora original del promo, sintetizada desde cero (sin samples).

120 BPM, La menor (Am–F–C–G). Los efectos caen en los mismos tiempos que la
animación de anim.js: rebotes, explosión del logo, la bola que rompe el texto,
barridos entre escenas, el tecleo de la URL y el golpe final.

    python3 promo/music.py   →  promo/out/music.wav  (48 kHz, estéreo, −14 LUFS)
"""
import json
import subprocess
import wave
from pathlib import Path

import numpy as np

SR = 48000
DUR = 30.0
N = int(SR * DUR)
BEAT = 0.5
OUT = Path(__file__).resolve().parent / "out"
rng = np.random.default_rng(7)

L = np.zeros(N)
R = np.zeros(N)
MUSIC_L = np.zeros(N)  # bus que se "agacha" con el bombo (sidechain)
MUSIC_R = np.zeros(N)


# ------------------------------------------------------------ utilidades
def tt(dur):
    return np.arange(int(dur * SR)) / SR


def noise(dur):
    return rng.standard_normal(int(dur * SR))


def filt(x, lo=None, hi=None, order=2):
    """Filtro Butterworth de fase cero en el dominio de frecuencia."""
    n = len(x)
    f = np.fft.rfftfreq(n, 1 / SR)
    h = np.ones_like(f)
    if hi:
        h /= np.sqrt(1 + (f / hi) ** (2 * order))
    if lo:
        h /= np.sqrt(1 + (lo / np.maximum(f, 1e-3)) ** (2 * order))
    return np.fft.irfft(np.fft.rfft(x) * h, n)


def add(sig, t0, gain=1.0, pan=0.0, bus="main"):
    i = int(round(t0 * SR))
    if i >= N or i + len(sig) <= 0:
        return
    if i < 0:
        sig, i = sig[-i:], 0
    s = sig[: N - i] * gain
    gl = np.cos((pan + 1) * np.pi / 4) * np.sqrt(2)
    gr = np.sin((pan + 1) * np.pi / 4) * np.sqrt(2)
    tl, tr = (L, R) if bus == "main" else (MUSIC_L, MUSIC_R)
    tl[i : i + len(s)] += s * gl
    tr[i : i + len(s)] += s * gr


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def saw(f0, t, decay_base, decay_per_h, max_h=40, phase_seed=0):
    """Diente de sierra aditivo cuyo brillo decae con el tiempo."""
    out = np.zeros_like(t)
    ph = np.random.default_rng(phase_seed).uniform(0, 2 * np.pi, max_h)
    for h in range(1, max_h + 1):
        if h * f0 > SR * 0.45:
            break
        out += np.sin(2 * np.pi * h * f0 * t + ph[h - 1]) / h * np.exp(-t * (decay_base + h * decay_per_h))
    return out


# --------------------------------------------------------------- sonidos
def kick(big=False):
    t = tt(0.6 if big else 0.45)
    f = 44 + 120 * np.exp(-t * 26)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * (4.5 if big else 7.5))
    click = filt(noise(len(t) / SR), lo=2000) * np.exp(-t * 350) * 0.25
    return np.tanh((body + click) * (2.2 if big else 1.6)) * 0.9


def clap():
    t = tt(0.35)
    n = filt(noise(0.35), lo=900, hi=4000)
    env = sum(np.exp(-np.clip(t - o, 0, None) * 380) * (t >= o) for o in (0, 0.011, 0.023)) * 0.7
    env += np.exp(-np.clip(t - 0.023, 0, None) * 16) * (t >= 0.023) * 0.6
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30) * 0.4
    return (n * env / 3 + body) * 0.8


def hat(open_=False):
    d = 0.25 if open_ else 0.06
    t = tt(d)
    return filt(noise(d), lo=7500) * np.exp(-t * (14 if open_ else 70)) * 0.25


def crash(dur=2.6):
    t = tt(dur)
    a = filt(noise(dur), lo=3500, hi=15000)
    b = filt(noise(dur), lo=3500, hi=15000)
    env = np.exp(-t * 1.7) * (1 - np.exp(-t * 400))
    return a * env * 0.22, b * env * 0.22


def sub_boom(dur=1.6):
    t = tt(dur)
    f = 34 + 40 * np.exp(-t * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 2.4) * 0.9


def whoosh(dur, up=True):
    t = tt(dur)
    p = t / dur
    if not up:
        p = 1 - p
    lo = filt(noise(dur), hi=900)
    hi = filt(noise(dur), lo=2500, hi=11000)
    env = (p ** 2.2) if up else (p ** 0.6) * np.exp(-t * 6)
    return ((1 - p) * lo * 1.6 + p * hi) * env * 0.35


def riser(dur):
    t = tt(dur)
    f = 180 * (1300 / 180) ** (t / dur)
    tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * (t / dur) ** 2 * 0.18
    return tone + whoosh(dur) * 0.8


def thud():
    t = tt(0.3)
    f = 70 + 90 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 14) * 0.8


def boing(pitch=1.0):
    t = tt(0.32)
    f = (300 + 420 * np.exp(-t * 18)) * pitch * (1 + 0.03 * np.sin(2 * np.pi * 22 * t))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 11) * 0.25


def pop(pitch=1.0):
    t = tt(0.09)
    f = (700 + 900 * (1 - np.exp(-t * 60))) * pitch
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45) * 0.35


def tick(pitch=1.0):
    t = tt(0.03)
    return filt(noise(0.03), lo=3000 * pitch, hi=9000) * np.exp(-t * 400) * 0.3


def pluck(note, seed):
    t = tt(0.4)
    return saw(midi(note), t, 6, 1.4, 24, seed) * 0.18


def bass(note, seed):
    t = tt(0.24)
    f0 = midi(note)
    env = np.minimum(1, t / 0.004) * np.exp(-t * 6)
    tail = np.minimum(1, (0.24 - t) / 0.02)
    s = saw(f0, t, 0, 0.9, 14, seed) * 0.5 + np.sin(2 * np.pi * f0 * t) * 0.7
    return np.tanh(s * env * tail * 1.4) * 0.5


def pad(notes, dur, cents=8):
    t = tt(dur)
    env = np.minimum(1, t / 0.35) * np.minimum(1, (dur - t) / 0.3)
    l = np.zeros_like(t)
    r = np.zeros_like(t)
    for i, n in enumerate(notes):
        f = midi(n)
        for h in range(1, 9):
            a = 1 / h**1.6
            l += a * np.sin(2 * np.pi * h * f * 2 ** (-cents / 1200) * t + i + h)
            r += a * np.sin(2 * np.pi * h * f * 2 ** (cents / 1200) * t + 2 * i + h)
    return l * env * 0.05, r * env * 0.05


# ------------------------------------------------------------ armonía
CHORDS = [  # (bajo, tríada para arpegio/pad)
    (45, [57, 60, 64]),  # Am
    (41, [53, 57, 60]),  # F
    (48, [60, 64, 67]),  # C
    (43, [55, 59, 62]),  # G
]


def chord_at(t):
    return CHORDS[int(max(0, t - 2) // 2) % 4]


def beats(a, b, step=BEAT, offset=0.0):
    return [round(a + offset + k * step, 4) for k in range(int(round((b - a) / step)))]


END = 29.0  # golpe final; después solo queda la cola

# ----------------------------------------------------------- bombo + bus
kick_times = beats(2.0, 6.0) + beats(6.0, END)
for k in kick_times:
    add(kick(big=k in (2.0, 6.0, 20.0, 25.0)), k, 1.0)
add(kick(big=True), END, 1.1)

# sidechain: el bus musical baja en cada golpe de bombo
duck = np.ones(N)
tN = np.arange(N) / SR
for k in kick_times:
    i = int(k * SR)
    j = min(N, i + int(0.5 * SR))
    duck[i:j] = np.minimum(duck[i:j], 1 - 0.6 * np.exp(-(tN[i:j] - k) * 9))

# --------------------------------------------------------------- groove
for b in beats(2.5, 4.0, 1.0) + beats(6.5, END, 1.0):
    add(clap(), b, 0.9, 0.05)
for b in beats(2.0, END, BEAT, 0.25):
    add(hat(open_=True), b, 0.6 if 4 <= b < 6 else 0.9, 0.25)
for i, b in enumerate(beats(8.0, END, 0.125)):
    if i % 4 != 2:
        add(hat(), b, (1.0 if i % 2 == 0 else 0.55), -0.3)
for i, b in enumerate(beats(2.0, END, BEAT, 0.25)):
    root = chord_at(b)[0]
    note = root + (12 if i % 4 == 3 else 0)
    add(bass(note, i), b, 0.55 if 4 <= b < 6 else 1.0, 0, "music")
for bar in beats(2.0, 30.0, 2.0):
    notes = chord_at(bar + 0.01)[1]
    gain = 0.5 if 4 <= bar < 6 else 1.0
    if bar >= END:
        continue
    pl, pr = pad(notes, min(2.0, END - bar + 0.25))
    add(pl * gain, bar, 1, -1, "music")
    add(pr * gain, bar, 1, 1, "music")
ARP = [0, 1, 2, 3, 2, 1, 3, 2]
for i, b in enumerate(beats(8.0, END, 0.125)):
    tri = chord_at(b)[1]
    step = ARP[i % 8]
    note = tri[step] if step < 3 else tri[0] + 12
    add(pluck(note + 12, i), b, 0.8 + 0.2 * (i % 2 == 0), -0.35 if i % 2 else 0.35, "music")

# --------------------------------------------------------- efectos (SFX)
# escena 1: rebotes, espiral y explosión del logo
add(whoosh(0.5), 0.0, 0.9)
for k, land in enumerate((0.5, 1.0, 1.5)):
    add(thud(), land, 2.0 - 0.3 * k)
    add(kick(), land, 0.7 - 0.1 * k)
    add(boing(1.0 + 0.12 * k), land, 1.6)
add(boing(1.3), 1.5, 0.5, -0.6)
add(boing(1.45), 1.5, 0.5, 0.6)
add(riser(0.5), 1.5, 1.0)
cl, cr = crash(3.0)
add(cl, 2.0, 1.2, -1)
add(cr, 2.0, 1.2, 1)
add(sub_boom(), 2.0, 1.0)

# escena 2: textos, bola volando, rotura y respuesta
for k in (4.0, 4.5, 5.0):
    add(pop(0.8), k, 0.8)
add(whoosh(0.45), 5.55, 1.0, 0.4)
cl, cr = crash(2.2)
add(cl, 6.0, 1.0, -1)
add(cr, 6.0, 1.0, 1)
add(filt(noise(0.4), lo=1500) * np.exp(-tt(0.4) * 12) * 0.4, 6.0, 1.0)
add(sub_boom(1.0), 6.0, 0.7)
for k in (6.25, 6.5):
    add(clap(), k, 1.1)
    add(kick(), k, 0.6)

# escena 3: tarjetas
for i, k in enumerate((8.5, 9.0, 9.5, 10.0)):
    add(whoosh(0.25, up=False), k - 0.05, 0.6, 0.5)
    add(pop(1.0 + 0.15 * i), k + 0.15, 0.6)

# escena 4: muro de obras
add(pop(1.2), 15.0, 0.6)

# escena 5: tres golpes de color y la bola que aterriza
for k in (20.0, 21.5, 23.0):
    cl, cr = crash(1.4)
    add(cl, k, 0.8, -1)
    add(cr, k, 0.8, 1)
    add(sub_boom(0.8), k, 0.6)
    add(thud(), k + 0.5, 0.9)
for k in (21.2, 22.7):
    add(whoosh(0.3), k, 0.8, -0.3)

# escena 6: llamada a la acción
for k in (25.5, 26.0):
    add(pop(0.9), k, 0.6)
add(pop(1.4), 26.5, 0.9)
url_len = 22
for k in range(url_len):
    add(tick(1 + 0.15 * (k % 3)), 27.0 + k / url_len, 0.7, (k % 5 - 2) * 0.1)
add(pop(1.8), 28.0, 0.8)
add(thud(), 28.0, 0.4)

# transiciones entre escenas (terminan en el beat)
for k in (4.0, 8.0, 14.0, 20.0, 25.0):
    add(whoosh(0.45), k - 0.45, 1.0, 0)

# golpe final con acorde que se desvanece
cl, cr = crash(1.0)
add(cl, END, 1.2, -1)
add(cr, END, 1.2, 1)
add(sub_boom(1.0), END, 1.0)
for n in (45, 57, 60, 64, 69):
    t = tt(1.0)
    stab = saw(midi(n), t, 2.5, 0.5, 20, n) * np.minimum(1, (1.0 - t) / 0.3) * 0.16
    add(stab, END, 1, (n - 57) / 20)

# ---------------------------------------------------------------- mezcla
mix_l = L + MUSIC_L * duck
mix_r = R + MUSIC_R * duck
peak = max(np.abs(mix_l).max(), np.abs(mix_r).max())
drive = 1.6
mix = np.stack([mix_l, mix_r], 1) / peak
mix = np.tanh(mix * drive) / np.tanh(drive)
fade = np.minimum(1, (DUR - tN) / 0.2)[:, None]
mix *= fade
mix = mix / np.abs(mix).max() * 0.89

OUT.mkdir(exist_ok=True)
raw = OUT / "music_raw.wav"
with wave.open(str(raw), "wb") as w:
    w.setnchannels(2)
    w.setsampwidth(2)
    w.setframerate(SR)
    w.writeframes((mix * 32767).astype("<i2").tobytes())

# normalización de sonoridad para redes: −14 LUFS, pico real −1 dBTP (2 pasadas)
meas = subprocess.run(
    ["ffmpeg", "-hide_banner", "-i", str(raw), "-af", "loudnorm=I=-14:TP=-1:LRA=11:print_format=json", "-f", "null", "-"],
    capture_output=True, text=True, check=True,
).stderr
m = json.loads(meas[meas.rindex("{") :])
af = (
    "loudnorm=I=-14:TP=-1:LRA=11:linear=true:"
    f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
    f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}"
)
subprocess.run(
    ["ffmpeg", "-y", "-loglevel", "error", "-i", str(raw), "-af", af, "-ar", str(SR), "-c:a", "pcm_s16le", str(OUT / "music.wav")],
    check=True,
)
raw.unlink()
print(OUT / "music.wav", f"(entrada {m['input_i']} LUFS)")
