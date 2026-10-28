"""Coloca la voz en off (ElevenLabs) sobre la línea de tiempo y mezcla con música y efectos."""
import subprocess, re, json, wave, numpy as np
SR = 48000; N = SR * 60
def load(path):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
def trim(x, thr=0.01):
    idx = np.where(np.abs(x) > thr)[0]
    return x[max(0, idx[0] - int(.03 * SR)): idx[-1] + int(.08 * SR)] if len(idx) else x
def segments(path):  # tramos de voz entre silencios
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-38dB:d=0.18', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r'silence_start: ([\d.]+)', out)]; en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', out)]
    seg, cur = [], 0.0
    for s, e in zip(st, en):
        if s > cur + .05: seg.append((cur, s))
        cur = e
    seg.append((cur, None)); return seg
voice = np.zeros(N); placed = []
def put(x, t, label):
    i = int(t * SR); voice[i:i + len(x)] += x[: N - i]; placed.append((label, round(t, 2), round(t + len(x) / SR, 2)))
R = 'voz-raw/'
put(trim(load(R + '1-hook.mp3')), 0.05, 'hook')
put(trim(load(R + '2-what.mp3')), 4.15, 'qué son')
cards = load(R + '3-cards.mp3'); seg = segments(R + '3-cards.mp3'); assert len(seg) == 24, len(seg)
for k in range(12):
    a, m1 = seg[2 * k]; m2, b = seg[2 * k + 1]; b = b or len(cards) / SR
    gap = min(m2 - m1, .2)  # la pausa entre arquetipo y marca se acorta a 0.2 s como máximo
    clip = np.concatenate([cards[int(max(0, a - .03) * SR): int(m1 * SR)], np.zeros(int(gap * SR)), cards[int(m2 * SR): int((b + .05) * SR)]])
    assert len(clip) / SR <= 1.92, (k, len(clip) / SR)
    put(clip, 12.0 + 2 * k + .06, f'carta {k + 1}')
put(trim(load(R + '4-why.mp3')), 36.6, 'por qué')
put(trim(load(R + '5-app.mp3')), 46.3, 'aplicación')
put(trim(load(R + '6-cta.mp3')), 54.3, 'cta')
voice *= 0.89 / np.abs(voice).max()
def rd(p):
    with wave.open(p) as w: d = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32767
    return d.reshape(-1, 2).T
mus, fx = rd('musica-sola.wav'), rd('efectos-solos.wav')
# bajo la voz la música queda alrededor del 10 %
env = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(.4 * SR)) / int(.4 * SR), 'same'); duck = 1 - .25 * np.clip(env * 3, 0, 1)
mix = np.tanh(mus * duck + fx * .7 + np.stack([voice, voice]))
def save(p, x):
    d = (np.clip(x, -1, 1).T * 32767).astype('<i2')
    with wave.open(p, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save('voz-en-off.wav', np.stack([voice, voice])); save('mezcla-con-voz.wav', mix)
for p in placed: print(p)
print('pico', np.abs(mix).max())
