"""Write the caption blocks of build/timeline.json as an .srt file: python3 export_srt.py OUT.srt"""
import json, sys
from pathlib import Path

tl = json.load(open(Path(__file__).resolve().parent.parent / 'build' / 'timeline.json'))


def ts(x):
    ms = int(round(x * 1000))
    return f'{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}'


with open(sys.argv[1], 'w') as f:
    for i, b in enumerate(tl['blocks'], 1):
        text = ' '.join(tl['tokens'][k]['text'] for k in b['tokens'])
        f.write(f"{i}\n{ts(b['start'])} --> {ts(b['end'])}\n{text}\n\n")
