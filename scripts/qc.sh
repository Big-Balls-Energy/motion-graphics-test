#!/usr/bin/env bash
# Control de calidad del MP4 final
set -e
F=${1:-out/AtlasPath_MetaAds2026_40s.mp4}
ffprobe -v error -show_entries format=duration,size,bit_rate -show_entries stream=codec_name,profile,width,height,r_frame_rate,nb_frames,pix_fmt,sample_rate,channels,duration -of default=nw=1 "$F"
echo "--- frames decodificados:"; ffprobe -v error -count_frames -select_streams v:0 -show_entries stream=nb_read_frames -of csv=p=0 "$F"
echo "--- detección de cuadros negros (>0.3 s):"; ffmpeg -hide_banner -i "$F" -vf blackdetect=d=0.3:pix_th=0.06 -an -f null - 2>&1 | grep blackdetect || echo "ninguno"
echo "--- congelamientos (>0.8 s):"; ffmpeg -hide_banner -i "$F" -vf freezedetect=n=0.0008:d=0.8 -an -f null - 2>&1 | grep freeze_ || echo "ninguno"
echo "--- loudness:"; ffmpeg -hide_banner -i "$F" -af loudnorm=print_format=summary -vn -f null - 2>&1 | grep -E "Input Integrated|Input True Peak"
