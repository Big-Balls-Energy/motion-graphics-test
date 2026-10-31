"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde la carpeta del reel): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; cifras y números de consejo ≥ 2 s; la frase clave y «WEB» ≥ 3 s solas;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Joaquín, eleven_v4), colocada por voz-tools/voz_tomas.py clientes/vanguardia-academics/curva-del-olvido
VOZ = [(0.30, 3.79, '[curious] ¿Cuánto de lo que estudias hoy… seguirá ahí mañana?'),
       (6.80, 14.85, 'En mil ochocientos ochenta y cinco, el psicólogo alemán Hermann Ebbinghaus memorizó listas de sílabas sin sentido…'),
       (15.20, 18.98, '[intrigued] …para medir algo que nadie había medido: el olvido.'),
       (20.60, 24.74, 'Veinte minutos después, ya se le había escapado casi la mitad.'),
       (25.40, 28.85, 'Al día siguiente, conservaba apenas un tercio.'),
       (29.60, 32.40, '[serious] Y al mes, solo una quinta parte.'),
       (36.80, 39.85, '[intrigued] Pero hay recuerdos que no siguen esa curva.'),
       (42.30, 47.27, 'Los que llevan emoción: lo que nos sorprende se graba con más fuerza.'),
       (50.30, 56.54, 'Los que llevan acción: lo que hacemos con las manos se recuerda mejor que lo que solo leemos.'),
       (58.80, 60.69, 'Y los que volvemos a recordar.'),
       (61.20, 68.23, 'En un experimento, quienes se pusieron a prueba recordaron el sesenta y uno por ciento una semana después…'),
       (68.50, 71.00, '…quienes solo releyeron, el cuarenta.'),
       (72.30, 79.80, '[warmly] Un viaje académico bien diseñado junta las tres: emoción, acción… y momentos para volver a lo vivido. (acelerada 0.8 %)'),
       (80.00, 83.14, 'No es un paseo… es una clase que se queda.'),
       (84.20, 87.97, '[warmly] Guárdalo, y compártelo con quien diseña los viajes de tu escuela.')]

out = ["# Guion con tiempos — La curva del olvido (Vanguardia Academics)", "",
       "Video: `Vanguardia_Curva_del_Olvido.mp4` (con voz) y `Vanguardia_Curva_del_Olvido-sin-voz.mp4` · 1080×1920 · 30 fps · 90 s · H.264 + AAC · "
       "voz masculina «Joaquín – Rich and Captivating» (ElevenLabs) · música cinematográfica ligera a 96 BPM (36 compases exactos, el loop cierra): "
       "La menor mientras la curva cae y Do mayor desde las tres llaves; 15.5 % con texto / 19 % sin texto, con pausas antes de cada cifra; efectos sincronizados "
       "(hoja que se desintegra, máquina de escribir y cronómetro, la curva que cae, latido, barras de cristal, orbes que se funden, logo que se arma y clic en seguir). Mezcla a −14 LUFS.", "",
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

out += ["## Voz en off (Joaquín – Rich and Captivating, `eleven_v4`): una toma independiente por bloque", "",
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
