"""Música épica-electrónica cinematográfica (≈117 BPM; 44 compases exactos en 90 s para que el loop cierre)
+ efectos sincronizados con timeline.json. Más tensa y baja en los riesgos; explota en los beneficios. Sin voz."""
import json, sys, wave, numpy as np
from scipy.signal import fftconvolve
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SR = 48000; DUR = float(TL.get('duration', 90)); N = int(SR * DUR)
rng = np.random.default_rng(11)
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
def saw(f, n, ph=0.0):
    t = np.arange(n) / SR; return 2 * ((f * t + ph) % 1) - 1
def smooth(x, k):  # media móvil O(N) con suma acumulada (rápida con ventanas largas)
    c = np.cumsum(np.concatenate([[0.0], x])); h = k // 2; i = np.arange(len(x)); lo = np.clip(i - h, 0, len(x)); hi = np.clip(i + h, 0, len(x))
    return (c[hi] - c[lo]) / np.maximum(hi - lo, 1)
def curve(points):  # automatización por tramos lineales [(t, v), ...]
    xs = [p[0] for p in points]; ys = [p[1] for p in points]; return np.interp(T, xs, ys)
def reverb(x, secs=1.8, damp=2.5, seed=1):
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * damp) * (1 - np.exp(-t * 400)); ir = band(ir, 200, 9000); ir /= np.abs(ir).sum() ** .5 * 40
    return fftconvolve(x, ir)[: len(x)]

# ---------------- MÚSICA ----------------
BPM = 44 * 4 * 60 / DUR; beat = 60 / BPM; bar = beat * 4; NB = int(round(DUR / bar))
RISK = TL['mood']['tension']; EXPL = TL['mood']['explode']
def section(t):
    if t < 5.95: return 'intro'
    if RISK[0] <= t < RISK[1]: return 'tension'
    if EXPL[0] <= t < EXPL[1]: return 'explode'
    if 80.9 <= t < 83.95: return 'drop'
    if t >= 83.95: return 'outro'
    if t >= 67.9: return 'lift'
    return 'main'
MAIN = [[50, 57, 62, 65, 69], [46, 53, 58, 62, 65], [41, 53, 57, 60, 65], [48, 55, 60, 64, 67]]          # Dm – B♭ – F – C
UP = [[41, 53, 57, 60, 65, 69], [48, 55, 60, 64, 67, 72], [50, 57, 62, 65, 69, 74], [46, 53, 58, 62, 65, 70]]  # F – C – Dm – B♭
TENSE = [[38, 50, 57, 62, 64], [38, 46, 53, 58, 61]]
def chord_at(bi):
    s = section(bi * bar + .05)
    if s == 'tension': return TENSE[bi % 2]
    if s in ('explode', 'lift'): return UP[bi % 4]
    if s == 'drop': return [38, 50, 57, 62, 64, 69, 74]
    return MAIN[bi % 4]

padL = np.zeros(N); padR = np.zeros(N); bass = np.zeros(N); arpL = np.zeros(N); arpR = np.zeros(N)
for bi in range(NB + 1):
    t0 = bi * bar; ch = chord_at(bi); n = int(bar * SR * 1.15)
    if t0 >= DUR: break
    e = env_ad(n, .25, 2.2); e[-int(.3 * SR):] *= np.linspace(1, 0, int(.3 * SR))
    for j, m in enumerate(ch[1:]):
        for d, (gl, gr) in zip((-.11, 0, .11), ((1, .55), (.8, .8), (.55, 1))):
            x = saw(note(m + d), n, ph=(j * .17 + d) % 1) * e * .05
            add(padL, t0, x * gl); add(padR, t0, x * gr)
    root = note(ch[0] - 12 if ch[0] > 44 else ch[0])
    s = section(t0 + .05); steps = 16 if s in ('main', 'explode', 'lift', 'outro') else 8
    if s == 'tension': steps = 2
    for q in range(steps):
        tq = t0 + q * bar / steps; m = int(.9 * bar / steps * SR) if steps > 2 else int(bar * .5 * SR)
        x = (saw(root, m) * .6 + np.sin(2 * np.pi * root * np.arange(m) / SR)) * env_ad(m, .004, .11 if steps > 2 else .9)
        add(bass, tq, x * (.9 if q % 4 == 0 else .7))
    if s in ('main', 'explode', 'lift', 'outro', 'intro'):
        tones = [m + 12 for m in ch[1:4]] + [ch[1] + 24]
        pat = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 3, 2, 1, 2]
        for q in range(16):
            tq = t0 + q * bar / 16; m = int(.22 * SR); f = note(tones[pat[q] % len(tones)])
            tt = np.arange(m) / SR; x = sum(np.sin(2 * np.pi * f * h * tt) / h for h in (1, 3, 5, 7)) * env_ad(m, .002, .07) * .09
            add(arpL, tq, x * (1 if q % 2 else .7)); add(arpR, tq + .004, x * (.7 if q % 2 else 1))
