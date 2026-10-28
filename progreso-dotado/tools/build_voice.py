"""Synthesize the narration and emit a word-level timeline.

usage: python3 build_voice.py MODEL_DIR OUT_DIR [--voice ef_dora] [--speed 1.0] [--start 0.12]
"""
import argparse, hashlib, json, re, wave
from pathlib import Path
import numpy as np
import onnxruntime as ort
from kokoro_tts import Kokoro, SR
from script_data import UNITS

FRAME = 600 / SR  # seconds per Kokoro duration frame
MIN_BLOCK = 1.2   # seconds a caption block must stay on screen
BORROW = 0.2      # max delay of a block so the previous one reaches MIN_BLOCK


def parse_unit(text):
    """-> (tokens {disp, spoken, kw, fig, brk}, continues_previous_block)."""
    toks, brk = [], False
    cont = text.startswith('+')
    for raw in text.lstrip('+').split():
        if raw == '|':
            brk = True
            continue
        kw, fig = raw.startswith('*'), raw.startswith('#')
        raw = raw.lstrip('*#')
        m = re.match(r'^(.*?)([,.!?;:…]*)$', raw)
        word, punct = m.group(1), m.group(2)
        if '=' in word:
            disp, spoken = word.split('=', 1)
            spoken = spoken.replace('_', ' ')
        else:
            disp = spoken = word
        toks.append(dict(disp=disp + punct, spoken=spoken + punct, kw=kw, fig=fig, brk=brk))
        brk = False
    return toks, cont


