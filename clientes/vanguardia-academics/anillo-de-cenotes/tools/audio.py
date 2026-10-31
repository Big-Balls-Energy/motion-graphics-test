"""Música cinematográfica ligera a 96 BPM (36 compases exactos en 90 s, así el loop cierra) para «El anillo de cenotes» (70 s, 28 compases exactos).
Arco: el cuaderno que se deshace (piano grave, La menor) → 1885 (pulso de reloj) → la curva cae (menor, tensión contenida)
→ el giro (las cuerdas entran) → las tres llaves (Do mayor, ritmo que crece) → síntesis (lo más luminoso) → cierre que resuelve. Pausas antes de cada cifra y efectos sincronizados con timeline.json. Sin voz.

Uso: python3 audio.py timeline.json <carpeta-audio>"""
import json, sys, wave, numpy as np
from scipy.signal import fftconvolve
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SR = 48000; DUR = float(TL.get('duration', 80)); N = int(SR * DUR)
rng = np.random.default_rng(17)
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
def smooth(x, k):  # media móvil O(N) con suma acumulada
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
BPM = 28 * 4 * 60 / DUR; beat = 60 / BPM; bar = beat * 4; NB = int(round(DUR / bar))
SEC = [(0, 'dim'), (3.2, 'open'), (6.5, 'data'), (12.75, 'world'), (19.8, 'build'), (28.6, 'kolb'), (40.6, 'montage'), (51.6, 'build'),
       (56.3, 'aula'), (60.6, 'cta')]
def section(t):
    s = 'dim'
    for a, name in SEC:
        if t >= a: s = name
    return s
C_ = [31, 59, 62, 67, 71]; G_ = [38, 62, 66, 69, 74]; Am = [28, 59, 64, 67, 71]; F_ = [36, 60, 64, 67, 72]; Em = [35, 59, 62, 66, 71]
PROG = [C_, G_, Am, F_]; SOC = [F_, G_, Am, Em]; END = [F_, G_, C_, C_]; DIM = [Am, F_, C_, G_]
def chord_at(t):
    s = section(t + .05); bi = int(t / bar)
    if s in ('dim', 'open', 'data') or t < 12.75: return DIM[bi % 4]
    if s == 'social': return SOC[bi % 4]
    if s == 'cta': return END[min(3, int((t - 60.6) / bar))]
    return PROG[bi % 4]
def piano(f, n, vel=1.0):  # piano suave: parciales con caída distinta y ataque de martillo
    t = np.arange(n) / SR; x = np.zeros(n)
    for h, (a, d) in enumerate(((1, 1.6), (.45, .7), (.22, .35), (.1, .2)), start=1):
        x += a * np.sin(2 * np.pi * f * h * t * (1 + .0006 * h)) * np.exp(-t / d)
    return x * np.clip(t / .004, 0, 1) * vel * .22
