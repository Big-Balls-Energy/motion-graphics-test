"""Plano 2 (7.8–16.3 s): corte anatómico de piel y tejido subcutáneo con la vena varicosa expuesta.
Un transductor lineal se apoya sobre la piel; su plano de exploración (haz ecográfico) coincide con el
plano de corte, en el eje longitudinal de la vena. Una microaguja entra "en plano" (visible en todo su
trayecto, técnica habitual en escleroterapia ecoguiada), atraviesa la piel y la grasa y alcanza la luz
venosa; el reflujo de sangre en el cono (flashback) confirma la posición intravascular.
Unidades: 1 = 1 cm."""
import math

import numpy as np

from lib import bl, looks

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(4, 1, 2, 4, 8), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

VEIN_Z = -0.85
VEIN_R = 0.33
SKIN = 0.24
FAT_BOTTOM = -1.70
BOTTOM = -4.8
X0, X1 = -4.8, 4.8
ENTRY = np.array([-1.75, 0.0, 0.0])
ANG = math.radians(34)
DIR = np.array([math.cos(ANG), 0.0, -math.sin(ANG)])
from lib.s2_timing import S_FINAL, beam_on, flashback, foam_out, needle_s, probe_drop  # noqa: E402,F401


def box(x0, x1, y0, y1, z0, z1):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0],
                  [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], float)
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return v, f


def grooved_fat(x0=X0, x1=X1, y1=1.6, z0=FAT_BOTTOM, z1=-SKIN, zc=VEIN_Z, rg=0.38, n=24):
    """Bloque de grasa (y >= 0) con un surco semicilíndrico donde se aloja la vena."""
    prof = [(0.0, z1)]
    for k in range(n + 1):
        a = math.pi / 2 - math.pi * k / n          # de arriba (90°) a abajo (-90°) por detrás (y>0)
        prof.append((rg * math.cos(a), zc + rg * math.sin(a)))
    prof += [(0.0, z0), (y1, z0), (y1, z1)]
    # el contorno debe ir sin cruzarse: (0,z1) -> surco -> (0,z0) -> (y1,z0) -> (y1,z1)
    prof = [prof[0]] + [(y, z) for y, z in prof[1:n + 2]] + prof[n + 2:]
    m = len(prof)
    verts = [(x0, y, z) for y, z in prof] + [(x1, y, z) for y, z in prof]
    faces = []
    for i in range(m):
        j = (i + 1) % m
        faces.append((i, j, m + j, m + i))
    faces.append(tuple(range(m))[::-1])
    faces.append(tuple(range(m, 2 * m)))
    return np.array(verts, float), faces


