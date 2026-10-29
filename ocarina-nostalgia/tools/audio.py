"""Música original de «Ocarina of Time: la nostalgia es tu mejor arma»: 101.33 BPM, 38 compases exactos en 90 s (el loop cierra).
Cambia con cada acto del guion:
  acto 1 (0–30.8 s)     chiptune de 8 bits en La menor (pulsos, triángulo y ruido) con remate en cada cifra;
  acto 2 (30.8–47.4 s)  orquesta en Re mayor: cuerdas, arpa, coro, corno, glockenspiel y timbales;
  acto 3 (47.4–64 s)    batalla en Re menor: ostinato de cuerdas, taikos y metales, con 1 s de silencio total (61.95–62.95)
                        antes del golpe final en Re mayor;
  epílogo (64–90 s)     tema heroico en Re mayor que crece hasta la fanfarria de «¡MISIÓN CUMPLIDA!» y se apaga con la tele.
Melodías, armonías y efectos propios: no usa ni imita música ni sonidos de videojuegos existentes; la ocarina solo toca tres notas
genéricas (Mi–Re–Sol). Queda al 19 % sin texto y al 15.5 % con subtítulos o cifras, con pausas antes de cada cifra, y se calibra a
−29.5 LUFS (música; la orquesta ocupa más la banda de la voz que la electrónica) y −22.5 LUFS (efectos). Efectos sincronizados con timeline.json. Sin voz.

Uso (desde ocarina-nostalgia/): python3 tools/audio.py tools/timeline.json audio"""
import json, os, subprocess, sys, wave, numpy as np
from scipy.signal import fftconvolve
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
SR = 48000; DUR = float(TL.get('duration', 90)); N = int(SR * DUR)
rng = np.random.default_rng(23)
T = np.arange(N) / SR

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def soft(x, lo=0, hi=0, o=2):  # filtro suave de fase cero (pendiente tipo Butterworth) para pistas largas
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9; H = np.ones_like(f)
    if hi: H /= np.sqrt(1 + (f / hi) ** (2 * o))
    if lo: H /= np.sqrt(1 + (lo / f) ** (2 * o))
    return np.fft.irfft(X * H, len(x))
def env_ad(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def adsr(n, a=.01, d=.1, s=.7, r=.1):
    e = np.full(n, float(s)); na = min(n, max(1, int(a * SR))); e[:na] = np.linspace(0, 1, na)
    nd = max(1, int(d * SR)); m = min(nd, n - na); e[na:na + m] = np.linspace(1, s, nd)[:m]
    nr = min(n, max(1, int(r * SR))); e[n - nr:] *= np.linspace(1, 0, nr); return e
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
def reverb(x, secs=1.8, damp=2.5, seed=1):
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * damp) * (1 - np.exp(-t * 400)); ir = band(ir, 200, 9000); ir /= np.abs(ir).sum() ** .5 * 40
    return fftconvolve(x, ir)[: len(x)]
