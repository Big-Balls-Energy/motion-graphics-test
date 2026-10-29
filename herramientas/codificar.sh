#!/bin/bash
# Codifica el reel en dos versiones (H.264 CRF 19 yuv420p + AAC 192k 48 kHz, faststart), normalizadas a −14 LUFS en dos pasadas:
#   · con voz: loudnorm con pico real −1.5 dBTP
#   · sin voz: compresor + loudnorm a −3 dBTP (sin voz que cubra los golpes, el AAC llegaba a +0.4 dBTP)
# También deja audio/mezcla-con-voz.m4a, que usa index.html para reproducir con sonido en el navegador.
# Uso: bash herramientas/codificar.sh <carpeta_reel> <carpeta_cuadros> <salida-con-voz.mp4> <salida-sin-voz.mp4>
# Requiere audio/mezcla-sin-voz.wav (tools/audio.py) y audio/mezcla-con-voz.wav (voz-tools/voz_tomas.py).
set -e
cd "$1"; FR=$(cd "$2" && pwd); CON=$3; SIN=$4
ln2() { # $1 archivo, $2 pico real, $3 filtro previo opcional
  local pre=${3:+$3,}
  local J=$(ffmpeg -hide_banner -i "$1" -af "${pre}loudnorm=I=-14:TP=$2:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  echo "${pre}loudnorm=I=-14:TP=$2:LRA=11:measured_I=$(echo "$J" | jq -r .input_i):measured_TP=$(echo "$J" | jq -r .input_tp):measured_LRA=$(echo "$J" | jq -r .input_lra):measured_thresh=$(echo "$J" | jq -r .input_thresh):offset=$(echo "$J" | jq -r .target_offset):linear=true"
}
PRE="acompressor=threshold=0.1:ratio=4:attack=1:release=120:knee=4"
AF_SIN=$(ln2 audio/mezcla-sin-voz.wav -3 "$PRE"); AF_CON=$(ln2 audio/mezcla-con-voz.wav -1.5)
ffmpeg -y -v error -framerate 30 -i "$FR/f_%05d.jpg" -i audio/mezcla-sin-voz.wav -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p \
  -af "$AF_SIN" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$SIN"
ffmpeg -y -v error -i "$SIN" -i audio/mezcla-con-voz.wav -map 0:v -map 1:a -c:v copy -af "$AF_CON" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$CON"
ffmpeg -y -v error -i audio/mezcla-con-voz.wav -af "$AF_CON" -c:a aac -b:a 160k audio/mezcla-con-voz.m4a
for f in "$CON" "$SIN"; do
  echo "== $f"; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -show_entries format=duration -of compact "$f"
  ffmpeg -hide_banner -i "$f" -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p' | grep -E "I:|Peak:" | sed 's/Peak:/Pico real:/'
done
