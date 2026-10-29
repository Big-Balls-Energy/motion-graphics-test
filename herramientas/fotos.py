"""Preparación de fotos para los reels (recortes, borrar marcas, recortar transparencias).

Uso:
  python3 herramientas/fotos.py info <imagen> [<imagen> ...]                  # tamaño, modo y % transparente
  python3 herramientas/fotos.py fondo-blanco <entrada> <salida.png>           # quita el fondo blanco que toca el borde
  python3 herramientas/fotos.py borrar <entrada> <salida> rect:x0,y0,x1,y1 [elipse:cx,cy,rx,ry ...] [--sigma 5] [--margen 0]
                                                                              # borra logotipos o marcas rellenando con los alrededores
                                                                              # --sigma: qué tan lejos toma color (4–6 para marcas chicas;
                                                                              #   si es grande jala colores de otras zonas, p. ej. una pantalla blanca)
                                                                              # --margen: px que crece la máscara si quedan restos de la marca
  python3 herramientas/fotos.py recortar <entrada.png> <salida.png>           # recorta un PNG transparente a su contenido

Las coordenadas son píxeles de la imagen original. Revisa siempre el resultado ampliado (con Read) antes de usarlo:
si el relleno manchó algo (por ejemplo, un dedo que toca la marca), usa máscaras más chicas o varias formas.
Funciones reutilizables desde Python: smooth_fill, bg_model, keep_largest, quitar_fondo_blanco."""
import sys
import numpy as np
import cv2
from PIL import Image
from scipy import ndimage as ndi


def smooth_fill(img, mask, sigma=14, noise=1.6, seed=1):
    """Rellena la zona marcada con una interpolación suave de los alrededores (convolución normalizada multiescala) + grano ligero."""
    m = (mask > 0).astype(np.float32); keep = 1 - m
    f = img.astype(np.float32); fill = np.zeros_like(f); done = np.zeros(m.shape, np.float32)
    for s in (sigma, sigma * 2, sigma * 4, sigma * 8, sigma * 16):
        num = cv2.GaussianBlur(f * keep[..., None], (0, 0), s); den = cv2.GaussianBlur(keep, (0, 0), s)
        ok = np.clip(den / 0.15, 0, 1) * (1 - done)
        fill += (num / np.maximum(den, 1e-6)[..., None]) * ok[..., None]; done += ok
    fill /= np.maximum(done, 1e-6)[..., None]
    rng = np.random.default_rng(seed); fill += rng.normal(0, noise, fill.shape)
    soft = cv2.GaussianBlur(m, (0, 0), 2.5)[..., None]
    return np.clip(f * (1 - soft) + fill * soft, 0, 255).astype(np.uint8)


def bg_model(img, bgmask):
    """Ajusta un gradiente cuadrático por canal al fondo (para separar objetos claros sobre fondo gris)."""
    H, W = img.shape[:2]; ys, xs = np.where(bgmask > 0); sel = np.random.default_rng(0).choice(len(xs), min(40000, len(xs)), replace=False)
    x = xs[sel] / W; y = ys[sel] / H; A = np.stack([np.ones_like(x), x, y, x * x, y * y, x * y], 1)
    Y, X = np.mgrid[0:H, 0:W]; Xn, Yn = X / W, Y / H; B = np.stack([np.ones_like(Xn), Xn, Yn, Xn * Xn, Yn * Yn, Xn * Yn], -1)
    out = np.zeros(img.shape, np.float32)
    for c in range(3):
        coef, *_ = np.linalg.lstsq(A, img[ys[sel], xs[sel], c].astype(np.float64), rcond=None); out[..., c] = B @ coef
    return out


def keep_largest(m, min_hole=1500):
    """Se queda con la mancha más grande de una máscara y tapa sus huecos pequeños."""
    n, lab, st, _ = cv2.connectedComponentsWithStats(m); k = 1 + np.argmax(st[1:, cv2.CC_STAT_AREA]); m = np.where(lab == k, 255, 0).astype(np.uint8)
    inv = 255 - m; n, lab, st, _ = cv2.connectedComponentsWithStats(inv)
    for i in range(1, n):
        if st[i, cv2.CC_STAT_AREA] < min_hole: m[lab == i] = 255
    return m


