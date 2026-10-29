"""Música electrónica cinematográfica con pulso de latido (104 BPM; 39 compases exactos en 90 s para que el loop cierre)
+ efectos sincronizados con timeline.json: clic grave con eco por botón, siseo reptil en el núcleo, una nota del acorde por
neurotransmisor en la sinapsis y el acorde completo en la lección. Sin voz."""
import json, sys, wave, numpy as np
from scipy.signal import fftconvolve
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SR = 48000; DUR = float(TL.get('duration', 90)); N = int(SR * DUR)
rng = np.random.default_rng(7)
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
def riser(len_s, f0=300, f1=6000):
    n = int(len_s * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 12
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = f0 * (f1 / f0) ** (k / seg); out[a:b] = band(x, c * .6, c * 1.6)[a:b]
    return out * (t / len_s) ** 2 * .6

# ---------------- MÚSICA ----------------
BPM = 39 * 4 * 60 / DUR; beat = 60 / BPM; bar = beat * 4; NB = int(round(DUR / bar))
SEC = [(0, 'intro'), (6.0, 'quien'), (11.0, 'tension'), (14.6, 'ride'), (19.95, 'main'), (33.85, 'break'), (37.25, 'main'), (45.78, 'sweep'),
       (50.04, 'chem'), (73.82, 'lift'), (79.6, 'build'), (81.15, 'drop'), (84.2, 'outro')]
def section(t):
    s = 'intro'
    for a, name in SEC:
        if t >= a: s = name
    return s
A_ = [45, 57, 60, 64, 69]; F_ = [41, 53, 57, 60, 65]; C_ = [48, 55, 60, 64, 67]; G_ = [43, 55, 59, 62, 67]
P1 = [A_, F_, C_, G_]                                  # Am – F – C – G (instinto)
P2 = [F_, C_, G_, [45, 57, 60, 64, 67]]                # F – C – G – Am7 (química, más luminoso)
TENSE = [[45, 57, 59, 64, 71], [45, 56, 59, 64, 71]]   # Am(add9) ↔ E/A
FMAJ9 = [41, 53, 57, 60, 64, 67]
def chord_at(bi):
    s = section(bi * bar + .05)
    if s == 'tension': return TENSE[bi % 2]
    if s in ('chem', 'lift'): return P2[bi % 4]
    if s == 'drop': return FMAJ9
    return P1[bi % 4]

padL = np.zeros(N); padR = np.zeros(N); bass = np.zeros(N); arpL = np.zeros(N); arpR = np.zeros(N)
for bi in range(NB + 1):
    t0 = bi * bar; ch = chord_at(bi); n = int(bar * SR * 1.15); s = section(t0 + .05)
    if t0 >= DUR: break
    e = env_ad(n, .3, 2.4); e[-int(.3 * SR):] *= np.linspace(1, 0, int(.3 * SR))
    for j, m in enumerate(ch[1:]):
        for d, (gl, gr) in zip((-.09, 0, .09), ((1, .55), (.8, .8), (.55, 1))):
            x = saw(note(m + d), n, ph=(j * .17 + d) % 1) * e * .05
            add(padL, t0, x * gl); add(padR, t0, x * gr)
    root = note(ch[0] - 12 if ch[0] > 44 else ch[0])
    steps = {'ride': 16, 'main': 8, 'chem': 8, 'lift': 8, 'build': 16, 'sweep': 4}.get(s, 2)
    for q in range(steps):
        tq = t0 + q * bar / steps; m = int(.9 * bar / steps * SR) if steps > 2 else int(bar * .5 * SR)
        oc = 2 if (s == 'chem' and q % 2) else 1
        x = (saw(root * oc, m) * .55 + np.sin(2 * np.pi * root * oc * np.arange(m) / SR)) * env_ad(m, .004, .12 if steps > 2 else 1.0)
        add(bass, tq, x * (.9 if q % 4 == 0 else .7))
    if s in ('quien', 'ride', 'main', 'chem', 'lift', 'outro', 'intro', 'build'):
        tones = [m + 12 for m in ch[1:4]] + [ch[1] + 24]
        pat = [0, 1, 2, 3, 2, 1, 2, 3, 0, 1, 2, 3, 3, 2, 1, 2] if s != 'chem' else [0, 2, 1, 3, 0, 2, 3, 1, 0, 2, 1, 3, 2, 3, 1, 0]
        for q in range(16):
            tq = t0 + q * bar / 16; m = int(.22 * SR); f = note(tones[pat[q] % len(tones)]); tt = np.arange(m) / SR
            if s == 'chem':  # pluck burbujeante
                x = np.sin(2 * np.pi * np.cumsum(f * (1 + .25 * np.exp(-tt / .012))) / SR) * env_ad(m, .002, .06) * .11
            else:
                x = sum(np.sin(2 * np.pi * f * h * tt) / h for h in (1, 3, 5, 7)) * env_ad(m, .002, .07) * .09
            add(arpL, tq, x * (1 if q % 2 else .7)); add(arpR, tq + .004, x * (.7 if q % 2 else 1))
# filtros y automatización
pad = np.stack([padL, padR]); dark = np.stack([band(c, 40, 800) for c in pad]); bright = np.stack([band(c, 40, 6500) for c in pad])
bpad = curve([(0, .12), (5.9, .2), (6.0, .4), (11.0, .15), (14.6, .5), (19.95, .7), (33.85, .25), (37.25, .75), (45.78, .7), (49.9, .1), (50.04, .8),
              (73.82, 1), (79.6, .8), (81.15, .55), (84.2, .45), (89.4, .15), (90, .12)])
pad = dark * (1 - bpad) + bright * bpad
bass = band(bass, 28, 900)
arp = np.stack([band(arpL, 300, 8000), band(arpR, 300, 8000)])
dl = int(beat * .75 * SR); arp[0][dl:] += arp[1][:-dl] * .35; arp[1][dl:] += arp[0][:-dl] * .35  # eco ping-pong
# batería: latido (lub-dub) como pulso principal
def thump(f0, f1, dec, secs=.4):
    n = int(secs * SR); t = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / .02)) / SR) * np.exp(-t / dec)
