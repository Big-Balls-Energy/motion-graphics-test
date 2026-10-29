"""Recorta las poses AV02–AV09 de la hoja de personaje (AV00) usando su propio canal alfa, sin redibujar nada."""
import sys
import numpy as np
from PIL import Image, ImageFilter
from scipy import ndimage as ndi

SRC = sys.argv[1]; OUT = sys.argv[2]; SCALE = float(sys.argv[3]) if len(sys.argv) > 3 else 3.0
im = Image.open(SRC).convert('RGBA'); A = np.asarray(im).astype(np.float32); a = A[..., 3]

def cut(name, box, y_max, comp_thr=200, lo=196, hi=242, keep_all=False):
    x0, y0, x1, y1 = box
    sub = A[y0:y1, x0:x1].copy(); sa = sub[..., 3]
    m = sa > comp_thr
    m[y_max - y0:] = False
    lab, n = ndi.label(m)
    if not keep_all:
        sizes = ndi.sum(m, lab, range(1, n + 1)); k = 1 + int(np.argmax(sizes)); m = lab == k
    m = ndi.binary_fill_holes(m)
    reg = ndi.binary_dilation(m, iterations=2)
    al = np.clip((sa - lo) / (hi - lo), 0, 1) * reg
    al[y_max - y0:] = 0
    # defringe: color of edge pixels from the nearest solid pixel
    solid = al >= 0.96
    _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
    rgb = sub[..., :3].copy(); edge = (al > 0) & ~solid
    rgb[edge] = sub[..., :3][iy[edge], ix[edge]]
    out = np.dstack([rgb, al * 255]).clip(0, 255).astype(np.uint8)
    o = Image.fromarray(out, 'RGBA'); bb = o.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox(); o = o.crop(bb)
    # upscale with premultiplied alpha (avoids dark halos), Lanczos, light unsharp
    W, H = o.size; o2 = o.resize((round(W * SCALE), round(H * SCALE)), Image.LANCZOS)
    rgbS = o2.convert('RGB').filter(ImageFilter.UnsharpMask(radius=2.2, percent=70, threshold=2))
    alS = o2.getchannel('A')
    res = Image.merge('RGBA', (*rgbS.split(), alS))
    res.save(f'{OUT}/{name}'); print(name, o.size, '→', res.size)

# (x0, y0, x1, y1) generous boxes; y_max excludes the labels under each pose
cut('AV02_presentando.png', (170, 612, 312, 860), 853)
cut('AV03_senalando.png', (292, 612, 402, 860), 853)
cut('AV04_pensando.png', (400, 612, 520, 860), 853)
cut('AV05_usando_tablet.png', (526, 612, 632, 860), 853)
cut('AV06_explicando_2.png', (636, 612, 757, 860), 853)
cut('AV07_brazos_cruzados.png', (770, 612, 870, 860), 853)
cut('AV08_pulgar_arriba.png', (880, 612, 985, 860), 853)
SCALE = 3.5
cut('AV09_avatar_aventurero.png', (1148, 878, 1338, 1024), 1024)
SCALE = 4.0
cut('AV08_mano_pulgar.png', (1280, 618, 1366, 708), 706)
