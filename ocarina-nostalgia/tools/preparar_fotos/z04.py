"""Z04 ocarinas: borra la marca de agua del banco de imágenes y recorta el fondo blanco (también el encerrado por el cordón)."""
import sys
sys.path.insert(0, '/home/user/motion-graphics-test')
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).copy()
H, W, _ = im.shape
hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV).astype(np.float32)
L = cv2.cvtColor(im, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32)
med = cv2.medianBlur(L.astype(np.uint8), 9).astype(np.float32)
R = np.zeros((H, W), bool); R[250:308, 236:550] = True
stroke = ((L - med) > 8) & R & (hsv[..., 1] < 105)
stroke = cv2.dilate(stroke.astype(np.uint8), np.ones((3, 3), np.uint8))
im = cv2.inpaint(im, stroke, 3, cv2.INPAINT_TELEA)
# segunda pasada para los restos tenues de la marca
L = cv2.cvtColor(im, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32); med = cv2.medianBlur(L.astype(np.uint8), 11).astype(np.float32)
hsv = cv2.cvtColor(im, cv2.COLOR_RGB2HSV).astype(np.float32)
st2 = ((L - med) > 5) & R & (hsv[..., 1] < 95)
im = cv2.inpaint(im, cv2.dilate(st2.astype(np.uint8), np.ones((3, 3), np.uint8)), 3, cv2.INPAINT_TELEA)
# restos sobre la zona naranja (saturada): cualquier trazo más claro que su entorno
R3 = np.zeros((H, W), bool); R3[255:300, 425:468] = True
L = cv2.cvtColor(im, cv2.COLOR_RGB2LAB)[..., 0].astype(np.float32); med = cv2.medianBlur(L.astype(np.uint8), 13).astype(np.float32)
st3 = ((L - med) > 3) & R3
im = cv2.inpaint(im, cv2.dilate(st3.astype(np.uint8), np.ones((3, 3), np.uint8)), 4, cv2.INPAINT_TELEA)
Image.fromarray(im).save(out.replace('.png', '_limpia.jpg'), quality=95)
# fondo: blanco o gris muy claro poco saturado (sombra), en manchas grandes aunque no toquen el borde
f = im.astype(np.float32); mn, mx = f.min(2), f.max(2)
light = (mn > 200) & ((mx - mn) < 28)
lab, n = ndi.label(light); sizes = ndi.sum(light, lab, range(1, n + 1))
bg = np.isin(lab, 1 + np.where(sizes > 150)[0])
obj = ~bg
lab2, n2 = ndi.label(obj); s2 = ndi.sum(obj, lab2, range(1, n2 + 1)); keep = 1 + np.where(s2 > 400)[0]; obj = np.isin(lab2, keep)
dist = ndi.distance_transform_edt(obj)
a = np.clip(dist / 1.5, 0, 1)
ring = obj & (dist <= 2); soft = np.clip((255 - mn) / 55, 0, 1); a[ring] = np.minimum(a[ring] + 0.35, 1) * soft[ring] ** 0.5
a = ndi.gaussian_filter(a, 0.5) * ndi.binary_dilation(obj, iterations=1)
solid = a >= 0.95; _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
rgb = f.copy(); e = (a > 0) & ~solid; rgb[e] = f[iy[e], ix[e]]
o = Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
o = o.crop(o.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()); o.save(out); print(out, o.size)
