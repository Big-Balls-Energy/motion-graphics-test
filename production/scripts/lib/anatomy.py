"""Anatomía procedural (numpy puro, sin bpy).

Sistema de coordenadas (metros): pierna DERECHA de pie, z hacia arriba, +y = anterior,
+x = lateral, -x = medial (hacia la línea media del cuerpo).

Contenido:
  - SDF de la pierna (tronco elíptico + rasgos: pantorrilla, rodilla, maléolos, Aquiles, pie).
  - Mallas por marching cubes: piel (con y sin abultamiento varicoso), capa muscular, huesos.
  - Red venosa: safena mayor (GSV), safena menor (SSV), tributaria varicosa en pantorrilla medial,
    venas profundas (femoral, poplítea, tibiales posteriores, peroneas, tibiales anteriores),
    perforantes. Cada vena es una polilínea con radio por punto.
  - Malla de eritrocito bicóncavo (modelo de Evans-Fung).
"""
import numpy as np

# ----------------------------------------------------------------------------- SDF primitives


def smin(a, b, k):
    h = np.clip(0.5 + 0.5 * (b - a) / k, 0.0, 1.0)
    return b * (1 - h) + a * h - k * h * (1 - h)


def smax(a, b, k):
    return -smin(-a, -b, k)


def sd_ellipsoid(p, c, r):
    c = np.asarray(c, float)
    r = np.asarray(r, float)
    q = (p - c) / r
    k0 = np.linalg.norm(q, axis=-1)
    k1 = np.linalg.norm((p - c) / (r * r), axis=-1)
    return k0 * (k0 - 1.0) / np.maximum(k1, 1e-9)


def sd_capsule(p, a, b, ra, rb=None):
    a = np.asarray(a, float)
    b = np.asarray(b, float)
    rb = ra if rb is None else rb
    pa = p - a
    ba = b - a
    h = np.clip((pa @ ba) / (ba @ ba), 0.0, 1.0)
    d = np.linalg.norm(pa - h[..., None] * ba, axis=-1)
    return d - (ra + (rb - ra) * h)


def sd_polyline_tube(p, pts, radii):
    """SDF de un tubo a lo largo de una polilínea (unión de cápsulas cónicas)."""
    d = np.full(p.shape[:-1], 1e9)
    for i in range(len(pts) - 1):
        d = np.minimum(d, sd_capsule(p, pts[i], pts[i + 1], radii[i], radii[i + 1]))
    return d


# ----------------------------------------------------------------------------- leg profile

# z, semieje medio-lateral a, semieje antero-posterior b, centro cx, cy
_PROFILE = np.array([
    [0.060, 0.030, 0.035, 0.002, -0.004],
    [0.100, 0.028, 0.034, 0.000, -0.006],
    [0.160, 0.032, 0.039, 0.000, -0.010],
    [0.240, 0.040, 0.049, -0.001, -0.014],
    [0.300, 0.048, 0.057, -0.002, -0.016],
    [0.350, 0.053, 0.060, -0.003, -0.016],
    [0.400, 0.051, 0.056, -0.002, -0.012],
    [0.450, 0.050, 0.051, 0.000, -0.006],
    [0.500, 0.055, 0.054, 0.000, 0.000],
    [0.560, 0.058, 0.057, 0.001, 0.002],
    [0.650, 0.066, 0.066, 0.003, 0.003],
    [0.750, 0.076, 0.075, 0.006, 0.004],
    [0.850, 0.084, 0.083, 0.009, 0.004],
    [0.980, 0.090, 0.089, 0.012, 0.004],
])


def profile(z):
    z = np.asarray(z, float)
    zs = _PROFILE[:, 0]
    out = [np.interp(z, zs, _PROFILE[:, i]) for i in range(1, 5)]
    return out  # a, b, cx, cy


def sd_trunk(p):
    x, y, z = p[..., 0], p[..., 1], p[..., 2]
    a, b, cx, cy = profile(z)
    xp, yp = x - cx, y - cy
    # perfil anterior de la tibia algo más "afilado": reduce b en la cara anterior de la pierna
    shin = np.clip((0.44 - z) / 0.1, 0, 1) * np.clip((z - 0.12) / 0.06, 0, 1)
    b_eff = np.where(yp > 0, b * (1 - 0.06 * shin), b)
    rho = np.sqrt((xp / a) ** 2 + (yp / b_eff) ** 2)
    grad = np.sqrt((xp / a ** 2) ** 2 + (yp / b_eff ** 2) ** 2) / np.maximum(rho, 1e-9)
    d = (rho - 1.0) / np.maximum(grad, 1e-9)
    return smax(d, 0.055 - z, 0.01)


