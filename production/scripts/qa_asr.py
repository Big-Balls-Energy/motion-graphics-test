"""QA de locución: transcribe cada segmento con Whisper-small (sherpa-onnx) y calcula WER.

Uso: python qa_asr.py <dir_whisper> <dir_narracion>   (lee timeline.json del dir de narración)
"""
import json
import re
import sys
import unicodedata

import numpy as np
import scipy.signal as ss
import sherpa_onnx
import soundfile as sf


def norm(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-zñ ]+", " ", s).split()


def wer(ref, hyp):
    r, h = norm(ref), norm(hyp)
    d = np.zeros((len(r) + 1, len(h) + 1), int)
    d[:, 0] = range(len(r) + 1)
    d[0, :] = range(len(h) + 1)
    for i in range(1, len(r) + 1):
        for j in range(1, len(h) + 1):
            d[i, j] = min(d[i - 1, j] + 1, d[i, j - 1] + 1, d[i - 1, j - 1] + (r[i - 1] != h[j - 1]))
    return d[-1, -1] / max(len(r), 1)


def main(wdir, ndir):
    rec = sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{wdir}/small-encoder.int8.onnx", decoder=f"{wdir}/small-decoder.int8.onnx",
        tokens=f"{wdir}/small-tokens.txt", language="es", task="transcribe", num_threads=4)
    timeline = json.load(open(f"{ndir}/timeline.json", encoding="utf-8"))
    errs = []
    for key, info in timeline.items():
        x, sr = sf.read(f"{ndir}/{key}.wav", dtype="float32")
        x = ss.resample_poly(x, 16000, sr).astype(np.float32)
        s = rec.create_stream()
        s.accept_waveform(16000, x)
        rec.decode_stream(s)
        hyp = s.result.text.strip()
        e = wer(info["text"], hyp)
        errs.append(e)
        print(f"{key}: WER={e:.2f} | {hyp}")
    print(f"WER medio: {np.mean(errs):.3f}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
