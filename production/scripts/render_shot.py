"""Renderiza un plano 3D.

Uso:
  python render_shot.py <shot> --out DIR [--scale 0.33] [--spp N] [--frames 0,60,120 | --every 10]
                        [--assets DIR]

<shot> es un módulo de shots/ que define:
  build(sc, ctx) -> update(t_local_seconds)    (construye la escena)
  RENDER = dict(spp=..., bounces=..., ...)      (ajustes de calidad final)
"""
import argparse
import importlib
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bpy  # noqa: E402

from lib import bl  # noqa: E402
from lib.timeline import FPS, SHOTS  # noqa: E402


def export_anchors(sc, mod, frames, a, path):
    """Proyección 2D (0..1, origen abajo-izquierda) de los puntos 3D que usan las etiquetas."""
    import json
    from bpy_extras.object_utils import world_to_camera_view
    from mathutils import Vector
    data = {}
    if os.path.exists(path):
        data = json.load(open(path))
    for fr in frames:
        sc.frame_set(fr)
        t = (fr - a) / FPS
        out = {}
        for name, p in mod.anchors(t).items():
            v = world_to_camera_view(sc, sc.camera, Vector(p))
            out[name] = [round(v.x, 5), round(v.y, 5), round(v.z, 4)]
        data[str(fr)] = out
    os.makedirs(os.path.dirname(path), exist_ok=True)
    json.dump(data, open(path, "w"))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("shot")
    ap.add_argument("--out", required=True)
    ap.add_argument("--scale", type=float, default=1.0)
    ap.add_argument("--spp", type=int, default=None)
    ap.add_argument("--frames", default=None)
    ap.add_argument("--every", type=int, default=None)
    ap.add_argument("--assets", default=os.environ.get("AMC_ASSETS", ""))
    ap.add_argument("--no-mblur", action="store_true")
    ap.add_argument("--anchors-only", action="store_true")
    args = ap.parse_args()

    mod = importlib.import_module(f"shots.{args.shot}")
    sc = bl.reset()
    R = dict(getattr(mod, "RENDER", {}))
    res = R.pop("res", (1080, 1920))
    res = (int(round(res[0] * args.scale / 2) * 2), int(round(res[1] * args.scale / 2) * 2))
    if args.spp:
        R["spp"] = args.spp
    if args.no_mblur:
        R["motion_blur"] = False
    bl.setup_render(sc, res=res, **R)
    ctx = dict(assets=args.assets, scale=args.scale)
    update = mod.build(sc, ctx)
    a, b = SHOTS[args.shot]
    sc.frame_start, sc.frame_end = a, b

    def fn(t_master):
        update(t_master - a / FPS)

    bl.register_update(sc, fn)
    if args.frames:
        frames = [a + int(f) for f in args.frames.split(",")]
    elif args.every:
        frames = list(range(a, b + 1, args.every))
    else:
        frames = list(range(a, b + 1))
    t0 = time.time()
    if hasattr(mod, "anchors"):
        export_anchors(sc, mod, frames, a, os.path.join(args.out, "anchors.json"))
    if args.anchors_only:
        print("ANCHORS ONLY", flush=True)
        return
    bl.render_frames(sc, args.out, frames, prefix=f"{args.shot}_", log=os.path.join(args.out, "render.log"))
    print(f"DONE {args.shot} {len(frames)} frames in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
