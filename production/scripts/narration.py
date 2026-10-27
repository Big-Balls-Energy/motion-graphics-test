"""Narración en español latinoamericano para el video de escleroterapia con microespuma.

Motor: Supertonic 3 (ONNX, OpenRAIL-M) vía sherpa-onnx, voz preset sid=8 (barítono).
Modelo: https://github.com/k2-fsa/sherpa-onnx/releases/download/tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2

El texto que se envía al motor usa una re-escritura fonética con seseo (c/z -> s) para
garantizar pronunciación latinoamericana; los subtítulos conservan la ortografía correcta.

Uso:
    python narration.py <dir_modelo> <dir_salida> [<dir_whisper_para_elegir_tomas>]
Salida: un WAV por segmento (44.1 kHz) + timeline.json con duraciones y pausas internas.
"""
import json
import os
import re
import sys

import numpy as np
import sherpa_onnx
import soundfile as sf

VOICE_SID = 8
SPEED = 1.0
NUM_STEPS = 32
# Ajuste fino del ritmo del propio modelo (no es time-stretch) para encajar en la ventana de cada escena.
SPEED_OVERRIDE = {"n2": 1.05, "n4a": 1.03, "n4b": 1.03}

# (id, texto correcto para subtítulos)
SEGMENTS = [
    ("n1", "Cuando las válvulas venosas fallan, la sangre puede retroceder y acumularse, favoreciendo la aparición de várices."),
    ("n2", "La escleroterapia con microespuma permite tratar determinadas venas enfermas mediante un procedimiento mínimamente invasivo."),
    ("n3a", "La microespuma entra en contacto con la pared interna de la vena"),
    ("n3b", "y provoca una reacción que favorece su cierre progresivo."),
    ("n4a", "Con el tiempo, la vena tratada se transforma y el organismo la reabsorbe progresivamente."),
    ("n4b", "La sangre continúa circulando por otras venas funcionales."),
    ("n5", "Es una alternativa ambulatoria, sin cirugía abierta y con recuperación habitualmente rápida, según la valoración de cada paciente."),
    ("n6a", "En Arias Medical Clinic, la salud de tus piernas merece atención especializada."),
    ("n6b", "Agenda tu valoración."),
]


def tts_text(text):
    """Re-escritura fonética solo para el motor TTS (seseo + acentuación de la marca)."""
    t = text.replace("Arias Medical Clinic", "Árias Médical Clínic")
    t = re.sub(r"c(?=[eiéí])", "s", t)
    t = re.sub(r"C(?=[eiéí])", "S", t)
    return t.replace("z", "s").replace("Z", "S")


def build_tts(model_dir):
    d = model_dir
    cfg = sherpa_onnx.OfflineTtsConfig(model=sherpa_onnx.OfflineTtsModelConfig(
        supertonic=sherpa_onnx.OfflineTtsSupertonicModelConfig(
            duration_predictor=f"{d}/duration_predictor.int8.onnx",
            text_encoder=f"{d}/text_encoder.int8.onnx",
            vector_estimator=f"{d}/vector_estimator.int8.onnx",
            vocoder=f"{d}/vocoder.int8.onnx",
            tts_json=f"{d}/tts.json",
            unicode_indexer=f"{d}/unicode_indexer.bin",
            voice_style=f"{d}/voice.bin"),
        num_threads=4, provider="cpu"))
    return sherpa_onnx.OfflineTts(cfg)


def trim(x, sr, thr=0.004, head=0.01, tail=0.12):
    idx = np.where(np.abs(x) > thr * np.abs(x).max())[0]
    return x[max(idx[0] - int(head * sr), 0): idx[-1] + int(tail * sr)]


def internal_pauses(x, sr, min_gap=0.07):
    """Silencios internos (para alinear cortes de subtítulos con comas/puntos)."""
    hop = int(sr * 0.01)
    rms = np.sqrt(np.convolve(x ** 2, np.ones(hop) / hop, mode="same"))[::hop]
    quiet = rms < 0.02 * rms.max()
    gaps, start = [], None
    for i, q in enumerate(quiet):
        if q and start is None:
            start = i
        elif not q and start is not None:
            if (i - start) * 0.01 >= min_gap and start > 5:
                gaps.append(((start) * 0.01, i * 0.01))
            start = None
    return gaps


# Duración máxima (s) que admite la ventana de cada segmento en el timeline del video.
MAX_DUR = {"n1": 7.4, "n2": 7.8, "n3a": 4.4, "n3b": 3.6, "n4a": 5.7, "n4b": 3.7,
           "n5": 9.2, "n6a": 5.5, "n6b": 1.8}
TAKES = 6


def main(model_dir, out_dir, whisper_dir=None):
    """Genera varias tomas por segmento (el muestreo es estocástico) y elige la mejor:
    menor WER en Whisper (si se indica) y duración dentro de la ventana; desempate por
    cercanía a la mediana de duración (ritmo más natural)."""
    os.makedirs(out_dir, exist_ok=True)
    tts = build_tts(model_dir)
    rec = None
    if whisper_dir:
        import scipy.signal as ss
        from qa_asr import wer
        rec = sherpa_onnx.OfflineRecognizer.from_whisper(
            encoder=f"{whisper_dir}/small-encoder.int8.onnx", decoder=f"{whisper_dir}/small-decoder.int8.onnx",
            tokens=f"{whisper_dir}/small-tokens.txt", language="es", task="transcribe", num_threads=4)
    timeline = {}
    for key, text in SEGMENTS:
        takes = []
        for take in range(TAKES):
            g = sherpa_onnx.GenerationConfig()
            g.sid = VOICE_SID
            g.speed = SPEED_OVERRIDE.get(key, SPEED)
            g.num_steps = NUM_STEPS
            g.extra = {"lang": "es"}
            a = tts.generate(tts_text(text), g)
            x = trim(np.array(a.samples, np.float32), a.sample_rate)
            err = 0.0
            if rec is not None:
                s = rec.create_stream()
                s.accept_waveform(16000, ss.resample_poly(x, 16000, a.sample_rate).astype(np.float32))
                rec.decode_stream(s)
                err = wer(text, s.result.text)
            takes.append((x, a.sample_rate, err))
        durs = np.array([len(t[0]) / t[1] for t in takes])
        med = np.median(durs)

        def score(i):
            over = max(0.0, durs[i] - MAX_DUR[key])
            return (round(takes[i][2], 3), over > 0, abs(durs[i] - med))

        best = min(range(TAKES), key=score)
        x, sr, err = takes[best]
        sf.write(f"{out_dir}/{key}.wav", x, sr, subtype="PCM_24")
        timeline[key] = {
            "text": text,
            "tts_input": tts_text(text),
            "duration": round(len(x) / sr, 3),
            "pauses": [[round(s, 2), round(e, 2)] for s, e in internal_pauses(x, sr)],
            "sample_rate": sr,
            "speed": SPEED_OVERRIDE.get(key, SPEED),
            "take": best,
            "wer": round(err, 3),
            "take_durations": [round(float(d), 2) for d in durs],
        }
        print(key, timeline[key]["duration"], "take", best, "wer", round(err, 3), timeline[key]["take_durations"])
    with open(f"{out_dir}/timeline.json", "w", encoding="utf-8") as f:
        json.dump(timeline, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