# filtros y automatización
pad = np.stack([padL, padR]); dark = np.stack([band(c, 40, 900) for c in pad]); bright = np.stack([band(c, 40, 6000) for c in pad])
bpad = curve([(0, .1), (5.9, .2), (6, .45), (13.2, .55), (37.4, .7), (50.6, .7), (50.7, 0), (59.1, .05), (59.2, 1), (67.9, .75), (76.85, .7), (80.8, 1), (83.95, .5), (89.4, .25), (90, .1)])
pad = dark * (1 - bpad) + bright * bpad
bass = band(bass, 30, 900)
arp = np.stack([band(arpL, 300, 8000), band(arpR, 300, 8000)])
dl = int(beat * .75 * SR); arp[0][dl:] += arp[1][:-dl] * .35; arp[1][dl:] += arp[0][:-dl] * .35  # eco ping-pong
# batería
kick_n = int(.4 * SR); kt = np.arange(kick_n) / SR
KICK = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(45 + 95 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .2)) * .9 + band(rng.standard_normal(kick_n), 2000, 8000) * np.exp(-kt / .004) * .3
sn_n = int(.45 * SR); st = np.arange(sn_n) / SR
SNARE = band(rng.standard_normal(sn_n), 900, 9000) * np.exp(-st / .12) * .5 + np.sin(2 * np.pi * 185 * st) * np.exp(-st / .05) * .35
CLAP = band(rng.standard_normal(sn_n), 1000, 7000) * sum((st >= d) * np.exp(-np.clip(st - d, 0, None) / .02) for d in (0, .012, .024)) * .4
hat_n = int(.06 * SR); HAT = band(rng.standard_normal(hat_n), 7000, 16000) * np.exp(-np.arange(hat_n) / SR / .015) * .2
oh_n = int(.35 * SR); OHAT = band(rng.standard_normal(oh_n), 6000, 15000) * np.exp(-np.arange(oh_n) / SR / .1) * .14
cr_n = int(2.6 * SR); CRASH = band(rng.standard_normal(cr_n), 3500, 15000) * np.exp(-np.arange(cr_n) / SR / .7) * .3
def tom(f0, f1):
    n = int(.35 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / .06)) / SR) * np.exp(-t / .16) * .6
DL = np.zeros(N); DR = np.zeros(N); SNR = np.zeros(N); kicks = []
def both(t, x, g=1, pan=0): add(DL, t, x, g * (1 - pan)); add(DR, t, x, g * (1 + pan))
for k in range(int(DUR / beat) + 1):
    tb = k * beat; s = section(tb + .01); qb = k % 4
    if tb >= DUR: break
    if s == 'intro':
        if tb > 2.0 and qb in (0, 2): both(tb, KICK, .8); kicks.append(tb)
    elif s == 'tension':
        if qb == 0: both(tb, KICK, .55); both(tb + beat * .28, KICK, .35); kicks.append(tb)
    elif s == 'drop':
        if qb == 0: both(tb, KICK, .9); kicks.append(tb)
    else:
        four = s == 'explode'
        if four or qb in (0, 2): both(tb, KICK, .95 if four else .9); kicks.append(tb)
        if qb in (1, 3): add(SNR, tb, SNARE, .9); add(SNR, tb + .003, CLAP, .8 if s in ('explode', 'lift') else .5)
        sub = 4 if s in ('explode', 'lift', 'main') and tb > 13.2 else 2
        for h in range(sub): both(tb + h * beat / sub, HAT, (1 if h % 2 else .6) * (.9 if s != 'outro' else .6), pan=.25)
        if s in ('explode',) or (s == 'main' and tb > 37.4): both(tb + beat / 2, OHAT, .8, pan=-.2)
