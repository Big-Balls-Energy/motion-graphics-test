"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde efecto-ikea/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «CREAR» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py efecto-ikea
VOZ = [(0.15, 4.11, '[intrigued] ¿Por qué pagarías más por un mueble… que tú mismo armaste?'),
       (5.00, 10.20, 'Se llama efecto IKEA: valoramos más lo que construimos con nuestras propias manos.'),
       (11.10, 19.48, 'En un estudio de investigadores de Harvard, Yale y Duke, quienes armaron una caja de IKEA estaban dispuestos a pagar sesenta y tres por ciento más.'),
       (20.50, 27.46, 'Con figuras de origami fue aún más fuerte: ofrecían unas cinco veces más por la suya… aunque fuera de principiante.'),
       (28.60, 33.88, '[serious] Pero ojo: solo funciona si lo terminas. Si no se completa, el efecto desaparece.'),
       (35.10, 39.90, 'Por eso hay tiendas donde armas tu propio oso de peluche… y lo pagas con gusto.'),
       (40.90, 44.19, '¿Cómo usarlo en tu negocio? Deja que tu cliente participe.'),
       (45.20, 49.58, 'Uno: que personalice. Colores, nombre, su propia combinación.'),
       (50.70, 55.70, 'Dos: que dé un paso fácil. Un cuestionario, un diseño, una elección.'),
       (56.60, 60.57, 'Tres: que termine algo. Celebra cada paso completado.'),
       (61.50, 64.56, '[warmly] Lo que tu cliente ayuda a crear… lo valora más.'),
       (65.90, 67.50, '[excited] Comenta… ¡crear!'),
       (70.90, 75.31, 'Y te mando cinco ideas para que tus clientes participen. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — El efecto IKEA", "",
       "Video: `Atlas_Path_Efecto_IKEA.mp4` (con voz de Fernanda) y `Atlas_Path_Efecto_IKEA-sin-voz.mp4` · 1080×1920 · 30 fps · 76 s · H.264 + AAC · "
       "música electrónica a 116.8 BPM (37 compases exactos, el loop cierra), 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; "
       "efectos sincronizados (repisa 3D que se arma sola, etiqueta de precio, barras +63 %, grulla de origami que se dobla, tache y palomita, corazón cosido, taza que cambia de color, cuestionario, pasos con confeti, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