padL = np.zeros(N); padR = np.zeros(N); bass = np.zeros(N); pnL = np.zeros(N); pnR = np.zeros(N); strL = np.zeros(N); strR = np.zeros(N)
for bi in range(NB + 1):
    t0 = bi * bar
    if t0 >= DUR: break
    s = section(t0 + .05); ch = chord_at(t0); n = int(bar * SR * 1.2)
    e = env_ad(n, .6, 3.0); e[-int(.35 * SR):] *= np.linspace(1, 0, int(.35 * SR))
    for j, m in enumerate(ch[1:4]):
        for d, (gl, gr) in zip((-.07, 0, .07), ((1, .5), (.8, .8), (.5, 1))):
            x = saw(note(m + d), n, ph=(j * .21 + d) % 1) * e * .04
            add(padL, t0, x * gl); add(padR, t0, x * gr)
    root = note(ch[0]); m = int(bar * SR * .98); tt = np.arange(m) / SR
    add(bass, t0, np.sin(2 * np.pi * root * tt) * env_ad(m, .02, 2.2) * (0 if s == 'dim' else 1))
    # piano: arpegio en corcheas (en penumbra, solo blancas graves)
    tones = [ch[1], ch[2], ch[3], ch[1] + 12, ch[2] + 12, ch[3], ch[2], ch[1] + 12]
    step = {'dim': 4, 'open': 8, 'kolb': 8, 'data': 8, 'world': 8, 'build': 8, 'montage': 16, 'aula': 8, 'social': 4, 'cta': 8}[s]
    for q in range(step):
        tq = t0 + q * bar / step; f = note(tones[(q * (8 // step if step < 8 else 1)) % 8] + (0 if step < 16 else 12 * (q % 2)) - (12 if s == 'dim' else 0))
        x = piano(f, int(1.8 * SR), .9 if q % 4 == 0 else .65); add(pnL, tq, x * (1 if q % 2 else .75)); add(pnR, tq + .006, x * (.75 if q % 2 else 1))
    # cuerdas: acordes largos con ataque lento (el mundo, el montaje y el cierre)
    if s in ('world', 'build', 'montage', 'aula', 'cta', 'social'):
        ns = int(bar * SR * 1.25); es = env_ad(ns, 1.1 if s != 'montage' else .5, 3.5); es[-int(.4 * SR):] *= np.linspace(1, 0, int(.4 * SR))
        for j, m2 in enumerate([ch[0] + 12, ch[1], ch[2], ch[3] + 12]):
            for d in (-.09, .09):
                x = band(saw(note(m2 + d), ns), 150, 3200) * es * .035; add(strL, t0, x * (1.2 if d < 0 else .8)); add(strR, t0, x * (.8 if d < 0 else 1.2))
pad = np.stack([padL, padR]); dark = np.stack([band(c, 40, 900) for c in pad]); bright = np.stack([band(c, 40, 6000) for c in pad])
bpad = curve([(0, .2), (3.2, .5), (6.5, .35), (12.75, .9), (19.8, .6), (28.6, .7), (40.6, .9), (51.6, .6), (56.3, 1), (60.6, .7), (70, .2)])
pad = dark * (1 - bpad) + bright * bpad
bass = band(bass, 28, 400)
pn = np.stack([pnL, pnR]); pn = pn + np.stack([reverb(pnL, 2.2, 2.0), reverb(pnR, 2.2, 2.0, seed=3)]) * .5
strs = np.stack([strL, strR]); strs = strs + np.stack([reverb(strL, 2.6, 1.6, seed=4), reverb(strR, 2.6, 1.6, seed=5)]) * .4
# batería suave
kick_n = int(.4 * SR); kt = np.arange(kick_n) / SR
KICK = np.sin(2 * np.pi * np.cumsum(48 + 70 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .22) * .8
sn_n = int(.4 * SR); st = np.arange(sn_n) / SR
CLAP = band(rng.standard_normal(sn_n), 1000, 7000) * sum((st >= d) * np.exp(-np.clip(st - d, 0, None) / .025) for d in (0, .011, .022)) * .32
sh_n = int(.09 * SR); SHK = band(rng.standard_normal(sh_n), 5000, 14000) * np.sin(np.pi * np.arange(sh_n) / sh_n) ** 2 * .13
rim_n = int(.05 * SR); RIM = band(rng.standard_normal(rim_n), 1500, 6000) * np.exp(-np.arange(rim_n) / SR / .006) * .35
cr_n = int(3.0 * SR); SWELL = band(rng.standard_normal(cr_n), 3000, 13000) * np.exp(-np.arange(cr_n) / SR / .9) * .16
def tom(f0, f1):
    n = int(.4 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / .06)) / SR) * np.exp(-t / .2) * .45
DL = np.zeros(N); DR = np.zeros(N); kicks = []
def both(t, x, g=1, pan=0): add(DL, t, x, g * (1 - pan)); add(DR, t, x, g * (1 + pan))
def kick(t, g=.9): both(t, KICK, g); kicks.append(t)
for k in range(int(DUR / beat) + 1):
    tb = k * beat; s = section(tb + .01); qb = k % 4
    if tb >= DUR: break
    if s in ('dim', 'open'): continue
    if s == 'social':
        if qb == 0: kick(tb, .5)
        continue
    if s in ('kolb', 'cta'):
        if qb in (0, 2): kick(tb, .55)
        both(tb + beat / 2, SHK, .6, pan=.3)
    elif s in ('data', 'world', 'build'):
        if qb in (0, 2): kick(tb, .75)
        if qb == 3: both(tb + beat / 2, RIM, .55, pan=-.3)
        for h in range(2): both(tb + h * beat / 2, SHK, .9 if h else .55, pan=.3)
    else:  # montage, aula: la parte con más energía
        kick(tb, .85)
        if qb in (1, 3): both(tb, CLAP, .85, pan=.05)
        for h in range(4): both(tb + h * beat / 4, SHK, 1 if h % 2 else .6, pan=.3)
for tc in (3.2, 12.75, 19.8, 28.6, 40.85, 51.6, 56.3, 60.6):
    both(tc, SWELL, 1.0, pan=.1)
for tf in (12.75, 40.85, 56.3):  # redobles suaves que llevan a la cifra o la frase
    for i, (a, b) in enumerate(((180, 90), (150, 76), (125, 62), (105, 52))): both(tf - .5 + i * .12, tom(a, b), .5, pan=(i - 1.5) * .2)
for tr, ln in ((5.2, 1.2), (11.4, 1.3), (26.4, 1.2), (39.6, 1.0), (55.1, 1.2)):
    rz = riser(ln, 300, 5000) * .7; add(DL, tr, rz); add(DR, tr, rz)
pump = np.ones(N)
for kb in kicks:
    i = int(kb * SR); n = min(N - i, int(.3 * SR))
    if n > 0: pump[i:i + n] = np.minimum(pump[i:i + n], 1 - .3 * np.exp(-np.arange(n) / SR / .09))
drums = np.stack([DL, DR])
pn_g = curve([(0, 1), (12.75, .8), (28.6, 1.0), (40.6, .8), (56.3, .9), (60.6, 1), (70, .9)])
pad_g = curve([(0, .7), (3.2, .9), (12.75, 1.05), (28.6, .9), (40.6, 1), (56.3, 1.05), (60.6, 1), (70, .7)])
str_g = curve([(0, .2), (6.5, .4), (12.75, 1.1), (19.8, .7), (28.6, .9), (40.6, 1.0), (56.3, 1.2), (60.6, .9), (70, .6)])
drum_g = curve([(0, .6), (6.5, .8), (12.75, .9), (28.6, .8), (40.6, 1.05), (51.6, .8), (56.3, .9), (60.6, .7), (70, .6)])
mus = pad * pad_g * pump + np.stack([bass, bass]) * .55 * pump + pn * pn_g + strs * str_g + drums * drum_g
mus /= np.abs(mus).max()
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(0.2 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); kk = smooth(kk, int(.3 * SR)); g = g * kk
dip = np.ones(N)
for a, b in TL.get('musicDips', []):
    i0, i1 = int(a * SR), int(b * SR); f0 = int(.08 * SR); f1 = int(.03 * SR)
    dip[i0:i0 + f0] = np.minimum(dip[i0:i0 + f0], np.linspace(1, .12, f0)); dip[i0 + f0:i1] = .12; dip[i1:i1 + f1] = np.minimum(dip[i1:i1 + f1], np.linspace(.12, 1, f1))
mus *= g * dip * 1.5
fo = int(.05 * SR); mus[:, -fo:] *= np.linspace(1, 0, fo)

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
    for i, m in enumerate([86, 89, 93, 98, 101]):
        n = int(0.6 * SR); tt = np.arange(n) / SR; s = np.sin(2 * np.pi * note(m) * p * tt) * env_ad(n, 0.002, 0.15) * .25
        j = int(i * .05 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def chime(p):
    out = np.zeros(int(1.3 * SR))
    for i, m in enumerate((74, 77, 81)):
        n = int(1.1 * SR); tt = np.arange(n) / SR; f = note(m) * p
        s = (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / .2)) * env_ad(n, .002, .4) * .3
        j = int(i * .06 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def flash(p):
    out = np.zeros(int(1.4 * SR)); x = shine(1.1 * p); out[:min(len(x), len(out))] = x[:len(out)]; n = len(out); tt = np.arange(n) / SR
    return out + band(rng.standard_normal(n), 4000, 14000) * np.exp(-tt / .25) * .5
def scan(p):
    n = int(1.4 * SR); tt = np.arange(n) / SR; f = (700 + 1400 * tt / tt[-1]) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * (.5 + .5 * np.sin(2 * np.pi * 26 * tt)) * np.sin(np.pi * tt / tt[-1]) * .22
def rise(p): return riser(1.0, 400, 5000) * .9
def impact(p):  # golpe cinematográfico: caída de sub + grieta + cola
    n = int(2.6 * SR); tt = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(32 * p + 70 * np.exp(-tt / .08)) / SR) * np.exp(-tt / .7)
    crack = band(rng.standard_normal(n), 800, 9000) * np.exp(-tt / .03) * .7
    body = band(rng.standard_normal(n), 60, 500) * np.exp(-tt / .25) * .6
    x = np.tanh((sub * 1.2 + crack + body) * 1.2)
    return x + reverb(x, 1.4, 2.5)[:n] * .5
def hit(p):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    x = np.tanh(np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-tt / .05)) / SR) * np.exp(-tt / .3) * 1.4 + band(rng.standard_normal(n), 1500, 8000) * np.exp(-tt / .02) * .4)
    return x * .8 + reverb(x, 1.2, 3)[:n] * .35
