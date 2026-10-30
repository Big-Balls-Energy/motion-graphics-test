"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde sara-blakely/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «IDEA» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py sara-blakely
VOZ = [(0.16, 6.84, '[intrigued] Reprobó un examen, vendía fax de puerta en puerta… y creó una marca de mil doscientos millones de dólares.'),
       (7.63, 14.45, 'Se llama Sara Blakely. Durante siete años vendió máquinas de fax… y la rechazaban una y otra vez.'),
       (15.24, 21.41, 'Un día, antes de una fiesta, le cortó los pies a unas medias… para que su pantalón blanco se viera mejor.'),
       (22.13, 27.71, '[excited] Ahí nació su idea. Con cinco mil dólares de ahorros, empezó su propia marca: Spanx.'),
       (28.53, 32.84, 'Las fábricas le decían que no… hasta que una aceptó fabricar su prototipo.'),
       (33.64, 38.87, 'Para convencer a la compradora de una tienda de lujo, se cambió en el baño… y le mostró el resultado.'),
       (39.64, 45.23, 'En el año dos mil, Oprah la eligió entre sus cosas favoritas… y las ventas explotaron.'),
       (45.93, 51.21, 'En dos mil doce, Forbes la nombró la mujer más joven en hacerse milmillonaria por sí sola.'),
       (51.94, 57.71, 'Y en dos mil veintiuno vendió la mayoría de su empresa, con un valor de mil doscientos millones de dólares.'),
       (58.44, 64.37, '[warmly] La lección: no necesitas un gran inversionista… necesitas resolver un problema que tú misma vives.'),
       (65.10, 66.61, '[excited] Comenta… ¡idea!'),
       (70.14, 74.70, 'Y te mando cinco preguntas para validar tu idea de negocio. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Sara Blakely: de vender fax a una marca de $1,200 M", "",
       "Video: `Atlas_Path_Sara_Blakely.mp4` (con voz de Fernanda) y `Atlas_Path_Sara_Blakely-sin-voz.mp4` · 1080×1920 · 30 fps · 76 s · H.264 + AAC · "
       "música electrónica a 116.8 BPM (37 compases exactos, el loop cierra), con pausas antes de cada cifra; "
       "efectos sincronizados (foco 3D que se enciende, sellos «NO», tijera y medias, contador $5,000, fábricas con ✗, puerta del baño y sello ¡ACEPTADO!, televisor con estrellas, barras de ventas, anillos dorados, gráfica circular, contador $1,200 M, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