def riser(len_s, f0=300, f1=6000):
    n = int(len_s * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 12
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = f0 * (f1 / f0) ** (k / seg); out[a:b] = band(x, c * .6, c * 1.6)[a:b]
    return out * (t / len_s) ** 2 * .6
class Bus:  # pista estéreo
    def __init__(s): s.L = np.zeros(N); s.R = np.zeros(N)
    def add(s, t, x, g=1., pan=0.): add(s.L, t, x, g * min(1., 1. - pan)); add(s.R, t, x, g * min(1., 1. + pan))
    def st(s): return np.stack([s.L, s.R])

# ---------------- INSTRUMENTOS ----------------
def pulse(f, n, duty=.5, vib=0.):  # onda de pulso de 8 bits
    t = np.arange(n) / SR; fr = f * (1 + vib * np.sin(2 * np.pi * 5.5 * t) * np.clip((t - .15) / .2, 0, 1))
    return np.where(np.cumsum(fr) / SR % 1 < duty, 1., -1.)
def tri4v(fr):  # triángulo de 4 bits con frecuencia variable
    ph = np.cumsum(fr) / SR % 1; return np.round((2 * np.abs(2 * ph - 1) - 1) * 7.5) / 7.5
def tri4(f, n): return tri4v(np.full(n, float(f)))
def chipnoise(n, hold=1):  # ruido de 8 bits (muestreo y retención)
    return np.repeat(rng.choice([-1., 1.], size=n // hold + 1), hold)[:n]
def strings(f, n, a=.3, r=.45, s=.85):  # sección de cuerdas: 4 sierras desafinadas con vibrato
    t = np.arange(n) / SR; v = 1 + .0032 * np.sin(2 * np.pi * 5.3 * t + rng.random() * 6) * np.clip((t - .25) / .4, 0, 1); out = np.zeros(n)
    for d in (-.11, -.04, .03, .1): out += 2 * ((np.cumsum(f * 2 ** (d / 12) * v) / SR + rng.random()) % 1) - 1
    return out / 4 * adsr(n, a, .2, s, r)
def brass(f, n, a=.05, r=.18, s=.8, bright=1.):  # metal aditivo: el brillo se abre con la intensidad
    t = np.arange(n) / SR; e = adsr(n, a, .3, s, r)
    ph = 2 * np.pi * np.cumsum(f * (1 + .004 * np.sin(2 * np.pi * 5 * t) * np.clip((t - .3) / .3, 0, 1))) / SR
    out = np.zeros(n); w = e.copy(); ek = e ** (.45 / bright)
    for k in range(1, int(min(28, 8000 / f)) + 1): out += np.sin(k * ph) / k * w; w = w * ek
    return out * .55
def harp(f, dur=1.8):  # arpa: parciales que se apagan más rápido cuanto más agudos
    n = int(dur * SR); t = np.arange(n) / SR; out = np.zeros(n)
    for k in range(1, 9):
        if k * f > 12000: break
        out += np.sin(2 * np.pi * k * f * t + rng.random() * 6) / k ** 1.4 * np.exp(-t * (1.2 + .9 * k))
    return out * np.clip(t / .003, 0, 1) * .5
FORM = {'a': ((800, 110, 1.), (1150, 120, .5), (2900, 200, .2)), 'o': ((450, 90, 1.), (800, 110, .35), (2830, 200, .08)),
        'u': ((325, 70, 1.), (700, 100, .18), (2530, 200, .04))}
def choir(f, n, vowel='a', a=.5, r=.7):  # coro: armónicos filtrados por los formantes de la vocal
    t = np.arange(n) / SR; out = np.zeros(n); K = max(1, int(5000 / f))
    amp = [sum(g * np.exp(-((k * f - F) / B) ** 2) for F, B, g in FORM[vowel]) + .015 for k in range(1, K + 1)]
    for d in (-.09, 0., .1):
        ph = 2 * np.pi * np.cumsum(f * 2 ** (d / 12) * (1 + .0045 * np.sin(2 * np.pi * (4.6 + 2 * abs(d)) * t + rng.random() * 6))) / SR + rng.random() * 6
        for k in range(K): out += np.sin((k + 1) * ph) * amp[k]
    return out / 3 * adsr(n, a, .3, .9, r) * .6
def glock(f, dur=1.2):
    n = int(dur * SR); t = np.arange(n) / SR
    return (np.sin(2 * np.pi * f * t) * np.exp(-t / .5) + .4 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / .12)
            + .2 * np.sin(2 * np.pi * f * 5.4 * t) * np.exp(-t / .05)) * np.clip(t / .002, 0, 1) * .4
def timp(m, dur=1.8):  # timbal
    n = int(dur * SR); t = np.arange(n) / SR; f = note(m) * (1 + .05 * np.exp(-t / .04))
    x = (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / .6) + .45 * np.sin(2 * np.pi * np.cumsum(f * 1.504) / SR) * np.exp(-t / .3)
         + .25 * np.sin(2 * np.pi * np.cumsum(f * 1.742) / SR) * np.exp(-t / .2))
    return (x + band(rng.standard_normal(n), 50, 1200) * np.exp(-t / .025) * .5) * .8
def taiko(f0=62):
    n = int(1.1 * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * np.cumsum(f0 + 70 * np.exp(-t / .025)) / SR) * np.exp(-t / .3) + band(rng.standard_normal(n), 70, 1800) * np.exp(-t / .035) * .6
    return np.tanh(x * 1.6) * .8
def osnare():  # caja de orquesta
    n = int(.4 * SR); t = np.arange(n) / SR
    return band(rng.standard_normal(n), 300, 9000) * np.exp(-t / .09) * .6 + np.sin(2 * np.pi * 185 * t) * np.exp(-t / .04) * .35
def cymbal(dur=3.):
    n = int(dur * SR); t = np.arange(n) / SR
    return band(rng.standard_normal(n), 3000, 16000) * np.exp(-t / (dur * .3)) * .35 + band(rng.standard_normal(n), 400, 3000) * np.exp(-t / .06) * .15
def swell(dur=1.5):  # platillo al revés
    n = int(dur * SR); t = np.arange(n) / SR; return band(rng.standard_normal(n), 2500, 15000) * (t / dur) ** 3 * .35

# ---------------- FORMA Y ARMONÍA ----------------
NB = 38; BPM = NB * 4 * 60 / DUR; beat = 60 / BPM; bar = 4 * beat; NB = int(round(DUR / bar))
def at(b, q=0.): return b * bar + q * beat   # compás b, tiempo q (en negras)
A2, A3, EP = 13, 20, 27                      # compases donde empiezan el acto 2, el acto 3 y el epílogo
SIL0, SIL1 = 61.95, 62.95                    # silencio total antes del golpe final
CH = {'Am': (45, [57, 60, 64]), 'F': (41, [57, 60, 65]), 'C': (48, [55, 60, 64]), 'G': (43, [55, 59, 62]), 'A': (45, [57, 61, 64]),
      'D': (38, [57, 62, 66]), 'Bm': (47, [54, 59, 62]), 'A/C#': (37, [57, 61, 64]), 'D/F#': (42, [57, 62, 66]), 'Em': (40, [55, 59, 64]),
      'Dm': (38, [57, 62, 65]), 'Bb': (46, [58, 62, 65]), 'Gm': (43, [55, 58, 62])}
HARM = ['Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'Am', 'F', 'C', 'G', 'A',                # acto 1 · La menor (cierra en La mayor)
        'D', 'Bm', 'G', 'A', 'D', 'G', 'A',                                                  # acto 2 · Re mayor
        'Dm', 'Dm', 'Bb', 'Gm', 'Dm', 'Bb', 'A',                                             # acto 3 · Re menor
        'D', 'A/C#', 'Bm', 'G', 'D/F#', 'Em', 'A', 'D', ('G', 'A'), 'D', 'D']               # epílogo · Re mayor
def segs(b):  # [(tiempo inicial, tiempo final, acorde)] de un compás
    h = HARM[b]; return [(0, 2, h[0]), (2, 4, h[1])] if isinstance(h, tuple) else [(0, 4, h)]
def chord_at(t):
    if SIL1 <= t < at(EP): return 'D'       # el golpe final ya es Re mayor
    b = min(NB - 1, max(0, int(t / bar))); return [c for q0, q1, c in segs(b) if q0 <= (t - b * bar) / beat < q1 or q1 == 4][0]
def tones(name, octs=(0,)): return sorted({m + 12 * o for m in CH[name][1] for o in octs})
IMPACTS = [e['t'] for e in TL['sfx'] if e['type'] == 'impact']
HITS = [e['t'] for e in TL['sfx'] if e['type'] == 'hit']
FAN = [e['t'] for e in TL['sfx'] if e['type'] == 'fanfare'][0]

# ---------------- ACTO 1 · CHIPTUNE ----------------
arp, lead, cbass, cdrm = Bus(), Bus(), Bus(), Bus()
ARP = [0, 1, 2, 3, 2, 1, 0, 1, 2, 3, 2, 1, 0, 1, 2, 1]
for b in range(A2):
    for q0, q1, name in segs(b):
        tn = [m + 12 for m in CH[name][1]] + [CH[name][1][0] + 24]
        for i in range(int((q1 - q0) * 4)):  # arpegio en semicorcheas
            m = int(.13 * SR); arp.add(at(b, q0 + i / 4), pulse(note(tn[ARP[i % 16]]), m, .25) * env_ad(m, .002, .06),
                                       .8 if i % 4 == 0 else .55, pan=.25 if i % 2 else -.25)
        r = CH[name][0]
        if b < 2:  # entrada: el bajo en blancas
            for q in np.arange(q0, q1, 2):
                m = int(2 * beat * .95 * SR); cbass.add(at(b, q), tri4(note(r), m) * adsr(m, .01, .2, .7, .1))
        else:      # bajo de octavas en corcheas
            for i in range(int((q1 - q0) * 2)):
                m = int(beat / 2 * .9 * SR); cbass.add(at(b, q0 + i / 2), tri4(note(r + (12 if i % 2 else 0)), m) * adsr(m, .003, .05, .8, .02), 1 if i % 2 == 0 else .8)
nk, ns, nh, no = int(.18 * SR), int(.22 * SR), int(.05 * SR), int(.25 * SR)
CKICK = tri4v(55 + 220 * np.exp(-np.arange(nk) / SR / .018)) * env_ad(nk, .001, .07)
CSNARE = chipnoise(ns, 2) * env_ad(ns, .001, .07) * .55 + tri4(190, ns) * env_ad(ns, .001, .03) * .4
CHAT = band(chipnoise(nh), 5000, 16000) * env_ad(nh, .0005, .012) * .35
COHAT = band(chipnoise(no), 5000, 16000) * env_ad(no, .001, .08) * .25
for k in range(int(round(at(A2) / beat))):
    tb = k * beat; b = int(tb / bar + 1e-6); q = k % 4
    if b < 2: continue
    if b == 2:  # los platillos anuncian el ritmo
        if q >= 2: cdrm.add(tb, CHAT, .6, .2); cdrm.add(tb + beat / 2, CHAT, .8, .2)
        continue
    if q in (0, 2): cdrm.add(tb, CKICK, 1.0)
    if q == 2 and b % 2: cdrm.add(tb + beat / 2, CKICK, .7)
    if q in (1, 3): cdrm.add(tb, CSNARE, .9)
    cdrm.add(tb, CHAT, .55, .2); cdrm.add(tb + beat / 2, CHAT, .8, .2)
    if q == 3 and b % 2: cdrm.add(tb + beat / 2, COHAT, .8, -.2)
for i in range(8): cdrm.add(at(12, 3) + i * beat / 8, CSNARE, .45 + .07 * i)   # redoble que lleva a la orquesta
# melodía propia del acto 1 (compás, tiempo, duración en negras, nota MIDI)
MEL1 = [(4, 0, .5, 69), (4, .5, .5, 72), (4, 1, 1, 76), (4, 2, .5, 74), (4, 2.5, .5, 72), (4, 3, 1, 69),
        (5, 0, .5, 65), (5, .5, .5, 69), (5, 1, 1, 72), (5, 2, .5, 74), (5, 2.5, .5, 72), (5, 3, 1, 69),
        (6, 0, .5, 67), (6, .5, .5, 72), (6, 1, 1, 76), (6, 2, 1, 79), (6, 3, 1, 76),
        (7, 0, 1.5, 74), (7, 1.5, .5, 71), (7, 2, 1, 67),
        (8, 0, 1, 76), (8, 1, 1, 81), (8, 2, .5, 79), (8, 2.5, .5, 76), (8, 3, 1, 74),
        (9, 0, 1, 72), (9, 1, 1, 77), (9, 2, .5, 76), (9, 2.5, .5, 72), (9, 3, 1, 69),
        (10, 0, .5, 67), (10, .5, .5, 69), (10, 1, 1, 72), (10, 2, 1.5, 76), (10, 3.5, .5, 74),
        (11, 0, 2, 74), (11, 2, 1, 71), (11, 3, 1, 67),
        (12, 2, .5, 73), (12, 2.5, .5, 76)]
for b, q, d, m in MEL1:
    n = int(d * beat * .95 * SR); lead.add(at(b, q), pulse(note(m), n, .5, vib=.004) * adsr(n, .005, .08, .65, .04), .9)
for i in range(9):  # carrera ascendente de La mayor hacia el acto 2
    m = (57, 61, 64)[i % 3] + 12 * (i // 3); n = int(beat / 9 * .95 * SR)
    lead.add(at(12, 3) + i * beat / 9, pulse(note(m + 12), n, .25) * env_ad(n, .001, .04), .55)
for tr in [t for t in IMPACTS if t < at(A2)]:  # remate de 8 bits en cada cifra
    n = int(.35 * SR)
    for m in CH[chord_at(tr + .12)][1]: lead.add(tr, pulse(note(m + 12), n, .5) * env_ad(n, .002, .15), .35)
    n = int(.6 * SR); cdrm.add(tr, chipnoise(n, 3) * env_ad(n, .001, .22), .5)
    n = int(.3 * SR); cbass.add(tr, tri4v(220 * np.exp(-np.arange(n) / SR / .1) + 40) * env_ad(n, .001, .2), 1.0)

# ---------------- ACTO 2 · ORQUESTA ----------------
hs, ls, br, hp, cho, gl, prc = Bus(), Bus(), Bus(), Bus(), Bus(), Bus(), Bus()
def pad(b, q0, q1, name, g=1., a=.35, octs=(0,)):  # cuerdas: bajos en la raíz y el acorde arriba
    n = int((q1 - q0) * beat * SR + .35 * SR); r, tr = CH[name]
    ls.add(at(b, q0), strings(note(r), n, a, .45), .9 * g); ls.add(at(b, q0), strings(note(r + 12), n, a, .45), .6 * g)
    for o in octs:
        for j, m in enumerate(tr): hs.add(at(b, q0), strings(note(m + 12 * o), n, a, .45), .45 * g, pan=(j - 1) * .4)
def harp_arp(b, q0, q1, name, g=1., step=.25):
    tn = tones(name, (-1, 0, 1)); seq = tn + tn[::-1]
    for i in range(int((q1 - q0) / step)):
        m = seq[i % len(seq)]; hp.add(at(b, q0 + i * step), harp(note(m)), g * (.9 if i % 4 == 0 else .7), pan=(m - 66) / 30)
def orch_hit(t, g=1., name=None):  # golpe de orquesta: metales, cuerdas, timbal, taiko y platillo
    name = name or chord_at(t + .1); r, tr = CH[name]; n = int(1.4 * SR)
    for m in (r, r + 7, r + 12): br.add(t, brass(note(m), int(.9 * SR), .01, .5, .7, bright=1.3), .5 * g)
    for m in tr: br.add(t, brass(note(m), int(.9 * SR), .01, .5, .7, bright=1.3), .35 * g)
    for m in (r, r + 12): ls.add(t, strings(note(m), n, .01, .9, .6), .7 * g)
    prc.add(t, timp(r if r >= 38 else r + 12), g); prc.add(t, cymbal(3.0), .55 * g); prc.add(t, taiko(), .5 * g)
for b in range(A2, A3):
    g = {13: .55, 14: .6, 15: .75, 16: .8, 17: .9, 18: .85, 19: 1.0}[b]
    for q0, q1, name in segs(b):
        pad(b, q0, q1, name, g, octs=(0, 1) if b >= 15 else (0,))
        if b in (13, 14, 17, 18): harp_arp(b, q0, q1, name, .8)
for b, vow, g in ((13, 'a', .5), (14, 'a', .55), (17, 'o', .6), (18, 'o', .6), (19, 'o', .7)):
    n = int(bar * SR + .5 * SR)
    for m in CH[HARM[b]][1]: cho.add(at(b), choir(note(m), n, vow), g)
# melodía del acto 2: violines y después corno
MEL2 = [(13, 0, 3, 81, 'v'), (13, 3, 1, 78, 'v'), (14, 0, 2, 83, 'v'), (14, 2, 1, 81, 'v'), (14, 3, 1, 78, 'v'),
        (15, 0, 2, 67, 'h'), (15, 2, 2, 71, 'h'), (16, 0, 4, 69, 'h'),
        (17, 0, 2, 74, 'h'), (17, 2, 1, 73, 'h'), (17, 3, 1, 69, 'h'), (18, 0, 1.2, 71, 'h'),
        (19, 0, 2, 73, 'h'), (19, 2, 2, 76, 'h')]
for b, q, d, m, ins in MEL2:
    n = int(d * beat * SR * 1.02)
    if ins == 'v': hs.add(at(b, q), strings(note(m), n, .25, .35, .9), .55)
    else: br.add(at(b, q), brass(note(m), n, .06, .2, .85, bright=.8), .7)
OCA = [e['t'] for e in TL['sfx'] if e['type'] == 'ocarina'][0]
for b in (17, 18):  # destellos de glockenspiel (gráficos nuevos); dejan sola a la ocarina
    for i in range(8):
        tq = at(b, i / 2)
        if rng.random() < .7 and not (OCA - .2 < tq < OCA + 1.3):
            gl.add(tq, glock(note(tones(chord_at(tq), (2,))[rng.integers(3)])), .5, pan=rng.uniform(-.5, .5))
prc.add(at(A2), timp(38), 1.0); prc.add(at(A2), cymbal(3.0), .5)
for t in [t for t in IMPACTS if at(A2) <= t < at(EP)]: orch_hit(t, .9 if t < at(A3) else 1.1)
for i in range(24): prc.add(at(19, 2) + i * 2 * beat / 24, osnare(), .15 + .5 * i / 24)   # redoble hacia la batalla
for i in range(12): prc.add(at(19, 2.5) + i * 1.5 * beat / 12, timp(45, .6), .2 + .4 * i / 12)
prc.add(at(A3) - 1.5, swell(1.5), .8)

# ---------------- ACTO 3 · BATALLA ----------------
orch_hit(at(A3), 1.0, 'Dm')
n = int(2 * bar * SR + .5 * SR); trem = 1 - .5 * (np.sin(2 * np.pi * 11 * np.arange(n) / SR) > 0)
ls.add(at(A3), strings(note(26), n, .8, .6) * trem, .9); ls.add(at(A3), strings(note(38), n, .8, .6) * trem, .7)   # dron grave del jefe
for m in (62, 65, 69): cho.add(at(A3), choir(note(m), n, 'u', .9, .8), .55)
hs.add(at(A3), (strings(note(81), n, 1.5, .4) + strings(note(82), n, 1.5, .4)) * trem * np.linspace(.2, 1, n), .25)   # segunda menor aguda
for b in (20, 21):
    for q, g in ((0, 1.), (1.5, .6), (2, .8), (3.5, .5)): prc.add(at(b, q), taiko(58), g * .8)
OST = [0, 0, 12, 0, 0, 0, 12, 0, 0, 0, 12, 0, 0, 12, 7, 12]
for b in range(22, 26):
    for q0, q1, name in segs(b):
        r = CH[name][0]
        for i in range(int((q1 - q0) * 4)):  # ostinato de cuerdas graves en semicorcheas
            m = r + OST[i % 16]; nn = int(.14 * SR)
            ls.add(at(b, q0 + i / 4), (saw(note(m), nn) + saw(note(m) * 1.004, nn, .3)) * env_ad(nn, .004, .07) * .5, 1. if i % 4 == 0 else .7)
        nn = int((q1 - q0) * beat * SR)
        for m in (r, r + 7, r + 12): br.add(at(b, q0), brass(note(m), nn, .03, .25, .6, bright=.9), .3)
        for m in CH[name][1]: br.add(at(b, q0 + 2.5), brass(note(m), int(.35 * SR), .01, .15, .7, bright=1.3), .3)
        if b >= 23:
            nn = int((q1 - q0) * beat * SR + .2 * SR); tr_ = 1 - .45 * (np.sin(2 * np.pi * 12 * np.arange(nn) / SR) > 0)
            for m in CH[name][1]: hs.add(at(b, q0), strings(note(m + 12), nn, .1, .2) * tr_, .3)
    for q, g in ((0, 1.), (.75, .55), (1.5, .7), (2, .9), (2.5, .55), (3, .8), (3.5, .6), (3.75, .5)): prc.add(at(b, q), taiko(62), g * .75)
    for q in (1, 3): prc.add(at(b, q), osnare(), .55)
MEL3 = [(22, 0, 1.5, 74), (22, 1.5, .5, 72), (22, 2, 1, 70), (22, 3, 1, 65), (23, 0, 1, 67), (23, 1, 1, 70), (23, 2, 1.5, 74), (23, 3.5, .5, 72),
        (24, 0, 2, 69), (24, 2, 1, 65), (24, 3, 1, 62), (25, 0, 1, 65), (25, 1, 1, 67), (25, 2, 1, 70), (25, 3, 1, 72)]
for b, q, d, m in MEL3:
    nn = int(d * beat * SR * 1.02); br.add(at(b, q), brass(note(m), nn, .04, .15, .85, bright=1.1), .6)
for t in HITS: prc.add(t, cymbal(2.0), .5); prc.add(t, taiko(50), .9)
for i in range(16): prc.add(at(25, 2) + i * 2 * beat / 16, osnare(), .2 + .5 * i / 16)
prc.add(at(26) - 1.2, swell(1.2), .9)
orch_hit(at(26), .9, 'A')            # golpe de La que el silencio corta en seco
orch_hit(SIL1, 1.3, 'D')             # golpe final: Re mayor, el héroe gana
for m in (62, 66, 69, 74): cho.add(SIL1, choir(note(m), int(2.6 * SR), 'a', .02, 1.2), .6)
for m in (62, 69, 74, 78, 81, 86): hs.add(SIL1, strings(note(m), int(2.4 * SR), .02, 1.2, .7), .3)
prc.add(SIL1, cymbal(4.0), .8)

# ---------------- EPÍLOGO · HEROICO ----------------
for b in range(EP, NB):
    g = {27: .45, 28: .5, 29: .6, 30: .65, 31: .7, 32: .75, 33: .9, 34: .95, 35: 1.0, 36: 1.1, 37: .9}[b]
    for q0, q1, name in segs(b):
        pad(b, q0, q1, name, g, a=.6 if b < 29 else .35, octs=(0,) if b < 33 else (0, 1))
        if b < 37: harp_arp(b, q0, q1, name, .7 if b < 33 else .8, .5 if b < 33 else .25)
        if b >= 33:
            for m in CH[name][1]: cho.add(at(b, q0), choir(note(m), int((q1 - q0) * beat * SR + .5 * SR), 'a'), .5)
MEL4 = [(29, 0, 2, 66), (29, 2, 1, 62), (29, 3, 1, 66), (30, 0, 1.5, 67), (30, 1.5, .5, 66), (30, 2, 2, 62),
        (31, 0, 2, 69), (31, 2, 1, 66), (31, 3, 1, 69), (32, 0, 2, 71), (32, 2, 1, 67), (32, 3, 1, 64),
        (33, .6, 3.4, 73), (34, 0, 1, 66), (34, 1, 1, 69), (34, 2, 2, 74), (35, 0, 1, 71), (35, 1, 1, 74), (35, 2, 1, 73), (35, 3, 1, 76),
        (36, 0, 2, 74)]
for b, q, d, m in MEL4:
    nn = int(d * beat * SR * 1.02); br.add(at(b, q), brass(note(m), nn, .07, .25, .85, bright=.9), .65)
for b in (27, 28, 36):  # destellos del amanecer y de la victoria
    for i in range(8):
        if rng.random() < .6:
            tq = at(b, i / 2); gl.add(tq, glock(note(tones(chord_at(tq), (2,))[rng.integers(3)])), .45, pan=rng.uniform(-.5, .5))
for b in range(31, 37):
    prc.add(at(b), timp(CH[HARM[b][0] if isinstance(HARM[b], tuple) else HARM[b]][0] % 12 + 38), .5)
    if b >= 33:
        for q, g in ((0, .9), (.75, .4), (1, .6), (2, .8), (2.75, .4), (3, .6), (3.5, .45)): prc.add(at(b, q), osnare(), g * .5)
        for q in (0, 2): prc.add(at(b, q), taiko(55), .55)
prc.add(at(36), cymbal(3.0), .6)
for i in range(14): prc.add(FAN - .7 + i * .05, timp(38, .5), .15 + .5 * i / 14)   # redoble de timbal hacia la fanfarria
orch_hit(FAN, .8, 'D'); prc.add(FAN, cymbal(3.5), .6)

# ---------------- MEZCLA DE LA MÚSICA ----------------
F = lambda bus, lo, hi: np.stack([soft(c, lo, hi) for c in bus.st()])
ld = F(lead, 120, 6500); dl = int(.75 * beat * SR); ld[0, dl:] += ld[1, :-dl] * .3; ld[1, dl:] += ld[0, :-dl] * .3   # eco cruzado
chip = F(arp, 120, 6500) * .2 + ld * .3 + F(cbass, 30, 3000) * .5 + cdrm.st() * .4
chip += np.stack([reverb(c, 1.0, 5., seed=i) for i, c in enumerate(chip)]) * .15
orch = F(hs, 80, 7000) * .5 + F(ls, 30, 2500) * .6 + F(br, 50, 6500) * .5 + F(hp, 80, 9000) * .35 + F(cho, 150, 6000) * .35 + F(gl, 300, 12000) * .25
orch += np.stack([reverb(c, 2.4, 2.2, seed=3 + i) for i, c in enumerate(orch)]) * .45
perc = F(prc, 25, 16000); perc += np.stack([reverb(c, 2.0, 2.5, seed=7 + i) for i, c in enumerate(perc)]) * .25
mus = chip + orch + perc * .6
# cada acto con un volumen parecido (la batalla un poco más fuerte), sin perder sus crescendos internos
def rms(x, a, b): i, j = int(a * SR), int(b * SR); return np.sqrt((x[:, i:j] ** 2).mean()) + 1e-9
ACTS = [(0, at(A2), 1.0), (at(A2), at(A3), 1.0), (at(A3), SIL0, 1.12), (SIL1, 88.5, 1.0)]
gk = [tg * rms(mus, *ACTS[0][:2]) / rms(mus, a, b) for a, b, tg in ACTS]
mus *= np.interp(T, [0, at(A2) - .15, at(A2) + .15, at(A3) - .15, at(A3) + .15, SIL1 - .01, SIL1, DUR],
                 [gk[0], gk[0], gk[1], gk[1], gk[2], gk[2], gk[3], gk[3]])
# silencio total antes del golpe final; entrada suave con la tele y final que se apaga con ella (el loop empalma en silencio)
mask = np.ones(N); i0, i1, f = int(SIL0 * SR), int(SIL1 * SR), int(.01 * SR)
mask[i0 - f:i0] = np.linspace(1, 0, f); mask[i0:i1] = 0; mask[i1:i1 + f] = np.linspace(0, 1, f)
mask *= np.clip((T - .2) / 1.1, 0, 1) * np.clip((89.4 - T) / .9, 0, 1)
mus *= mask; mus /= np.abs(mus).max()
# volumen: 19 % sin texto, 15.5 % con subtítulos o cifras (la voz siempre por encima)
g = np.full(N, 0.19)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.155
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.155
g = smooth(g, int(0.2 * SR))
for a, b, m in TL.get('musicBoost', []):
    kk = np.ones(N); i0, i1 = int(a * SR), int(b * SR); kk[i0:i1] = np.linspace(1, m, i1 - i0); kk = smooth(kk, int(.3 * SR)); g = g * kk
# pausas estratégicas: la música casi desaparece antes de cada cifra (y desaparece del todo antes del golpe final)
dip = np.ones(N)
for a, b in TL.get('musicDips', []):
    i0, i1 = int(a * SR), int(b * SR); f0 = int(.08 * SR); f1 = int(.03 * SR); lv = 0. if b - a > .9 else .12
    dip[i0:i0 + f0] = np.minimum(dip[i0:i0 + f0], np.linspace(1, lv, f0)); dip[i0 + f0:i1] = lv; dip[i1:i1 + f1] = np.minimum(dip[i1:i1 + f1], np.linspace(lv, 1, f1))
mus *= g * dip
fo = int(.05 * SR); mus[:, -fo:] *= np.linspace(1, 0, fo)

# ---------------- EFECTOS ----------------
def sq(f, n, duty=.5): return np.where((f * np.arange(n) / SR) % 1 < duty, 1., -1.)
def pop(p, t0=0):
    n = int(0.14 * SR); tt = np.arange(n) / SR; f = (380 + 650 * np.exp(-tt / 0.025)) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.045)
def whoosh(p, t0=0):
    n = int(0.6 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n); m = tt / tt[-1]
    s = band(x, 250 * p, 1200 * p) * (1 - m) + band(x, 1200 * p, 5000 * p) * m * .7
    return s * np.sin(np.pi * np.clip(tt / .55, 0, 1)) ** 2 * 1.4
def tick(p, t0=0):
    n = int(0.03 * SR); tt = np.arange(n) / SR; return np.sin(2 * np.pi * 2100 * p * tt) * env_ad(n, 0.001, 0.006) * .6
def click(p, t0=0):
    n = int(0.09 * SR); x = band(rng.standard_normal(n), 2000, 9000); e = np.zeros(n); e[:int(.008 * SR)] = 1; e[int(.045 * SR):int(.05 * SR)] = .6; return x * e * 1.2
def key(p, t0=0):
    n = int(0.06 * SR); tt = np.arange(n) / SR
    return (band(rng.standard_normal(n), 1500, 8000) * .8 + np.sin(2 * np.pi * 900 * p * tt) * .3) * np.exp(-tt / .008) + band(rng.standard_normal(n), 200, 1200) * np.exp(-tt / .02) * .3
def shine(p, t0=0):
    out = np.zeros(int(1.1 * SR))
    for i, m in enumerate([86, 89, 93, 98, 101]):
        n = int(0.6 * SR); tt = np.arange(n) / SR; s = np.sin(2 * np.pi * note(m) * p * tt) * env_ad(n, 0.002, 0.15) * .25
        j = int(i * .05 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def flash(p, t0=0):
    out = np.zeros(int(1.4 * SR)); x = shine(1.1 * p); out[:min(len(x), len(out))] = x[:len(out)]; n = len(out); tt = np.arange(n) / SR
    return out + band(rng.standard_normal(n), 4000, 14000) * np.exp(-tt / .25) * .5
def rise(p, t0=0): return riser(1.0, 400, 5000) * .9
def impact(p, t0=0):  # golpe cinematográfico: caída de sub + grieta + cola
    n = int(2.6 * SR); tt = np.arange(n) / SR
    sub = np.sin(2 * np.pi * np.cumsum(32 * p + 70 * np.exp(-tt / .08)) / SR) * np.exp(-tt / .7)
    crack = band(rng.standard_normal(n), 800, 9000) * np.exp(-tt / .03) * .7
    body = band(rng.standard_normal(n), 60, 500) * np.exp(-tt / .25) * .6
    x = np.tanh((sub * 1.2 + crack + body) * 1.2)
    return x + reverb(x, 1.4, 2.5)[:n] * .5
def hit(p, t0=0):
    n = int(1.2 * SR); tt = np.arange(n) / SR
    x = np.tanh(np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-tt / .05)) / SR) * np.exp(-tt / .3) * 1.4 + band(rng.standard_normal(n), 1500, 8000) * np.exp(-tt / .02) * .4)
    return x * .8 + reverb(x, 1.2, 3)[:n] * .35
