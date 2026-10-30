"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde blockbuster/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «CAMBIO» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py blockbuster
VOZ = [(0.18, 7.40, '[intrigued] Se rieron de una oferta de cincuenta millones de dólares… y hoy esa empresa vale más de doscientos cincuenta mil millones.'),
       (8.14, 14.14, 'En el año dos mil, Blockbuster era el rey de las películas en renta: miles de tiendas en todo el mundo.'),
       (15.04, 21.27, 'Ese año, los fundadores de Netflix volaron a Dallas para ofrecerles su empresa por cincuenta millones de dólares.'),
       (22.13, 25.00, '[dramatically] Y en la junta… casi se ríen de ellos.'),
       (25.93, 35.53, 'Netflix rentaba películas por correo, sin multas por retraso. Y las multas… eran parte del negocio de Blockbuster: unos ochocientos millones de dólares.'),
       (36.44, 42.06, 'En dos mil cuatro llegó a nueve mil tiendas. Seis años después… se declaró en quiebra.'),
       (42.94, 47.07, 'Hoy solo queda una tienda Blockbuster en el mundo, en Bend, Oregón.'),
       (47.94, 51.75, 'Y Netflix vale unos doscientos cincuenta mil millones de dólares.'),
       (52.64, 57.60, '[serious] La lección: Blockbuster no perdió por falta de dinero… perdió por no querer cambiar.'),
       (58.44, 62.59, 'Si tu cliente ya cambió… y tú no, alguien más va a ocupar tu lugar.'),
       (63.44, 64.80, '[excited] Comenta… ¡cambio!'),
       (68.34, 73.26, 'Y te mando cinco señales de que tu negocio necesita cambiar. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Blockbuster: se rieron de Netflix", "",
       "Video: `Atlas_Path_Blockbuster.mp4` (con voz de Fernanda) y `Atlas_Path_Blockbuster-sin-voz.mp4` · 1080×1920 · 30 fps · 74 s · H.264 + AAC · "
       "música electrónica a 116.8 BPM (36 compases exactos, el loop cierra), con pausas antes de cada cifra y capas de suspenso en la junta y en la quiebra; "
       "efectos sincronizados (videocasete 3D genérico, burbujas «JA JA», contadores $250,000 M, $800 M y 9,000, ruta en avión a Dallas, tarjeta de oferta con sello, sobre vs. ticket de multa, rejilla de tiendas que se apagan, gráfica de crecimiento, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
