"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde escasez/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «ESCASEZ» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py escasez
VOZ = [(0.19, 3.03, '[intrigued] ¿Por qué deseas más lo que está a punto de acabarse?'),
       (3.93, 12.93, 'En mil novecientos setenta y cinco, unos psicólogos le dieron a ciento treinta y cuatro personas un frasco con galletas… a unas con diez, a otras con solo dos.'),
       (13.83, 18.21, 'Las galletas del frasco con dos… se calificaron como más deseables.'),
       (19.14, 24.79, 'Pero lo más fuerte vino después: a algunos les cambiaron el frasco de diez… por uno de dos.'),
       (25.63, 31.79, '[dramatically] Esas galletas valieron todavía más… sobre todo cuando les dijeron que se acabaron porque otros las pidieron.'),
       (32.63, 38.04, 'Se llama escasez: lo que es poco, y lo que otros quieren, nos parece más valioso.'),
       (38.94, 41.52, '¿Cómo usarlo en tu negocio… sin mentir?'),
       (42.34, 46.51, 'Uno: ediciones limitadas de verdad. Pocas piezas y fecha de fin.'),
       (47.41, 52.30, 'Dos: muestra la demanda real. «Quedan cinco». «Doce personas lo están viendo».'),
       (53.24, 57.80, 'Tres: cupos reales. Agenda, grupos o lugares limitados.'),
       (58.64, 62.31, '[serious] Pero ojo: si la escasez es falsa, pierdes la confianza.'),
       (63.24, 64.88, '[excited] Comenta… ¡escasez!'),
       (68.34, 73.03, 'Y te mando diez frases de escasez que venden sin mentir. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Escasez: el experimento de las galletas", "",
       "Video: `Atlas_Path_Escasez.mp4` (con voz de Fernanda) y `Atlas_Path_Escasez-sin-voz.mp4` · 1080×1920 · 30 fps · 74 s · H.264 + AAC · "
       "música electrónica a 116.8 BPM (36 compases exactos, el loop cierra), con pausas antes de cada cifra y capas de suspenso al quitar las galletas y en la escasez falsa; "
       "efectos sincronizados (frascos 3D de vidrio con galletas, sello ¡QUEDAN 2!, rejilla de 134 personas, galletas que salen volando, podio de la demanda, ecuación de la escasez, ficha de edición limitada, «quedan 5», agenda que se llena, reloj falso que se reinicia, barra de confianza que se rompe, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
