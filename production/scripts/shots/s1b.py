"""Plano 1B (4.1–8.3 s): dentro de una vena varicosa. Válvula bicúspide incompetente: las valvas no
coaptan (hueco central) y los glóbulos rojos retroceden hacia abajo (reflujo, hacia el pie) y se acumulan
en el segmento dilatado. La cámara desciende acompañando el reflujo."""
import numpy as np

from lib import bl, looks, micro
from lib.anatomy import rbc_mesh

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(4, 1, 2, 3, 8), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

GAP = 0.60
VALVE_Z = 0.35
FOG = (0.10, 0.008, 0.012)
DENS = 0.21


def build(sc, ctx):
    bl.world(sc, top=FOG, bottom=FOG, strength=1.0)
    wall_m = looks.vessel_wall("Wall", base=(0.40, 0.06, 0.07), fog=FOG, fog_density=DENS, translucent=0.45,
                               noise_scale=2.2, bump_strength=0.4, emission=0.02)
    v, f = micro.vessel_wall()
    bl.mesh_object("Wall", v, f, mat=wall_m)
    cusp_m = looks.membrane("Cusp", color=(0.88, 0.52, 0.50), fog=FOG, fog_density=DENS, translucent=0.55, emission=0.06)
    for side in (1, -1):
        cv, cf, _ = micro.cusp(side=side, gap=GAP, valve_z=VALVE_Z)
        bl.mesh_object(f"Cusp{side}", cv, cf, mat=cusp_m)

    # glóbulos rojos
    rv, rf = rbc_mesh(R=1.0)
    rbc_obj = bl.mesh_object("RBC", rv * np.array([0.05, 0.05, 0.05]), rf, mat=looks.rbc(fog=FOG, fog_density=DENS))
    n = 1500

    def forbid(p):  # sin partículas dentro de los bolsillos valvulares al inicio
        return (np.abs(p[:, 0]) > GAP / 2 - 0.05) & (p[:, 2] < VALVE_Z + 0.1) & (p[:, 2] > VALVE_Z - 1.15)

    dt = 1 / 240
    pos, wrap = micro.simulate(n, 5.0, dt, lambda p: micro.reflux_velocity(p, GAP, VALVE_Z), bounds_z=(-5.5, 5.0),
                               radius_fn=micro.vessel_radius, seed=4, forbid=forbid, noise=0.07)
    track = micro.Track(pos, wrap, dt)
    p0, r0, _ = track.at(0)
    scale = np.random.default_rng(2).uniform(0.85, 1.12, n)
    cells = bl.instances_object("Cells", p0, rbc_obj, scale, r0)

    # iluminación: luz suave junto a la cámara + luces externas que atraviesan la pared (translucidez)
    cam = bl.camera(sc, lens=17, clip=(0.01, 60), dof=(1.3, 2.4))
    key = bl.point_light(sc, "CamLight", (0, 0, 0), 22, radius=0.25, color=(1.0, 0.86, 0.80))
    for i, (zz, ang) in enumerate([(2.5, 0.3), (0.5, 2.2), (-1.5, 4.1), (-3.5, 1.2), (4.5, 3.4)]):
        bl.point_light(sc, f"Out{i}", (2.0 * np.cos(ang), 2.0 * np.sin(ang), zz), 650, radius=0.6,
                       color=(1.0, 0.25, 0.18))
    bl.point_light(sc, "TopGlow", (0, 0.2, 3.2), 60, radius=0.4, color=(0.9, 0.75, 0.75))

    cam_keys = [(0.0, (0.00, -0.68, 2.15)), (2.2, (0.06, -0.66, 1.45)), (4.25, (0.12, -0.62, 0.98))]
    tgt_keys = [(0.0, (0.0, 0.50, 0.30)), (2.2, (0.0, 0.42, -0.15)), (4.25, (0.0, 0.36, -0.65))]

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        bl.set_camera(cam, p, g, focus=np.linalg.norm(np.array(g) - p) * 0.75)
        key.location = (p[0] + 0.05, p[1] + 0.1, p[2] + 0.25)
        pos_t, rot_t, hidden = track.at(t + 0.6)   # la simulación arranca antes (flujo ya establecido)
        sc_t = np.where(hidden, 0.0, scale)
        bl.update_points(cells, pos_t, scale=sc_t, rot=rot_t)

    return update


def anchors(t):
    """Puntos 3D para etiquetas: borde libre de la valva y chorro de reflujo."""
    return {"cusp_edge": (GAP / 2 + 0.08, 0.35, VALVE_Z - 0.05), "reflux": (0.0, 0.6, VALVE_Z - 1.0)}
