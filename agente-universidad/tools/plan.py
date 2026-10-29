"""Plan de edición a partir de los tiempos por palabra (ElevenLabs Scribe) y del análisis del video (cortes y cara).

Uso (desde agente-universidad/): python3 tools/plan.py
Lee tools/transcripcion_palabras.json y tools/analisis.json; escribe tools/plan.json y tools/plan.js (window.PLAN) con:
  segs    tramos del video fuente que se conservan [inicio, fin) en segundos (se quitan las pausas ≥ 0.22 s)
  frames  por cada cuadro de salida: [cuadro fuente, escala, centro x, centro y] (encuadre centrado en la cara)
  faces   caja de la cara por cuadro de salida, ya en coordenadas de pantalla (para no tapar la cara con gráficos)
  htop    altura de pantalla donde empieza su cabeza (del matte), para poner títulos detrás de ella sin taparlos de más
  cuts    tiempos de salida donde cambia la imagen (cortes de toma y cortes por pausa)
  words   palabras con su tiempo de salida, palabra clave y emoji
  blocks  bloques de subtítulos literales (1–5 palabras, una línea, ≥ 0.45 s cuando se puede)"""
import json, re
import numpy as np

FPS = 30
W = [w for w in json.load(open('tools/transcripcion_palabras.json'))['words'] if w['type'] == 'word']
A = json.load(open('tools/analisis.json')); NF = A['frames']
FIX = {'Pad': 'Path'}                       # Scribe escribió «Atlas Pad»
for w in W: w['text'] = FIX.get(w['text'], w['text'])

# ---------- 1. ritmo: quitar las pausas largas sin tocar las palabras ----------
GAP, KEEP_AFTER, KEEP_BEFORE, LEAD, TAIL = .22, .08, .06, .10, .12
fr = lambda x: round(x * FPS) / FPS
remove = [(0.0, max(0.0, W[0]['start'] - LEAD))]
for a, b in zip(W, W[1:]):
    if b['start'] - a['end'] >= GAP: remove.append((a['end'] + KEEP_AFTER, b['start'] - KEEP_BEFORE))
remove = [(fr(a), fr(b)) for a, b in remove if fr(b) - fr(a) >= 2 / FPS]
segs, cur = [], 0.0
for a, b in remove:
    if a > cur: segs.append([cur, a])
    cur = b
segs.append([cur, fr(min(W[-1]['end'] + TAIL, NF / FPS))])
src_of = []                                  # cuadro fuente de cada cuadro de salida
seg_out = []                                 # inicio de cada tramo en tiempo de salida
for a, b in segs:
    seg_out.append(len(src_of) / FPS)
    src_of += list(range(round(a * FPS), round(b * FPS)))
src_of = [min(i, NF - 1) for i in src_of]
NO = len(src_of); DUR = NO / FPS
def out_t(ts):                               # tiempo fuente → tiempo de salida
    for (a, b), o in zip(segs, seg_out):
        if a - 1e-6 <= ts < b + 1e-6: return round(o + (ts - a), 3)
    return round(seg_out[-1] + segs[-1][1] - segs[-1][0], 3)

# ---------- 2. cortes de imagen y subtomas ----------
joins = [i for i in range(1, NO) if src_of[i] != src_of[i - 1] + 1 and src_of[i] != src_of[i - 1]]   # cortes por pausa
src_cuts = set(A['cuts'])
shot_cuts = [i for i in range(1, NO) if src_of[i] in src_cuts and src_of[i - 1] == src_of[i] - 1]
cut_frames = sorted(set(joins) | set(shot_cuts))
bounds = [0] + cut_frames + [NO]
subs = list(zip(bounds, bounds[1:]))

