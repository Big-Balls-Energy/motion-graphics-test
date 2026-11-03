"""Valida subtítulos y cifras de timeline.json y escribe guion-con-tiempos.md y subtitulos.srt.

Uso (desde matbarre-studio/ o matbarre-studio/precio/): python3 tools/guion.py tools/timeline.json
Reglas: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s; «@matbarre_mx» ≥ 3 s sola;
0.5 s sin subtítulo al final de cada escena."""
import json, sys
TL = json.load(open(sys.argv[1]))
def ts(x): return f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"

# voz en off: una toma independiente por bloque (Fernanda, eleven_v4), colocada por voz-tools/voz_tomas.py matbarre-studio (y matbarre-studio/precio)
import os
PRECIO = 'precio' in os.path.abspath(sys.argv[1])
VOZ = [(0.60, 6.92, '[warmly] En diez sesiones lo sientes. En veinte lo ves. Y en treinta… tienes un cuerpo nuevo.'),
       (7.50, 11.00, '[warmly] Eso decía Joseph Pilates, hace casi cien años.'),
       (11.60, 16.23, '[warmly] Hoy, en Orizaba, esa filosofía tiene un nombre: Matbarre Studio.'),
       (16.70, 19.24, '[warmly] Más que movimiento… es tu momento.'),
       (20.00, 25.05, '[warmly] Barre: inspirado en el ballet, para ganar resistencia, equilibrio y postura.'),
       (26.00, 31.14, '[warmly] Pilates: fuerza desde tu centro, con precisión y conexión cuerpo-mente.'),
       (32.00, 36.33, '[warmly] Y Sculpt: para tonificar todo tu cuerpo, con fuerza y ritmo.'),
       (37.40, 39.97, '[warmly] Y lo mejor… la ciencia lo respalda.'),
       (40.50, 45.63, '[warmly] Una revisión de diez estudios encontró que el pilates puede aliviar el dolor de espalda baja.'),
       (46.40, 50.91, '[warmly] Y en mujeres, se asocia con más fuerza, flexibilidad y equilibrio.'),
       (51.50, 56.43, '[warmly] Además, la OMS recomienda entrenar fuerza al menos dos días por semana.'),
       (57.20, 62.50, '[warmly] En Matbarre te guían instructoras especializadas: Pao, Mirey (Mireille), Ana y Liz.'),
       (63.10, 67.65, '[warmly] Cuidan tu técnica en cada movimiento… para que avances segura, a tu ritmo.'),
       (68.60, 72.21, '[warmly] Y tu primera clase… cuesta solo ciento cincuenta pesos.') if PRECIO else
       (68.60, 73.37, '[warmly] Clases de barre, pilates y sculpt, de lunes a sábado, en el centro de Orizaba.'),
       (74.20, 78.01, '[warmly] Reserva tu clase en línea… y comparte esto con tu amiga de pilates.'),
       (78.90, 83.50, '[warmly] Síguenos en Instagram: arroba matbarre, guion bajo, eme equis.'),
       (84.00, 87.44, '[warmly] Matbarre Studio. Bienvenida a tu era de bienestar.')]
NOMBRE = 'Matbarre_Studio_Promo' + ('_Clase_Prueba' if PRECIO else '')

out = ["# Guion con tiempos — Matbarre Studio (video promocional, 90 s" + (", versión con clase de prueba $150)" if PRECIO else ", versión sin precios)"), "",
       f"Video: `{NOMBRE}.mp4` (con voz de Fernanda) y `{NOMBRE}-sin-voz.mp4` · 1080×1920 · 30 fps · 90 s · H.264 + AAC · "
       "música ambiental elegante a 80 BPM (30 compases exactos, el loop cierra): pads, kalimba, campanas, shaker suave, sin batería; "
       "efectos suaves sincronizados (campanas, brisa, toques y clic en Seguir). Mezcla a −14 LUFS.", "",
       "**Cómo leer:** cada fila es lo que aparece en pantalla; los subtítulos son una versión condensada de la voz. *(pausa)* es medio segundo sin subtítulo entre escenas. "
       "**[SOLA EN PANTALLA]** es el usuario @matbarre_mx, sin subtítulo encima.", ""]
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
