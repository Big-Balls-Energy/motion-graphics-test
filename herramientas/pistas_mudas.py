"""Crea musica-sola.wav y efectos-solos.wav en silencio para poder correr voz_tomas.py antes de tener la música
(sirve para colocar la voz y sacar los tiempos del karaoke). audio.py las reemplaza después.

Uso: python3 herramientas/pistas_mudas.py <carpeta_reel> <duración_s>"""
import os, sys, wave
import numpy as np
d = os.path.join(sys.argv[1], 'audio'); os.makedirs(d, exist_ok=True); n = int(48000 * float(sys.argv[2]))
for name in ('musica-sola', 'efectos-solos'):
    with wave.open(os.path.join(d, name + '.wav'), 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(48000); w.writeframes(np.zeros(n * 2, '<i2').tobytes())
print('pistas mudas de', sys.argv[2], 's en', d)
