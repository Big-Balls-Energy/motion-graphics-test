"""Procedural music + SFX, mixed under the narration with ducking.

usage: python3 build_audio.py BUILD_DIR [STEMS_DIR]
  reads voice.wav, timeline.json, cues.json; writes mix.wav. With STEMS_DIR it also writes
  sfx.wav, musica.wav (not ducked), sfx_musica.wav and voz_guia.wav at the same gain as the
  full mix, so a voice recorded later sits at the right level against them.

Music: 112 BPM lo-fi/electronic groove in D minor; 28 bars = exactly 60 s so the
reel loops seamlessly. Music sits ~15 dB under the voice and ducks a further
~5 dB whenever the voice is talking.
"""
import json, subprocess, sys
from pathlib import Path
import numpy as np

SR = 48000
DUR = 60.0
N = int(DUR * SR)
BPM = 112
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)


def t_(d):
    return np.arange(int(d * SR)) / SR


def midi(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(buf, t0, x, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf):
        return
    if i < 0:
        x, i = x[-i:], 0
    n = min(len(x), len(buf) - i)
    buf[i:i + n] += gain * x[:n]


def onepole_lp(x, fc):
    a = np.exp(-2 * np.pi * fc / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):  # small buffers only
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def biquad_bp(x, fc, q):
    """Constant-gain band-pass (RBJ) applied with scipy-free direct form."""
    w0 = 2 * np.pi * fc / SR
    alpha = np.sin(w0) / (2 * q)
    b0, b1, b2 = alpha, 0.0, -alpha
    a0, a1, a2 = 1 + alpha, -2 * np.cos(w0), 1 - alpha
    b0, b1, b2, a1, a2 = b0 / a0, b1 / a0, b2 / a0, a1 / a0, a2 / a0
    y = np.zeros_like(x)
    x1 = x2 = y1 = y2 = 0.0
    for i, v in enumerate(x):
        o = b0 * v + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
        x2, x1, y2, y1 = x1, v, y1, o
        y[i] = o
    return y


def hp_noise(d, amt=0.85):
    n = rng.standard_normal(int(d * SR))
    return n - amt * np.concatenate([[0], n[:-1]])


# ------------------------------------------------------------------ drums
def kick():
    t = t_(0.42)
    f = 48 + 120 * np.exp(-t * 32)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5)
    click = rng.standard_normal(len(t)) * np.exp(-t * 400) * 0.3
    return np.tanh(1.6 * (body + click))


def snare():
    t = t_(0.35)
    noise = biquad_bp(rng.standard_normal(len(t)), 2200, 0.7) * np.exp(-t * 16)
    body = np.sin(2 * np.pi * 185 * t) * np.exp(-t * 28) * 0.5
    clap = np.zeros(len(t))
    for k, d in enumerate([0, 0.011, 0.022]):
        place(clap, d, biquad_bp(rng.standard_normal(int(0.02 * SR)), 1500, 1.2) * (0.5 + 0.25 * k))
    return 0.8 * noise + body + 0.5 * clap


def hat(open_=False):
    d = 0.25 if open_ else 0.05
    t = t_(d)
    return hp_noise(d, 0.97) * np.exp(-t * (14 if open_ else 70)) * 0.35


# ---------------------------------------------------------------- tonal
def ep_note(f, d, vel=1.0):
    """Soft electric-piano-ish tone."""
    t = t_(d)
    env = (1 - np.exp(-t * 180)) * np.exp(-t * 1.6)
    trem = 1 + 0.08 * np.sin(2 * np.pi * 4.5 * t)
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2 * f * t) * np.exp(-t * 6)
         + 0.08 * np.sin(2 * np.pi * 3.01 * f * t) * np.exp(-t * 12))
    return vel * x * env * trem


def bass_note(f, d):
    t = t_(d)
    env = (1 - np.exp(-t * 300)) * np.exp(-t * 2.2) * np.clip((d - t) / 0.04, 0, 1)
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * 2 * f * t)
    return np.tanh(1.3 * x) * env


def pluck(f, d=0.35):
    t = t_(d)
    return (np.sin(2 * np.pi * f * t) * 0.7 + 0.3 * np.sign(np.sin(2 * np.pi * f * t)) * np.exp(-t * 30)) * np.exp(-t * 11)


CHORDS = [  # (bass midi, voicing) — Dm9, Bbmaj7, Fmaj7, C6/9
    (38, [53, 57, 60, 64]),
    (34, [53, 57, 58, 62]),
    (41, [52, 57, 60, 65]),
    (36, [52, 55, 60, 62]),
]