# platillos y fills en los cambios de sección
for tc in (5.95, 13.2, 37.4, 59.2, 67.9, 80.9):
    both(tc, CRASH, 1.0, pan=.1)
for tf in (5.95, 13.2, 22.45, 29.66, 37.4, 67.9, 76.85):
    for i, (a, b) in enumerate(((200, 95), (160, 80), (130, 66), (110, 55))): both(tf - .5 + i * .12, tom(a, b), .7, pan=(i - 1.5) * .2)
# redoble que crece antes de CHIP y riser antes de los beneficios
for i in range(48):
    tt = 79.3 + 1.6 * (1 - (1 - i / 48) ** 1.6)
    add(SNR, tt, SNARE, .25 + .6 * i / 48)
def riser(len_s, f0=300, f1=6000):
    n = int(len_s * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 12
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = f0 * (f1 / f0) ** (k / seg); out[a:b] = band(x, c * .6, c * 1.6)[a:b]
    return out * (t / len_s) ** 2 * .6
for tr, ln in ((57.7, 1.5), (4.95, 1.0), (79.3, 1.6), (12.2, 1.0)):
    rz = riser(ln); add(DL, tr, rz); add(DR, tr, rz)
# capa de tensión: dron grave + tono agudo con trémolo
ten = np.zeros(N); w = np.clip((T - RISK[0]) / .4, 0, 1) * np.clip((RISK[1] - T) / .3, 0, 1)
ten += (np.sin(2 * np.pi * note(26) * T) * .5 + band(saw(note(38), N), 30, 300) * .4 + np.sin(2 * np.pi * note(82) * T) * (.5 + .5 * np.sin(2 * np.pi * 5 * T)) * .05) * w
ten = np.stack([ten, ten * .95])
# compresión lateral (bombeo) con cada bombo
pump = np.ones(N)
for kb in kicks:
    i = int(kb * SR); n = min(N - i, int(.35 * SR));
    if n > 0: pump[i:i + n] = np.minimum(pump[i:i + n], 1 - .55 * np.exp(-np.arange(n) / SR / .09))
drums = np.stack([DL, DR]); snr = band(SNR, 150, 12000); snr_rev = reverb(snr, 1.6, 3.0)
drums += np.stack([snr + snr_rev * .6, snr + reverb(snr, 1.6, 3.0, seed=2) * .6])
arp_g = curve([(0, .35), (5.9, .5), (6, .8), (50.6, .8), (50.7, 0), (59.2, 0), (59.21, 1.1), (67.9, .9), (80.9, .4), (83.95, .7), (89.5, .45), (90, .35)])
bass_g = curve([(0, .3), (5.9, .5), (6, .85), (50.6, .85), (50.7, .25), (59.15, .25), (59.2, 1.1), (67.9, .9), (80.9, .6), (83.95, .7), (90, .4)])
drum_g = curve([(0, .7), (50.6, 1), (50.7, .7), (59.15, .7), (59.2, 1.1), (67.9, .95), (90, .8)])
mus = pad * .9 * pump + np.stack([bass, bass]) * bass_g * pump * .9 + arp * arp_g * pump + drums * drum_g + ten * .4
mus /= np.abs(mus).max()
# volumen: 19 % sin texto, 15.5 % con subtítulos o cifras (la mezcla con voz baja un poco más bajo la voz)
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(0.2 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); kk = smooth(kk, int(.3 * SR)); g = g * kk
mus *= g * 1.75  # la normalización por pico es conservadora (platillos/impactos); esto deja la música al nivel de los otros reels

# ---------------- EFECTOS ----------------
def ding(p):
    n = int(1.4 * SR); tt = np.arange(n) / SR; f = 1318.5 * p
    s = np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt / 0.2) + 0.25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / 0.12)
    return s * env_ad(n, 0.002, 0.45) * 0.5
