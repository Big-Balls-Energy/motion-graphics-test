"""Utilidades de Blender (bpy) para construir y renderizar los planos."""
import math
import os
import time

import bpy
import numpy as np
from mathutils import Euler, Matrix, Vector

FPS = 30


# ----------------------------------------------------------------------------- scene / render


def reset():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = FPS
    return sc


def setup_render(sc, res=(1080, 1920), spp=8, threshold=0.06, bounces=(3, 1, 2, 4, 10), motion_blur=True,
                 shutter=0.5, exposure=0.0, look="AgX - Medium High Contrast", film_transparent=False,
                 clamp_indirect=3.0, filter_width=1.5):
    sc.render.engine = "CYCLES"
    cy = sc.cycles
    cy.device = "CPU"
    cy.samples = spp
    cy.use_adaptive_sampling = True
    cy.adaptive_threshold = threshold
    cy.adaptive_min_samples = 0
    cy.use_denoising = True
    cy.denoiser = "OPENIMAGEDENOISE"
    cy.denoising_input_passes = "RGB_ALBEDO_NORMAL"
    cy.denoising_prefilter = "ACCURATE"
    mx, dif, glo, tra, trp = bounces
    cy.max_bounces = mx
    cy.diffuse_bounces = dif
    cy.glossy_bounces = glo
    cy.transmission_bounces = tra
    cy.transparent_max_bounces = trp
    cy.volume_bounces = 0
    cy.sample_clamp_indirect = clamp_indirect
    cy.caustics_reflective = False
    cy.caustics_refractive = False
    cy.blur_glossy = 1.0
    cy.filter_width = filter_width
    cy.seed = 0
    cy.use_animated_seed = True
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 100
    sc.render.use_motion_blur = motion_blur
    sc.render.motion_blur_shutter = shutter
    sc.render.film_transparent = film_transparent
    sc.render.use_persistent_data = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_depth = "16"
    sc.render.image_settings.compression = 15
    sc.view_settings.view_transform = "AgX"
    try:
        sc.view_settings.look = look
    except TypeError:
        pass
    sc.view_settings.exposure = exposure
    sc.render.threads_mode = "AUTO"


