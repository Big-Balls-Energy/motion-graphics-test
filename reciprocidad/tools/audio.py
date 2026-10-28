"""Genera música lo-fi (102 BPM) + efectos sincronizados con timeline.json. Sin voz."""
import json, sys, wave, numpy as np
SR = 48000; DUR = 60.0; N = int(SR * DUR)
TL = json.load(open(sys.argv[1])); OUT = sys.argv[2]
rng = np.random.default_rng(7)
t_all = np.arange(N) / SR

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR)
    X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def env_ad(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na)
    e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def add(buf, start, sig, gain=1.0):
    i = int(start * SR); j = min(len(buf), i + len(sig))
    if j > i: buf[i:j] += sig[: j - i] * gain

# ---------------- MÚSICA ----------------
BPM = 102; beat = 60 / BPM; bar = beat * 4
note = lambda m: 440 * 2 ** ((m - 69) / 12)
chords = [[48, 52, 55, 59], [57, 60, 64, 67], [50, 53, 57, 60], [55, 59, 62, 65]]  # Cmaj7 Am7 Dm7 G7
musL = np.zeros(N); musR = np.zeros(N)
nb = int(np.ceil(DUR / bar)) + 1
for b in range(nb):
    t0 = b * bar; ch = chords[b % 4]; n = int(bar * SR * 1.1); tt = np.arange(n) / SR
    e = np.minimum(1, tt / 0.35) * np.exp(-tt / 3.0)
    for k, m in enumerate(ch):
        f = note(m)
        for side, det in ((musL, 0.997), (musR, 1.003)):
            s = np.sin(2 * np.pi * f * det * tt) + 0.3 * np.sin(2 * np.pi * 2 * f * det * tt + k)
            add(side, t0, s * e * 0.10)
    # bajo
    for q in (0, 2, 3.5):
        nn = int(beat * 1.2 * SR); tt2 = np.arange(nn) / SR
        s = np.sin(2 * np.pi * note(ch[0] - 12) * tt2) * env_ad(nn, 0.01, 0.35) * 0.35
        add(musL, t0 + q * beat, s); add(musR, t0 + q * beat, s)
    # piano/keys suave: arpegio en corcheas
    for q in range(8):
        m = ch[[0, 2, 1, 3, 2, 1, 3, 2][q]] + 12; nn = int(0.6 * SR); tt2 = np.arange(nn) / SR
        sw = 0.06 * beat if q % 2 else 0
        s = (np.sin(2 * np.pi * note(m) * tt2) + 0.2 * np.sin(4 * np.pi * note(m) * tt2)) * env_ad(nn, 0.005, 0.18) * 0.07
        add(musL if q % 2 else musR, t0 + q * beat / 2 + sw, s); add(musR if q % 2 else musL, t0 + q * beat / 2 + sw, s * 0.5)
# batería
kick_n = int(0.4 * SR); kt = np.arange(kick_n) / SR
kick = np.sin(2 * np.pi * np.cumsum(45 + 80 * np.exp(-kt / 0.03)) / SR) * np.exp(-kt / 0.12) * 0.7
sn_n = int(0.25 * SR); st = np.arange(sn_n) / SR
snare = (band(rng.standard_normal(sn_n), 900, 6000) * 0.5 + np.sin(2 * np.pi * 185 * st) * 0.4) * np.exp(-st / 0.06) * 0.45
hat_n = int(0.06 * SR)
hat = band(rng.standard_normal(hat_n), 7000, 16000) * np.exp(-np.arange(hat_n) / SR / 0.015) * 0.18
nbeats = int(DUR / beat) + 1
for i in range(nbeats):
    tb = i * beat
    if i % 4 in (0, 2) or (i % 8 == 7): add(musL, tb, kick); add(musR, tb, kick)
    if i % 4 in (1, 3): add(musL, tb, snare); add(musR, tb, snare)
    for h, sw in ((0, 0), (0.5, 0.06)):
        g = 1 if h == 0 else 0.6
        add(musL, tb + (h + sw) * beat, hat * g); add(musR, tb + (h + sw) * beat, hat * g * 0.8)
# vinilo
crk = np.zeros(N); idx = rng.integers(0, N, 900); crk[idx] = rng.standard_normal(900) * 0.3
crk = band(crk + rng.standard_normal(N) * 0.004, 1500, 9000)
musL += crk; musR += crk
mus = np.stack([musL, musR]); mus /= np.abs(mus).max()
# ducking: 18% sin texto, 12% con subtítulos (más espacio para la voz)
g = np.full(N, 0.18)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.12
for h in TL['holds']: g[int(h['a'] * SR):int(h['b'] * SR)] = 0.13
k = int(0.15 * SR); g = np.convolve(g, np.ones(k) / k, mode='same')
mus *= g

# ---------------- EFECTOS ----------------
def pop(p):
    n = int(0.14 * SR); tt = np.arange(n) / SR
    f = (380 + 650 * np.exp(-tt / 0.025)) * p
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * env_ad(n, 0.002, 0.045)
def whoosh(p):
    n = int(0.55 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n)
    lo = band(x, 250, 1200); hi = band(x, 1200, 5000); m = tt / tt[-1]
    s = lo * (1 - m) + hi * m * 0.7; e = np.sin(np.pi * np.clip(tt / 0.5, 0, 1)) ** 2
    return s * e * 1.4
