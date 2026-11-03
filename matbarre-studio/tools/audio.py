"""Música ambiental elegante a 80 BPM (30 compases exactos en 90 s, así el loop cierra) para el promo de Matbarre Studio:
10·20·30 (pad y campanas) → marca (entra la kalimba) → Barre · Pilates · Sculpt (pulso ligero) → la ciencia (se abre)
→ coaches (pulso) → reserva → cierre (acorde final cálido). Sin batería: pads, kalimba, bajo suave, shaker y aire.

Uso: python3 audio.py timeline.json <carpeta-audio>"""
import json, sys, wave, numpy as np
from scipy.signal import fftconvolve
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SR = 48000; DUR = float(TL.get('duration', 90)); N = int(SR * DUR)
rng = np.random.default_rng(23)
T = np.arange(N) / SR

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def env_ad(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def add(buf, start, sig, gain=1.0):
    i = int(round(start * SR)); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    if j > i: buf[i:j] += sig[: j - i] * gain
note = lambda m: 440 * 2 ** ((m - 69) / 12)
def smooth(x, k):
    c = np.cumsum(np.concatenate([[0.0], x])); h = k // 2; i = np.arange(len(x)); lo = np.clip(i - h, 0, len(x)); hi = np.clip(i + h, 0, len(x))
    return (c[hi] - c[lo]) / np.maximum(hi - lo, 1)
def curve(points):
    return np.interp(T, [p[0] for p in points], [p[1] for p in points])
def reverb(x, secs=3.0, damp=1.6, seed=1):
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * damp) * (1 - np.exp(-t * 300)); ir = band(ir, 150, 7000); ir /= np.abs(ir).sum() ** .5 * 40
    return fftconvolve(x, ir)[: len(x)]

# ---------------- MÚSICA ----------------
BPM = 30 * 4 * 60 / DUR; beat = 60 / BPM; bar = beat * 4; NB = int(round(DUR / bar))
# Fa mayor cálido y femenino: Fmaj9 – Am7 – Dm9 – Bbmaj7 (luminoso, sin tensión)
G9 = [41, 57, 60, 64, 67]; D_ = [45, 57, 60, 64, 67]; E9 = [38, 57, 60, 62, 65]; A2 = [46, 57, 62, 65, 69]
PROG = [G9, D_, E9, A2]
def chord_at(t): return PROG[int(t / bar) % 4]

# pad: osciladores suaves desafinados, ataque lento, cambio de acorde con fundido
padL = np.zeros(N); padR = np.zeros(N)
for b in range(NB + 1):
    t0 = b * bar
    if t0 >= DUR: break
    ch = chord_at(t0 + .01); n = int((bar + 1.6) * SR); tt = np.arange(n) / SR
    e = np.clip(tt / 1.2, 0, 1) * np.clip((bar + 1.6 - tt) / 1.6, 0, 1)
    for k, m in enumerate(ch[1:]):
        f = note(m)
        for det, side in ((-.18, 0), (.18, 1)):
            s = np.sin(2 * np.pi * (f + det) * tt + k) + .18 * np.sin(2 * np.pi * 2 * (f + det) * tt)
            add(padL if side == 0 else padR, t0, s * e, .16)
pad = np.stack([band(padL, 80, 3200), band(padR, 80, 3200)])
pad = pad + np.stack([reverb(pad[0], 3.5, 1.2, 3), reverb(pad[1], 3.5, 1.2, 4)]) * .6
# bajo: senoidal suave en cada compás
bass = np.zeros(N)
for b in range(NB + 1):
    t0 = b * bar
    if t0 >= DUR: break
    n = int(bar * SR); tt = np.arange(n) / SR; f = note(chord_at(t0 + .01)[0])
    s = (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * 2 * f * tt)) * np.clip(tt / .25, 0, 1) * np.exp(-tt / 2.2)
    add(bass, t0, s, .5)
# kalimba: arpegio en corcheas con huecos (determinista), tono de madera
def kal(f, dur=1.6):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) * np.exp(-t / .55) + .3 * np.sin(2 * np.pi * f * 4.2 * t) * np.exp(-t / .05) + .12 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .2)
    return s * np.clip(t / .002, 0, 1)
kL = np.zeros(N); kR = np.zeros(N)
PAT = [0, 2, 1, 3, 2, 4, 1, 3]
for i in range(int(DUR / (beat / 2)) + 1):
    t0 = i * beat / 2
    if t0 >= DUR - .3: break
    if rng.random() < .32 and i % 8 != 0: continue
    ch = chord_at(t0 + .01); m = ch[1:][PAT[i % 8] % 4] + 12; pan = .3 * np.sin(i * 1.7)
    x = kal(note(m)) * (1 if i % 2 == 0 else .7)
    add(kL, t0, x, .22 * (1 - pan)); add(kR, t0, x, .22 * (1 + pan))