LUB = np.tanh(thump(115, 47, .13) * 1.7) * .95; DUB = np.tanh(thump(135, 56, .09) * 1.5) * .62
kick_n = int(.4 * SR); kt = np.arange(kick_n) / SR
KICK = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(45 + 95 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .2)) * .9 + band(rng.standard_normal(kick_n), 2000, 8000) * np.exp(-kt / .004) * .3
sn_n = int(.45 * SR); st = np.arange(sn_n) / SR
SNARE = band(rng.standard_normal(sn_n), 900, 9000) * np.exp(-st / .12) * .5 + np.sin(2 * np.pi * 185 * st) * np.exp(-st / .05) * .35
CLAP = band(rng.standard_normal(sn_n), 1000, 7000) * sum((st >= d) * np.exp(-np.clip(st - d, 0, None) / .02) for d in (0, .012, .024)) * .4
hat_n = int(.06 * SR); HAT = band(rng.standard_normal(hat_n), 7000, 16000) * np.exp(-np.arange(hat_n) / SR / .015) * .2
oh_n = int(.35 * SR); OHAT = band(rng.standard_normal(oh_n), 6000, 15000) * np.exp(-np.arange(oh_n) / SR / .1) * .14
sh_n = int(.08 * SR); SHAK = band(rng.standard_normal(sh_n), 5000, 12000) * np.sin(np.pi * np.arange(sh_n) / sh_n) * .12
cr_n = int(2.6 * SR); CRASH = band(rng.standard_normal(cr_n), 3500, 15000) * np.exp(-np.arange(cr_n) / SR / .7) * .3
def tom(f0, f1):
    n = int(.35 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / .06)) / SR) * np.exp(-t / .16) * .6