def pop(p):
    n = int(0.14 * SR); tt = np.arange(n) / SR; f = (380 + 650 * np.exp(-tt / 0.025)) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.045)
def whoosh(p):
    n = int(0.6 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n); m = tt / tt[-1]
    s = band(x, 250 * p, 1200 * p) * (1 - m) + band(x, 1200 * p, 5000 * p) * m * .7
    return s * np.sin(np.pi * np.clip(tt / .55, 0, 1)) ** 2 * 1.4
def tick(p):
    n = int(0.03 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 2100 * p * tt) * env_ad(n, 0.001, 0.006) * .6
def click(p):
    n = int(0.09 * SR); x = band(rng.standard_normal(n), 2000, 9000); e = np.zeros(n); e[:int(.008 * SR)] = 1; e[int(.045 * SR):int(.05 * SR)] = .6; return x * e * 1.2
def key(p):
    n = int(0.06 * SR); tt = np.arange(n) / SR
    return (band(rng.standard_normal(n), 1500, 8000) * .8 + np.sin(2 * np.pi * 900 * p * tt) * .3) * np.exp(-tt / .008) + band(rng.standard_normal(n), 200, 1200) * np.exp(-tt / .02) * .3
def type_(p): return key(p * 1.3) * .6
def shine(p):
    out = np.zeros(int(1.1 * SR))
    for i, m in enumerate([84, 88, 91, 96, 100]):
        n = int(0.6 * SR); tt = np.arange(n) / SR; s = np.sin(2 * np.pi * note(m) * p * tt) * env_ad(n, 0.002, 0.15) * .25
        j = int(i * .05 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def chime(p):
    out = np.zeros(int(1.3 * SR))
    for i, m in enumerate((76, 80, 83)):
        n = int(1.1 * SR); tt = np.arange(n) / SR; f = note(m) * p
        s = (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / .2)) * env_ad(n, .002, .4) * .3
        j = int(i * .06 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def beep(p):
    n = int(.12 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 1450 * p * tt) * env_ad(n, .003, .05) * .5
def hum(p):
    n = int(1.6 * SR); tt = np.arange(n) / SR; f = 110 * p * (1 + .04 * tt)
    s = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in (1, 2, 3, 4, 6)) * (1 + .4 * np.sin(2 * np.pi * 60 * tt))
    cr = (rng.random(n) > .996) * rng.uniform(-1, 1, n)
    return (band(s, 60, 3000) * .35 + band(cr, 2000, 9000) * .5) * env_ad(n, .06, .6)
def boot(p):
    out = np.zeros(int(.9 * SR))
    for i, f in enumerate((660, 880, 990, 1320, 1760)):
        n = int(.05 * SR); tt = np.arange(n) / SR; s = np.sign(np.sin(2 * np.pi * f * p * tt)) * env_ad(n, .002, .02) * .18
        j = int(i * .07 * SR); out[j:j + n] += s
    n = len(out); tt = np.arange(n) / SR; out += band(rng.standard_normal(n), 2000, 7000) * np.sin(np.pi * tt / tt[-1]) * .15
    return out
def flash(p):
    out = np.zeros(int(1.4 * SR)); x = shine(1.15 * p); out[:min(len(x), len(out))] = x[:len(out)]; n = len(out); tt = np.arange(n) / SR
    return out + band(rng.standard_normal(n), 4000, 14000) * np.exp(-tt / .25) * .5
def scan(p):
    n = int(.6 * SR); tt = np.arange(n) / SR; f = (800 + 1600 * tt / tt[-1]) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (.5 + .5 * np.sin(2 * np.pi * 30 * tt)) * np.sin(np.pi * tt / tt[-1]) * .25
