"""Plano 4 (29.8–40.3 s): LA CIRCULACIÓN CONTINÚA.
1) Primer plano de la vena tratada, ahora un cordón fibroso pálido que se va desvaneciendo (reabsorción).
2) Alejamiento: red venosa completa en rayos X; la sangre sube hacia el corazón por la safena mayor y menor,
   las perforantes y, sobre todo, por el sistema venoso profundo.
3) Comparación anatómica: ANTES (tributaria varicosa dilatada con reflujo) / DESPUÉS (cordón fibroso, flujo
   por venas funcionales). La forma de la pierna no cambia: no se exageran resultados."""
import os

import numpy as np

from lib import bl, looks
from lib.anatomy import load_leg_assets

RENDER = dict(res=(960, 1707), spp=8, threshold=0.05, bounces=(4, 1, 2, 4, 16), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

BEFORE_OFF = np.array([0.0, 0.40, 0.0])   # pierna "ANTES" a la izquierda de pantalla (vista medial)
FLOW = (1.0, 0.10, 0.07)


def polar(theta, dist, z, cy=-0.016, off=(0.0, 0.0)):
    th = np.radians(theta)
    return np.array([-np.sin(th) * dist + off[0], np.cos(th) * dist + cy + off[1], z])


def orient(pts, radius, kind):
    """Ordena los puntos para que 'u' crezca en el sentido del flujo fisiológico (hacia el corazón; en
    perforantes, de superficial a profunda)."""
    if kind in ("superficial", "deep") and pts[0][2] > pts[-1][2]:
        return pts[::-1], radius[::-1]
    return pts, radius


def leg_set(A, prefix, offset, before, mats):
    objs = []
    skin_v = A["skinvar_v"] if before else A["skin_v"]
    skin_f = A["skinvar_f"] if before else A["skin_f"]
    objs.append(bl.mesh_object(prefix + "Skin", skin_v + offset, skin_f, mat=mats["skin"]))
    objs.append(bl.mesh_object(prefix + "Muscle", A["muscle_v"] + offset, A["muscle_f"], mat=mats["muscle"]))
    objs.append(bl.mesh_object(prefix + "Bone", A["bone_v"] + offset, A["bone_f"], mat=mats["bone"]))
    for k, d in A["veins"].items():
        pts, rad = orient(d["pts"], d["radius"], d["kind"])
        kind = d["kind"]
        if kind == "varicose":
            if before:
                m = mats["varicose"]
            else:
                m = mats["cord"]
                rad = rad * 0.36
        else:
            m = mats[kind]
        objs.append(bl.tube_mesh(f"{prefix}V_{k}", pts + offset, rad, n_ring=12, mat=m, u_mode="length"))
    return objs


def make_mats(tag, before):
    M = {}
    M["skin"] = looks.skin_reveal(f"Skin{tag}")
    M["muscle"] = looks.xray_layer(f"Muscle{tag}", rim=(0.85, 0.20, 0.16), strength=0.22, power=2.6,
                                   fill=(0.25, 0.03, 0.03), fill_strength=0.006)
    M["bone"] = looks.xray_layer(f"Bone{tag}", rim=(0.70, 0.80, 1.0), strength=0.22, power=2.2,
                                 fill=(0.4, 0.45, 0.55), fill_strength=0.006)
    kw = dict(flow=True, flow_color=FLOW, flow_density=8.0)
    M["superficial"] = looks.vein(f"VSup{tag}", base=(0.02, 0.05, 0.30), glow=(0.06, 0.25, 1.0), glow_strength=0.75,
                                  flow_speed=0.13, **kw)
    M["deep"] = looks.vein(f"VDeep{tag}", base=(0.02, 0.05, 0.32), glow=(0.05, 0.20, 0.95), glow_strength=0.6,
                           flow_speed=0.16, **kw)
    M["perforator"] = looks.vein(f"VPerf{tag}", base=(0.03, 0.10, 0.35), glow=(0.10, 0.45, 1.0), glow_strength=0.6,
                                 flow_speed=0.05, **kw)
    M["reticular"] = looks.vein(f"VRet{tag}", base=(0.12, 0.03, 0.26), glow=(0.40, 0.12, 0.95), glow_strength=0.55)
    M["varicose"] = looks.vein(f"VVar{tag}", base=(0.08, 0.01, 0.17), glow=(0.42, 0.05, 0.95), glow_strength=0.6,
                               flow=True, flow_color=(0.95, 0.06, 0.25), flow_speed=0.06, flow_density=26.0)
    M["cord"] = looks.vein(f"VCord{tag}", base=(0.55, 0.50, 0.52), glow=(0.35, 0.33, 0.36), glow_strength=0.5)
    for m in M.values():
        if "dim" in m.node_tree.nodes and m is M["cord"]:
            bl.set_value(m, "dim", 1.0)
    return M


def build(sc, ctx):
    A = load_leg_assets(os.path.join(ctx["assets"], "leg.npz"))
    bl.world(sc, top=(0.010, 0.030, 0.070), bottom=(0.0, 0.003, 0.010))
    after = make_mats("A", False)
    before = make_mats("B", True)
    leg_set(A, "A_", np.zeros(3), False, after)
    leg_set(A, "B_", BEFORE_OFF, True, before)
    for m in (after["skin"], before["skin"]):
        bl.set_value(m, "xray", 1.0)
        bl.set_value(m, "scan_z", -0.2)
        bl.set_value(m, "rim_k", 0.9)

    rng = np.random.default_rng(3)
    n = 240
    dust0 = np.column_stack([rng.uniform(-1.6, 1.2, n), rng.uniform(-1.6, 1.8, n), rng.uniform(-0.3, 1.3, n)])
    dust = bl.points_object("Dust", dust0, rng.uniform(0.001, 0.0035, n),
                            mat=bl.emission_mat("Dust", (0.35, 0.60, 1.0), 1.2))
    dust_v = rng.normal(0, 0.01, (n, 3))

    bl.area_light(sc, "Key", (-1.4, 0.6, 1.4), (0, 0.2, 0.40), 55, size=0.9, color=(1.0, 0.90, 0.80))
    bl.area_light(sc, "RimL", (0.9, 1.8, 1.0), (0, 0.2, 0.4), 150, size=0.6, color=(0.45, 0.68, 1.0))
    bl.area_light(sc, "RimR", (1.2, -1.2, 0.8), (0, 0.2, 0.4), 140, size=0.6, color=(0.60, 0.80, 1.0))
    bl.area_light(sc, "Top", (0.0, 0.2, 2.2), (0, 0.2, 0.4), 25, size=1.5, color=(0.85, 0.9, 1.0))

    cam = bl.camera(sc, lens=70, clip=(0.01, 30), dof=(0.45, 3.2))
    mid = BEFORE_OFF * 0.5
    cam_keys = [(0.0, polar(141, 0.42, 0.30)), (1.8, polar(138, 0.55, 0.31)), (5.4, polar(118, 2.15, 0.47)),
                (7.4, polar(104, 2.75, 0.47, off=(mid[0], mid[1]))), (10.5, polar(100, 2.85, 0.47, off=(mid[0], mid[1])))]
    tgt_keys = [(0.0, (-0.040, -0.042, 0.295)), (1.8, (-0.040, -0.040, 0.30)), (5.4, (0.0, 0.0, 0.45)),
                (7.4, (0.0, mid[1], 0.455)), (10.5, (0.0, mid[1], 0.455))]
    fstop_keys = [(0.0, (3.2,)), (3.0, (6.0,)), (5.4, (9.0,)), (10.5, (10.0,))]

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        cam.data.dof.aperture_fstop = float(bl.hermite_path(t, fstop_keys)[0])
        bl.set_camera(cam, p, g, focus=np.linalg.norm(p - g))
        # reabsorción progresiva del cordón fibroso
        bl.set_value(after["cord"], "vis", float(1.0 - 0.6 * bl.smoothstep(0.8, 5.5, t)))
        # flujo fisiológico hacia el corazón en las venas funcionales
        fk = 0.95 * bl.smoothstep(1.2, 3.2, t)
        for key in ("superficial", "deep", "perforator"):
            bl.set_value(after[key], "flow_t", float(t))
            bl.set_value(after[key], "flow_k", float(fk))
            bl.set_value(before[key], "flow_t", float(t))
            bl.set_value(before[key], "flow_k", float(fk if key == "deep" else 0.0))
        # pierna "ANTES": aparece para la comparación, con reflujo descendente en la várice
        vb = float(bl.smoothstep(5.6, 6.8, t))
        for m in before.values():
            if "vis" in m.node_tree.nodes:
                bl.set_value(m, "vis", vb)
        bl.set_value(before["varicose"], "flow_t", float(t))
        bl.set_value(before["varicose"], "flow_k", 1.1 * vb)
        bl.set_value(before["varicose"], "pulse", float(0.18 * (0.5 + 0.5 * np.sin(2 * np.pi * 0.9 * t))))
        bl.update_points(dust, dust0 + dust_v * t)

    return update


def anchors(t):
    return {"after_foot": (0.0, 0.05, -0.02), "before_foot": tuple(BEFORE_OFF + np.array([0.0, 0.05, -0.02])),
            "cord": (-0.0319, -0.0618, 0.3107)}