DL = np.zeros(N); DR = np.zeros(N); SNR = np.zeros(N); kicks = []
def both(t, x, g=1, pan=0): add(DL, t, x, g * (1 - pan)); add(DR, t, x, g * (1 + pan))
def heart(t, g): both(t, LUB, g); both(t + .17, DUB, g); kicks.append(t)
for k in range(int(DUR / beat) + 1):
    tb = k * beat; s = section(tb + .01); qb = k % 4
    if tb >= DUR: break
    if s in ('intro', 'outro'): heart(tb, .85)
    elif s == 'quien':
        heart(tb, .8); both(tb + beat / 2, HAT, .6, pan=.25)
    elif s == 'tension': heart(tb, 1.0 if qb in (0, 2) else .7)
    elif s == 'break': heart(tb, .9)
    elif s == 'drop': heart(tb, .9 if qb in (0, 2) else .6)
    elif s == 'sweep':
        heart(tb, .8)
        for h in range(2): both(tb + h * beat / 2, HAT, .5, pan=.25)
    else:  # ride, main, chem, lift, build
        four = s in ('ride', 'lift')
        if four or qb in (0, 2): both(tb, KICK, .95); both(tb + .17, DUB, .45); kicks.append(tb)
        if s != 'ride' and qb in (1, 3): add(SNR, tb, SNARE, .85); add(SNR, tb + .003, CLAP, .8 if s in ('chem', 'lift') else .5)
        sub = 4 if s in ('ride', 'lift', 'chem', 'build') or tb > 25 else 2
        for h in range(sub): both(tb + h * beat / sub, HAT, (1 if h % 2 else .6) * .85, pan=.25)
        if s in ('chem', 'lift'):
            for h in range(4): both(tb + h * beat / 4 + .01, SHAK, .9, pan=-.3)
        if s in ('lift',) or (s == 'main' and tb > 37.25): both(tb + beat / 2, OHAT, .8, pan=-.2)
# platillos y redobles en los cambios de sección
for tc in (6.0, 19.95, 37.25, 50.04, 73.82, 81.15):
    both(tc, CRASH, 1.0, pan=.1)
for tf in (19.95, 37.25, 50.04, 73.82):
    for i, (a, b) in enumerate(((200, 95), (160, 80), (130, 66), (110, 55))): both(tf - .5 + i * .12, tom(a, b), .7, pan=(i - 1.5) * .2)
for i in range(40):  # redoble que crece antes de MENTE
    tt = 79.6 + 1.5 * (1 - (1 - i / 40) ** 1.6)
    add(SNR, tt, SNARE, .25 + .6 * i / 40)
for tr, ln in ((18.75, 1.2), (35.9, 1.35), (48.4, 1.6), (72.45, 1.35), (79.6, 1.55), (4.9, 1.1)):
    rz = riser(ln); add(DL, tr, rz); add(DR, tr, rz)
# capa de tensión (85 %): dron grave con trémolo
ten = np.zeros(N); w = np.clip((T - 11.0) / .4, 0, 1) * np.clip((14.7 - T) / .3, 0, 1)
ten += (np.sin(2 * np.pi * note(33) * T) * .55 + band(saw(note(45), N), 30, 300) * .35 + np.sin(2 * np.pi * note(81) * T) * (.5 + .5 * np.sin(2 * np.pi * 4 * T)) * .04) * w
ten = np.stack([ten, ten * .95])
# compresión lateral (bombeo) con cada golpe
pump = np.ones(N)
for kb in kicks:
    i = int(kb * SR); n = min(N - i, int(.35 * SR))
    if n > 0: pump[i:i + n] = np.minimum(pump[i:i + n], 1 - .5 * np.exp(-np.arange(n) / SR / .09))
drums = np.stack([DL, DR]); snr = band(SNR, 150, 12000)
drums += np.stack([snr + reverb(snr, 1.6, 3.0) * .6, snr + reverb(snr, 1.6, 3.0, seed=2) * .6])
arp_g = curve([(0, .25), (5.9, .25), (6.0, .5), (10.9, .5), (11.0, .12), (14.5, .12), (14.6, .9), (19.9, .9), (19.95, .8), (33.8, .8), (33.85, .18), (37.2, .2),
               (37.25, .8), (45.7, .8), (49.9, .35), (50.04, .95), (73.8, .95), (73.82, 1.05), (79.5, .9), (81.1, .6), (81.15, .15), (84.1, .2), (84.2, .45), (90, .3)])
bass_g = curve([(0, .35), (5.9, .4), (6.0, .5), (11.0, .65), (14.5, .65), (14.6, .9), (33.8, .85), (33.85, .3), (37.2, .3), (37.25, .85), (45.78, .5), (50.0, .4),
                (50.04, .85), (73.82, 1.0), (79.6, .75), (81.15, .9), (84.1, .7), (84.2, .45), (90, .35)])