def sweep(p, t0=0):  # barrido de interfaz
    n = int(.5 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 10
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = 600 * p * 8 ** (k / seg); out[a:b] = band(x, c * .6, c * 1.5)[a:b]
    bl = np.sin(2 * np.pi * np.cumsum(900 * p + 1200 * p * tt / tt[-1]) / SR) * .12
    return (out * .7 + bl) * np.sin(np.pi * tt / tt[-1]) ** 1.5
def assemble(p, t0=0):  # partículas que se juntan: crepitar que se acelera y tono que sube
    n = int(.75 * SR); tt = np.arange(n) / SR; out = np.zeros(n); dens = (tt / tt[-1]) ** 1.5
    hits = rng.random(n) < (.002 + .03 * dens); out += band(hits * rng.standard_normal(n), 2500, 12000) * 1.2
    out += np.sin(2 * np.pi * np.cumsum(300 * p * 4 ** (tt / tt[-1])) / SR) * dens * .15
    return out * np.clip((tt[-1] - tt) / .03, 0, 1)
def morph(p, t0=0):
    n = int(.8 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 800, 7000)
    ph = x * (.5 + .5 * np.sin(2 * np.pi * (3 + 9 * tt) * tt)); gl_ = np.sin(2 * np.pi * np.cumsum(500 * p + 900 * p * tt) / SR) * .1
    return (ph * .5 + gl_) * np.sin(np.pi * tt / tt[-1])
def paper(p, t0=0):  # el mapa se despliega
    n = int(.7 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 900, 7000)
    return x * (.5 + .5 * np.abs(np.sin(2 * np.pi * 14 * tt))) * np.sin(np.pi * tt / tt[-1]) ** 2 * .9
def send(p, t0=0):
    n = int(.45 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 1500, 9000)
    return x * np.sin(np.pi * tt / tt[-1]) ** 3 * .6 + np.sin(2 * np.pi * np.cumsum(600 + 1800 * tt / tt[-1]) / SR) * env_ad(n, .01, .12) * .25
def bellf(f, dur=2.4):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t + 1.2 * np.sin(2 * np.pi * f * 2 * t) * np.exp(-t / .4)) * np.exp(-t / .9) + .35 * np.sin(2 * np.pi * f * 3.01 * t) * np.exp(-t / .25)
    return s * np.clip(t / .004, 0, 1)
