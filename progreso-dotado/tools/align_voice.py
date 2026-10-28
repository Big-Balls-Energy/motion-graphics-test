"""Use an external narration (e.g. an ElevenLabs export) instead of the built-in TTS.

usage: python3 align_voice.py WHISPER_MODEL_DIR NARRATION.(mp3|wav) BUILD_DIR [--fit 58.2]

Transcribes the narration with Whisper (word timestamps), aligns it to the script
in script_data.py and writes BUILD_DIR/voice.wav + BUILD_DIR/timeline.json in the
same format build_voice.py produces, so the render picks it up unchanged.
Leading silence is trimmed so the first word lands at 0.12 s; if the last word
ends after --fit seconds the take is sped up (at most 8 %) to fit.
"""
import argparse, difflib, json, re, subprocess, unicodedata
from pathlib import Path
import numpy as np
from faster_whisper import WhisperModel
from build_voice import parse_unit, make_blocks
from script_data import UNITS

SR = 48000
START = 0.12
NUM = {'2': 'dos', '8': 'ocho', '10': 'diez', '19': 'diecinueve', '20': 'veinte',
       '34': 'treinta y cuatro', '%': 'por ciento'}


def norm(w):
    w = unicodedata.normalize('NFD', w.lower())
    return re.sub(r'[^a-z0-9ñ]', '', ''.join(c for c in w if unicodedata.category(c) != 'Mn'))


def expand(word):
    """Whisper may write '19%' or '8'; spell numbers the way the script speaks them."""
    m = re.match(r'^(\d+)(%?)', word.strip())
    if not m:
        return [word]
    out = NUM.get(m.group(1), m.group(1)).split()
    return out + (NUM['%'].split() if m.group(2) else [])


def load(path):
    pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(path), '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, dtype=np.float32).copy()


def transcribe(model, audio):
    a16 = audio[::3]  # 48 kHz -> 16 kHz (speech band only; fine for alignment)
    segs, _ = model.transcribe(a16, language='es', word_timestamps=True, beam_size=5,
                               initial_prompt='Efecto de progreso dotado. Autolavado, sellos. Atlas Path.')
    words = []
    for s in segs:
        for w in s.words:
            parts = expand(w.word)
            step = (w.end - w.start) / len(parts)
            words += [(p, w.start + i * step, w.start + (i + 1) * step) for i, p in enumerate(parts)]
    return words


def onset(audio, hop=0.01):
    """Time where the voice first becomes audible."""
    h = int(hop * SR)
    n = len(audio) // h
    env = np.sqrt(np.mean(audio[:n * h].reshape(n, h) ** 2, axis=1))
    return float(np.argmax(env > 0.2 * np.median(env[env > 0.05 * env.max()])) * hop)


WHISPER_LAG = 0.09   # this model stamps words ~90 ms early (measured against exact TTS timings)


