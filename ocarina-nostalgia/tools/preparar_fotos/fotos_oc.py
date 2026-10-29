"""Fotos del reel ocarina-nostalgia: recortes, logotipos fuera y personajes de terceros desenfocados."""
import sys
sys.path.insert(0, '/home/user/motion-graphics-test')
import numpy as np, cv2
from PIL import Image
from scipy import ndimage as ndi
from herramientas.fotos import smooth_fill, quitar_fondo_blanco
U = '/root/.claude/uploads/9b8a7e0a-a64f-51ea-9543-f8732b0b3167/'
OUT = sys.argv[1]

def feather(m, s):
    return cv2.GaussianBlur(m.astype(np.float32), (0, 0), s)

# ---------- Z03 N64: sin logotipos (insignia frontal, relieves de la marca) y sin fondo
im = np.asarray(Image.open(U + '52ed6414-image.jpg').convert('RGB')).copy()
H, W, _ = im.shape
m = np.zeros((H, W), np.uint8)
cv2.fillPoly(m, [np.array([(858, 800), (884, 799), (996, 846), (996, 866), (952, 872), (950, 902), (886, 902), (884, 852), (857, 824)])], 255)
a = feather(m > 0, 1.2)[..., None]
black = np.array([9, 9, 11], np.float32)
im = (im * (1 - a) + black * a).astype(np.uint8)
m2 = np.zeros((H, W), np.uint8)
cv2.ellipse(m2, (256, 652), (66, 25), -4, 0, 360, 255, -1)      # relieve del control
cv2.ellipse(m2, (1231, 578), (66, 20), 17, 0, 360, 255, -1)      # relieve de la consola
im = smooth_fill(im, m2, sigma=4, noise=0.8)
Image.fromarray(im).save(OUT + '/Z03_limpia.jpg', quality=95)
rgba = quitar_fondo_blanco(im)
o = Image.fromarray(rgba, 'RGBA'); o = o.crop(o.getchannel('A').point(lambda v: 255 if v > 8 else 0).getbbox())
o.save(OUT + '/Z03_consola_n64.png'); print('Z03', o.size)

# ---------- Z01 sala de los 90: carteles, figura y pantalla con personajes de terceros → desenfoque fuerte
im = np.asarray(Image.open(U + '458423ca-image.jpg').convert('RGB')).astype(np.float32)
H, W, _ = im.shape
m = np.zeros((H, W), np.uint8)
for r in [(0, 0, 64, 335), (352, 10, 408, 470), (250, 125, 340, 195), (225, 200, 305, 248)]:
    cv2.rectangle(m, r[:2], r[2:], 255, -1)
a = feather(m > 0, 4)[..., None]
bl = cv2.GaussianBlur(im, (0, 0), 9)
g = bl.mean(2, keepdims=True); bl = bl * 0.55 + g * 0.45
im = im * (1 - a) + bl * a
# pantalla: se reemplaza por un resplandor de CRT sin imagen
scr = np.zeros((H, W), np.uint8); cv2.rectangle(scr, (102, 282), (305, 412), 255, -1)
cv2.ellipse(scr, (104, 418), (60, 66), 0, 0, 360, 0, -1); cv2.ellipse(scr, (312, 425), (44, 58), 0, 0, 360, 0, -1)
a2 = feather(scr > 0, 2.5)[..., None]
yy, xx = np.mgrid[0:H, 0:W]
d = np.sqrt(((xx - 203) / 120) ** 2 + ((yy - 348) / 80) ** 2)
glow = np.clip(1 - d, 0, 1)[..., None]
rng = np.random.default_rng(3); noise = rng.normal(0, 7, (H, W, 1))
col = np.array([70, 92, 125], np.float32) * (0.45 + 0.75 * glow) + noise
im = im * (1 - a2) + col * a2
Image.fromarray(np.clip(im, 0, 255).astype(np.uint8)).save(OUT + '/Z01_sala_tv_90s.jpg', quality=94); print('Z01', (W, H))

# ---------- fondos sin cambios (Z02, Z09, Z10)
for src, name in [('2ad796a5-image.jpg', 'Z02_nino_jugando_90s.jpg'), ('11e0c19c-image.jpg', 'Z09_padre_hijo_jugando.jpg'), ('e25aa6dd-image.jpg', 'Z10_negocio_retro.jpg')]:
    Image.open(U + src).convert('RGB').save(OUT + '/' + name, quality=94); print(name)
