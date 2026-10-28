"""Voz en off armada con tomas independientes (una por bloque): sin cortes dentro de las frases.

Uso: python3 voz_tomas.py <proyecto>   (lee <proyecto>/audio/voz-raw/tomas/NN-T.mp3)
"""
import glob, os, subprocess, sys, wave
import numpy as np
SR = 48000; N = SR * 60
proj = sys.argv[1]
# (inicio deseado, fin máximo) de cada bloque, en el orden de las tomas 00..NN
SLOTS = {'reel-viral': [(0.0, 4.55), (4.6, 7.95), (8.05, 14.95), (15.05, 21.95), (22.05, 26.95),
                        (27.05, 33.95), (34.05, 39.95), (40.05, 43.5), (43.55, 51.95), (52.05, 59.4)],
         'viaje-heroe': [(0.0, 3.95), (4.05, 10.95), (11.15, 15.95), (16.15, 20.95), (21.15, 25.95), (26.15, 30.95),
                         (31.15, 35.95), (36.55, 45.95), (46.05, 51.95), (52.05, 53.6), (53.65, 56.6), (56.65, 59.4)],
         'liquid-death': [(0.0, 4.4), (4.7, 11.95), (12.05, 18.55), (19.4, 24.05), (24.15, 30.05), (30.15, 38.05),
                          (38.15, 45.05), (45.15, 51.4), (51.5, 52.9), (52.95, 57.65), (57.75, 59.4)]}[proj]
def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def trim(x):  # quita el silencio de las orillas con base en la energía (sin tocar palabras)
    env = np.convolve(np.abs(x), np.ones(480) / 480, 'same'); idx = np.where(env > 10 ** (-45 / 20))[0]
    y = x[max(0, idx[0] - int(.04 * SR)): idx[-1] + int(.12 * SR)].copy()
    # pausas internas de silencio total mayores a 0.35 s se dejan en 0.25 s (no toca palabras)
    e = np.convolve(np.abs(y), np.ones(480) / 480, 'same') < 10 ** (-48 / 20); out, i = [], 0
    while i < len(y):
        if e[i]:
            j = i
            while j < len(y) and e[j]: j += 1
            out.append(y[i:i + int(.25 * SR)] if j - i > .35 * SR else y[i:j]); i = j
        else:
            j = i
            while j < len(y) and not e[j]: j += 1
            out.append(y[i:j]); i = j
    y = np.concatenate(out)
    f = int(.01 * SR); y[:f] *= np.linspace(0, 1, f); y[-f:] *= np.linspace(1, 0, f)
    return y
def stretch(p, tempo):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={tempo:.4f}', '-f', 'f32le', '-'],
                                        input=p.astype(np.float32).tobytes(), capture_output=True, check=True).stdout, np.float32)
D = os.path.join(proj, 'audio', 'voz-raw', 'tomas')
voice = np.zeros(N); prev_end = -1.0; ok = True
for k, (t0, t1) in enumerate(SLOTS):
    takes = [trim(load(f)) for f in sorted(glob.glob(os.path.join(D, f'{k:02d}-*.mp3')))]
    p = min(takes, key=len)  # entre las dos tomas, la que mejor cabe
    tempo = 1.0
    if len(p) / SR > t1 - t0: tempo = min(len(p) / SR / (t1 - t0), 1.10); p = stretch(p, tempo)
    start = max(t0, prev_end + .15); end = start + len(p) / SR
    i = int(start * SR); voice[i:i + len(p)] += p[: N - i]; prev_end = end
    flag = 'OK' if end <= t1 + .05 else 'REVISAR'; ok &= flag == 'OK'
    print(f'{k:02d} {start:6.2f}-{end:6.2f} (límite {t1:5.2f}) tempo {tempo:.3f} {flag}')
voice *= 0.89 / np.abs(voice).max()
def rd(p):
    with wave.open(p) as w: d = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32767
    return d.reshape(-1, 2).T
A = os.path.join(proj, 'audio')
mus, fx = rd(os.path.join(A, 'musica-sola.wav')), rd(os.path.join(A, 'efectos-solos.wav'))
env = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(.4 * SR)) / int(.4 * SR), 'same')
mix = np.tanh(mus * (1 - .25 * np.clip(env * 3, 0, 1)) + fx * .7 + np.stack([voice, voice]))
def save(p, y):
    d = (np.clip(y, -1, 1).T * 32767).astype('<i2')
    with wave.open(p, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(os.path.join(A, 'voz-en-off.wav'), np.stack([voice, voice])); save(os.path.join(A, 'mezcla-con-voz.wav'), mix)
print('TODO OK' if ok else 'REVISAR')
