"""Plano 3C (24.8–30.3 s): CIERRE PROGRESIVO. Corte transversal de la vena tratada en su tejido.
Fases (comprimidas en el tiempo; el texto en pantalla indica horas → días → semanas):
  1) la espuma se disipa; la capa interna reacciona (edema e inflamación de la pared);
  2) la luz se estrecha y se ocupa por un material de reparación (esclerotrombo) que se organiza;
  3) la vena se transforma en un cordón fibroso más pequeño, sin luz, que el organismo reabsorbe con el tiempo.
Nada desaparece de golpe: todos los cambios son graduales.
Unidades: radio externo inicial de la vena = 1."""
import numpy as np

from lib import bl, looks

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(4, 1, 2, 3, 8), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

LEN = 3.2


def phase(t):
    """Parámetros de la sección en el tiempo local."""
    edema = bl.smoothstep(0.6, 2.2, t) * (1 - 0.6 * bl.smoothstep(3.6, 5.2, t))
    close = bl.smoothstep(1.4, 3.9, t)            # 0: luz abierta -> 1: luz cerrada
    fib = bl.smoothstep(2.6, 4.9, t)              # organización fibrosa
    shrink = bl.smoothstep(3.4, 5.4, t)           # retracción del cordón
    r_out = 1.0 + 0.10 * edema - 0.42 * shrink
    r_lum = max(0.78 * (1 - close) ** 1.3, 0.0) * (r_out / 1.0)
    return dict(edema=edema, close=close, fib=fib, shrink=shrink, r_out=r_out, r_lum=r_lum,
                foam=1 - bl.smoothstep(0.2, 1.6, t))


