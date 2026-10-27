"""Banda sonora completa (60 s, 48 kHz, estéreo): música ambiental cinematográfica sintetizada, efectos
discretos sincronizados con la imagen y la narración procesada; mezcla con ducking y normalización.

Uso: python audio.py <dir_narracion_raw> <dir_salida>
Salidas: music.wav, sfx.wav, narration.wav, mix.wav (24 bit) y mix_report.json
"""
import json
import os
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.timeline import NARRATION  # noqa: E402

SR = 48000
DUR = 60.0
N = int(SR * DUR)
RNG = np.random.default_rng(7)


def midi(n):
    return 440.0 * 2 ** ((n - 69) / 12)


def t_axis(n):
    return np.arange(n) / SR


def env_adsr(n, a, d, s, r, total=None):
    """Envolvente ADSR en muestras (a,d,r en s; s nivel). total: duración de la nota (s)."""
    total = total if total is not None else n / SR
    t = t_axis(n)
    e = np.where(t < a, t / max(a, 1e-4), 1.0)
    e = np.where((t >= a) & (t < a + d), 1 - (1 - s) * (t - a) / max(d, 1e-4), e)
    e = np.where(t >= a + d, s, e)
    rel = np.clip((t - (total - r)) / max(r, 1e-4), 0, 1)
    return e * (1 - rel) ** 2


def polyblep_saw(freq, n, phase0=0.0):
    t = t_axis(n)
    dt = freq / SR
    ph = (phase0 + freq * t) % 1.0
    y = 2 * ph - 1
    m1 = ph < dt
    x = ph[m1] / dt
    y[m1] -= x + x - x * x - 1
    m2 = ph > 1 - dt
    x = (ph[m2] - 1) / dt
    y[m2] -= x * x + x + x + 1
    return y


def lowpass(x, fc, q=0.707):
    b, a = ss.iirfilter(2, min(fc, SR * 0.45) / (SR / 2), btype="low", ftype="butter")
    return ss.lfilter(b, a, x)


def highpass(x, fc):
    b, a = ss.butter(2, fc / (SR / 2), btype="high")
    return ss.lfilter(b, a, x)


def bandpass(x, f1, f2):
    b, a = ss.butter(2, [f1 / (SR / 2), min(f2, SR * 0.45) / (SR / 2)], btype="band")
    return ss.lfilter(b, a, x)


def sweep_lowpass(x, fc_curve, block=512):
    """Filtro paso bajo variable (cutoff por bloque) con estado continuo."""
    y = np.zeros_like(x)
    zi = None
    for i in range(0, len(x), block):
        fc = float(np.clip(fc_curve[min(i, len(fc_curve) - 1)], 40, SR * 0.45))
        sos = ss.butter(2, fc / (SR / 2), btype="low", output="sos")
        if zi is None:
            zi = ss.sosfilt_zi(sos) * 0.0
        y[i:i + block], zi = ss.sosfilt(sos, x[i:i + block], zi=zi)
    return y


def reverb_ir(seconds=2.8, tau=0.9, damp=4500, seed=0):
    rng = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = t_axis(n)
    ir = []
    for ch in range(2):
        noise = rng.normal(0, 1, n)
        noise = lowpass(noise, damp) * 0.7 + noise * 0.3
        e = np.exp(-t / tau) * (1 - np.exp(-t / 0.012))
        ir.append(noise * e)
    ir = np.array(ir)
    ir /= np.sqrt((ir ** 2).sum(axis=1, keepdims=True))
    return ir


IR_BIG = reverb_ir(3.2, 1.05, 5000, 1)
IR_ROOM = reverb_ir(0.8, 0.18, 7000, 2)


def reverb(stereo, ir, wet):
    out = np.zeros_like(stereo)
    for ch in range(2):
        src = stereo[ch] if stereo.ndim == 2 else stereo
        out[ch] = ss.fftconvolve(src, ir[ch])[: stereo.shape[-1]]
    return stereo * (1 - wet) + out * wet * 1.8


