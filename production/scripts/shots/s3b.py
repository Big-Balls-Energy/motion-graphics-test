"""Plano 3B (20.3–25.3 s): ACCIÓN SOBRE LA PARED VENOSA. Macro del endotelio (revestimiento interno).
Las microburbujas quedan en contacto con las células endoteliales; el esclerosante (detergente) altera sus
membranas: las células palidecen, se hinchan, se abren las uniones intercelulares y algunas se desprenden
(descamación), exponiendo el subendotelio (colágeno), donde empiezan a adherirse plaquetas. Es una reacción
local y progresiva, sin destrucción violenta del tejido.
Unidades: 1 = 10 µm (las burbujas están estilizadas en tamaño)."""
import numpy as np
from scipy.spatial import Voronoi

from lib import bl, looks

RENDER = dict(res=(1080, 1920), spp=8, threshold=0.05, bounces=(4, 1, 2, 3, 8), motion_blur=True,
              shutter=0.5, look="AgX - Medium High Contrast")

FOG = (0.28, 0.07, 0.07)
DENS = 0.012
BUBBLES = [(-7.5, 21.0, 5.6), (5.5, 26.0, 6.4), (-2.0, 33.0, 5.0), (12.5, 18.0, 4.2), (-14.0, 30.0, 5.4),
           (9.0, 37.0, 5.8)]


def make_cells(rng, size=(40.0, 52.0), n=700, elong=2.4, gap=0.035):
    """Teselación de Voronoi anisótropa (células alargadas en y = sentido del flujo)."""
    W, H = size
    pts = np.column_stack([rng.uniform(-W / 2 - 3, W / 2 + 3, n), rng.uniform(-6, H + 3, n) / elong])
    # relajación de Lloyd para regularizar el empedrado
    for _ in range(3):
        vor = Voronoi(pts)
        new = []
        for i, reg in enumerate(vor.point_region):
            r = vor.regions[reg]
            if -1 in r or len(r) == 0:
                new.append(pts[i])
                continue
            poly = vor.vertices[r]
            new.append(poly.mean(0))
        pts = np.array(new)
    vor = Voronoi(pts)
    cells = []
    for i, reg in enumerate(vor.point_region):
        r = vor.regions[reg]
        if -1 in r or len(r) < 3:
            continue
        poly = vor.vertices[r] * np.array([1.0, elong])
        c = poly.mean(0)
        if abs(c[0]) > W / 2 + 1 or c[1] < -4 or c[1] > H + 1:
            continue
        ang = np.arctan2(poly[:, 1] - c[1], poly[:, 0] - c[0])
        poly = poly[np.argsort(ang)]
        poly = c + (poly - c) * (1 - gap)
        cells.append((c, poly))
    return cells


def cell_mesh(cells, rings=6, h=0.34, nuc=0.20):
    """Cúpula por célula + núcleo elíptico. Devuelve verts, faces, cell_index por vértice, radios relativos."""
    V, Fc, CI, RR = [], [], [], []
    for ci, (c, poly) in enumerate(cells):
        base = len(V)
        m = len(poly)
        for k in range(rings + 1):
            s = 1 - k / rings                       # 1 en el borde, 0 en el centro
            if k == rings:
                V.append((c[0], c[1], h + nuc))
                CI.append(ci)
                RR.append(0.0)
                break
            z = h * np.clip(1 - s ** 2, 0, 1) ** 0.6 + nuc * np.exp(-(s / 0.5) ** 2)
            for p in poly:
                q = c + (p - c) * s
                V.append((q[0], q[1], z))
                CI.append(ci)
                RR.append(s)
        for k in range(rings - 1):
            for j in range(m):
                a = base + k * m + j
                b = base + k * m + (j + 1) % m
                Fc.append((a, b, b + m, a + m))
        center = base + rings * m
        for j in range(m):
            a = base + (rings - 1) * m + j
            b = base + (rings - 1) * m + (j + 1) % m
            Fc.append((a, b, center))
    return np.array(V, float), Fc, np.array(CI), np.array(RR)