drum_g = curve([(0, .8), (14.5, .8), (14.6, 1.0), (33.8, 1.0), (33.85, .85), (37.2, .85), (37.25, 1.0), (90, .9)])
mus = pad * .9 * pump + np.stack([bass, bass]) * bass_g * pump * .9 + arp * arp_g * pump + drums * drum_g + ten * .45
mus /= np.abs(mus).max()
# volumen: 19 % sin texto, 15.5 % con subtítulos o cifras (la mezcla con voz baja un poco más bajo la voz)
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(0.2 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); kk = smooth(kk, int(.3 * SR)); g = g * kk
mus *= g * 1.5  # la normalización por pico es conservadora (platillos/impactos); con el latido constante, 1.5 deja la música al nivel de los otros reels

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
def flash(p):
    out = np.zeros(int(1.4 * SR)); x = shine(1.15 * p); out[:min(len(x), len(out))] = x[:len(out)]; n = len(out); tt = np.arange(n) / SR
    return out + band(rng.standard_normal(n), 4000, 14000) * np.exp(-tt / .25) * .5
def scan(p):
    n = int(.6 * SR); tt = np.arange(n) / SR; f = (800 + 1600 * tt / tt[-1]) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (.5 + .5 * np.sin(2 * np.pi * 30 * tt)) * np.sin(np.pi * tt / tt[-1]) * .25
def counter(p):  # contador HUD: clics que aceleran durante 1.5 s y campanita al llegar a la cifra
    out = np.zeros(int(2.1 * SR)); tj = 0.0; k = 0
    while tj < 1.45:
        c = tick(1 + k * .01)[: int(.03 * SR)]; j = int(tj * SR); out[j:j + len(c)] += c * .7; tj += .09 * (1 - tj / 1.9) + .02; k += 1
    d = ding(1.2)[: len(out) - int(1.5 * SR)]; out[int(1.5 * SR):] += d * .7; return out
def zap(p):
    n = int(.35 * SR); tt = np.arange(n) / SR; f = 3000 * p * np.exp(-tt / .08) + 200
    return (np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * .25 + band(rng.standard_normal(n), 2000, 9000) * .3) * env_ad(n, .002, .07)
def rise(p): return riser(1.2, 400, 5000) * .8
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
# --- propios de este reel ---
def press(p):  # botón arcade: golpe grave + clic, con eco que se apaga
    n = int(1.1 * SR); t = np.arange(n) / SR
    thock = np.sin(2 * np.pi * np.cumsum(70 * p + 120 * p * np.exp(-t / .012)) / SR) * np.exp(-t / .07)
    clk = band(rng.standard_normal(n), 1800, 7000) * np.exp(-t / .004) * .7
    spring = np.sin(2 * np.pi * 520 * p * t) * np.exp(-t / .05) * .12
    dry = np.tanh((thock * 1.1 + clk + spring) * 1.3); out = dry.copy(); wet = band(dry, 60, 1800)
    for d, gg in ((.19, .42), (.38, .24), (.57, .12)):
        k = int(d * SR); out[k:] += wet[:n - k] * gg
    return out * .8
def hiss(p):  # siseo reptil con gruñido grave
    n = int(1.3 * SR); t = np.arange(n) / SR
    h = band(rng.standard_normal(n), 3200 * p, 10000) * (1 + .35 * np.sin(2 * np.pi * 27 * t))
    growl = band(saw(55 * p, n), 40, 400) * (1 + .5 * np.sin(2 * np.pi * 13 * t)) * .25
    return (h * .55 + growl) * np.clip(t / .06, 0, 1) * np.clip((t[-1] - t) / .5, 0, 1)
def down(p):  # apagado
    n = int(.8 * SR); t = np.arange(n) / SR; f = 700 * p * np.exp(-t / .25) + 60
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * .4 + band(rng.standard_normal(n), 300, 3000) * .15 * np.exp(-t / .2)) * env_ad(n, .005, .35)
CHORD_NOTES = [69, 72, 76, 79]  # La, Do, Mi, Sol: cada neurotransmisor toca una nota; juntas (con Fa) forman Fmaj9
def bell(f, dur=2.4):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .4)) * np.exp(-t / .9) + .35 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / .25)
    return s * np.clip(t / .004, 0, 1)
def note_(p):
    x = bell(note(CHORD_NOTES[int(round(p)) % 4])); out = x.copy()
    for d, gg in ((.29, .35), (.58, .18)):
        k = int(d * SR); out[k:] += x[:len(x) - k] * gg
    return out * .45
def chord(p):
    out = np.zeros(int(3.4 * SR))
    for i, m in enumerate([53] + CHORD_NOTES):
        x = bell(note(m), 3.2) * (.6 if i == 0 else .4); j = int(i * .045 * SR); out[j:j + len(x)] += x[:len(out) - j]
    return out * .5 + reverb(out, 2.2, 1.8)[:len(out)] * .4