def sd_leg(p, bulge=None):
    """SDF de la piel. `bulge`: (pts, radii) de una vena varicosa que abomba la piel."""
    d = sd_trunk(p)
    # pantorrilla: cabezas del gastrocnemio (medial más baja y voluminosa)
    d = smin(d, sd_ellipsoid(p, (-0.020, -0.034, 0.345), (0.030, 0.034, 0.085)), 0.025)
    d = smin(d, sd_ellipsoid(p, (0.018, -0.032, 0.370), (0.026, 0.030, 0.075)), 0.025)
    # muslo: vasto medial (lágrima sobre la rodilla), vasto lateral y aductores
    d = smin(d, sd_ellipsoid(p, (-0.036, 0.018, 0.590), (0.034, 0.038, 0.075)), 0.03)
    d = smin(d, sd_ellipsoid(p, (0.040, 0.008, 0.680), (0.036, 0.046, 0.150)), 0.04)
    d = smin(d, sd_ellipsoid(p, (-0.040, -0.012, 0.790), (0.044, 0.056, 0.170)), 0.04)
    # rodilla: rótula y cóndilos
    d = smin(d, sd_ellipsoid(p, (0.000, 0.040, 0.505), (0.024, 0.016, 0.028)), 0.018)
    d = smin(d, sd_ellipsoid(p, (-0.030, 0.006, 0.488), (0.026, 0.040, 0.030)), 0.02)
    d = smin(d, sd_ellipsoid(p, (0.028, 0.004, 0.490), (0.024, 0.038, 0.028)), 0.02)
    # tobillo: maléolos y tendón de Aquiles
    d = smin(d, sd_ellipsoid(p, (-0.026, 0.006, 0.078), (0.012, 0.014, 0.016)), 0.012)
    d = smin(d, sd_ellipsoid(p, (0.028, -0.006, 0.064), (0.012, 0.013, 0.016)), 0.012)
    d = smin(d, sd_capsule(p, (0.0, -0.040, 0.045), (0.0, -0.036, 0.200), 0.009, 0.007), 0.012)
    # pie
    foot = sd_ellipsoid(p, (0.003, -0.030, 0.036), (0.030, 0.036, 0.036))          # talón
    foot = smin(foot, sd_ellipsoid(p, (-0.002, 0.040, 0.036), (0.036, 0.066, 0.032)), 0.02)  # mediopié
    foot = smin(foot, sd_ellipsoid(p, (0.004, 0.112, 0.022), (0.044, 0.042, 0.022)), 0.02)  # antepié
    toes = sd_capsule(p, (-0.025, 0.135, 0.020), (-0.027, 0.190, 0.016), 0.0125, 0.0105)
    for x0, y1, r in [(-0.004, 0.183, 0.0085), (0.010, 0.176, 0.0080), (0.022, 0.166, 0.0075), (0.033, 0.152, 0.0068)]:
        toes = smin(toes, sd_capsule(p, (x0 * 0.9, 0.130, 0.019), (x0, y1, 0.014), r + 0.001, r), 0.004)
    foot = smin(foot, toes, 0.012)
    d = smin(d, foot, 0.03)
    d = smax(d, -p[..., 2] + 0.001, 0.004)  # planta plana
    if bulge is not None:
        pts, radii = bulge
        d = smin(d, sd_polyline_tube(p, pts, np.asarray(radii) * 0.85 + 0.0005), 0.006)
    return d


