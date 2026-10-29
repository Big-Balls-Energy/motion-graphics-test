"""Z05 Switch 2: sin logotipos (pantallas, base y agarre) y sin fondo."""
import sys
sys.path.insert(0, '/home/user/motion-graphics-test')
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from herramientas.fotos import smooth_fill
src, out = sys.argv[1], sys.argv[2]
im = np.asarray(Image.open(src).convert('RGB')).copy(); H, W, _ = im.shape
for (x0, y0, x1, y1), sg in [((418, 202, 545, 322), 9), ((98, 371, 174, 439), 6), ((750, 376, 820, 449), 6), ((373, 392, 423, 448), 4), ((491, 397, 559, 459), 5)]:
    m = np.zeros((H, W), np.uint8); cv2.rectangle(m, (x0, y0), (x1, y1), 255, -1)
    im = smooth_fill(im, m, sigma=sg, noise=1.0)
Image.fromarray(im).save(out.replace('.png', '_limpia.jpg'), quality=95)
f = im.astype(np.float32); mn, mx = f.min(2), f.max(2)
light = (mn > 196) & ((mx - mn) < 30)
lab, n = ndi.label(light)
border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
obj = ~np.isin(lab, list(border))
lab2, n2 = ndi.label(obj); s2 = ndi.sum(obj, lab2, range(1, n2 + 1)); obj = np.isin(lab2, 1 + np.where(s2 > 300)[0])
obj = ndi.binary_fill_holes(obj)
dist = ndi.distance_transform_edt(obj); a = np.clip(dist / 1.4, 0, 1)
ring = obj & (dist <= 2); soft = np.clip((250 - mn) / 70, 0, 1); a[ring] = np.minimum(a[ring] + .3, 1) * soft[ring] ** .5
a = ndi.gaussian_filter(a, .5) * ndi.binary_dilation(obj, iterations=1)
solid = a >= .95; _, (iy, ix) = ndi.distance_transform_edt(~solid, return_indices=True)
rgb = f.copy(); e = (a > 0) & ~solid; rgb[e] = f[iy[e], ix[e]]
o = Image.fromarray(np.dstack([rgb, a * 255]).clip(0, 255).astype(np.uint8), 'RGBA')
o = o.crop(o.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox()); o.save(out); print(out, o.size)