def section_material():
    """Cara de corte: capas concéntricas calculadas por radio (íntima, media, adventicia, luz)."""
    m, nt, out = bl.new_mat("Section")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    sep = looks.node(nt, "ShaderNodeSeparateXYZ")
    looks.link(nt, tc.outputs["Object"], sep.inputs[0])
    r = looks.math(nt, "SQRT", looks.math(nt, "ADD", looks.math(nt, "MULTIPLY", sep.outputs["X"], sep.outputs["X"]),
                                          looks.math(nt, "MULTIPLY", sep.outputs["Y"], sep.outputs["Y"])))
    v_lum = bl.value_node(nt, "r_lum", 0.78)
    v_out = bl.value_node(nt, "r_out", 1.0)
    v_ed = bl.value_node(nt, "edema", 0.0)
    v_fib = bl.value_node(nt, "fib", 0.0)
    # radio normalizado dentro de la pared: 0 en la luz, 1 en el borde externo
    rel = looks.math(nt, "DIVIDE", looks.math(nt, "SUBTRACT", r, v_lum.outputs[0]),
                     looks.math(nt, "MAXIMUM", looks.math(nt, "SUBTRACT", v_out.outputs[0], v_lum.outputs[0]), 0.001))
    ramp = looks.node(nt, "ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.interpolation = "EASE"
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.92, 0.55, 0.55, 1)       # íntima / endotelio
    cr.elements[1].position = 1.0
    cr.elements[1].color = (0.88, 0.80, 0.70, 1)       # adventicia
    e = cr.elements.new(0.07)
    e.color = (0.98, 0.80, 0.78, 1)                    # íntima (línea pálida)
    e = cr.elements.new(0.12)
    e.color = (0.74, 0.22, 0.26, 1)                    # media (músculo liso)
    e = cr.elements.new(0.60)
    e.color = (0.66, 0.20, 0.24, 1)
    e = cr.elements.new(0.70)
    e.color = (0.90, 0.74, 0.66, 1)                    # adventicia (colágeno)
    looks.link(nt, looks.math(nt, "MAXIMUM", rel, 0.0), ramp.inputs[0])
    # anillos de músculo liso (estriación circular) en la media
    ring = looks.math(nt, "POWER", looks.math(nt, "ABSOLUTE", looks.math(nt, "SINE", looks.math(nt, "MULTIPLY", r, 70.0))), 6.0)
    wall = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, looks.math(nt, "MULTIPLY", ring, 0.18), wall.inputs["Factor"])
    looks.link(nt, ramp.outputs[0], wall.inputs["A"])
    wall.inputs["B"].default_value = (0.55, 0.16, 0.18, 1)
    # inflamación: enrojece la pared; fibrosis: la vuelve blanquecina
    infl = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, looks.math(nt, "MULTIPLY", v_ed.outputs[0], 0.55), infl.inputs["Factor"])
    looks.link(nt, wall.outputs["Result"], infl.inputs["A"])
    infl.inputs["B"].default_value = (0.82, 0.12, 0.14, 1)
    fibc = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, looks.math(nt, "MULTIPLY", v_fib.outputs[0], 0.75), fibc.inputs["Factor"])
    looks.link(nt, infl.outputs["Result"], fibc.inputs["A"])
    fibc.inputs["B"].default_value = (0.93, 0.86, 0.82, 1)
    # material de la luz (esclerotrombo que se organiza): rojo oscuro -> rosado -> blanquecino fibroso
    noise = looks.node(nt, "ShaderNodeTexNoise", Scale=9.0, Detail=3.0)
    looks.link(nt, tc.outputs["Object"], noise.inputs["Vector"])
    lum = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, v_fib.outputs[0], lum.inputs["Factor"])
    lum.inputs["A"].default_value = (0.38, 0.03, 0.05, 1)
    lum.inputs["B"].default_value = (0.90, 0.74, 0.72, 1)
    lum2 = looks.node(nt, "ShaderNodeMix", _data_type="RGBA", _blend_type="MULTIPLY")
    looks.link(nt, looks.math(nt, "MULTIPLY", noise.outputs["Fac"], 0.9), lum2.inputs["Factor"])
    looks.link(nt, lum.outputs["Result"], lum2.inputs["A"])
    lum2.inputs["B"].default_value = (0.75, 0.6, 0.6, 1)
    v_foam = bl.value_node(nt, "foam", 1.0)
    lum3 = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, v_foam.outputs[0], lum3.inputs["Factor"])
    looks.link(nt, lum2.outputs["Result"], lum3.inputs["A"])
    lum3.inputs["B"].default_value = (0.90, 0.92, 0.96, 1)    # espuma residual (blanca)
    inside = looks.math(nt, "LESS_THAN", r, v_lum.outputs[0])
    col = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, inside, col.inputs["Factor"])
    looks.link(nt, fibc.outputs["Result"], col.inputs["A"])
    looks.link(nt, lum3.outputs["Result"], col.inputs["B"])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.42, **{"Coat Weight": 0.45, "Coat Roughness": 0.12})
    looks.link(nt, col.outputs["Result"], p.inputs["Base Color"])
    bump = looks.node(nt, "ShaderNodeBump", Strength=0.12, Distance=0.02)
    looks.link(nt, noise.outputs["Fac"], bump.inputs["Height"])
    looks.link(nt, bump.outputs[0], p.inputs["Normal"])
    looks.link(nt, p.outputs[0], out.inputs[0])
    return m


