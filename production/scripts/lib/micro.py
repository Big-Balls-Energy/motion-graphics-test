"""Geometría y simulación del "micro-mundo" dentro de la vena (unidades: radio de la luz = 1)."""
import numpy as np


def vessel_radius(z, phi, dilate_below=0.18, sinus=0.07, valve_z=0.35):
    """Radio de la luz venosa: segmento dilatado bajo la válvula y senos valvulares (detrás de cada valva)."""
    below = np.clip((valve_z - 0.4 - z) / 2.2, 0, 1)
    below = below * below * (3 - 2 * below)
    sin_z = np.exp(-((z - (valve_z - 0.45)) / 0.55) ** 2)
    sin_phi = np.abs(np.cos(phi)) ** 2          # senos en los lados ±x (detrás de las valvas)
    return 1.0 + dilate_below * below + sinus * sin_z * sin_phi


def vessel_wall(z0=-7.0, z1=7.0, n_phi=110, n_z=300, seed=1, radius_fn=vessel_radius, fold=0.035):
    rng = np.random.default_rng(seed)
    zs = np.linspace(z0, z1, n_z)
    phis = np.linspace(0, 2 * np.pi, n_phi, endpoint=False)
    Z, PHI = np.meshgrid(zs, phis, indexing="ij")
    R = radius_fn(Z, PHI)
    # pliegues orgánicos longitudinales + ruido suave
    k = rng.uniform(0, 2 * np.pi, 6)
    fold_f = (np.sin(PHI * 7 + k[0] + 0.3 * np.sin(Z * 0.7 + k[1])) * 0.6
              + np.sin(PHI * 13 + Z * 0.4 + k[2]) * 0.3 + np.sin(Z * 2.1 + PHI * 3 + k[3]) * 0.4)
    R = R * (1 + fold * fold_f / 1.3)
    verts = np.stack([R * np.cos(PHI), R * np.sin(PHI), Z], -1).reshape(-1, 3)
    faces = []
    for i in range(n_z - 1):
        for j in range(n_phi):
            a = i * n_phi + j
            b = i * n_phi + (j + 1) % n_phi
            faces.append((a, a + n_phi, b + n_phi, b))   # normales hacia el interior
    return verts, np.array(faces, np.int32)


def cusp(side=1, gap=0.42, valve_z=0.35, depth=1.05, n_u=48, n_v=24, belly=0.30, sag=0.0, thickness=0.018):
    """Valva venosa (cúspide) en el lado x=side. Membrana con espesor (dos caras + borde).
    gap: separación entre bordes libres en el centro (incompetencia). belly: convexidad hacia la luz."""
    us = np.linspace(-1, 1, n_u)
    vs = np.linspace(0, 1, n_v)
    U, V = np.meshgrid(us, vs, indexing="ij")
    phi = U * (np.pi / 2) * 0.985
    Ra = vessel_radius(valve_z - depth * (1 - U ** 2), phi + (0 if side > 0 else np.pi)) * 0.985
    A = np.stack([side * Ra * np.cos(phi), Ra * np.sin(phi), valve_z - depth * (1 - U ** 2)], -1)
    xf = (gap / 2) * np.sqrt(np.clip(1 - U ** 2, 0, 1)) + 0.01
    F = np.stack([side * xf, 0.985 * np.sin(phi) * np.maximum(Ra, 0.9), valve_z + 0.06 * (1 - U ** 2) - sag * (1 - U ** 2)], -1)
    P = A + (F - A) * V[..., None]
    w = np.sin(np.pi * V) * (1 - U ** 2) ** 0.8
    P[..., 0] += -side * belly * w * 0.55      # convexo hacia la luz
    P[..., 2] += -belly * w * 0.65             # bolsillo hacia abajo
    # normales aproximadas para dar espesor
    du = np.gradient(P, axis=0)
    dv = np.gradient(P, axis=1)
    N = np.cross(du, dv)
    N /= np.linalg.norm(N, axis=-1, keepdims=True) + 1e-12
    th = thickness * (0.6 + 0.4 * (1 - V))[..., None]
    top = (P + N * th / 2).reshape(-1, 3)
    bot = (P - N * th / 2).reshape(-1, 3)
    verts = np.vstack([top, bot])
    nn = n_u * n_v
    faces = []
    for i in range(n_u - 1):
        for j in range(n_v - 1):
            a = i * n_v + j
            faces.append((a, a + 1, a + n_v + 1, a + n_v))
            faces.append((nn + a, nn + a + n_v, nn + a + n_v + 1, nn + a + 1))
    # borde libre (v = 1) cerrado con una tira
    for i in range(n_u - 1):
        a = i * n_v + (n_v - 1)
        b = (i + 1) * n_v + (n_v - 1)
        faces.append((a, b, nn + b, nn + a))
    return verts, np.array(faces, np.int32), P


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0, 1)
    return t * t * (3 - 2 * t)