def build_music(breaks):
    drums = np.zeros(N)
    bass = np.zeros(N)
    keys_l, keys_r = np.zeros(N), np.zeros(N)
    hats_l, hats_r = np.zeros(N), np.zeros(N)
    K, Sn, Hc, Ho = kick(), snare(), hat(), hat(True)
    kick_times = []
    for bar in range(28):
        b0 = bar * BAR
        bass_m, voicing = CHORDS[bar % 4]
        # drums
        for beat in (0, 2):
            kick_times.append(b0 + beat * BEAT)
        if bar % 2 == 1:
            kick_times.append(b0 + 2.5 * BEAT)
        for beat in (1, 3):
            place(drums, b0 + beat * BEAT, Sn, 0.55)
        for e in range(8):
            tt = b0 + e * BEAT / 2 + (0.018 if e % 2 else 0)        # light swing
            h = Ho if (e == 7 and bar % 4 == 3) else Hc
            g = 0.55 if e % 2 else 0.8
            place(hats_l if e % 2 else hats_r, tt, h, g)
            place(hats_r if e % 2 else hats_l, tt, h, g * 0.5)
        # bass: 1, 1.5-and, 2.5, 3.5
        for beat, d in ((0, 1.3), (1.5, 0.45), (2.5, 0.6), (3.5, 0.4)):
            m = bass_m + (12 if beat == 3.5 and bar % 2 else 0)
            place(bass, b0 + beat * BEAT, bass_note(midi(m), d * BEAT), 0.55)
        # keys: chord on 1 and an off-beat stab on 2-and
        for k, m in enumerate(voicing):
            spread = 0.012 * k
            place(keys_l, b0 + spread, ep_note(midi(m), BAR * 0.95), 0.16)
            place(keys_r, b0 + spread + 0.009, ep_note(midi(m) * 1.003, BAR * 0.95), 0.16)
            place(keys_l if k % 2 else keys_r, b0 + 1.5 * BEAT, ep_note(midi(m + 12), BEAT * 0.8), 0.06)
        # sparkly pluck arpeggio on odd bars
        if bar % 2 == 1:
            notes = voicing + [voicing[1] + 12]
            for s16 in range(0, 16, 3):
                place(keys_r if s16 % 2 else keys_l, b0 + s16 * BEAT / 4, pluck(midi(notes[s16 % 5] + 12)), 0.05)
    for kt in kick_times:
        place(drums, kt, K, 0.9)
    # sidechain pump on bass + keys from the kick
    pump = np.ones(N)
    for kt in kick_times:
        i = int(kt * SR)
        seg = t_(BEAT)
        m = 1 - 0.45 * np.exp(-seg * 9)
        n = min(len(seg), N - i)
        pump[i:i + n] = np.minimum(pump[i:i + n], m[:n])
    bass *= pump
    keys_l *= pump; keys_r *= pump
    # drum/bass breaks (pause before "Regala progreso")
    gate = np.ones(N)
    for a, b in breaks:
        ia, ib = int(a * SR), int(b * SR)
        gate[ia:ib] = 0.0
        ramp = int(0.01 * SR)
        gate[ib:ib + ramp] = np.linspace(0, 1, ramp)
    drums *= gate; bass *= gate
    # simple stereo delay on keys for width
    d = int(0.75 * BEAT * SR)
    keys_l[d:] += 0.25 * keys_r[:-d]
    keys_r[d:] += 0.25 * keys_l[:-d]
    vinyl = np.zeros(N)
    for tt in rng.uniform(0, DUR, 220):
        place(vinyl, tt, rng.standard_normal(30) * np.exp(-np.arange(30) / 6), rng.uniform(0.02, 0.06))
    L = drums + bass + keys_l + hats_l + vinyl
    R = drums + bass + keys_r + hats_r + vinyl
    return np.stack([L, R])