def sd_bones(p):
    # tibia: meseta, diáfisis (con cresta anterior) y maléolo medial
    d = sd_ellipsoid(p, (-0.004, 0.006, 0.452), (0.036, 0.027, 0.020))
    d = smin(d, sd_capsule(p, (-0.006, 0.010, 0.430), (-0.008, 0.012, 0.095), 0.016, 0.012), 0.02)
    d = smin(d, sd_ellipsoid(p, (-0.017, 0.008, 0.078), (0.010, 0.012, 0.022)), 0.008)
    # peroné
    d = smin(d, sd_capsule(p, (0.026, -0.010, 0.420), (0.025, -0.004, 0.075), 0.0065, 0.0055), 0.006)
    d = smin(d, sd_ellipsoid(p, (0.027, -0.010, 0.425), (0.010, 0.010, 0.012)), 0.006)
    d = smin(d, sd_ellipsoid(p, (0.026, -0.004, 0.062), (0.007, 0.010, 0.017)), 0.006)
    # fémur: diáfisis y cóndilos
    d = smin(d, sd_capsule(p, (0.010, 0.000, 0.960), (0.002, 0.000, 0.540), 0.014, 0.016), 0.02)
    d = smin(d, sd_ellipsoid(p, (-0.020, -0.004, 0.492), (0.020, 0.030, 0.024)), 0.015)
    d = smin(d, sd_ellipsoid(p, (0.020, -0.004, 0.494), (0.019, 0.029, 0.023)), 0.015)
    # rótula
    d = smin(d, sd_ellipsoid(p, (0.000, 0.030, 0.505), (0.019, 0.009, 0.023)), 0.004)
    # pie: astrágalo, calcáneo, metatarsianos y falanges
    d = smin(d, sd_ellipsoid(p, (0.000, 0.004, 0.058), (0.016, 0.022, 0.014)), 0.006)
    d = smin(d, sd_ellipsoid(p, (0.004, -0.024, 0.030), (0.015, 0.030, 0.018)), 0.008)
    d = smin(d, sd_ellipsoid(p, (-0.004, 0.034, 0.042), (0.022, 0.018, 0.012)), 0.008)
    for i, (x0, x1, y1, r) in enumerate([(-0.018, -0.024, 0.122, 0.0055), (-0.008, -0.006, 0.124, 0.0042),
                                         (0.000, 0.007, 0.119, 0.0040), (0.008, 0.018, 0.112, 0.0038),
                                         (0.016, 0.029, 0.100, 0.0040)]):
        mt = sd_capsule(p, (x0, 0.048, 0.036), (x1, y1, 0.016), r)
        ph = sd_capsule(p, (x1, y1 + 0.004, 0.015), (x1 * 1.05, y1 + 0.045 - i * 0.004, 0.012), r * 0.8, r * 0.6)
        d = smin(d, smin(mt, ph, 0.003), 0.004)
    return d


# ----------------------------------------------------------------------------- meshing


def mesh_sdf(fn, bounds, voxel=0.002, level=0.0, chunk=48):
    """Evalúa la SDF por bloques en z y extrae la isosuperficie con marching cubes."""
    from skimage.measure import marching_cubes
    (x0, x1), (y0, y1), (z0, z1) = bounds
    xs = np.arange(x0, x1 + voxel, voxel)
    ys = np.arange(y0, y1 + voxel, voxel)
    zs = np.arange(z0, z1 + voxel, voxel)
    vol = np.empty((len(xs), len(ys), len(zs)), np.float32)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    for k0 in range(0, len(zs), chunk):
        zz = zs[k0:k0 + chunk]
        P = np.stack(np.broadcast_arrays(X[..., None], Y[..., None], zz[None, None, :]), -1)
        vol[:, :, k0:k0 + chunk] = fn(P)
    v, f, n, _ = marching_cubes(vol, level=level, spacing=(voxel, voxel, voxel))
    v += np.array([x0, y0, z0])
    return v.astype(np.float64), f.astype(np.int32)


def taubin_smooth(v, f, iters=10, lam=0.5, mu=-0.53):
    import scipy.sparse as sp
    n = len(v)
    e = np.concatenate([f[:, [0, 1]], f[:, [1, 2]], f[:, [2, 0]]])
    e = np.concatenate([e, e[:, ::-1]])
    A = sp.coo_matrix((np.ones(len(e)), (e[:, 0], e[:, 1])), shape=(n, n)).tocsr()
    A.data[:] = 1.0
    deg = np.asarray(A.sum(1)).ravel()
    deg[deg == 0] = 1
    W = sp.diags(1.0 / deg) @ A
    for _ in range(iters):
        v = v + lam * (W @ v - v)
        v = v + mu * (W @ v - v)
    return v


# ----------------------------------------------------------------------------- curves