def snap_onsets(audio, words, hop=0.01):
    """Correct Whisper's word starts: if a word's span holds a real pause (>= 150 ms),
    the word starts where the pause ends; otherwise apply the measured lag."""
    h = int(hop * SR)
    n = len(audio) // h
    env = np.sqrt(np.mean(audio[:n * h].reshape(n, h) ** 2, axis=1))
    quiet = env < 0.2 * np.median(env[env > 0.05 * env.max()])
    out = []
    for w, s0, e0 in words:
        start, run = min(s0 + WHISPER_LAG, e0 - 0.03), 0
        for i in range(int(s0 / hop), min(int((e0 - 0.06) / hop), n - 1)):
            run = run + 1 if quiet[i] else 0
            if run >= 15 and not quiet[i + 1]:
                start = (i + 1) * hop
        out.append((w, start, e0))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model_dir')
    ap.add_argument('audio')
    ap.add_argument('build')
    ap.add_argument('--fit', type=float, default=58.2)
    a = ap.parse_args()
    build = Path(a.build)
    model = WhisperModel(a.model_dir, device='cpu', compute_type='int8')

    audio = load(a.audio)
    words = transcribe(model, audio)
    first, last = onset(audio), words[-1][2]
    tempo = min(1.08, max(1.0, (last - first) / (a.fit - START)))
    if tempo > 1.0:   # speed up slightly to fit, then re-transcribe for exact timings
        stretched = subprocess.run(['ffmpeg', '-v', 'error', '-i', str(a.audio), '-af', f'atempo={tempo:.4f}',
                                    '-ar', str(SR), '-ac', '1', '-f', 'f32le', '-'], capture_output=True, check=True).stdout
        audio = np.frombuffer(stretched, dtype=np.float32).copy()
        words = transcribe(model, audio)
        first = onset(audio)
    # trim/pad so the voice starts at START
    shift = START - first
    lead = int(round(shift * SR))
    audio = np.concatenate([np.zeros(lead, np.float32), audio]) if lead > 0 else audio[-lead:]
    words = [(w, s + shift, e + shift) for w, s, e in words]

    # script tokens and their spoken words
    tokens, spoken = [], []
    for ui, (section, text, _) in enumerate(UNITS):
        toks, cont = parse_unit(text)
        for j, tk in enumerate(toks):
            # numbers are matched as spoken ("diecinueve por ciento"), everything else as written
            src = tk['spoken'] if re.search(r'\d', tk['disp']) else tk['disp']
            sw = [x for x in src.split() if norm(x)]
            tokens.append(dict(text=tk['disp'], kw=tk['kw'], fig=tk['fig'], soft=tk['brk'],
                               hard=j == 0 and not cont, unit=ui, section=section, n=len(sw)))
            spoken += [norm(x) for x in sw]
    words = snap_onsets(audio, words)
    heard = [norm(w) for w, _, _ in words]
    times = [None] * len(spoken)
    for blk in difflib.SequenceMatcher(None, spoken, heard, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = words[blk.b + k][1:]
    matched = sum(t is not None for t in times)
    # interpolate unmatched words between their matched neighbours
    known = [i for i, t in enumerate(times) if t]
    for i, t in enumerate(times):
        if t is None:
            lo = max([k for k in known if k < i], default=None)
            hi = min([k for k in known if k > i], default=None)
            s0 = times[lo][1] if lo is not None else START
            s1 = times[hi][0] if hi is not None else s0 + 0.3
            span = (s1 - s0) / ((hi or len(times)) - (lo if lo is not None else -1))
            k0 = i - (lo if lo is not None else -1)
            times[i] = (s0 + span * (k0 - 1), s0 + span * k0)
    si = 0
    for tk in tokens:
        n = tk.pop('n')
        tk['start'] = round(times[si][0], 3)
        tk['end'] = round(times[si + n - 1][1], 3)
        si += n
    sections = []
    for tk in tokens:
        if not sections or sections[-1]['id'] != tk['section']:
            sections.append(dict(id=tk['section'], start=tk['start']))
    voice_end = tokens[-1]['end']
    blocks = make_blocks(tokens, voice_end)

    import wave
    with wave.open(str(build / 'voice.wav'), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        peak = max(1e-6, float(np.abs(audio).max()))
        f.writeframes((np.clip(audio / peak * 0.89, -1, 1) * 32767).astype(np.int16).tobytes())
    json.dump(dict(voice=Path(a.audio).name, speed=round(tempo, 4), voiceEnd=round(voice_end, 3),
                   sections=sections, tokens=tokens, blocks=blocks),
              open(build / 'timeline.json', 'w'), ensure_ascii=False, indent=1)
    print(f'aligned {matched}/{len(spoken)} spoken words directly (rest interpolated); '
          f'tempo x{tempo:.3f}; voice ends at {voice_end:.2f}s')
    if voice_end > 58.6:
        print('WARNING: narration still ends after 58.6 s; the CTA click/loop will be squeezed')


if __name__ == '__main__':
    main()
