# Reel: El efecto señuelo (60 s · 1080×1920 · 30 fps · sin voz)

- `entregables/` — MP4 (con música + efectos y sin audio), guion con tiempos, reproductor HTML autónomo y pistas WAV por separado.
- `player/` — fuente de la animación (`timeline.js` = subtítulos, efectos y volumen; `anim.js` = escenas).
- `tools/` — `audio.py` (música/efectos), `render.mjs` (cuadros → MP4), `build.mjs` (HTML autónomo + guion), `stills.mjs` (cuadros sueltos).

Regenerar todo:
```
python3 tools/audio.py build
node tools/render.mjs build/mezcla.wav build/efecto_senuelo.mp4
ffmpeg -y -i build/mezcla.wav -c:a aac -b:a 192k player/audio/musica_y_efectos.m4a
node tools/build.mjs entregables
```