def quitar_fondo_blanco(rgb, umbral=236, tolerancia=14):
    """Recorte de un objeto sobre fondo blanco: el fondo es el blanco conectado con el borde (los blancos interiores,
    como la pantalla de un celular, se conservan). Borde suave de 3 px y descontaminación del halo blanco."""
    im = rgb.astype(np.float32); H, W, _ = im.shape; mn = im.min(2); mx = im.max(2)
    cand = (mn > umbral) & ((mx - mn) < tolerancia); lab, n = ndi.label(cand)
    border = set(np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))) - {0}
    bg = np.isin(lab, list(border)); obj = ~bg
    dist = ndi.distance_transform_edt(obj); a = np.ones((H, W), np.float32); a[bg] = 0
    ring = obj & (dist <= 3); soft = np.clip((255 - mn) / 42, 0, 1); a[ring] = soft[ring]
    a = np.clip(ndi.gaussian_filter(a, .6) * (obj | ndi.binary_dilation(obj, iterations=1)), 0, 1)
    out = im.copy(); m = (a > 0.02) & (a < 0.98)
    for c in range(3):
        ch = out[..., c]; ch[m] = np.clip((ch[m] - (1 - a[m]) * 255) / a[m], 0, 255)
    return np.dstack([out, a * 255]).astype(np.uint8)


def mascara(shape, specs):
    m = np.zeros(shape[:2], np.uint8)
    for s in specs:
        kind, vals = s.split(':'); v = [int(round(float(x))) for x in vals.split(',')]
        if kind == 'rect': cv2.rectangle(m, (v[0], v[1]), (v[2], v[3]), 255, -1)
        elif kind == 'elipse': cv2.ellipse(m, (v[0], v[1]), (v[2], v[3]), 0, 0, 360, 255, -1)
        else: sys.exit(f'forma desconocida: {kind} (usa rect:x0,y0,x1,y1 o elipse:cx,cy,rx,ry)')
    return m


def guardar(arr, path, mode):
    im = Image.fromarray(arr, mode)
    if path.lower().endswith(('.jpg', '.jpeg')): im.convert('RGB').save(path, quality=94)
    else: im.save(path)


if __name__ == '__main__':
    if len(sys.argv) < 3: sys.exit(__doc__)
    cmd = sys.argv[1]
    if cmd == 'info':
        for f in sys.argv[2:]:
            im = Image.open(f); extra = ''
            if im.mode == 'RGBA': a = np.asarray(im)[..., 3]; extra = f' transparente {(a < 10).mean() * 100:.1f}% · contenido {im.getbbox()}'
            print(f, im.size, im.mode, extra)
    elif cmd == 'fondo-blanco':
        guardar(quitar_fondo_blanco(np.asarray(Image.open(sys.argv[2]).convert('RGB'))), sys.argv[3], 'RGBA'); print('→', sys.argv[3])
    elif cmd == 'borrar':
        args = sys.argv[4:]; margen = 0; sigma = 5
        if '--margen' in args: i = args.index('--margen'); margen = int(args[i + 1]); del args[i:i + 2]
        if '--sigma' in args: i = args.index('--sigma'); sigma = float(args[i + 1]); del args[i:i + 2]
        im = Image.open(sys.argv[2]); rgba = im.mode == 'RGBA'; a = np.asarray(im.convert('RGBA' if rgba else 'RGB'))
        rgb = a[..., :3]; m = mascara(rgb.shape, args)
        if margen > 0: m = cv2.dilate(m, np.ones((2 * margen + 1, 2 * margen + 1), np.uint8))
        out = smooth_fill(rgb, m, sigma=sigma, noise=1.2)
        guardar(np.dstack([out, a[..., 3]]) if rgba else out, sys.argv[3], 'RGBA' if rgba else 'RGB'); print('→', sys.argv[3])
    elif cmd == 'recortar':
        im = Image.open(sys.argv[2]).convert('RGBA'); box = im.getchannel('A').point(lambda v: 255 if v > 10 else 0).getbbox()
        im.crop(box).save(sys.argv[3]); print('→', sys.argv[3], box)
    else: sys.exit(__doc__)