def gate(p):
    n = int(.45 * SR); tt = np.arange(n) / SR; f = (1800 - 1200 * tt / tt[-1]) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, .003, .12) * .3 + whoosh(1.4)[:n] * .5
def coaster(p):  # recorrido del simulador: rumor + viento + juntas del riel que aceleran
    n = int(5.2 * SR); tt = np.arange(n) / SR; sp = np.clip(.4 + .6 * np.sin(np.pi * tt / tt[-1]), 0, 1)
    x = band(rng.standard_normal(n), 40, 220) * .9 + band(rng.standard_normal(n), 300, 3000) * sp * .5
    out = x * sp * np.clip(tt / .2, 0, 1) * np.clip((tt[-1] - tt) / .4, 0, 1)
    tj = 0.0
    while tj < 5.0:
        j = int(tj * SR); m = int(.03 * SR); out[j:j + m] += band(rng.standard_normal(m), 800, 5000) * np.exp(-np.arange(m) / SR / .006) * .5; tj += .28 - .14 * np.sin(np.pi * tj / 5)
    return out * .8
def counter(p):
    out = np.zeros(int(1.6 * SR)); tj = 0.0; k = 0
    while tj < 1.15:
        c = tick(1 + k * .01)[: int(.03 * SR)]; j = int(tj * SR); out[j:j + len(c)] += c * .7; tj += .09 * (1 - tj / 1.4) + .02; k += 1
    d = ding(1.2)[: len(out) - int(1.15 * SR)]; out[int(1.15 * SR):] += d * .7; return out
def zap(p):
    n = int(.35 * SR); tt = np.arange(n) / SR; f = 3000 * p * np.exp(-tt / .08) + 200
    return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .25 + band(rng.standard_normal(n), 2000, 9000) * .3) * env_ad(n, .002, .07)
def rise(p): return riser(1.2, 400, 5000) * .8
def clank(p):
    n = int(.6 * SR); tt = np.arange(n) / SR
    ring = sum(a * np.sin(2 * np.pi * f * p * tt) * np.exp(-tt / d) for f, a, d in ((420, .5, .25), (1130, .35, .15), (2280, .25, .08), (3410, .15, .05)))
    thump = np.sin(2 * np.pi * np.cumsum(60 + 80 * np.exp(-tt / .02)) / SR) * np.exp(-tt / .08)
    return np.tanh((ring * .6 + thump * .8 + band(rng.standard_normal(n), 1500, 8000) * np.exp(-tt / .01)) * 1.2) * .7
def stamp(p):
    n = int(.4 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 80 * p * tt) * np.exp(-tt / .06) + band(rng.standard_normal(n), 200 * p, 2500 * p) * np.exp(-tt / .03)
def thud(p):
    n = int(.4 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 70 * p * tt) * np.exp(-tt / .08) + band(rng.standard_normal(n), 100, 800) * np.exp(-tt / .03) * .5
def wind(p):  # viento con eco en el camino gris
    n = int(8.4 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n)
    s = band(x, 150, 900) * (.55 + .45 * np.sin(2 * np.pi * .23 * tt + 1)) + band(x, 900, 2600) * (.3 + .3 * np.sin(2 * np.pi * .37 * tt)) * .5
    s *= np.clip(tt / 1.2, 0, 1) * np.clip((tt[-1] - tt) / .6, 0, 1); out = s.copy()
    for dly, g in ((.32, .45), (.64, .25), (.96, .12)):
        d = int(dly * SR); out[d:] += s[:-d] * g
    return out * .8
def lock(p):
    n = int(.5 * SR); tt = np.arange(n) / SR
    clk = band(rng.standard_normal(n), 2500, 9000) * (np.exp(-tt / .004) + (tt > .07) * np.exp(-np.clip(tt - .07, 0, None) / .004))
    return clk * .9 + np.sin(2 * np.pi * 90 * tt) * np.exp(-tt / .07) * .8 + sum(np.sin(2 * np.pi * f * tt) * np.exp(-tt / .09) for f in (1700, 2650)) * .12