def place(buf, sig, t0, gain=1.0, pan=0.0):
    """Suma una señal (mono o estéreo) en el buffer estéreo a partir de t0 (s)."""
    i0 = int(round(t0 * SR))
    if sig.ndim == 1:
        l, r = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
        sig = np.vstack([sig * l * 1.414, sig * r * 1.414])
    n = min(sig.shape[1], buf.shape[1] - i0)
    if n <= 0:
        return
    buf[:, i0:i0 + n] += sig[:, :n] * gain


# ----------------------------------------------------------------------------- music

CHORDS = {  # bajo, voces
    "Dm9": (38, [50, 57, 60, 64, 65]), "Bbmaj7": (46, [58, 62, 65, 69]), "Bbmaj9": (46, [58, 62, 65, 69, 72]),
    "Asus4": (45, [57, 62, 64, 69]), "A": (45, [57, 61, 64, 69]), "C6": (48, [60, 64, 67, 69]),
    "Fmaj7/A": (45, [53, 60, 64, 69]), "Gm9": (43, [58, 62, 65, 69]), "Fmaj9": (41, [57, 60, 64, 67]),
    "C/E": (40, [60, 64, 67, 72]), "C": (48, [64, 67, 72]), "Csus4": (48, [65, 67, 72]),
    "Fadd9": (41, [53, 57, 60, 67]),
}
PROG = [(0, 4, "Dm9"), (4, 6, "Bbmaj7"), (6, 8, "Asus4"),
        (8, 12, "Dm9"), (12, 14, "Bbmaj9"), (14, 16, "C6"),
        (16, 20, "Dm9"), (20, 24, "Bbmaj9"), (24, 26, "Fmaj7/A"), (26, 28, "Gm9"), (28, 29, "Asus4"), (29, 30, "A"),
        (30, 34, "Fmaj9"), (34, 36, "C/E"), (36, 38, "Dm9"), (38, 40, "Bbmaj7"),
        (40, 44, "Fmaj9"), (44, 46, "C"), (46, 48, "Dm9"), (48, 50, "Bbmaj9"),
        (50, 54, "Fmaj9"), (54, 56, "Bbmaj7"), (56, 57, "Csus4"), (57, 60, "Fadd9")]


def section_level(t):
    """Intensidad musical por escena (0..1)."""
    pts = [(0, 0.45), (7.5, 0.6), (8, 0.55), (15.5, 0.7), (16, 0.75), (24, 0.85), (29.5, 0.95), (30, 0.7),
           (39.5, 0.8), (40, 0.8), (49.5, 0.9), (50, 0.85), (57, 0.75), (60, 0.0)]
    return np.interp(t, [p[0] for p in pts], [p[1] for p in pts])


def pad_bus():
    out = np.zeros((2, N))
    for (t0, t1, name) in PROG:
        bass, notes = CHORDS[name]
        dur = (t1 - t0) + 1.6                    # solapamiento con la cola siguiente
        n = int(dur * SR)
        e = env_adsr(n, 0.9, 0.5, 0.85, 1.6, dur)
        for k, m in enumerate(notes):
            f = midi(m)
            st = []
            for ch, det in enumerate((-0.07, 0.07)):
                v = 0.0
                for d2 in (-1, 0, 1):
                    v = v + polyblep_saw(f * 2 ** ((det + d2 * 0.05) / 12), n, RNG.uniform())
                st.append((v / 3) * e * 0.06)
            place(out, np.vstack(st), t0, 1.0)
        # sub-bajo (seno) y bajo suave
        sb = np.sin(2 * np.pi * midi(bass - 12) * t_axis(n)) * 0.22 + np.sin(2 * np.pi * midi(bass) * t_axis(n)) * 0.06
        place(out, sb * env_adsr(n, 0.6, 0.4, 0.9, 1.4, dur), t0, 1.0)
    t = t_axis(N)
    fc = 500 + 2600 * section_level(t) ** 1.6 + 400 * np.sin(2 * np.pi * t / 7.0)
    for ch in range(2):
        out[ch] = sweep_lowpass(out[ch], fc)
    return reverb(out, IR_BIG, 0.45)


