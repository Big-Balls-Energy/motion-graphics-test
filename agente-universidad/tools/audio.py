"""Audio de la edición: voz original recortada con los mismos tramos del video, música original y efectos sincronizados.

Uso (desde agente-universidad/): python3 tools/audio.py tools/plan.json tools/timeline.json audio
  voz         la voz del video fuente, cortada en los tramos de plan.json (fundidos de 6 ms que no cambian la duración),
              sin graves de ruido y con un nivelador suave
  música      house/pop original a ~123 BPM (28 compases exactos: el loop cierra), sin derechos: tensión en el problema,
              «drop» cuando entra Atlas Path, groove ligero en el caso y subida en el cierre; se agacha 25 % bajo la voz
  efectos     los de timeline.json (notificaciones genéricas, pops, whooshes, clics, éxito…), diseñados aquí
Escribe voz.wav, musica-sola.wav, efectos-solos.wav, mezcla-final.wav (voz + música + efectos) y mezcla-sin-musica.wav
(voz + efectos, para poner encima un audio en tendencia de Instagram). Niveles: voz −18, música −30 y efectos −27.5 LUFS."""
import json, os, subprocess, sys, wave
import numpy as np
from scipy.signal import fftconvolve
PLAN = json.load(open(sys.argv[1])); TL = json.load(open(sys.argv[2])); OUT = sys.argv[3]
SR = 48000; DUR = PLAN['n'] / PLAN['fps']; N = int(round(DUR * SR))
rng = np.random.default_rng(7)
T = np.arange(N) / SR

def band(x, lo, hi):
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR); X[(f < lo) | (f > hi)] = 0; return np.fft.irfft(X, len(x))
def soft(x, lo=0, hi=0, o=2):  # filtro suave de fase cero para pistas largas
    X = np.fft.rfft(x); f = np.fft.rfftfreq(len(x), 1 / SR) + 1e-9; H = np.ones_like(f)
    if hi: H /= np.sqrt(1 + (f / hi) ** (2 * o))
    if lo: H /= np.sqrt(1 + (lo / f) ** (2 * o))
    return np.fft.irfft(X * H, len(x))
def env_ad(n, a, d):
    e = np.ones(n); na = max(1, int(a * SR)); e[:na] = np.linspace(0, 1, na); e[na:] = np.exp(-np.arange(n - na) / (d * SR)); return e
def add(buf, start, sig, gain=1.0):
    i = int(round(start * SR)); j = min(len(buf), i + len(sig))
    if i < 0: sig = sig[-i:]; i = 0
    if j > i: buf[i:j] += sig[: j - i] * gain
note = lambda m: 440 * 2 ** ((m - 69) / 12)
def saw(f, n, ph=0.0): t = np.arange(n) / SR; return 2 * ((f * t + ph) % 1) - 1
def smooth(x, k):
    c = np.cumsum(np.concatenate([[0.0], x])); h = k // 2; i = np.arange(len(x)); lo = np.clip(i - h, 0, len(x)); hi = np.clip(i + h, 0, len(x))
    return (c[hi] - c[lo]) / np.maximum(hi - lo, 1)
def reverb(x, secs=1.6, damp=3.0, seed=1):
    r = np.random.default_rng(seed); n = int(secs * SR); t = np.arange(n) / SR
    ir = r.standard_normal(n) * np.exp(-t * damp) * (1 - np.exp(-t * 400)); ir = band(ir, 200, 9000); ir /= np.abs(ir).sum() ** .5 * 40
    return fftconvolve(x, ir)[: len(x)]
def riser(len_s, f0=300, f1=6000):
    n = int(len_s * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); out = np.zeros(n); seg = 12
    for k in range(seg):
        a, b = int(k * n / seg), int((k + 1) * n / seg); c = f0 * (f1 / f0) ** (k / seg); out[a:b] = band(x, c * .6, c * 1.6)[a:b]
    return out * (t / len_s) ** 2 * .6
