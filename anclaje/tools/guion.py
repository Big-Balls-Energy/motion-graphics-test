"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde anclaje/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «ANCLA» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py anclaje
VOZ = [(0.19, 4.04, '[intrigued] Un número al azar… puede cambiar lo que estás dispuesto a pagar.'),
       (4.82, 11.34, 'En mil novecientos setenta y cuatro, los psicólogos Tversky y Kahneman hicieron girar una ruleta frente a un grupo de personas.'),
       (12.14, 15.42, 'La ruleta caía en diez… o en sesenta y cinco.'),
       (16.44, 20.56, 'Luego preguntaron: ¿qué porcentaje de los países de la ONU son africanos?'),
       (21.44, 28.26, '[dramatically] Los que vieron el diez dijeron veinticinco por ciento. Los que vieron el sesenta y cinco… dijeron cuarenta y cinco.'),
       (29.22, 32.71, 'Un número sin ninguna relación… movió su respuesta.'),
       (33.62, 38.06, 'Se llama anclaje: el primer número que ves… se vuelve tu referencia.'),
       (39.04, 43.16, '¿Cómo usarlo en tu negocio? Uno: muestra primero tu paquete más caro.'),
       (44.01, 48.93, 'Dos: enseña el precio original junto al precio con descuento… solo si es real.'),
       (49.84, 52.93, 'Tres: en una negociación, di tu número primero.'),
       (53.84, 55.35, '[excited] Comenta… ¡ancla!'),
       (58.84, 63.84, 'Y te mando tres ejemplos de precios ancla para tu menú o tu tienda. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Anclaje: el experimento de la ruleta (1974)", "",
       "Video: `Atlas_Path_Anclaje.mp4` (con voz de Fernanda) y `Atlas_Path_Anclaje-sin-voz.mp4` · 1080×1920 · 30 fps · 65 s · H.264 + AAC · "
       "música electrónica a 118.2 BPM (32 compases exactos, el loop cierra), con pausas antes de cada cifra; "
       "efectos sincronizados (ruletas 3D que se detienen en 10 y 65, etiqueta de precio que cambia, pregunta de la ONU, barras 25 % vs 45 %, sello SIN NINGUNA RELACIÓN, ancla que cae, paquetes de precios, precio tachado, globos de negociación, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
