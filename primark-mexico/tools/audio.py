"""Música electrónica tonal a 120 BPM (compases de 2 s exactos, el loop cierra) y efectos afinados, sin ruido.
Regla de audio de Atlas Path (3 nov 2026): nada de barridos de aire, público sintético ni golpes con ruido; las transiciones
son notas suaves afinadas al acorde que suena (trans) y los cierres arpegios (arp). La voz siempre manda.
Las secciones vienen de window.TL.sections (index.html).

Uso: python3 tools/audio.py tools/timeline.json audio"""
import json, sys, wave, numpy as np
from scipy.signal import fftconvolve
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SR = 48000; DUR = float(TL['duration']); N = int(SR * DUR); T = np.arange(N) / SR
rng = np.random.default_rng(7)
NB = int(round(DUR / 2)); bar = DUR / NB; beat = bar / 4; BPM = 60 / beat
SEC = TL.get('sections', [[0, 'main']])
def section(t):
    s = SEC[0][1]
    for a, n in SEC:
        if t >= a: s = n
    return s
def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def env(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def add(buf, start, sig, g=1.0):
    i = int(round(start * SR)); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    if j > i: buf[i:j] += sig[:j - i] * g
note = lambda m: 440 * 2 ** ((m - 69) / 12)
def saw(f, n, ph=0.0): t = np.arange(n) / SR; return 2 * ((f * t + ph) % 1) - 1
def sine(f, n): return np.sin(2 * np.pi * f * np.arange(n) / SR)
def smooth(x, k):
    c = np.cumsum(np.concatenate([[0.0], x])); h = k // 2; i = np.arange(len(x)); lo = np.clip(i - h, 0, len(x)); hi = np.clip(i + h, 0, len(x))
    return (c[hi] - c[lo]) / np.maximum(hi - lo, 1)
def reverb(x, secs=1.6, damp=2.6, seed=1):  # cola de sala (solo para dar espacio a tonos limpios)
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * damp) * (1 - np.exp(-t * 300)); ir = band(ir, 300, 7000); ir /= np.abs(ir).sum() ** .5 * 40
    return fftconvolve(x, ir)[:len(x)]

# ---------------- ARMONÍA ----------------
Am = [45, 57, 60, 64, 69]; F = [41, 57, 60, 65, 69]; Cc = [48, 55, 60, 64, 67]; G = [43, 55, 59, 62, 67]; Dm = [38, 57, 62, 65, 69]; E = [40, 56, 59, 64, 68]
PROG = {'main': [Am, F, Cc, G], 'groove': [Am, F, Cc, G], 'intro': [Am, F], 'lift': [F, G, Am, Cc], 'tense': [Dm, E], 'hold': [F, Cc],
        'build': [F, G, Am, G], 'drop': [Cc, G, Am, F], 'outro': [F, Cc, G, Cc]}
def chord_at(t):
    bi = int(t / bar); pr = PROG.get(section(t + .02), PROG['main']); return pr[bi % len(pr)]
padL = np.zeros(N); padR = np.zeros(N); bass = np.zeros(N); arpL = np.zeros(N); arpR = np.zeros(N); drums = np.zeros(N)
for bi in range(NB):
    t0 = bi * bar; s = section(t0 + .02); ch = chord_at(t0 + .02); n = int(bar * SR * 1.15)
    e = env(n, .3, 2.4); e[-int(.3 * SR):] *= np.linspace(1, 0, int(.3 * SR))
    for j, m in enumerate(ch[1:]):
        for d, (gl, gr) in zip((-.07, 0, .07), ((1, .5), (.8, .8), (.5, 1))):
            x = saw(note(m + d), n, (j * .17 + d) % 1) * e * .045; add(padL, t0, x * gl); add(padR, t0, x * gr)
    root = note(ch[0] - 12 if ch[0] > 44 else ch[0])
    steps = {'hold': 1, 'intro': 2, 'tense': 4, 'outro': 4}.get(s, 8)
    for q in range(steps):
        m = int(bar / steps * SR * .9); x = (np.tanh(saw(root, m) * .8) * .5 + sine(root, m)) * env(m, .004, .14 if steps > 2 else .9)
        add(bass, t0 + q * bar / steps, x * (1 if q % 4 == 0 else .75))
    if s not in ('hold',):
        tones = [m + 12 for m in ch[1:4]] + [ch[1] + 24]; pat = [0, 2, 1, 3, 2, 1, 3, 2, 0, 2, 1, 3, 3, 1, 2, 0]
        for q in range(16):
            if s in ('intro', 'tense') and q % 2: continue
            m = int(.22 * SR); f = note(tones[pat[q] % 4]); tt = np.arange(m) / SR
            x = np.sin(2 * np.pi * np.cumsum(f * (1 + .15 * np.exp(-tt / .01))) / SR) * env(m, .002, .07) * .1
            tq = t0 + q * bar / 16; add(arpL, tq, x * (1 if q % 2 else .7)); add(arpR, tq + .004, x * (.7 if q % 2 else 1))