def word_times(k, sess, text, voice, speed, cache_dir):
    """Synthesize `text`; return (wav, [(start, end)] per spoken word)."""
    key = hashlib.sha1(f'{voice}|{speed}|{text}'.encode()).hexdigest()[:16]
    cached = Path(cache_dir) / f'{key}.npz'
    if cached.exists():
        z = np.load(cached)
        return z['wav'], [tuple(x) for x in z['spans']]
    ps = k.phonemize(text)
    nwords = len(text.replace('¿', '').replace('¡', '').split())
    if len(ps.split()) != nwords:
        # fall back to per-word phonemes so word boundaries stay exact
        ps = ' '.join(k.phonemize(w) for w in text.split())
    assert len(ps.split()) == nwords, (text, ps)
    chars = [c for c in ps if c in k.vocab]
    ids = [k.vocab[c] for c in chars]
    style = k.voice(voice)[len(ids)]
    wav, dur = sess.run(None, {
        'input_ids': np.array([[0, *ids, 0]], dtype=np.int64),
        'style': style.astype(np.float32),
        'speed': np.array([speed], dtype=np.float32)})
    wav, dur = wav[0], dur.flatten()
    t = dur[0]  # BOS
    spans, cur = [], None
    for c, d in zip(chars, dur[1:-1]):
        if c == ' ':
            if cur:
                spans.append(cur)
                cur = None
        elif c in ',.!?;:…':
            pass  # punctuation pause belongs to no word
        else:
            cur = [t, t + d] if cur is None else [cur[0], t + d]
        t += d
    if cur:
        spans.append(cur)
    assert len(spans) == nwords, (text, ps, len(spans))
    spans = [(a * FRAME, b * FRAME) for a, b in spans]
    np.savez(cached, wav=wav, spans=np.array(spans))
    return wav, spans


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('model_dir')
    ap.add_argument('out_dir')
    ap.add_argument('--voice', default='ef_dora')
    ap.add_argument('--speed', type=float, default=1.0)
    ap.add_argument('--start', type=float, default=0.12)
    a = ap.parse_args()
    out = Path(a.out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cache = out / 'tts_cache'
    cache.mkdir(exist_ok=True)

    k = Kokoro(a.model_dir)
    sess = ort.InferenceSession(str(Path(a.model_dir) / 'model_q8_dur.onnx'),
                                providers=['CPUExecutionProvider'])

    clips, tokens, sections = [], [], []
    t = a.start
    for ui, (section, text, pause) in enumerate(UNITS):
        toks, cont = parse_unit(text)
        spoken = ' '.join(tk['spoken'] for tk in toks)
        wav, spans = word_times(k, sess, spoken, a.voice, a.speed, cache)
        offset = t - spans[0][0]           # place first word exactly at t
        clips.append((offset, wav))
        si = 0
        for j, tk in enumerate(toks):
            n = len(tk['spoken'].split())
            s0, s1 = spans[si][0], spans[si + n - 1][1]
            si += n
            tokens.append(dict(text=tk['disp'], kw=tk['kw'], fig=tk['fig'],
                               soft=tk['brk'], hard=j == 0 and not cont, unit=ui,
                               section=section, start=round(float(offset + s0), 3),
                               end=round(float(offset + s1), 3)))
        if not sections or sections[-1]['id'] != section:
            sections.append(dict(id=section, start=tokens[-len(toks)]['start']))
        t = float(offset + spans[-1][1] + pause)
        print(f'{section:12s} {tokens[-len(toks)]["start"]:6.2f}-{t - pause:6.2f}  {spoken}')

    voice_end = t - UNITS[-1][2]
    total = int(np.ceil((max(o + len(w) / SR for o, w in clips)) * SR))
    mix = np.zeros(total + SR, dtype=np.float32)
    for o, w in clips:
        i = int(round(o * SR))
        if i < 0:
            w, i = w[-i:], 0
        mix[i:i + len(w)] += w
    mix /= max(1e-6, np.abs(mix).max()) / 0.89
    with wave.open(str(out / 'voice.wav'), 'wb') as f:
        f.setnchannels(1); f.setsampwidth(2); f.setframerate(SR)
        f.writeframes((mix * 32767).astype(np.int16).tobytes())

    blocks = make_blocks(tokens, voice_end)
    json.dump(dict(voice=a.voice, speed=a.speed, voiceEnd=round(voice_end, 3),
                   sections=sections, tokens=tokens, blocks=blocks),
              open(out / 'timeline.json', 'w'), ensure_ascii=False, indent=1)
    words = sum(len(x['text'].split()) for x in tokens)
    print(f'voice ends at {voice_end:.2f}s, {len(tokens)} tokens, '
          f'{words / (voice_end - a.start):.2f} words/s incl. pauses')


FUNCTION_WORDS = set('de del la las el los un una y a al que en no tu te se por para con ya'.split())


def make_blocks(tokens, voice_end):
    """Partition tokens into caption blocks of <=5 words lasting >=1.2 s.

    Hard breaks: unit starts (unless continued with '+'). A segment between
    hard breaks that holds a figure stays one block; others are split by DP.
    """
    segs, cur = [], []
    for i, tk in enumerate(tokens):
        if tk['hard'] and cur:
            segs.append(cur)
            cur = []
        cur.append(i)
    segs.append(cur)

    def start(i):
        return 0.0 if i == 0 else tokens[i]['start'] if i < len(tokens) else voice_end + 0.6

    def cost(i, j):  # block = tokens[i:j]
        n = j - i
        dur = start(j) - start(i)
        deficit = max(0, MIN_BLOCK - dur)
        # deficits up to BORROW are fixed later by delaying the next block a bit
        c = 0.3 * abs(n - 4) + 40 * max(0, n - 5) + (8 if deficit <= BORROW else 60) * deficit
        last = tokens[j - 1]['text']
        if j < len(tokens) and not tokens[j]['hard']:
            if last[-1] in ',.!?;:…':
                c -= 2
            if tokens[j]['soft']:
                c -= 1.5
            if last.lower() in FUNCTION_WORDS:
                c += 4
        return c

    def dp(seg):
        a, b = seg[0], seg[-1] + 1
        best = {a: (0.0, None)}
        for j in range(a + 1, b + 1):
            best[j] = min((best[i][0] + cost(i, j), i) for i in range(max(a, j - 6), j))
        cuts, j = [], b
        while j != a:
            i = best[j][1]
            cuts.append(list(range(i, j)))
            j = i
        return list(reversed(cuts))

    blocks = []
    for seg in segs:
        figs = [i for i in seg if tokens[i]['fig']]
        if not figs:
            blocks.extend(dp(seg))
            continue
        # the figure block starts at the last soft break before the figure
        soft = [i for i in seg if tokens[i]['soft'] and i <= figs[0]]
        cut = soft[-1] if soft else seg[0]
        if cut > seg[0]:
            blocks.extend(dp([i for i in seg if i < cut]))
        blocks.append([i for i in seg if i >= cut])

    starts = [start(idx[0]) for idx in blocks] + [voice_end + 0.6]
    for k in range(len(blocks) - 1):
        deficit = MIN_BLOCK - (starts[k + 1] - starts[k])
        if 0 < deficit <= BORROW and starts[k + 2] - starts[k + 1] - deficit >= MIN_BLOCK - 0.01:
            starts[k + 1] += deficit
    out = []
    for k, idx in enumerate(blocks):
        out.append(dict(tokens=idx, figure=any(tokens[i]['fig'] for i in idx),
                        start=round(starts[k], 3), end=round(starts[k + 1], 3)))
    for b in out:
        txt = ' '.join(tokens[i]['text'] for i in b['tokens'])
        flag = '  <-- SHORT' if b['end'] - b['start'] < MIN_BLOCK - 0.01 else ''
        flag += '  <-- LONG' if len(b['tokens']) > 5 and not b['figure'] else ''
        print(f"  [{b['start']:6.2f} {b['end'] - b['start']:4.2f}s] {'FIG ' if b['figure'] else ''}{txt}{flag}")
    return out


if __name__ == '__main__':
    main()
