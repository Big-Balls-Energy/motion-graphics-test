# El efecto de progreso dotado — Reel 60 s (9:16)

Motion graphic de 60 s, 1080×1920, 30 fps, con narración IA en español latino, subtítulos karaoke quemados, música y efectos.

## Entregables (`dist/`)

| Archivo | Qué es |
|---|---|
| `efecto-progreso-dotado.mp4` | Video final: H.264 High, AAC 48 kHz estéreo, −14 LUFS, listo para Reels |
| `efecto-progreso-dotado.html` | Misma animación en un solo archivo, reproducible a pantalla completa (F), con audio |
| `subtitulos.srt` | Los bloques de subtítulos con sus tiempos |
| `efecto-progreso-dotado_sin-voz.mp4` | Mismo video con subtítulos, **sin voz en off**: solo efectos de sonido |
| `efecto-progreso-dotado_sin-voz_con-musica.mp4` | Sin voz en off, con efectos y música (sin ducking) |
| `pistas/sfx.wav`, `pistas/musica.wav` | Pistas separadas al mismo nivel que en la mezcla completa, para mezclar con una voz grabada aparte |
| `pistas/voz_guia.mp3` | La narración IA solo como guía de tiempos para grabar la voz |

## Cómo se construye

```
KOKORO_DIR=/ruta/kokoro ./make.sh [voz] [velocidad]     # por defecto: ef_dora 0.96
```

1. `tools/build_voice.py`: sintetiza el guion (`tools/script_data.py`) con Kokoro-82M (ONNX q8) y fonemas espeak-ng `es-419`.
   La salida de duraciones del modelo da tiempos exactos por palabra → `build/timeline.json`. Los bloques de subtítulo
   se optimizan para quedar en ≤ 5 palabras y ≥ 1.2 s en pantalla.
2. `src/reel.js`: toda la animación es una función `render(t)` en canvas; las escenas y los efectos se anclan a palabras del timeline.
3. `tools/render.js`: renderiza los 1800 cuadros con Chromium headless (Playwright) → `build/video.mp4`, y exporta los cues de SFX.
4. `tools/build_audio.py`: música procedural (112 BPM, 28 compases = 60 s exactos, loop limpio), efectos (pum, whoosh, ding, clic),
   ducking de la música bajo la voz y normalización a −14 LUFS.
5. `tools/qa_transcribe.py` (opcional): transcribe con Whisper para verificar dicción y sincronía.

`KOKORO_DIR` necesita `model_q8_dur.onnx` (el `model_quantized.onnx` de Kokoro-82M-v1.0-ONNX con la salida de duraciones
`/encoder/Clip_output_0` expuesta), `tokenizer.json` y los `.bin` de voz (`ef_dora`, `em_alex`, `em_santa`).

En el HTML: **F** pantalla completa · **Espacio** pausa · **R** reiniciar · **G** muestra las zonas seguras de Instagram.
