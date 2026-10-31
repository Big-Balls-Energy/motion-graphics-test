"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde la carpeta del reel): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras y números de consejo ≥ 2 s; la frase clave y «WEB» ≥ 3 s solas;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py clientes/vanguardia-academics/antes-de-firmar
VOZ = [(0.30, 4.20, '[curious] Tu hijo llega a casa con un permiso para un viaje escolar al extranjero…'),
       (4.60, 7.50, 'Antes de firmarlo, haz estas cinco preguntas.'),
       (8.30, 14.52, 'Uno: ¿qué va a aprender? Un viaje académico tiene objetivos claros, conectados con su programa de estudios.'),
       (16.30, 22.34, 'Dos: ¿quién lo acompaña? Pregunta cuántos adultos van por grupo… y quién está disponible de noche.'),
       (23.90, 30.39, 'Tres: ¿qué cubre el seguro? Gastos médicos, hospital… y, si hace falta, el regreso anticipado.'),
       (31.60, 38.68, 'Cuatro: ¿cuál es el plan si algo sale mal? Debe existir un protocolo por escrito y un teléfono activo las veinticuatro horas.'),
       (39.90, 48.09, 'Y cinco: los documentos. Si viaja con la escuela y sin ustedes, necesita el formato de salida de menores del Instituto Nacional de Migración…'),
       (48.30, 53.05, 'además de su pasaporte y, según el destino, visa o permiso electrónico.'),
       (55.50, 60.68, '[warmly] Un buen viaje no se improvisa: estas respuestas deberían llegar por escrito, antes de salir.'),
       (61.00, 63.88, 'Cuando todo está claro… firmar es fácil.'),
       (64.60, 67.22, '[warmly] Guárdalo… y mándaselo al grupo de papás.')]

out = ["# Guion con tiempos — Antes de firmar el permiso (Vanguardia Academics)", "",
       "Video: `Vanguardia_Antes_de_Firmar.mp4` (con voz) y `Vanguardia_Antes_de_Firmar-sin-voz.mp4` · 1080×1920 · 30 fps · 75 s · H.264 + AAC · "
       "voz de Fernanda (ElevenLabs) · música cálida a 96 BPM (30 compases exactos, el loop cierra), piano, pads y percusión suave; 15.5 % con texto / 19 % sin texto; "
       "efectos sincronizados (mensajes del chat, palomitas, papel, números, sello, pluma que firma, enviar y clic en seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es una frase clave sin subtítulo encima. Las cifras y los números de pregunta se quedan al menos 2 s.", ""]
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