def sweep(p):  # barrido de interfaz
    n = int(.5 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 10
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = 600 * p * 8 ** (k / seg); out[a:b] = band(x, c * .6, c * 1.5)[a:b]
    bl = np.sin(2 * np.pi * np.cumsum(900 * p + 1200 * p * tt / tt[-1]) / SR) * .12
    return (out * .7 + bl) * np.sin(np.pi * tt / tt[-1]) ** 1.5
def lock(p):  # un bloque encaja
    n = int(.25 * SR); out = np.zeros(n)
    for d, f in ((0, 1900), (.06, 2600)):
        j = int(d * SR); m = int(.05 * SR); out[j:j + m] += np.sin(2 * np.pi * f * p * np.arange(m) / SR) * env_ad(m, .001, .015) * .5
    c = click(1); out[:len(c)] += c * .3; return out
def ping(p):
    n = int(.9 * SR); tt = np.arange(n) / SR; f = 1760 * p
    return (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2.01 * tt) * np.exp(-tt / .08)) * env_ad(n, .001, .22) * .45
def assemble(p):  # miles de partículas que se juntan: crepitar que se acelera y tono que sube
    n = int(.75 * SR); tt = np.arange(n) / SR; out = np.zeros(n); dens = (tt / tt[-1]) ** 1.5
    hits = rng.random(n) < (.002 + .03 * dens); out += band(hits * rng.standard_normal(n), 2500, 12000) * 1.2
    out += np.sin(2 * np.pi * np.cumsum(300 * p * 4 ** (tt / tt[-1])) / SR) * dens * .15
    return out * np.clip((tt[-1] - tt) / .03, 0, 1)
