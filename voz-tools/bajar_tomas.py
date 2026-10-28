"""Descarga las tomas de ElevenLabs de un resultado de creative_get_flow_run_status guardado en archivo.
Uso: python3 bajar_tomas.py <status.json> <carpeta_tomas> <prefijo0|prefijo1|...>  (un prefijo de texto por bloque, en orden)"""
import json, os, subprocess, sys
d = json.load(open(sys.argv[1])); out = sys.argv[2]; keys = sys.argv[3].split('|'); os.makedirs(out, exist_ok=True)
pend = 0
for g in d['generations']:
    if g['status'] != 'completed': pend += 1; continue
    i = [k for k, s in enumerate(keys) if s in g['prompt']][0]
    fn = next(f'{out}/{i:02d}-{n}.mp3' for n in range(1, 9) if not os.path.exists(f'{out}/{i:02d}-{n}.mp3') or open(f'{out}/{i:02d}-{n}.id').read() == g['id'])
    if os.path.exists(fn): continue
    subprocess.run(['curl', '-sS', '-o', fn, g['content_url']], check=True); open(fn[:-4] + '.id', 'w').write(g['id'])
    print(fn, g['duration_secs'])
print('pendientes:', pend)
