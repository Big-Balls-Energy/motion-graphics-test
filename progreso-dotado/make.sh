#!/usr/bin/env bash
# Full pipeline: voice → timeline → frames → music/SFX mix → MP4 + standalone HTML.
#   KOKORO_DIR=/path/to/kokoro ./make.sh [voice] [speed]
set -euo pipefail
cd "$(dirname "$0")"
VOICE=${1:-ef_dora}
SPEED=${2:-0.96}
KOKORO_DIR=${KOKORO_DIR:?set KOKORO_DIR to the folder with model_q8_dur.onnx, tokenizer.json and voice .bin files}

python3 tools/build_voice.py "$KOKORO_DIR" build --voice "$VOICE" --speed "$SPEED"
python3 tools/build_html.py build/render.html
node tools/render.js build/render.html build --workers 3
python3 tools/build_audio.py build
mkdir -p dist
ffmpeg -y -v error -i build/video.mp4 -i build/mix.wav -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 192k -ar 48000 -t 60 -movflags +faststart dist/efecto-progreso-dotado.mp4
ffmpeg -y -v error -i build/mix.wav -c:a libmp3lame -b:a 160k build/mix.mp3
python3 tools/build_html.py dist/efecto-progreso-dotado.html --audio build/mix.mp3
python3 tools/export_srt.py dist/subtitulos.srt
ls -la dist
