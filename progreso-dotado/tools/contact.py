"""Contact sheet of snapshot PNGs: python3 contact.py OUT.png a.png b.png ... (4 per row)."""
import sys
from PIL import Image, ImageDraw
out, files = sys.argv[1], sys.argv[2:]
tw, th, cols = 360, 640, 4
rows = (len(files) + cols - 1) // cols
sheet = Image.new('RGB', (tw * cols, (th + 30) * rows), 'white')
d = ImageDraw.Draw(sheet)
for i, f in enumerate(files):
    im = Image.open(f).convert('RGB').resize((tw, th), Image.LANCZOS)
    x, y = (i % cols) * tw, (i // cols) * (th + 30)
    sheet.paste(im, (x, y + 30))
    d.text((x + 8, y + 8), f.split('snap_')[-1], fill='black')
    d.rectangle([x, y + 30, x + tw - 1, y + 30 + th - 1], outline='red')
sheet.save(out)
