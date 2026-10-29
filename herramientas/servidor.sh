#!/bin/bash
# Servidor local para ver o renderizar un reel (index.html carga módulos, fuentes y fotos: con file:// no funciona).
# Uso: bash herramientas/servidor.sh iniciar <carpeta_reel> [puerto=8811]
#      bash herramientas/servidor.sh detener [puerto=8811]
# Detiene por PID del proceso python: nunca uses «pkill -f» con un patrón que aparezca en tu propio comando
# (mata la terminal y el comando termina con código 144).
case "$1" in
  iniciar)
    DIR=$(cd "$2" && pwd); PORT=${3:-8811}
    bash "$0" detener "$PORT"
    # comando simple en segundo plano (sin subshell que se quede esperando con la salida abierta)
    setsid python3 -m http.server "$PORT" -d "$DIR" >/dev/null 2>&1 < /dev/null &
    for i in $(seq 1 30); do curl -s -o /dev/null "http://localhost:$PORT/index.html" && break; sleep 0.3; done
    if cmp -s <(curl -s "http://localhost:$PORT/index.html") "$DIR/index.html"; then echo "http://localhost:$PORT/index.html → $DIR"
    else echo "ERROR: el puerto $PORT no sirve $DIR"; exit 1; fi ;;
  detener)
    PORT=${2:-8811}
    for pid in $(ps -eo pid,comm,args | awk -v p="http.server $PORT" '$2 ~ /^python/ && index($0, p) {print $1}'); do kill "$pid"; done ;;
  *) echo "uso: servidor.sh iniciar <carpeta_reel> [puerto] | detener [puerto]"; exit 1 ;;
esac