def adventitia_material():
    """Superficie externa de la vena: tejido rosado húmedo con vasa vasorum; palidece con la fibrosis."""
    m, nt, out = bl.new_mat("Adventitia")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    nz = looks.node(nt, "ShaderNodeTexNoise", Scale=4.0, Detail=3.0)
    looks.link(nt, tc.outputs["Object"], nz.inputs["Vector"])
    vv = looks.node(nt, "ShaderNodeTexWave", Scale=2.2, Distortion=9.0, **{"Detail": 2.0})
    vv.bands_direction = "Z"
    looks.link(nt, tc.outputs["Object"], vv.inputs["Vector"])
    vess = looks.math(nt, "POWER", vv.outputs["Fac"], 18.0)
    v_fib = bl.value_node(nt, "fib", 0.0)
    v_ed = bl.value_node(nt, "edema", 0.0)
    base = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, nz.outputs["Fac"], base.inputs["Factor"])
    base.inputs["A"].default_value = (0.62, 0.30, 0.32, 1)
    base.inputs["B"].default_value = (0.80, 0.50, 0.48, 1)
    ves = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, looks.math(nt, "MULTIPLY", vess, looks.math(nt, "SUBTRACT", 1.0, v_fib.outputs[0])), ves.inputs["Factor"])
    looks.link(nt, base.outputs["Result"], ves.inputs["A"])
    ves.inputs["B"].default_value = (0.45, 0.04, 0.07, 1)
    inf = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, looks.math(nt, "MULTIPLY", v_ed.outputs[0], 0.35), inf.inputs["Factor"])
    looks.link(nt, ves.outputs["Result"], inf.inputs["A"])
    inf.inputs["B"].default_value = (0.78, 0.16, 0.18, 1)
    fb = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    looks.link(nt, looks.math(nt, "MULTIPLY", v_fib.outputs[0], 0.7), fb.inputs["Factor"])
    looks.link(nt, inf.outputs["Result"], fb.inputs["A"])
    fb.inputs["B"].default_value = (0.88, 0.80, 0.78, 1)
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.35, **{"Coat Weight": 0.6, "Coat Roughness": 0.1,
                                                                      "Sheen Weight": 0.3})
    looks.link(nt, fb.outputs["Result"], p.inputs["Base Color"])
    tl = looks.node(nt, "ShaderNodeBsdfTranslucent")
    looks.link(nt, fb.outputs["Result"], tl.inputs["Color"])
    mx = looks.node(nt, "ShaderNodeMixShader", Fac=0.25)
    looks.link(nt, p.outputs[0], mx.inputs[1])
    looks.link(nt, tl.outputs[0], mx.inputs[2])
    bump = looks.node(nt, "ShaderNodeBump", Strength=0.2, Distance=0.03)
    looks.link(nt, nz.outputs["Fac"], bump.inputs["Height"])
    looks.link(nt, bump.outputs[0], p.inputs["Normal"])
    looks.link(nt, mx.outputs[0], out.inputs[0])
    return m