def rewind(p):
    n = int(.9 * SR); tt = np.arange(n) / SR; f = 200 + 2600 * (tt / tt[-1]) ** 2
    ch = np.sign(np.sin(2 * np.pi * np.cumsum(f * .5) / SR)) * .15
    return (band(rng.standard_normal(n), 400, 6000) * (tt / tt[-1]) ** 1.5 * .7 + ch * (tt / tt[-1])) * np.clip((tt[-1] - tt) / .05, 0, 1)
def shatter(p):
    n = int(1.4 * SR); tt = np.arange(n) / SR; out = band(rng.standard_normal(n), 2500, 14000) * np.exp(-tt / .07) * 1.1
    for k in range(40):
        j = int(rng.uniform(0, .8) * SR); m = int(.05 * SR); f = rng.uniform(2500, 8000)
        out[j:j + m] += np.sin(2 * np.pi * f * np.arange(m) / SR) * np.exp(-np.arange(m) / SR / .01) * rng.uniform(.2, .6)
    return out + np.sin(2 * np.pi * np.cumsum(90 * np.exp(-tt / .3) + 40) / SR) * np.exp(-tt / .25) * .8
def powerup(p):
    n = int(1.4 * SR); tt = np.arange(n) / SR; f = 180 * 2 ** (2.6 * (tt / tt[-1]) ** .7)
    s = sum(np.sin(2 * np.pi * np.cumsum(f * h) / SR) / h for h in (1, 2, 3)) * .3
    sh = np.zeros(n); x = shine(1.0)[:n]; sh[:len(x)] = x
    return s * np.clip(tt / .05, 0, 1) * np.clip((tt[-1] - tt) / .3, 0, 1) + sh * .6
def impact(p):  # golpe cinematográfico: caída de sub + grieta + cola
    n = int(2.6 * SR); tt = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(32 + 70 * np.exp(-tt / .08)) / SR) * np.exp(-tt / .7)
    crack = band(rng.standard_normal(n), 800, 9000) * np.exp(-tt / .03) * .7
    body = band(rng.standard_normal(n), 60, 500) * np.exp(-tt / .25) * .6
    x = np.tanh((sub * 1.2 + crack + body) * 1.2)
    return x + reverb(x, 1.4, 2.5)[:n] * .5
def glitch(p):
    n = int(.5 * SR); out = np.zeros(n)
    for k in range(9):
        j = int(rng.uniform(0, .42) * SR); m = int(rng.uniform(.015, .05) * SR); x = band(rng.standard_normal(m), 500, 9000)
        out[j:j + m] += np.round(x * 4) / 4 * .5
    tt = np.arange(n) / SR; return out + np.sign(np.sin(2 * np.pi * 220 * tt)) * (np.sin(2 * np.pi * 30 * tt) > .7) * .08
GEN = dict(ding=(ding, .3), pop=(pop, .3), whoosh=(whoosh, .24), tick=(tick, .2), click=(click, .45), key=(key, .32), type=(type_, .3), shine=(shine, .26),
           chime=(chime, .3), beep=(beep, .26), hum=(hum, .22), boot=(boot, .3), flash=(flash, .3), scan=(scan, .26), gate=(gate, .22), coaster=(coaster, .18),
           counter=(counter, .26), zap=(zap, .26), rise=(rise, .3), clank=(clank, .26), stamp=(stamp, .32), thud=(thud, .32), wind=(wind, .24), lock=(lock, .4),
           rewind=(rewind, .32), shatter=(shatter, .32), powerup=(powerup, .3), impact=(impact, .32), glitch=(glitch, .3))
fx = np.zeros(N)
for e in TL['sfx']:
    fn, gn = GEN[e['type']]; add(fx, e['t'], fn(e['pitch']), gn * e['v'])
fxs = np.stack([fx, fx])
mix = np.tanh((mus + fxs) * 1.0)

def save(path, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-sin-voz.wav', mix)
print('BPM %.2f' % BPM, 'peak mix', np.abs(mix).max(), 'music rms', np.sqrt((mus ** 2).mean()))
