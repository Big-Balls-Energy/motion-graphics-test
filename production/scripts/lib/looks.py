"""Materiales del look "documental médico": piel con revelado por escáner, capas en rayos X,
venas con volumen, eritrocitos, microburbujas, endotelio y niebla de profundidad."""
import bpy

from . import bl


def node(nt, typ, x=0, y=0, **inputs):
    n = nt.nodes.new(typ)
    n.location = (x, y)
    for k, v in inputs.items():
        if isinstance(k, str) and k.startswith("_"):
            setattr(n, k[1:], v)
            continue
        n.inputs[k].default_value = v
    return n


def link(nt, a, b):
    nt.links.new(a, b)


def math(nt, op, a, b=None, clamp=False):
    n = nt.nodes.new("ShaderNodeMath")
    n.operation = op
    n.use_clamp = clamp
    for i, v in enumerate([a, b]):
        if v is None:
            continue
        if isinstance(v, (int, float)):
            n.inputs[i].default_value = v
        else:
            nt.links.new(v, n.inputs[i])
    return n.outputs[0]


def rgb(c):
    return (*c, 1.0) if len(c) == 3 else c


def fog_wrap(nt, shader_out, fog_color=(0.25, 0.02, 0.02), density_name="fog_density", density=0.0,
             strength=1.0):
    """Mezcla el sombreado con una emisión de niebla según la profundidad de cámara (fog barato)."""
    cam = nt.nodes.new("ShaderNodeCameraData")
    dens = bl.value_node(nt, density_name, density)
    prod = math(nt, "MULTIPLY", cam.outputs["View Z Depth"], dens.outputs[0])
    neg = math(nt, "MULTIPLY", prod, -1.0)
    ex = math(nt, "EXPONENT", neg)
    fac = math(nt, "SUBTRACT", 1.0, ex, clamp=True)
    em = node(nt, "ShaderNodeEmission", Color=rgb(fog_color), Strength=strength)
    mix = nt.nodes.new("ShaderNodeMixShader")
    link(nt, fac, mix.inputs[0])
    link(nt, shader_out, mix.inputs[1])
    link(nt, em.outputs[0], mix.inputs[2])
    return mix.outputs[0]


# ----------------------------------------------------------------------------- leg