def build(sc, ctx):
    bl.world(sc, top=(0.012, 0.035, 0.075), bottom=(0.0, 0.004, 0.012))
    rng = np.random.default_rng(5)
    mats = make_materials()

    # capas de tejido (bloque sólido detrás del plano de corte y = 0)
    v, f = box(X0, X1, 0.0, 1.6, -SKIN, 0.0)
    skin = bl.mesh_object("Skin", v, f, smooth=False, mat=mats["skin_cut"])
    skin.data.materials.append(mats["skin_top"])
    for poly in skin.data.polygons:
        if poly.normal.z > 0.9:
            poly.material_index = 1
    v, f = grooved_fat()
    bl.mesh_object("Fat", v, f, smooth=False, mat=mats["fat"])
    v, f = box(X0, X1, 0.0, 1.6, FAT_BOTTOM - 0.08, FAT_BOTTOM)
    bl.mesh_object("Fascia", v, f, smooth=False, mat=mats["fascia"])
    v, f = box(X0, X1, 0.0, 1.6, BOTTOM, FAT_BOTTOM - 0.08)
    bl.mesh_object("Muscle", v, f, smooth=False, mat=mats["muscle"])
    # tejido retirado (delante del corte) como volumen fantasma
    v, f = box(X0, X1, -1.6, 0.0, BOTTOM, 0.0)
    bl.mesh_object("Ghost", v, f, smooth=False, mat=mats["ghost"])
    # paquete vascular profundo en el músculo: arteria y dos venas acompañantes (funcionales)
    xd = np.linspace(X0 - 0.1, X1 + 0.1, 60)
    for nm, dy, dz, r, key in [("DeepVein1", 0.0, -3.30, 0.21, "deep_vein"), ("DeepVein2", 0.0, -3.92, 0.19, "deep_vein"),
                               ("DeepArtery", 0.0, -3.60, 0.13, "artery")]:
        pts_d = np.column_stack([xd, dy + 0.0 * xd, dz + 0.04 * np.sin(xd * 0.8 + dz)])
        bl.tube_mesh(nm, pts_d, np.full(len(xd), r), n_ring=28, mat=mats[key], cap=True)

    # vena varicosa: pared translúcida + sangre (absorción volumétrica) + eritrocitos
    xs = np.linspace(X0 - 0.1, X1 + 0.1, 160)
    pts = np.column_stack([xs, 0.015 * np.sin(xs * 1.3), VEIN_Z + 0.03 * np.sin(xs * 0.9 + 0.4)])
    rad = VEIN_R * (1 + 0.05 * np.sin(xs * 2.1 + 1.0))
    bl.tube_mesh("VeinWall", pts, rad, n_ring=40, mat=mats["vein_wall"], cap=False)
    bl.tube_mesh("Blood", pts, rad * 0.86, n_ring=32, mat=mats["blood"], cap=True)
    from lib.anatomy import rbc_mesh
    rv, rf = rbc_mesh(R=1.0)
    rbc_obj = bl.mesh_object("RBC", rv * 0.028, rf, mat=mats["rbc"])
    n = 380
    rx = rng.uniform(X0, X1, n)
    rr = np.sqrt(rng.uniform(0, 1, n)) * VEIN_R * 0.72
    ra = rng.uniform(0, 2 * np.pi, n)
    rbc0 = np.column_stack([rx, rr * np.cos(ra), VEIN_Z + rr * np.sin(ra)])
    rbc_rot0 = rng.uniform(0, 6.3, (n, 3))
    rbc_w = rng.normal(0, 0.5, (n, 3))
    cells = bl.instances_object("Cells", rbc0, rbc_obj, rng.uniform(0.85, 1.15, n), rbc_rot0)

    # transductor lineal + gel
    probe = make_probe(mats)
    # plano del haz (coincide con el corte, ligeramente por delante para no solaparse)
    bv = np.array([[-1.0, -0.015, -4.2], [2.8, -0.015, -4.2], [2.8, -0.015, -0.005], [-1.0, -0.015, -0.005]])
    beam = bl.mesh_object("Beam", bv, [(0, 1, 2, 3)], smooth=False, mat=mats["beam"])
    uv = beam.data.uv_layers.new(name="UVMap")
    for li, (u_, v_) in enumerate([(0, 0), (1, 0), (1, 1), (0, 1)]):
        uv.data[li].uv = (u_, v_)

    # aguja (bisel en la punta), cono translúcido y sangre del flashback
    needle_len = 3.6
    nv, nf = needle_mesh(needle_len, 0.032)
    needle = bl.mesh_object("Needle", nv, nf, mat=mats["steel"])
    hv, hf = cyl_mesh(0.10, 0.20, 1.0, 32)
    hub = bl.mesh_object("Hub", hv, hf, mat=mats["hub"])
    fv, ff = cyl_mesh(0.06, 0.14, 0.9, 24)
    flash = bl.mesh_object("Flash", fv, ff, mat=mats["flash"])
    sv, sf_ = cyl_mesh(0.62, 0.62, 5.5, 48)
    syringe = bl.mesh_object("Syringe", sv, sf_, mat=mats["hub"])
    plv, plf = cyl_mesh(0.57, 0.57, 3.2, 40)
    foam_col = bl.mesh_object("SyrFoam", plv, plf, mat=mats["foam_syringe"])
    # microespuma que empieza a salir por la punta al final del plano
    nb = 160
    b_off = rng.normal(0, 1, (nb, 3))
    b_off /= np.linalg.norm(b_off, axis=1, keepdims=True)
    b_rad = rng.uniform(0.012, 0.035, nb)
    b_dist = rng.uniform(0.0, 1.0, nb) ** 0.7
    bubbles = bl.points_object("TipFoam", np.zeros((nb, 3)), np.zeros(nb), mat=mats["bubble"])

    # luces de estudio
    bl.area_light(sc, "Key", (-7, -10, 7), (0, 0, -1.5), 1500, size=7, color=(1.0, 0.94, 0.88))
    bl.area_light(sc, "Fill", (9, -8, 0), (0, 0, -1.5), 380, size=7, color=(0.62, 0.78, 1.0))
    bl.area_light(sc, "Rim", (2, 10, 6), (0, 0, -1.0), 1500, size=6, color=(0.6, 0.78, 1.0))
    bl.area_light(sc, "Top", (0, -2, 12), (0, 0, 0), 260, size=8)

    cam = bl.camera(sc, lens=45, clip=(0.05, 200), dof=(11, 3.5))
    cam_keys = [(0.0, (-8.4, -8.6, 2.0)), (3.6, (-7.4, -8.0, 1.5)), (6.4, (-5.2, -6.2, 0.8)),
                (8.5, (-3.4, -4.4, 0.25))]
    tgt_keys = [(0.0, (-0.2, 0.0, -1.55)), (3.6, (-0.5, 0.0, -1.3)), (6.4, (-0.7, 0.0, -0.95)),
                (8.5, (-0.78, 0.0, -0.80))]

    def place_needle(s):
        tip = ENTRY + DIR * s
        base = tip - DIR * needle_len
        rot = (0.0, ANG - math.pi / 2, 0.0)       # eje local +z alineado con -DIR (de la punta hacia el cono)
        needle.location = tuple(tip)
        needle.rotation_euler = rot
        hub_pos = base - DIR * 0.45
        hub.location = tuple(base)
        hub.rotation_euler = rot
        flash.location = tuple(base + (-DIR) * 0.05)
        flash.rotation_euler = rot
        syringe.location = tuple(base - DIR * 1.0)
        syringe.rotation_euler = rot
        foam_col.location = tuple(base - DIR * 1.15)
        foam_col.rotation_euler = rot
        return tip, hub_pos

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        bl.set_camera(cam, p, g, focus=np.linalg.norm(np.array(g) - p))
        cam.data.dof.aperture_fstop = float(bl.lerp(3.5, 1.8, bl.smoothstep(4.0, 8.0, t)))
        drop = probe_drop(t)
        probe.location = (0.9, 0.0, 0.07 + 3.2 * drop)
        bl.set_value(mats["beam"], "on", beam_on(t) * (1 - drop))
        bl.set_value(mats["beam"], "phase", t)
        s = needle_s(t)
        tip, _ = place_needle(s)
        fb = flashback(t)
        flash.scale = (1, 1, max(fb, 0.001))
        flash.hide_render = fb < 0.01
        # eritrocitos: deriva lenta en la luz venosa
        pos = rbc0 + np.column_stack([0.06 * t * np.ones(n), np.zeros(n), np.zeros(n)])
        pos[:, 0] = (pos[:, 0] - X0) % (X1 - X0) + X0
        bl.update_points(cells, pos, rot=rbc_rot0 + rbc_w * t)
        fo = foam_out(t)
        bp = tip + DIR * 0.03 + b_off * (0.04 + 0.22 * fo * b_dist[:, None])
        bp[:, 2] = np.clip(bp[:, 2], VEIN_Z - VEIN_R * 0.7, VEIN_Z + VEIN_R * 0.7)
        bl.update_points(bubbles, bp, radius=b_rad * fo)
        bl.set_value(mats["foam_syringe"], "vis", 1.0)

    return update


