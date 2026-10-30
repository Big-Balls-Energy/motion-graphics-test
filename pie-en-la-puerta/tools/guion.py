"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde pie-en-la-puerta/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «PUERTA» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py pie-en-la-puerta
VOZ = [(0.18, 4.08, '[intrigued] ¿Pondrías un letrero enorme y feo… en el jardín de tu casa?'),
       (5.03, 10.06, 'En 1966, dos psicólogos de Stanford se lo pidieron a varias familias.'),
       (11.04, 14.93, 'Cuando se lo pedían directo… solo el diecisiete por ciento aceptaba.'),
       (16.04, 21.90, 'Pero a otras familias, primero les pidieron algo pequeño: un letrerito de unos ocho centímetros en la ventana.'),
       (22.93, 28.62, 'Dos semanas después, les pidieron el letrero grande… [excited] y aceptó el setenta y seis por ciento.'),
       (29.52, 35.45, 'Se llama «el pie en la puerta»: después de un sí pequeño, queremos ser coherentes con lo que ya hicimos.'),
       (36.44, 41.00, 'Ojo: estudios posteriores encontraron un efecto más pequeño… pero real.'),
       (42.04, 49.27, 'En tu negocio, no pidas la venta de entrada. Pide un sí pequeño: una muestra, una pregunta, un diagnóstico gratis.'),
       (50.34, 51.73, '[excited] Comenta… ¡puerta!'),
       (55.64, 60.37, 'Y te mando cinco pequeños «sí» que llevan a una venta. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — El pie en la puerta: 17% → 76%", "",
       "Video: `Atlas_Path_Pie_en_la_Puerta.mp4` (con voz de Fernanda) y `Atlas_Path_Pie_en_la_Puerta-sin-voz.mp4` · 1080×1920 · 30 fps · 62 s · H.264 + AAC · "
       "música electrónica a 108.4 BPM (28 compases exactos, el loop cierra); "
       "efectos sincronizados (letrero que cae, rejilla de 100 casas, letrerito en la ventana, barras 17 % y 76 %, puerta con pie, sello OJO, escalera de «sí» pequeños y clic en seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla; los subtítulos son una versión condensada de la voz. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es la palabra clave, sin subtítulo encima. Las cifras se quedan al menos 2 s.", ""]
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
