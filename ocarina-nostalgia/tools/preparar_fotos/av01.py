"""Recorte de AV01 (fondo blanco con sombra de piso): el fondo es todo pixel claro y poco saturado conectado con el borde."""
import sys
import numpy as np
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
H, W, _ = im.shape
mn, mx = im.min(2), im.max(2)
light = (mn > 178) & ((mx - mn) < 46)
lab, n = ndi.label(light)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
bg = np.isin(lab, list(border))
obj = ~bg
# los tenis blancos tocan el fondo blanco: se protegen con su contorno (coordenadas de la imagen original)
from PIL import ImageDraw
pm = Image.new('L', (W, H), 0); dr = ImageDraw.Draw(pm)
dr.polygon([(615,941),(619,956),(640,961),(700,957),(742,950),(778,942),(784,930),(782,915),(777,880),(770,872),(740,880),(722,876),(700,870),(690,880),(660,905),(640,915),(625,925)], fill=255)
dr.polygon([(868,1000),(876,1013),(900,1017),(937,1015),(956,1002),(959,980),(950,945),(944,922),(935,915),(917,906),(890,906),(878,918),(872,940),(868,980)], fill=255)
shoes = np.asarray(pm) > 0
# dentro del contorno, el piso gris claro no es tenis: se queda lo que es claro (tenis) o tiene línea de contorno
obj = obj | shoes
# keep the main body only (drop specks), fill small holes
lab2, n2 = ndi.label(obj); sizes = ndi.sum(obj, lab2, range(1, n2 + 1)); obj = lab2 == (1 + int(np.argmax(sizes)))
obj = ndi.binary_fill_holes(obj)
# soft edge: 1.5 px feather from the boundary, plus luminance-based softness on the outer ring
dist_in = ndi.distance_transform_edt(obj)
a = np.clip(dist_in / 1.6, 0, 1)
ring = obj & (dist_in <= 2)
soft = np.clip((255 - mn) / 60, 0, 1)
a[ring] = np.maximum(a[ring] * 0.6, soft[ring]) * np.clip(dist_in[ring], 0, 1)
a = ndi.gaussian_filter(a, 0.5) * ndi.binary_dilation(obj, iterations=1)
# defringe edge colors from the nearest solid pixel
solid = a >= 0.95
_, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
rgb = im.copy(); edge = (a > 0) & ~solid; rgb[edge] = im[iy[edge], ix[edge]]
res = Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
res = res.crop(res.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
res.save(out); print(out, res.size)
