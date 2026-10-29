"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde ocarina-nostalgia/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s solas; «NOSTALGIA» ≥ 3 s sola; títulos de acto ≥ 1.5 s;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Joaquín, eleven_v4), colocada por voz-tools/voz_tomas.py ocarina-nostalgia
VOZ = [(0.12, 5.56, '[excited] Si tienes entre 30 y 45 años, este juego probablemente marcó tu infancia. (acelerada 8.4 %)'),
       (6.30, 10.71, '[excited] Soy Guillermo Arcos, de Atlas Path… ¡y hoy nos vamos de aventura! (acelerada 6.3 %)'),
       (11.40, 14.90, '[warmly] Ocarina of Time salió en 1998… (acelerada 5.1 %)'),
       (15.05, 20.69, '[excited] y sigue siendo el juego mejor calificado de la historia en Metacritic: ¡99 de 100! (acelerada 4.4 %)'),
       (21.40, 24.84, 'Vendió más de 7.6 millones de copias… (acelerada 5.9 %)'),
       (25.00, 30.51, 'y en Estados Unidos tuvo tres veces más preventas que cualquier otro juego de su época. (acelerada 5.8 %)'),
       (31.25, 35.56, '[dramatically] Ahora, 28 años después… Nintendo lo relanza: (acelerada 5.5 %)'),
       (35.71, 39.12, '[excited] un remake para Switch 2 que sale este 5 de noviembre. (acelerada 5.9 %)'),
       (39.80, 46.50, 'Con gráficos nuevos, música orquestal, voces… ¡y hasta puedes tocar la ocarina tarareando al micrófono! (acelerada 6 %)'),
       (47.60, 51.23, '[dramatically] Pero toda marca tiene un jefe final… el olvido.'),
       (52.80, 55.30, '[excited] Y la nostalgia es tu mejor arma. (acelerada 5.5 %)'),
       (55.50, 62.90, 'Un estudio del Journal of Consumer Research encontró que, cuando sentimos nostalgia, estamos dispuestos a pagar más. (acelerada 5.9 %)'),
       (64.45, 70.90, '[warmly] Nintendo lo sabe: vende recuerdos a quien lo jugó de niño… y una primera aventura a sus hijos. (acelerada 1.4 %)'),
       (71.60, 77.28, '[curious] ¿Tu negocio? Encuentra lo que hacía feliz a tu cliente hace 20 años… y tráelo de vuelta. (acelerada 4.7 %)'),
       (78.00, 81.94, '[excited] Comenta NOSTALGIA, y te ayudamos a crear tu propia campaña. (acelerada 1.1 %)'),
       (82.10, 83.97, '[warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Ocarina of Time: la nostalgia es tu mejor arma", "",
       "Video: `Atlas_Path_Ocarina_Nostalgia.mp4` (con voz) y `Atlas_Path_Ocarina_Nostalgia-sin-voz.mp4` · 1080×1920 · 30 fps · 90 s · H.264 + AAC · "
       "música original a 101.33 BPM (38 compases exactos, el loop cierra) que cambia con cada acto: chiptune de 8 bits (acto 1) → orquesta (acto 2) → "
       "batalla con 1 s de silencio antes del golpe final (acto 3) → tema heroico (epílogo). Queda al 15.5 % con texto y al 19 % sin texto, "
       "con pausas antes de cada cifra; efectos sincronizados (tele CRT que se enciende y se apaga, cartucho, portal, notas genéricas de ocarina, "
       "estática y rugido del jefe, impactos, cofre, píxeles, teclado, clic y fanfarria). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es una cifra o la palabra clave, sin subtítulo encima: las cifras se quedan al menos 2 s, "
       "«JEFE FINAL: EL OLVIDO» y los títulos de acto 1.5 s, y «NOSTALGIA» 3 s.", ""]
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
            rows.append((s['a'], f"| {ts(s['a'])} | {ts(s['b'])} | *título en pantalla:* **{s['text']}** | {d:.1f} s |"))
    if sc['id'] != 'cta': rows.append((sc['b'] - .5, f"| {ts(sc['b'] - .5)} | {ts(sc['b'])} | *(pausa)* | — |"))
    rows.sort(key=lambda r: r[0]); out += [r for _, r in rows]; out.append("")

out += ["## Voz en off (Joaquín – Rich and Captivating, `rtQzMJmQhSg0YB7cp3ed`, `eleven_v4`): una toma independiente por bloque", "",
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
