"""Composición final: planos 3D + transiciones + etalonaje + gráficos + subtítulos + audio -> MP4.

Uso:
  python compose.py --frames DIR_FRAMES --anchors DIR_ANCHORS --audio mix.wav --out video.mp4 [--srt out.srt]
                    [--preview 0,120,400 --preview-dir DIR] [--workers 4] [--logo assets/logo.png]

DIR_FRAMES/<shot>/<shot>_NNNN.png son los renders (frame maestro en el nombre). Los anclajes 3D proyectados
(anchors.json) se buscan en DIR_FRAMES/<shot>/ y en DIR_ANCHORS/<shot>/.
"""
import argparse
import json
import math
import os
import subprocess
import sys

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from lib.timeline import CUTS, FPS, NARRATION, SHOTS, TOTAL_FRAMES  # noqa: E402

W, H = 1080, 1920
FONT_DIR = "/usr/share/fonts/opentype/inter"
WHITE = (255, 255, 255)
ACCENT = (94, 209, 255)        # cian médico
BLUE = (31, 111, 235)          # azul institucional (paleta neutra; confirmar con manual de marca)
SAFE_X0, SAFE_X1 = 72, 940     # margen derecho libre para los botones de Reels

TRANSITIONS = {("s1a", "s1b"): "dive", ("s1b", "s2"): "cross", ("s2", "s3a"): "dive", ("s3a", "s3b"): "flash",
               ("s3b", "s3c"): "cross", ("s3c", "s4"): "cross", ("s4", "s5"): "cross", ("s5", "s6"): "flash"}


def font(name, size):
    return ImageFont.truetype(os.path.join(FONT_DIR, name), size)


def ease(x):
    x = min(max(x, 0.0), 1.0)
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(max(x, 0.0), 1.0)
    return 1 - (1 - x) ** 3


def fade_window(t, t0, t1, fin=0.45, fout=0.4):
    """Opacidad 0..1 para un elemento visible entre t0 y t1 con fundidos."""
    return ease((t - t0) / fin) * (1 - ease((t - (t1 - fout)) / fout))


# ----------------------------------------------------------------------------- texto (sprites cacheados)

_SPRITES = {}