def save(path, x):
    x = np.clip(x, -1, 1); x = np.stack([x, x]) if x.ndim == 1 else x; d = (x.T * 32767).astype('<i2')
    with wave.open(path, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
def lufs(x):  # sonoridad integrada EBU R128 con ffmpeg
    p = os.path.join(OUT, '_medir.wav'); pk = max(1e-9, np.abs(x).max()); save(p, x / max(1, pk))
    r = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', p, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    os.remove(p); return float(r[r.rfind('I:') + 2:].split('LUFS')[0]) + 20 * np.log10(max(1, pk))
def to_lufs(x, target): return x * 10 ** ((target - lufs(x)) / 20)

# ---------------- VOZ ----------------
src = subprocess.run(['ffmpeg', '-v', 'error', '-i', 'fuente/video_original.mp4', '-vn', '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True).stdout
src = np.frombuffer(src, np.float32).astype(np.float64)
voice = np.zeros(N); XF = int(.006 * SR); pos = 0
for k, (a, b) in enumerate(PLAN['segs']):
    i0, i1 = int(round(a * SR)), int(round(b * SR)); seg = src[max(0, i0 - XF):min(len(src), i1 + XF)].copy()
    pre = i0 - max(0, i0 - XF); n = len(seg)
    fade = np.ones(n)
    if k > 0: fade[:2 * XF] = np.sin(np.linspace(0, np.pi / 2, 2 * XF)) ** 2          # cruce de igual potencia centrado en la unión
    if k < len(PLAN['segs']) - 1: fade[-2 * XF:] = np.cos(np.linspace(0, np.pi / 2, 2 * XF)) ** 2
    add(voice, pos / SR - pre / SR, seg * fade); pos += i1 - i0
voice = band(voice, 75, 16000)
lev = smooth(np.abs(voice), int(.12 * SR)) + 1e-4                                       # nivelador suave (sube lo bajo, baja lo alto)
ref = np.percentile(lev[lev > lev.max() * .05], 60); voice *= np.clip((ref / lev) ** .3, .6, 1.6)
voice = to_lufs(voice, -18.0)
vact = smooth((np.abs(voice) > np.abs(voice).max() * .05).astype(float), int(.3 * SR))

# ---------------- MÚSICA ----------------
BARS = 28; BPM = BARS * 4 * 60 / DUR; beat = 60 / BPM; bar = 4 * beat
TR = TL['transitions']; END = DUR
def bar_of(t): return int(t / bar + 1e-6)
SEC = [(0, 'tension'), (TR[0], 'build'), (TR[1], 'drop'), (TR[2], 'groove'), (TR[3], 'lift'), (TR[4], 'cta')]
def section(t):
    s = 'tension'
    for a, name in SEC:
        if t >= round(a / bar) * bar - 1e-6: s = name                                   # cambia en el compás más cercano a la transición
    return s
Am = (45, [57, 60, 64]); F = (41, [57, 60, 65]); C_ = (48, [55, 60, 64]); G = (43, [55, 59, 62]); E = (40, [56, 59, 64])
PROB, SOL = [Am, F, Am, E], [F, G, Am, C_]                                              # problema (menor, tenso) y solución (pop luminoso)
def chord(b):
    s = section(b * bar + .01); return (PROB if s in ('tension', 'build') else SOL)[b % 4]
L = {k: np.zeros(N) for k in ('kick', 'clap', 'hat', 'ohat', 'bass', 'stab', 'pad', 'arp', 'fx')}
nk = int(.42 * SR); kt = np.arange(nk) / SR
KICK = np.tanh(2.2 * np.sin(2 * np.pi * np.cumsum(48 + 110 * np.exp(-kt / .03)) / SR) * np.exp(-kt / .2)) + band(rng.standard_normal(nk), 2000, 8000) * np.exp(-kt / .004) * .3
nc = int(.4 * SR); ct = np.arange(nc) / SR
CLAP = band(rng.standard_normal(nc), 900, 8000) * sum((ct >= d) * np.exp(-np.clip(ct - d, 0, None) / .025) for d in (0, .011, .022, .034)) * .6
nh = int(.05 * SR); HAT = band(rng.standard_normal(nh), 7500, 16000) * np.exp(-np.arange(nh) / SR / .012) * .3
no = int(.3 * SR); OHAT = band(rng.standard_normal(no), 6500, 15000) * np.exp(-np.arange(no) / SR / .09) * .22
kicks = []
for k in range(int(DUR / beat) + 1):
    tb = k * beat; s = section(tb + .01); q = k % 4
    if tb >= DUR: break
    if s == 'tension':
        add(L['kick'], tb, KICK, 1 if q in (0, 2) else .75); kicks.append(tb)
        if q in (1, 3): add(L['clap'], tb, CLAP, .8)
        add(L['hat'], tb + beat / 2, HAT, .7)
    elif s == 'build':
        add(L['kick'], tb, KICK, .95); kicks.append(tb)
        if q in (1, 3): add(L['clap'], tb, CLAP, .85)
        for h in range(4 if tb > TR[1] - 2 * bar else 2): add(L['hat'], tb + h * beat / (4 if tb > TR[1] - 2 * bar else 2), HAT, .5 + .3 * (h % 2))
    else:
        light = s == 'groove'
        add(L['kick'], tb, KICK, .85 if light else 1); kicks.append(tb)
        if q in (1, 3): add(L['clap'], tb, CLAP, .7 if light else .9)
        add(L['ohat'], tb + beat / 2, OHAT, .55 if light else .8)
        if not light or q % 2: add(L['hat'], tb + beat / 4, HAT, .35); add(L['hat'], tb + 3 * beat / 4, HAT, .35)
for b in range(BARS):
    t0 = b * bar; s = section(t0 + .01); r, tr = chord(b)
    for k in range(4):                                                                  # bajo en contratiempo (bombea con el bombo)
        tq = t0 + (k + .5) * beat; n = int(beat * .45 * SR)
        x = (saw(note(r), n) * .5 + np.sin(2 * np.pi * note(r - 12) * np.arange(n) / SR)) * env_ad(n, .004, .12)
        add(L['bass'], tq, x, .9 if s != 'tension' else .75)
    if s in ('tension', 'groove'):                                                      # pad suave
        n = int(bar * 1.05 * SR); e = env_ad(n, .3, 2.5)
        for m in tr:
            for d in (-.07, .07): add(L['pad'], t0, saw(note(m) * 2 ** (d / 12), n, rng.random()) * e, .05)
    if s in ('drop', 'lift', 'cta', 'build'):                                           # stabs de acorde en contratiempo
        for k in range(4):
            if s == 'build' and k % 2 == 0: continue
            n = int(.18 * SR); e = env_ad(n, .003, .07)
            for m in tr: add(L['stab'], t0 + (k + .5) * beat, (saw(note(m + 12), n) + saw(note(m + 12) * 1.004, n, .3)) * e, .09)
    if s in ('lift', 'cta'):                                                            # arpegio brillante
        tones = [m + 12 for m in tr] + [tr[0] + 24]
        for q in range(16):
            tq = t0 + q * bar / 16; n = int(.16 * SR); f = note(tones[[0, 1, 2, 3, 2, 1, 2, 3][q % 8]])
            add(L['arp'], tq, np.sin(2 * np.pi * f * np.arange(n) / SR) * env_ad(n, .002, .05), .14)
add(L['fx'], TR[1] - 2 * bar, riser(2 * bar - .05, 250, 7000), .9)                      # subida hacia el «drop» de Atlas Path
add(L['fx'], END - bar, riser(bar - .05, 300, 6000), .6)                                # subida al final: empalma con el inicio del loop
pump = np.ones(N)
for kb in kicks:
    i = int(kb * SR); n = min(N - i, int(.28 * SR))
    if n > 0: pump[i:i + n] = np.minimum(pump[i:i + n], 1 - .55 * np.exp(-np.arange(n) / SR / .08))
mus = (soft(L['kick'], 25, 9000) * .9 + soft(L['clap'], 300, 10000) * .5 + L['hat'] * .5 + L['ohat'] * .45 + soft(L['bass'], 30, 1200) * .7 * pump
       + soft(L['pad'], 120, 3500) * pump + soft(L['stab'], 150, 4500) * pump + soft(L['arp'], 300, 8000) * pump + L['fx'] * .5)
mus = mus + reverb(soft(L['stab'] + L['arp'] + L['clap'] * .5, 200, 8000), 1.5, 3.2) * .5
mus *= np.clip(T / .05, 0, 1) * np.clip((DUR - T) / .05, 0, 1)
mus = to_lufs(mus, -30.0)
mus_d = mus * (1 - .25 * np.clip(vact * 3, 0, 1))                                       # se agacha bajo la voz

# ---------------- EFECTOS ----------------
def sine(f, n): return np.sin(2 * np.pi * f * np.arange(n) / SR)
def notif(p):  # notificación genérica: dos tonos cortos que suben (no es el sonido de ninguna app)
    out = np.zeros(int(.5 * SR))
    for k, m in enumerate((88, 95)):
        n = int(.2 * SR); x = (sine(note(m + 5) * p, n) + .25 * sine(note(m + 5) * p * 2, n)) * env_ad(n, .003, .06); add(out, k * .085, x, .22)
    return out
def tick(p): n = int(.03 * SR); return sine(2200 * p, n) * env_ad(n, .001, .006) * .5
def blipdown(p): n = int(.18 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(900 * p * np.exp(-t / .08)) / SR) * env_ad(n, .002, .06) * .4
def error(p): n = int(.16 * SR); return band((saw(160 * p, n) + saw(167 * p, n)) * .5, 80, 3000) * env_ad(n, .003, .07) * .45
def fail(p):  # caída: tono que baja con un poco de ruido
    n = int(.7 * SR); t = np.arange(n) / SR; x = np.sin(2 * np.pi * np.cumsum(520 * np.exp(-t / .35) + 90) / SR) * np.exp(-t / .3) * .4
    return x + band(rng.standard_normal(n), 300, 2500) * np.exp(-t / .1) * .15
def thud(p): n = int(.4 * SR); t = np.arange(n) / SR; return np.tanh(np.sin(2 * np.pi * np.cumsum(55 + 70 * np.exp(-t / .03)) / SR) * np.exp(-t / .12) * 1.6) * .6
def whoosh(p):
    n = int(.42 * SR); t = np.arange(n) / SR; x = rng.standard_normal(n); m = t / t[-1]
    s = band(x, 700 * p, 2200 * p) * (1 - m) * .6 + band(x, 2200 * p, 8000 * p) * m * .8
    return s * np.sin(np.pi * np.clip(t / .4, 0, 1)) ** 2 * 1.1
def swoosh(p): x = whoosh(p * 1.3); return x[: int(.3 * SR)] * np.linspace(1, 0, int(.3 * SR)) ** .5
def flash(p):
    n = int(.6 * SR); out = np.zeros(n)
    for k, m in enumerate((96, 100, 103)): add(out, k * .03, sine(note(m), int(.4 * SR)) * env_ad(int(.4 * SR), .002, .12), .12)
    return out + band(rng.standard_normal(n), 5000, 14000) * np.exp(-np.arange(n) / SR / .1) * .2
def pop(p): n = int(.08 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum((1100 + 900 * np.exp(-t / .012)) * p) / SR) * env_ad(n, .001, .025) * .6   # agudo y corto: fuera de la banda de la voz
def rise(p): return riser(1.6, 300, 6000) * .8
def poof(p): n = int(.35 * SR); t = np.arange(n) / SR; return band(rng.standard_normal(n), 400, 5000) * np.exp(-t / .07) * .8 + thud(1)[:n] * .4
def chime(p):
    out = np.zeros(int(1.2 * SR))
    for k, m in enumerate((84, 88, 91)):
        n = int(1.0 * SR); add(out, k * .06, (sine(note(m) * p, n) + .35 * sine(note(m) * p * 2, n) * np.exp(-np.arange(n) / SR / .2)) * env_ad(n, .002, .35), .25)
    return out
def impact(p):
    n = int(1.6 * SR); t = np.arange(n) / SR
    x = np.tanh((np.sin(2 * np.pi * np.cumsum(38 * p + 80 * np.exp(-t / .07)) / SR) * np.exp(-t / .5) * 1.3 + band(rng.standard_normal(n), 900, 9000) * np.exp(-t / .03) * .6) * 1.2)
    return x * .8 + reverb(x, 1.2, 3)[:n] * .4
def hit(p): return impact(p * 1.1)[: int(1.0 * SR)] * .8
def shine(p):
    out = np.zeros(int(1.0 * SR))
    for k, m in enumerate((91, 95, 98, 103)): add(out, k * .05, sine(note(m) * p, int(.5 * SR)) * env_ad(int(.5 * SR), .002, .14), .18)
    return out
def ding(p): n = int(1.1 * SR); t = np.arange(n) / SR; f = 1568 * p; return (np.sin(2 * np.pi * f * t) + .4 * np.sin(2 * np.pi * f * 2.7 * t) * np.exp(-t / .1)) * np.exp(-t / .4) * .35
def msgin(p): n = int(.1 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(600 + 500 * np.exp(-t / .015)) / SR) * env_ad(n, .002, .03) * .55
def msgout(p): n = int(.1 * SR); t = np.arange(n) / SR; return np.sin(2 * np.pi * np.cumsum(900 + 700 * np.exp(-t / .015)) / SR) * env_ad(n, .002, .03) * .5
def typing(p):
    out = np.zeros(int(.4 * SR))
    for k in range(5): add(out, k * .07 + rng.uniform(0, .02), band(rng.standard_normal(int(.03 * SR)), 1500, 7000) * np.exp(-np.arange(int(.03 * SR)) / SR / .006), .35)
    return out
def data(p):
    out = np.zeros(int(.5 * SR))
    for k in range(6): add(out, k * .06, sine(note(84 + (k * 5) % 12) * p, int(.05 * SR)) * env_ad(int(.05 * SR), .001, .015), .2)
    return out
def success(p):  # éxito: dos notas que suben y un brillo
    out = np.zeros(int(1.0 * SR))
    for k, m in enumerate((91, 98)):
        n = int(.5 * SR); add(out, k * .08, (sine(note(m) * p, n) + .2 * sine(note(m) * p * 2, n)) * env_ad(n, .002, .18), .25)
    return out
def click(p):
    n = int(.08 * SR); x = band(rng.standard_normal(n), 2000, 9000); e = np.zeros(n); e[:int(.006 * SR)] = 1; e[int(.04 * SR):int(.045 * SR)] = .5; return x * e
def scratch(p): n = int(.35 * SR); t = np.arange(n) / SR; return band(rng.standard_normal(n), 900, 6000) * (.6 + .4 * np.sin(2 * np.pi * 45 * t)) * np.sin(np.pi * t / t[-1]) * .55
def stamp(p): n = int(.5 * SR); x = thud(1)[:n] * 1.1; x[:int(.05 * SR)] += band(rng.standard_normal(int(.05 * SR)), 600, 4000) * .5; return x
def cash(p):  # brillo de monedas (diseño propio, sin muestras)
    out = np.zeros(int(1.0 * SR))
    for k in range(9):
        f = 2600 + rng.uniform(-300, 900); n = int(.25 * SR); add(out, k * .045 + rng.uniform(0, .02), (sine(f, n) + .5 * sine(f * 1.51, n)) * env_ad(n, .001, .05), .14)
    return out + chime(1.2)[: len(out)] * .6
def sparkle(p):
    out = np.zeros(int(1.0 * SR))
    for k in range(10): add(out, k * .05 + rng.uniform(0, .02), sine(note(96 + int(rng.integers(0, 10))), int(.2 * SR)) * env_ad(int(.2 * SR), .001, .05), .1)
    return out
def tap(p): n = int(.06 * SR); return band(rng.standard_normal(n), 800, 5000) * np.exp(-np.arange(n) / SR / .008) * .6 + sine(700, n) * np.exp(-np.arange(n) / SR / .015) * .3
GEN = dict(hit=hit, notif=notif, tick=tick, blipdown=blipdown, error=error, fail=fail, thud=thud, whoosh=whoosh, flash=flash, pop=pop,
           riser=rise, poof=poof, swoosh=swoosh, chime=chime, impact=impact, shine=shine, ding=ding, msgin=msgin, msgout=msgout,
           typing=typing, data=data, success=success, click=click, scratch=scratch, stamp=stamp, cash=cash, sparkle=sparkle, tap=tap)
# los efectos graves o medios van más bajos: acompañan, no tapan la voz
TYPE_GAIN = {'thud': .45, 'fail': .55, 'error': .6, 'whoosh': .65, 'swoosh': .75, 'impact': .8, 'stamp': .8, 'pop': .6, 'notif': .6, 'tick': .7, 'flash': .7}
fx = np.zeros(N)
for e in TL['sfx']:
    add(fx, e['t'], GEN[e['type']](e['pitch']), e['v'] * TYPE_GAIN.get(e['type'], 1))
fx *= np.clip((DUR - T) / .05, 0, 1)
fx *= 1 - .35 * np.clip(vact * 3, 0, 1)                                                 # los efectos también se agachan mientras ella habla
fx = to_lufs(fx, -27.5)

# ---------------- MEZCLAS ----------------
full = np.tanh(voice + mus_d + fx); nomus = np.tanh(voice + fx)
save(OUT + '/voz.wav', voice); save(OUT + '/musica-sola.wav', mus); save(OUT + '/efectos-solos.wav', fx)
save(OUT + '/mezcla-final.wav', full); save(OUT + '/mezcla-sin-musica.wav', nomus)
# claridad: cuánto queda la voz por encima del fondo (música + efectos) en la banda de la palabra, en ventanas de 0.25 s con voz
v = band(voice, 300, 4000); bg = band(mus_d + fx, 300, 4000); w = int(.25 * SR); rs = []
for i in range(0, N - w, w):
    vv = v[i:i + w]
    if np.sqrt((vv ** 2).mean()) < .02: continue
    rs.append(20 * np.log10(np.sqrt((vv ** 2).mean()) / (np.sqrt((bg[i:i + w] ** 2).mean()) + 1e-9)))
rs = np.array(rs)
print(f'{DUR:.3f} s · BPM {BPM:.2f} · compases {BARS} · voz sobre fondo: mediana {np.median(rs):.1f} dB, p5 {np.percentile(rs, 5):.1f}, mín {rs.min():.1f}')