def anchors(t):
    s = needle_s(t)
    tip = ENTRY + DIR * s
    return {"probe": (0.9, 0.0, 1.2), "needle": tuple(ENTRY - DIR * 0.9), "tip": tuple(tip),
            "vein": (1.6, 0.0, VEIN_Z)}


# ----------------------------------------------------------------------------- geometry helpers


def ellipsoid(c, r, nu=32, nv=16):
    us = np.linspace(0, 2 * np.pi, nu, endpoint=False)
    vs = np.linspace(0.02, np.pi / 2, nv)   # media elipsoide (cara inferior plana sobre la piel)
    verts = [(c[0] + r[0] * np.cos(u) * np.sin(v), c[1] + r[1] * np.sin(u) * np.sin(v), c[2] + r[2] * np.cos(v) - r[2] * 0.0)
             for v in vs for u in us]
    faces = []
    for i in range(nv - 1):
        for j in range(nu):
            a = i * nu + j
            b = i * nu + (j + 1) % nu
            faces.append((a, b, b + nu, a + nu))
    verts.append((c[0], c[1], c[2] + r[2]))
    top = len(verts) - 1
    for j in range(nu):
        faces.append((top, (j + 1) % nu, j))
    return np.array(verts), faces


def cyl_mesh(r0, r1, length, n=24):
    """Cilindro/cono a lo largo de +z local desde z=0 hasta z=length (r0 en z=0)."""
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    v = [(r0 * np.cos(x), r0 * np.sin(x), 0.0) for x in a] + [(r1 * np.cos(x), r1 * np.sin(x), length) for x in a]
    f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    f.append(tuple(range(n))[::-1])
    f.append(tuple(range(n, 2 * n)))
    return np.array(v), f


