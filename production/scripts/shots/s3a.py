"""Plano 3A (15.8–20.8 s): MICROESPUMA. Dentro de la vena, la espuma esclerosante sale por el bisel de la
microaguja, ocupa toda la luz y avanza como un tapón ("plug flow"): desplaza la sangre por delante en lugar
de mezclarse con ella, y queda en contacto con el endotelio de la pared. No es pegamento: es una espuma de
microburbujas de gas en solución esclerosante.
Unidades: radio de la luz venosa = 1 (las burbujas y los eritrocitos están estilizados en tamaño)."""
import math

import numpy as np

from lib import bl, looks, micro
from lib.anatomy import rbc_mesh

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(4, 1, 2, 4, 10), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

FOG = (0.10, 0.008, 0.012)
DENS = 0.17
TIP = np.array([0.0, 0.78, 2.35])     # punta de la aguja (pared superior)
L_MAX = 10.0


def straight_radius(z, phi):
    return 1.0 + 0.04 * np.sin(z * 0.5) + 0.0 * phi


def front(t):
    """Posición z del frente de la espuma (avanza hacia -z, desacelerando)."""
    u = np.clip(t / 4.6, 0, 1)
    return 2.25 - 7.4 * (1 - (1 - u) ** 2.2) - 0.25 * min(t, 0.4)


def growth(t):
    return float(bl.smoothstep(0.0, 0.9, t))


def plug_radius(u, g):
    """Radio del tapón de espuma a distancia u del frente (casquete frontal redondeado)."""
    return 0.94 * np.sqrt(np.clip(u / 0.75, 0, 1)) * (0.22 + 0.78 * g)