def build(sc, ctx):
    rng = np.random.default_rng(21)
    bl.world(sc, top=FOG, bottom=FOG)
    cells = make_cells(rng)
    V0, F0, CI, RR = cell_mesh(cells)
    centers = np.array([c for c, _ in cells])
    nc = len(cells)

    # material de las células: color según "react" (atributo por vértice)
    m, nt, out = bl.new_mat("Endo")
    at = looks.node(nt, "ShaderNodeAttribute", _attribute_name="react")
    rr_at = looks.node(nt, "ShaderNodeAttribute", _attribute_name="rr")
    healthy = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    healthy.inputs["A"].default_value = (0.95, 0.42, 0.42, 1)    # núcleo/centro
    healthy.inputs["B"].default_value = (0.78, 0.22, 0.26, 1)    # citoplasma
    looks.link(nt, rr_at.outputs["Fac"], healthy.inputs["Factor"])
    col = looks.node(nt, "ShaderNodeMix", _data_type="RGBA")
    tn = looks.node(nt, "ShaderNodeAttribute", _attribute_name="tint")
    tint = looks.node(nt, "ShaderNodeMix", _data_type="RGBA", _blend_type="MULTIPLY")
    tint.inputs["Factor"].default_value = 1.0
    looks.link(nt, healthy.outputs["Result"], tint.inputs["A"])
    tramp = looks.node(nt, "ShaderNodeValToRGB")
    tramp.color_ramp.elements[0].color = (0.82, 0.86, 0.9, 1)
    tramp.color_ramp.elements[1].color = (1.0, 0.97, 0.95, 1)
    looks.link(nt, tn.outputs["Fac"], tramp.inputs[0])
    looks.link(nt, tramp.outputs[0], tint.inputs["B"])
    looks.link(nt, tint.outputs["Result"], col.inputs["A"])
    col.inputs["B"].default_value = (0.86, 0.74, 0.70, 1)          # célula alterada: pálida
    looks.link(nt, at.outputs["Fac"], col.inputs["Factor"])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.28, **{"Coat Weight": 0.7, "Coat Roughness": 0.06,
                                                                      "Sheen Weight": 0.3})
    looks.link(nt, col.outputs["Result"], p.inputs["Base Color"])
    tl = looks.node(nt, "ShaderNodeBsdfTranslucent")
    looks.link(nt, col.outputs["Result"], tl.inputs["Color"])
    mx = looks.node(nt, "ShaderNodeMixShader", Fac=0.3)
    looks.link(nt, p.outputs[0], mx.inputs[1])
    looks.link(nt, tl.outputs[0], mx.inputs[2])
    fd = looks.node(nt, "ShaderNodeAttribute", _attribute_name="fade")
    trn = looks.node(nt, "ShaderNodeBsdfTransparent")
    mfd = nt.nodes.new("ShaderNodeMixShader")
    looks.link(nt, fd.outputs["Fac"], mfd.inputs[0])
    looks.link(nt, looks.fog_wrap(nt, mx.outputs[0], FOG, density=DENS), mfd.inputs[1])
    looks.link(nt, trn.outputs[0], mfd.inputs[2])
    looks.link(nt, mfd.outputs[0], out.inputs[0])
    endo = bl.mesh_object("Endothelium", V0, F0, mat=m)
    a_re = endo.data.attributes.new("react", "FLOAT", "POINT")
    a_rr = endo.data.attributes.new("rr", "FLOAT", "POINT")
    a_fd = endo.data.attributes.new("fade", "FLOAT", "POINT")
    a_tn = endo.data.attributes.new("tint", "FLOAT", "POINT")
    a_tn.data.foreach_set("value", rng.uniform(0, 1, nc)[CI].astype(np.float32))
    a_rr.data.foreach_set("value", RR.astype(np.float32))

    # subendotelio (membrana basal / colágeno) bajo las células
    m2, nt, out = bl.new_mat("Subendo")
    tc = looks.node(nt, "ShaderNodeTexCoord")
    wv = looks.node(nt, "ShaderNodeTexWave", Scale=0.35, Distortion=6.0, **{"Detail": 3.0})
    looks.link(nt, tc.outputs["Object"], wv.inputs["Vector"])
    ramp = looks.node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.62, 0.40, 0.34, 1)
    ramp.color_ramp.elements[1].color = (0.95, 0.86, 0.72, 1)
    looks.link(nt, wv.outputs["Fac"], ramp.inputs[0])
    p = looks.node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.45, **{"Coat Weight": 0.4})
    looks.link(nt, ramp.outputs[0], p.inputs["Base Color"])
    looks.link(nt, looks.fog_wrap(nt, p.outputs[0], FOG, density=DENS), out.inputs[0])
    bl.mesh_object("Subendo", np.array([[-40, -20, 0.02], [40, -20, 0.02], [40, 80, 0.02], [-40, 80, 0.02]]),
                   [(0, 1, 2, 3)], mat=m2)

    # microburbujas apoyadas en la pared
    bub_m = looks.bubble_fast("BubbleMacro", fog=FOG, fog_density=DENS, body=0.04, rim_strength=0.8, gloss=0.55)
    bpos = np.array([(x, y, r * 0.9) for x, y, r in BUBBLES])
    brad = np.array([r for _, _, r in BUBBLES])
    bubbles = bl.points_object("Bubbles", bpos, brad, mat=bub_m)
    bdrift = rng.normal(0, 0.12, (len(BUBBLES), 2))

    # tiempo de reacción de cada célula: según distancia al punto de contacto de la burbuja más cercana
    d = np.min(np.linalg.norm(centers[:, None, :] - bpos[None, :, :2], axis=2) - brad[None, :] * 0.45, axis=1)
    t0 = 0.4 + np.clip(d, 0, None) * 0.16 + rng.uniform(0, 0.5, nc)
    detach = (rng.uniform(0, 1, nc) < 0.10) & (d < 5.0)
    det_v = np.column_stack([rng.normal(0, 0.6, nc), rng.normal(0.8, 0.4, nc), rng.uniform(1.0, 2.0, nc)])
    det_w = rng.normal(0, 0.35, (nc, 3))

    # plaquetas que se adhieren al subendotelio expuesto
    from lib.anatomy import rbc_mesh
    pv, pf = rbc_mesh(R=1.0, n_r=8, n_a=20)
    plate = bl.mesh_object("Platelet", pv * np.array([0.16, 0.16, 0.5]), pf,
                           mat=bl.principled("Platelet", base=(0.95, 0.80, 0.55), rough=0.35, coat=0.4))
    n_p = 60
    sel = rng.choice(np.where(d < 7.0)[0], n_p)
    p_tgt = np.column_stack([centers[sel] + rng.normal(0, 0.6, (n_p, 2)), np.full(n_p, 0.08)])
    p_start = p_tgt + np.column_stack([rng.normal(0, 3, n_p), rng.uniform(-8, -3, n_p), rng.uniform(3, 7, n_p)])
    p_t = rng.uniform(2.6, 4.2, n_p)
    plates = bl.instances_object("Platelets", p_start, plate, np.ones(n_p), rng.uniform(0, 6, (n_p, 3)))

    # luces
    bl.area_light(sc, "Key", (-16, -6, 30), (0, 18, 0), 7000, size=6, color=(1.0, 0.92, 0.88))
    bl.area_light(sc, "Rim", (8, 62, 14), (0, 18, 0), 12000, size=8, color=(1.0, 0.70, 0.62))
    bl.area_light(sc, "Fill", (26, 2, 12), (0, 15, 0), 2200, size=6, color=(0.85, 0.85, 1.0))

    cam = bl.camera(sc, lens=32, clip=(0.1, 400), dof=(22, 2.0))
    cam_keys = [(0.0, (2.0, -6.0, 13.0)), (2.5, (1.0, -3.0, 11.5)), (5.0, (0.0, -0.5, 10.0))]
    tgt_keys = [(0.0, (0.0, 15.0, 0.5)), (2.5, (-0.5, 16.0, 0.5)), (5.0, (-1.0, 17.0, 0.5))]

    def update(t):
        p = bl.hermite_path(t, cam_keys)
        g = bl.hermite_path(t, tgt_keys)
        bl.set_camera(cam, p, g, focus=np.linalg.norm(np.array(g) - p) * 0.95)
        r = bl.smoothstep(t0, t0 + 1.6, t)                 # progreso de la reacción por célula
        swell = 1 + 0.38 * r                               # tumefacción
        shrink = 1 - 0.09 * r                              # retracción: se abren las uniones
        lift = np.where(detach, bl.smoothstep(t0 + 1.2, t0 + 3.2, t), 0.0)
        cpos = np.column_stack([centers, np.zeros(nc)])
        vc = cpos[CI]
        loc = V0 - vc
        loc[:, :2] *= shrink[CI][:, None]
        loc[:, 2] *= swell[CI]
        # células que se desprenden: suben, rotan suavemente y se alejan con el flujo
        ang = det_w[CI] * lift[CI][:, None] * 0.9
        cz, sz = np.cos(ang[:, 2]), np.sin(ang[:, 2])
        cx, sx = np.cos(ang[:, 0]), np.sin(ang[:, 0])
        x1 = loc[:, 0] * cz - loc[:, 1] * sz
        y1 = loc[:, 0] * sz + loc[:, 1] * cz
        z1 = loc[:, 2]
        y2 = y1 * cx - z1 * sx
        z2 = y1 * sx + z1 * cx
        loc = np.column_stack([x1, y2, z2])
        off = det_v[CI] * (lift[CI][:, None] ** 1.4) * 2.4
        V = vc + loc + off
        endo.data.vertices.foreach_set("co", V.astype(np.float32).ravel())
        a_re.data.foreach_set("value", r[CI].astype(np.float32))
        a_fd.data.foreach_set("value", (lift[CI] ** 1.5).astype(np.float32))
        endo.data.update()
        bp = bpos.copy()
        bp[:, :2] += bdrift * t
        bl.update_points(bubbles, bp)
        k = bl.smoothstep(p_t - 1.2, p_t, t)[:, None]
        pp = p_start + (p_tgt - p_start) * k
        bl.update_points(plates, pp, scale=np.where(t > p_t - 1.4, 1.0, 0.0))

    return update


def anchors(t):
    return {"endo": (-5.0, 8.0, 0.6), "bubble": (5.5, 26.0, 9.0), "exposed": (-5.0, 18.0, 0.3)}