def catmull_rom(ctrl, samples_per_seg=16):
    ctrl = np.asarray(ctrl, float)
    P = np.vstack([2 * ctrl[0] - ctrl[1], ctrl, 2 * ctrl[-1] - ctrl[-2]])
    out = []
    for i in range(1, len(P) - 2):
        p0, p1, p2, p3 = P[i - 1], P[i], P[i + 1], P[i + 2]
        t = np.linspace(0, 1, samples_per_seg, endpoint=False)[:, None]
        out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t ** 2
                          + (-p0 + 3 * p1 - 3 * p2 + p3) * t ** 3))
    out.append(ctrl[-1][None])
    return np.vstack(out)


def resample(pts, step):
    seg = np.linalg.norm(np.diff(pts, axis=0), axis=1)
    s = np.concatenate([[0], np.cumsum(seg)])
    n = max(int(s[-1] / step), 2)
    t = np.linspace(0, s[-1], n)
    return np.stack([np.interp(t, s, pts[:, i]) for i in range(pts.shape[1])], 1)


def surface_point(z, theta_deg, depth, sdf=sd_leg):
    """Punto a `depth` m bajo la piel, a la altura z y ángulo theta
    (0=anterior, 90=medial, 180=posterior, 270=lateral)."""
    th = np.radians(theta_deg)
    a, b, cx, cy = profile(z)
    d = np.array([-np.sin(th), np.cos(th), 0.0])
    c = np.array([cx, cy, z])
    lo, hi = 0.0, 0.16
    for _ in range(40):
        mid = 0.5 * (lo + hi)
        if sdf((c + d * mid)[None])[0] > 0:
            hi = mid
        else:
            lo = mid
    return c + d * (lo - depth)


def vein_on_surface(ctrl_ztheta, radii, depth=0.0035, step=0.0015, sdf=sd_leg):
    ctrl = np.array([[z, th] for z, th in ctrl_ztheta], float)
    dense = catmull_rom(ctrl, 24)
    pts = np.array([surface_point(z, th, depth + r_extra, sdf)
                    for (z, th), r_extra in zip(dense, np.interp(np.linspace(0, 1, len(dense)),
                                                                   np.linspace(0, 1, len(radii)), radii))])
    pts = resample(pts, step)
    r = np.interp(np.linspace(0, 1, len(pts)), np.linspace(0, 1, len(radii)), radii)
    return pts, r