def morph(p):
    n = int(.8 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 800, 7000)
    ph = x * (.5 + .5 * np.sin(2 * np.pi * (3 + 9 * tt) * tt)); gl = np.sin(2 * np.pi * np.cumsum(500 * p + 900 * p * tt) / SR) * .1
    return (ph * .5 + gl) * np.sin(np.pi * tt / tt[-1])
def blip(p):
    n = int(.1 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 1300 * p * tt) * env_ad(n, .002, .03) * .5
def dissolve(p):  # desintegración por bloques: ráfagas cuantizadas que se deshacen y bajan
    n = int(1.6 * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for k in range(44):
        j = int(rng.uniform(0, 1.35) * SR); m = int(rng.uniform(.01, .05) * SR); x = band(rng.standard_normal(m), 600, 10000)
        out[j:j + m] += (np.round(x * 3) / 3)[: n - j] * (1 - j / n) * .5
    down = np.sin(2 * np.pi * np.cumsum(1800 * p * np.exp(-tt / .45) + 80) / SR) * np.exp(-tt / .6) * .25
    sw = band(rng.standard_normal(n), 2000, 9000) * np.sin(np.pi * np.clip(tt / 1.45, 0, 1)) ** 2 * .35
    return out + down + sw
def select(p):  # la IA elige: acorde corto + brillo
    out = np.zeros(int(1.6 * SR))
    for i, m in enumerate((62, 65, 69, 74)):
        n = int(1.4 * SR); tt = np.arange(n) / SR; f = note(m) * p
        s = (np.sin(2 * np.pi * f * tt) + .35 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / .15)) * env_ad(n, .003, .45) * .22
        j = int(i * .03 * SR); out[j:j + n] += s[: len(out) - j]
    sh = shine(1.0); out[:len(sh)] += sh * .6; return out