def chord(p, t0=0):  # acorde de campanas en la armonía del momento
    r, tr = CH[chord_at(t0 + .15)]; out = np.zeros(int(3.4 * SR))
    for i, m in enumerate([r + 12] + [m + 12 for m in tr] + [tr[0] + 24]): add(out, i * .045, bellf(note(m), 3.2), .6 if i == 0 else .4)
    return out * .5 + reverb(out, 2.2, 1.8)[:len(out)] * .4
def chime(p, t0=0):
    out = np.zeros(int(1.3 * SR))
    for i, m in enumerate(tones(chord_at(t0 + .1), (1,))):
        n = int(1.1 * SR); tt = np.arange(n) / SR; f = note(m + 12)
        add(out, i * .06, (np.sin(2 * np.pi * f * tt) + .4 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt / .2)) * env_ad(n, .002, .4) * .3)
    return out
# --- propios de este reel ---
def hum(p, t0=0):  # zumbido de la tele CRT
    n = int(1.1 * SR); t = np.arange(n) / SR
    x = sum(np.sin(2 * np.pi * 60 * k * t) / k for k in (1, 2, 3, 5)) * .35 + band(rng.standard_normal(n), 3000, 9000) * .03
    return x * np.clip(t / .25, 0, 1) * np.clip((t[-1] - t) / .4, 0, 1)