def text_sprite(text, fnt, fill=WHITE, tracking=0, shadow=True, glow=None, stroke=0):
    """Renderiza texto en RGBA (con sombra suave) y lo cachea. Devuelve np.float32 premultiplicado."""
    key = (text, fnt.path, fnt.size, fill, tracking, shadow, glow, stroke)
    if key in _SPRITES:
        return _SPRITES[key]
    # medir con tracking
    widths = [fnt.getlength(ch) for ch in text]
    tw = int(sum(widths) + tracking * max(len(text) - 1, 0)) + 2
    asc, desc = fnt.getmetrics()
    th = asc + desc
    pad = int(fnt.size * 0.6)
    img = Image.new("RGBA", (tw + 2 * pad, th + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    x = pad
    for ch, w_ in zip(text, widths):
        d.text((x, pad), ch, font=fnt, fill=fill + (255,), stroke_width=stroke, stroke_fill=fill + (255,))
        x += w_ + tracking
    out = img
    if shadow or glow:
        a = img.split()[3]
        layers = Image.new("RGBA", img.size, (0, 0, 0, 0))
        if shadow:
            sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
            sh.putalpha(a.filter(ImageFilter.GaussianBlur(fnt.size * 0.18)).point(lambda v: int(v * 0.75)))
            layers = Image.alpha_composite(layers, sh)
        if glow:
            gl = Image.new("RGBA", img.size, glow + (0,))
            gl.putalpha(a.filter(ImageFilter.GaussianBlur(fnt.size * 0.35)).point(lambda v: int(v * 0.6)))
            layers = Image.alpha_composite(layers, gl)
        out = Image.alpha_composite(layers, img)
    arr = np.asarray(out).astype(np.float32) / 255.0
    arr[..., :3] *= arr[..., 3:4]
    _SPRITES[key] = (arr, pad)
    return _SPRITES[key]


def paste(canvas, sprite, x, y, opacity=1.0, anchor="center"):
    """Compone un sprite premultiplicado sobre el lienzo RGBA premultiplicado (float)."""
    arr, pad = sprite
    h, w = arr.shape[:2]
    if anchor == "center":
        x0, y0 = int(round(x - w / 2)), int(round(y - h / 2))
    elif anchor == "left":
        x0, y0 = int(round(x - pad)), int(round(y - h / 2))
    else:  # right
        x0, y0 = int(round(x - w + pad)), int(round(y - h / 2))
    xa, ya = max(x0, 0), max(y0, 0)
    xb, yb = min(x0 + w, W), min(y0 + h, H)
    if xb <= xa or yb <= ya or opacity <= 0:
        return
    src = arr[ya - y0:yb - y0, xa - x0:xb - x0] * opacity
    dst = canvas[ya:yb, xa:xb]
    dst[:] = src + dst * (1 - src[..., 3:4])


def sprite_width(sprite):
    arr, pad = sprite
    return arr.shape[1] - 2 * pad


# ----------------------------------------------------------------------------- dibujo vectorial (antialias)


def draw_line(canvas, p0, p1, color, alpha, thick=2):
    if alpha <= 0:
        return
    layer = np.zeros((H, W), np.uint8)
    cv2.line(layer, (int(p0[0] * 4), int(p0[1] * 4)), (int(p1[0] * 4), int(p1[1] * 4)), 255, thick, cv2.LINE_AA, 2)
    blend_mask(canvas, layer, color, alpha)


def draw_circle(canvas, c, r, color, alpha, thick=-1):
    if alpha <= 0:
        return
    layer = np.zeros((H, W), np.uint8)
    cv2.circle(layer, (int(c[0] * 4), int(c[1] * 4)), int(r * 4), 255, thick, cv2.LINE_AA, 2)
    blend_mask(canvas, layer, color, alpha)


def draw_rounded_rect(canvas, x0, y0, x1, y1, r, color, alpha, outline=None, outline_alpha=0.0, thick=2):
    layer = np.zeros((H, W), np.uint8)
    x0, y0, x1, y1, r = int(x0), int(y0), int(x1), int(y1), int(r)
    cv2.rectangle(layer, (x0 + r, y0), (x1 - r, y1), 255, -1)
    cv2.rectangle(layer, (x0, y0 + r), (x1, y1 - r), 255, -1)
    for cx, cy in ((x0 + r, y0 + r), (x1 - r, y0 + r), (x0 + r, y1 - r), (x1 - r, y1 - r)):
        cv2.circle(layer, (cx, cy), r, 255, -1, cv2.LINE_AA)
    blend_mask(canvas, layer, color, alpha)
    if outline is not None and outline_alpha > 0:
        ol = np.zeros((H, W), np.uint8)
        cv2.line(ol, (x0 + r, y0), (x1 - r, y0), 255, thick, cv2.LINE_AA)
        cv2.line(ol, (x0 + r, y1), (x1 - r, y1), 255, thick, cv2.LINE_AA)
        cv2.line(ol, (x0, y0 + r), (x0, y1 - r), 255, thick, cv2.LINE_AA)
        cv2.line(ol, (x1, y0 + r), (x1, y1 - r), 255, thick, cv2.LINE_AA)
        for (cx, cy), a0 in (((x0 + r, y0 + r), 180), ((x1 - r, y0 + r), 270), ((x0 + r, y1 - r), 90), ((x1 - r, y1 - r), 0)):
            cv2.ellipse(ol, (cx, cy), (r, r), 0, a0, a0 + 90, 255, thick, cv2.LINE_AA)
        blend_mask(canvas, ol, outline, outline_alpha)


def blend_mask(canvas, mask_u8, color, alpha):
    ys, xs = np.nonzero(mask_u8)
    if len(ys) == 0:
        return
    y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
    m = mask_u8[y0:y1, x0:x1].astype(np.float32)[..., None] / 255.0 * alpha
    col = np.array(color, np.float32) / 255.0
    src = np.concatenate([col[None, None, :] * m, m], axis=-1)
    dst = canvas[y0:y1, x0:x1]
    dst[:] = src + dst * (1 - m)


# ----------------------------------------------------------------------------- contenido gráfico

F_TITLE = font("InterDisplay-Bold.otf", 70)
F_TITLE_S = font("InterDisplay-Bold.otf", 60)
F_KICK = font("Inter-SemiBold.otf", 26)
F_LABEL = font("Inter-SemiBold.otf", 32)
F_SUB = font("Inter-SemiBold.otf", 44)
F_SMALL = font("Inter-Medium.otf", 26)
F_BRAND = font("InterDisplay-Bold.otf", 64)
F_TAG = font("Inter-SemiBold.otf", 31)
F_SEDES = font("Inter-SemiBold.otf", 29)
F_CTA = font("InterDisplay-Bold.otf", 42)
F_DISC = font("Inter-Medium.otf", 29)
F_US = font("Inter-SemiBold.otf", 22)

# (t0, t1, líneas, antetítulo)
TITLES = [
    (0.45, 7.55, ["¿QUÉ OCURRE DENTRO", "DE UNA VÁRICE?"], "INSUFICIENCIA VENOSA"),
    (8.35, 15.55, ["ESCLEROTERAPIA", "CON MICROESPUMA"], "EL TRATAMIENTO"),
    (16.25, 20.25, ["MICROESPUMA"], "MECANISMO DE ACCIÓN · 1"),
    (20.55, 24.85, ["ACCIÓN SOBRE LA", "PARED VENOSA"], "MECANISMO DE ACCIÓN · 2"),
    (25.15, 29.65, ["CIERRE PROGRESIVO"], "MECANISMO DE ACCIÓN · 3"),
    (30.55, 39.6, ["LA CIRCULACIÓN", "CONTINÚA"], "RESULTADO"),
    (40.35, 43.45, ["MÍNIMAMENTE", "INVASIVO"], "BENEFICIOS · 1/3"),
    (43.65, 46.65, ["SIN CIRUGÍA", "ABIERTA"], "BENEFICIOS · 2/3"),
    (46.85, 49.65, ["PROCEDIMIENTO", "AMBULATORIO"], "BENEFICIOS · 3/3"),
]

# etiquetas médicas: (plano, ancla, t0, t1, texto, lado)
LABELS = [
    ("s1a", "varicose", 2.55, 4.15, "Vena varicosa", "left"),
    ("s1b", "cusp_edge", 4.75, 7.70, "Válvula incompetente", "right"),
    ("s2", "probe", 9.30, 12.4, "Guía ecográfica", "right-down"),
    ("s2", "needle", 10.6, 13.9, "Microaguja", "left-down"),
    ("s3a", "foam_front", 17.4, 20.1, "Desplaza la sangre", "left"),
    ("s3b", "endo", 20.9, 22.9, "Endotelio", "left"),
    ("s3b", "exposed", 23.0, 24.8, "Reacción local", "left"),
    ("s4", "cord", 31.0, 34.2, "Vena tratada · cordón fibroso", "left"),
]

SUB_CHUNKS = {
    "n1": ["Cuando las válvulas venosas fallan,", "la sangre puede retroceder y acumularse,",
           "favoreciendo la aparición de várices."],
    "n2": ["La escleroterapia con microespuma", "permite tratar determinadas venas enfermas",
           "mediante un procedimiento mínimamente invasivo."],
    "n3a": ["La microespuma entra en contacto", "con la pared interna de la vena"],
    "n3b": ["y provoca una reacción", "que favorece su cierre progresivo."],
    "n4a": ["Con el tiempo, la vena tratada se transforma", "y el organismo la reabsorbe progresivamente."],
    "n4b": ["La sangre continúa circulando", "por otras venas funcionales."],
    "n5": ["Es una alternativa ambulatoria,", "sin cirugía abierta", "y con recuperación habitualmente rápida,",
           "según la valoración de cada paciente."],
    "n6a": ["En Arias Medical Clinic,", "la salud de tus piernas", "merece atención especializada."],
    "n6b": ["Agenda tu valoración."],
}


def build_cues(timeline):
    """Reparte cada segmento de narración en subtítulos según caracteres y pausas reales del audio."""
    cues = []
    for key, t0 in NARRATION:
        info = timeline[key]
        dur = info["duration"]
        chunks = SUB_CHUNKS[key]
        assert " ".join(chunks).replace("  ", " ") == info["text"], (key, info["text"])
        lens = np.array([len(c.replace(" ", "")) for c in chunks], float)
        bounds = list(np.cumsum(lens) / lens.sum() * dur)
        pauses = [(a + b) / 2 for a, b in info["pauses"]]
        for i in range(len(bounds) - 1):
            if pauses:
                p = min(pauses, key=lambda x: abs(x - bounds[i]))
                if abs(p - bounds[i]) < 0.7:
                    bounds[i] = p
        start = 0.0
        for c, b in zip(chunks, bounds):
            cues.append((t0 + start, t0 + b, c))
            start = b
    # mantener cada subtítulo al menos hasta el siguiente o +0.25 s (lectura cómoda, sin solapes)
    out = []
    for i, (a, b, c) in enumerate(cues):
        nxt = cues[i + 1][0] if i + 1 < len(cues) else 60.0
        out.append((a, min(b + 0.25, nxt - 0.02), c))
    return out


def wrap_two(text, fnt, maxw=880):
    if fnt.getlength(text) <= maxw:
        return [text]
    words = text.split()
    best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        m = max(fnt.getlength(a), fnt.getlength(b))
        if best is None or m < best[0]:
            best = (m, [a, b])
    return best[1]


def srt_time(t):
    ms = int(round(t * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def write_srt(cues, path):
    with open(path, "w", encoding="utf-8") as f:
        for i, (a, b, c) in enumerate(cues, 1):
            lines = wrap_two(c, F_SUB, 880)
            f.write(f"{i}\n{srt_time(a)} --> {srt_time(b)}\n" + "\n".join(lines) + "\n\n")


# ----------------------------------------------------------------------------- frames 3D y transiciones


def shot_frame(frames_dir, shot, fr):
    p = os.path.join(frames_dir, shot, f"{shot}_{fr:04d}.png")
    img = cv2.imread(p, cv2.IMREAD_UNCHANGED)
    if img is None:
        return None
    img = img[..., :3][..., ::-1].astype(np.float32) / (65535.0 if img.dtype == np.uint16 else 255.0)
    if img.shape[1] != W:
        img = cv2.resize(img, (W, H), interpolation=cv2.INTER_LANCZOS4)
        blur = cv2.GaussianBlur(img, (0, 0), 1.1)
        img = np.clip(img + 0.45 * (img - blur), 0, 1)
    return img


def zoom(img, s, cx=W / 2, cy=H / 2, radial=0.0, n=6):
    """Escala alrededor de (cx, cy); con radial>0 promedia copias escaladas (desenfoque radial)."""
    acc = None
    scales = [s * (1 + radial * k / max(n - 1, 1)) for k in range(n)] if radial > 0 else [s]
    for sk in scales:
        M = np.array([[sk, 0, cx * (1 - sk)], [0, sk, cy * (1 - sk)]], np.float32)
        z = cv2.warpAffine(img, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        acc = z if acc is None else acc + z
    return acc / len(scales)


def active(fr):
    """Devuelve [(shot, peso, rol)] para el frame maestro."""
    order = ["s1a", "s1b", "s2", "s3a", "s3b", "s3c", "s4", "s5", "s6"]
    for a, b, c, d in CUTS:
        lo, hi = c - d // 2, c + d - d // 2
        if lo <= fr < hi:
            u = (fr - lo + 0.5) / d
            return [(a, 1 - ease(u), "out", u), (b, ease(u), "in", u)]
    cur = order[0]
    for a, b, c, d in CUTS:
        if fr >= c:
            cur = b
    return [(cur, 1.0, "solo", 0.0)]


def base_image(frames_dir, fr, anchors):
    parts = active(fr)
    if len(parts) == 1:
        img = shot_frame(frames_dir, parts[0][0], fr)
        return (img if img is not None else placeholder(parts[0][0])), parts
    (a, wa, _, u), (b, wb, _, _) = parts
    A = shot_frame(frames_dir, a, fr)
    B = shot_frame(frames_dir, b, fr)
    A = A if A is not None else placeholder(a)
    B = B if B is not None else placeholder(b)
    kind = TRANSITIONS.get((a, b), "cross")
    if kind == "dive":
        c = (W / 2, H * 0.48)
        if a == "s2":
            p = anchor_px(anchors, "s2", "tip", fr)
            if p is not None:
                c = p
        A = zoom(A, 1 + 0.9 * ease(u), c[0], c[1], radial=0.10 * math.sin(math.pi * u))
        B = zoom(B, 1.18 - 0.18 * ease(u), W / 2, H / 2, radial=0.06 * (1 - u))
        img = A * wa + B * wb
        glow = math.sin(math.pi * u) ** 2 * 0.35
        img = img + glow * np.array([1.0, 0.55, 0.5], np.float32)
    elif kind == "flash":
        img = A * wa + B * wb
        glow = math.sin(math.pi * u) ** 2 * 0.45
        img = img + glow * np.array([0.85, 0.92, 1.0], np.float32)
    else:
        img = A * wa + B * wb
    return np.clip(img, 0, 4), parts


def placeholder(shot):
    img = np.zeros((H, W, 3), np.uint8)
    img[:] = (5, 10, 20)
    cv2.putText(img, f"[{shot} pendiente]", (260, 960), cv2.FONT_HERSHEY_SIMPLEX, 2.0, (80, 130, 200), 3)
    return img.astype(np.float32) / 255.0


# ----------------------------------------------------------------------------- etalonaje

_VIG = None


def grade(img, fr, rng):
    global _VIG
    if _VIG is None:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
        _VIG = (1 - 0.30 * np.clip(r, 0, 1.4) ** 2.2)[..., None].astype(np.float32)
    # bloom suave de altas luces
    hi = np.clip(img - 0.72, 0, None)
    small = cv2.resize(hi, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    b = cv2.GaussianBlur(small, (0, 0), 5) * 0.6 + cv2.GaussianBlur(small, (0, 0), 16) * 0.4
    img = img + cv2.resize(b, (W, H), interpolation=cv2.INTER_LINEAR) * 0.55
    img = img * _VIG
    # hombro suave solo en altas luces (por encima de 0.8)
    k = 0.8
    over = img > k
    img = np.where(over, k + (1 - k) * (1 - np.exp(-(img - k) / (1 - k))), img)
    # grano fílmico (luma), dinámico
    g = rng.normal(0, 0.012, (H // 2, W // 2)).astype(np.float32)
    g = cv2.resize(g, (W, H), interpolation=cv2.INTER_LINEAR)[..., None]
    lum = img.mean(axis=2, keepdims=True)
    img = img + g * (0.35 + 0.65 * (1 - np.abs(lum - 0.5) * 2))
    return np.clip(img, 0, 1)


# ----------------------------------------------------------------------------- anclajes


def load_anchors(frames_dir, anchors_dir):
    A = {}
    for shot in SHOTS:
        for d in (os.path.join(anchors_dir or "", shot), os.path.join(frames_dir, shot)):
            p = os.path.join(d, "anchors.json")
            if os.path.exists(p):
                A[shot] = json.load(open(p))
                break
    return A


def anchor_px(anchors, shot, name, fr):
    d = anchors.get(shot, {}).get(str(fr))
    if not d or name not in d:
        return None
    x, y, z = d[name]
    if z <= 0:
        return None
    return (x * W, (1 - y) * H)


# ----------------------------------------------------------------------------- overlays por frame


def draw_title(canvas, t, t0, t1, lines, kicker):
    a = fade_window(t, t0, t1, 0.5, 0.35)
    if a <= 0:
        return
    rise = (1 - ease_out((t - t0) / 0.7)) * 26
    fnt = F_TITLE if max(F_TITLE.getlength(l) + 4 * len(l) for l in lines) < 860 else F_TITLE_S
    y = 318 + rise
    ks = text_sprite(kicker, F_KICK, fill=ACCENT, tracking=5, shadow=True)
    paste(canvas, ks, W / 2, y - 62, a)
    # línea de acento que crece
    lw = 120 * ease_out((t - t0 - 0.1) / 0.6)
    draw_line(canvas, (W / 2 - lw / 2, y - 36), (W / 2 + lw / 2, y - 36), ACCENT, a * 0.9, 3)
    for i, line in enumerate(lines):
        sp = text_sprite(line, fnt, tracking=3, shadow=True)
        paste(canvas, sp, W / 2, y + 12 + i * (fnt.size * 1.08), a)


def draw_label(canvas, t, fr, anchors, shot, name, t0, t1, text, side):
    p = anchor_px(anchors, shot, name, fr)
    if p is None:
        return
    a = fade_window(t, t0, t1, 0.35, 0.3)
    if a <= 0:
        return
    x, y = p
    x = min(max(x, 40), W - 40)
    down = side.endswith("-down")
    side = side.replace("-down", "")
    y = min(max(y, 470 if down else 590), 1240)
    sp = text_sprite(text, F_LABEL, tracking=1, shadow=True)
    tw = sprite_width(sp)
    ly = y + 110 if down else y - 120
    ly = min(max(ly, 480), 1230)
    # codo de la línea guía; el texto se apoya sobre un subrayado que nunca sale del área segura
    for sd in ((side, "right" if side == "left" else "left")):
        lx = x + (-95 if sd == "left" else 95)
        ux = lx - tw - 18 if sd == "left" else lx + tw + 18
        if SAFE_X0 <= min(lx, ux) and max(lx, ux) <= SAFE_X1:
            break
    else:
        lx = min(max(lx, SAFE_X0), SAFE_X1)
        ux = min(max(ux, SAFE_X0), SAFE_X1)
    k = ease_out((t - t0) / 0.5)
    draw_circle(canvas, (x, y), 7 + 3 * math.sin(t * 6), ACCENT, a * 0.35)
    draw_circle(canvas, (x, y), 5, WHITE, a)
    mx, my = x + (lx - x) * k, y + (ly - y) * k
    draw_line(canvas, (x, y), (mx, my), WHITE, a * 0.85, 2)
    if k > 0.95:
        u2 = ease((t - t0 - 0.3) / 0.3)
        cx_ = (lx + ux) / 2
        draw_rounded_rect(canvas, cx_ - tw / 2 - 14, ly - 50, cx_ + tw / 2 + 14, ly - 4, 14, (4, 10, 22),
                          a * u2 * 0.45)
        draw_line(canvas, (lx, ly), (lx + (ux - lx) * u2, ly), WHITE, a * 0.85, 2)
        paste(canvas, sp, cx_, ly - 26, a * u2)


def draw_reflux_arrow(canvas, t):
    """Flecha descendente animada (dirección del reflujo) en el plano 1B."""
    a = fade_window(t, 5.35, 7.75, 0.4, 0.3)
    if a <= 0:
        return
    x = 200
    y0, y1 = 760, 1080
    draw_line(canvas, (x, y0), (x, y1), ACCENT, a * 0.9, 4)
    draw_line(canvas, (x, y1), (x - 22, y1 - 30), ACCENT, a * 0.9, 4)
    draw_line(canvas, (x, y1), (x + 22, y1 - 30), ACCENT, a * 0.9, 4)
    for k in range(3):
        yy = y0 + ((t * 160 + k * 107) % (y1 - y0 - 20))
        draw_circle(canvas, (x, yy), 6, WHITE, a * 0.9)
    sp = text_sprite("REFLUJO", F_LABEL, fill=WHITE, tracking=4, shadow=True)
    paste(canvas, sp, x, y0 - 40, a)
    sp2 = text_sprite("hacia el pie", F_SMALL, fill=(200, 225, 255), tracking=1, shadow=True)
    paste(canvas, sp2, x, y1 + 40, a)


def draw_us_inset(canvas, t, us, us_frames):
    a = fade_window(t, 9.35, 16.05, 0.45, 0.35)
    if a <= 0:
        return
    x0, y0 = 72, 905
    img = us_frames(t)
    h, w = img.shape[:2]
    pad = 10
    draw_rounded_rect(canvas, x0 - pad, y0 - 46, x0 + w + pad, y0 + h + pad, 18, (6, 14, 28), a * 0.82,
                      outline=ACCENT, outline_alpha=a * 0.6)
    region = canvas[y0:y0 + h, x0:x0 + w]
    src = img.astype(np.float32) / 255.0
    m = np.full((h, w, 1), a, np.float32)
    region[:] = np.concatenate([src * m, m], -1) + region * (1 - m)
    sp = text_sprite("ECOGRAFÍA · LONGITUDINAL", F_US, fill=ACCENT, tracking=2, shadow=False)
    paste(canvas, sp, x0 + 4, y0 - 24, a, anchor="left")
    # escala de profundidad (cm)
    for k in range(4):
        yy = y0 + k * (h - 1) / 3
        draw_line(canvas, (x0 + w - 12, yy), (x0 + w - 2, yy), WHITE, a * 0.7, 2)


def draw_timeline(canvas, t):
    a = fade_window(t, 25.2, 29.75, 0.4, 0.3)
    if a <= 0:
        return
    steps = ["HORAS", "DÍAS", "SEMANAS"]
    u = ease((t - 25.4) / 4.0)
    x0, x1, y = 230, 850, 445
    draw_line(canvas, (x0, y), (x1, y), (120, 150, 190), a * 0.6, 3)
    draw_line(canvas, (x0, y), (x0 + (x1 - x0) * u, y), ACCENT, a, 4)
    for i, s in enumerate(steps):
        px = x0 + (x1 - x0) * i / 2
        on = u >= i / 2 - 0.02
        draw_circle(canvas, (px, y), 9, ACCENT if on else (120, 150, 190), a)
        sp = text_sprite(s, F_SMALL, fill=WHITE if on else (150, 170, 200), tracking=3, shadow=True)
        paste(canvas, sp, px, y + 40, a)
    draw_circle(canvas, (x0 + (x1 - x0) * u, y), 13, WHITE, a * 0.9, 3)


def draw_before_after(canvas, t, fr, anchors):
    a = fade_window(t, 36.0, 39.75, 0.5, 0.35)
    if a <= 0:
        return
    for name, txt, col in (("before_foot", "ANTES", (210, 160, 255)), ("after_foot", "DESPUÉS", ACCENT)):
        p = anchor_px(anchors, "s4", name, fr)
        if p is None:
            continue
        x = min(max(p[0], SAFE_X0 + 90), SAFE_X1 - 90)
        sp = text_sprite(txt, F_LABEL, fill=WHITE, tracking=5, shadow=True)
        tw = sprite_width(sp)
        draw_rounded_rect(canvas, x - tw / 2 - 22, 586, x + tw / 2 + 22, 642, 26, (6, 14, 28), a * 0.7,
                          outline=col, outline_alpha=a * 0.9)
        paste(canvas, sp, x, 613, a)


def draw_subtitles(canvas, t, cues):
    """Un único subtítulo activo a la vez; fundidos solo cuando hay silencio entre frases."""
    for i, (a_, b_, text) in enumerate(cues):
        if not (a_ <= t < b_):
            continue
        prev_end = cues[i - 1][1] if i > 0 else -1.0
        next_start = cues[i + 1][0] if i + 1 < len(cues) else 99.0
        fin = ease((t - a_) / 0.14) if a_ - prev_end > 0.2 else 1.0
        fout = (1 - ease((t - (b_ - 0.14)) / 0.14)) if next_start - b_ > 0.2 else 1.0
        op = fin * fout
        lines = wrap_two(text, F_SUB, 880)
        sprites = [text_sprite(l, F_SUB, shadow=False) for l in lines]
        wmax = max(sprite_width(sp) for sp in sprites)
        lh = 58
        yc = 1372 if len(lines) == 1 else 1350
        top = yc - lh * len(lines) / 2 - 16
        bot = yc + lh * len(lines) / 2 + 12
        cx = (SAFE_X0 + SAFE_X1) / 2 + 30
        draw_rounded_rect(canvas, cx - wmax / 2 - 26, top, cx + wmax / 2 + 26, bot, 22, (0, 0, 0), op * 0.52)
        for k, sp in enumerate(sprites):
            paste(canvas, sp, cx, top + 16 + lh * k + lh / 2 - 4, op)
        break


_LOGO = None


def draw_closing(canvas, t, logo_path):
    global _LOGO
    if t < 50.4:
        return
    has_logo = logo_path and os.path.exists(logo_path)
    if has_logo and _LOGO is None:
        im = Image.open(logo_path).convert("RGBA")
        im.thumbnail((560, 300), Image.LANCZOS)
        arr = np.asarray(im).astype(np.float32) / 255.0
        arr[..., :3] *= arr[..., 3:4]
        _LOGO = (arr, 0)
    yb = 900 if has_logo else 760
    # resplandor suave tras la marca
    a0 = ease((t - 50.6) / 1.2)
    if has_logo:
        a_logo = ease((t - 50.9) / 0.9)
        paste(canvas, _LOGO, W / 2, 640 + (1 - ease_out((t - 50.9) / 1.0)) * 20, a_logo)
    a1 = ease((t - 51.1) / 0.8)
    sp = text_sprite("ARIAS MEDICAL CLINIC", F_BRAND, tracking=4, shadow=True, glow=(80, 170, 255))
    paste(canvas, sp, W / 2 - 20, yb + (1 - ease_out((t - 51.1) / 1.0)) * 22, a1)
    lw = 520 * ease_out((t - 51.5) / 0.9)
    draw_line(canvas, (W / 2 - 20 - lw / 2, yb + 64), (W / 2 - 20 + lw / 2, yb + 64), ACCENT, a1, 3)
    a2 = ease((t - 51.9) / 0.7)
    sp = text_sprite("EXPERTOS EN FLEBOLOGÍA Y LINFOLOGÍA", F_TAG, fill=(205, 230, 255), tracking=3, shadow=True)
    paste(canvas, sp, W / 2 - 20, yb + 116, a2)
    a3 = ease((t - 52.8) / 0.7)
    sp = text_sprite("XALAPA · BOCA DEL RÍO · PUEBLA · SANTA CRUZ", F_SEDES, fill=WHITE, tracking=2, shadow=True)
    paste(canvas, sp, W / 2 - 20, yb + 206, a3)
    a4 = ease((t - 56.25) / 0.45)
    if a4 > 0:
        sp = text_sprite("AGENDA TU VALORACIÓN", F_CTA, tracking=3, shadow=False)
        tw = sprite_width(sp)
        cx, cy = W / 2 - 20, yb + 330
        s = 0.92 + 0.08 * ease_out((t - 56.25) / 0.6)
        draw_rounded_rect(canvas, cx - (tw / 2 + 46) * s, cy - 44 * s, cx + (tw / 2 + 46) * s, cy + 44 * s, 44 * s,
                          BLUE, a4 * 0.95, outline=ACCENT, outline_alpha=a4)
        paste(canvas, sp, cx, cy, a4)
    a5 = ease((t - 53.6) / 0.8)
    sp = text_sprite("Tratamiento sujeto a valoración médica individual", F_DISC, fill=(190, 205, 225), shadow=True)
    paste(canvas, sp, W / 2 - 20, 1478, a5 * 0.9)


def overlay(fr, t, anchors, cues, us_frames, logo_path):
    canvas = np.zeros((H, W, 4), np.float32)
    for t0, t1, lines, kicker in TITLES:
        draw_title(canvas, t, t0, t1, lines, kicker)
    for shot, name, t0, t1, text, side in LABELS:
        if t0 - 0.1 <= t <= t1 + 0.1:
            draw_label(canvas, t, fr, anchors, shot, name, t0, t1, text, side)
    draw_reflux_arrow(canvas, t)
    draw_us_inset(canvas, t, None, us_frames)
    draw_timeline(canvas, t)
    draw_before_after(canvas, t, fr, anchors)
    draw_closing(canvas, t, logo_path)
    draw_subtitles(canvas, t, cues)
    return canvas


# ----------------------------------------------------------------------------- pipeline

G = {}


def init_worker(frames_dir, anchors_dir, timeline_path, logo):
    from lib.ultrasound import Ultrasound
    import lib.s2_timing as S2
    G["frames"] = frames_dir
    G["anchors"] = load_anchors(frames_dir, anchors_dir)
    G["cues"] = build_cues(json.load(open(timeline_path, encoding="utf-8")))
    G["logo"] = logo
    us = Ultrasound()
    s2_start = SHOTS["s2"][0] / FPS

    def us_frames(t):
        tl = t - s2_start
        img, _ = us.frame(S2.needle_s(tl), S2.foam_out(tl))
        return img

    G["us"] = us_frames


def render_frame(fr):
    t = fr / FPS
    rng = np.random.default_rng(1000 + fr)
    img, parts = base_image(G["frames"], fr, G["anchors"])
    img = grade(img, fr, rng)
    ov = overlay(fr, t, G["anchors"], G["cues"], G["us"], G["logo"])
    img = ov[..., :3] + img * (1 - ov[..., 3:4])
    # dithering ligero antes de cuantizar a 8 bits
    img = np.clip(img * 255 + rng.uniform(-0.5, 0.5, img.shape[:2])[..., None], 0, 255).astype(np.uint8)
    return img


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--frames", required=True)
    ap.add_argument("--anchors", default="")
    ap.add_argument("--timeline", required=True)
    ap.add_argument("--audio", default="")
    ap.add_argument("--out", default="")
    ap.add_argument("--srt", default="")
    ap.add_argument("--preview", default="")
    ap.add_argument("--preview-dir", default="")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--logo", default="")
    ap.add_argument("--crf", type=int, default=17)
    args = ap.parse_args()
    init_worker(args.frames, args.anchors, args.timeline, args.logo)
    if args.srt:
        write_srt(G["cues"], args.srt)
    if args.preview:
        os.makedirs(args.preview_dir, exist_ok=True)
        for fr in [int(x) for x in args.preview.split(",")]:
            img = render_frame(fr)
            Image.fromarray(img).save(os.path.join(args.preview_dir, f"comp_{fr:04d}.png"))
            print("preview", fr, flush=True)
        return
    from multiprocessing import Pool
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
           "-r", str(FPS), "-i", "-"]
    if args.audio:
        cmd += ["-i", args.audio, "-map", "0:v:0", "-map", "1:a:0", "-c:a", "aac", "-b:a", "256k", "-ar", "48000",
                "-ac", "2"]
    cmd += ["-c:v", "libx264", "-preset", "slow", "-crf", str(args.crf), "-profile:v", "high", "-level", "4.2",
            "-pix_fmt", "yuv420p", "-x264-params", "keyint=60:min-keyint=30:aq-mode=3:deblock=-1,-1",
            "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
            "-movflags", "+faststart", "-t", f"{TOTAL_FRAMES / FPS:.3f}", args.out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(args.workers, initializer=init_worker,
              initargs=(args.frames, args.anchors, args.timeline, args.logo)) as pool:
        for i, img in enumerate(pool.imap(render_frame, range(TOTAL_FRAMES), chunksize=4)):
            proc.stdin.write(img.tobytes())
            if i % 60 == 0:
                print(f"frame {i}/{TOTAL_FRAMES}", flush=True)
    proc.stdin.close()
    proc.wait()
    print("OK", args.out, flush=True)


if __name__ == "__main__":
    main()
