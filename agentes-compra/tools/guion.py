"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde agentes-compra/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «AGENTE» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py agentes-compra
VOZ = [(0.15, 5.23, '[intrigued] Ya hay inteligencias artificiales que compran por ti… y Amazon les cerró la puerta.'),
       (6.20, 11.08, 'En septiembre, Amazon bloqueó en su tienda a Muse, el asistente de compras de Meta.'),
       (12.40, 20.90, 'Según Zuckerberg, más de diez millones de personas ya lo configuraron en Estados Unidos y Canadá… y su compra promedio supera los doscientos dólares.'),
       (22.40, 31.36, 'Esta semana, el director de Amazon, Andy Jassy, dijo que comprar con agentes externos todavía no es tan bueno… ni más cómodo que ir directo a la tienda.'),
       (33.00, 36.40, 'Mientras tanto, impulsa a su propio asistente de compras.'),
       (37.00, 40.80, 'Más de cuatrocientos millones de clientes lo usaron en el último año.'),
       (41.40, 45.98, '[excited] Y en Estados Unidos, quienes lo usan gastan cincuenta por ciento más por pedido.'),
       (46.60, 51.68, '[serious] La batalla ya no es solo por el cliente… es por la inteligencia artificial que compra por él.'),
       (52.80, 59.57, '¿Y tu negocio? Que tus productos tengan fotos, precios y descripciones claras… para que una IA los entienda.'),
       (60.40, 62.08, '[excited] Comenta… ¡agente!'),
       (66.20, 70.99, 'Y te mando cinco pasos para preparar tu tienda para la IA. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Amazon vs. los agentes de IA que compran por ti", "",
       "Video: `Atlas_Path_Agentes_Compra.mp4` (con voz de Fernanda) y `Atlas_Path_Agentes_Compra-sin-voz.mp4` · 1080×1920 · 30 fps · 72 s · H.264 + AAC · "
       "música electrónica a 116.7 BPM (35 compases exactos, el loop cierra), 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; "
       "efectos sincronizados (agente 3D de luz, muro rojo y sello ACCESO BLOQUEADO, tarjetas unidas por una línea que se corta con candado, contadores +10 M y +400 M, ticket +$200, cita traducida, chat genérico, barras +50 %, cuerda entre cliente e IA, ficha de producto escaneada, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