def needle_mesh(length, r, n=20):
    """Aguja hueca simplificada: cilindro con bisel en z=0 (punta) y extremo en z=length."""
    a = np.linspace(0, 2 * np.pi, n, endpoint=False)
    bevel = 0.16
    v = []
    for x in a:
        zb = bevel * (0.5 + 0.5 * np.cos(x))   # plano oblicuo: punta en x=pi
        v.append((r * np.cos(x), r * np.sin(x), zb))
    for x in a:
        v.append((r * np.cos(x), r * np.sin(x), length))
    f = [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    f.append(tuple(range(n))[::-1])
    f.append(tuple(range(n, 2 * n)))
    return np.array(v), f


def make_probe(mats):
    """Transductor lineal: cabezal redondeado, lente acústica oscura y mango."""
    import bpy
    from mathutils import Matrix
    parts = []
    hv, hf = rounded_box((3.9, 0.95, 0.85), 0.22)
    head = bl.mesh_object("ProbeHead", hv + np.array([0, 0, 0.50]), hf, mat=mats["plastic"])
    lv, lf = rounded_box((3.7, 0.78, 0.14), 0.05)
    lens = bl.mesh_object("ProbeLens", lv + np.array([0, 0, 0.07]), lf, mat=mats["rubber"])
    nv_, nf_ = rounded_box((2.6, 0.78, 0.9), 0.3)
    neck = bl.mesh_object("ProbeNeck", nv_ + np.array([0, 0, 1.15]), nf_, mat=mats["plastic"])
    gv, gf = rounded_box((1.7, 0.72, 3.4), 0.35)
    grip = bl.mesh_object("ProbeGrip", gv + np.array([0, 0, 2.75]), gf, mat=mats["plastic_dark"])
    cv, cf = cyl_mesh(0.18, 0.13, 3.0, 24)
    cable = bl.mesh_object("ProbeCable", cv + np.array([0, 0, 4.3]), cf, mat=mats["rubber"])
    root = bpy.data.objects.new("Probe", None)
    bl.link(root)
    for o in (head, lens, neck, grip, cable):
        o.parent = root
    return root


def rounded_box(size, rad, n=6):
    """Caja con aristas redondeadas (superelipsoide)."""
    sx, sy, sz = np.array(size) / 2
    us = np.linspace(-np.pi, np.pi, 48, endpoint=False)
    vs = np.linspace(-np.pi / 2, np.pi / 2, 24)
    e = 0.18 + 0.4 * rad / max(min(sx, sy, sz), 1e-3) * 0.3

    def sp(x, p):
        return np.sign(x) * np.abs(x) ** p

    verts = []
    for v in vs:
        for u in us:
            verts.append((sx * sp(np.cos(v), e) * sp(np.cos(u), e), sy * sp(np.cos(v), e) * sp(np.sin(u), e),
                          sz * sp(np.sin(v), e)))
    faces = []
    nu = len(us)
    for i in range(len(vs) - 1):
        for j in range(nu):
            a = i * nu + j
            b = i * nu + (j + 1) % nu
            faces.append((a, b, b + nu, a + nu))
    return np.array(verts), faces


def make_materials():
    M = {}
    M["skin_top"] = bl.principled("SkinTop", base=(0.62, 0.42, 0.33), rough=0.5, coat=0.15, coat_rough=0.3,
                                  sheen=0.2)
    m, nt, out = bl.new_mat("SkinCut")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    sep = looks.node(nt, "ShaderNodeSeparateXYZ")
    looks.link(nt, tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.inputs["From Min"].default_value = -0.05
    mr.inputs["From Max"].default_value = -0.02
    looks.link(nt, sep.outputs["Z"], mr.inputs["Value"])
    mix = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    mix.inputs["A"].default_value = (0.78, 0.36, 0.36, 1)   # dermis
    mix.inputs["B"].default_value = (0.55, 0.36, 0.28, 1)   # epidermis
    looks.link(nt, mr.outputs["Result"], mix.inputs["Factor"])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.45, **{"Coat Weight": 0.3})
    looks.link(nt, mix.outputs["Result"], p.inputs["Base Color"])
    looks.link(nt, p.outputs[0], out.inputs[0])
    M["skin_cut"] = m
    # grasa lobulillar (voronoi): lóbulos amarillos con tabiques rosados
    m, nt, out = bl.new_mat("Fat")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    vo = looks.node(nt, "ShaderNodeTexVoronoi", Scale=5.0, _feature="DISTANCE_TO_EDGE")
    looks.link(nt, tc.outputs["Object"], vo.inputs["Vector"])
    ramp = looks.node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.0
    ramp.color_ramp.elements[0].color = (0.75, 0.38, 0.30, 1)
    ramp.color_ramp.elements[1].position = 0.08
    ramp.color_ramp.elements[1].color = (0.95, 0.74, 0.36, 1)
    looks.link(nt, vo.outputs["Distance"], ramp.inputs[0])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.35, **{"Coat Weight": 0.4, "Coat Roughness": 0.15})
    looks.link(nt, ramp.outputs[0], p.inputs["Base Color"])
    bump = looks.node(nt, "ShaderNodeBump", Strength=0.35, Distance=0.05)
    looks.link(nt, vo.outputs["Distance"], bump.inputs["Height"])
    looks.link(nt, bump.outputs[0], p.inputs["Normal"])
    looks.link(nt, p.outputs[0], out.inputs[0])
    M["fat"] = m
    M["fascia"] = bl.principled("Fascia", base=(0.92, 0.88, 0.84), rough=0.25, coat=0.5)
    m, nt, out = bl.new_mat("Muscle")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    wv = looks.node(nt, "ShaderNodeTexWave", Scale=9.0, Distortion=2.5, **{"Detail": 2.0})
    wv.bands_direction = "Z"
    looks.link(nt, tc.outputs["Object"], wv.inputs["Vector"])
    ramp = looks.node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.30, 0.03, 0.035, 1)
    ramp.color_ramp.elements[1].color = (0.62, 0.10, 0.10, 1)
    looks.link(nt, wv.outputs["Fac"], ramp.inputs[0])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.38, **{"Coat Weight": 0.4})
    looks.link(nt, ramp.outputs[0], p.inputs["Base Color"])
    looks.link(nt, p.outputs[0], out.inputs[0])
    M["muscle"] = m
    M["ghost"] = looks.xray_layer("Ghost", rim=(0.45, 0.7, 1.0), strength=0.25, power=3.0,
                                  fill=(0.3, 0.5, 0.8), fill_strength=0.004)
    # pared venosa translúcida (violácea) y sangre por absorción volumétrica
    m, nt, out = bl.new_mat("VeinWall")
    lw = looks.node(nt, "ShaderNodeLayerWeight", Blend=0.35)
    gl = looks.node(nt, "ShaderNodeBsdfGlossy", Roughness=0.18)
    tr = looks.node(nt, "ShaderNodeBsdfTransparent", Color=(0.62, 0.45, 0.85, 1))
    mx = nt.nodes.new("ShaderNodeMixShader")
    looks.link(nt, looks.math(nt, "ADD", 0.18, looks.math(nt, "MULTIPLY", lw.outputs["Facing"], 0.55)), mx.inputs[0])
    looks.link(nt, tr.outputs[0], mx.inputs[1])
    pr = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.3, **{"Coat Weight": 0.6})
    pr.inputs["Base Color"].default_value = (0.20, 0.06, 0.34, 1)
    looks.link(nt, pr.outputs[0], mx.inputs[2])
    em = looks.node(nt, "ShaderNodeEmission", Color=(0.45, 0.25, 0.9, 1))
    looks.link(nt, looks.math(nt, "MULTIPLY", lw.outputs["Facing"], 0.35), em.inputs["Strength"])
    a = looks.node(nt, "ShaderNodeAddShader")
    looks.link(nt, mx.outputs[0], a.inputs[0])
    looks.link(nt, em.outputs[0], a.inputs[1])
    looks.link(nt, a.outputs[0], out.inputs[0])
    M["vein_wall"] = m
    m, nt, out = bl.new_mat("Blood")
    tr = looks.node(nt, "ShaderNodeBsdfTransparent")
    gl = looks.node(nt, "ShaderNodeBsdfGlossy", Roughness=0.1)
    mx = looks.node(nt, "ShaderNodeMixShader", Fac=0.06)
    looks.link(nt, tr.outputs[0], mx.inputs[1])
    looks.link(nt, gl.outputs[0], mx.inputs[2])
    looks.link(nt, mx.outputs[0], out.inputs["Surface"])
    va = looks.node(nt, "ShaderNodeVolumeAbsorption", Color=(0.75, 0.05, 0.06, 1), Density=2.2)
    looks.link(nt, va.outputs[0], out.inputs["Volume"])
    M["blood"] = m
    M["rbc"] = looks.rbc("RBC2")
    M["plastic"] = bl.principled("Plastic", base=(0.80, 0.82, 0.85), rough=0.35, coat=0.25, coat_rough=0.2)
    M["plastic_dark"] = bl.principled("PlasticDark", base=(0.22, 0.25, 0.30), rough=0.4, coat=0.2)
    M["deep_vein"] = looks.vein("DeepVeinM", base=(0.05, 0.10, 0.42), glow=(0.1, 0.3, 1.0), glow_strength=0.25,
                                fade_top=False)
    M["artery"] = bl.principled("Artery", base=(0.55, 0.04, 0.05), rough=0.3, coat=0.6)
    M["rubber"] = bl.principled("Rubber", base=(0.06, 0.065, 0.075), rough=0.6)
    M["gel"] = bl.principled("Gel", base=(0.9, 0.95, 1.0), rough=0.05, transmission=1.0, ior=1.34)
    M["steel"] = bl.principled("Steel", base=(0.85, 0.87, 0.9), rough=0.16, metallic=1.0)
    M["hub"] = bl.principled("Hub", base=(0.92, 0.95, 1.0), rough=0.12, transmission=0.92, ior=1.45, coat=0.4)
    M["flash"] = bl.principled("Flash", base=(0.32, 0.01, 0.02), rough=0.2, coat=0.6)
    M["foam_syringe"] = looks.xray_layer("SyrFoam", rim=(0.95, 0.97, 1.0), strength=0.6, power=1.2,
                                         fill=(0.92, 0.95, 1.0), fill_strength=0.55)
    M["bubble"] = looks.bubble("TipBubble", body=0.35, rim_strength=1.2)
    # haz ecográfico: plano emisivo con barrido de líneas y pulsos que descienden
    m, nt, out = bl.new_mat("Beam")
    on = bl.value_node(nt, "on", 0.0)
    ph = bl.value_node(nt, "phase", 0.0)
    tc = looks.node(nt, "ShaderNodeTexCoord")
    sep = looks.node(nt, "ShaderNodeSeparateXYZ")
    looks.link(nt, tc.outputs["UV"], sep.inputs[0])
    # pulsos (frentes de onda) que bajan: frac(v*6 + phase*2)
    wave = looks.math(nt, "FRACT", looks.math(nt, "ADD", looks.math(nt, "MULTIPLY", sep.outputs["Y"], 7.0),
                                                looks.math(nt, "MULTIPLY", ph.outputs[0], 2.2)))
    pulse = looks.math(nt, "POWER", wave, 5.0)
    lines = looks.math(nt, "POWER", looks.math(nt, "ABSOLUTE", looks.math(nt, "SINE", looks.math(
        nt, "MULTIPLY", sep.outputs["X"], 220.0))), 18.0)
    depth = looks.math(nt, "POWER", sep.outputs["Y"], 1.6)
    edge = looks.math(nt, "MINIMUM", looks.math(nt, "MULTIPLY", sep.outputs["X"], 5.0),
                      looks.math(nt, "MULTIPLY", looks.math(nt, "SUBTRACT", 1.0, sep.outputs["X"]), 5.0))
    edge = looks.math(nt, "MINIMUM", edge, 1.0)
    inten = looks.math(nt, "ADD", 0.13, looks.math(nt, "ADD", looks.math(nt, "MULTIPLY", pulse, 0.22),
                                                    looks.math(nt, "MULTIPLY", lines, 0.0)))
    inten = looks.math(nt, "MULTIPLY", looks.math(nt, "MULTIPLY", inten, depth), edge)
    inten = looks.math(nt, "MULTIPLY", inten, on.outputs[0])
    em = looks.node(nt, "ShaderNodeEmission", Color=(0.25, 0.75, 1.0, 1))
    looks.link(nt, looks.math(nt, "MULTIPLY", inten, 1.1), em.inputs["Strength"])
    tr = looks.node(nt, "ShaderNodeBsdfTransparent")
    a = looks.node(nt, "ShaderNodeAddShader")
    looks.link(nt, tr.outputs[0], a.inputs[0])
    looks.link(nt, em.outputs[0], a.inputs[1])
    looks.link(nt, a.outputs[0], out.inputs[0])
    M["beam"] = m
    return M