def arp_bus():
    out = np.zeros((2, N))
    step = 0.25                                   # semicorcheas a 120 BPM
    pattern = [0, 2, 1, 3, 2, 4, 3, 1]
    t = 8.0
    i = 0
    while t < 58.0:
        name = [p for p in PROG if p[0] <= t < p[1]][0][2]
        _, notes = CHORDS[name]
        nn = sorted(notes)
        note = nn[pattern[i % len(pattern)] % len(nn)] + 12
        lvl = section_level(t)
        dens = 1.0 if (16 <= t < 30 or 40 <= t < 50) else (0.55 if t < 16 else 0.75)
        if RNG.uniform() < dens:
            dur = 0.9
            n = int(dur * SR)
            tt = t_axis(n)
            f = midi(note)
            mod = np.sin(2 * np.pi * f * 2.0 * tt) * np.exp(-tt * 9) * 2.2
            pl = np.sin(2 * np.pi * f * tt + mod) * np.exp(-tt * 5.5)
            pl += 0.3 * np.sin(2 * np.pi * f * 2 * tt) * np.exp(-tt * 8)
            pan = 0.35 * np.sin(i * 0.9)
            accent = 1.0 if i % 4 == 0 else 0.72
            place(out, pl * 0.05 * lvl * accent, t, 1.0, pan)
        t += step
        i += 1
    # delay ping-pong (3/8) + reverb
    d = int(0.75 * SR)
    dl = np.zeros_like(out)
    fb = 0.38
    for k in range(1, 6):
        g = fb ** k
        src = out[(k + 1) % 2]
        dl[k % 2, k * d:] += src[:-k * d] * g
    out = out + lowpass(dl, 3500) * 0.8
    return reverb(out, IR_BIG, 0.35)


def shimmer_bus():
    out = np.zeros((2, N))
    t = t_axis(N)
    lvl = section_level(t)
    for k, m in enumerate([81, 84, 88, 91, 93]):
        am = 0.5 + 0.5 * np.sin(2 * np.pi * (0.05 + 0.03 * k) * t + k)
        sig = np.sin(2 * np.pi * midi(m) * t + 0.3 * np.sin(2 * np.pi * 0.2 * t)) * am * 0.006 * lvl
        out[k % 2] += sig
    return reverb(out, IR_BIG, 0.6)


def kick(n_s=0.5, f0=110, f1=42):
    n = int(n_s * SR)
    tt = t_axis(n)
    f = f1 + (f0 - f1) * np.exp(-tt * 28)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-tt * 7)


def perc_bus():
    out = np.zeros((2, N))
    # pulso muy suave tipo latido en la escena 1 (desaparece)
    for b in np.arange(0.5, 7.6, 1.0):
        place(out, kick(0.4, 80, 38) * 0.10 * (1 - b / 9), b)
        place(out, kick(0.35, 70, 36) * 0.06 * (1 - b / 9), b + 0.28)
    # pulso discreto en escenas 3, 4 y 5 (negras a 120 BPM, acentos en 1 y 3)
    for b in np.arange(16.0, 50.0, 0.5):
        beat = int(round(b * 2)) % 4
        if beat in (0, 2):
            g = 0.10 if beat == 0 else 0.07
            if 30.0 <= b < 31.0 or 40.0 <= b < 40.5:
                continue
            place(out, kick() * g * section_level(b), b)
        else:
            hat = highpass(RNG.normal(0, 1, int(0.06 * SR)), 7000) * np.exp(-np.arange(int(0.06 * SR)) / SR * 70)
            place(out, hat * 0.012 * section_level(b), b, 1.0, 0.3)
    return reverb(out, IR_ROOM, 0.2)


def riser(dur=1.6, f0=300, f1=5000):
    n = int(dur * SR)
    tt = t_axis(n)
    noise = RNG.normal(0, 1, n)
    fc = f0 * (f1 / f0) ** (tt / dur)
    y = sweep_lowpass(noise, fc, 256)
    return y * (tt / dur) ** 2.2 * np.exp(-np.clip(tt - dur * 0.97, 0, None) * 60)