def build_veins():
    """Devuelve dict nombre -> dict(pts, radius, kind). kind: 'superficial', 'varicose', 'deep', 'perforator'."""
    V = {}
    # Safena mayor: anterior al maléolo medial, cara medial de pierna, posterior al cóndilo femoral medial,
    # cara medial del muslo hacia la ingle.
    gsv_ctrl = [(0.085, 40), (0.12, 72), (0.18, 92), (0.26, 104), (0.34, 112), (0.42, 122), (0.48, 130),
                (0.54, 128), (0.62, 116), (0.72, 104), (0.82, 92), (0.93, 80)]
    pts, r = vein_on_surface(gsv_ctrl, [0.0026, 0.0028, 0.003, 0.0033, 0.0036, 0.0038, 0.0038, 0.0038, 0.0038,
                                        0.0039, 0.004, 0.0042], depth=0.0042)
    # tramo del pie (vena marginal medial) desde el dorso del pie
    foot = catmull_rom([(-0.006, 0.105, 0.040), (-0.024, 0.075, 0.046), (-0.034, 0.045, 0.058), pts[0]], 12)
    foot = resample(foot, 0.0015)
    V["gsv"] = dict(pts=np.vstack([foot[:-1], pts]), radius=np.concatenate([np.full(len(foot) - 1, 0.0022), r]),
                    kind="superficial")
    # Safena menor: detrás del maléolo lateral, línea media posterior de la pantorrilla, hasta la fosa poplítea
    ssv_ctrl = [(0.07, 238), (0.12, 212), (0.20, 196), (0.30, 186), (0.38, 182), (0.45, 180)]
    pts, r = vein_on_surface(ssv_ctrl, [0.0022, 0.0024, 0.0026, 0.0028, 0.003, 0.0032], depth=0.0045)
    # inmersión hacia la vena poplítea
    dive = catmull_rom([pts[-1], pts[-1] + np.array([0.0, 0.010, 0.012]), (0.004, -0.034, 0.485)], 10)
    V["ssv"] = dict(pts=np.vstack([pts, resample(dive, 0.0015)[1:]]),
                    radius=np.concatenate([r, np.full(len(resample(dive, 0.0015)) - 1, 0.0032)]),
                    kind="superficial")
    # Tributaria varicosa tortuosa en la cara medial-posterior de la pantorrilla (rama de la safena mayor)
    s = np.linspace(0, 1, 34)
    vz = 0.415 - 0.235 * s + 0.010 * np.sin(2 * np.pi * 4.2 * s + 0.6)
    vth = 124 + 30 * s + 11 * np.sin(2 * np.pi * 3.1 * s)
    rad = 0.0042 + 0.0016 * np.sin(2 * np.pi * 5.5 * s + 1.0) ** 2 + 0.0012 * np.exp(-((s - 0.55) / 0.12) ** 2)
    rad[:3] = np.linspace(0.0034, rad[3], 3)
    pts, r = vein_on_surface(list(zip(vz, vth)), rad, depth=0.0012)
    V["varicose"] = dict(pts=pts, radius=r, kind="varicose")
    # rama varicosa secundaria
    s2 = np.linspace(0, 1, 18)
    pts2, r2 = vein_on_surface(list(zip(0.33 - 0.12 * s2 + 0.006 * np.sin(6 * np.pi * s2),
                                        146 - 26 * s2 + 7 * np.sin(5 * np.pi * s2))),
                               0.0032 + 0.001 * np.sin(4 * np.pi * s2) ** 2, depth=0.0012)
    V["varicose_b"] = dict(pts=pts2, radius=r2, kind="varicose")
    # pequeñas venas reticulares alrededor
    rng = np.random.default_rng(7)
    for i in range(7):
        z0 = rng.uniform(0.17, 0.40)
        t0 = rng.uniform(112, 168)
        L = rng.uniform(0.03, 0.06)
        ss_ = np.linspace(0, 1, 9)
        ctrl = list(zip(z0 - L * ss_, t0 + rng.uniform(-18, 18) * ss_ + 4 * np.sin(rng.uniform(2, 5) * ss_)))
        p_, r_ = vein_on_surface(ctrl, np.linspace(0.0014, 0.0007, 9), depth=0.0008)
        V[f"reticular_{i}"] = dict(pts=p_, radius=r_, kind="reticular")
    # Venas profundas (acompañan a las arterias, cercanas a los huesos)
    fem = catmull_rom([(0.004, 0.012, 0.98), (-0.006, 0.006, 0.80), (-0.008, -0.006, 0.66),
                       (-0.002, -0.022, 0.56), (0.002, -0.030, 0.49), (0.002, -0.028, 0.42)], 16)
    V["femoral_popliteal"] = dict(pts=resample(fem, 0.0015), radius=np.interp(
        np.linspace(0, 1, len(resample(fem, 0.0015))), [0, 0.5, 1], [0.0062, 0.0055, 0.0048]), kind="deep")
    for nm, ctrl, r0 in [
        ("post_tibial_1", [(0.002, -0.028, 0.42), (-0.010, -0.022, 0.32), (-0.016, -0.014, 0.20), (-0.020, -0.008, 0.10), (-0.016, 0.010, 0.050)], 0.0028),
        ("post_tibial_2", [(0.004, -0.030, 0.42), (-0.006, -0.026, 0.32), (-0.012, -0.018, 0.20), (-0.016, -0.012, 0.10), (-0.012, 0.012, 0.050)], 0.0026),
        ("peroneal", [(0.004, -0.030, 0.40), (0.012, -0.024, 0.30), (0.018, -0.016, 0.18), (0.020, -0.012, 0.09)], 0.0026),
        ("ant_tibial", [(0.002, -0.026, 0.43), (0.010, 0.000, 0.40), (0.010, 0.016, 0.30), (0.006, 0.020, 0.18), (0.002, 0.024, 0.09)], 0.0022),
    ]:
        p_ = resample(catmull_rom(ctrl, 16), 0.0015)
        V[nm] = dict(pts=p_, radius=np.linspace(r0, r0 * 0.75, len(p_)), kind="deep")
    # Perforantes de la cara medial de la pierna (conectan safena/arco posterior con tibiales posteriores)
    for i, z in enumerate([0.15, 0.23, 0.31]):
        a_ = surface_point(z, 118, 0.004)
        b_ = np.array([-0.014 + 0.004 * i * 0 - 0.002, -0.016 + 0.002 * i, z + 0.01])
        p_ = resample(catmull_rom([a_, 0.6 * a_ + 0.4 * b_ + np.array([0, 0, 0.004]), b_], 10), 0.0012)
        V[f"perforator_{i}"] = dict(pts=p_, radius=np.linspace(0.0018, 0.0016, len(p_)), kind="perforator")
    return V