def pulse(p):  # pulso de la red
    n = int(.7 * SR); tt = np.arange(n) / SR
    th = np.sin(2 * np.pi * np.cumsum(60 * p + 80 * np.exp(-tt / .03)) / SR) * np.exp(-tt / .12)
    zp = np.sin(2 * np.pi * np.cumsum(2400 * p * np.exp(-tt / .05) + 300) / SR) * np.exp(-tt / .06) * .2
    return th * .8 + zp
def paper(p):  # periódico que entra flotando
    n = int(.7 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 900, 7000)
    return x * (.5 + .5 * np.abs(np.sin(2 * np.pi * 14 * tt))) * np.sin(np.pi * tt / tt[-1]) ** 2 * .9
def send(p):
    n = int(.45 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 1500, 9000)
    return x * np.sin(np.pi * tt / tt[-1]) ** 3 * .6 + np.sin(2 * np.pi * np.cumsum(600 + 1800 * tt / tt[-1]) / SR) * env_ad(n, .01, .12) * .25
def bellf(f, dur=2.4):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .4)) * np.exp(-t / .9) + .35 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / .25)
    return s * np.clip(t / .004, 0, 1)
def chord(p):
    out = np.zeros(int(3.4 * SR)); notes = [46, 57, 62, 65, 69, 72] if p > 1.05 else [50, 57, 62, 65, 69]
    for i, m in enumerate(notes):
        x = bellf(note(m), 3.2) * (.6 if i == 0 else .4); j = int(i * .045 * SR); out[j:j + len(x)] += x[:len(out) - j]
    return out * .5 + reverb(out, 2.2, 1.8)[:len(out)] * .4
def number(p):  # acento de cada número de consejo: golpe grave + brillo
    n = int(1.6 * SR); tt = np.arange(n) / SR
    th = np.tanh(np.sin(2 * np.pi * np.cumsum(50 * p + 110 * np.exp(-tt / .04)) / SR) * np.exp(-tt / .35) * 1.3) * .8
    sh = shine(p); th[:len(sh)] += sh * .7
    return th + reverb(th, 1.4, 2.4)[:n] * .35
def count(p):  # contador de 4 s: clics que se aceleran
    n = int(4.1 * SR); out = np.zeros(n); tj = 0.0; k = 0
    while tj < 4.0:
        c = tick(1 + k * .01); j = int(tj * SR); out[j:j + len(c)] += c[: n - j] * (.45 + .35 * tj / 4); tj += .16 * (1 - tj / 4.6) + .03; k += 1
    return out
def door(p):  # puertas que se deslizan: aire + golpe suave al final
    n = int(.8 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 300, 3000) * np.sin(np.pi * np.clip(tt / .42, 0, 1)) ** 2 * .7
    q = np.clip(tt - .42, 0, None); th = np.sin(2 * np.pi * np.cumsum(70 + 60 * np.exp(-q / .04)) / SR) * np.exp(-q / .12) * (tt >= .42) * .5
    return x + th
def meter(p):  # el medidor sube: blips ascendentes y un ping
    out = np.zeros(int(1.2 * SR))
    for i in range(4):
        b = blip(p * (1 + i * .12)) if i < 3 else ping(p * 1.2); j = int(i * .11 * SR); out[j:j + len(b)] += b[: len(out) - j] * (.8 if i < 3 else .9)
    return out
