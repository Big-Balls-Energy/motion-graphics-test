# Arias Medical Clinic — Escleroterapia con microespuma (Reel 60 s, 9:16)

Producción audiovisual médica 3D original: anatomía procedural en Blender (Cycles), locución neuronal en
español latinoamericano, música y efectos sintetizados, composición y subtítulos en Python + FFmpeg.

## Entregables (`deliverables/`)
| Archivo | Contenido |
|---|---|
| `Arias_Medical_Clinic_Escleroterapia_60s.mp4` | Video final 1080×1920, 30 fps, H.264 High + AAC 48 kHz, 60,0 s |
| `subtitulos.srt` | Subtítulos sincronizados con la locución |
| `narracion.wav` | Locución procesada, ubicada en su tiempo final (60 s) |
| `miniatura_reels.png` | Miniatura vertical 1080×1920 |
| `../docs/` | Referencias, guion/storyboard con tiempos, control de calidad médica, reporte de QA (`qa_reporte.md`, `qa_tecnico.json`) |
| `../blend/*.blend` | Escenas editables de Blender 5.2 (modelos, materiales, luces, cámara) de los planos 1B, 2, 3A, 3B y 4 |
| `../audio/stems/*.flac` | Stems de audio: locución, música, efectos y mezcla final |

Las animaciones completas están definidas en los scripts (`scripts/shots/*.py`): son el proyecto editable
principal; los `.blend` congelan un instante representativo de cada plano para retocar modelos y materiales.

## Estructura
```
production/
  scripts/
    lib/anatomy.py       pierna por SDF + marching cubes, red venosa sobre la piel, huesos, eritrocito (Evans-Fung)
    lib/micro.py         pared venosa, valvas venosas, campo de flujo del reflujo, simulación de partículas
    lib/looks.py         materiales: piel con barrido de escáner, rayos X, venas, pared, membrana, burbujas
    lib/bl.py            utilidades de Blender (escena, cámaras, luces, mallas, instancias, render)
    lib/timeline.py      línea de tiempo maestra (60 s / 1800 frames), cortes y narración
    lib/ultrasound.py    inserto ecográfico modo B procedural
    lib/s2_timing.py     tiempos de la aguja/espuma compartidos entre 3D e inserto
    shots/s1a … s6.py    un archivo por plano 3D (build + animación + anclajes de etiquetas)
    render_shot.py       render de un plano (con escala, frames y exportación de anclajes 2D)
    render_daemon.sh     cola de render secuencial
    narration.py         locución (Supertonic 3 vía sherpa-onnx) con selección de toma por ASR
    qa_asr.py            verificación de la locución con Whisper
    audio.py             música, efectos, procesado de voz, mezcla y masterizado
    compose.py           composición final, gráficos, subtítulos, SRT y codificación
  audio/                 locución (segmentos y timeline), música, efectos y mezcla
  docs/                  documentación
  deliverables/          entregables
```

## Reproducir
Requisitos: Python 3.13, FFmpeg con libx264, ~8 GB de disco para frames.
```bash
python3 -m venv venv && . venv/bin/activate
pip install bpy==5.2.3 numpy scipy scikit-image opencv-python-headless pillow soundfile \
            sherpa-onnx piper-tts pyloudnorm
# Modelos (GitHub releases de k2-fsa/sherpa-onnx):
#   tts-models/sherpa-onnx-supertonic-3-tts-int8-2026-05-11.tar.bz2   (voz)
#   asr-models/sherpa-onnx-whisper-small.tar.bz2                       (QA de la locución)
cd production/scripts
python -m lib.anatomy ASSETS/leg.npz                              # geometría anatómica (≈2 min)
python narration.py MODELS/supertonic ../audio/narration_raw MODELS/whisper-small
python audio.py ../audio/narration_raw ../audio
for s in s1a s1b s2 s3a s3b s3c s4 s5 s6; do
  python render_shot.py $s --out FRAMES/$s --scale 0.75 --assets ASSETS
done
python compose.py --frames FRAMES --timeline ../audio/narration_raw/timeline.json \
  --audio ../audio/mix.wav --srt ../deliverables/subtitulos.srt \
  --out ../deliverables/Arias_Medical_Clinic_Escleroterapia_60s.mp4 [--logo ../assets/logo.png]
```
Render 3D: Cycles CPU, 8 muestras + OpenImageDenoise, desenfoque de movimiento y profundidad de campo,
resolución interna 810×1440 (720×1280 en los planos 4 y 5) reescalada con Lanczos + realce suave a 1080×1920;
todos los textos y gráficos se componen a 1080×1920 nativos.

## Logotipo oficial
La política de red del entorno bloqueó `ariasmedical.com`, por lo que el archivo del logotipo oficial no pudo
descargarse. Para no inventarlo ni alterarlo, el cierre usa el nombre de la clínica en tipografía.
Para integrarlo: guardar el logotipo oficial (PNG con transparencia) en `production/assets/logo.png` y volver
a ejecutar solo `compose.py` con `--logo ../assets/logo.png` (no requiere volver a renderizar el 3D).

## Licencias de terceros
- Blender (bpy) — GPL. Inter (tipografía) — SIL OFL.
- Supertonic 3 (Supertone Inc.) — OpenRAIL-M (uso comercial permitido con restricciones de uso responsable).
- Whisper (OpenAI) — MIT (solo QA). Todo el contenido visual y sonoro es original y procedural.
