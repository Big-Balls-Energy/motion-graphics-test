"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde jensen-huang/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «LÍDER» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py jensen-huang
VOZ = [(0.15, 6.72, '[intrigued] Limpiaba baños… lavaba platos… y hoy dirige una empresa de casi seis billones de dólares.'),
       (7.50, 11.43, 'Se llama Jensen Huang… y su historia empieza con un error.'),
       (12.30, 20.29, 'A los nueve años lo mandaron de Taiwán a Estados Unidos… a una escuela en Kentucky que en realidad era un internado para jóvenes problemáticos.'),
       (20.60, 23.37, 'Ahí limpiaba baños… todos los días.'),
       (24.00, 28.27, "A los quince trabajó en Denny's: lavaplatos, garrotero y mesero."),
       (28.90, 35.89, "En mil novecientos noventa y tres, en una mesa de un Denny's, fundó Nvidia con dos amigos… y seiscientos dólares."),
       (36.60, 40.45, '[serious] Casi quiebra: llegó a tener dinero para un solo mes de nómina.'),
       (41.40, 46.95, '[excited] Lo salvó un chip… y después apostó por la computación que hoy mueve a la inteligencia artificial.'),
       (47.30, 50.71, 'Hoy Nvidia vale cerca de seis billones de dólares.'),
       (51.30, 56.81, 'Y a unos estudiantes de Stanford les dijo: [warmly] les deseo grandes dosis de dolor y sufrimiento.'),
       (57.30, 62.71, 'Porque, según él, la grandeza viene del carácter… y el carácter se forma sufriendo.'),
       (63.50, 67.44, '[warmly] ¿Tienes un negocio? Tus peores días también te están construyendo.'),
       (68.40, 70.09, '[excited] Comenta… ¡líder!'),
       (73.40, 77.16, 'Y te mando tres hábitos de Jensen Huang. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Jensen Huang: de lavar platos a Nvidia", "",
       "Video: `Atlas_Path_Jensen_Huang.mp4` (con voz de Fernanda) y `Atlas_Path_Jensen_Huang-sin-voz.mp4` · 1080×1920 · 30 fps · 80 s · H.264 + AAC · "
       "música electrónica a 117 BPM (39 compases exactos, el loop cierra), 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; "
       "efectos sincronizados (cortes del gancho, chip 3D que gira, ruta de avión, tarjeta que voltea a REFORMATORIO, mantel que se dibuja, calendario de nómina en cuenta regresiva, red neuronal, cita de Stanford, gráfica que cae y sube, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
