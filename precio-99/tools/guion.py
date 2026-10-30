"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde precio-99/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; el nombre del efecto y «PRECIO» ≥ 3 s solos;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py precio-99
VOZ = [(0.15, 2.26, '[curious] ¿Por qué todo cuesta noventa y nueve…'), (2.50, 3.64, '[intrigued] ¿…y no cien?'),
       (5.05, 7.16, 'No es casualidad. Tiene un nombre…'), (8.75, 11.68, '[dramatically] Se llama: efecto del dígito izquierdo.'),
       (12.55, 18.84, 'Investigadores de Kellogg y del MIT pusieron el mismo vestido en un catálogo… con tres precios distintos.'),
       (19.45, 20.96, '[curious] ¿Cuál crees que vendió más?'), (21.95, 23.82, '[excited] ¡El de treinta y nueve dólares!'),
       (23.97, 26.18, 'Un tercio más que el de treinta y cuatro.'), (26.40, 28.60, 'Más caro… [surprised] y vendió más. (acelerada 5 %)'),
       (28.75, 31.26, 'Y a cuarenta y cuatro, no hubo diferencia.'),
       (31.55, 36.51, '[curious] ¿Por qué funciona? Leemos de izquierda a derecha… y el primer número es el que manda.'),
       (38.35, 42.21, 'Noventa y nueve suena a «noventa y algo»… no a cien. (acelerada 3 %)'), (42.45, 44.94, 'Y funciona más cuando cambia el primer dígito.'),
       (47.05, 50.38, 'Lo ves en menús, en la gasolina y en las suscripciones.'), (51.50, 54.76, '¿Tienes un negocio? Úsalo en tus productos de compra práctica.'),
       (56.05, 61.33, '[serious] Pero ojo: en compras emocionales, como un regalo… el precio redondo convence más.'),
       (63.05, 64.59, '[excited] Comenta… ¡precio!'), (68.30, 71.35, 'Y te mando más trucos. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — ¿Por qué todo cuesta $99?", "",
       "Video: `Atlas_Path_Precios_99.mp4` (con voz de Fernanda) y `Atlas_Path_Precios_99-sin-voz.mp4` · 1080×1920 · 30 fps · 75 s · H.264 + AAC · "
       "música electrónica a 112 BPM (35 compases exactos, el loop cierra), 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; "
       "efectos sincronizados (partículas que forman $100 y se rearman en $99, cubos que encajan, papel, etiquetas, barras, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla; los subtítulos son una versión condensada de la voz. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es el nombre del efecto o la palabra clave, sin subtítulo encima. Las cifras se quedan al menos 2 s.", ""]
srt_rows = []; n = 0
items = [('sub', s) for s in TL['subs']] + [('card', c) for c in TL.get('holds', [])]
items.sort(key=lambda x: x[1]['a'])
for sc in TL['scenes']:
    out += [f"## {ts(sc['a'])} – {ts(sc['b'])} · {sc['name']}", "", f"_Visual: {sc['vis']}_", "", "| Entra | Sale | En pantalla | ritmo |", "|---|---|---|---|"]
    rows = []
    for kind, s in items:
        if not (sc['a'] <= s['a'] < sc['b']): continue
        d = s['b'] - s['a']; w = len(s['text'].split())
        if kind == 'sub':
            rows.append((s['a'], f"| {ts(s['a'])} | {ts(s['b'])} | {s['text']} | {w} pal · {d:.1f} s · {w / d:.1f} pal/s |"))
            n += 1; srt_rows.append(f"{n}\n{srt(s['a'])} --> {srt(s['b'])}\n{s['text']}\n")
        elif s.get('sola'):
            rows.append((s['a'], f"| {ts(s['a'])} | {ts(s['b'])} | **[SOLA EN PANTALLA] {s['text']}** | sola {d:.1f} s |"))
            n += 1; srt_rows.append(f"{n}\n{srt(s['a'])} --> {srt(s['b'])}\n{s['text']}\n")
        else:
            rows.append((s['a'], f"| {ts(s['a'])} | {ts(s['b'])} | *cifra en pantalla:* **{s['text']}** | {d:.1f} s |"))
    if sc['id'] != 'cta': rows.append((sc['b'] - .5, f"| {ts(sc['b'] - .5)} | {ts(sc['b'])} | *(pausa)* | — |"))
    rows.sort(key=lambda r: r[0]); out += [r for _, r in rows]; out.append("")

if VOZ:
    out += ["## Voz en off (Fernanda – Smooth and Articulate, `eleven_v4`): una toma independiente por bloque", "",
            "Ninguna toma se cortó: cada bloque se grabó por separado y solo se acortaron silencios.", "", "| Bloque | Entra – sale | Texto grabado |", "|---|---|---|"]
    out += [f"| {i:02d} | {ts(a)} – {ts(b)} | {t} |" for i, (a, b, t) in enumerate(VOZ)]
out += ["", open(sys.argv[2]).read() if len(sys.argv) > 2 else ""]
open('guion-con-tiempos.md', 'w').write("\n".join(out)); open('subtitulos.srt', 'w').write("\n".join(srt_rows))

bad = [s for s in TL['subs'] if (s['b'] - s['a']) < 1.5 - 1e-6 or len(s['text'].split()) / (s['b'] - s['a']) > 2.3 + 1e-6 or not 3 <= len(s['text'].split()) <= 5]
badc = [c['text'] for c in TL.get('holds', []) if (c['b'] - c['a']) < c.get('min', 2) - 1e-6]
# una frase «sola» no puede tener subtítulo encima
bads = [(c['text'], s['text']) for c in TL.get('holds', []) if c.get('sola') for s in TL['subs'] if s['a'] < c['b'] and s['b'] > c['a']]
# pausa de 0.5 s entre escenas: ningún subtítulo puede seguir en pantalla en el último medio segundo de su escena
badp = [s['text'] for s in TL['subs'] for sc in TL['scenes'] if sc['id'] != 'cta' and sc['a'] <= s['a'] < sc['b'] and s['b'] > sc['b'] - 0.5 + 1e-6]
print('bloques', len(TL['subs']), 'fuera de regla:', [(s['text'], round(s['b'] - s['a'], 2)) for s in bad], 'cifras cortas:', badc, 'solas con subtítulo:', bads, 'sin pausa:', badp)
