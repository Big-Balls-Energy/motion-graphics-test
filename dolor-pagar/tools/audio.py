"""Genera música electrónica lo-fi con tensión (104 BPM) + efectos sincronizados con timeline.json. Sin voz."""
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
# electrónica lo-fi con tensión, 104 BPM (swing): Am9 – Fmaj7 – Dm9 – E7
BPM = 104; beat = 60 / BPM; bar = beat * 4
note = lambda m: 440 * 2 ** ((m - 69) / 12)
CH = [[57, 60, 64, 67, 71], [53, 57, 60, 64], [50, 53, 57, 60, 64], [52, 56, 59, 62]]
L = np.zeros(N); R = np.zeros(N); nb = int(DUR / bar) + 2
def rhodes(f, n):
    tt = np.arange(n) / SR; x = np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt) * np.exp(-tt / .4) + .12 * np.sin(6 * np.pi * f * tt) * np.exp(-tt / .2)
    return x * env_ad(n, .008, 1.6) * (1 + .12 * np.sin(2 * np.pi * 4.5 * tt))
kick_n = int(.35 * SR); kt = np.arange(kick_n) / SR; kick = np.sin(2 * np.pi * np.cumsum(45 + 70 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .12) * .7
sn_n = int(.3 * SR); st_ = np.arange(sn_n) / SR; snare = band(rng.standard_normal(sn_n), 600, 5000) * np.exp(-st_ / .09) * .32 + np.sin(2 * np.pi * 180 * st_) * np.exp(-st_ / .04) * .2
hat_n = int(.05 * SR); hat = band(rng.standard_normal(hat_n), 6000, 14000) * np.exp(-np.arange(hat_n) / SR / .015) * .12
for bi in range(nb):
    t0 = bi * bar; ch = CH[bi % 4]; n = int(bar * SR * 1.05)
    for j, m in enumerate(ch):
        x = rhodes(note(m), n) * .045; add(L, t0 + j * .012, x * (1.1 - j * .05)); add(R, t0 + j * .012 + .004, x * (.9 + j * .05))
    nn = int(bar * SR); t2 = np.arange(nn) / SR; bs = np.sin(2 * np.pi * note(ch[0] - 24) * t2) * env_ad(nn, .02, 1.4) * .28; add(L, t0, bs); add(R, t0, bs)
    for q in (0, 2.5): add(L, t0 + q * beat, kick); add(R, t0 + q * beat, kick)
    for q in (1, 3): add(L, t0 + q * beat, snare); add(R, t0 + q * beat, snare)
    for q in range(8):
        sw = .06 * beat if q % 2 else 0; add(L, t0 + q * beat / 2 + sw, hat * (1 if q % 2 else .6)); add(R, t0 + q * beat / 2 + sw, hat * .8)
# capa de tensión: nota aguda sostenida y pulso grave en las escenas de dolor
tt = np.arange(N) / SR
ten = np.sin(2 * np.pi * note(76) * tt) * (.5 + .5 * np.sin(2 * np.pi * .25 * tt)) * .03 + np.sin(2 * np.pi * note(77) * tt) * .012
pulse = np.sin(2 * np.pi * 55 * tt) * (np.sin(2 * np.pi * (BPM / 60) * tt) > .6) * .06
w = np.zeros(N)
for a0, b0 in ((5.6, 21.5), (29.6, 32.3), (51.4, 54.4)):
    w += np.clip((tt - a0) / .5, 0, 1) * np.clip((b0 - tt) / .5, 0, 1)
L += (ten + pulse) * w; R += (ten * .9 + pulse) * w
crackle = (rng.random(N) > .9993) * rng.uniform(-.3, .3, N); L += crackle * .25; R += crackle * .25
mus = np.stack([L, R]); mus /= np.abs(mus).max()
# ducking: 18% sin texto, 12% con subtítulos (más espacio para la voz)
g = np.full(N, 0.18)
for s in TL['subs']: g[int(s['a'] * SR):int(s['b'] * SR)] = 0.12
for h in TL['holds'] + TL.get('cards', []): g[int(h['a'] * SR):int(h['b'] * SR)] = 0.12
k = int(0.15 * SR); g = np.convolve(g, np.ones(k) / k, mode='same')
for a, b, m in TL.get('musicBoost', []):
    k = np.ones(N); i0, i1 = int(a * SR), int(b * SR); k[i0:i1] = np.linspace(1, m, i1 - i0); k = np.convolve(k, np.ones(int(.3 * SR)) / int(.3 * SR), 'same'); g = g * k
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
def alert(p):
    out = np.zeros(int(0.42 * SR))
    for k, f in enumerate((988, 1319, 988, 1319)):
        n = int(0.09 * SR); tt = np.arange(n) / SR; sq = np.tanh(4 * np.sin(2 * np.pi * f * p * tt)) * env_ad(n, 0.003, 0.05) * 0.5
        j = int(k * 0.1 * SR); out[j:j + n] += sq[: len(out) - j]
    return out
def register(p):
    n = int(0.9 * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    dr = band(rng.standard_normal(int(.12 * SR)), 300, 3000) * np.exp(-np.arange(int(.12 * SR)) / SR / .03) * .7; out[:len(dr)] += dr
    j = int(0.08 * SR); bl = ding(1.35 * p)[: n - j] * 1.4; out[j:j + len(bl)] += bl
    for k in range(5):
        jj = int((0.12 + k * 0.05) * SR); c = clink(1.0 + k * 0.07)[: n - jj] * 0.5; out[jj:jj + len(c)] += c
    return out
def warn(p):
    out = np.zeros(int(0.6 * SR))
    for k, f in enumerate((587, 440)):
        n = int(0.25 * SR); tt = np.arange(n) / SR; s = np.sin(2 * np.pi * f * p * tt) * env_ad(n, 0.02, 0.12) * 0.55
        j = int(k * 0.22 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def flip(p):
    n = int(0.16 * SR); tt = np.arange(n) / SR
    snap = band(rng.standard_normal(n), 1500 * p, 9000) * np.exp(-tt / 0.02) * 1.2
    sw = band(rng.standard_normal(n), 400, 2500) * np.sin(np.pi * tt / tt[-1]) * 0.5
    return snap + sw
def rise(p):
    out = np.zeros(int(1.6 * SR))
    for k, m in enumerate((62, 65, 69, 74, 77)):
        n = int(1.3 * SR); tt = np.arange(n) / SR; f = 440 * 2 ** ((m - 69) / 12) * p
        s = (np.sin(2 * np.pi * f * tt) + .4 * np.sin(4 * np.pi * f * tt) + .2 * np.sin(6 * np.pi * f * tt)) * env_ad(n, 0.01, 0.6) * 0.3
        j = int(k * 0.07 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def clapsfx(p):
    n = int(0.3 * SR); tt = np.arange(n) / SR
    crack = band(rng.standard_normal(n), 1500, 9000) * np.exp(-tt / 0.012) * 1.6
    body = (np.sin(2 * np.pi * 180 * tt) + band(rng.standard_normal(n), 200, 1500)) * np.exp(-tt / 0.05) * 0.7
    return crack + body
def pages(p):
    n = int(0.9 * SR); tt = np.arange(n) / SR; out = np.zeros(n)
    for k in range(4):
        j = int(k * 0.17 * SR); m = int(0.25 * SR); x = band(rng.standard_normal(m), 2000, 9000) * np.sin(np.pi * np.arange(m) / m) * (0.7 + .3 * np.sin(2 * np.pi * 40 * np.arange(m) / SR))
        out[j:j + m] += x[: n - j]
    return out * 0.8
def thunder(p):
    n = int(2.2 * SR); tt = np.arange(n) / SR
    x = band(rng.standard_normal(n), 30, 400) * (np.exp(-tt / 0.6) * (1 + 0.6 * np.sin(2 * np.pi * 3 * tt))) * 1.8
    crack = band(rng.standard_normal(n), 800, 5000) * np.exp(-tt / 0.08) * 0.5
    return np.tanh(x + crack)
def triumph(p):
    out = np.zeros(int(2.4 * SR))
    for k, m in enumerate((60, 64, 67, 72, 76)):
        n = int(2.2 * SR); tt = np.arange(n) / SR; f = 440 * 2 ** ((m - 69) / 12)
        s = sum(np.sin(2 * np.pi * f * h * tt) / h for h in range(1, 5)) * np.minimum(1, tt / 0.03) * np.exp(-tt / 1.1) * 0.22
        j = int(k * 0.06 * SR); out[j:j + n] += s[: len(out) - j]
    return out
def key(p):
    n = int(0.05 * SR); tt = np.arange(n) / SR
    return (band(rng.standard_normal(n), 1500, 8000) * 0.8 + np.sin(2 * np.pi * 900 * p * tt) * 0.3) * np.exp(-tt / 0.008)
def impact(p):  # golpe metálico de lata contra el piso
    n = int(1.2 * SR); tt = np.arange(n) / SR
    thump = np.sin(2 * np.pi * np.cumsum(45 + 90 * np.exp(-tt / .03)) / SR) * np.exp(-tt / .12) * .9
    ring = sum(a * np.sin(2 * np.pi * f * p * tt) * np.exp(-tt / d) for f, a, d in ((523, .5, .35), (1187, .35, .22), (2113, .25, .14), (3307, .18, .09)))
    crack = band(rng.standard_normal(n), 1500, 9000) * np.exp(-tt / .015) * .8
    return np.tanh((thump + ring * .7 + crack) * 1.3)
def psst(p):  # lata que se abre: clic + siseo
    n = int(0.9 * SR); tt = np.arange(n) / SR
    clk = band(rng.standard_normal(n), 2000, 9000) * np.exp(-tt / .006) * 1.2
    hiss = band(rng.standard_normal(n), 3500, 12000) * np.clip(tt / .03, 0, 1) * np.exp(-tt / .28) * .9
    return clk + hiss
def stamp(p):  # sello de goma
    n = int(0.35 * SR); tt = np.arange(n) / SR
    return (np.sin(2 * np.pi * 80 * p * tt) * np.exp(-tt / .05) * 1.0 + band(rng.standard_normal(n), 200 * p, 2500 * p) * np.exp(-tt / .03) * 1.0)
def scratch(p):  # scratch de vinilo
    n = int(0.7 * SR); tt = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n)
    sp = np.sin(2 * np.pi * 2.8 * tt) * np.sin(np.pi * tt / tt[-1])
    for k in range(6):
        seg = slice(int(k * n / 6), int((k + 1) * n / 6)); c = 900 + 1400 * abs(np.mean(sp[seg]))
        out[seg] = band(x, c * .6, c * 1.6)[seg]
    tone = np.sin(2 * np.pi * np.cumsum(300 + 500 * sp) / SR) * .6
    return np.tanh((out * 1.4 + tone) * np.abs(sp) * 2) * .8
def coin(p):
    out = clink(1.25 * p) * 1.2; d = ding(1.6 * p)[: len(out)]; return out + d[:len(out)] * .6
def tear(p):  # papel rasgado
    n = int(0.5 * SR); tt = np.arange(n) / SR; x = band(rng.standard_normal(n), 1200, 9000)
    am = (rng.random(n) > .6).astype(float); am = np.convolve(am, np.ones(60) / 60, 'same')
    return x * am * np.sin(np.pi * tt / tt[-1]) * 1.8
def thud(p):
    n = int(0.3 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 95 * p * tt) * np.exp(-tt / .06) + band(rng.standard_normal(n), 100, 900) * np.exp(-tt / .03) * .6
def marker(p):  # plumón sobre papel
    n = int(0.5 * SR); tt = np.arange(n) / SR
    return band(rng.standard_normal(n), 2500, 7000) * (.5 + .5 * np.sin(2 * np.pi * 9 * tt)) * np.sin(np.pi * tt / tt[-1]) * .7
def spin(p):
    n = int(0.9 * SR); tt = np.arange(n) / SR
    return band(rng.standard_normal(n), 500, 4000) * (.5 + .5 * np.sin(2 * np.pi * (6 + 10 * (1 - tt / tt[-1])) * tt)) * np.sin(np.pi * tt / tt[-1]) * 1.1
def glass(p):  # crujido de vidrio en la grieta
    n = int(1.0 * SR); tt = np.arange(n) / SR; out = band(rng.standard_normal(n), 2500, 12000) * np.exp(-tt / .05) * 1.2
    for k in range(28):
        j = int(rng.uniform(0, .6) * SR); m = int(.03 * SR); f = rng.uniform(3000, 7000)
        out[j:j + m] += np.sin(2 * np.pi * f * np.arange(m) / SR) * np.exp(-np.arange(m) / SR / .006) * rng.uniform(.3, .8)
    return out
def tankfx(p):  # motor de tanque + orugas
    n = int(2.0 * SR); tt = np.arange(n) / SR
    eng = np.tanh(3 * (np.sin(2 * np.pi * 38 * tt) + .6 * np.sign(np.sin(2 * np.pi * 19 * tt)))) * .4
    tread = band(rng.standard_normal(n), 300, 2500) * (np.sin(2 * np.pi * 9 * tt) > .6) * .6
    return band(eng, 30, 800) * 1.2 + tread
def heli(p):  # hélice de helicóptero
    n = int(2.0 * SR); tt = np.arange(n) / SR
    chop = (.5 + .5 * np.sign(np.sin(2 * np.pi * 13 * tt))) * np.exp(-((tt % (1 / 13)) / .02))
    return band(rng.standard_normal(n), 80, 900) * chop * 1.6 + band(rng.standard_normal(n), 2000, 6000) * .08
def switch(p):  # interruptor que se apaga
    n = int(0.12 * SR); tt = np.arange(n) / SR
    return (band(rng.standard_normal(n), 1500, 7000) * np.exp(-tt / .004) * 1.2 + np.sin(2 * np.pi * 900 * p * tt) * np.exp(-tt / .01) * .3)
def fire(p):  # papel quemándose
    n = int(1.8 * SR); tt = np.arange(n) / SR; out = band(rng.standard_normal(n), 300, 3000) * .25 * np.sin(np.pi * tt / tt[-1])
    for k in range(60):
        j = int(rng.uniform(0, 1.6) * SR); m = int(.01 * SR); out[j:j + m] += band(rng.standard_normal(m), 1500, 8000) * rng.uniform(.3, .9)
    return out
def tapestop(p):  # caída de tono
    n = int(1.6 * SR); tt = np.arange(n) / SR; f = 220 * (1 - .9 * (tt / tt[-1]) ** 1.3)
    return np.tanh(3 * np.sin(2 * np.pi * np.cumsum(f) / SR)) * .25 * (1 - tt / tt[-1]) + band(rng.standard_normal(n), 100, 600) * .15 * (1 - tt / tt[-1])
def chips(p):  # fichas de casino chocando
    n = int(.7 * SR); out = np.zeros(n)
    for k in range(9):
        j = int(rng.uniform(0, .45) * SR); m = int(.06 * SR); tt = np.arange(m) / SR; f = rng.uniform(2200, 4200) * p
        c = (np.sin(2 * np.pi * f * tt) + .6 * np.sin(2 * np.pi * f * 1.47 * tt)) * np.exp(-tt / .012) + band(rng.standard_normal(m), 2000, 9000) * np.exp(-tt / .004) * .8
        out[j:j + m] += c[: n - j] * rng.uniform(.4, 1)
    return out * .8
def heart(p):  # latido grave
    n = int(.35 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * np.cumsum(38 + 40 * np.exp(-tt / .04)) / SR) * np.exp(-tt / .1) * 1.4
def pulsefx(p):  # pulso de alerta en la zona del cerebro
    n = int(1.2 * SR); tt = np.arange(n) / SR
    return np.sin(2 * np.pi * 220 * tt) * np.exp(-tt / .5) * (.5 + .5 * np.sin(2 * np.pi * 6 * tt)) * .5
def printer(p):  # ticket que se imprime y se alarga
    n = int(3.3 * SR); tt = np.arange(n) / SR
    return band(rng.standard_normal(n), 1500, 6000) * (.6 + .4 * np.sign(np.sin(2 * np.pi * 38 * tt))) * np.clip(tt / .1, 0, 1) * np.clip((3.3 - tt) / .3, 0, 1) * .35
def beep(p):  # pago sin contacto
    out = np.zeros(int(.35 * SR))
    for k, f in enumerate((1760, 2349)):
        m = int(.12 * SR); tt = np.arange(m) / SR; j = int(k * .13 * SR); out[j:j + m] += np.sin(2 * np.pi * f * p * tt) * env_ad(m, .003, .06) * .5
    return out
def relief(p):  # alivio: barrido descendente suave
    n = int(.9 * SR); tt = np.arange(n) / SR; f = 900 * np.exp(-tt * 2.2) + 300
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.sin(np.pi * tt / tt[-1]) * .35 + band(rng.standard_normal(n), 2000, 8000) * np.exp(-tt / .3) * .1
GEN = dict(chips=(chips, .34), heart=(heart, .40), pulse=(pulsefx, .28), printer=(printer, .22), beep=(beep, .30), relief=(relief, .26),
glass=(glass, .34), tank=(tankfx, .26), heli=(heli, .28), switch=(switch, .30), fire=(fire, .28), tapestop=(tapestop, .30),
impact=(impact, .42), psst=(psst, .30), stamp=(stamp, .36), scratch=(scratch, .32), coin=(coin, .32), tear=(tear, .26), thud=(thud, .32), marker=(marker, .26), spin=(spin, .24),
clap=(clapsfx, .32), pages=(pages, .28), thunder=(thunder, .30), triumph=(triumph, .30), key=(key, .30), flip=(flip, .30), rise=(rise, .32), alert=(alert, .28), register=(register, .26), warn=(warn, .30), clink=(clink, .30), step=(step, .30), gift=(giftopen, .30), cling=(cling, .30), tictac=(tictac, .30), buzz=(buzz, .32), pop=(pop, .30), whoosh=(whoosh, .22), ding=(ding, .30), tick=(tick, .18), click=(click, .45), strike=(strike, .22), shine=(shine, .25))
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
save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fxs); save(OUT + '/mezcla-sin-voz.wav', mix)
print('peak mix', np.abs(mix).max(), 'music rms', np.sqrt((mus ** 2).mean()))