def music():
    m = pad_bus() + arp_bus() + shimmer_bus() + perc_bus()
    for t1 in (8.0, 16.0, 30.0, 40.0, 50.0):
        place(m, riser(1.4), t1 - 1.4, 0.05)
    # acorde final de marca (campana suave) al aparecer el logo
    n = int(4.5 * SR)
    tt = t_axis(n)
    bell = sum(np.sin(2 * np.pi * midi(x) * tt + 1.5 * np.sin(2 * np.pi * midi(x) * 3.5 * tt) * np.exp(-tt * 3))
               * np.exp(-tt * 1.1) for x in (65, 69, 72, 77))
    place(m, reverb(np.vstack([bell, bell]) * 0.03, IR_BIG, 0.5), 50.9)
    # fundido final
    t = t_axis(N)
    m *= np.clip((60.0 - t) / 2.2, 0, 1) ** 1.5
    return m


# ----------------------------------------------------------------------------- sfx


def whoosh(dur=0.9, f0=400, f1=2600, peak=0.55):
    n = int(dur * SR)
    tt = t_axis(n)
    noise = RNG.normal(0, 1, n)
    x = tt / dur
    fc = f0 + (f1 - f0) * np.sin(np.pi * np.clip(x, 0, 1))
    y = sweep_lowpass(noise, fc, 256)
    e = np.where(x < peak, (x / peak) ** 2, np.exp(-(x - peak) * 7))
    return y * e


def blip(f=1800, dur=0.12):
    n = int(dur * SR)
    tt = t_axis(n)
    return (np.sin(2 * np.pi * f * tt) * 0.6 + np.sin(2 * np.pi * f * 1.5 * tt) * 0.25) * np.exp(-tt * 38)


def scan_sweep(dur=1.8):
    n = int(dur * SR)
    tt = t_axis(n)
    f = 900 + 1400 * tt / dur
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3 + bandpass(RNG.normal(0, 1, n), 2500, 6000) * 0.25
    trem = 0.6 + 0.4 * np.sin(2 * np.pi * 18 * tt)
    return s * trem * np.sin(np.pi * tt / dur) ** 1.5


def bubbles(dur, rate=60.0, seed=0, f_lo=900, f_hi=4200):
    """Burbujeo: microburbujas como chirps resonantes cortos con temporización aleatoria."""
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    out = np.zeros(n)
    k = int(rate * dur)
    for t0 in np.sort(rng.uniform(0, dur, k)):
        f = rng.uniform(f_lo, f_hi)
        L = int(0.03 * SR)
        tt = t_axis(L)
        ch = np.sin(2 * np.pi * (f * tt + 3000 * tt * tt)) * np.exp(-tt * 140)
        i = int(t0 * SR)
        m = min(L, n - i)
        out[i:i + m] += ch[:m] * rng.uniform(0.3, 1.0)
    return out


def flow_rumble(dur, seed=0):
    rng = np.random.default_rng(seed)
    n = int(dur * SR)
    b = np.cumsum(rng.normal(0, 1, n))
    b = highpass(b - np.convolve(b, np.ones(4800) / 4800, "same"), 30)
    b = lowpass(b, 380)
    b /= np.abs(b).max() + 1e-9
    tt = t_axis(n)
    return b * (0.7 + 0.3 * np.sin(2 * np.pi * 1.1 * tt)) * np.sin(np.pi * tt / dur) ** 0.4


def ticks(t0, t1, every=0.5):
    out = []
    t = t0
    while t < t1:
        out.append(t)
        t += every
    return out


