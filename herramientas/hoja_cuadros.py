"""Hoja de contacto a partir de los cuadros ya renderizados (f_00000.jpg …) para revisar el movimiento completo.

Uso: python3 herramientas/hoja_cuadros.py <carpeta_cuadros> <salida.jpg> t0:t1:paso [t0:t1:paso ...] [--fps 30]
Ejemplo: python3 herramientas/hoja_cuadros.py /tmp/cuadros /tmp/hoja_0_20.jpg 0:19.5:0.5"""
import glob, os, sys
from PIL import Image, ImageDraw
args = [a for a in sys.argv[1:]]; fps = 30
if '--fps' in args: i = args.index('--fps'); fps = float(args[i + 1]); del args[i:i + 2]
d, out = args[0], args[1]; ts = []
for spec in args[2:]:
    a, b, st = map(float, spec.split(':')); t = a
    while t <= b + 1e-6: ts.append(round(t, 3)); t += st
last = len(glob.glob(os.path.join(d, 'f_*.jpg'))) - 1
cols = 8; w, h = 216, 384; rows = (len(ts) + cols - 1) // cols
S = Image.new('RGB', (cols * w, rows * (h + 22)), 'white'); D = ImageDraw.Draw(S)
for i, t in enumerate(ts):
    f = min(last, int(round(t * fps))); im = Image.open(f'{d}/f_{f:05d}.jpg').convert('RGB').resize((w, h))
    x, y = (i % cols) * w, (i // cols) * (h + 22); S.paste(im, (x, y + 22)); D.text((x + 4, y + 5), f'{t:.2f}', fill='black')
S.save(out); print(len(ts), 'cuadros →', out)