def build(sc, ctx):
    rng = np.random.default_rng(31)
    bl.world(sc, top=(0.012, 0.035, 0.075), bottom=(0.0, 0.004, 0.012))
    sec_m = section_material()
    # disco de corte (cara frontal z=0) y cilindro externo de la vena
    nr, na = 48, 96
    rs = np.linspace(0, 1, nr)
    ang = np.linspace(0, 2 * np.pi, na, endpoint=False)
    dv = np.array([(r * np.cos(a), r * np.sin(a), 0.0) for r in rs for a in ang])
    df = []
    for i in range(nr - 1):
        for j in range(na):
            a0 = i * na + j
            b0 = i * na + (j + 1) % na
            df.append((a0, a0 + na, b0 + na, b0))
    disk = bl.mesh_object("SectionFace", dv, df, mat=sec_m)
    outer_m = adventitia_material()
    zs = np.linspace(0, -LEN, 40)
    cv = np.array([(np.cos(a), np.sin(a), z) for z in zs for a in ang])
    cf = []
    for i in range(len(zs) - 1):
        for j in range(na):
            a0 = i * na + j
            b0 = i * na + (j + 1) % na
            cf.append((a0, b0, b0 + na, a0 + na))
    tube = bl.mesh_object("VeinOuter", cv, cf, mat=outer_m)
    import bpy
    from mathutils import Vector
    root = bpy.data.objects.new("Specimen", None)
    bl.link(root)
    axis_n = Vector((-0.40, -0.60, -0.69)).normalized()        # normal de la cara de corte (hacia cámara)
    root.rotation_euler = Vector((0, 0, 1)).rotation_difference(axis_n).to_euler()
    disk.parent = root
    tube.parent = root

    # tejido graso que rodea (cortado), con hueco que se adapta a la vena
    fat_m = bl.new_mat("FatSec")[0]
    nt = fat_m.node_tree
    out = nt.nodes["Material Output"]
    tc = looks.node(nt, "ShaderNodeTexCoord")
    vo = looks.node(nt, "ShaderNodeTexVoronoi", Scale=2.2, _feature="DISTANCE_TO_EDGE")
    looks.link(nt, tc.outputs["Object"], vo.inputs["Vector"])
    ramp = looks.node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.72, 0.36, 0.28, 1)
    ramp.color_ramp.elements[1].position = 0.06
    ramp.color_ramp.elements[1].color = (0.95, 0.75, 0.38, 1)
    looks.link(nt, vo.outputs["Distance"], ramp.inputs[0])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.35, **{"Coat Weight": 0.35})
    looks.link(nt, ramp.outputs[0], p.inputs["Base Color"])
    looks.link(nt, p.outputs[0], out.inputs[0])
    ghost = looks.xray_layer("FatGhost", rim=(0.45, 0.7, 1.0), strength=0.35, power=2.5,
                             fill=(0.25, 0.45, 0.8), fill_strength=0.003)
    gv = np.array([(2.3 * np.cos(a), 2.3 * np.sin(a), z) for z in zs for a in ang])
    # (sin volumen fantasma: distraía como un aro azul)
    # partículas de ambiente
    nd = 120
    dust0 = np.column_stack([rng.uniform(-3, 5, nd), rng.uniform(1.5, 8, nd), rng.uniform(-3, 5, nd)])
    bl.points_object("Dust", dust0, rng.uniform(0.006, 0.02, nd), mat=bl.emission_mat("Dust", (0.4, 0.65, 1.0), 1.5))

    # burbujas residuales de espuma en la luz al inicio
    nb = 140
    br = np.sqrt(rng.uniform(0, 1, nb)) * 0.62
    ba = rng.uniform(0, 2 * np.pi, nb)
    bz = rng.uniform(-0.25, 0.05, nb)
    brad = rng.uniform(0.035, 0.09, nb)
    bub = bl.points_object("Foam", np.column_stack([br * np.cos(ba), br * np.sin(ba), bz]), brad,
                           mat=looks.bubble_fast("FoamSec", body=0.3, rim_strength=1.0))
    bub.parent = root

    bl.area_light(sc, "Key", (-4.5, -5.0, 3.5), (0.6, 0.9, 1.0), 520, size=3, color=(1.0, 0.94, 0.88))
    bl.area_light(sc, "Rim", (3.0, 4.5, 4.5), (0.8, 1.2, 1.4), 1100, size=3, color=(0.55, 0.75, 1.0))
    bl.area_light(sc, "Rim2", (-2.5, 4.0, 0.5), (0.8, 1.2, 1.4), 600, size=3, color=(0.7, 0.85, 1.0))
    bl.area_light(sc, "Fill", (4.5, -4.0, -1.0), (0.5, 0.6, 0.7), 140, size=4, color=(0.75, 0.85, 1.0))

    cam = bl.camera(sc, lens=40, clip=(0.05, 100), dof=(5.0, 3.5))
    cam_keys = [(0.0, (-2.6, -5.4, -1.3)), (2.8, (-2.2, -5.0, -1.6)), (5.5, (-1.6, -4.4, -1.6))]
    tgt_keys = [(0.0, (0.55, 0.95, 1.05)), (2.8, (0.5, 0.85, 0.95)), (5.5, (0.4, 0.7, 0.8))]

    def update(t):
        P = phase(t)
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        bl.set_camera(cam, p, g, focus=np.linalg.norm(np.array(g) - p))
        # la cara de corte se escala con el radio externo; el sombreador trabaja en radios normalizados
        disk.scale = (P["r_out"], P["r_out"], 1)
        bl.set_value(outer_m, "fib", float(P["fib"]))
        bl.set_value(outer_m, "edema", float(P["edema"]))
        bl.set_value(sec_m, "r_out", 1.0)
        bl.set_value(sec_m, "r_lum", float(P["r_lum"] / max(P["r_out"], 1e-3)))
        bl.set_value(sec_m, "edema", float(P["edema"]))
        bl.set_value(sec_m, "fib", float(P["fib"]))
        bl.set_value(sec_m, "foam", float(P["foam"]))
        tube.scale = (P["r_out"], P["r_out"], 1)
        fo = P["foam"]
        pos = np.column_stack([br * np.cos(ba) * P["r_lum"] / 0.78, br * np.sin(ba) * P["r_lum"] / 0.78, bz])
        bl.update_points(bub, pos, radius=brad * fo)

    return update


def anchors(t):
    return {"lumen": (0.0, 0.0, 0.0)}