def reflux_velocity(p, gap=0.42, valve_z=0.35):
    """Campo de velocidad del reflujo a través de una válvula incompetente (flujo descendente)."""
    x, y, z = p[:, 0], p[:, 1], p[:, 2]
    v = np.zeros_like(p)
    above = z > valve_z + 0.05
    k = smoothstep(2.8, valve_z + 0.05, z)
    slit = gap / 2 - 0.06
    # convergencia hacia la hendidura entre las valvas
    v[:, 0] = np.where(above, -np.sign(x) * np.maximum(np.abs(x) - slit * 0.6, 0) * 1.6 * k, 0)
    v[:, 2] = np.where(above, -(0.30 + 0.95 * k), 0)
    inslit = (~above) & (z > valve_z - 1.0)
    v[:, 0] = np.where(inslit, -x * 2.2, v[:, 0])
    v[:, 2] = np.where(inslit, -1.30, v[:, 2])
    below = z <= valve_z - 1.0
    d = np.maximum(valve_z - 1.0 - z, 0)
    jet = np.exp(-d / 1.1)
    v[:, 2] = np.where(below, -(0.22 + 1.05 * jet), v[:, 2])
    v[:, 0] = np.where(below, x * 0.55 * jet, v[:, 0])
    v[:, 1] = np.where(below, y * 0.35 * jet, v[:, 1])
    # recirculación (vórtices) bajo las valvas: componente en el plano x-z
    for cx in (-0.62, 0.62):
        dx = x - cx
        dz = z - (valve_z - 1.25)
        r2 = dx ** 2 + dz ** 2
        s = 0.55 * np.exp(-r2 / 0.18) * np.sign(cx)
        v[:, 0] += -dz * s
        v[:, 2] += dx * s
    return v


def simulate(n, t_end, dt, vel_fn, bounds_z=(-5.0, 5.0), radius_fn=None, seed=0, init=None, margin=0.08,
             noise=0.06, forbid=None):
    """Integra partículas en el campo vel_fn. Devuelve pos[T, n, 3], wrap[T, n] (bool: reaparición)."""
    rng = np.random.default_rng(seed)
    z0, z1 = bounds_z
    if init is None:
        r = np.sqrt(rng.uniform(0, 1, n)) * 0.9
        a = rng.uniform(0, 2 * np.pi, n)
        p = np.column_stack([r * np.cos(a), r * np.sin(a), rng.uniform(z0, z1, n)])
    else:
        p = init.copy()
    if forbid is not None:
        bad = forbid(p)
        while bad.any():
            r = np.sqrt(rng.uniform(0, 1, bad.sum())) * 0.9
            a = rng.uniform(0, 2 * np.pi, bad.sum())
            p[bad] = np.column_stack([r * np.cos(a), r * np.sin(a), rng.uniform(z0, z1, bad.sum())])
            bad = forbid(p)
    steps = int(np.ceil(t_end / dt)) + 1
    out = np.empty((steps, n, 3), np.float32)
    wrap = np.zeros((steps, n), bool)
    phase = rng.uniform(0, 100, (n, 3))
    for i in range(steps):
        out[i] = p
        v = vel_fn(p)
        # ruido suave (turbulencia) por partícula
        tt = i * dt
        v += noise * np.sin(phase + tt * np.array([1.3, 1.7, 1.1]))
        p = p + v * dt
        if radius_fn is not None:
            rr = np.linalg.norm(p[:, :2], axis=1)
            phi = np.arctan2(p[:, 1], p[:, 0])
            rmax = radius_fn(p[:, 2], phi) - margin
            over = rr > rmax
            p[over, :2] *= (rmax[over] / rr[over])[:, None]
        w = p[:, 2] < z0
        if w.any():
            r = np.sqrt(rng.uniform(0, 1, w.sum())) * 0.88
            a = rng.uniform(0, 2 * np.pi, w.sum())
            p[w] = np.column_stack([r * np.cos(a), r * np.sin(a), np.full(w.sum(), z1)])
            if i + 1 < steps:
                wrap[i + 1, w] = True
    return out, wrap


class Track:
    """Interpolación temporal de una simulación precomputada (para subframes / motion blur)."""

    def __init__(self, pos, wrap, dt, rot_speed=None, seed=0):
        self.pos, self.wrap, self.dt = pos, wrap, dt
        n = pos.shape[1]
        rng = np.random.default_rng(seed + 11)
        self.rot0 = rng.uniform(0, 2 * np.pi, (n, 3))
        self.rot_speed = rng.normal(0, 1.4, (n, 3)) if rot_speed is None else rot_speed

    def at(self, t):
        f = np.clip(t / self.dt, 0, len(self.pos) - 1.001)
        i = int(f)
        u = f - i
        p = self.pos[i] * (1 - u) + self.pos[i + 1] * u
        # ocultar partículas que reaparecen cerca de t (evita estelas de motion blur)
        k = int(round(1.0 / 30 / self.dt)) + 1
        lo, hi = max(i - k, 0), min(i + k + 1, len(self.wrap))
        hidden = self.wrap[lo:hi].any(axis=0)
        rot = self.rot0 + self.rot_speed * t
        return p, rot, hidden
