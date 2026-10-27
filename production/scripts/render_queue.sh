#!/bin/bash
# Renderiza planos en secuencia: render_queue.sh <escala> <shot1> [shot2 ...]
# Variables: PY (python con bpy), OUT (carpeta de frames), AMC_ASSETS (assets .npz)
SCALE=$1; shift
cd "$(dirname "$0")"
for s in "$@"; do
  echo "=== $s $(date +%T)"
  $PY render_shot.py "$s" --out "$OUT/$s" --scale "$SCALE" --assets "$AMC_ASSETS" 2>&1 | grep -E "^frame|DONE|Error|Traceback" | tail -n 2000
done
echo "=== QUEUE DONE $(date +%T)"
