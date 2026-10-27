"""Plano 1A (0.0–4.5 s): pierna con piel realista -> barrido de escáner -> piel semitransparente con
red venosa (safenas, profundas, perforantes) -> acercamiento a la tributaria varicosa de la pantorrilla medial.
Pulsos tenues descendentes en la várice sugieren el reflujo (sangre que retrocede)."""
import os

import numpy as np

from lib import bl, looks
from lib.anatomy import load_leg_assets

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(4, 1, 2, 4, 16), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")


def build(sc, ctx):
    A = load_leg_assets(os.path.join(ctx["assets"], "leg.npz"))
    bl.world(sc, top=(0.010, 0.030, 0.070), bottom=(0.0, 0.003, 0.010))

    skin = looks.skin_reveal()
    bl.mesh_object("Skin", A["skinvar_v"], A["skinvar_f"], mat=skin)
    muscle = looks.xray_layer("Muscle", rim=(0.85, 0.20, 0.16), strength=0.22, power=2.6,
                              fill=(0.25, 0.03, 0.03), fill_strength=0.006)
    bl.mesh_object("Muscle", A["muscle_v"], A["muscle_f"], mat=muscle)
    bone = looks.xray_layer("Bone", rim=(0.70, 0.80, 1.0), strength=0.22, power=2.2,
                            fill=(0.4, 0.45, 0.55), fill_strength=0.006)
    bl.mesh_object("Bone", A["bone_v"], A["bone_f"], mat=bone)

    mats = {
        "superficial": looks.vein("VeinSup", base=(0.02, 0.05, 0.30), glow=(0.06, 0.25, 1.0), glow_strength=0.75),
        "deep": looks.vein("VeinDeep", base=(0.02, 0.05, 0.32), glow=(0.05, 0.20, 0.95), glow_strength=0.55),
        "perforator": looks.vein("VeinPerf", base=(0.03, 0.10, 0.35), glow=(0.10, 0.45, 1.0), glow_strength=0.6),
        "reticular": looks.vein("VeinRet", base=(0.12, 0.03, 0.26), glow=(0.40, 0.12, 0.95), glow_strength=0.55),
        "varicose": looks.vein("VeinVar", base=(0.08, 0.01, 0.17), glow=(0.42, 0.05, 0.95), glow_strength=0.6,
                               flow=True, flow_color=(0.95, 0.06, 0.25), flow_speed=0.22, flow_density=9.0),
    }
    for k, d in A["veins"].items():
        bl.tube_mesh(f"V_{k}", d["pts"], d["radius"], n_ring=12, mat=mats[d["kind"]])

    # partículas de ambiente (bokeh)
    rng = np.random.default_rng(3)
    n = 220
    dust0 = np.column_stack([rng.uniform(-1.4, 1.0, n), rng.uniform(-1.6, 1.4, n), rng.uniform(-0.3, 1.3, n)])
    dust_r = rng.uniform(0.001, 0.0035, n)
    dust_mat = bl.emission_mat("Dust", (0.35, 0.60, 1.0), 1.2)
    dust = bl.points_object("Dust", dust0, dust_r, mat=dust_mat)
    dust_v = rng.normal(0, 0.01, (n, 3))

    # luces: clave cálida desde el lado de cámara, contraluces fríos que dibujan el borde
    bl.area_light(sc, "Key", (-1.4, 0.6, 1.4), (0, 0, 0.40), 55, size=0.9, color=(1.0, 0.90, 0.80))
    bl.area_light(sc, "RimL", (0.9, 1.4, 1.0), (0, 0, 0.4), 150, size=0.6, color=(0.45, 0.68, 1.0))
    bl.area_light(sc, "RimR", (1.2, -1.2, 0.8), (0, 0, 0.4), 140, size=0.6, color=(0.60, 0.80, 1.0))
    bl.area_light(sc, "Top", (0.0, 0.0, 2.2), (0, 0, 0.4), 25, size=1.5, color=(0.85, 0.9, 1.0))
    bl.area_light(sc, "Under", (-0.6, -0.6, -0.6), (0, 0, 0.3), 10, size=1.0, color=(0.4, 0.55, 1.0))

    cam = bl.camera(sc, lens=75, clip=(0.01, 30), dof=(2.2, 6.0))

    # trayectoria de cámara: plano general medial -> órbita posteromedial -> primer plano de la várice
    def polar(theta, dist, z):
        th = np.radians(theta)
        return np.array([-np.sin(th) * dist, np.cos(th) * dist - 0.016, z])

    cam_keys = [(0.0, polar(112, 2.25, 0.50)), (1.6, polar(118, 2.0, 0.47)), (3.0, polar(132, 0.95, 0.35)),
                (4.5, polar(140, 0.40, 0.30))]
    tgt_keys = [(0.0, (0.0, 0.02, 0.475)), (1.6, (0.0, 0.0, 0.45)), (3.0, (-0.03, -0.03, 0.31)),
                (4.5, (-0.040, -0.042, 0.295))]
    fstop_keys = [(0.0, (8.0,)), (2.0, (6.0,)), (4.5, (3.2,))]

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        cam.data.dof.aperture_fstop = float(bl.hermite_path(t, fstop_keys)[0])
        bl.set_camera(cam, p, g, focus=np.linalg.norm(p - g) * 0.99)
        # barrido del escáner de arriba hacia abajo
        u = bl.ease_in_out((t - 0.85) / 1.75)
        bl.set_value(skin, "xray", 1.0)
        bl.set_value(skin, "scan_z", float(bl.lerp(1.02, -0.06, u)))
        bl.set_value(skin, "scan_glow", float(9.0 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.5))
        bl.set_value(skin, "rim_k", float(0.55 + 0.35 * u))
        # várice: pulso de estasis y flujo retrógrado (descendente)
        vv = mats["varicose"]
        bl.set_value(vv, "pulse", float(0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t))))
        bl.set_value(vv, "flow_t", float(t))
        bl.set_value(vv, "flow_k", float(1.1 * bl.smoothstep(2.3, 3.2, t)))
        bl.update_points(dust, dust0 + dust_v * t)

    return update


def anchors(t):
    return {"varicose": (-0.0319, -0.0618, 0.3107), "gsv": (-0.0562, -0.0259, 0.6202)}
