"""QA: transcribe an audio file with Whisper and compare word timings with timeline.json.

usage: python3 qa_transcribe.py WHISPER_MODEL_DIR AUDIO [timeline.json]
"""
import json, re, subprocess, sys, unicodedata
import numpy as np
from faster_whisper import WhisperModel


def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9%ñ]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))


model = WhisperModel(sys.argv[1], device='cpu', compute_type='int8')
pcm = subprocess.run(['ffmpeg', '-v', 'error', '-i', sys.argv[2], '-ar', '16000', '-ac', '1', '-f', 'f32le', '-'],
                     capture_output=True, check=True).stdout
segs, _ = model.transcribe(np.frombuffer(pcm, dtype=np.float32), language='es', word_timestamps=True, beam_size=5,
                           initial_prompt='Efecto de progreso dotado. Autolavado, sellos, tarjeta.')
words = []
for s in segs:
    print(f'[{s.start:5.1f}-{s.end:5.1f}] {s.text.strip()}')
    words += [(w.word.strip(), w.start, w.end) for w in s.words]
if len(sys.argv) > 3:
    tl = json.load(open(sys.argv[3]))
    toks = [(t['text'], t['start']) for t in tl['tokens']]
    # greedy alignment on normalized text, report timing offsets of matched words
    j, offs = 0, []
    for w, ws, we in words:
        for k in range(j, min(j + 4, len(toks))):
            if norm(toks[k][0]) and norm(toks[k][0]) == norm(w):
                offs.append(ws - toks[k][1]); j = k + 1
                break
    import statistics as st
    print(f'\nmatched {len(offs)}/{len(toks)} words; whisper-minus-timeline start offset: '
          f'median {st.median(offs) * 1000:.0f} ms, p90 |off| {sorted(abs(o) for o in offs)[int(0.9 * len(offs))] * 1000:.0f} ms')
