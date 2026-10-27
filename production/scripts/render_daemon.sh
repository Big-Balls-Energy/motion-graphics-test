#!/bin/bash
# Cola de render continua: procesa los planos listados en el archivo de cola (uno por línea) en orden.
# Escribir "END" en la cola para terminar. Espera a que no haya otro render_shot.py en ejecución.
# Variables: PY, OUT, AMC_ASSETS, SCALE
QUEUE=$1
DONE="$QUEUE.done"
touch "$DONE"
cd "$(dirname "$0")"
while true; do
  next=$(grep -vxFf "$DONE" "$QUEUE" | head -1)
  if [ "$next" = "END" ]; then echo "=== ALL DONE $(date +%T)"; exit 0; fi
  if [ -z "$next" ] || pgrep -f "render_shot.py" > /dev/null; then sleep 15; continue; fi
  echo "=== $next start $(date +%T)"
  $PY render_shot.py "$next" --out "$OUT/$next" --scale "${SCALE:-0.75}" --assets "$AMC_ASSETS" 2>&1 \
    | grep -E "^frame|DONE|Error|Traceback"
  echo "$next" >> "$DONE"
  echo "=== $next end $(date +%T)"
done
