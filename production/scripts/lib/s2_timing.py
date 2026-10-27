"""Tiempos del plano 2 (sin dependencias de Blender): compartidos entre el render 3D y el inserto ecográfico."""
import numpy as np


def _smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def _ease_in_out(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def _ease_out(t):
    t = np.clip(t, 0, 1)
    return 1 - (1 - t) ** 3


S_FINAL = 1.22   # avance final de la punta (cm) a lo largo de la aguja


def needle_s(t):
    """Avance de la punta (cm desde el punto de entrada en la piel) según el tiempo local del plano."""
    return float(-0.9 + (S_FINAL + 0.9) * _ease_in_out((t - 2.0) / 2.7))


def flashback(t):
    return float(_smoothstep(4.75, 5.6, t))


def probe_drop(t):
    return float(1.0 - _ease_out((t - 0.15) / 1.2))


def beam_on(t):
    return float(_smoothstep(1.2, 2.0, t))


def foam_out(t):
    return float(_smoothstep(7.4, 8.4, t))
