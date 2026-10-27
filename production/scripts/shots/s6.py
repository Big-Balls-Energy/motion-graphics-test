"""Plano 6 (49.8–60.0 s): cierre institucional. Las líneas de la red venosa de la pierna se desprenden y se
reorganizan en un fondo elegante de trazos luminosos azules/blancos que fluyen (red venosa -> identidad).
Los textos, sedes, CTA y el logotipo se componen en 2D sobre este fondo (áreas seguras de Reels)."""
import os

import numpy as np

from lib import bl, looks
from lib.anatomy import load_leg_assets, resample

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(2, 0, 1, 2, 8), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

NPTS = 90


def target_lines(n_lines, rng):
    """Trazos ondulantes verticales, en abanico suave alrededor del centro (fondo de marca)."""
    out = []
    for i in range(n_lines):
        u = (i // 2 + 0.5) / (n_lines // 2)
        side = 1 if i % 2 else -1
        x0 = side * (0.30 + 0.48 * u)            # dos haces laterales: el centro queda limpio para la marca
        depth = rng.uniform(-0.35, 0.35)
        amp = rng.uniform(0.02, 0.06)
        freq = rng.uniform(2.0, 4.5)
        ph = rng.uniform(0, 6.28)
        z = np.linspace(-0.45, 1.35, NPTS)
        x = x0 * (1 + 0.22 * np.cos((z - 0.45) * 1.8)) + amp * np.sin(freq * z + ph)
        out.append(np.column_stack([x, np.full(NPTS, depth), z]))
    return out


def build(sc, ctx):
    rng = np.random.default_rng(66)
    A = load_leg_assets(os.path.join(ctx["assets"], "leg.npz"))
    bl.world(sc, top=(0.006, 0.020, 0.055), bottom=(0.0, 0.002, 0.008))
    names = [k for k, d in A["veins"].items() if d["kind"] in ("superficial", "deep", "perforator", "reticular")]
    src = []
    for k in names:
        p = A["veins"][k]["pts"]
        p = resample(p, max(np.linalg.norm(np.diff(p, axis=0), axis=1).sum() / (NPTS - 1), 1e-4))
        idx = np.linspace(0, len(p) - 1, NPTS).astype(int)
        # la pierna se ve de lado (vista medial): se rota para que mire a cámara (x <- -y)
        q = p[idx][:, [1, 0, 2]] * np.array([1.0, -1.0, 1.0])
        src.append(q)
    n_lines = 26
    while len(src) < n_lines:
        j = rng.integers(0, len(src))
        src.append(src[j] + rng.normal(0, 0.004, 3))
    src = src[:n_lines]
    tgt = target_lines(n_lines, rng)
    delay = rng.uniform(0.0, 0.9, n_lines)
    cols = [(0.20, 0.55, 1.0), (0.45, 0.80, 1.0), (0.85, 0.93, 1.0), (0.10, 0.35, 0.95)]
    mats = [bl.emission_mat(f"Line{i}", cols[i % len(cols)], 1.0) for i in range(4)]
    curves = []
    for i in range(n_lines):
        c = bl.tube_object(f"L{i}", src[i], np.full(NPTS, 0.0025), mat=mats[i % 4], bevel_res=2)
        curves.append(c)
    # partículas/bokeh
    nd = 260
    dust0 = np.column_stack([rng.uniform(-1.4, 1.4, nd), rng.uniform(-0.6, 1.4, nd), rng.uniform(-0.6, 1.5, nd)])
    dust = bl.points_object("Dust", dust0, rng.uniform(0.002, 0.007, nd),
                            mat=bl.emission_mat("Dust", (0.35, 0.65, 1.0), 1.6))
    dust_v = rng.normal(0, 0.012, (nd, 3)) + np.array([0, 0, 0.01])
    # anillo de luz suave tras la zona del logotipo
    ang = np.linspace(0, 2 * np.pi, 121)
    halo_pts = np.column_stack([0.36 * np.cos(ang), np.full(121, 0.35), 0.62 + 0.36 * np.sin(ang)])
    halo_m = bl.emission_mat("Halo", (0.35, 0.70, 1.0), 0.0)
    halo_pts[:, 1] = 0.0
    bl.tube_object("Halo", halo_pts, np.full(121, 0.0018), mat=halo_m, bevel_res=2)

    cam = bl.camera(sc, lens=50, clip=(0.01, 30), dof=(2.6, 1.6))
    cam_keys = [(0.0, (0.0, -2.55, 0.45)), (10.2, (0.0, -2.25, 0.52))]
    tgt_keys = [(0.0, (0.0, 0.0, 0.45)), (10.2, (0.0, 0.0, 0.52))]

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        bl.set_camera(cam, p, g, focus=np.linalg.norm(p - g))
        for i, c in enumerate(curves):
            k = bl.ease_in_out((t - 0.3 - delay[i]) / 2.4)
            flow = 0.01 * np.sin(np.linspace(0, 6.28, NPTS) * 2 + t * 1.2 + i)
            pts = src[i] + (tgt[i] - src[i]) * k
            pts = pts + np.column_stack([flow * k, np.zeros(NPTS), np.zeros(NPTS)])
            co = np.hstack([pts, np.ones((NPTS, 1))]).astype(np.float32)
            c.data.splines[0].points.foreach_set("co", co.ravel())
            c.data.splines[0].points.foreach_set("radius", np.full(NPTS, 1.0 + 0.6 * k, np.float32) * 0.0025 / 0.0025)
            c.data.bevel_depth = 0.0019
        for i, m in enumerate(mats):
            m.node_tree.nodes["Emission"].inputs[1].default_value = float(1.6 - 1.0 * bl.smoothstep(2.5, 4.5, t))
        halo_m.node_tree.nodes["Emission"].inputs[1].default_value = float(1.2 * bl.smoothstep(2.6, 4.2, t))
        bl.update_points(dust, dust0 + dust_v * t)

    return update
