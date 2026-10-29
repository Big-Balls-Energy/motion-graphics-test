"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde consejos-ia/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras y números de consejo ≥ 2 s; la frase clave y «WEB» ≥ 3 s solas;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py consejos-ia
VOZ = [(0.20, 2.67, '[curious] ¿Creías que las páginas web estaban muriendo?'),
       (2.89, 5.90, 'La IA les dio una nueva razón para existir.'),
       (6.45, 13.86, 'En tiendas en línea de Estados Unidos, las visitas que llegan desde una IA crecieron más de mil doscientos por ciento desde dos mil veinticuatro. (acelerada 6 %)'),
       (14.07, 17.16, '[excited] Y terminan en compra un sesenta por ciento más.'),
       (17.73, 22.06, 'Cada vez más gente le pregunta a ChatGPT o a Gemini qué negocio elegir. (acelerada 2.9 %)'),
       (22.50, 25.87, 'Ya no basta con que te encuentren… [excited] tienen que recomendarte.'),
       (26.54, 29.85, 'Uno: un sitio rápido y que los buscadores puedan leer.'),
       (30.25, 33.87, 'Si bloqueas sus rastreadores, la IA no puede citarte.'),
       (34.43, 39.06, 'Dos: di claramente qué vendes, dónde estás y por qué elegirte. (acelerada 2.5 %)'),
       (39.28, 41.64, 'Y completa tu perfil de negocio en Google.'),
       (42.19, 46.94, 'Tres: responde las preguntas reales de tus clientes, con datos y fuentes. (acelerada 1 %)'),
       (47.16, 52.21, 'En un estudio de Princeton, eso aumentó la visibilidad en IA hasta un cuarenta por ciento. (acelerada 5 %)'),
       (52.75, 54.42, 'Cuatro: reputación.'),
       (54.78, 61.08, 'Las IA suelen citar más lo que otros dicen de ti que tu propio sitio: consigue reseñas reales y menciones. (acelerada 4 %)'),
       (61.63, 65.43, 'Cinco: mantén tu información al día y mide tus resultados.'),
       (67.11, 70.65, '[warmly] El futuro no es solo que te encuentren: es que te recomienden.'),
       (70.95, 72.13, '[excited] Comenta web…'),
       (75.50, 77.67, 'y te decimos qué mejorar en tu sitio.'),
       (77.82, 79.40, '[warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — 5 consejos para que una IA recomiende tu negocio", "",
       "Video: `Atlas_Path_5_Consejos_IA.mp4` (con voz) y `Atlas_Path_5_Consejos_IA-sin-voz.mp4` · 1080×1920 · 30 fps · 80 s · H.264 + AAC · "
       "música electrónica cinematográfica a 117 BPM (39 compases exactos, el loop cierra), 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; "
       "efectos sincronizados (impacto del hook y de «a ser recomendado», partículas que se deshacen y se reconstruyen, clics y barridos de interfaz, "
       "escaneo del rastreador, tarjetas, acento en cada número, medidor que sube, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es la frase clave o la palabra clave, sin subtítulo encima. Las cifras y los números de consejo se quedan al menos 2 s.", ""]
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

out += ["## Voz en off (Fernanda – Smooth and Articulate, `eleven_v4`): una toma independiente por bloque", "",
        "Los subtítulos son una versión condensada de la voz para cumplir la regla de lectura (3–5 palabras, ≤ 2.3 palabras/s). "
        "Ninguna toma se cortó: cada bloque se grabó por separado y solo se acortaron silencios.", "",
        "| Bloque | Entra – sale | Texto grabado |", "|---|---|---|"]
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