def tunnel(p):  # viaje en montaña rusa: rumor, viento y anillos que pasan zumbando
    n = int(5.0 * SR); t = np.arange(n) / SR; sp = np.clip(.45 + .55 * np.sin(np.pi * np.clip(t / 4.6, 0, 1)), 0, 1)
    out = (band(rng.standard_normal(n), 35, 200) * .8 + band(rng.standard_normal(n), 400, 4000) * sp * .45) * sp * np.clip(t / .15, 0, 1) * np.clip((t[-1] - t) / .4, 0, 1)
    tj = .05
    while tj < 4.8:
        j = int(tj * SR); m = int(.12 * SR); tt = np.arange(m) / SR
        out[j:j + m] += band(rng.standard_normal(m), 900 * p, 6000) * np.sin(np.pi * tt / tt[-1]) ** 2 * .35; tj += .22 - .08 * np.sin(np.pi * tj / 4.8)
    return out * .75
def spin(p):
    n = int(1.1 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 10
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = 600 * 2 ** (2 * np.sin(np.pi * k / seg)); out[a:b] = band(x, c * .6, c * 1.8)[a:b]
    return out * (.5 + .5 * np.sin(2 * np.pi * 9 * t)) * np.sin(np.pi * t / t[-1]) * .7
def bubble(p):
    n = int(.18 * SR); t = np.arange(n) / SR; f = (280 + 900 * (1 - np.exp(-t / .03))) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, .003, .05) * .6
def confetti(p):
    n = int(1.2 * SR); out = band(rng.standard_normal(n), 5000, 15000) * np.exp(-np.arange(n) / SR / .35) * .25
    for k in range(14):
        j = int(rng.uniform(0, .7) * SR); x = pop(rng.uniform(1.2, 2.2)) * .35; out[j:j + len(x)] += x[:n - j]
    return out
def untie(p):  # cuerda que se estira y se suelta
    n = int(1.4 * SR); t = np.arange(n) / SR; f = 180 + 500 * (t / .9) ** 1.5
    creak = np.sign(np.sin(2 * np.pi * np.cumsum(f) / SR)) * band(rng.standard_normal(n), 300, 2500) * .15 * np.clip((.9 - t) / .1, 0, 1)
    j = int(.9 * SR); m = n - j; out = creak.copy(); out[j:] += band(rng.standard_normal(m), 1500, 9000) * np.exp(-np.arange(m) / SR / .02) * .7
    sh = shine(1.2)[:m]; out[j:j + len(sh)] += sh * .5; return out
def engrave(p):  # grabado láser + campanita
    n = int(1.6 * SR); t = np.arange(n) / SR; on = np.clip((.7 - t) / .05, 0, 1) * np.clip(t / .02, 0, 1)
    siz = band(rng.standard_normal(n), 2500, 12000) * (.6 + .4 * (rng.random(n) > .7)) * on * .4
    tone = np.sin(2 * np.pi * (1800 + 60 * np.sin(2 * np.pi * 14 * t)) * t) * .12 * on
    out = siz + tone; k = int(.68 * SR); d = ding(1.05); out[k:k + len(d)] += d[:n - k] * .5; return out
GEN = dict(ding=(ding, .3), pop=(pop, .3), whoosh=(whoosh, .24), tick=(tick, .2), click=(click, .45), key=(key, .32), shine=(shine, .26), chime=(chime, .3),
           beep=(beep, .26), flash=(flash, .3), scan=(scan, .26), counter=(counter, .26), zap=(zap, .26), rise=(rise, .3), impact=(impact, .32), glitch=(glitch, .3),
           press=(press, .42), hiss=(hiss, .3), down=(down, .28), note=(note_, .4), chord=(chord, .45), tunnel=(tunnel, .2), spin=(spin, .25), bubble=(bubble, .3),
           confetti=(confetti, .3), untie=(untie, .32), engrave=(engrave, .3))
fx = np.zeros(N)
for e in TL['sfx']:
    fn, gn = GEN[e['type']]; add(fx, e['t'], fn(e['pitch']), gn * e['v'])
fxs = np.stack([fx, fx])
mix = np.tanh((mus + fxs) * 1.0)

def save(path, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-sin-voz.wav', mix)
print('BPM %.2f' % BPM, 'compases', NB, 'peak mix', np.abs(mix).max(), 'music rms', np.sqrt((mus ** 2).mean()))
