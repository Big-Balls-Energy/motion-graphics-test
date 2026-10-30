"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde busqueda-visual/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «VISUAL» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py busqueda-visual
VOZ = [(0.16, 4.05, '[intrigued] La gente ya no solo escribe en Google… ahora busca con fotos.'),
       (4.72, 10.00, 'En su reporte del veintinueve de octubre, Sundar Pichai, director de Google, dio tres cifras.'),
       (10.73, 17.14, 'Uno: la app de Gemini ya tiene mil millones de usuarios. Es el producto que más rápido ha crecido en su historia.'),
       (17.82, 22.06, 'Dos: ya hay más de cincuenta mil millones de búsquedas visuales al mes.'),
       (22.74, 28.50, 'Y tres: una de cada cinco búsquedas en el Modo IA usa voz, imágenes o documentos.'),
       (29.24, 33.23, '¿Qué significa para ti? Que tus fotos ya son parte de cómo te encuentran.'),
       (33.93, 39.15, 'Sube fotos reales de tus productos, con buena luz… y nómbralas como las busca tu cliente.'),
       (39.80, 41.42, '[excited] Comenta… ¡visual!'),
       (45.43, 50.15, 'Y te mando una lista para que Google entienda las fotos de tu negocio. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Google: ahora buscan con fotos (Gemini 1,000 M · 50,000 M búsquedas visuales)", "",
       "Video: `Atlas_Path_Busqueda_Visual.mp4` (con voz de Fernanda) y `Atlas_Path_Busqueda_Visual-sin-voz.mp4` · 1080×1920 · 30 fps · 51 s · H.264 + AAC · "
       "música electrónica a 131.8 BPM (28 compases exactos, el loop cierra); "
       "efectos sincronizados (visor de cámara que escanea, silueta y tres cifras, contadores 1,000 M y 50,000 M, íconos de búsqueda, fotos escaneadas, nombres de archivo y clic en seguir). Mezcla a −14 LUFS.", "",
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
