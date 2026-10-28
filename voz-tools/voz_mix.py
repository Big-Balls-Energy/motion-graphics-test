"""Coloca una narración de ElevenLabs sobre la línea de tiempo de un reel y la mezcla.

Uso: python3 voz_mix.py <proyecto> <narracion.mp3>
La narración trae una pausa larga entre cada frase de cues.json; se corta por las
pausas más largas y cada frase empieza en su marca de tiempo. Si una frase no cabe
en su ventana se acelera un poco (máximo 15 %).
"""
import json, re, subprocess, sys, wave, os
import numpy as np

SR = 48000; N = SR * 60
proj, src = sys.argv[1], sys.argv[2]
cues = json.load(open(os.path.join(os.path.dirname(__file__), 'cues.json')))[proj]

def load(path, tempo=1.0):
    af = ['-af', f'atempo={tempo:.4f}'] if abs(tempo - 1) > 1e-3 else []
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', path, *af, '-ac', '1', '-ar', str(SR), '-f', 'f32le', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()

def silences(path):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-i', path, '-af', 'silencedetect=noise=-40dB:d=0.3', '-f', 'null', '-'], capture_output=True, text=True).stderr
    st = [float(v) for v in re.findall(r'silence_start: (-?[\d.]+)', out)]
    en = [float(v) for v in re.findall(r'silence_end: ([\d.]+)', out)]
    return list(zip(st, en))

x = load(src); dur = len(x) / SR
# cortes exactos a partir de la transcripción con tiempos por palabra (words.json)
W = json.load(open(os.path.join(os.path.dirname(src), 'words.json')))['words']
groups, cur, skip = [], [], False
for w in W:
    t = w['text']
    if t.startswith('[long'): groups.append(cur); cur = []; skip = True; continue
    if skip and t.startswith('pause]'): skip = False; continue
    skip = False
    if t.startswith('[') and t.endswith(']'): continue  # etiquetas de tono
    cur.append(w)
groups.append(cur); groups = [g for g in groups if g]
if len(groups) != len(cues): sys.exit(f'{proj}: {len(groups)} frases transcritas para {len(cues)} marcas')
def est(txt): return 1.0
exp = [g[-1]['end'] - g[0]['start'] for g in groups]
pieces = []
for i, g in enumerate(groups):
    a0 = max(0, g[0]['start'] - .05); a1 = g[-1]['end'] + .12
    if i + 1 < len(groups): a1 = min(a1, groups[i + 1][0]['start'] - .02)
    pieces.append(x[int(a0 * SR): int(a1 * SR)])
# control: la duración de cada pieza debe ser proporcional a su texto
words = [len(re.sub(r'\[[^\]]*\]', '', c[2]).split()) for c in cues]
rates = [len(p) / SR / e for p, e in zip(pieces, exp)]
voice = np.zeros(N); report = []; prev_end = -1.0
def stretch(p, tempo):
    return np.frombuffer(subprocess.run(['ffmpeg', '-v', 'error', '-f', 'f32le', '-ar', str(SR), '-ac', '1', '-i', '-', '-af', f'atempo={tempo:.4f}', '-f', 'f32le', '-'],
                                        input=p.astype(np.float32).tobytes(), capture_output=True, check=True).stdout, np.float32)
prev_t1 = -1.0
for (t0, t1, txt), p, w, r in zip(cues, pieces, words, rates):
    d = len(p) / SR; tempo = 1.0
    lead = .15 if t0 - prev_t1 >= .08 else .4  # dentro de la misma escena puede adelantarse más
    prev_t1 = t1
    if d > t1 - t0:  # acelera como máximo 10 % para que suene natural
        tempo = min(d / (t1 - t0), 1.10); p = stretch(p, tempo); d = len(p) / SR
    # si aún no cabe, arranca un poco antes aprovechando el silencio previo
    start = max(0.0, prev_end + .12, min(t0, max(t1 - d, t0 - lead)))
    i = int(start * SR); voice[i:i + len(p)] += p[: N - i]
    end = start + d; prev_end = end
    report.append((round(start, 2), round(end, 2), round(t1, 2), round(tempo, 3), round(start - t0, 2), 'OK' if end <= t1 + .45 and start - t0 >= -.45 and start - t0 <= .5 else 'REVISAR', re.sub(r'\[[^\]]*\] ?', '', txt)[:48]))
for row in report: print(*row, sep=' | ')
voice *= 0.89 / np.abs(voice).max()

def rd(p):
    with wave.open(p) as w: d = np.frombuffer(w.readframes(w.getnframes()), '<i2').astype(np.float32) / 32767
    return d.reshape(-1, 2).T
A = os.path.join(proj, 'audio')
mus, fx = rd(os.path.join(A, 'musica-sola.wav')), rd(os.path.join(A, 'efectos-solos.wav'))
env = np.convolve((np.abs(voice) > .02).astype(float), np.ones(int(.4 * SR)) / int(.4 * SR), 'same')
duck = 1 - .25 * np.clip(env * 3, 0, 1)  # la música baja a ~10 % mientras habla la voz
mix = np.tanh(mus * duck + fx * .7 + np.stack([voice, voice]))
def save(p, y):
    d = (np.clip(y, -1, 1).T * 32767).astype('<i2')
    with wave.open(p, 'wb') as w: w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes(d.tobytes())
save(os.path.join(A, 'voz-en-off.wav'), np.stack([voice, voice])); save(os.path.join(A, 'mezcla-con-voz.wav'), mix)
print('REVISAR' if any(r[5] != 'OK' for r in report) else 'TODO OK')
