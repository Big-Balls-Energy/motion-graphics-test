"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde ignite-studio/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «ENCIÉNDETE» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py ignite-studio
VOZ = [(0.24, 3.33, '[excited] ¿Y si tu mejor versión… empieza con una sola clase?'),
       (4.24, 9.28, 'Esto es Ignite Studio: cycling y entrenamiento funcional… aquí en Jalapa.'),
       (10.14, 13.40, 'Aquí no vienes solo a sudar… [excited] vienes a encenderte.'),
       (15.34, 19.71, 'Uno: tu salud. Cada clase fortalece tu corazón… y tus pulmones.'),
       (20.42, 25.12, 'Bajas el estrés, duermes mejor… y sales con más energía de la que trajiste.'),
       (26.61, 31.96, 'Dos: tu cuerpo. En la bici trabajas piernas y glúteos… pedalada tras pedalada.'),
       (32.74, 36.53, 'Y en las clases de fuerza defines brazos, espalda y abdomen.'),
       (38.04, 43.46, 'Tres: tu rendimiento. Más resistencia… más fuerza… [excited] más potencia.'),
       (44.24, 49.95, 'Pierna, empuje, jalón, cuerpo completo… y rodadas que te sacan todo.'),
       (51.44, 54.54, 'Pero lo mejor no se ve en el espejo… [warmly] es la gente.'),
       (55.33, 59.52, 'Coaches que te conocen por tu nombre… y te empujan a dar un poquito más.'),
       (62.44, 66.88, 'Aquí nadie entrena solo: aquí cada meta se celebra… juntos.'),
       (67.74, 71.60, 'Clases desde las seis de la mañana… entre semana y en fin de semana.'),
       (72.43, 75.92, 'Reserva tu lugar desde la app… y vive tu primera clase.'),
       (76.64, 79.63, 'Etiqueta a la persona con la que vendrías a tu primera clase.'),
       (80.64, 84.57, 'Ignite Studio. Plaza Xanat, Jalapa. [warmly] Enciéndete.')]

out = ["# Guion con tiempos — Ignite Studio (video promocional, 90 s)", "",
       "Video: `Ignite_Studio_Promo.mp4` (con voz de Fernanda) y `Ignite_Studio_Promo-sin-voz.mp4` · 1080×1920 · 30 fps · 90 s · H.264 + AAC · "
       "música electrónica deportiva a 138.7 BPM (52 compases exactos, el loop cierra); "
       "efectos sincronizados (golpes de sección, latidos, medidores, tarjetas de clases, espejo que se rompe, muro de coaches, app de reservas, comentario y clic en seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla; los subtítulos son una versión condensada de la voz. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es la frase de cierre, sin subtítulo encima. Las cifras se quedan al menos 2 s.", ""]
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
