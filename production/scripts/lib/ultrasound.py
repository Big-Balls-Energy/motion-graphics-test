"""Inserto ecográfico procedural (modo B, corte longitudinal) sincronizado con el plano 2.

Geometría compartida con shots/s2.py (unidades en cm): transductor lineal sobre x ∈ [-1.0, 2.8], profundidad
0–3.0 cm. Vena varicosa a 0.85 cm (radio 0.33 cm): luz anecoica con paredes ecogénicas. La aguja entra en el
plano desde la izquierda (línea hiperecogénica con artefacto de reverberación) y su punta alcanza la luz.
Al final, la microespuma aparece como contenido muy ecogénico que se extiende por la luz, con sombra acústica
posterior (hallazgo característico de la espuma en ecografía)."""
import math

import numpy as np
from scipy.ndimage import gaussian_filter

X0, X1 = -2.0, 1.8      # campo lateral del inserto (incluye todo el trayecto de la aguja en plano)
DEPTH = 3.0
VEIN_D = 0.85
VEIN_R = 0.33
FASCIA_D = 1.72
ENTRY_X = -1.75
ANG = math.radians(34)


class Ultrasound:
    def __init__(self, w=420, h=330, seed=3):
        self.w, self.h = w, h
        rng = np.random.default_rng(seed)
        self.rng = rng
        self.xs = np.linspace(X0, X1, w)
        self.ds = np.linspace(0, DEPTH, h)
        X, D = np.meshgrid(self.xs, self.ds)
        self.X, self.D = X, D
        # mapa de ecogenicidad de los tejidos
        e = np.full((h, w), 0.35)
        e[D < 0.05] = 1.0                                         # gel/epidermis
        e[(D >= 0.05) & (D < 0.24)] = 0.75                         # dermis
        fat = (D >= 0.24) & (D < FASCIA_D)
        sept = gaussian_filter(rng.normal(0, 1, (h, w)), (3, 9))
        e[fat] = 0.16 + 0.55 * (np.abs(sept[fat]) < 0.035)         # lóbulos hipoecoicos con septos
        e[(D >= FASCIA_D) & (D < FASCIA_D + 0.07)] = 1.0           # fascia
        mus = D >= FASCIA_D + 0.07
        e[mus] = 0.45 + 0.25 * (np.sin(D[mus] * 60 + 0.4 * np.sin(X[mus] * 3)) > 0.6)
        vz = VEIN_D + 0.03 * np.sin(X * 0.9 + 0.4)
        vr = VEIN_R * (1 + 0.05 * np.sin(X * 2.1 + 1.0))
        dist = np.abs(D - vz)
        self.lumen = dist < vr * 0.86
        wall = (dist >= vr * 0.86) & (dist < vr * 1.05)
        e[self.lumen] = 0.03
        e[wall] = 0.95
        self.vz, self.vr = vz, vr
        self.base = e
        self.speckle = self._speckle()

    def _speckle(self):
        n = self.rng.normal(0, 1, (self.h, self.w)) + 1j * self.rng.normal(0, 1, (self.h, self.w))
        s = np.abs(gaussian_filter(n.real, (1.3, 3.2)) + 1j * gaussian_filter(n.imag, (1.3, 3.2)))
        return s / s.mean()

    def frame(self, needle_s, foam):
        """needle_s: avance de la punta (cm); foam: 0..1 extensión de la espuma en la luz."""
        e = self.base.copy()
        X, D = self.X, self.D
        # espuma: contenido hiperecogénico que se extiende desde la punta + sombra acústica
        if foam > 0:
            tip_x = ENTRY_X + math.cos(ANG) * needle_s
            reach = foam * 3.2
            # bordes suaves: la espuma se extiende desde la punta con un frente difuso
            w = 1.0 / (1.0 + np.exp((np.abs(X - tip_x) - reach) / 0.12))
            lum = gaussian_filter(self.lumen.astype(float), 1.2)
            e = e * (1 - w * lum) + 1.3 * w * lum
            below = 1.0 / (1.0 + np.exp(-(D - (self.vz + self.vr)) / 0.05))
            e = e * (1 - 0.62 * w * below)
        # aguja: línea hiperecogénica + reverberación (cola de cometa) bajo el eje
        tip_x = ENTRY_X + math.cos(ANG) * needle_s
        tip_d = math.sin(ANG) * needle_s
        if needle_s > 0:
            # distancia de cada píxel a la recta de la aguja (solo el tramo insertado)
            px = X - ENTRY_X
            along = px * math.cos(ANG) + D * math.sin(ANG)
            perp = -px * math.sin(ANG) + D * math.cos(ANG)
            on = (along > 0) & (along < needle_s) & (np.abs(perp) < 0.026)
            e[on] = 2.2
            for k in range(1, 4):
                rev = (along > 0) & (along < needle_s) & (np.abs(perp - 0.07 * k) < 0.012)
                e[rev] = np.maximum(e[rev], 0.9 - 0.2 * k)
        img = e * self.speckle * (0.85 + 0.15 * self.rng.random((self.h, self.w)))
        img = gaussian_filter(img, (0.6, 1.0))
        # ganancia en profundidad (TGC) y compresión logarítmica
        img *= 1.0 - 0.25 * (D / DEPTH)
        img = np.log1p(img * 4) / np.log1p(7)
        img = np.clip(img, 0, 1)
        # haz con forma de abanico suave en los bordes laterales
        edge = np.clip(np.minimum(X - X0, X1 - X) / 0.15, 0, 1)
        img *= edge
        g = (img * 255).astype(np.uint8)
        rgb = np.stack([g, g, (g * 1.0).clip(0, 255).astype(np.uint8)], -1)
        return rgb, (tip_x, tip_d)

    def to_px(self, x, d):
        return ((x - X0) / (X1 - X0) * (self.w - 1), d / DEPTH * (self.h - 1))
