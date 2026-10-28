"""Kokoro-82M (ONNX q8) Spanish TTS with espeak-ng es-419 phonemes."""
import json, re, subprocess
from pathlib import Path
import numpy as np
import onnxruntime as ort

SR = 24000
PUNCT = ',.!?;:…'


class Kokoro:
    def __init__(self, model_dir):
        model_dir = Path(model_dir)
        self.sess = ort.InferenceSession(str(model_dir / 'model_q8.onnx'),
                                         providers=['CPUExecutionProvider'])
        tok = json.load(open(model_dir / 'tokenizer.json'))
        self.vocab = tok['model']['vocab']
        self.voices = {}
        self.model_dir = model_dir

    def voice(self, name):
        if name not in self.voices:
            v = np.fromfile(self.model_dir / f'{name}.bin', dtype=np.float32)
            self.voices[name] = v.reshape(-1, 1, 256)
        return self.voices[name]

    @staticmethod
    def phonemize(text, lang='es-419'):
        text = text.replace('¿', '').replace('¡', '')
        out = []
        # phonemize chunk by chunk so punctuation (prosody cue) survives
        for chunk, punct in re.findall(r'([^,.!?;:…]+)([,.!?;:…]*)', text):
            chunk = chunk.strip()
            if not chunk:
                continue
            ipa = subprocess.run(['espeak-ng', '-v', lang, '-q', '--ipa=3', chunk],
                                 capture_output=True, text=True).stdout
            ipa = ' '.join(ipa.replace('_', '').split())
            out.append(ipa + punct[:1])
        return ' '.join(out)

    def tokens(self, ps):
        return [self.vocab[c] for c in ps if c in self.vocab]

    def synth(self, text, voice='ef_dora', speed=1.0):
        ps = self.phonemize(text)
        ids = self.tokens(ps)[:510]
        style = self.voice(voice)[len(ids)]
        wav = self.sess.run(None, {
            'input_ids': np.array([[0, *ids, 0]], dtype=np.int64),
            'style': style.astype(np.float32),
            'speed': np.array([speed], dtype=np.float32),
        })[0][0]
        return wav.astype(np.float32), ps


def trim(wav, thresh=0.012, pad=0.02):
    """Trim leading/trailing silence; returns (trimmed, lead_samples_removed)."""
    env = np.convolve(np.abs(wav), np.ones(240) / 240, mode='same')
    idx = np.where(env > thresh)[0]
    if len(idx) == 0:
        return wav, 0
    a = max(0, idx[0] - int(pad * SR))
    b = min(len(wav), idx[-1] + int(pad * SR))
    return wav[a:b], a