def world(sc, top=(0.004, 0.012, 0.03), bottom=(0.0, 0.002, 0.006), strength=1.0):
    w = bpy.data.worlds.new("World")
    sc.world = w
    w.use_nodes = True
    nt = w.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (*bottom, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (*top, 1)
    nt.links.new(tc.outputs["Generated"], sep.inputs[0])
    nt.links.new(sep.outputs["Z"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], bg.inputs[0])
    bg.inputs[1].default_value = strength
    nt.links.new(bg.outputs[0], out.inputs[0])
    # el fondo no ilumina la escena (control total con luces)
    lp = nt.nodes.new("ShaderNodeLightPath")
    mix = nt.nodes.new("ShaderNodeMixShader")
    black = nt.nodes.new("ShaderNodeBackground")
    black.inputs[0].default_value = (0, 0, 0, 1)
    nt.links.new(lp.outputs["Is Camera Ray"], mix.inputs[0])
    nt.links.new(black.outputs[0], mix.inputs[1])
    nt.links.new(bg.outputs[0], mix.inputs[2])
    nt.links.new(mix.outputs[0], out.inputs[0])
    return w


def link(obj, sc=None):
    (sc or bpy.context.scene).collection.objects.link(obj)
    return obj


def camera(sc, name="Cam", lens=50.0, sensor=36.0, clip=(0.001, 100.0), dof=None):
    cd = bpy.data.cameras.new(name)
    cd.lens = lens
    cd.sensor_fit = "VERTICAL"
    cd.sensor_height = sensor
    cd.clip_start, cd.clip_end = clip
    cam = bpy.data.objects.new(name, cd)
    link(cam, sc)
    sc.camera = cam
    if dof:
        cd.dof.use_dof = True
        cd.dof.focus_distance = dof[0]
        cd.dof.aperture_fstop = dof[1]
        cd.dof.aperture_blades = 0
    return cam


def look_at(obj, target, roll=0.0):
    loc = Vector(obj.location)
    d = Vector(target) - loc
    rot = d.to_track_quat("-Z", "Y").to_euler()
    obj.rotation_euler = rot
    if roll:
        obj.rotation_euler.rotate_axis("Z", roll)


def area_light(sc, name, loc, target, energy, size=0.5, color=(1, 1, 1), shape="DISK", size_y=None,
               spread=180.0, visible=False):
    ld = bpy.data.lights.new(name, "AREA")
    ld.energy = energy
    ld.color = color
    ld.shape = shape
    ld.size = size
    if size_y is not None:
        ld.size_y = size_y
    ld.spread = math.radians(spread)
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    look_at(o, target)
    o.visible_camera = visible
    link(o, sc)
    return o


def point_light(sc, name, loc, energy, radius=0.05, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "POINT")
    ld.energy = energy
    ld.color = color
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    link(o, sc)
    return o


def spot_light(sc, name, loc, target, energy, angle=40, blend=0.6, radius=0.05, color=(1, 1, 1)):
    ld = bpy.data.lights.new(name, "SPOT")
    ld.energy = energy
    ld.color = color
    ld.spot_size = math.radians(angle)
    ld.spot_blend = blend
    ld.shadow_soft_size = radius
    o = bpy.data.objects.new(name, ld)
    o.location = loc
    look_at(o, target)
    link(o, sc)
    return o


# ----------------------------------------------------------------------------- geometry


def mesh_object(name, verts, faces, sc=None, smooth=True, mat=None):
    me = bpy.data.meshes.new(name)
    verts = np.asarray(verts, np.float32)
    faces = list(faces) if not isinstance(faces, np.ndarray) else faces
    if isinstance(faces, np.ndarray) and faces.ndim == 2:
        n = faces.shape[1]
        me.vertices.add(len(verts))
        me.vertices.foreach_set("co", verts.ravel())
        me.loops.add(faces.size)
        me.loops.foreach_set("vertex_index", faces.astype(np.int32).ravel())
        me.polygons.add(len(faces))
        me.polygons.foreach_set("loop_start", np.arange(0, faces.size, n, dtype=np.int32))
        me.update(calc_edges=True)
    else:
        me.from_pydata(verts.tolist(), [], [list(f) for f in faces])
        me.update()
    if smooth:
        me.shade_smooth()
    o = bpy.data.objects.new(name, me)
    link(o, sc)
    if mat is not None:
        me.materials.append(mat)
    return o


def points_object(name, positions, radius, sc=None, mat=None, attrs=None):
    """Malla de vértices sueltos + GN 'Mesh to Points' => Cycles los renderiza como esferas."""
    me = bpy.data.meshes.new(name)
    positions = np.asarray(positions, np.float32)
    me.vertices.add(len(positions))
    me.vertices.foreach_set("co", positions.ravel())
    a = me.attributes.new("radius", "FLOAT", "POINT")
    a.data.foreach_set("value", np.asarray(radius, np.float32))
    for k, (typ, val) in (attrs or {}).items():
        at = me.attributes.new(k, typ, "POINT")
        key = "value" if typ == "FLOAT" else "vector" if typ == "FLOAT_VECTOR" else "color"
        at.data.foreach_set(key, np.asarray(val, np.float32).ravel())
    me.update()
    o = bpy.data.objects.new(name, me)
    link(o, sc)
    ng = bpy.data.node_groups.new(name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    m2p = ng.nodes.new("GeometryNodeMeshToPoints")
    na = ng.nodes.new("GeometryNodeInputNamedAttribute")
    na.data_type = "FLOAT"
    na.inputs["Name"].default_value = "radius"
    sm = ng.nodes.new("GeometryNodeSetMaterial")
    ng.links.new(gi.outputs[0], m2p.inputs["Mesh"])
    ng.links.new(na.outputs["Attribute"], m2p.inputs["Radius"])
    ng.links.new(m2p.outputs[0], sm.inputs["Geometry"])
    ng.links.new(sm.outputs[0], go.inputs[0])
    if mat is not None:
        sm.inputs["Material"].default_value = mat
    mod = o.modifiers.new("GN", "NODES")
    mod.node_group = ng
    return o


def instances_object(name, positions, inst_obj, scale, rot_euler, sc=None, attrs=None):
    """Vértices + GN 'Instance on Points' con escala (float) y rotación (euler) por punto."""
    me = bpy.data.meshes.new(name)
    positions = np.asarray(positions, np.float32)
    me.vertices.add(len(positions))
    me.vertices.foreach_set("co", positions.ravel())
    a = me.attributes.new("scale", "FLOAT", "POINT")
    a.data.foreach_set("value", np.asarray(scale, np.float32))
    r = me.attributes.new("rot", "FLOAT_VECTOR", "POINT")
    r.data.foreach_set("vector", np.asarray(rot_euler, np.float32).ravel())
    for k, (typ, val) in (attrs or {}).items():
        at = me.attributes.new(k, typ, "POINT")
        key = "value" if typ == "FLOAT" else "vector"
        at.data.foreach_set(key, np.asarray(val, np.float32).ravel())
    me.update()
    o = bpy.data.objects.new(name, me)
    link(o, sc)
    ng = bpy.data.node_groups.new(name + "_GN", "GeometryNodeTree")
    ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
    ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
    gi = ng.nodes.new("NodeGroupInput")
    go = ng.nodes.new("NodeGroupOutput")
    iop = ng.nodes.new("GeometryNodeInstanceOnPoints")
    oi = ng.nodes.new("GeometryNodeObjectInfo")
    oi.inputs["Object"].default_value = inst_obj
    oi.inputs["As Instance"].default_value = True
    ns = ng.nodes.new("GeometryNodeInputNamedAttribute")
    ns.data_type = "FLOAT"
    ns.inputs["Name"].default_value = "scale"
    nr = ng.nodes.new("GeometryNodeInputNamedAttribute")
    nr.data_type = "FLOAT_VECTOR"
    nr.inputs["Name"].default_value = "rot"
    e2r = ng.nodes.new("FunctionNodeEulerToRotation")
    ng.links.new(gi.outputs[0], iop.inputs["Points"])
    ng.links.new(oi.outputs["Geometry"], iop.inputs["Instance"])
    ng.links.new(ns.outputs["Attribute"], iop.inputs["Scale"])
    ng.links.new(nr.outputs["Attribute"], e2r.inputs[0])
    ng.links.new(e2r.outputs[0], iop.inputs["Rotation"])
    ng.links.new(iop.outputs[0], go.inputs[0])
    mod = o.modifiers.new("GN", "NODES")
    mod.node_group = ng
    inst_obj.hide_render = True
    return o


def update_points(o, positions, radius=None, scale=None, rot=None, attrs=None):
    me = o.data
    positions = np.asarray(positions, np.float32)
    if len(me.vertices) != len(positions):
        raise ValueError("cambiar el número de puntos no está soportado")
    me.vertices.foreach_set("co", positions.ravel())
    if radius is not None:
        me.attributes["radius"].data.foreach_set("value", np.asarray(radius, np.float32))
    if scale is not None:
        me.attributes["scale"].data.foreach_set("value", np.asarray(scale, np.float32))
    if rot is not None:
        me.attributes["rot"].data.foreach_set("vector", np.asarray(rot, np.float32).ravel())
    for k, val in (attrs or {}).items():
        at = me.attributes[k]
        key = "value" if at.data_type == "FLOAT" else "vector" if at.data_type == "FLOAT_VECTOR" else "color"
        at.data.foreach_set(key, np.asarray(val, np.float32).ravel())
    me.update()


def tube_object(name, pts, radii, sc=None, mat=None, bevel_res=6, attrs=None):
    """Curva POLY con radio por punto y bisel circular (vena)."""
    cd = bpy.data.curves.new(name, "CURVE")
    cd.dimensions = "3D"
    cd.bevel_depth = 1.0
    cd.bevel_resolution = bevel_res
    cd.use_fill_caps = True
    sp = cd.splines.new("POLY")
    pts = np.asarray(pts, float)
    sp.points.add(len(pts) - 1)
    co = np.hstack([pts, np.ones((len(pts), 1))]).astype(np.float32)
    sp.points.foreach_set("co", co.ravel())
    sp.points.foreach_set("radius", np.asarray(radii, np.float32))
    o = bpy.data.objects.new(name, cd)
    link(o, sc)
    if mat is not None:
        cd.materials.append(mat)
    return o


def tube_mesh(name, pts, radii, n_ring=12, sc=None, mat=None, cap=True, v_attr=True, u_mode="norm"):
    """Tubo como malla (permite atributo 'u' a lo largo de la vena para animar sombreado)."""
    pts = np.asarray(pts, float)
    radii = np.asarray(radii, float)
    n = len(pts)
    t = np.gradient(pts, axis=0)
    t /= np.linalg.norm(t, axis=1, keepdims=True) + 1e-12
    # marco con transporte paralelo
    ref = np.array([0.0, 0.0, 1.0]) if abs(t[0][2]) < 0.9 else np.array([1.0, 0.0, 0.0])
    nrm = np.cross(t[0], ref)
    nrm /= np.linalg.norm(nrm)
    normals = [nrm]
    for i in range(1, n):
        v = np.cross(normals[-1], t[i])
        b = np.cross(t[i], v)
        normals.append(b / (np.linalg.norm(b) + 1e-12))
    normals = np.array(normals)
    binormals = np.cross(t, normals)
    ang = np.linspace(0, 2 * np.pi, n_ring, endpoint=False)
    ca, sa = np.cos(ang), np.sin(ang)
    verts = (pts[:, None, :] + radii[:, None, None] * (ca[None, :, None] * normals[:, None, :]
                                                      + sa[None, :, None] * binormals[:, None, :])).reshape(-1, 3)
    faces = []
    for i in range(n - 1):
        for j in range(n_ring):
            a0 = i * n_ring + j
            a1 = i * n_ring + (j + 1) % n_ring
            faces.append((a0, a1, a1 + n_ring, a0 + n_ring))
    faces = np.array(faces, np.int32)
    if u_mode == "length":
        arc = np.concatenate([[0.0], np.cumsum(np.linalg.norm(np.diff(pts, axis=0), axis=1))])
        u = np.repeat(arc, n_ring)
    else:
        arc = np.linspace(0, 1, n)
        u = np.repeat(arc, n_ring)
    extra_v = []
    if cap:
        c0 = len(verts)
        verts = np.vstack([verts, pts[0], pts[-1]])
        u = np.concatenate([u, [arc[0], arc[-1]]])
        caps = []
        for j in range(n_ring):
            caps.append((c0, (j + 1) % n_ring, j, j))
            last = (n - 1) * n_ring
            caps.append((c0 + 1, last + j, last + (j + 1) % n_ring, last + (j + 1) % n_ring))
        # triángulos degenerados como quads -> usar from_pydata para mezcla
        me_faces = [tuple(f) for f in faces] + [(c, a, b) for c, a, b, _ in caps]
        o = mesh_object(name, verts, me_faces, sc=sc, mat=mat)
    else:
        o = mesh_object(name, verts, faces, sc=sc, mat=mat)
    if v_attr:
        at = o.data.attributes.new("u", "FLOAT", "POINT")
        at.data.foreach_set("value", u.astype(np.float32))
    return o


# ----------------------------------------------------------------------------- materials


def new_mat(name):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    return m, nt, out


def principled(name, base=(0.8, 0.8, 0.8), rough=0.4, metallic=0.0, spec=0.5, coat=0.0, coat_rough=0.1,
               sheen=0.0, sheen_tint=(1, 1, 1), emission=None, emission_strength=0.0, alpha=1.0,
               transmission=0.0, ior=1.45, subsurface=0.0, sss_radius=(1.0, 0.2, 0.1), sss_scale=0.01,
               thin_film=0.0, thin_film_ior=1.33):
    m, nt, out = new_mat(name)
    b = nt.nodes.new("ShaderNodeBsdfPrincipled")
    b.inputs["Base Color"].default_value = (*base, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metallic
    b.inputs["Specular IOR Level"].default_value = spec
    b.inputs["Coat Weight"].default_value = coat
    b.inputs["Coat Roughness"].default_value = coat_rough
    b.inputs["Sheen Weight"].default_value = sheen
    b.inputs["Sheen Tint"].default_value = (*sheen_tint, 1)
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Transmission Weight"].default_value = transmission
    b.inputs["IOR"].default_value = ior
    b.inputs["Subsurface Weight"].default_value = subsurface
    b.inputs["Subsurface Radius"].default_value = sss_radius
    b.inputs["Subsurface Scale"].default_value = sss_scale
    if thin_film:
        b.inputs["Thin Film Thickness"].default_value = thin_film
        b.inputs["Thin Film IOR"].default_value = thin_film_ior
    if emission is not None:
        b.inputs["Emission Color"].default_value = (*emission, 1)
        b.inputs["Emission Strength"].default_value = emission_strength
    nt.links.new(b.outputs[0], out.inputs[0])
    return m


def emission_mat(name, color, strength=1.0):
    m, nt, out = new_mat(name)
    e = nt.nodes.new("ShaderNodeEmission")
    e.inputs[0].default_value = (*color, 1)
    e.inputs[1].default_value = strength
    nt.links.new(e.outputs[0], out.inputs[0])
    return m


def value_node(nt, name, value):
    v = nt.nodes.new("ShaderNodeValue")
    v.name = name
    v.label = name
    v.outputs[0].default_value = value
    return v


def set_value(mat, name, value):
    mat.node_tree.nodes[name].outputs[0].default_value = value


# ----------------------------------------------------------------------------- animation helpers


def smoothstep(a, b, x):
    t = np.clip((x - a) / (b - a), 0.0, 1.0)
    return t * t * (3 - 2 * t)


def ease_in_out(t):
    t = np.clip(t, 0, 1)
    return t * t * (3 - 2 * t)


def ease_out(t):
    t = np.clip(t, 0, 1)
    return 1 - (1 - t) ** 3


def lerp(a, b, t):
    return a + (b - a) * t


def keyframe_path(t, keys):
    """keys: lista de (tiempo, valor/array). Interpolación suave (smoothstep por tramo)."""
    times = [k[0] for k in keys]
    if t <= times[0]:
        return np.asarray(keys[0][1], float)
    if t >= times[-1]:
        return np.asarray(keys[-1][1], float)
    for (t0, v0), (t1, v1) in zip(keys[:-1], keys[1:]):
        if t0 <= t <= t1:
            u = ease_in_out((t - t0) / (t1 - t0))
            return np.asarray(v0, float) + (np.asarray(v1, float) - np.asarray(v0, float)) * u


def hermite_path(t, keys):
    """Trayectoria C1 (Catmull-Rom con tiempos no uniformes). keys: [(t, vec), ...]."""
    ts = np.array([k[0] for k in keys], float)
    P = np.array([np.asarray(k[1], float) for k in keys])
    if t <= ts[0]:
        return P[0]
    if t >= ts[-1]:
        return P[-1]
    i = int(np.searchsorted(ts, t) - 1)
    n = len(ts)

    def tangent(j):
        if j == 0 or j == n - 1:
            return np.zeros_like(P[0])
        return (P[j + 1] - P[j - 1]) / (ts[j + 1] - ts[j - 1])

    h = ts[i + 1] - ts[i]
    u = (t - ts[i]) / h
    h00 = 2 * u ** 3 - 3 * u ** 2 + 1
    h10 = u ** 3 - 2 * u ** 2 + u
    h01 = -2 * u ** 3 + 3 * u ** 2
    h11 = u ** 3 - u ** 2
    return h00 * P[i] + h10 * h * tangent(i) + h01 * P[i + 1] + h11 * h * tangent(i + 1)


def set_camera(cam, loc, target, focus=None, roll=0.0):
    cam.location = Vector(loc)
    look_at(cam, target, roll)
    if focus is not None:
        cam.data.dof.focus_distance = float(focus)


def register_update(sc, fn):
    """fn(t_seconds) se llama en cada (sub)frame, también para el motion blur."""
    def handler(scene, depsgraph=None):
        t = (scene.frame_current + scene.frame_subframe) / FPS
        fn(t)
    bpy.app.handlers.frame_change_pre.clear()
    bpy.app.handlers.frame_change_pre.append(handler)


def render_frames(sc, out_dir, frames, prefix="f", skip_existing=True, log=None):
    os.makedirs(out_dir, exist_ok=True)
    total = 0.0
    done = 0
    for fr in frames:
        path = os.path.join(out_dir, f"{prefix}{fr:04d}.png")
        if skip_existing and os.path.exists(path):
            continue
        t0 = time.time()
        sc.frame_set(fr)
        sc.render.filepath = path
        bpy.ops.render.render(write_still=True)
        dt = time.time() - t0
        total += dt
        done += 1
        msg = f"frame {fr} {dt:.1f}s (avg {total / done:.1f}s)"
        print(msg, flush=True)
        if log:
            with open(log, "a") as f:
                f.write(msg + "\n")
