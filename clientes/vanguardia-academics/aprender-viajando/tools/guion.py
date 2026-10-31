"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde la carpeta del reel): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras y números de consejo ≥ 2 s; la frase clave y «WEB» ≥ 3 s solas;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py clientes/vanguardia-academics/aprender-viajando
VOZ = [(0.20, 2.77, '[curious] ¿Por qué recuerdas un viaje de hace años…'),
       (3.05, 5.25, '[intrigued] …y no la clase de la semana pasada?'),
       (6.30, 10.00, '[calm] Porque lo que vivimos en primera persona se aprende de otra manera.'),
       (10.25, 17.71, 'El investigador David Kolb lo llamó aprendizaje experiencial: vivir, reflexionar, entender… y aplicar.'),
       (18.70, 24.00, 'En Arkansas, casi once mil estudiantes entraron a un sorteo para visitar un museo de arte.'),
       (24.60, 30.19, '[warmly] Los que fueron mostraron más pensamiento crítico, más empatía histórica… y más tolerancia.'),
       (31.10, 37.16, 'En Atlanta, otro estudio sorteó tres salidas culturales al año: museo, teatro y orquesta.'),
       (37.50, 42.80, 'Esos alumnos faltaron menos a clases… y obtuvieron mejores resultados en sus exámenes. (acelerada 1.1 %)'),
       (43.60, 47.89, 'Y entre más de cuatro mil quinientos universitarios que estudiaron en el extranjero…'),
       (48.20, 55.50, '[inspired] más del setenta por ciento notó una gran mejora en habilidades interculturales, curiosidad, adaptabilidad y confianza. (acelerada 1.2 %)'),
       (56.30, 59.36, '[warmly] Por eso, cuando un viaje se diseña con intención…'),
       (59.60, 62.00, 'La historia se entiende frente a una pirámide. (acelerada 2.9 %)'),
       (62.30, 65.53, 'La sostenibilidad, dentro de una empresa que la practica.'),
       (65.90, 69.51, 'Y el emprendimiento, en una ciudad que vive en dos idiomas. (acelerada 2.4 %)'),
       (70.00, 71.87, '[inspired] …cada destino es un aula.'),
       (73.80, 79.33, '[softly] Y hay lecciones que ningún libro enseña: construir, junto a una comunidad, algo que se queda.'),
       (80.00, 81.80, '[warmly] Eso también es educación. (acelerada 2.8 %)'),
       (82.55, 85.65, '[warmly] Viajar abre las puertas a nuevos aprendizajes. (acelerada 3.3 %)'),
       (85.80, 89.35, 'Compártelo con quien organiza los viajes de tu escuela… y síguenos.')]

out = ["# Guion con tiempos — Aprender viajando (Vanguardia Academics)", "",
       "Video: `Vanguardia_Aprender_Viajando.mp4` (con voz) y `Vanguardia_Aprender_Viajando-sin-voz.mp4` · 1080×1920 · 30 fps · 90 s · H.264 + AAC · "
       "música cinematográfica ligera a 96 BPM en Re mayor (36 compases exactos, el loop cierra): piano, pads, cuerdas y percusión suave; 15.5 % con texto / 19 % sin texto, "
       "con pausas antes de cada cifra; efectos sincronizados (paredes del salón que caen, obturador y polaroid, nodos del ciclo, sorteo, boletos, rutas de vuelo, "
       "sellos de pasaporte, barridos entre fotos, puertas y clic en seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es una frase clave sin subtítulo encima. Las cifras se quedan al menos 2 s.", ""]
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