def sfx():
    s = np.zeros((2, N))
    # escena 1: escáner, inmersión en la vena, flujo
    place(s, scan_sweep(1.9), 0.85, 0.10)
    place(s, whoosh(1.0, 300, 3000, 0.75), 3.55, 0.20)
    place(s, kick(0.6, 90, 35), 4.32, 0.18)
    place(s, flow_rumble(4.0, 1), 4.2, 0.20)
    # transiciones
    for t in (7.65, 15.65, 25.0, 29.6, 39.6, 49.6):
        place(s, whoosh(0.8, 500, 2400), t, 0.09, RNG.uniform(-0.3, 0.3))
    # escena 2: sonda, pulsos ecográficos, punción, flashback
    place(s, blip(1200, 0.18), 9.15, 0.12)
    for t in ticks(9.6, 15.6, 0.455):
        place(s, blip(3200, 0.05), t, 0.025, 0.2)
    place(s, whoosh(0.35, 1500, 5000, 0.6), 10.80, 0.07)   # la punta atraviesa la piel (11.0 s)
    place(s, blip(700, 0.08), 11.70, 0.08)                  # entra en la luz venosa
    place(s, blip(500, 0.1), 12.60, 0.06)                   # reflujo de sangre al cono (flashback)
    # escena 3A: burbujeo de la microespuma
    bb = bubbles(5.6, 70, 3)
    place(s, bb * np.linspace(0.2, 1, len(bb)) * np.minimum(1, np.linspace(6, 0, len(bb))), 15.2, 0.035, -0.2)
    bb2 = bubbles(5.0, 45, 4, 600, 2500)
    place(s, bb2, 16.0, 0.03, 0.25)
    # escena 3B: textura delicada; 3C: paso del tiempo
    for t in ticks(25.4, 29.4, 0.5):
        place(s, blip(2600, 0.04), t, 0.03, 0.1)
    # escena 4: flujo
    place(s, flow_rumble(8.0, 5), 31.5, 0.10)
    place(s, blip(1500, 0.14), 36.2, 0.08, -0.3)
    place(s, blip(1900, 0.14), 36.6, 0.08, 0.3)
    # escena 5: tres beneficios + pasos suaves
    for t in (40.5, 43.6, 46.8):
        place(s, blip(1700, 0.16), t, 0.09)
    for i, t in enumerate(np.arange(47.45, 49.3, 0.42)):
        place(s, kick(0.12, 220, 120) * 0.5 + bandpass(RNG.normal(0, 1, int(0.12 * SR)), 300, 2500)
              * np.exp(-np.arange(int(0.12 * SR)) / SR * 40) * 0.2, t, 0.06, -0.2 if i % 2 else 0.2)
    # escena 6: logo, sedes y llamada a la acción
    place(s, whoosh(1.2, 800, 7000, 0.8), 50.0, 0.06)
    place(s, blip(2200, 0.2), 53.1, 0.05)
    place(s, blip(1600, 0.2), 56.35, 0.08)
    return reverb(s, IR_ROOM, 0.18)


# ----------------------------------------------------------------------------- narración


def narration(raw_dir):
    out = np.zeros((2, N))
    env = np.zeros(N)
    timeline = json.load(open(os.path.join(raw_dir, "timeline.json"), encoding="utf-8"))
    for key, t0 in NARRATION:
        x, sr = sf.read(os.path.join(raw_dir, f"{key}.wav"), dtype="float64")
        if x.ndim > 1:
            x = x.mean(axis=1)
        x = ss.resample_poly(x, SR, sr)
        # cadena de voz: HPF, calidez, presencia, des-esser suave, compresión
        x = highpass(x, 75)
        x = x + 0.22 * bandpass(x, 140, 320)
        x = x + 0.28 * bandpass(x, 2800, 5200)
        sib = bandpass(x, 6500, 11000)
        x = x - 0.35 * sib
        e = np.sqrt(np.convolve(x ** 2, np.ones(480) / 480, "same")) + 1e-6
        thr = np.percentile(e, 70)
        gain = np.where(e > thr, (thr / e) ** (1 - 1 / 3.0), 1.0)
        gain = np.convolve(gain, np.ones(240) / 240, "same")
        x = x * gain
        x = x / (np.abs(x).max() + 1e-9) * 0.9
        place(out, x, t0, 1.0)
        i0 = int(t0 * SR)
        env[i0:i0 + len(x)] = np.maximum(env[i0:i0 + len(x)], 1.0)
        assert t0 + len(x) / SR <= 60.0, key
    out = reverb(out, IR_ROOM, 0.06)
    return out, env, timeline