# batería tonal (sin ruido): bombo de seno, rim afinado y «hat» metálico FM muy suave
kn = int(.4 * SR); kt = np.arange(kn) / SR
KICK = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .2)) * .9
rn = int(.12 * SR); rt = np.arange(rn) / SR
RIM = (np.sin(2 * np.pi * 1700 * rt) + .5 * np.sin(2 * np.pi * 2550 * rt)) * np.exp(-rt / .018) * .35 + np.sin(2 * np.pi * 220 * rt) * np.exp(-rt / .04) * .3
hn = int(.07 * SR); ht = np.arange(hn) / SR
HAT = np.sin(2 * np.pi * 7200 * ht + 3 * np.sin(2 * np.pi * 10300 * ht)) * np.exp(-ht / .012) * .09
kicks = []
for k in range(int(DUR / beat)):
    tb = k * beat; s = section(tb + .01); qb = k % 4
    if s == 'hold': continue
    if s in ('intro', 'outro', 'tense'):
        if qb in (0, 2): add(drums, tb, KICK, .8); kicks.append(tb)
        add(drums, tb + beat / 2, HAT, .8)
    else:
        add(drums, tb, KICK, .9); kicks.append(tb)
        if qb in (1, 3): add(drums, tb, RIM, .7)
        for h in range(2 if s in ('groove', 'main') else 4): add(drums, tb + h * beat / (2 if s in ('groove', 'main') else 4), HAT, 1 if h % 2 else .6)
pump = np.ones(N)
for kb in kicks:
    i = int(kb * SR); n = min(N - i, int(.3 * SR))
    if n > 0: pump[i:i + n] = np.minimum(pump[i:i + n], 1 - .45 * np.exp(-np.arange(n) / SR / .08))
pad = np.stack([band(padL, 40, 2600), band(padR, 40, 2600)]); bass = band(bass, 28, 700)
arp = np.stack([band(arpL, 300, 9000), band(arpR, 300, 9000)]); dl = int(beat * .75 * SR); arp[0][dl:] += arp[1][:-dl] * .3; arp[1][dl:] += arp[0][:-dl] * .3
mus = pad * pump + np.stack([bass, bass]) * pump * .85 + arp * pump * .9 + np.stack([drums, drums]) * .75
mus /= np.abs(mus).max()
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(.2 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); g = g * smooth(kk, int(.3 * SR))
dip = np.ones(N)
for a, b in TL.get('musicDips', []):
    i0, i1 = int(a * SR), int(b * SR); f0 = int(.08 * SR); f1 = int(.03 * SR)
    dip[i0:i0 + f0] = np.minimum(dip[i0:i0 + f0], np.linspace(1, .12, f0)); dip[i0 + f0:i1] = .12; dip[i1:i1 + f1] = np.minimum(dip[i1:i1 + f1], np.linspace(.12, 1, f1))
mus *= g * dip * .66  # ≈ 13 dB bajo la voz
fo = int(.05 * SR); mus[:, -fo:] *= np.linspace(1, 0, fo)

# ---------------- EFECTOS AFINADOS (sin ruido) ----------------
def bellf(f, d=1.6):
    n = int(d * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t + .8 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .3)) * np.exp(-t / .6) + .3 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / .2)) * np.clip(t / .004, 0, 1)
CUR_T = [0.0]
def tones(): return chord_at(CUR_T[0] + .02)
def trans(p):  # nota suave afinada al acorde: raíz + quinta, una octava arriba
    ch = tones(); out = bellf(note(ch[1] + 12) * p, 1.4) * .5 + bellf(note(ch[3] + 12) * p, 1.4) * .3; return out + reverb(out, 1.4)[:len(out)] * .4
def arp(p):
    ch = tones(); out = np.zeros(int(1.8 * SR))
    for i, m in enumerate([ch[1], ch[2], ch[3], ch[1] + 12, ch[2] + 12]):
        x = bellf(note(m + 12) * p, 1.2) * .35; j = int(i * .07 * SR); out[j:j + len(x)] += x[:len(out) - j]
    return out + reverb(out, 1.6)[:len(out)] * .4