# ----------------------------------------------------------------------------- red blood cell


def rbc_mesh(R=1.0, n_r=18, n_a=40):
    """Eritrocito bicóncavo (Evans & Fung 1972). Devuelve verts, faces (quads/tris)."""
    C0, C1, C2 = 0.207, 2.003, -1.123
    rho = np.sin(np.linspace(0, np.pi / 2, n_r)) * 0.999
    h = np.sqrt(np.maximum(1 - rho ** 2, 0)) * (C0 + C1 * rho ** 2 + C2 * rho ** 4) * 0.5
    ang = np.linspace(0, 2 * np.pi, n_a, endpoint=False)
    verts = []
    # anillos superiores (de centro a borde) y luego inferiores (de borde a centro)
    rings = [(r, hh) for r, hh in zip(rho, h)] + [(r, -hh) for r, hh in zip(rho[::-1], h[::-1])]
    for r, hh in rings:
        for a in ang:
            verts.append((R * r * np.cos(a), R * r * np.sin(a), R * hh))
    verts = np.array(verts)
    faces = []
    nr = len(rings)
    for i in range(nr - 1):
        for j in range(n_a):
            a0 = i * n_a + j
            a1 = i * n_a + (j + 1) % n_a
            b0 = (i + 1) * n_a + j
            b1 = (i + 1) * n_a + (j + 1) % n_a
            faces.append((a0, b0, b1, a1))
    # tapas en los polos (centro superior e inferior)
    top = len(verts)
    bot = top + 1
    verts = np.vstack([verts, [(0, 0, R * h[0]), (0, 0, -R * h[0])]])
    for j in range(n_a):
        faces.append((top, j, (j + 1) % n_a))
        last = (nr - 1) * n_a
        faces.append((bot, last + (j + 1) % n_a, last + j))
    return verts, faces


LEG_BOUNDS = ((-0.105, 0.115), (-0.095, 0.215), (-0.004, 0.975))


def build_leg_assets(out_path, voxel=0.0022):
    """Construye y guarda en .npz: piel normal, piel con várices, capa muscular, huesos y venas."""
    veins = build_veins()
    bulge = (np.vstack([veins["varicose"]["pts"]]), veins["varicose"]["radius"])
    out = {}
    v, f = mesh_sdf(lambda P: sd_leg(P), LEG_BOUNDS, voxel)
    out["skin_v"], out["skin_f"] = taubin_smooth(v, f, 8), f
    v, f = mesh_sdf(lambda P: sd_leg(P, bulge), LEG_BOUNDS, voxel)
    out["skinvar_v"], out["skinvar_f"] = taubin_smooth(v, f, 8), f
    v, f = mesh_sdf(lambda P: sd_leg(P), LEG_BOUNDS, voxel * 1.4, level=-0.0075)
    out["muscle_v"], out["muscle_f"] = taubin_smooth(v, f, 10), f
    v, f = mesh_sdf(sd_bones, ((-0.06, 0.06), (-0.07, 0.20), (0.0, 0.975)), 0.0016)
    out["bone_v"], out["bone_f"] = taubin_smooth(v, f, 6), f
    for k, d in veins.items():
        out[f"vein__{k}__pts"] = d["pts"]
        out[f"vein__{k}__r"] = d["radius"]
        out[f"vein__{k}__kind"] = np.array(d["kind"])
    np.savez_compressed(out_path, **out)
    return out


def load_leg_assets(path):
    z = np.load(path, allow_pickle=False)
    out = {k: z[k] for k in z.files}
    veins = {}
    for k in z.files:
        if k.startswith("vein__") and k.endswith("__pts"):
            name = k.split("__")[1]
            veins[name] = dict(pts=z[k], radius=z[f"vein__{name}__r"], kind=str(z[f"vein__{name}__kind"]))
    out["veins"] = veins
    return out


if __name__ == "__main__":
    import sys
    import time
    t = time.time()
    o = build_leg_assets(sys.argv[1])
    print("skin", o["skin_v"].shape, o["skin_f"].shape, "bones", o["bone_v"].shape, "t", round(time.time() - t, 1))
