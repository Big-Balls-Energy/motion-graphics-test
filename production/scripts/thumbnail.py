"""Miniatura vertical para Reels (1080x1920) a partir de un render 3D.

Uso: python thumbnail.py <frame_render.png> <salida.png> [--logo logo.png]
"""
import argparse
import os
import sys

import cv2
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import compose as C  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("frame")
    ap.add_argument("out")
    ap.add_argument("--logo", default="")
    a = ap.parse_args()
    img = cv2.imread(a.frame, cv2.IMREAD_UNCHANGED)
    img = img[..., :3][..., ::-1].astype(np.float32) / (65535.0 if img.dtype == np.uint16 else 255.0)
    img = cv2.resize(img, (C.W, C.H), interpolation=cv2.INTER_LANCZOS4)
    img = C.grade(img, 0, np.random.default_rng(5))
    # degradados para legibilidad (arriba y abajo)
    yy = np.linspace(0, 1, C.H)[:, None, None]
    shade = 1 - 0.75 * np.clip((0.36 - yy) / 0.36, 0, 1) ** 1.4 - 0.8 * np.clip((yy - 0.66) / 0.34, 0, 1) ** 1.3
    img = img * shade
    canvas = np.zeros((C.H, C.W, 4), np.float32)
    k = C.text_sprite("TRATAMIENTO DE VÁRICES", C.F_KICK, fill=C.ACCENT, tracking=6)
    C.paste(canvas, k, C.W / 2, 250)
    C.draw_line(canvas, (C.W / 2 - 70, 282), (C.W / 2 + 70, 282), C.ACCENT, 1.0, 3)
    big = C.font("InterDisplay-Bold.otf", 96)
    for i, line in enumerate(["ESCLEROTERAPIA", "CON MICROESPUMA"]):
        sp = C.text_sprite(line, big if i == 0 else C.font("InterDisplay-Bold.otf", 80), tracking=3)
        C.paste(canvas, sp, C.W / 2, 368 + i * 98)
    q = C.text_sprite("¿Qué ocurre dentro de una várice?", C.font("Inter-SemiBold.otf", 40), fill=(215, 235, 255))
    C.paste(canvas, q, C.W / 2, 545)
    if a.logo and os.path.exists(a.logo):
        im = Image.open(a.logo).convert("RGBA")
        im.thumbnail((440, 220), Image.LANCZOS)
        arr = np.asarray(im).astype(np.float32) / 255.0
        arr[..., :3] *= arr[..., 3:4]
        C.paste(canvas, (arr, 0), C.W / 2, 1470)
        ytxt = 1640
    else:
        ytxt = 1560
    brand = C.text_sprite("ARIAS MEDICAL CLINIC", C.font("InterDisplay-Bold.otf", 58), tracking=4,
                          glow=(80, 170, 255))
    C.paste(canvas, brand, C.W / 2, ytxt)
    tag = C.text_sprite("EXPERTOS EN FLEBOLOGÍA Y LINFOLOGÍA", C.F_TAG, fill=(205, 230, 255), tracking=3)
    C.paste(canvas, tag, C.W / 2, ytxt + 70)
    out = canvas[..., :3] + img * (1 - canvas[..., 3:4])
    Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8)).save(a.out)
    print("ok", a.out)


if __name__ == "__main__":
    main()