# ---------- 3. encuadre: cara estable por subtoma, zoom alterno y composición por sección ----------
# cada sección deja espacio a sus gráficos: C = cara al centro, L = cara a la izquierda (gráficos a la derecha), R = a la derecha
LAYOUT = [(0, 'C', 900), (7, 'L', 760), (25, 'R', 760), (51, 'C', 760), (76, 'R', 760), (114, 'C', 740), (128, 'R', 760), (141, 'C', 760), (153, 'C', 740)]
FX = {'C': 540, 'L': 380, 'R': 720}
cut_t = [i / FPS for i in cut_frames]
switch = []                                  # (tiempo de salida, x, y, instantáneo): en un corte cercano el cambio es seco; si no, paneo suave
for wi, mode, y in LAYOUT:
    t0 = out_t(W[wi]['start']) - .12 if wi else 0.0
    near = [c for c in cut_t if abs(c - t0) < .45]
    switch.append((near[0] if near else t0, FX[mode], y, bool(near) or wi == 0))
def target(t):                               # posición deseada de la cara en pantalla
    x, y = switch[0][1], switch[0][2]
    for k, (ts, sx, sy, inst) in enumerate(switch):
        if t < ts: break
        px, py = (switch[k - 1][1], switch[k - 1][2]) if k else (sx, sy)
        e = 1.0 if inst else min(1.0, (t - ts) / .4); e = e * e * (3 - 2 * e)
        x, y = px + (sx - px) * e, py + (sy - py) * e
    return x, y
faces_src = A['faces']
def face_med(a, b):
    fs = [faces_src[str(src_of[i])] for i in range(a, b) if faces_src.get(str(src_of[i]))]
    return np.median(np.array([x[:4] for x in fs]), axis=0) if fs else None
from PIL import Image
_ht = {}
def head_top(fi):                         # fila más alta de la silueta (matte) en la franja central: dónde empieza su cabeza
    if fi not in _ht:
        al = np.asarray(Image.open(f'mat/m_{fi:05d}.png'))[:, 200:880, 1]
        rows = np.nonzero((al > 128).sum(1) > 24)[0]
        _ht[fi] = int(rows[0]) if len(rows) else 400
    return _ht[fi]
frames, faces_out, htop, prev_f = [], [], [], np.array([400, 500, 300, 420.0])
for n, (a, b) in enumerate(subs):
    f = face_med(a, b); f = prev_f if f is None else f; prev_f = f
    fx, fy, fh = f[0] + f[2] / 2, f[1] + f[3] / 2, f[3]
    for i in range(a, b):
        t = i / FPS; X, Y = target(t); off = abs(X - 540) > 60
        tgt = (560 if n % 2 == 0 else 520) if off else (520 if n % 2 == 0 else 460)   # alterna cerrado / medio en cada corte
        s0 = float(np.clip(tgt / fh, 1.04, 1.30))
        p_ = (i - a) / max(1, b - a - 1); s = s0 * (1 + .025 * p_)     # empuje lento dentro de la subtoma
        left = np.clip(fx - X / s, 0, 1080 - 1080 / s); top = np.clip(fy - Y / s, 0, 1920 - 1920 / s)
        cx, cy = left + 540 / s, top + 960 / s
        frames.append([src_of[i], round(s, 4), round(float(cx), 1), round(float(cy), 1)])
        g = faces_src.get(str(src_of[i])) or list(f) + [0]
        faces_out.append([round(float((g[0] - cx) * s + 540), 1), round(float((g[1] - cy) * s + 960), 1), round(float(g[2] * s), 1), round(float(g[3] * s), 1)])
        htop.append(round(float((head_top(src_of[i]) - cy) * s + 960), 1))

# ---------- 4. palabras, palabras clave y emojis ----------
clean = lambda t: re.sub(r'[¿?¡!,.:;]', '', t)
KEY = {'negocio', 'mensajes', 'consultas', 'olvidando', 'responder', 'seguimientos', 'oportunidades', 'venta', 'imagina', 'preguntas',
       'datos', 'información', 'agendar', 'citas', 'atlas', 'path', 'automatización', 'agente', 'universidad', 'prospectos', 'carrera',
       'dudas', 'planes', 'registra', 'instalaciones', 'visita', 'sistema', 'comercial', 'organizada', 'tiempo', 'repetitivas',
       'importante', 'cerrar', 'hacemos', 'clic', 'escríbenos', 'ti', 'todo', 'eso'}
EMOJI = {'mensajes': '💬', 'venta?': '💸', 'imagina': '🤯', 'citas': '📅', 'agente': '🤖', 'universidad': '🎓', 'datos': '📊',
         'visita': '📍', 'organizada.': '✅', 'repetitivas': '🔁', 'importante:': '🎯', 'oportunidades.': '🚀', 'escríbenos': '📩'}
