"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde airbnb-cereal/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras ≥ 2 s; «CEREAL» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py airbnb-cereal
VOZ = [(0.15, 3.95, '[intrigued] Para salvar su empresa… vendieron cajas de cereal.'),
       (5.00, 10.12, 'En dos mil siete, Brian Chesky y Joe Gebbia no podían pagar la renta en San Francisco.'),
       (11.50, 16.58, 'Así que inflaron colchones en su sala… y se los rentaron a visitantes de una conferencia.'),
       (17.60, 23.25, 'Así nació Airbnb. Pero casi nadie lo usaba… y los inversionistas les decían que no.'),
       (24.30, 30.63, '[dramatically] Sin dinero, en dos mil ocho diseñaron cajas de cereal… inspiradas en los candidatos a la presidencia.'),
       (31.60, 36.55, 'Las vendieron a cuarenta dólares cada una… y juntaron treinta mil dólares.'),
       (37.30, 44.81, 'Eso convenció a Paul Graham: si lograron vender cereal a cuarenta dólares… podían convencer a la gente de dormir en casa de extraños.'),
       (46.00, 51.09, 'En dos mil nueve entraron a su aceleradora, Y Combinator, con veinte mil dólares.'),
       (52.00, 55.96, '[excited] Hoy Airbnb vale unos noventa y ocho mil millones de dólares.'),
       (56.70, 60.94, '[warmly] ¿La lección? Cuando nadie cree en ti… haz algo que no puedan ignorar.'),
       (62.30, 64.06, '[excited] Comenta… ¡cereal!'),
       (67.60, 72.90, 'Y te mando tres ideas creativas para conseguir tus primeros clientes. [warmly] Síguenos en Atlas Path.')]

out = ["# Guion con tiempos — Airbnb: vendieron cereal para salvar su empresa", "",
       "Video: `Atlas_Path_Airbnb_Cereal.mp4` (con voz de Fernanda) y `Atlas_Path_Airbnb_Cereal-sin-voz.mp4` · 1080×1920 · 30 fps · 76 s · H.264 + AAC · "
       "música electrónica a 116.8 BPM (37 compases exactos, el loop cierra), 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; "
       "efectos sincronizados (caja de cereal 3D que cae, sello RENTA VENCIDA, colchones que se inflan, sobres «NO, GRACIAS», cajas 3D de dos ediciones, etiqueta $40 y cajas que se multiplican, tarjeta de idea, contadores, teclado y clic en seguir). Mezcla a −14 LUFS.", "",
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
