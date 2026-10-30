"""Música electrónica a 112 BPM (35 compases exactos en 75 s, así el loop cierra) que sigue el arco del guion:
pregunta ($100 → $99, con corte de música en el golpe) → nombre del efecto → experimento (suspenso en «¿cuál vendió más?» y remate en +33 %)
→ explicación → ejemplos → letra chiquita → acción (PRECIO y seguir). Pausas antes de cada cifra y efectos sincronizados con timeline.json. Sin voz.

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
BPM = 35 * 4 * 60 / DUR; beat = 60 / BPM; bar = beat * 4; NB = int(round(DUR / bar))
TIPS = [12.5, 31.5, 47.0, 56.0]
SEC = [(0, 'intro'), (2.45, 'freeze'), (2.9, 'rebuild'), (5.0, 'data'), (8.75, 'groove'), (12.5, 'main'), (19.45, 'discovery'), (21.95, 'reveal'),
       (26.55, 'main'), (31.5, 'groove'), (42.45, 'lift'), (47.0, 'main'), (51.4, 'groove'), (56.0, 'hold'), (58.25, 'discovery'), (60.4, 'reveal'),
       (63.0, 'hold'), (65.1, 'drop'), (68.3, 'outro')]
def section(t):
    s = 'intro'
    for a, name in SEC:
        if t >= a: s = name
    return s
Dm = [38, 57, 62, 65, 69]; Bb = [34, 58, 62, 65, 70]; F_ = [41, 57, 60, 65, 69]; C_ = [36, 55, 60, 64, 67]
PROG = [Dm, Bb, F_, C_]                                   # Rem – Sib – Fa – Do: tecnológico, sin dramatismo
TENSE = [[38, 57, 62, 64, 69], [38, 56, 62, 65, 70]]      # suspenso de la pregunta a la IA
LIFT = [Bb, F_, C_, [38, 57, 62, 65, 72]]
BMAJ9 = [34, 57, 62, 65, 69, 72]
def chord_at(t):
    s = section(t + .05); bi = int(t / bar)
    if s == 'discovery': return TENSE[bi % 2]
    if s in ('lift', 'build'): return LIFT[bi % 4]
    if s in ('reveal', 'drop'): return BMAJ9 if bi % 2 == 0 else F_
    return PROG[bi % 4]

padL = np.zeros(N); padR = np.zeros(N); bass = np.zeros(N); arpL = np.zeros(N); arpR = np.zeros(N)
for bi in range(NB + 1):
    t0 = bi * bar
    if t0 >= DUR: break
    s = section(t0 + .05); ch = chord_at(t0); n = int(bar * SR * 1.15)
    e = env_ad(n, .35, 2.6); e[-int(.3 * SR):] *= np.linspace(1, 0, int(.3 * SR))
    for j, m in enumerate(ch[1:]):
        for d, (gl, gr) in zip((-.08, 0, .08), ((1, .55), (.8, .8), (.55, 1))):
            x = saw(note(m + d), n, ph=(j * .17 + d) % 1) * e * .05
            add(padL, t0, x * gl); add(padR, t0, x * gr)
    root = note(ch[0])
    steps = {'groove': 8, 'main': 16, 'lift': 16, 'build': 16, 'reveal': 8, 'drop': 8, 'data': 4, 'rebuild': 4, 'hold': 4, 'outro': 4, 'discovery': 2}.get(s, 2)
    for q in range(steps):
        tq = t0 + q * bar / steps; m = int(.9 * bar / steps * SR) if steps > 2 else int(bar * .5 * SR)
        x = (saw(root, m) * .5 + np.sin(2 * np.pi * root * np.arange(m) / SR)) * env_ad(m, .004, .11 if steps > 2 else 1.0)
        add(bass, tq, x * (.95 if q % 4 == 0 else .7))
    if s != 'freeze':
        tones = [m + 12 for m in ch[1:4]] + [ch[1] + 24]
        pat = [0, 2, 1, 3, 2, 1, 3, 2, 0, 2, 1, 3, 3, 1, 2, 0]
        for q in range(16):
            tq = t0 + q * bar / 16; m = int(.2 * SR); f = note(tones[pat[q] % len(tones)]); tt = np.arange(m) / SR
            x = np.sin(2 * np.pi * np.cumsum(f * (1 + .2 * np.exp(-tt / .01))) / SR) * env_ad(m, .002, .06) * .1  # pluck digital
            add(arpL, tq, x * (1 if q % 2 else .7)); add(arpR, tq + .004, x * (.7 if q % 2 else 1))
pad = np.stack([padL, padR]); dark = np.stack([band(c, 40, 700) for c in pad]); bright = np.stack([band(c, 40, 7000) for c in pad])
bpad = curve([(0, .15), (2.4, .5), (2.9, .3), (5.0, .3), (8.75, .6), (12.5, .45), (19.45, .2), (21.95, .8), (26.55, .5), (31.5, .4), (42.45, .6), (47.0, .5), (56.0, .3), (60.4, .8), (63.0, .3), (65.1, 1), (68.3, .5), (75, .15)])
pad = dark * (1 - bpad) + bright * bpad
bass = band(bass, 28, 900)
arp = np.stack([band(arpL, 300, 9000), band(arpR, 300, 9000)])
dl = int(beat * .75 * SR); arp[0][dl:] += arp[1][:-dl] * .35; arp[1][dl:] += arp[0][:-dl] * .35  # eco ping-pong
# batería
kick_n = int(.4 * SR); kt = np.arange(kick_n) / SR
KICK = np.tanh(2 * np.sin(2 * np.pi * np.cumsum(46 + 100 * np.exp(-kt / .028)) / SR) * np.exp(-kt / .19)) * .9 + band(rng.standard_normal(kick_n), 2000, 8000) * np.exp(-kt / .004) * .3
sn_n = int(.45 * SR); st = np.arange(sn_n) / SR
SNARE = band(rng.standard_normal(sn_n), 900, 9000) * np.exp(-st / .12) * .5 + np.sin(2 * np.pi * 190 * st) * np.exp(-st / .05) * .35
CLAP = band(rng.standard_normal(sn_n), 1000, 7000) * sum((st >= d) * np.exp(-np.clip(st - d, 0, None) / .02) for d in (0, .012, .024)) * .45
hat_n = int(.06 * SR); HAT = band(rng.standard_normal(hat_n), 7000, 16000) * np.exp(-np.arange(hat_n) / SR / .014) * .2
oh_n = int(.35 * SR); OHAT = band(rng.standard_normal(oh_n), 6000, 15000) * np.exp(-np.arange(oh_n) / SR / .1) * .14
rim_n = int(.05 * SR); RIM = band(rng.standard_normal(rim_n), 1500, 6000) * np.exp(-np.arange(rim_n) / SR / .006) * .5
cr_n = int(2.6 * SR); CRASH = band(rng.standard_normal(cr_n), 3500, 15000) * np.exp(-np.arange(cr_n) / SR / .7) * .3
def tom(f0, f1):
    n = int(.35 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(f1 + (f0 - f1) * np.exp(-t / .06)) / SR) * np.exp(-t / .16) * .6
DL = np.zeros(N); DR = np.zeros(N); SNR = np.zeros(N); kicks = []
def both(t, x, g=1, pan=0): add(DL, t, x, g * (1 - pan)); add(DR, t, x, g * (1 + pan))
def kick(t, g=.95): both(t, KICK, g); kicks.append(t)
for k in range(int(DUR / beat) + 1):
    tb = k * beat; s = section(tb + .01); qb = k % 4
    if tb >= DUR: break
    if s == 'freeze': continue
    if s in ('intro', 'outro'):
        kick(tb, .75 if s == 'intro' else .7); both(tb + beat / 2, HAT, .5, pan=.25)
    elif s in ('rebuild', 'data', 'hold'):
        if qb in (0, 2): kick(tb, .9)
        if qb == 3 and s != 'rebuild': both(tb + beat / 2, RIM, .5, pan=-.3)
        for h in range(2): both(tb + h * beat / 2, HAT, .55 if h else .35, pan=.25)
    elif s == 'discovery':
        if qb == 0: kick(tb, .9)
        if qb == 2: kick(tb, .5)
        both(tb + beat / 2, HAT, .4, pan=.25)
    else:  # groove, reveal, main, lift, build, drop
        kick(tb, .95)
        if qb in (1, 3): add(SNR, tb, SNARE, .8); add(SNR, tb + .003, CLAP, .7 if s in ('reveal', 'drop', 'lift') else .45)
        sub = 4 if s in ('main', 'lift', 'build', 'drop') else 2
        for h in range(sub): both(tb + h * beat / sub, HAT, (1 if h % 2 else .6) * .85, pan=.25)
        if s in ('reveal', 'drop', 'lift'): both(tb + beat / 2, OHAT, .7, pan=-.2)
for tc in (5.0, 8.75, 23.95, *TIPS, 60.4, 65.1):
    both(tc, CRASH, 1.0, pan=.1)
for tf in (8.75, 21.95, *TIPS, 65.1):  # redobles de toms que llevan a cada número
    for i, (a, b) in enumerate(((200, 95), (160, 80), (130, 66), (110, 55))): both(tf - .5 + i * .12, tom(a, b), .7, pan=(i - 1.5) * .2)
for i in range(48):  # redoble que crece hasta la palabra PRECIO
    tt = 63.6 + 1.4 * (1 - (1 - i / 48) ** 1.6)
    add(SNR, tt, SNARE, .2 + .55 * i / 48)
for tr, ln in ((1.25, 1.2), (7.65, 1.1), (20.85, 1.1), (22.85, 1.1), (63.9, 1.2)):
    rz = riser(ln); add(DL, tr, rz); add(DR, tr, rz)
# capa de suspenso en «¿cuál vendió más?»: dron grave con trémolo
ten = np.zeros(N); w = np.clip((T - 19.45) / .5, 0, 1) * np.clip((21.95 - T) / .25, 0, 1)
ten += (np.sin(2 * np.pi * note(26) * T) * .55 + band(saw(note(38), N), 30, 300) * .35 + np.sin(2 * np.pi * note(74) * T) * (.5 + .5 * np.sin(2 * np.pi * 4 * T)) * .035) * w
# golpe de $99: la música se corta y queda un brillo suspendido
fr = np.zeros(N); w2 = np.clip((T - 2.47) / .05, 0, 1) * np.clip((2.95 - T) / .15, 0, 1)
for m, g_ in ((86, .05), (93, .035), (98, .025), (81, .04)):
    fr += np.sin(2 * np.pi * note(m) * T + .3 * np.sin(2 * np.pi * 5.3 * T)) * g_
fr *= w2
ten = np.stack([ten + fr, ten * .95 + fr * 1.05])
# compresión lateral (bombeo) con cada bombo
pump = np.ones(N)
for kb in kicks:
    i = int(kb * SR); n = min(N - i, int(.33 * SR))
    if n > 0: pump[i:i + n] = np.minimum(pump[i:i + n], 1 - .5 * np.exp(-np.arange(n) / SR / .085))
drums = np.stack([DL, DR]); snr = band(SNR, 150, 12000)
drums += np.stack([snr + reverb(snr, 1.6, 3.0) * .6, snr + reverb(snr, 1.6, 3.0, seed=2) * .6])
# el ritmo crece con el arco: curiosidad → sorpresa → descubrimiento → utilidad → acción
arp_g = curve([(0, .5), (2.4, .6), (2.45, 0), (2.85, 0), (2.9, .5), (5.0, .5), (8.75, .8), (12.5, .85), (19.4, .7), (19.45, .25), (21.9, .3), (21.95, .9),
               (26.55, .85), (31.5, .75), (42.45, .95), (47.0, .9), (56.0, .55), (58.25, .3), (60.4, .9), (63.0, .55), (65.1, 1.0), (68.3, .6), (75, .5)])
bass_g = curve([(0, .4), (2.4, .5), (2.45, 0), (2.85, 0), (2.9, .55), (5.0, .6), (8.75, .85), (12.5, .85), (19.45, .55), (21.95, .95), (26.55, .85), (31.5, .8),
                (42.45, .95), (47.0, .9), (56.0, .6), (58.25, .55), (60.4, .95), (63.0, .6), (65.1, 1.0), (68.3, .6), (75, .45)])
pad_g = curve([(0, .8), (2.4, .9), (2.45, 0), (2.85, 0), (2.9, .85), (8.75, 1.0), (12.5, .85), (21.95, 1.0), (26.55, .85), (56.0, .9), (60.4, 1.05), (63.0, .8), (65.1, 1.1), (68.3, .9), (75, .8)])
drum_g = curve([(0, .65), (5.0, .8), (8.75, .9), (12.5, .95), (19.45, .8), (21.95, 1.0), (26.55, .95), (42.45, 1.0), (56.0, .8), (60.4, 1.0), (63.0, .8), (65.1, 1.0), (68.3, .8), (75, .7)])
mus = pad * pad_g * .9 * pump + np.stack([bass, bass]) * bass_g * pump * .9 + arp * arp_g * pump + drums * drum_g + ten * .5
mus /= np.abs(mus).max()
# volumen: 19 % sin texto, 15.5 % con subtítulos o cifras (la voz siempre por encima)
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(0.2 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); kk = smooth(kk, int(.3 * SR)); g = g * kk
# pausas estratégicas: la música casi desaparece justo antes de cada cifra y regresa con el golpe
dip = np.ones(N)
for a, b in TL.get('musicDips', []):
    i0, i1 = int(a * SR), int(b * SR); f0 = int(.08 * SR); f1 = int(.03 * SR)
    dip[i0:i0 + f0] = np.minimum(dip[i0:i0 + f0], np.linspace(1, .12, f0)); dip[i0 + f0:i1] = .12; dip[i1:i1 + f1] = np.minimum(dip[i1:i1 + f1], np.linspace(.12, 1, f1))
mus *= g * dip * 1.5
# loop: los últimos 50 ms se funden para que el final empalme con el inicio
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
# --- propios de este reel ---
def drone(p):  # zumbido grave del sitio que flota en el vacío
    n = int(2.6 * SR); tt = np.arange(n) / SR
    x = np.sin(2 * np.pi * note(38) * tt) * .5 + band(saw(note(50), n), 40, 600) * .25 + np.sin(2 * np.pi * note(74) * tt) * (.5 + .5 * np.sin(2 * np.pi * 3 * tt)) * .05
    return x * np.clip(tt / .6, 0, 1) * np.clip((tt[-1] - tt) / .5, 0, 1) * .6
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
def deny(p):  # acceso bloqueado: golpe seco + zumbido grave
    n = int(.7 * SR); tt = np.arange(n) / SR
    bz = band((saw(note(43), n) + saw(note(44), n)) * .5, 60, 2500) * np.exp(-tt / .25) * .35
    return bz + hit(.8)[:n] * .7
def unlock(p):  # candado que se abre: doble clic metálico + brillo
    n = int(1.2 * SR); out = np.zeros(n)
    for d, f in ((0, 2400), (.07, 3100)):
        j = int(d * SR); m = int(.04 * SR); out[j:j + m] += band(rng.standard_normal(m), f * .7, f * 1.6) * np.exp(-np.arange(m) / SR / .006) * 1.2
    sh = chime(1.2); j = int(.12 * SR); out[j:j + len(sh)] += sh[: n - j] * .8; return out
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
GEN = dict(ding=(ding, .3), pop=(pop, .3), whoosh=(whoosh, .24), tick=(tick, .2), click=(click, .45), key=(key, .32), chime=(chime, .3), flash=(flash, .28),
           scan=(scan, .26), rise=(rise, .3), impact=(impact, .32), hit=(hit, .32), ping=(ping, .26), sweep=(sweep, .24), lock=(lock, .3),
           assemble=(assemble, .3), morph=(morph, .26), blip=(blip, .24), dissolve=(dissolve, .34), select=(select, .34), pulse=(pulse, .34),
           paper=(paper, .28), send=(send, .3), chord=(chord, .42), drone=(drone, .3), number=(number, .36), count=(count, .26), deny=(deny, .32),
           unlock=(unlock, .32), door=(door, .3), meter=(meter, .3), flip=(flip, .26), strike=(strike, .3))
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
