"""Plano 5 (39.8–50.3 s): BENEFICIOS, una idea a la vez.
  A) MÍNIMAMENTE INVASIVO: un único punto de punción, diminuto, en la piel.
  B) SIN CIRUGÍA ABIERTA: la piel recupera su aspecto real e íntegro (sin incisiones).
  C) PROCEDIMIENTO AMBULATORIO: media de compresión y huellas de marcha (caminar tras el procedimiento
     es parte habitual de la recuperación; la indicación concreta depende de la valoración médica)."""
import os

import numpy as np

from lib import bl, looks
from lib.anatomy import load_leg_assets
from shots.s4 import orient

RENDER = dict(res=(960, 1707), spp=8, threshold=0.05, bounces=(4, 1, 2, 4, 16), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

SITE = np.array([-0.0397, -0.0634, 0.3000])   # punto de punción sobre la piel (cara medial-posterior de la pantorrilla)


def vertex_normals(v, f):
    n = np.zeros_like(v)
    fn = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]])
    for k in range(3):
        np.add.at(n, f[:, k], fn)
    return n / (np.linalg.norm(n, axis=1, keepdims=True) + 1e-12)


def stocking_material():
    """Tejido de punto de compresión: costillas finas horizontales, brillo suave, aparición de abajo arriba."""
    m, nt, out = bl.new_mat("Stocking")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    sep = looks.node(nt, "ShaderNodeSeparateXYZ")
    looks.link(nt, tc.outputs["Object"], sep.inputs[0])
    knit = looks.math(nt, "POWER", looks.math(nt, "ABSOLUTE", looks.math(nt, "SINE", looks.math(
        nt, "MULTIPLY", sep.outputs["Z"], 1400.0))), 0.6)
    col = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, knit, col.inputs["Factor"])
    col.inputs["A"].default_value = (0.40, 0.33, 0.28, 1)
    col.inputs["B"].default_value = (0.66, 0.56, 0.48, 1)
    welt = looks.node(nt, "ShaderNodeMapRange")
    welt.inputs["From Min"].default_value = 0.405
    welt.inputs["From Max"].default_value = 0.410
    looks.link(nt, sep.outputs["Z"], welt.inputs["Value"])
    col2 = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, welt.outputs["Result"], col2.inputs["Factor"])
    looks.link(nt, col.outputs["Result"], col2.inputs["A"])
    col2.inputs["B"].default_value = (0.32, 0.27, 0.24, 1)
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.6, **{"Sheen Weight": 0.8, "Sheen Roughness": 0.35})
    p.inputs["Sheen Tint"].default_value = (1.0, 0.95, 0.9, 1)
    looks.link(nt, col2.outputs["Result"], p.inputs["Base Color"])
    bump = looks.node(nt, "ShaderNodeBump", Strength=0.25, Distance=0.0004)
    looks.link(nt, knit, bump.inputs["Height"])
    looks.link(nt, bump.outputs[0], p.inputs["Normal"])
    wz = bl.value_node(nt, "wipe_z", -0.1)
    mask = looks.node(nt, "ShaderNodeMapRange")
    mask.interpolation_type = "SMOOTHSTEP"
    looks.link(nt, sep.outputs["Z"], mask.inputs["Value"])
    looks.link(nt, looks.math(nt, "SUBTRACT", wz.outputs[0], 0.01), mask.inputs["From Min"])
    looks.link(nt, looks.math(nt, "ADD", wz.outputs[0], 0.01), mask.inputs["From Max"])
    tr = looks.node(nt, "ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    looks.link(nt, mask.outputs["Result"], mx.inputs[0])
    looks.link(nt, p.outputs[0], mx.inputs[1])
    looks.link(nt, tr.outputs[0], mx.inputs[2])
    # borde luminoso que sube con la media
    band = looks.node(nt, "ShaderNodeMapRange")
    band.interpolation_type = "SMOOTHSTEP"
    band.inputs["From Min"].default_value = 0.0
    band.inputs["From Max"].default_value = 0.006
    band.inputs["To Min"].default_value = 1.0
    band.inputs["To Max"].default_value = 0.0
    looks.link(nt, looks.math(nt, "ABSOLUTE", looks.math(nt, "SUBTRACT", sep.outputs["Z"], wz.outputs[0])), band.inputs["Value"])
    em = looks.node(nt, "ShaderNodeEmission", Color=(0.3, 0.75, 1.0, 1))
    looks.link(nt, looks.math(nt, "MULTIPLY", band.outputs["Result"], 6.0), em.inputs["Strength"])
    a = looks.node(nt, "ShaderNodeAddShader")
    looks.link(nt, mx.outputs[0], a.inputs[0])
    looks.link(nt, em.outputs[0], a.inputs[1])
    looks.link(nt, a.outputs[0], out.inputs[0])
    return m


def footprint(cx, cy, ang, right=True, s=1.0):
    """Huella estilizada: antepié + talón + dedos (mallas planas)."""
    parts = [((0.0, 0.045), (0.034, 0.055)), ((0.0, -0.060), (0.026, 0.032))]
    toes = [(-0.020, 0.112, 0.011), (-0.004, 0.118, 0.008), (0.010, 0.115, 0.007), (0.022, 0.108, 0.0065),
            (0.031, 0.097, 0.006)]
    V, F = [], []
    sgn = 1 if right else -1
    ca, sa = np.cos(ang), np.sin(ang)

    def add_ellipse(c, r, n=28):
        base = len(V)
        V.append((c[0], c[1]))
        for k in range(n):
            a = 2 * np.pi * k / n
            V.append((c[0] + r[0] * np.cos(a), c[1] + r[1] * np.sin(a)))
        for k in range(n):
            F.append((base, base + 1 + k, base + 1 + (k + 1) % n))

    for c, r in parts:
        add_ellipse((sgn * c[0], c[1]), r)
    for x, y, r in toes:
        add_ellipse((sgn * x, y), (r, r * 1.2), 14)
    V = np.array(V) * s
    W = np.column_stack([cx + V[:, 0] * ca - V[:, 1] * sa, cy + V[:, 0] * sa + V[:, 1] * ca, np.full(len(V), 0.0012)])
    return W, F


def build(sc, ctx):
    import bpy
    A = load_leg_assets(os.path.join(ctx["assets"], "leg.npz"))
    bl.world(sc, top=(0.010, 0.030, 0.070), bottom=(0.0, 0.003, 0.010))
    root = bpy.data.objects.new("LegRoot", None)
    bl.link(root)
    skin = looks.skin_reveal("Skin5")
    bl.set_value(skin, "xray", 1.0)
    bl.set_value(skin, "scan_z", -0.2)
    objs = [bl.mesh_object("Skin", A["skin_v"], A["skin_f"], mat=skin)]
    muscle = looks.xray_layer("Muscle5", rim=(0.85, 0.20, 0.16), strength=0.22, power=2.6,
                              fill=(0.25, 0.03, 0.03), fill_strength=0.006)
    bone = looks.xray_layer("Bone5", rim=(0.70, 0.80, 1.0), strength=0.22, power=2.2, fill=(0.4, 0.45, 0.55),
                            fill_strength=0.006)
    objs.append(bl.mesh_object("Muscle", A["muscle_v"], A["muscle_f"], mat=muscle))
    objs.append(bl.mesh_object("Bone", A["bone_v"], A["bone_f"], mat=bone))
    kw = dict(flow=True, flow_color=(1.0, 0.10, 0.07), flow_density=8.0)
    vm = {"superficial": looks.vein("VSup5", base=(0.02, 0.05, 0.30), glow=(0.06, 0.25, 1.0), glow_strength=0.75,
                                    flow_speed=0.13, **kw),
          "deep": looks.vein("VDeep5", base=(0.02, 0.05, 0.32), glow=(0.05, 0.20, 0.95), glow_strength=0.6,
                             flow_speed=0.16, **kw),
          "perforator": looks.vein("VPerf5", base=(0.03, 0.10, 0.35), glow=(0.10, 0.45, 1.0), glow_strength=0.6,
                                   flow_speed=0.05, **kw),
          "reticular": looks.vein("VRet5", base=(0.12, 0.03, 0.26), glow=(0.40, 0.12, 0.95), glow_strength=0.55),
          "varicose": looks.vein("VCord5", base=(0.55, 0.50, 0.52), glow=(0.35, 0.33, 0.36), glow_strength=0.5)}
    bl.set_value(vm["varicose"], "dim", 1.0)
    bl.set_value(vm["varicose"], "vis", 0.3)
    for k, d in A["veins"].items():
        pts, rad = orient(d["pts"], d["radius"], d["kind"])
        if d["kind"] == "varicose":
            rad = rad * 0.36
        objs.append(bl.tube_mesh(f"V_{k}", pts, rad, n_ring=12, mat=vm[d["kind"]], u_mode="length"))

    # media de compresión (desde el pie hasta debajo de la rodilla)
    v, f = A["skin_v"], A["skin_f"]
    n = vertex_normals(v, f)
    sv = v + n * 0.0014
    keep = (v[f][:, :, 2].max(axis=1) < 0.41)
    stock = bl.mesh_object("Stocking", sv, f[keep], mat=stocking_material())
    objs.append(stock)
    st_m = stock.data.materials[0]

    # punto de punción con anillo de pulso
    dot = bl.points_object("Site", SITE[None], np.array([0.0022]), mat=bl.emission_mat("SiteDot", (0.6, 0.9, 1.0), 25))
    ring_m = bl.emission_mat("Ring", (0.3, 0.8, 1.0), 6)
    ang = np.linspace(0, 2 * np.pi, 64, endpoint=False)
    nrm = np.array([-0.62, -0.78, 0.0])
    nrm /= np.linalg.norm(nrm)
    t1 = np.cross(nrm, [0, 0, 1.0])
    t1 /= np.linalg.norm(t1)
    t2 = np.cross(nrm, t1)
    ring_pts = SITE + np.outer(np.cos(ang), t1) + np.outer(np.sin(ang), t2)
    ring = bl.tube_mesh("Ring", np.vstack([ring_pts, ring_pts[:1]]), np.full(65, 0.05), n_ring=6, mat=ring_m)
    ring.scale = (0.0, 0.0, 0.0)
    objs += [dot, ring]
    for o in objs:
        o.parent = root

    # suelo oscuro brillante con desvanecimiento radial + huellas de marcha
    m, nt, out = bl.new_mat("Floor")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    grad = looks.node(nt, "ShaderNodeTexGradient", _gradient_type="SPHERICAL")
    mp = looks.node(nt, "ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (0.9, 0.9, 0.9)
    looks.link(nt, tc.outputs["Object"], mp.inputs["Vector"])
    looks.link(nt, mp.outputs[0], grad.inputs["Vector"])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.28, **{"Specular IOR Level": 0.6})
    p.inputs["Base Color"].default_value = (0.004, 0.010, 0.022, 1)
    tr = looks.node(nt, "ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    looks.link(nt, grad.outputs["Fac"], mx.inputs[0])
    looks.link(nt, tr.outputs[0], mx.inputs[1])
    looks.link(nt, p.outputs[0], mx.inputs[2])
    looks.link(nt, mx.outputs[0], out.inputs[0])
    fv = np.array([[-1.2, -1.2, 0], [1.2, -1.2, 0], [1.2, 1.2, 0], [-1.2, 1.2, 0]], float)
    bl.mesh_object("Floor", fv, [(0, 1, 2, 3)], mat=m)
    steps = [(-0.17, 0.30, False), (-0.06, 0.52, True), (-0.20, 0.74, False), (-0.09, 0.96, True),
             (-0.23, 1.18, False)]
    fp_mats, fps = [], []
    for i, (x, y, right) in enumerate(steps):
        W, F = footprint(x, y, np.radians(8), right=right, s=0.95)
        fm, fnt, fout = bl.new_mat(f"Foot{i}")
        fe = looks.node(fnt, "ShaderNodeEmission", Color=(0.30, 0.78, 1.0, 1), Strength=2.2)
        ftr = looks.node(fnt, "ShaderNodeBsdfTransparent")
        fk = bl.value_node(fnt, "k", 0.0)
        fmx = fnt.nodes.new("ShaderNodeMixShader")
        looks.link(fnt, fk.outputs[0], fmx.inputs[0])
        looks.link(fnt, ftr.outputs[0], fmx.inputs[1])
        looks.link(fnt, fe.outputs[0], fmx.inputs[2])
        looks.link(fnt, fmx.outputs[0], fout.inputs[0])
        fp_mats.append(fm)
        fps.append(bl.mesh_object(f"Foot{i}", W, F, mat=fm, smooth=False))

    bl.area_light(sc, "Key", (-1.4, 0.6, 1.4), (0, 0, 0.40), 55, size=0.9, color=(1.0, 0.90, 0.80))
    bl.area_light(sc, "RimL", (0.9, 1.4, 1.0), (0, 0, 0.4), 150, size=0.6, color=(0.45, 0.68, 1.0))
    bl.area_light(sc, "RimR", (1.2, -1.2, 0.8), (0, 0, 0.4), 140, size=0.6, color=(0.60, 0.80, 1.0))
    bl.area_light(sc, "Top", (0.0, 0.0, 2.2), (0, 0, 0.4), 25, size=1.5, color=(0.85, 0.9, 1.0))

    cam = bl.camera(sc, lens=60, clip=(0.01, 30), dof=(2.4, 9.0))
    cam_keys = [(0.0, (-1.95, -0.85, 0.62)), (5.0, (-2.05, -0.55, 0.58)), (10.5, (-2.30, -0.20, 0.64))]
    tgt_keys = [(0.0, (0.0, 0.02, 0.44)), (5.0, (0.0, 0.05, 0.42)), (10.5, (0.0, 0.16, 0.40))]

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        bl.set_camera(cam, p, g, focus=np.linalg.norm(p - g))
        root.rotation_euler = (0, 0, np.radians(-18 + 52 * bl.ease_in_out(t / 10.5)))
        for key in ("superficial", "deep", "perforator"):
            bl.set_value(vm[key], "flow_t", float(t))
            bl.set_value(vm[key], "flow_k", 0.95)
        # A) punción mínima: punto + anillo que se expande y se desvanece
        a = bl.smoothstep(0.4, 0.8, t) * (1 - bl.smoothstep(3.3, 3.8, t))
        bl.update_points(dot, SITE[None], radius=np.array([0.0022 * a + 1e-6]))
        ph = ((t - 0.6) % 1.2) / 1.2
        rs = 0.004 + 0.022 * ph
        ring.scale = (rs * a, rs * a, rs * a)
        ring.location = tuple(SITE * (1 - rs * a))
        ring_m.node_tree.nodes["Emission"].inputs[1].default_value = float(6.0 * (1 - ph) * a)
        # B) la piel vuelve a ser opaca y realista de abajo arriba (piel íntegra)
        u = bl.ease_in_out((t - 3.6) / 1.8)
        bl.set_value(skin, "scan_z", float(bl.lerp(-0.2, 1.02, u)))
        bl.set_value(skin, "scan_glow", float(7.0 * np.sin(np.pi * np.clip(u, 0, 1)) ** 0.5))
        # C) media de compresión y huellas de marcha
        w = bl.ease_in_out((t - 6.9) / 1.5)
        bl.set_value(st_m, "wipe_z", float(bl.lerp(-0.02, 0.42, w)))
        for i, fm in enumerate(fp_mats):
            k = bl.smoothstep(7.6 + 0.42 * i, 8.0 + 0.42 * i, t)
            bl.set_value(fm, "k", float(k * (1 - 0.35 * bl.smoothstep(9.6, 10.4, t))))

    return update


def anchors(t):
    a = np.radians(-18 + 52 * bl.ease_in_out(t / 10.5))
    c, s_ = np.cos(a), np.sin(a)
    x, y, z = SITE
    return {"site": (x * c - y * s_, x * s_ + y * c, z)}
