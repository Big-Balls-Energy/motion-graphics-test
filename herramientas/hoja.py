"""Hoja de contacto de capturas sueltas (snap_*.png que deja tools/render.js en modo snap).

Uso: python3 herramientas/hoja.py <carpeta_capturas> <salida.jpg> [columnas=5]
Después ábrela con la herramienta Read para revisar varios cuadros de un vistazo."""
import glob, sys
from PIL import Image, ImageDraw
files = sorted(glob.glob(sys.argv[1] + '/snap_*.png'), key=lambda f: float(f.split('_')[-1][:-4]))
cols = int(sys.argv[3]) if len(sys.argv) > 3 else 5; w, h = 360, 640; rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (cols * w, rows * (h + 30)), 'white'); d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((w, h)); x, y = (i % cols) * w, (i // cols) * (h + 30)
    sheet.paste(im, (x, y + 30)); d.text((x + 5, y + 8), f.split('_')[-1][:-4], fill='black')
sheet.save(sys.argv[2]); print(len(files), 'capturas →', sys.argv[2])
