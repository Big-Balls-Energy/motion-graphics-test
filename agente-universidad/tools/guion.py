"""Escribe guion-con-tiempos.md y subtitulos.srt a partir de tools/plan.json y tools/timeline.json.

Uso (desde agente-universidad/): python3 tools/guion.py"""
import json
P = json.load(open('tools/plan.json')); TL = json.load(open('tools/timeline.json'))
ts = lambda x: f"{int(x // 60):02d}:{x % 60:05.2f}"
def srt(x): ms = int(round(x * 1000)); return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"
W = P['words']; SEC = TL['sections']
NOMBRES = {'hook': 'Gancho: mensajes sin responder = ventas perdidas', 'imagina': '«Ahora imagina»: tareas que se amontonan',
           'agente': 'Atlas Path y su agente de IA', 'caso': 'Caso real: el agente de la universidad', 'beneficio': 'Beneficio: menos tareas, más cierres',
           'cta': 'Llamada a la acción y cierre de Atlas Path'}
VIS = {'hook': 'Título «¿PIERDES VENTAS?» detrás de su cabeza; notificaciones que se acumulan (contador 99+), se quedan «Sin responder» y «Seguimiento pendiente»; gráfica de ventas que cae.',
       'imagina': 'Las tareas aparecen al decirlas (contestar preguntas, recopilar datos, mandar información, agendar citas) y luego se amontonan con más pendientes hasta «SATURADO».',
       'agente': 'Etiqueta «ATLAS PATH · Automatización con IA», título «AGENTE IA» detrás de ella y las cuatro tareas resueltas con ✓.',
       'caso': 'Píldora «CASO REAL · UNIVERSIDAD»; teléfono con la conversación del agente (chat ilustrativo), registro en la base de datos, visita agendada y el prospecto que pasa a «Visita agendada» en el sistema del equipo comercial.',
       'beneficio': 'Resumen para guardar «TU AGENTE IA:» con 7 funciones, «TAREAS REPETITIVAS» tachado, «LO MÁS IMPORTANTE» detrás de ella y sello «VENTA CERRADA» con confeti.',
       'cta': '«¿CÓMO LO HACEMOS?», toque en pantalla, tarjeta de cierre con logo, @Atlas_Path, ESCRÍBENOS y SEGUIR → SIGUIENDO ✓; el último medio segundo regresa al primer cuadro (loop).'}
out = ['# Guion con tiempos — Agente de IA para una universidad (Atlas Path)', '',
       f"Video: `Atlas_Path_Agente_IA_Universidad.mp4` (con música) y `Atlas_Path_Agente_IA_Universidad-sin-musica.mp4` · 1080×1920 · 30 fps · {P['dur']:.2f} s · "
       "H.264 + AAC · −14 LUFS. Voz original de la persona del video, con las pausas largas recortadas (el original dura 55.77 s). "
       "Música original a 123 BPM (28 compases exactos: el loop cierra) y efectos sincronizados.", '',
       '**Subtítulos literales:** son las palabras exactas, palabra por palabra, en bloques de 1 a 5 palabras. Ella habla a unas 3.3 palabras por segundo, '
       'así que no se cumple el tope de 2.3 palabras/s de los reels narrados; resumirlos haría que no coincidieran con lo que dice. '
       'Scribe transcribió «Atlas Pad»; en pantalla va «Atlas Path».', '']
srt_rows = []
for k, (key, (a, b)) in enumerate(SEC.items()):
    out += [f'## {ts(a)} – {ts(b)} · {NOMBRES[key]}', '', f'_Gráficos: {VIS[key]}_', '', '| Entra | Sale | Subtítulo |', '|---|---|---|']
    for blk in P['blocks']:
        if a - 1e-6 <= blk['a'] < b - 1e-6:
            text = ' '.join(W[i]['t'] for i in blk['w'])
            out.append(f"| {ts(blk['a'])} | {ts(blk['b'])} | {text} |")
    out.append('')
for n, blk in enumerate(P['blocks'], 1):
    srt_rows.append(f"{n}\n{srt(blk['a'])} --> {srt(blk['b'])}\n{' '.join(W[i]['t'] for i in blk['w'])}\n")
out += ['## Transcripción completa', '', ' '.join(w['t'] for w in W), '']
open('guion-con-tiempos.md', 'w').write('\n'.join(out)); open('subtitulos.srt', 'w').write('\n'.join(srt_rows))
print('bloques', len(P['blocks']), 'secciones', len(SEC))
