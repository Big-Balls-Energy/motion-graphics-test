#!/bin/bash
# Lista los silencios de la voz ya colocada (inicio-fin, en segundos). Entre silencios está lo que se oye:
# de ahí salen los tramos [voz desde, voz hasta] del karaoke de cada subtítulo en SUBS_RAW.
# Uso: bash herramientas/silencios.sh <reel>/audio/voz-en-off.wav
ffmpeg -hide_banner -i "$1" -af silencedetect=n=-38dB:d=0.11 -f null - 2>&1 | grep -o "silence_\(start\|end\): [0-9.]*" | paste - - | awk '{printf "%s-%s  ", $2, $4} END {print ""}'
