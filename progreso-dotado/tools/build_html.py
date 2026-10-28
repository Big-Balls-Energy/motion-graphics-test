"""Inline font, timeline, script (and optionally audio) into a single HTML file.

usage: python3 build_html.py OUT.html [--audio mix.mp3]
"""
import argparse, base64, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('out')
    ap.add_argument('--audio')
    a = ap.parse_args()
    b64 = lambda p: base64.b64encode(Path(p).read_bytes()).decode()
    timeline = json.load(open(ROOT / 'build' / 'timeline.json'))
    audio_tag = ''
    if a.audio:
        audio_tag = f'<audio id="audio" preload="auto" src="data:audio/mpeg;base64,{b64(a.audio)}"></audio>'
    html = (ROOT / 'src' / 'template.html').read_text()
    html = (html.replace('{{FONT}}', b64(ROOT / 'assets' / 'Montserrat-latin.woff2'))
                .replace('{{AUDIO_TAG}}', audio_tag)
                .replace('{{BRAND}}', json.dumps({k: 'data:image/png;base64,' + b64(ROOT / 'assets' / f'atlas-path-{k}.png')
                                                  for k in ('logo', 'icon', 'word')}))
                .replace('{{TIMELINE}}', json.dumps(timeline, ensure_ascii=False, separators=(',', ':')))
                .replace('{{REEL_JS}}', (ROOT / 'src' / 'reel.js').read_text()))
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(html)
    print(f'{a.out}: {len(html) / 1e6:.2f} MB')


if __name__ == '__main__':
    main()