def build(sc, ctx):
    rng = np.random.default_rng(12)
    bl.world(sc, top=FOG, bottom=FOG)
    wall_m = looks.vessel_wall("Wall", base=(0.40, 0.06, 0.07), fog=FOG, fog_density=DENS, translucent=0.45,
                               noise_scale=2.2, bump_strength=0.35, emission=0.02)
    v, f = micro.vessel_wall(z0=-14, z1=6, n_z=360, radius_fn=straight_radius, seed=3)
    bl.mesh_object("Wall", v, f, mat=wall_m)

    # aguja que atraviesa la pared superior (bisel dentro de la luz)
    from shots.s2 import needle_mesh
    nv, nf = needle_mesh(4.0, 0.075)
    needle = bl.mesh_object("Needle", nv, nf, mat=bl.principled("Steel", base=(0.85, 0.87, 0.9), rough=0.14,
                                                                 metallic=1.0))
    ang = math.radians(34)
    needle.location = tuple(TIP)
    needle.rotation_euler = (-ang, 0.0, 0.0)     # eje +z local: hacia arriba (+y) y aguas arriba (+z)

    # --- microespuma: capa externa de burbujas + núcleo lechoso
    n_b = 3800
    u = rng.uniform(0, L_MAX, n_b * 3)
    rad = np.clip(rng.lognormal(math.log(0.06), 0.38, n_b * 3), 0.025, 0.16)
    phi = rng.uniform(0, 2 * np.pi, n_b * 3)
    # distribuir cerca de la superficie del tapón (capa de ~0.28)
    rmax = plug_radius(u, 1.0) - rad * 0.6
    depth = rng.uniform(0, 0.30, n_b * 3)
    r = rmax - depth
    keep = (r > 0) | (u < 0.35)
    r = np.clip(r, 0, None)
    u, rad, phi, r = u[keep][:n_b], rad[keep][:n_b], phi[keep][:n_b], r[keep][:n_b]
    b_local = np.column_stack([r * np.cos(phi), r * np.sin(phi), u])
    wob_ph = rng.uniform(0, 6.28, (len(u), 3))
    bub_m = looks.bubble_fast("Bubble", fog=FOG, fog_density=DENS * 0.5, body=0.10, rim_strength=1.1)
    bubbles = bl.points_object("Foam", np.zeros_like(b_local), np.zeros(len(u)), mat=bub_m)

    core_m = bl.new_mat("FoamCore")[0]
    nt = core_m.node_tree
    out = nt.nodes["Material Output"]
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.25, **{"Coat Weight": 0.5,
                                                                      "Coat Roughness": 0.05})
    p.inputs["Base Color"].default_value = (0.93, 0.95, 0.98, 1)
    tl = looks.node(nt, "ShaderNodeBsdfTranslucent", Color=(0.95, 0.96, 1.0, 1))
    mx = looks.node(nt, "ShaderNodeMixShader", Fac=0.45)
    looks.link(nt, p.outputs[0], mx.inputs[1])
    looks.link(nt, tl.outputs[0], mx.inputs[2])
    em = looks.node(nt, "ShaderNodeEmission", Color=(0.92, 0.95, 1.0, 1), Strength=0.42)
    a = looks.node(nt, "ShaderNodeAddShader")
    looks.link(nt, mx.outputs[0], a.inputs[0])
    looks.link(nt, em.outputs[0], a.inputs[1])
    looks.link(nt, looks.fog_wrap(nt, a.outputs[0], FOG, density=DENS * 0.6), out.inputs[0])
    nu, nphi = 120, 40
    us = np.concatenate([np.linspace(0.12, 1.0, 40), np.linspace(1.05, L_MAX, nu - 40)])
    ph = np.linspace(0, 2 * np.pi, nphi, endpoint=False)
    core_faces = []
    for i in range(nu - 1):
        for j in range(nphi):
            a0 = i * nphi + j
            b0 = i * nphi + (j + 1) % nphi
            core_faces.append((a0, b0, b0 + nphi, a0 + nphi))
    core = bl.mesh_object("FoamCore", np.zeros((nu * nphi, 3)), core_faces, mat=core_m)

    # --- eritrocitos desplazados por el frente de espuma (simulación precalculada)
    rv, rf = rbc_mesh(R=1.0)
    rbc_obj = bl.mesh_object("RBC", rv * 0.05, rf, mat=looks.rbc(fog=FOG, fog_density=DENS))
    n = 620
    rr = np.sqrt(rng.uniform(0, 1, n)) * 0.9
    ra = rng.uniform(0, 2 * np.pi, n)
    P = np.column_stack([rr * np.cos(ra), rr * np.sin(ra), rng.uniform(-13.5, 2.0, n)])
    dt = 1 / 240
    steps = int(5.4 / dt) + 2
    traj = np.empty((steps, n, 3), np.float32)
    ph_r = rng.uniform(0, 100, (n, 3))
    for i in range(steps):
        t = i * dt
        traj[i] = P
        F = front(t)
        Fd = (front(t + 0.01) - front(t - 0.01)) / 0.02 if t > 0.01 else (front(0.02) - front(0)) / 0.02
        g = growth(t)
        ahead = F - P[:, 2]                               # >0 si el eritrocito está por delante del frente
        push = np.exp(-np.clip(ahead, 0, None) / 1.6)
        vz = Fd * push * (0.35 + 0.65 * g) - 0.05
        rad_now = np.linalg.norm(P[:, :2], axis=1) + 1e-6
        # cerca del frente, ligero desplazamiento radial hacia la pared (rodea el casquete)
        vr = 0.35 * np.exp(-np.clip(ahead, 0, None) / 0.35) * (ahead < 0.6) * g
        v = np.column_stack([P[:, 0] / rad_now * vr, P[:, 1] / rad_now * vr, vz])
        v += 0.05 * np.sin(ph_r + t * np.array([1.1, 1.5, 0.9]))
        P = P + v * dt
        # no penetrar en la espuma: si quedaron detrás del frente, empujarlos delante
        inside = (P[:, 2] > F - 0.05) & (np.linalg.norm(P[:, :2], axis=1) < plug_radius(P[:, 2] - F + 0.0, g) + 0.04)
        P[inside, 2] = F - 0.06
        rn = np.linalg.norm(P[:, :2], axis=1)
        over = rn > 0.92
        P[over, :2] *= (0.92 / rn[over])[:, None]
    track = micro.Track(traj, np.zeros((steps, n), bool), dt)
    p0, r0, _ = track.at(0)
    scale = rng.uniform(0.85, 1.12, n)
    cells = bl.instances_object("Cells", p0, rbc_obj, scale, r0)

    # luces
    cam = bl.camera(sc, lens=20, clip=(0.01, 80), dof=(1.2, 2.0))
    key = bl.point_light(sc, "CamLight", (0, 0, 0), 38, radius=0.35, color=(1.0, 0.92, 0.88))
    bl.point_light(sc, "NeedleLight", (0.5, 0.2, 3.2), 25, radius=0.3, color=(0.9, 0.95, 1.0))
    for i, (zz, a_) in enumerate([(3.5, 0.3), (1.0, 2.2), (-1.5, 4.1), (-4.0, 1.2), (-6.5, 3.4), (-9.0, 5.2)]):
        bl.point_light(sc, f"Out{i}", (2.0 * np.cos(a_), 2.0 * np.sin(a_), zz), 650, radius=0.6,
                       color=(1.0, 0.25, 0.18))
    bl.point_light(sc, "Spec", (0.4, -0.5, 0.0), 0, radius=0.2)

    def update(t):
        F = front(t)
        g = growth(t)
        # cámara: por delante del frente, mirando hacia la espuma que avanza
        d = float(bl.lerp(1.55, 0.45, bl.smoothstep(2.4, 4.9, t)))
        cz = min(F - d, 1.0)
        c_off = bl.lerp(np.array([0.48, -0.40, 0.0]), np.array([0.22, -0.30, 0.0]), bl.smoothstep(0, 3.5, t))
        cam_p = np.array([c_off[0], c_off[1], cz - 0.4 * (1 - g)])
        tgt = np.array([0.0, 0.25 * (1 - g) + 0.05, F + 0.6])
        bl.set_camera(cam, cam_p, tgt, focus=max(np.linalg.norm(tgt - cam_p) * 0.8, 0.3))
        key.location = (cam_p[0] + 0.1, cam_p[1] - 0.05, cam_p[2] + 0.3)
        # espuma: posición en el mundo = frente + coordenada local; visible si ya fue inyectada
        length = max(TIP[2] + 0.15 - F, 0.05)
        scale_r = 0.22 + 0.78 * g
        off_y = 0.62 * (1 - g)
        wob = 0.008 * np.sin(wob_ph + t * np.array([2.1, 2.7, 1.9]))
        pos = np.column_stack([b_local[:, 0] * scale_r, b_local[:, 1] * scale_r + off_y, F + b_local[:, 2]]) + wob
        vis = b_local[:, 2] < length
        rr_ = np.where(vis, rad * (0.55 + 0.45 * g), 0.0)
        pos[~vis] = TIP
        bl.update_points(bubbles, pos, radius=rr_)
        cr = np.maximum(plug_radius(us, g) - 0.2 * g - 0.02, 0.0)
        zz = F + np.minimum(us, length)
        cv = np.column_stack([np.outer(cr, np.cos(ph)).ravel(), (np.outer(cr, np.sin(ph)) + off_y).ravel(),
                              np.repeat(zz, nphi)])
        core.data.vertices.foreach_set("co", cv.astype(np.float32).ravel())
        core.data.update()
        pt, rt, _ = track.at(t)
        bl.update_points(cells, pt, rot=rt)

    return update


def anchors(t):
    F = front(t)
    return {"foam_front": (0.0, -0.55, F + 0.25), "wall": (0.95, 0.0, F + 0.8)}
