#!/bin/bash
# Codifica la edición en dos versiones (H.264 CRF 19 yuv420p + AAC 192k 48 kHz, faststart), normalizadas a −14 LUFS en dos pasadas
# con pico real −1.5 dBTP:
#   · final:       voz + música original + efectos
#   · sin música:  voz + efectos (para poner encima un audio en tendencia de Instagram)
# También deja audio/mezcla-final.m4a, que usa index.html para reproducir con sonido en el navegador.
# Uso (desde la raíz del repo): bash agente-universidad/tools/codificar.sh <carpeta_cuadros>
# Requiere audio/mezcla-final.wav y audio/mezcla-sin-musica.wav (tools/audio.py).
set -e
cd "$(dirname "$0")/.."; FR=$(cd "$1" && pwd)
FIN=Atlas_Path_Agente_IA_Universidad.mp4; SIN=Atlas_Path_Agente_IA_Universidad-sin-musica.mp4
ln2() { # $1 archivo → filtro loudnorm de segunda pasada
  local J=$(ffmpeg -hide_banner -i "$1" -af "loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
  echo "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(echo "$J" | jq -r .input_i):measured_TP=$(echo "$J" | jq -r .input_tp):measured_LRA=$(echo "$J" | jq -r .input_lra):measured_thresh=$(echo "$J" | jq -r .input_thresh):offset=$(echo "$J" | jq -r .target_offset):linear=true"
}
AF_FIN=$(ln2 audio/mezcla-final.wav); AF_SIN=$(ln2 audio/mezcla-sin-musica.wav)
ffmpeg -y -v error -framerate 30 -i "$FR/f_%05d.jpg" -i audio/mezcla-final.wav -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p \
  -af "$AF_FIN" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$FIN"
ffmpeg -y -v error -i "$FIN" -i audio/mezcla-sin-musica.wav -map 0:v -map 1:a -c:v copy -af "$AF_SIN" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest "$SIN"
ffmpeg -y -v error -i audio/mezcla-final.wav -af "$AF_FIN" -c:a aac -b:a 160k audio/mezcla-final.m4a
for f in "$FIN" "$SIN"; do
  echo "== $f"; ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -show_entries format=duration -of compact "$f"
  ffmpeg -hide_banner -i "$f" -af ebur128=peak=true -f null - 2>&1 | sed -n '/Summary/,$p' | grep -E "I:|Peak:" | sed 's/Peak:/Pico real:/'
done