def top_fade(nt, shader_out, z0=0.84, z1=0.95):
    """Desvanece el sombreado a transparente por encima de z0..z1 (coordenadas de objeto)."""
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    link(nt, tc.outputs["Object"], sep.inputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    mr.inputs["From Min"].default_value = z0
    mr.inputs["From Max"].default_value = z1
    link(nt, sep.outputs["Z"], mr.inputs["Value"])
    tr = nt.nodes.new("ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    link(nt, mr.outputs["Result"], mx.inputs[0])
    link(nt, shader_out, mx.inputs[1])
    link(nt, tr.outputs[0], mx.inputs[2])
    return mx.outputs[0]


def skin_reveal(name="SkinReveal", skin=(0.50, 0.30, 0.22), rim=(0.40, 0.66, 1.0), rim_strength=1.0,
                scan_color=(0.15, 0.65, 1.0)):
    """Piel opaca realista que se vuelve semitransparente (rayos X) por encima de 'scan_z'.
    Valores animables: scan_z, scan_w, xray (0..1 global), rim_k, scan_glow, opacity_x."""
    m, nt, out = bl.new_mat(name)
    tco = node(nt, "ShaderNodeTexCoord")
    sep = node(nt, "ShaderNodeSeparateXYZ")
    link(nt, tco.outputs["Object"], sep.inputs[0])
    z = sep.outputs["Z"]
    scan = bl.value_node(nt, "scan_z", 2.0)
    w = bl.value_node(nt, "scan_w", 0.02)
    xr = bl.value_node(nt, "xray", 0.0)
    rimk = bl.value_node(nt, "rim_k", rim_strength)
    glow = bl.value_node(nt, "scan_glow", 0.0)
    opx = bl.value_node(nt, "opacity_x", 0.035)
    # máscara del revelado: 1 por encima de la línea de escaneo
    lo = math(nt, "SUBTRACT", scan.outputs[0], w.outputs[0])
    hi = math(nt, "ADD", scan.outputs[0], w.outputs[0])
    mr = nt.nodes.new("ShaderNodeMapRange")
    mr.interpolation_type = "SMOOTHSTEP"
    link(nt, z, mr.inputs["Value"])
    link(nt, lo, mr.inputs["From Min"])
    link(nt, hi, mr.inputs["From Max"])
    mask = math(nt, "MULTIPLY", mr.outputs["Result"], xr.outputs[0])
    # piel opaca: tono con variación, poros (bump), coat y sheen suaves
    tc = node(nt, "ShaderNodeTexCoord")
    nz = node(nt, "ShaderNodeTexNoise", Scale=18.0, Detail=3.0, Roughness=0.55)
    link(nt, tc.outputs["Object"], nz.inputs["Vector"])
    ramp = node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = rgb((skin[0] * 0.86, skin[1] * 0.80, skin[2] * 0.82))
    ramp.color_ramp.elements[1].color = rgb((skin[0] * 1.08, skin[1] * 1.04, skin[2] * 1.02))
    link(nt, nz.outputs["Fac"], ramp.inputs[0])
    p = node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.48, **{"Coat Weight": 0.12, "Coat Roughness": 0.35,
                                                                "Sheen Weight": 0.12, "Specular IOR Level": 0.5})
    p.inputs["Sheen Tint"].default_value = rgb((1.0, 0.85, 0.8))
    link(nt, ramp.outputs[0], p.inputs["Base Color"])
    # rayos X: transparente + brillo especular leve + borde emisivo (fresnel)
    lw = node(nt, "ShaderNodeLayerWeight", Blend=0.35)
    facing = math(nt, "POWER", lw.outputs["Facing"], 2.2)
    rim_em = node(nt, "ShaderNodeEmission", Color=rgb(rim))
    link(nt, math(nt, "MULTIPLY", facing, rimk.outputs[0]), rim_em.inputs["Strength"])
    body_em = node(nt, "ShaderNodeEmission", Color=rgb((skin[0], skin[1] * 0.85, skin[2] * 0.8)), Strength=0.008)
    trans = node(nt, "ShaderNodeBsdfTransparent")
    gloss = node(nt, "ShaderNodeBsdfGlossy", Roughness=0.35)
    gloss.inputs["Color"].default_value = rgb((0.8, 0.9, 1.0))
    mg = nt.nodes.new("ShaderNodeMixShader")
    link(nt, opx.outputs[0], mg.inputs[0])
    link(nt, trans.outputs[0], mg.inputs[1])
    link(nt, gloss.outputs[0], mg.inputs[2])
    add1 = node(nt, "ShaderNodeAddShader")
    link(nt, mg.outputs[0], add1.inputs[0])
    link(nt, rim_em.outputs[0], add1.inputs[1])
    add2 = node(nt, "ShaderNodeAddShader")
    link(nt, add1.outputs[0], add2.inputs[0])
    link(nt, body_em.outputs[0], add2.inputs[1])
    mix = nt.nodes.new("ShaderNodeMixShader")
    link(nt, mask, mix.inputs[0])
    link(nt, p.outputs[0], mix.inputs[1])
    link(nt, add2.outputs[0], mix.inputs[2])
    # línea de escaneo luminosa
    dist = math(nt, "ABSOLUTE", math(nt, "SUBTRACT", z, scan.outputs[0]))
    band = nt.nodes.new("ShaderNodeMapRange")
    band.interpolation_type = "SMOOTHSTEP"
    band.inputs["From Min"].default_value = 0.0
    band.inputs["From Max"].default_value = 0.006
    band.inputs["To Min"].default_value = 1.0
    band.inputs["To Max"].default_value = 0.0
    link(nt, dist, band.inputs["Value"])
    sc_em = node(nt, "ShaderNodeEmission", Color=rgb(scan_color))
    link(nt, math(nt, "MULTIPLY", band.outputs["Result"], glow.outputs[0]), sc_em.inputs["Strength"])
    add3 = node(nt, "ShaderNodeAddShader")
    link(nt, mix.outputs[0], add3.inputs[0])
    link(nt, sc_em.outputs[0], add3.inputs[1])
    vis = bl.value_node(nt, "vis", 1.0)
    trv = node(nt, "ShaderNodeBsdfTransparent")
    mxv = nt.nodes.new("ShaderNodeMixShader")
    link(nt, vis.outputs[0], mxv.inputs[0])
    link(nt, trv.outputs[0], mxv.inputs[1])
    link(nt, add3.outputs[0], mxv.inputs[2])
    link(nt, top_fade(nt, mxv.outputs[0]), out.inputs[0])
    return m


def xray_layer(name, rim=(0.9, 0.3, 0.25), strength=0.6, power=2.0, fill=(0, 0, 0), fill_strength=0.0):
    """Capa interna (músculo/hueso) vista como holograma: transparente + borde emisivo.
    Valor animable 'vis' (0..1)."""
    m, nt, out = bl.new_mat(name)
    vis = bl.value_node(nt, "vis", 1.0)
    lw = node(nt, "ShaderNodeLayerWeight", Blend=0.4)
    facing = math(nt, "POWER", lw.outputs["Facing"], power)
    em = node(nt, "ShaderNodeEmission", Color=rgb(rim))
    link(nt, math(nt, "MULTIPLY", math(nt, "MULTIPLY", facing, strength), vis.outputs[0]), em.inputs["Strength"])
    fe = node(nt, "ShaderNodeEmission", Color=rgb(fill))
    link(nt, math(nt, "MULTIPLY", vis.outputs[0], fill_strength), fe.inputs["Strength"])
    tr = node(nt, "ShaderNodeBsdfTransparent")
    a1 = node(nt, "ShaderNodeAddShader")
    link(nt, tr.outputs[0], a1.inputs[0])
    link(nt, em.outputs[0], a1.inputs[1])
    a2 = node(nt, "ShaderNodeAddShader")
    link(nt, a1.outputs[0], a2.inputs[0])
    link(nt, fe.outputs[0], a2.inputs[1])
    link(nt, top_fade(nt, a2.outputs[0]), out.inputs[0])
    return m


def vein(name, base=(0.05, 0.07, 0.32), glow=(0.12, 0.30, 1.0), glow_strength=1.2, rough=0.32,
         flow=False, flow_color=(1.0, 0.25, 0.25), flow_speed=0.25, flow_density=40.0, fade_top=True):
    """Vena con volumen: principled húmedo + emisión para leer a través de la piel.
    Valores animables: glow_k, dim (0=normal,1=cordón fibroso pálido), pulse, flow_t.
    Si flow=True, pulsos luminosos viajan a lo largo del atributo 'u' (sentido del retorno venoso)."""
    m, nt, out = bl.new_mat(name)
    gk = bl.value_node(nt, "glow_k", glow_strength)
    dim = bl.value_node(nt, "dim", 0.0)
    pulse = bl.value_node(nt, "pulse", 0.0)
    tc = node(nt, "ShaderNodeTexCoord")
    nz = node(nt, "ShaderNodeTexNoise", Scale=260.0, Detail=1.5)
    link(nt, tc.outputs["Object"], nz.inputs["Vector"])
    bump = node(nt, "ShaderNodeBump", Strength=0.25, Distance=0.0003)
    link(nt, nz.outputs["Fac"], bump.inputs["Height"])
    col = node(nt, "ShaderNodeMix", _data_type="RGBA")
    col.inputs["A"].default_value = rgb(base)
    col.inputs["B"].default_value = rgb((0.55, 0.50, 0.52))   # cordón fibroso pálido
    link(nt, dim.outputs[0], col.inputs["Factor"])
    p = node(nt, "ShaderNodeBsdfPrincipled", Roughness=rough, **{"Coat Weight": 0.6, "Coat Roughness": 0.15})
    link(nt, col.outputs["Result"], p.inputs["Base Color"])
    link(nt, bump.outputs[0], p.inputs["Normal"])
    lw = node(nt, "ShaderNodeLayerWeight", Blend=0.5)
    gcol = node(nt, "ShaderNodeMix", _data_type="RGBA")
    gcol.inputs["A"].default_value = rgb(glow)
    gcol.inputs["B"].default_value = rgb((0.35, 0.33, 0.36))
    link(nt, dim.outputs[0], gcol.inputs["Factor"])
    em = node(nt, "ShaderNodeEmission")
    link(nt, gcol.outputs["Result"], em.inputs["Color"])
    # intensidad: (0.55 + 0.45*facing) * glow_k * (1 - 0.8*dim) * (1 + pulse)
    s = math(nt, "ADD", 0.55, math(nt, "MULTIPLY", lw.outputs["Facing"], 0.45))
    s = math(nt, "MULTIPLY", s, gk.outputs[0])
    s = math(nt, "MULTIPLY", s, math(nt, "SUBTRACT", 1.0, math(nt, "MULTIPLY", dim.outputs[0], 0.8)))
    s = math(nt, "MULTIPLY", s, math(nt, "ADD", 1.0, pulse.outputs[0]))
    link(nt, s, em.inputs["Strength"])
    add = node(nt, "ShaderNodeAddShader")
    link(nt, p.outputs[0], add.inputs[0])
    link(nt, em.outputs[0], add.inputs[1])
    final = add.outputs[0]
    if flow:
        ft = bl.value_node(nt, "flow_t", 0.0)
        fk = bl.value_node(nt, "flow_k", 0.0)
        attr = node(nt, "ShaderNodeAttribute", _attribute_name="u")
        # fase = u*density - t*speed*density  -> pulsos que avanzan hacia u creciente
        ph = math(nt, "SUBTRACT", math(nt, "MULTIPLY", attr.outputs["Fac"], flow_density),
                  math(nt, "MULTIPLY", ft.outputs[0], flow_speed * flow_density))
        fr = math(nt, "FRACT", ph)
        pk = math(nt, "POWER", math(nt, "SINE", math(nt, "MULTIPLY", fr, 3.14159)), 6.0)
        fe = node(nt, "ShaderNodeEmission", Color=rgb(flow_color))
        link(nt, math(nt, "MULTIPLY", pk, fk.outputs[0]), fe.inputs["Strength"])
        add2 = node(nt, "ShaderNodeAddShader")
        link(nt, final, add2.inputs[0])
        link(nt, fe.outputs[0], add2.inputs[1])
        final = add2.outputs[0]
    # visibilidad global (para fundidos): mezcla con transparente
    vis = bl.value_node(nt, "vis", 1.0)
    tr = node(nt, "ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    link(nt, vis.outputs[0], mx.inputs[0])
    link(nt, tr.outputs[0], mx.inputs[1])
    link(nt, final, mx.inputs[2])
    link(nt, top_fade(nt, mx.outputs[0]) if fade_top else mx.outputs[0], out.inputs[0])
    return m


# ----------------------------------------------------------------------------- micro world


def vessel_wall(name, base=(0.42, 0.07, 0.08), fog=(0.20, 0.02, 0.025), fog_density=0.0, rough=0.28,
                translucent=0.35, noise_scale=3.0, bump_strength=0.35, emission=0.0):
    """Pared interna del vaso: húmeda (coat), con pliegues (bump) y translucidez (luz desde fuera)."""
    m, nt, out = bl.new_mat(name)
    tc = node(nt, "ShaderNodeTexCoord")
    nz = node(nt, "ShaderNodeTexNoise", Scale=noise_scale, Detail=3.0, Roughness=0.6)
    link(nt, tc.outputs["Object"], nz.inputs["Vector"])
    bump = node(nt, "ShaderNodeBump", Strength=bump_strength, Distance=0.02)
    link(nt, nz.outputs["Fac"], bump.inputs["Height"])
    ramp = node(nt, "ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = rgb((base[0] * 0.65, base[1] * 0.6, base[2] * 0.7))
    ramp.color_ramp.elements[1].color = rgb((min(base[0] * 1.35, 1), base[1] * 1.6, base[2] * 1.5))
    link(nt, nz.outputs["Fac"], ramp.inputs[0])
    p = node(nt, "ShaderNodeBsdfPrincipled", Roughness=rough, **{"Coat Weight": 0.7, "Coat Roughness": 0.08,
                                                                 "Specular IOR Level": 0.6})
    link(nt, ramp.outputs[0], p.inputs["Base Color"])
    link(nt, bump.outputs[0], p.inputs["Normal"])
    tl = node(nt, "ShaderNodeBsdfTranslucent")
    link(nt, ramp.outputs[0], tl.inputs["Color"])
    link(nt, bump.outputs[0], tl.inputs["Normal"])
    mx = node(nt, "ShaderNodeMixShader", Fac=translucent)
    link(nt, p.outputs[0], mx.inputs[1])
    link(nt, tl.outputs[0], mx.inputs[2])
    sh = mx.outputs[0]
    if emission:
        em = node(nt, "ShaderNodeEmission", Strength=emission)
        link(nt, ramp.outputs[0], em.inputs["Color"])
        a = node(nt, "ShaderNodeAddShader")
        link(nt, sh, a.inputs[0])
        link(nt, em.outputs[0], a.inputs[1])
        sh = a.outputs[0]
    link(nt, fog_wrap(nt, sh, fog, density=fog_density), out.inputs[0])
    return m


def membrane(name, color=(0.85, 0.62, 0.62), fog=(0.20, 0.02, 0.025), fog_density=0.0, translucent=0.55,
             emission=0.0):
    """Valva venosa: membrana fina, translúcida a contraluz."""
    m, nt, out = bl.new_mat(name)
    tc = node(nt, "ShaderNodeTexCoord")
    nz = node(nt, "ShaderNodeTexNoise", Scale=9.0, Detail=2.0)
    link(nt, tc.outputs["Object"], nz.inputs["Vector"])
    bump = node(nt, "ShaderNodeBump", Strength=0.15, Distance=0.01)
    link(nt, nz.outputs["Fac"], bump.inputs["Height"])
    p = node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.3, **{"Coat Weight": 0.5, "Coat Roughness": 0.1,
                                                               "Sheen Weight": 0.6})
    p.inputs["Base Color"].default_value = rgb(color)
    p.inputs["Sheen Tint"].default_value = rgb((1.0, 0.92, 0.9))
    link(nt, bump.outputs[0], p.inputs["Normal"])
    tl = node(nt, "ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = rgb((color[0], color[1] * 0.7, color[2] * 0.7))
    mx = node(nt, "ShaderNodeMixShader", Fac=translucent)
    link(nt, p.outputs[0], mx.inputs[1])
    link(nt, tl.outputs[0], mx.inputs[2])
    sh = mx.outputs[0]
    if emission:
        em = node(nt, "ShaderNodeEmission", Color=rgb(color), Strength=emission)
        a = node(nt, "ShaderNodeAddShader")
        link(nt, sh, a.inputs[0])
        link(nt, em.outputs[0], a.inputs[1])
        sh = a.outputs[0]
    link(nt, fog_wrap(nt, sh, fog, density=fog_density), out.inputs[0])
    return m


def rbc(name="RBC", color=(0.55, 0.02, 0.03), fog=(0.20, 0.02, 0.025), fog_density=0.0):
    """Eritrocito: rojo profundo, húmedo, con translucidez en los bordes (falso SSS)."""
    m, nt, out = bl.new_mat(name)
    p = node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.32, **{"Coat Weight": 0.45, "Coat Roughness": 0.12,
                                                                "Sheen Weight": 0.4})
    p.inputs["Base Color"].default_value = rgb(color)
    p.inputs["Sheen Tint"].default_value = rgb((1.0, 0.45, 0.4))
    tl = node(nt, "ShaderNodeBsdfTranslucent")
    tl.inputs["Color"].default_value = rgb((0.9, 0.08, 0.06))
    lw = node(nt, "ShaderNodeLayerWeight", Blend=0.5)
    mx = nt.nodes.new("ShaderNodeMixShader")
    link(nt, math(nt, "MULTIPLY", lw.outputs["Facing"], 0.45), mx.inputs[0])
    link(nt, p.outputs[0], mx.inputs[1])
    link(nt, tl.outputs[0], mx.inputs[2])
    em = node(nt, "ShaderNodeEmission", Color=rgb((0.6, 0.03, 0.02)), Strength=0.08)
    a = node(nt, "ShaderNodeAddShader")
    link(nt, mx.outputs[0], a.inputs[0])
    link(nt, em.outputs[0], a.inputs[1])
    link(nt, fog_wrap(nt, a.outputs[0], fog, density=fog_density), out.inputs[0])
    return m


def bubble(name="Bubble", tint=(0.85, 0.93, 1.0), fog=(0.20, 0.02, 0.025), fog_density=0.0, film=420.0,
           body=0.10, rim_strength=0.9):
    """Microburbuja de espuma: película fina (iridiscencia sutil) con reflexión fresnel y borde lechoso.
    Valor animable 'vis'."""
    m, nt, out = bl.new_mat(name)
    p = node(nt, "ShaderNodeBsdfPrincipled", Roughness=0.03, **{"Transmission Weight": 1.0, "IOR": 1.02,
                                                                "Thin Film Thickness": film, "Thin Film IOR": 1.36,
                                                                "Specular IOR Level": 0.9})
    p.inputs["Base Color"].default_value = rgb(tint)
    lw = node(nt, "ShaderNodeLayerWeight", Blend=0.25)
    milk = node(nt, "ShaderNodeEmission", Color=rgb((0.92, 0.95, 1.0)))
    link(nt, math(nt, "ADD", body, math(nt, "MULTIPLY", math(nt, "POWER", lw.outputs["Facing"], 2.5), rim_strength)),
         milk.inputs["Strength"])
    a = node(nt, "ShaderNodeAddShader")
    link(nt, p.outputs[0], a.inputs[0])
    link(nt, milk.outputs[0], a.inputs[1])
    vis = bl.value_node(nt, "vis", 1.0)
    tr = node(nt, "ShaderNodeBsdfTransparent")
    mx = nt.nodes.new("ShaderNodeMixShader")
    link(nt, vis.outputs[0], mx.inputs[0])
    link(nt, tr.outputs[0], mx.inputs[1])
    link(nt, fog_wrap(nt, a.outputs[0], fog, density=fog_density, strength=0.6), mx.inputs[2])
    link(nt, mx.outputs[0], out.inputs[0])
    return m


def bubble_fast(name="BubbleFast", fog=(0.20, 0.02, 0.025), fog_density=0.0, body=0.10, rim_strength=1.0,
                gloss=0.85):
    """Microburbuja económica: transparente + reflexión especular con tinte iridiscente según el ángulo
    (imita la interferencia de película fina sin refracción) + borde lechoso emisivo."""
    m, nt, out = bl.new_mat(name)
    lw = node(nt, "ShaderNodeLayerWeight", Blend=0.3)
    ramp = node(nt, "ShaderNodeValToRGB")
    cr = ramp.color_ramp
    cr.elements[0].position = 0.0
    cr.elements[0].color = (0.92, 0.96, 1.0, 1)
    cr.elements[1].position = 1.0
    cr.elements[1].color = (0.75, 0.95, 1.0, 1)
    e = cr.elements.new(0.55)
    e.color = (1.0, 0.85, 0.95, 1)
    e = cr.elements.new(0.78)
    e.color = (0.80, 1.0, 0.92, 1)
    link(nt, lw.outputs["Facing"], ramp.inputs[0])
    gl = node(nt, "ShaderNodeBsdfGlossy", Roughness=0.035)
    link(nt, ramp.outputs[0], gl.inputs["Color"])
    tr = node(nt, "ShaderNodeBsdfTransparent")
    fac = math(nt, "ADD", 0.12, math(nt, "MULTIPLY", math(nt, "POWER", lw.outputs["Fresnel"], 0.8), gloss))
    mx = nt.nodes.new("ShaderNodeMixShader")
    link(nt, math(nt, "MINIMUM", fac, 1.0), mx.inputs[0])
    link(nt, tr.outputs[0], mx.inputs[1])
    link(nt, gl.outputs[0], mx.inputs[2])
    milk = node(nt, "ShaderNodeEmission", Color=rgb((0.93, 0.96, 1.0)))
    link(nt, math(nt, "ADD", body, math(nt, "MULTIPLY", math(nt, "POWER", lw.outputs["Facing"], 2.5), rim_strength)),
         milk.inputs["Strength"])
    a = node(nt, "ShaderNodeAddShader")
    link(nt, mx.outputs[0], a.inputs[0])
    link(nt, milk.outputs[0], a.inputs[1])
    vis = bl.value_node(nt, "vis", 1.0)
    tr2 = node(nt, "ShaderNodeBsdfTransparent")
    mx2 = nt.nodes.new("ShaderNodeMixShader")
    link(nt, vis.outputs[0], mx2.inputs[0])
    link(nt, tr2.outputs[0], mx2.inputs[1])
    link(nt, fog_wrap(nt, a.outputs[0], fog, density=fog_density, strength=0.6), mx2.inputs[2])
    link(nt, mx2.outputs[0], out.inputs[0])
    return m