def ding(p):
    n = int(1.4 * SR); tt = np.arange(n) / SR; f = 1318.5 * p
    s = np.sin(2 * np.pi * f * tt) + 0.5 * np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt / 0.2) + 0.25 * np.sin(2 * np.pi * f * 2.76 * tt) * np.exp(-tt / 0.12)
    return s * env_ad(n, 0.002, 0.45) * 0.5
def tick(p):
    n = int(0.03 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 2100 * p * tt) * env_ad(n, 0.001, 0.006) * 0.6
def click(p):
    n = int(0.09 * SR); s = np.zeros(n); x = band(rng.standard_normal(n), 2000, 9000)
    e = np.zeros(n); e[:int(.008 * SR)] = 1; e[int(.045 * SR):int(.05 * SR)] = .6
    return x * e * 1.2
def strike(p):
    n = int(0.35 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 1800, 6000)
    return x * (0.6 + 0.4 * np.sin(2 * np.pi * 28 * tt)) * np.sin(np.pi * tt / tt[-1]) * 1.1
def shine(p):
    out = np.zeros(int(1.0 * SR))
    for i, m in enumerate([84, 88, 91, 96, 100]):
        n = int(0.6 * SR); tt = np.arange(n) / SR
        s = np.sin(2 * np.pi * note(m) * tt) * env_ad(n, 0.002, 0.15) * 0.25
        j = int(i * 0.05 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def murmur(length, fade_in, fade_out):
    n = int(length * SR); tt = np.arange(n) / SR; s = np.zeros(n)
    for v in range(10):  # varias "voces"
        x = band(rng.standard_normal(n), 250 + 60 * v, 900 + 120 * v)
        rate = rng.uniform(3, 6); ph = rng.uniform(0, 6)
        am = np.clip(np.sin(2 * np.pi * rate * tt + ph) + rng.uniform(-.2, .4), 0, None)
        s += x * am * (0.6 + 0.4 * np.sin(2 * np.pi * rng.uniform(.2, .5) * tt + ph))
    s /= np.abs(s).max(); e = np.ones(n)
    if fade_in: e *= np.clip(tt / fade_in, 0, 1)
    if fade_out: e *= np.clip((length - tt) / fade_out, 0, 1)
    return s * e
def cling(p):
    n = int(0.5 * SR); tt = np.arange(n) / SR; f = 2650 * p
    s = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt / d) for r, a, d in ((1, 1, .18), (1.48, .6, .12), (2.31, .45, .08), (3.07, .3, .05)))
    return s * env_ad(n, 0.001, 0.2) * 0.45
def tictac(p):
    n = int(0.05 * SR); tt = np.arange(n) / SR
    s = np.sin(2 * np.pi * 1500 * p * tt) * 0.6 + band(rng.standard_normal(n), 2500, 8000) * 0.5
    return s * env_ad(n, 0.0005, 0.008)
def buzz(p):
    n = int(0.45 * SR); tt = np.arange(n) / SR; f = 82 * p
    s = 2 * ((f * tt) % 1) - 1 + 0.5 * np.sign(np.sin(2 * np.pi * f * 1.01 * tt))
    s = band(s, 40, 1400) * (1 + 0.3 * np.sin(2 * np.pi * 30 * tt))
    return np.tanh(s * 1.5) * env_ad(n, 0.01, 0.2) * 0.6
def clink(p):
    n = int(0.35 * SR); tt = np.arange(n) / SR; f = 3400 * p
    s = sum(a * np.sin(2 * np.pi * f * r * tt) * np.exp(-tt / d) for r, a, d in ((1, 1, .09), (1.37, .5, .06), (2.1, .3, .04)))
    return s * env_ad(n, 0.0008, 0.12) * 0.5
def step(p):
    n = int(0.16 * SR); tt = np.arange(n) / SR
    s = band(rng.standard_normal(n), 60, 700) * 1.4 + np.sin(2 * np.pi * 70 * p * tt) * 0.6
    return s * env_ad(n, 0.003, 0.04)
def giftopen(p):
    n = int(0.6 * SR); tt = np.arange(n) / SR
    rustle = band(rng.standard_normal(n), 1500, 7000) * (0.5 + 0.5 * np.sin(2 * np.pi * 18 * tt)) * np.exp(-tt / 0.18) * 0.8
    out = rustle.copy(); sh = shine(1.0); j = int(0.12 * SR); out[j:j + len(sh)] += sh[: n - j]
    return out
GEN = dict(clink=(clink, .30), step=(step, .30), gift=(giftopen, .30), cling=(cling, .30), tictac=(tictac, .30), buzz=(buzz, .32), pop=(pop, .30), whoosh=(whoosh, .22), ding=(ding, .30), tick=(tick, .18), click=(click, .45), strike=(strike, .22), shine=(shine, .25))
fx = np.zeros(N)
for e in TL['sfx']:
    if e['type'] == 'murmur': add(fx, e['t'], murmur(2.9, 0.05, 0.6), 0.16 * e['v'])
    elif e['type'] == 'murmurIn': add(fx, e['t'], murmur(DUR - e['t'], 0.5, 0), 0.16 * e['v'])
    else:
        fn, gn = GEN[e['type']]; add(fx, e['t'], fn(e['pitch']), gn * e['v'])
fxs = np.stack([fx, fx])
mix = np.tanh((mus + fxs) * 1.0)

def save(path, x):
    x = np.clip(x, -1, 1); d = (x.T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-reciprocidad.wav', mix)
print('peak mix', np.abs(mix).max(), 'music rms', np.sqrt((mus ** 2).mean()))
