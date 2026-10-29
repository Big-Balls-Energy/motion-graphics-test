#!/bin/bash
# Renderiza todos los cuadros de un reel (f_00000.jpg …, JPEG 95 %, 30 fps) con varios Chromium en paralelo.
# Uso: bash herramientas/render_paralelo.sh <carpeta_reel> <carpeta_cuadros> <duración_s> [procesos=4] [puerto=8811]
# Tarda ~0.3–1.4 s por cuadro en cada proceso: 80 s (2400 cuadros) con 4 procesos ≈ 10–15 min.
# Desde Claude Code córrelo con run_in_background (el límite de un comando normal es 10 min) y espera el aviso.
set -e
H=$(cd "$(dirname "$0")" && pwd); REEL=$(cd "$1" && pwd); OUT=$2; DUR=$3; P=${4:-4}; PORT=${5:-8811}
TOTAL=$(python3 -c "print(round($DUR * 30))"); mkdir -p "$OUT"; rm -f "$OUT"/f_*.jpg "$OUT"/log_*.txt
bash "$H/servidor.sh" iniciar "$REEL" "$PORT"
STEP=$(( (TOTAL + P - 1) / P )); pids=()
for ((i = 0; i < P; i++)); do
  a=$((i * STEP)); b=$(( (i + 1) * STEP < TOTAL ? (i + 1) * STEP : TOTAL ))
  node "$REEL/tools/render.js" "http://localhost:$PORT/index.html" "$OUT" frames $a $b > "$OUT/log_$a.txt" 2>&1 & pids+=($!)
done
for p in "${pids[@]}"; do wait "$p" || true; done
N=$(ls "$OUT"/f_*.jpg 2>/dev/null | wc -l); echo "cuadros: $N de $TOTAL"
grep -h "\[err\]" "$OUT"/log_*.txt | sort | uniq -c | head || true
[ "$N" -eq "$TOTAL" ] || { echo "FALTAN CUADROS: revisa $OUT/log_*.txt"; exit 1; }