kal_s = np.stack([kL, kR]); kal_s = kal_s + np.stack([reverb(kL, 2.6, 1.8, 5), reverb(kR, 2.6, 1.8, 6)]) * .7
# campanas altas (escena de los colores y cierre)
bells = np.zeros(N)
def bell(f, dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / 1.1) + .3 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .3)) * np.clip(t / .003, 0, 1)
for i in range(int(DUR / beat)):
    t0 = i * beat
    if (t0 < 11.0 or 36.9 <= t0 < 46.0 or 78.5 <= t0 < 89) and i % 2 == 0:
        ch = chord_at(t0 + .01); add(bells, t0, bell(note(ch[2 + (i // 2) % 3] + 24)), .07)
bells = bells + reverb(bells, 3.0, 1.4, 7) * .9
# pulso ligero (shaker suave) en telas / sets / juntas: movimiento sin batería
shk = np.zeros(N)
for i in range(int(DUR / (beat / 2)) + 1):
    t0 = i * beat / 2; n = int(.12 * SR); tt = np.arange(n) / SR
    add(shk, t0, band(rng.standard_normal(n), 5000, 12000) * np.exp(-tt / .03) * (1 if i % 2 else .55), .05)
# aire de naturaleza: viento suave que ondula + gotitas ocasionales
wind = band(rng.standard_normal(N), 200, 2200) * (.55 + .45 * np.sin(2 * np.pi * T / 11 + 1)) * (.7 + .3 * np.sin(2 * np.pi * T / 4.3))
wind = wind / np.abs(wind).max() * .25
drops = np.zeros(N)
for t0 in np.arange(1.5, DUR - 1, 2.9):
    tt = np.arange(int(.15 * SR)) / SR; f0 = rng.uniform(900, 1500)
    add(drops, t0 + rng.uniform(0, 1.2), np.sin(2 * np.pi * np.cumsum(f0 * (1 + 1.2 * tt / .15)) / SR) * np.exp(-tt / .03), .05)
drops = drops + reverb(drops, 2.0, 2.5, 8) * .6

kal_g = curve([(0, .25), (7.2, .3), (11.5, .85), (36.9, .9), (37.4, .55), (46.0, .8), (56.9, .9), (73.8, .85), (78.5, .65), (86, .5), (90, .3)])
shk_g = curve([(0, 0), (19.2, 0), (19.8, .9), (36.6, .9), (37.0, 0), (51.0, 0), (51.4, .6), (56.9, .7), (68.0, .8), (78.2, .8), (78.6, 0), (90, 0)])
bass_g = curve([(0, .35), (11.0, .35), (11.6, .8), (36.9, .85), (37.6, .45), (46.0, .8), (86, .75), (90, .4)])
pad_g = curve([(0, 1.0), (11.5, .95), (19.7, .85), (36.9, 1.15), (46.0, .9), (78.5, 1.05), (90, 1.0)])
air_g = curve([(0, .8), (11.5, .5), (19.7, .35), (36.9, .7), (46.0, .9), (51.2, .4), (78.5, .7), (90, .8)])
mus = pad * pad_g + np.stack([bass, bass]) * bass_g + kal_s * kal_g + np.stack([bells, bells]) + np.stack([shk, shk * .9]) * shk_g \
    + np.stack([wind, np.roll(wind, 900)]) * air_g + np.stack([drops, np.roll(drops, 600)]) * air_g
mus /= np.abs(mus).max()
# volumen: 19 % sin texto, 15.5 % con subtítulos (la voz siempre por encima)
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(0.3 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); kk = smooth(kk, int(.4 * SR)); g = g * kk
mus *= g * .95  # pads continuos: 4 dB menos que en reels con batería para que la voz quede al frente
fi = int(.03 * SR); mus[:, :fi] *= np.linspace(0, 1, fi)
fo = int(.4 * SR); mus[:, -fo:] *= np.linspace(1, .25, fo)  # el final se suaviza y empalma con el inicio (pad y viento)

# ---------------- EFECTOS (suaves) ----------------
def ding(p):
    n = int(1.6 * SR); tt = np.arange(n) / SR; f = 1046.5 * p
    return (np.sin(2 * np.pi * f * tt) + .25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / .1)) * env_ad(n, .004, .5) * .45
def pop(p):  # gota de agua
    n = int(.18 * SR); tt = np.arange(n) / SR; f = (500 + 700 * tt / tt[-1]) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, .003, .04) * .8
def whoosh(p):  # brisa
    n = int(1.0 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n)
    return band(x, 250 * p, 2500 * p) * np.sin(np.pi * tt / tt[-1]) ** 2 * 1.1
def click(p):
    n = int(.08 * SR); tt = np.arange(n) / SR
    return band(rng.standard_normal(n), 1500, 7000) * np.exp(-tt / .006) * .8 + np.sin(2 * np.pi * 700 * tt) * np.exp(-tt / .02) * .3
def chime(p):
    out = np.zeros(int(2.4 * SR))
    for i, m in enumerate((74, 78, 81, 86)):
        n = int(2.0 * SR); tt = np.arange(n) / SR; f = note(m) * p
        s = (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / .25)) * env_ad(n, .003, .7) * .25
        j = int(i * .09 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def sweep(p):  # tela que se desliza
    n = int(1.2 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 600 * p, 5000 * p)
    return x * (.6 + .4 * np.sin(2 * np.pi * 6 * tt)) * np.sin(np.pi * tt / tt[-1]) ** 2 * .7
def send(p):
    n = int(.7 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 1200, 7000)
    return x * np.sin(np.pi * tt / tt[-1]) ** 3 * .5 + np.sin(2 * np.pi * np.cumsum(500 + 900 * tt / tt[-1]) / SR) * env_ad(n, .02, .15) * .15
GEN = dict(ding=(ding, .3), pop=(pop, .26), whoosh=(whoosh, .22), click=(click, .4), chime=(chime, .3), sweep=(sweep, .26), send=(send, .28))
fx = np.zeros(N)
for e in TL['sfx']:
    fn, gn = GEN[e['type']]; add(fx, e['t'], fn(e['pitch']), gn * e['v'])
fx = fx + reverb(fx, 2.2, 2.0, 9) * .5
fxs = np.stack([fx, fx])
mix = np.tanh((mus + fxs) * 1.0)

def save(path, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-sin-voz.wav', mix)
print('BPM %.2f' % BPM, 'compases', NB, 'peak mix', np.abs(mix).max(), 'music rms', np.sqrt((mus ** 2).mean()))
