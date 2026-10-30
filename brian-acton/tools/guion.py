"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde brian-acton/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «IDEA» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py brian-acton
VOZ = [(0.16, 6.15, '[intrigued] Facebook no quiso contratarlo… cinco años después, le pagó diecinueve mil millones de dólares.'),
       (6.92, 13.78, 'Se llama Brian Acton. Trabajó once años en Yahoo, y en dos mil siete renunció para tomarse un año sabático.'),
       (14.63, 19.84, 'En dos mil nueve buscó trabajo: Twitter le dijo que no. Y en agosto… Facebook también.'),
       (20.64, 25.25, 'Escribió en Twitter: «Facebook me rechazó… espero con ganas la próxima aventura».'),
       (26.04, 31.95, 'Ese mismo año se unió a su excompañero Jan Koum, que estaba creando una app de mensajes: WhatsApp.'),
       (32.74, 37.45, 'Sin anuncios, sin juegos, sin trucos. Solo mensajes que funcionaban.'),
       (38.23, 44.71, 'Y en dos mil catorce, la misma empresa que lo rechazó… [surprised] la compró por diecinueve mil millones de dólares.'),
       (45.53, 51.12, 'La lección: un «no» no es el final. A veces es la señal para construir lo tuyo.'),
       (51.94, 53.43, '[excited] Comenta… ¡idea!'),
       (57.32, 62.14, 'Y te mando cómo validar tu idea de negocio en siete días. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Brian Acton: Facebook lo rechazó y luego le pagó US$19,000 millones", "",
       "Video: `Atlas_Path_Brian_Acton.mp4` (con voz de Fernanda) y `Atlas_Path_Brian_Acton-sin-voz.mp4` · 1080×1920 · 30 fps · 63 s · H.264 + AAC · "
       "música electrónica a 106.7 BPM (28 compases exactos, el loop cierra); "
       "efectos sincronizados (solicitud de empleo con sello RECHAZADO, línea de tiempo 1996–2007, dos sellos «NO», publicación que se escribe letra por letra, dos siluetas, nota «SIN…» tachada, chat genérico, contador de US$19,000 millones, bloques que se apilan y clic en seguir). Mezcla a −14 LUFS.", "",
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
