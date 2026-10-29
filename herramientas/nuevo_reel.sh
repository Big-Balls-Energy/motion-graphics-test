#!/bin/bash
# Crea la carpeta de un reel nuevo con la base técnica de un reel anterior: Three.js r170 (vendor/), fuentes, logo oficial,
# tools/render.js, tools/guion.py, tools/audio.py e index.html como punto de partida (sus escenas se reemplazan).
# Uso: bash herramientas/nuevo_reel.sh <carpeta_nueva> [reel_base=consejos-ia]
set -e
cd "$(dirname "$0")/.."; NEW=$1; BASE=${2:-consejos-ia}
[ -n "$NEW" ] || { echo "uso: nuevo_reel.sh <carpeta_nueva> [reel_base]"; exit 1; }
[ -e "$NEW" ] && { echo "ya existe $NEW"; exit 1; }
mkdir -p "$NEW"/{assets/fotos,audio/voz-raw/tomas,fonts,tools,vendor}
cp -r "$BASE"/vendor/* "$NEW"/vendor/; cp "$BASE"/fonts/* "$NEW"/fonts/; cp "$BASE"/assets/AtlasPath_logo.png "$NEW"/assets/
cp "$BASE"/tools/{render.js,guion.py,audio.py} "$NEW"/tools/; cp "$BASE"/index.html "$NEW"/index.html
echo "Listo: $NEW. index.html, tools/guion.py y tools/audio.py vienen de $BASE: hay que adaptarlos al reel nuevo."