# ------------------------------------------------------------------ sfx
def sfx(kind):
    if kind in ('pum', 'thud'):
        t = t_(0.45)
        f = 55 + 150 * np.exp(-t * 28)
        body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)
        slap = biquad_bp(rng.standard_normal(len(t)), 900, 0.8) * np.exp(-t * 45)
        x = np.tanh(2.0 * (body + 0.9 * slap))
        return x * (0.55 if kind == 'thud' else 1.0)
    if kind == 'whoosh':
        d = 0.5
        t = t_(d)
        n = rng.standard_normal(len(t))
        out = np.zeros(len(t))
        seg = int(0.025 * SR)
        for i in range(0, len(t), seg):           # stepped band-pass sweep
            k = i / len(t)
            fc = 350 * (1 - k) + 3200 * k
            chunk = biquad_bp(n[max(0, i - 256):i + seg], fc, 0.9)[-min(seg, len(t) - i):]
            out[i:i + len(chunk)] = chunk
        env = np.sin(np.pi * np.clip(t / d, 0, 1)) ** 2 * np.clip(t / (0.7 * d), 0, 1) ** 0.5
        return out * env * 1.6
    if kind == 'ding':
        out = np.zeros(int(1.2 * SR))
        for f0, delay, g in ((1318.5, 0.0, 1.0), (1975.5, 0.075, 0.7)):
            t = t_(1.2 - delay)
            x = sum(a * np.sin(2 * np.pi * f0 * r * t) * np.exp(-t * dcy)
                    for r, a, dcy in ((1, 1, 4.5), (2.0, 0.35, 7), (3.01, 0.15, 10), (4.2, 0.08, 14)))
            place(out, delay, x * (1 - np.exp(-t * 900)), g)
        return out * 0.45
    if kind == 'pop':
        t = t_(0.09)
        f = 420 + 900 * t / 0.09
        return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 40) * 0.7
    if kind == 'pops':
        out = np.zeros(int(0.7 * SR))
        for k in range(6):
            t = t_(0.06)
            f = 600 + 120 * k + 700 * t / 0.06
            place(out, k * 0.065, np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 55), 0.5)
        return out
    if kind == 'scratch':
        t = t_(0.28)
        n = biquad_bp(rng.standard_normal(len(t)), 3200, 1.5)
        jitter = 0.6 + 0.4 * np.abs(np.sin(2 * np.pi * 38 * t))
        return n * jitter * np.sin(np.pi * t / 0.28) * 1.4
    if kind == 'shine':
        t = t_(0.9)
        x = sum(np.sin(2 * np.pi * f * t + p) * (0.5 + 0.5 * np.sin(2 * np.pi * r * t))
                for f, p, r in ((2637, 0, 11), (3520, 1, 13), (4186, 2, 9), (5274, 3, 15)))
        return x * np.exp(-t * 4) * (1 - np.exp(-t * 60)) * 0.12
    if kind == 'rise':
        t = t_(0.6)
        f = 300 + 900 * (t / 0.6) ** 2
        tone = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.3
        air = biquad_bp(rng.standard_normal(len(t)), 2500, 0.7) * 0.4
        return (tone + air) * (t / 0.6) ** 1.5
    if kind == 'car':
        out = np.zeros(int(0.5 * SR))
        for k in range(2):
            t = t_(0.11)
            x = np.tanh(3 * (np.sin(2 * np.pi * 440 * t) + 0.6 * np.sin(2 * np.pi * 554 * t)))
            place(out, k * 0.17, x * np.clip(t / 0.005, 0, 1) * np.clip((0.11 - t) / 0.01, 0, 1), 0.35)
        return out
    if kind == 'click':
        out = np.zeros(int(0.12 * SR))
        for k, g in ((0, 1.0), (0.055, 0.6)):
            t = t_(0.012)
            x = hp_noise(0.012, 0.95) * np.exp(-t * 900) + 0.6 * np.sin(2 * np.pi * 2600 * t) * np.exp(-t * 600)
            place(out, k, x, g)
        return out * 0.9
    raise ValueError(kind)


# set so each effect sits 3-14 dB under the voice (measured on active RMS)
SFX_GAIN = {'pum': 0.095, 'thud': 0.12, 'whoosh': 0.063, 'ding': 0.165, 'pop': 0.1, 'pops': 0.11,
            'scratch': 0.057, 'shine': 0.3, 'rise': 0.063, 'car': 0.07, 'click': 0.07}
SFX_PAN = {'whoosh': 'sweep'}


def build_sfx(cues):
    L, R = np.zeros(N), np.zeros(N)
    cache = {}
    for c in cues:
        kind = c['type']
        if kind not in cache:
            cache[kind] = sfx(kind)
        x = cache[kind] * SFX_GAIN[kind] * c['gain']
        if SFX_PAN.get(kind) == 'sweep':
            pan = np.linspace(-0.6, 0.6, len(x))
            place(L, c['t'], x * np.sqrt((1 - pan) / 2) * 1.41)
            place(R, c['t'], x * np.sqrt((1 + pan) / 2) * 1.41)
        else:
            place(L, c['t'], x); place(R, c['t'], x)
    return np.stack([L, R])