def crt_on(p, t0=0):  # la tele se enciende: golpe, silbido que sube, chasquidos y desmagnetizado
    n = int(1.2 * SR); t = np.arange(n) / SR
    thump = np.sin(2 * np.pi * np.cumsum(45 + 80 * np.exp(-t / .03)) / SR) * np.exp(-t / .12) * .9
    whine = np.sin(2 * np.pi * np.cumsum(1500 + 6500 * (1 - np.exp(-t / .25))) / SR) * np.exp(-t / .5) * .08 * np.clip(t / .02, 0, 1)
    crack = band(rng.standard_normal(n), 2000, 12000) * (rng.random(n) < .02 + .1 * np.exp(-t / .1)) * np.exp(-t / .35) * 1.5
    boing = np.sin(2 * np.pi * 110 * t) * np.sin(2 * np.pi * 7 * t) * np.exp(-t / .3) * .25
    return thump + whine + crack + boing
def static(p, t0=0):  # estática de televisión con parpadeo
    n = int(.7 * SR); t = np.arange(n) / SR; x = band(rng.standard_normal(n), 400 * p, 7000 * p)
    fl = .55 + .45 * np.sign(np.sin(2 * np.pi * (23 + 13 * p) * t + rng.random() * 6))
    return x * fl * np.clip(t / .01, 0, 1) * np.clip((t[-1] - t) / .25, 0, 1) * .6