def limiter(x, ceiling_db=-1.5, look=0.005, release=0.08):
    """Limitador de picos con anticipación: la ganancia baja antes del pico y se recupera suavemente.
    Detección sobre señal sobremuestreada x4 (aproxima picos reales entre muestras)."""
    c = 10 ** (ceiling_db / 20)
    up = ss.resample_poly(x, 4, 1, axis=1)
    det = np.abs(up).max(axis=0).reshape(-1, 4).max(axis=1)[: x.shape[1]]
    L = int(look * SR)
    # máximo en ventana deslizante hacia delante (look-ahead)
    from scipy.ndimage import maximum_filter1d
    env = maximum_filter1d(det, size=2 * L + 1, origin=0)
    need = np.minimum(1.0, c / np.maximum(env, 1e-9))
    # suavizado: ataque inmediato (ya anticipado) y liberación exponencial
    rel = np.exp(-1.0 / (release * SR))
    gsm = np.empty_like(need)
    acc = 1.0
    for i in range(0, len(need), 32):
        blk = need[i:i + 32].min()
        acc = blk if blk < acc else acc * rel ** 32 + (1 - rel ** 32) * blk
        gsm[i:i + 32] = acc
    gsm = np.convolve(gsm, np.ones(2 * L + 1) / (2 * L + 1), "same")
    gsm = np.minimum(gsm, need)
    return x * gsm[None, :]


def lufs(x):
    import pyloudnorm as pyln
    meter = pyln.Meter(SR)
    return meter.integrated_loudness(x.T)


def main(raw_dir, out_dir):
    os.makedirs(out_dir, exist_ok=True)
    mus = music()
    fx = sfx()
    nar, env, timeline = narration(raw_dir)
    # ducking de la música bajo la voz (ataque 80 ms, liberación 450 ms)
    a = np.convolve(env, np.ones(int(0.08 * SR)) / int(0.08 * SR), "same")
    dk = np.zeros_like(a)
    rel = np.exp(-1 / (0.45 * SR))
    acc = 0.0
    for i in range(0, N, 64):
        acc = max(a[i], acc * rel ** 64)
        dk[i:i + 64] = acc
    duck = 1 - 0.55 * dk
    mus_d = mus * duck
    # niveles relativos
    nar_l = lufs(nar)
    mus_l = lufs(mus)
    fx_l = lufs(fx)
    nar_g = 10 ** ((-16.0 - nar_l) / 20)
    mus_g = 10 ** ((-23.5 - mus_l) / 20)
    fx_g = 10 ** ((-30.0 - fx_l) / 20)
    mix = nar * nar_g + mus_d * mus_g + fx * fx_g
    # normalización a -14 LUFS con limitador de picos (look-ahead) y techo de -1.5 dBFS (sobremuestreado x4)
    pre = mix.copy()
    g = 10 ** ((-14.0 - lufs(pre)) / 20)
    for _ in range(4):
        mix = limiter(pre * g, ceiling_db=-1.5)
        err = -14.0 - lufs(mix)
        if abs(err) < 0.05:
            break
        g *= 10 ** (err / 20)
    final_l = lufs(mix)
    for name, sig in (("music", mus_d * mus_g * g), ("sfx", fx * fx_g * g), ("narration", nar * nar_g * g),
                      ("mix", mix)):
        # (las pistas sueltas no llevan el limitador; sirven como stems de edición)
        sf.write(os.path.join(out_dir, f"{name}.wav"), sig.T.astype(np.float32), SR, subtype="PCM_24")
    tp = np.abs(ss.resample_poly(mix, 4, 1, axis=1)).max()
    rep = dict(lufs_integrated=round(final_l, 2), peak_dbfs=round(20 * np.log10(np.abs(mix).max()), 2),
               true_peak_dbtp=round(20 * np.log10(tp), 2),
               duration_s=N / SR, narration_segments=[[k, t] for k, t in NARRATION])
    json.dump(rep, open(os.path.join(out_dir, "mix_report.json"), "w"), indent=2)
    print(rep)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
