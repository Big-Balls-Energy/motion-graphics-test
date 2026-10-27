"""QA técnico del MP4 final. Uso: python qa_video.py <video.mp4> <subtitulos.srt> <timeline.json> <reporte.json>"""
import json
import re
import subprocess
import sys

import numpy as np

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from lib.timeline import NARRATION  # noqa: E402


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True)


def main(video, srt, timeline_path, out):
    R = {}
    p = run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", video])
    info = json.loads(p.stdout)
    v = [s for s in info["streams"] if s["codec_type"] == "video"][0]
    a = [s for s in info["streams"] if s["codec_type"] == "audio"][0]
    R["archivo"] = video
    R["duracion_formato_s"] = float(info["format"]["duration"])
    R["video"] = dict(codec=v["codec_name"], perfil=v.get("profile"), ancho=v["width"], alto=v["height"],
                      fps=v["r_frame_rate"], frames=int(v.get("nb_frames", 0)), pix_fmt=v["pix_fmt"],
                      duracion_s=float(v["duration"]), bitrate_kbps=round(int(v.get("bit_rate", 0)) / 1000))
    R["audio"] = dict(codec=a["codec_name"], sample_rate=int(a["sample_rate"]), canales=a["channels"],
                      duracion_s=float(a["duration"]), bitrate_kbps=round(int(a.get("bit_rate", 0)) / 1000))
    R["tamano_MB"] = round(int(info["format"]["size"]) / 1e6, 1)
    # cuadros negros y congelados
    p = run(["ffmpeg", "-hide_banner", "-i", video, "-vf", "blackdetect=d=0.05:pic_th=0.97:pix_th=0.06",
             "-an", "-f", "null", "-"])
    R["cuadros_negros"] = re.findall(r"black_start:\S+ black_end:\S+ black_duration:\S+", p.stderr)
    p = run(["ffmpeg", "-hide_banner", "-i", video, "-vf", "freezedetect=n=0.0008:d=0.5", "-an", "-f", "null", "-"])
    R["congelados"] = re.findall(r"freeze_start: \S+|freeze_duration: \S+", p.stderr)
    # sonoridad EBU R128
    p = run(["ffmpeg", "-hide_banner", "-i", video, "-af", "ebur128=peak=true", "-vn", "-f", "null", "-"])
    m = re.search(r"Integrated loudness:\s+I:\s+(-?[\d.]+) LUFS", p.stderr)
    tp = re.search(r"True peak:\s+Peak:\s+(-?[\d.]+) dBFS", p.stderr)
    R["sonoridad_LUFS"] = float(m.group(1)) if m else None
    R["pico_real_dBTP"] = float(tp.group(1)) if tp else None
    # sincronía: cada subtítulo debe caer dentro de su segmento de narración
    tl = json.load(open(timeline_path, encoding="utf-8"))
    segs = [(k, t0, t0 + tl[k]["duration"]) for k, t0 in NARRATION]
    cues = []
    for block in open(srt, encoding="utf-8").read().strip().split("\n\n"):
        lines = block.split("\n")
        t = re.findall(r"(\d+):(\d+):(\d+),(\d+)", lines[1])
        ts = [int(h) * 3600 + int(mi) * 60 + int(s) + int(ms) / 1000 for h, mi, s, ms in t]
        cues.append((ts[0], ts[1], " ".join(lines[2:])))
    bad = []
    for c0, c1, txt in cues:
        ok = any(s0 - 0.05 <= c0 and c1 <= s1 + 0.30 for _, s0, s1 in segs)
        if not ok:
            bad.append([c0, c1, txt])
    R["subtitulos"] = dict(total=len(cues), fuera_de_su_locucion=bad,
                           escenas=[[k, round(s0, 2), round(s1, 2)] for k, s0, s1 in segs])
    R["checks"] = {
        "duracion_60s": abs(R["video"]["duracion_s"] - 60.0) < 0.02 and abs(R["audio"]["duracion_s"] - 60.0) < 0.05,
        "resolucion_1080x1920": (R["video"]["ancho"], R["video"]["alto"]) == (1080, 1920),
        "h264_aac": R["video"]["codec"] == "h264" and R["audio"]["codec"] == "aac",
        "fps_30": R["video"]["fps"] in ("30/1", "30"),
        "sin_cuadros_negros": len(R["cuadros_negros"]) == 0,
        "subtitulos_sincronizados": len(bad) == 0,
    }
    json.dump(R, open(out, "w"), ensure_ascii=False, indent=2)
    print(json.dumps(R, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main(*sys.argv[1:5])
