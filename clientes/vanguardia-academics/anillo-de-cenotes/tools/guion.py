"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde la carpeta del reel): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras y números de consejo ≥ 2 s; la frase clave y «WEB» ≥ 3 s solas;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque («Rayito», eleven_v4), colocada por voz-tools/voz_tomas.py clientes/vanguardia-academics/anillo-de-cenotes
VOZ = [(0.25, 4.87, '[excited] ¿Sabías que el asteroide que acabó con los dinosaurios… cayó aquí, en Yucatán?'),
       (6.80, 13.21, 'Hace sesenta y seis millones de años, una roca de unos diez kilómetros se estrelló contra el mar. (acelerada 1 %)'),
       (14.20, 19.39, 'Abrió un cráter de unos ciento ochenta kilómetros… que hoy está enterrado.'),
       (19.80, 23.49, '[intrigued] Pero dejó una huella que se descubrió desde el espacio:'),
       (23.80, 27.20, 'un anillo de cenotes que sigue el borde del cráter.'),
       (28.80, 33.81, 'En una tierra casi sin ríos, esos pozos fueron el agua de los mayas…'),
       (34.60, 39.21, 'y Chichén Itzá lleva su nombre: la boca del pozo de los itzáes.'),
       (40.80, 43.70, '[excited] Un solo lugar… cinco materias:'),
       (44.40, 49.90, 'física… geología… biología… historia… y geografía.'),
       (51.80, 54.19, 'Eso no cabe en un libro de texto.'),
       (56.30, 58.60, '[warmly] Cabe en un viaje bien diseñado. (acelerada 1.9 %)'),
       (60.80, 65.22, 'Mándaselo a quien todavía cree que la historia solo se aprende en el salón.')]

out = ["# Guion con tiempos — El anillo de cenotes (Vanguardia Academics)", "",
       "Video: `Vanguardia_Anillo_de_Cenotes.mp4` (con voz) y `Vanguardia_Anillo_de_Cenotes-sin-voz.mp4` · 1080×1920 · 30 fps · 70 s · H.264 + AAC · "
       "voz masculina «Rayito» (ElevenLabs, divulgación científica) · música cinematográfica a 96 BPM (28 compases exactos, el loop cierra), de Mi menor a Sol mayor, "
       "15.5 % con texto / 19 % sin texto, con caída antes del impacto, «1 lugar» y la frase final; efectos sincronizados (espacio, meteorito, impacto con escombros, "
       "capas de roca, escaneo satelital, puntos del anillo, agua del cenote, fichas que giran, golpes de texto, barridos, libro que se cierra y obturador de cámara). Mezcla a −14 LUFS.", "",
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

out += ["## Voz en off («Rayito», `eleven_v4`): una toma independiente por bloque", "",
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