def flip(p):  # hoja de calendario
    n = int(.09 * SR); tt = np.arange(n) / SR; return band(rng.standard_normal(n), 1200, 7000) * np.exp(-tt / .02) * np.sin(np.pi * tt / tt[-1]) * .9
def strike(p):  # trazo de plumón que tacha
    n = int(.36 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 900, 6000) * (.6 + .4 * np.sin(2 * np.pi * 40 * tt))
    return x * np.sin(np.pi * tt / tt[-1]) * .7

# --- propios de este reel ---
def room(p):  # aire del salón en penumbra: zumbido de lámparas y tic del reloj
    n = int(2.8 * SR); tt = np.arange(n) / SR; x = (np.sin(2 * np.pi * 120 * tt) * .04 + band(rng.standard_normal(n), 200, 1200) * .12) * np.clip(tt / .4, 0, 1) * np.clip((2.8 - tt) / .3, 0, 1)
    for k in range(5): c = tick(.6); j = int((.2 + k * .55) * SR); x[j:j + len(c)] += c * .5
    return x
def chalk(p):  # gis en el pizarrón
    n = int(.9 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 1800, 6000) * (.5 + .5 * np.sign(np.sin(2 * np.pi * 7 * tt))) * np.sin(np.pi * tt / tt[-1]) * .5
    return x
def creak(p):  # las paredes empiezan a ceder
    n = int(.5 * SR); tt = np.arange(n) / SR; f = 90 + 40 * np.sin(2 * np.pi * 3 * tt)
    return band(np.sin(2 * np.pi * np.cumsum(f) / SR) * (1 + .8 * np.sign(np.sin(2 * np.pi * 31 * tt))), 60, 2500) * np.sin(np.pi * tt / tt[-1]) * .5
def thud(p):  # caen: golpe grave y polvo
    x = hit(.8); n = len(x); tt = np.arange(n) / SR; return x + band(rng.standard_normal(n), 300, 4000) * np.exp(-tt / .4) * .3
def airy(p):  # aire luminoso del exterior
    n = int(2.2 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 2500, 11000) * np.sin(np.pi * tt / tt[-1]) ** 2 * .35
    sh = shine(.9); x[:len(sh)] += sh * .5
    return x
def shutter(p):  # obturador de cámara
    n = int(.18 * SR); out = np.zeros(n)
    for d in (0, .07): c = click(1); j = int(d * SR); out[j:j + len(c)] += c[: n - j] * (1 if d == 0 else .7)
    return out
def develop(p):  # la polaroid se revela: brillo que crece
    n = int(2.4 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * note(81) * tt) * (tt / tt[-1]) * np.exp(-np.clip(tt - 2.0, 0, None) / .2) * .12 + band(rng.standard_normal(n), 3000, 9000) * (tt / tt[-1]) ** 2 * .08
def ring_(p):  # aparece el anillo
    out = chime(.9); n = len(out); tt = np.arange(n) / SR; return out + np.sin(2 * np.pi * np.cumsum(200 + 400 * np.exp(-tt / .2)) / SR) * np.exp(-tt / .4) * .2
def node(p):  # se enciende una etapa
    n = int(1.0 * SR); tt = np.arange(n) / SR; f = note(74) * p
    return (np.sin(2 * np.pi * f * tt) + .3 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / .1)) * env_ad(n, .002, .35) * .5
def shuffle(p):  # sorteo: fichas que se mezclan
    n = int(1.1 * SR); out = np.zeros(n)
    for k in range(40): c = tick(.8 + rng.random() * .6); j = int(rng.uniform(0, 1.0) * SR); out[j:j + len(c)] += c[: n - j] * .6
    return out + band(rng.standard_normal(n), 1500, 7000) * np.sin(np.pi * np.arange(n) / n) * .12
def ticket(p):  # boleto que entra: papel + golpe suave
    x = paper(1.2 * p)[: int(.4 * SR)]; n = len(x); tt = np.arange(n) / SR; return x + np.sin(2 * np.pi * 180 * p * tt) * np.exp(-tt / .05) * .3
def down(p):  # flecha que baja
    n = int(.6 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(900 - 600 * tt / tt[-1]) / SR) * env_ad(n, .01, .25) * .35