def pixel(p, t0=0):  # destello de píxeles: tres notas de 8 bits muy rápidas
    out = np.zeros(int(.16 * SR))
    for i, st in enumerate((0, 7, 12)):
        m = int(.035 * SR); add(out, i * .035, sq(1046.5 * p * 2 ** (st / 12), m, .25) * env_ad(m, .001, .02), .3)
    return band(out, 200, 9000)
def select(p, t0=0):  # selección de menú de 8 bits
    out = np.zeros(int(.2 * SR))
    for i, m in enumerate((84, 91)):
        n = int(.07 * SR); add(out, i * .07, sq(note(m) * p, n) * env_ad(n, .001, .04), .25)
    return band(out, 200, 9000)
def chip(p, t0=0):  # arranque del juego: arpegio de La menor que sube, con eco
    out = np.zeros(int(.7 * SR))
    for i, m in enumerate((69, 72, 76, 81, 84)):
        n = int(.09 * SR); add(out, i * .055, sq(note(m) * p, n, .25) * env_ad(n, .001, .05), .3)
    d = int(.16 * SR); out[d:] += out[:-d] * .35
    return band(out, 200, 9000)
def quest(p, t0=0):  # ¡NUEVA MISIÓN!: dos notas cortas y una larga del acorde, con brillo
    out = np.zeros(int(1.3 * SR)); tn = tones(chord_at(t0 + .1), (1, 2))
    for i, (m, dl) in enumerate(zip((tn[0], tn[2], tn[1] + 12), (.07, .07, .7))):
        n = int(dl * SR); add(out, i * .08, sq(note(m), n, .5 if i < 2 else .25) * env_ad(n, .002, .05 if i < 2 else .35), .25)
    d = int(.15 * SR); out[d:] += out[:-d] * .3; sh = shine(1.0); out[:len(sh)] += sh * .5
    return band(out, 150, 10000)
def token(p, t0=0):  # ficha que se coloca en el mapa
    n = int(.6 * SR); t = np.arange(n) / SR
    knock = band(rng.standard_normal(n), 700 * p, 2500 * p) * np.exp(-t / .012) * 1.2 + np.sin(2 * np.pi * 420 * p * t) * np.exp(-t / .03) * .5
    return knock + np.sin(2 * np.pi * 2093 * p * t) * np.exp(-t / .25) * .12 * (t > .03)