def envelope(x, attack=0.03, release=0.35, win=0.02):
    hop = int(win * SR)
    frames = len(x) // hop
    rms = np.sqrt(np.mean(x[:frames * hop].reshape(frames, hop) ** 2, axis=1) + 1e-12)
    out = np.zeros(frames)
    acc = 0.0
    a_att, a_rel = np.exp(-win / attack), np.exp(-win / release)
    for i, v in enumerate(rms):
        a = a_att if v > acc else a_rel
        acc = a * acc + (1 - a) * v
        out[i] = acc
    return np.interp(np.arange(len(x)) / hop, np.arange(frames), out)


def rms(x):
    return float(np.sqrt(np.mean(x ** 2)))


def compress(x, thresh_db=-24, ratio=3.0):
    """Feed-forward RMS compressor (tames TTS peaks, more 'creator' presence)."""
    env = envelope(x, attack=0.005, release=0.08, win=0.005)
    thr = 10 ** (thresh_db / 20)
    gain = np.where(env > thr, (env / thr) ** (1 / ratio - 1), 1.0)
    return x * gain


def write_wav(path, x):
    import wave
    pcm = (np.clip(x.T, -1, 1) * 32767).astype('<i2')
    with wave.open(str(path), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(pcm.tobytes())


def main():
    build = Path(sys.argv[1])
    tl = json.load(open(build / 'timeline.json'))
    cues = json.load(open(build / 'cues.json'))
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(build / 'voice.wav'), '-ar', str(SR), '-ac', '1',
                          '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    voice = np.zeros(N)
    v = np.frombuffer(raw, dtype=np.float32).astype(np.float64)
    voice[:min(N, len(v))] = v[:N]
    voice = compress(voice / np.abs(voice).max())

    # musical break: the pause right before "Regala progreso"
    regala = next(x for x in tl['tokens'] if x['section'] == 'aplicacion' and x['text'].lower().startswith('regala'))
    breaks = [(regala['start'] - 0.42, regala['start'] - 0.02)]
    music = build_music(breaks)
    effects = build_sfx(cues)

    # levels: voice speech RMS as reference
    env = envelope(voice)
    speaking = env > 0.25 * env.max()
    v_rms = rms(voice[speaking]) if speaking.any() else rms(voice)
    music *= 0.2 * v_rms / rms(music)                          # ~ -14 dB under the voice
    music_dry = music.copy()
    duck = 1 - 0.45 * np.clip(env / (0.35 * env.max()), 0, 1)  # up to ~ -5 dB more while talking
    music *= duck
    mix = music + effects + np.stack([voice, voice])
    # soft bus limiter, referenced to the voice peak so stray SFX peaks get rounded off
    drive = 0.85 / np.abs(voice).max()
    mix = np.tanh(mix * drive)
    out = build / 'mix_raw.wav'
    pcm = (np.clip(mix.T, -1, 1) * 32767).astype('<i2')
    import wave
    with wave.open(str(out), 'wb') as f:
        f.setnchannels(2); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes(pcm.tobytes())
    # two-pass loudness normalisation for Instagram (-14 LUFS, -1.5 dBTP)
    p1 = subprocess.run(['ffmpeg', '-hide_banner', '-i', str(out), '-af',
                         'loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json', '-f', 'null', '-'],
                        capture_output=True, text=True).stderr
    m = json.loads(p1[p1.rindex('{'):p1.rindex('}') + 1])
    af = (f"loudnorm=I=-14:TP=-1.5:LRA=11:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', str(out), '-af', af, '-ar', str(SR),
                    str(build / 'mix.wav')], check=True)
    print(f"mix.wav written; input loudness {m['input_i']} LUFS -> -14 LUFS; "
          f"cues {len(cues)}")
    if len(sys.argv) > 2:
        stems = Path(sys.argv[2])
        stems.mkdir(parents=True, exist_ok=True)
        gain = 10 ** ((-14 - float(m['input_i'])) / 20)       # same gain loudnorm gave the full mix
        for name, x in (('sfx', effects), ('musica', music_dry), ('sfx_musica', effects + music_dry),
                        ('voz_guia', np.stack([voice, voice]))):
            write_wav(stems / f'{name}.wav', np.tanh(x * drive) * gain)
        print(f'stems written to {stems} (gain {20 * np.log10(gain):+.1f} dB, matching mix.wav)')


if __name__ == '__main__':
    main()