def upch(p):  # flecha que sube: acorde brillante
    return select(1.0)
def plane(p):  # paso de un avión (ruta que vuela)
    n = int(1.6 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 300 * p, 2500 * p) * np.sin(np.pi * tt / tt[-1]) ** 2
    return x * (.6 + .4 * np.sin(2 * np.pi * (2 + 4 * tt) * tt)) * .6
def stamp(p):  # sello de pasaporte: golpe seco de madera + papel
    n = int(.5 * SR); tt = np.arange(n) / SR
    th = np.sin(2 * np.pi * np.cumsum(140 * p + 200 * np.exp(-tt / .01)) / SR) * np.exp(-tt / .06)
    return np.tanh(th * 1.6 + band(rng.standard_normal(n), 800, 6000) * np.exp(-tt / .015) * .8) * .8
def pen(p):  # trazo de pluma sobre papel
    n = int(1.2 * SR); tt = np.arange(n) / SR; return band(rng.standard_normal(n), 2000, 8000) * (.4 + .6 * np.abs(np.sin(2 * np.pi * 5 * tt))) * np.sin(np.pi * tt / tt[-1]) * .3
def zoomin(p):  # la cámara entra al mapa
    w = whoosh(.8); r = rise(1.0); w[:min(len(w), len(r))] += r[:len(w)] * .4
    return w
def whip(p):  # barrido rápido entre fotos
    n = int(.35 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 600 * p, 6000 * p)
    return x * np.sin(np.pi * tt / tt[-1]) ** 3 * 1.3
def zoomout(p):  # el mosaico se aleja
    x = whoosh(.7); return x[::-1].copy() * .9
def tickclock(p):  # cronómetro de Ebbinghaus
    n = int(5.4 * SR); out = np.zeros(n)
    for k in range(int(5.3 / .25)): c = tick(1.3 if k % 4 == 0 else 1.0); j = int(k * .25 * SR); out[j:j + len(c)] += c[: n - j] * .6
    return out
def fall(p):  # la curva cae: tono que baja
    n = int(1.4 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(880 * np.exp(-tt / .5) + 120) / SR) * env_ad(n, .01, .6) * .3
def crack(p):  # el trazo se quiebra
    n = int(.8 * SR); tt = np.arange(n) / SR; return band(rng.standard_normal(n), 1500, 11000) * np.exp(-tt / .05) * 1.0 + band(rng.standard_normal(n), 200, 2000) * np.exp(-tt / .2) * .4
def heartbeat(p):  # latido
    n = int(.35 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(45 + 40 * np.exp(-tt / .03)) / SR) * np.exp(-tt / .09) * 1.1
def glass(p):  # barra de cristal que sube
    n = int(1.4 * SR); tt = np.arange(n) / SR; f = (400 + 900 * tt / 1.0) * p
    s = np.sin(2 * np.pi * np.cumsum(np.minimum(f, 1300 * p)) / SR) * env_ad(n, .02, .5) * .25
    sh = chime(1.3 * p); s[:len(sh)] += sh[:n] * .5; return s
def orb(p):  # orbe de luz
    n = int(1.2 * SR); tt = np.arange(n) / SR; f = note(76) * p
    return (np.sin(2 * np.pi * f * tt) + .5 * np.sin(2 * np.pi * f * 1.5 * tt)) * env_ad(n, .15, .5) * .25
def space(p):  # vacío del espacio: grave con brillo lejano
    n = int(3.2 * SR); tt = np.arange(n) / SR; x = np.sin(2 * np.pi * note(31) * tt) * .5 + band(rng.standard_normal(n), 2000, 9000) * .05 * (.5 + .5 * np.sin(2 * np.pi * .7 * tt))
    return x * np.clip(tt / .8, 0, 1) * np.clip((tt[-1] - tt) / .6, 0, 1) * .6