def tape(p, t0=0):  # cinta VHS que entra y arranca
    n = int(1.0 * SR); t = np.arange(n) / SR
    out = band(rng.standard_normal(n), 150, 2500) * np.exp(-t / .03) * .9 + np.sin(2 * np.pi * 90 * t) * np.exp(-t / .06) * .5
    m = n - int(.18 * SR); add(out, .18, band(rng.standard_normal(m), 1500, 6000) * np.exp(-np.arange(m) / SR / .008), .6)
    run = np.clip((t - .25) / .2, 0, 1) * np.clip((t[-1] - t) / .25, 0, 1)
    return out + (np.sin(2 * np.pi * np.cumsum(40 + 80 * np.clip((t - .25) / .4, 0, 1)) / SR) * .12 + band(rng.standard_normal(n), 800, 3000) * .06) * run
def sparkle(p, t0=0):  # chispas de glockenspiel con las notas del acorde
    out = np.zeros(int(1.4 * SR)); tn = tones(chord_at(t0 + .1), (2, 3))
    for k in range(14): add(out, k * .055 + rng.uniform(0, .03), glock(note(tn[rng.integers(len(tn))]) * min(p, 1.), .6), (1 - k / 16) * .6)
    return out
def cartridge(p, t0=0):  # cartucho que entra en la ranura: deslizamiento, clic y golpe sordo
    n = int(.9 * SR); t = np.arange(n) / SR
    out = band(rng.standard_normal(n), 1200, 6000) * np.clip(t / .05, 0, 1) * np.clip((.45 - t) / .05, 0, 1) * .35 * (1 + .5 * np.sin(2 * np.pi * 30 * t))
    for d, gg, lo, hi in ((.45, 1.0, 1500, 7000), (.5, .8, 300, 2500)):
        m = n - int(d * SR); add(out, d, band(rng.standard_normal(m), lo, hi) * np.exp(-np.arange(m) / SR / .015), gg)
    m = n - int(.5 * SR); tt = np.arange(m) / SR; add(out, .5, np.sin(2 * np.pi * np.cumsum(70 + 90 * np.exp(-tt / .02)) / SR) * np.exp(-tt / .08), .6)
    return out
def count(p, t0=0):  # contador que corre 0.55 s: clics que se aceleran y suben
    n = int(.6 * SR); out = np.zeros(n); tj = 0.; k = 0; m = int(.012 * SR)
    while tj < .55:
        add(out, tj, sq(1500 * (1 + k * .03), m) * env_ad(m, .0005, .004), .25); tj += .045 * (1 - tj / .75) + .012; k += 1
    return band(out, 300, 9000)
def achieve(p, t0=0):  # LOGRO DESBLOQUEADO: arpegio de 8 bits del acorde y nota larga, con brillo
    out = np.zeros(int(1.6 * SR)); tn = tones(chord_at(t0 + .1), (1, 2))
    for i, m in enumerate(tn[:4]):
        n = int((.6 if i == 3 else .08) * SR); add(out, i * .065, sq(note(m), n, .25 if i == 3 else .5) * env_ad(n, .002, .4 if i == 3 else .05), .25)
    n = int(.6 * SR); add(out, 3 * .065, sq(note(tn[1]), n, .5) * env_ad(n, .002, .4), .12)
    d = int(.14 * SR); out[d:] += out[:-d] * .3; sh = shine(1.1); add(out, .2, sh, .5)
    return band(out, 150, 10000)