def pop(p):
    n = int(.14 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum((380 + 650 * np.exp(-t / .025)) * p) / SR) * env(n, .002, .045)
def ding(p): ch = tones(); return bellf(note(ch[3] + 24) * p, 1.2) * .45
def blip(p): n = int(.1 * SR); return sine(1300 * p, n) * env(n, .002, .03) * .5
def ping(p): n = int(.9 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 1760 * p * t) + .3 * np.sin(2 * np.pi * 3537 * p * t) * np.exp(-t / .08)) * env(n, .001, .22) * .45
def tick(p): n = int(.03 * SR); return sine(2100 * p, n) * env(n, .001, .006) * .6
def key(p): n = int(.05 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 2600 * p * t) * .5 + np.sin(2 * np.pi * 900 * p * t) * .4) * np.exp(-t / .007)
def click(p): n = int(.06 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 3000 * t) * np.exp(-t / .004) + np.sin(2 * np.pi * 1500 * t) * np.exp(-np.clip(t - .03, 0, None) / .004) * (t > .03) * .6)
def send(p): n = int(.4 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(600 + 1600 * (t / t[-1]) ** 1.5) / SR) * env(n, .01, .12) * .4
def chord(p):
    ch = tones(); out = np.zeros(int(3.0 * SR))
    for i, m in enumerate(ch[1:] + [ch[1] + 12]):
        x = bellf(note(m + 12) * (1 if p < 1.05 else 1.0), 2.8) * (.35 if i else .45); j = int(i * .04 * SR); out[j:j + len(x)] += x[:len(out) - j]
    return out * .55 + reverb(out, 2.0, 1.9)[:len(out)] * .45
def select(p):
    ch = tones(); out = np.zeros(int(1.5 * SR))
    for i, m in enumerate(ch[1:4] + [ch[1] + 12]):
        x = bellf(note(m + 12) * p, 1.3) * .28; j = int(i * .03 * SR); out[j:j + len(x)] += x[:len(out) - j]
    return out
def boom(p):  # golpe tonal: caída de sub afinada + tono del acorde (sin ruido)
    n = int(2.2 * SR); t = np.arange(n) / SR; ch = tones()
    sub = np.tanh(1.4 * np.sin(2 * np.pi * np.cumsum(note(ch[0] - 12 if ch[0] > 44 else ch[0]) * p + 90 * np.exp(-t / .06)) / SR) * np.exp(-t / .55))
    return sub * .85 + bellf(note(ch[1]) * p, 2.2)[:n] * .25
def deny(p): n = int(.5 * SR); t = np.arange(n) / SR; return (np.sin(2 * np.pi * 196 * t) + np.sin(2 * np.pi * 207.6 * t)) * env(n, .005, .15) * .35
def meter(p):
    out = np.zeros(int(1.2 * SR))
    for i in range(4):
        b = blip(p * (1 + i * .12)) if i < 3 else ping(p * 1.2); j = int(i * .11 * SR); out[j:j + len(b)] += b[:len(out) - j] * (.8 if i < 3 else .9)
    return out
def count(p):
    n = int(1.3 * SR); out = np.zeros(n); tj = 0; k = 0
    while tj < 1.2: c = tick(1 + k * .02); j = int(tj * SR); out[j:j + len(c)] += c[:n - j] * .6; tj += .09 * (1 - tj / 1.5) + .02; k += 1
    return out
GEN = dict(trans=(trans, .3), arp=(arp, .32), pop=(pop, .28), ding=(ding, .26), blip=(blip, .22), ping=(ping, .24), tick=(tick, .2), key=(key, .26), click=(click, .4),
           send=(send, .28), chord=(chord, .36), select=(select, .32), boom=(boom, .34), deny=(deny, .3), meter=(meter, .28), count=(count, .26))
fx = np.zeros(N)
for e in TL['sfx']:
    CUR_T[0] = e['t']; fn, gn = GEN[e['type']]; add(fx, e['t'], fn(e['pitch']), gn * e['v'] * .4)
fxs = np.stack([fx, fx]); mix = np.tanh(mus + fxs)
def save(path, x):
    d = (np.clip(x, -1, 1).T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-sin-voz.wav', mix)
print('BPM %.2f' % BPM, 'compases', NB, 'pico mezcla %.2f' % np.abs(mix).max(), 'rms música %.4f' % np.sqrt((mus ** 2).mean()))