def meteor(p):  # meteorito que cruza: silbido que baja y retumba
    n = int(3.4 * SR); tt = np.arange(n) / SR; f = (2400 * np.exp(-tt / 1.2) + 200) * p
    x = band(rng.standard_normal(n), 300, 6000) * (tt / tt[-1]) ** 1.5 * .7 + np.sin(2 * np.pi * np.cumsum(f) / SR) * .08 * (tt / tt[-1])
    return x * np.clip((tt[-1] - tt) / .1, 0, 1)
def boom(p):  # el impacto: golpe sub, crujido y cola larga
    n = int(4.5 * SR); tt = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(28 + 90 * np.exp(-tt / .12)) / SR) * np.exp(-tt / 1.4)
    crack = band(rng.standard_normal(n), 600, 12000) * np.exp(-tt / .06) * .9; rumble = band(rng.standard_normal(n), 30, 300) * np.exp(-tt / 1.2) * .9
    x = np.tanh((sub * 1.6 + crack + rumble) * 1.3); return x + reverb(x, 2.5, 1.6)[:n] * .6
def debris(p):  # escombros que caen
    n = int(2.4 * SR); out = np.zeros(n)
    for k in range(70):
        j = int(rng.uniform(0, 2.2) * SR); m = int(rng.uniform(.01, .05) * SR); out[j:j + m] += band(rng.standard_normal(m), 400, 7000)[: n - j] * (1 - j / n) * .6
    return out
def layers(p):  # capas de roca que se depositan
    n = int(1.5 * SR); tt = np.arange(n) / SR; return band(rng.standard_normal(n), 150, 1500) * np.sin(np.pi * tt / tt[-1]) ** 2 * .6
def water(p):  # agua de cenote: goteo y eco
    n = int(5.5 * SR); out = np.zeros(n)
    for k in range(9):
        j = int((.2 + k * .58 + rng.uniform(0, .2)) * SR); m = int(.2 * SR); tt = np.arange(m) / SR; d = np.sin(2 * np.pi * np.cumsum(900 + 1400 * np.exp(-tt / .02)) / SR) * np.exp(-tt / .05) * .3
        out[j:j + m] += d[: n - j]
    return out + reverb(out, 2.0, 1.5)[:n] * .8
def splash(p):  # zambullida en el cenote
    n = int(1.2 * SR); tt = np.arange(n) / SR; return band(rng.standard_normal(n), 500, 9000) * np.exp(-tt / .25) * .8 + band(rng.standard_normal(n), 80, 600) * np.exp(-tt / .1) * .5
def slam(p):  # texto que cae con golpe
    x = hit(1.1 * p); n = len(x); tt = np.arange(n) / SR; return x + band(rng.standard_normal(n), 3000, 12000) * np.exp(-tt / .03) * .5
GEN = dict(ding=(ding, .3), pop=(pop, .3), whoosh=(whoosh, .24), tick=(tick, .2), click=(click, .45), chime=(chime, .3), flash=(flash, .28),
           rise=(rise, .3), hit=(hit, .3), sweep=(sweep, .24), paper=(paper, .28), chord=(chord, .38), number=(number, .34), count=(count, .24),
           door=(door, .3), strike=(strike, .3), shine=(shine, .3), room=(room, .3), chalk=(chalk, .2), creak=(creak, .3), thud=(thud, .34),
           airy=(airy, .3), shutter=(shutter, .4), develop=(develop, .3), ring=(ring_, .3), node=(node, .3), shuffle=(shuffle, .3), ticket=(ticket, .32),
           down=(down, .3), upch=(upch, .3), plane=(plane, .26), stamp=(stamp, .4), pen=(pen, .26), zoomin=(zoomin, .3), whip=(whip, .26), zoomout=(zoomout, .26), key=(key, .3), dissolve=(dissolve, .32), assemble=(assemble, .3),
           tickclock=(tickclock, .25), fall=(fall, .3), crack=(crack, .3), heartbeat=(heartbeat, .4), glass=(glass, .3), orb=(orb, .3), space=(space, .3), meteor=(meteor, .32), boom=(boom, .5),
           debris=(debris, .3), layers=(layers, .3), water=(water, .3), splash=(splash, .32), slam=(slam, .36), ping=(ping, .26), pulse=(pulse, .3), scan=(scan, .3), blip=(blip, .24), flip=(flip, .26))
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