def portal(p, t0=0):  # portal mágico: remolino de ruido que sube, sub que crece y campanas del acorde
    n = int(2.8 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 24
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = 250 * 10 ** (k / seg * 1.2); out[a:b] = band(x, c * .7, c * 1.5)[a:b]
    env = np.sin(np.pi * np.clip(t / 2.6, 0, 1))
    out *= (.6 + .4 * np.sin(2 * np.pi * (2 + 6 * t / t[-1]) * t)) * env * .8
    out += np.sin(2 * np.pi * np.cumsum(40 + 25 * t / t[-1]) / SR) * env ** 2 * .5
    for i, m in enumerate(tones(chord_at(t0 + .5), (1, 2))): add(out, .3 + i * .18, glock(note(m + 12), 1.2), .5)
    return out
def ocarina(p, t0=0):  # tres notas genéricas de ocarina (Mi–Re–Sol), no es ninguna canción existente
    out = np.zeros(int(1.8 * SR))
    for m, a, d in ((76, 0, .24), (74, .25, .24), (79, .5, .85)):
        n = int(d * SR); t = np.arange(n) / SR; ph = 2 * np.pi * np.cumsum(note(m) * (1 + .006 * np.sin(2 * np.pi * 5.2 * t) * np.clip((t - .2) / .2, 0, 1))) / SR
        x = np.sin(ph) + .06 * np.sin(2 * ph) + .03 * np.sin(3 * ph) + band(rng.standard_normal(n), note(m) * .8, note(m) * 3) * .08
        add(out, a, x * adsr(n, .03, .05, .85, .06), .45)
    return out + reverb(out, 1.2, 3.5)[:len(out)] * .4
def rumble(p, t0=0):  # temblor grave: el jefe despierta
    n = int(2.4 * SR); t = np.arange(n) / SR
    return np.tanh(band(rng.standard_normal(n), 25, 140) * 3 * (.4 + .6 * np.abs(np.sin(2 * np.pi * 1.7 * t)))) * np.sin(np.pi * np.clip(t / 2.3, 0, 1)) * .8
def erase(p, t0=0):  # recuerdo borrado: ruido digital que tartamudea y cae
    n = int(.8 * SR); t = np.arange(n) / SR; x = band(rng.standard_normal(n), 1000 * p, 9000)
    y = (x * .5 * (np.floor(t * 40) % 3 != 0) + np.sin(2 * np.pi * np.cumsum(2500 * p * np.exp(-t / .25) + 150) / SR) * .25) * np.exp(-t / .3)
    return np.round(y * 6) / 6
def roar(p, t0=0):  # rugido de estática del jefe (diseño propio)
    n = int(2.2 * SR); t = np.arange(n) / SR; s = 2 * (np.cumsum((55 + 18 * np.sin(2 * np.pi * .7 * t)) * p) / SR % 1) - 1
    growl = band(s * (1 + .6 * np.sin(2 * np.pi * 31 * t)), 40, 900) * 1.4   # grave: deja libre la banda de la voz («el olvido»)
    st = band(rng.standard_normal(n), 2500, 8000) * .25 * (.5 + .5 * np.sign(np.sin(2 * np.pi * 17 * t)))
    return np.tanh((growl + st) * 1.3) * np.clip(t / .25, 0, 1) * np.clip((t[-1] - t) / .9, 0, 1) * .8
def weapon(p, t0=0):  # el arma de la nostalgia: tono que sube, haz brillante y arpegio dorado
    n = int(1.3 * SR); t = np.arange(n) / SR
    out = np.sin(2 * np.pi * np.cumsum(400 * p + 1600 * p * (t / t[-1]) ** 2) / SR) * .15 * np.clip(t / .05, 0, 1)
    out += band(rng.standard_normal(n), 3000, 9000) * (t / t[-1]) ** 1.5 * .35
    tn = tones(chord_at(t0), (1,)); tn = tn + [m + 12 for m in tn]
    for i, m in enumerate(tn): add(out, i * .12, glock(note(m + 12), .5), .5)
    return out * np.clip((t[-1] - t) / .05, 0, 1)
def charge(p, t0=0):  # carga del golpe final: casi inaudible al principio (respeta el silencio) y sube en el último instante
    n = int(1.05 * SR); t = np.arange(n) / SR; k = (t / t[-1]) ** 4
    x = band(rng.standard_normal(n), 2000, 12000) * k * .5 + np.sin(2 * np.pi * np.cumsum(300 + 2500 * k) / SR) * k * .12
    return x * np.clip((t[-1] - t) / .01, 0, 1)
def boom(p, t0=0):  # golpe final: sub profundo, grieta y cola larga
    n = int(3.6 * SR); t = np.arange(n) / SR
    x = np.tanh((np.sin(2 * np.pi * np.cumsum(28 + 90 * np.exp(-t / .1)) / SR) * np.exp(-t / 1.1) * 1.2
                 + band(rng.standard_normal(n), 600, 12000) * np.exp(-t / .05) * .9 + band(rng.standard_normal(n), 40, 700) * np.exp(-t / .5) * .8) * 1.3)
    return x + reverb(x, 2.5, 1.6)[:n] * .6
def burst(p, t0=0):  # estallido de partículas doradas
    n = int(1.8 * SR); t = np.arange(n) / SR
    out = band((rng.random(n) < .03 * np.exp(-t / .5)) * rng.standard_normal(n), 2500, 14000) * 2.5
    tn = tones(chord_at(t0 + .3), (2, 3))
    for k in range(10): add(out, rng.uniform(0, .8), glock(note(tn[rng.integers(len(tn))]), .8), .4)
    return out
def dawn(p, t0=0):  # amanecer: aire que crece y brillo del acorde
    n = int(3.2 * SR); t = np.arange(n) / SR; out = band(rng.standard_normal(n), 1500, 9000) * np.sin(np.pi * np.clip(t / 3.1, 0, 1)) ** 2 * .25
    for i, m in enumerate(tones(chord_at(t0 + .3), (1, 2))): add(out, .4 + i * .16, glock(note(m + 12), 1.4), .35)
    return out
def chest(p, t0=0):  # cofre: rechinido de madera, cerrojo y brillo que sube (diseño propio)
    n = int(2.6 * SR); out = np.zeros(n); m = int(.5 * SR); tt = np.arange(m) / SR
    fr = 90 + 35 * np.sin(2 * np.pi * 1.4 * tt) + 12 * np.sin(2 * np.pi * 9 * tt)
    add(out, 0, band(2 * (np.cumsum(fr) / SR % 1) - 1, 300, 3500) * np.sin(np.pi * tt / tt[-1]), .45)
    add(out, 0, band(rng.standard_normal(int(.03 * SR)), 1500, 7000), .8)
    name = chord_at(t0 + .5)
    for i, mm in enumerate(tones(name, (1, 2))): add(out, .45 + i * .07, glock(note(mm + 12), 1.0), .45)
    r_, tr = CH[name]
    for i, mm in enumerate([r_ + 12] + tr): add(out, 1.0 + i * .03, bellf(note(mm), 1.5), .18)
    return out + reverb(out, 1.6, 2.4)[:n] * .3
def whirl(p, t0=0):  # giro: aire que da vueltas y sube
    n = int(.6 * SR); t = np.arange(n) / SR
    am = .5 + .5 * np.sin(2 * np.pi * np.cumsum(8 + 30 * t / t[-1]) / SR)
    return (band(rng.standard_normal(n), 600, 6000) * am * .6 + np.sin(2 * np.pi * np.cumsum(400 + 1400 * (t / t[-1]) ** 2) / SR) * .12) * np.sin(np.pi * t / t[-1]) ** 1.5
def fanfare(p, t0=0):  # fanfarria propia en Re mayor: tresillo que sube, nota larga y acorde final
    out = np.zeros(int(2.8 * SR))
    for a, d, ms in ((0, .11, (69,)), (.11, .11, (74,)), (.22, .11, (78,)), (.33, .55, (81, 78)), (.9, .14, (79, 76)), (1.04, .14, (83, 79)),
                     (1.18, 1.3, (86, 81, 78, 74))):
        n = int((d + .12) * SR)
        for k, m in enumerate(ms): add(out, a, brass(note(m), n, .012, .1, .8, bright=1.4), 1 if k == 0 else .6)
    return out * .6 + reverb(out, 1.6, 2.5)[:len(out)] * .35
def crt_off(p, t0=0):  # la tele se apaga: zap que cae, clic y golpe
    n = int(.6 * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * np.cumsum(2400 * np.exp(-t / .07) + 60) / SR) * np.exp(-t / .18) * .5 + band(rng.standard_normal(n), 1500, 8000) * np.exp(-t / .01) * .8
         + np.sin(2 * np.pi * np.cumsum(50 + 60 * np.exp(-t / .03)) / SR) * np.exp(-t / .1) * .5)
    return x * np.clip((t[-1] - t) / .1, 0, 1)
GEN = dict(hum=(hum, .3), crt_on=(crt_on, .35), static=(static, .25), pixel=(pixel, .3), select=(select, .3), chip=(chip, .3), tick=(tick, .2),
           rise=(rise, .3), whoosh=(whoosh, .24), sweep=(sweep, .24), quest=(quest, .32), paper=(paper, .28), token=(token, .3), pop=(pop, .3),
           tape=(tape, .32), impact=(impact, .32), chime=(chime, .3), sparkle=(sparkle, .28), assemble=(assemble, .2), chord=(chord, .3),
           cartridge=(cartridge, .22), count=(count, .2), achieve=(achieve, .34), portal=(portal, .34), flash=(flash, .28), morph=(morph, .26),
           ocarina=(ocarina, .42), rumble=(rumble, .4), erase=(erase, .3), roar=(roar, .26), weapon=(weapon, .2), hit=(hit, .32), charge=(charge, .3),
           boom=(boom, .45), burst=(burst, .32), dawn=(dawn, .3), chest=(chest, .28), key=(key, .32), send=(send, .3), click=(click, .32),
           whirl=(whirl, .28), fanfare=(fanfare, .42), crt_off=(crt_off, .35))
fx = np.zeros(N)
for e in TL['sfx']:
    fn, gn = GEN[e['type']]; add(fx, e['t'], fn(e['pitch'], e['t']), gn * e['v'])
fx[-fo:] *= np.linspace(1, 0, fo)
fxs = np.stack([fx, fx])

def save(path, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
def lufs(x):  # sonoridad integrada (EBU R128) medida con ffmpeg
    p = os.path.join(OUT, '_medir.wav'); save(p, x / max(1., np.abs(x).max()))
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    os.remove(p); return float(r[r.rfind('I:') + 2:].split('LUFS')[0]) + 20 * np.log10(max(1., np.abs(x).max()))
mus *= 10 ** ((-29.5 - lufs(mus)) / 20); fxs *= 10 ** ((-22.5 - lufs(fxs)) / 20)
mix = np.tanh(mus + fxs)
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-sin-voz.wav', mix)
print('BPM %.2f' % BPM, 'compases', NB, 'pico música %.3f' % np.abs(mus).max(), 'pico efectos %.3f' % np.abs(fxs).max(), 'pico mezcla %.3f' % np.abs(mix).max(),
      'música en el silencio %.5f' % np.abs(mus[:, int(SIL0 * SR) + 10:int(SIL1 * SR) - 10]).max())