used = set(); words = []
for i, w in enumerate(W):
    t = w['text']; e = EMOJI.get(t.lower()) if t.lower() not in used else None
    if e: used.add(t.lower())
    words.append({'t': t, 'a': out_t(w['start']), 'b': out_t(w['end']), 'key': clean(t).lower() in KEY, 'emoji': e})

# ---------- 5. bloques de subtítulos literales: 1–4 palabras, ≤ 20 caracteres, cortando en la puntuación ----------
SMALL = {'y', 'a', 'de', 'en', 'el', 'la', 'los', 'las', 'un', 'una', 'que', 'con', 'su', 'sus', 'lo', 'les', 'te', 'tu', 'o', 'para', 'por', 'del', 'al', 'es', 'se', 'si', 'e', 'qué', 'da', 'tanto', 'tener'}
MAXC, MAXW = 20, 4
size = lambda b: len(' '.join(clean(W[j]['text']) for j in b))
blocks, cur = [], []
for i, w in enumerate(W):
    cur.append(i); nxt = W[i + 1] if i + 1 < len(W) else None
    punct = w['text'][-1] in ',.?:;!'; gap = nxt['start'] - w['end'] if nxt else 9
    if punct or gap > .3 or len(cur) >= MAXW or nxt is None or size(cur) + 1 + len(clean(nxt['text'])) > MAXC:
        if not punct and nxt is not None and len(cur) > 1 and clean(w['text']).lower() in SMALL:
            cur.pop(); blocks.append(cur); cur = [i]       # no termina en palabra corta: pasa al siguiente bloque
        else: blocks.append(cur); cur = []
if cur: blocks.append(cur)
# los bloques de menos de 0.45 s no se alcanzan a leer: se unen con el siguiente (o con el anterior) si caben en una línea
dur = lambda b: out_t(W[b[-1]]['end']) - out_t(W[b[0]]['start'])
k = 0
while k < len(blocks):
    b = blocks[k]
    if dur(b) < .45 and len(blocks) > 1:
        if k + 1 < len(blocks) and size(b + blocks[k + 1]) <= 24 and len(b + blocks[k + 1]) <= 5 and W[b[-1]]['text'][-1] not in '.?':
            blocks[k] = b + blocks.pop(k + 1); continue
        if k > 0 and size(blocks[k - 1] + b) <= 24 and len(blocks[k - 1] + b) <= 5 and W[blocks[k - 1][-1]]['text'][-1] not in '.?':
            blocks[k - 1] += blocks.pop(k); k -= 1; continue
    k += 1
BL = []
for k, b in enumerate(blocks):
    a = max(0, words[b[0]]['a'] - .05)
    e = words[blocks[k + 1][0]]['a'] - .03 if k + 1 < len(blocks) else DUR
    if k + 1 < len(blocks) and e - words[b[-1]]['b'] > .45: e = words[b[-1]]['b'] + .3
    BL.append({'a': round(a, 3), 'b': round(e, 3), 'w': b})

plan = {'fps': FPS, 'dur': round(DUR, 3), 'n': NO, 'segs': segs, 'seg_out': [round(x, 3) for x in seg_out],
        'cuts': [round(i / FPS, 3) for i in cut_frames], 'frames': frames, 'faces': faces_out, 'htop': htop, 'words': words, 'blocks': BL}
json.dump(plan, open('tools/plan.json', 'w'), ensure_ascii=False)
open('tools/plan.js', 'w').write('window.PLAN=' + json.dumps(plan, ensure_ascii=False) + ';\n')
print(f'salida {DUR:.2f} s ({NO} cuadros) de {NF / FPS:.2f} s · tramos {len(segs)} · cortes {len(cut_frames)} · bloques {len(BL)}')
for k, b in enumerate(BL):
    print(f"{k:3d} {b['a']:6.2f}-{b['b']:6.2f}  " + ' '.join(('*' if words[j]['key'] else '') + W[j]['text'] + (words[j]['emoji'] or '') + f'[{j}]' for j in b['w']))
