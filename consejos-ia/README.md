# 5 consejos para que una IA recomiende tu negocio — Atlas Path

Reel de 80 s, 1080×1920, 30 fps. Todo el video sale de `index.html` (Three.js + canvas, determinista: el mismo segundo siempre da el mismo cuadro).

## Entregables

| Archivo | Qué es |
|---|---|
| `Atlas_Path_5_Consejos_IA.mp4` | Video final con voz: H.264, AAC, subtítulos quemados, −14 LUFS |
| `Atlas_Path_5_Consejos_IA-sin-voz.mp4` | Mismo video con música y efectos, sin voz |
| `portada.png` | Portada del reel, 1080×1920 |
| `recursos/*.png` | Objetos 3D y elementos sueltos con fondo transparente |
| `guion-con-tiempos.md` | Guion, tiempos de cada bloque, verificación de datos y fuentes |
| `subtitulos.srt` | Subtítulos (también van quemados en el video) |
| `audio/` | Voz, música, efectos y mezclas por separado |

## Ver la animación en el navegador

```bash
cd consejos-ia
python3 -m http.server 8811
# abrir http://localhost:8811/  (clic para reproducir con audio · F pantalla completa · Espacio pausa · R reiniciar)
```

## Qué se puede editar (todo está al inicio del `<script>` de `index.html`)

- **Textos en pantalla**: objeto `T` (títulos, cifras, etiquetas, nombre del negocio, usuario, CTA, portada).
- **Colores**: objeto `C` (#05080F, #07182D, #1479FF, #22D3EE, #FFFFFF, #A9B4C4 y ámbar #F59E0B solo para cifras).
- **Escenas y duración**: `SCENES` (inicio y fin de cada escena) y `DUR`. Los tiempos siguen a la voz; si los mueves, ajusta también `SUBS_RAW` y los `SLOTS` de `voz-tools/voz_tomas.py`.
- **Subtítulos**: `SUBS_RAW` = `[entra, sale, texto, palabras clave, [voz desde, voz hasta]]` (el karaoke sigue a la voz).
- **Cifras y frases fijas**: `HOLDS` (`sola: true` = sin subtítulo encima; `min` = segundos mínimos).
- **Fuentes en pantalla**: `SOURCES`. **Medidor ilustrativo**: `METER`. **Efectos de sonido**: las llamadas `sfx(tiempo, tipo, volumen, tono)`.
- **Fotos**: `assets/fotos/<NOMBRE EXACTO>`. Para cambiar una foto basta con reemplazar el archivo con el mismo nombre.
  `W05_barista_sirviendo.jpg` no se adjuntó: mientras falte, el consejo 03 muestra un rectángulo gris con su nombre.

Después de editar, valida los subtítulos (3–5 palabras, ≥ 1.5 s, ≤ 2.3 palabras/s, cifras ≥ 2 s, frase clave y WEB ≥ 3 s solas, 0.5 s de pausa entre escenas):

```bash
node tools/render.js http://localhost:8811/index.html /tmp/tl snap 0 && cp /tmp/tl/timeline.json tools/timeline.json
python3 tools/guion.py tools/timeline.json tools/notas.md      # escribe guion-con-tiempos.md y subtitulos.srt
```

## Renderizar el video

Requisitos: Node + Playwright con Chromium, Python 3 con numpy y scipy, ffmpeg.

```bash
cd consejos-ia && python3 -m http.server 8811 &
# 1) cuadros (2400 = 80 s × 30 fps), en 4 procesos en paralelo
for r in "0 600" "600 1200" "1200 1800" "1800 2400"; do set -- $r
  node tools/render.js http://localhost:8811/index.html /tmp/cuadros frames $1 $2 & done; wait
# 2) música y efectos (117 BPM, 39 compases: el loop cierra) y voz por bloques
python3 tools/audio.py tools/timeline.json audio
cd .. && python3 voz-tools/voz_tomas.py consejos-ia && cd consejos-ia
# 3) codificar con normalización a −14 LUFS en dos pasadas
ln2(){ J=$(ffmpeg -hide_banner -i "$1" -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
  echo "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$(echo "$J"|jq -r .input_i):measured_TP=$(echo "$J"|jq -r .input_tp):measured_LRA=$(echo "$J"|jq -r .input_lra):measured_thresh=$(echo "$J"|jq -r .input_thresh):offset=$(echo "$J"|jq -r .target_offset):linear=true"; }
AF2=$(ln2 audio/mezcla-con-voz.wav)
# la versión sin voz tiene más picos (efectos sin voz que los cubra): se comprime antes y se limita a −3 dBTP para que el AAC no sature
PRE="acompressor=threshold=0.1:ratio=4:attack=1:release=120:knee=4"
J=$(ffmpeg -hide_banner -i audio/mezcla-sin-voz.wav -af "$PRE,loudnorm=I=-14:TP=-3:LRA=11:print_format=json" -f null - 2>&1 | sed -n '/^{/,/^}/p')
AF1="$PRE,loudnorm=I=-14:TP=-3:LRA=11:measured_I=$(echo "$J"|jq -r .input_i):measured_TP=$(echo "$J"|jq -r .input_tp):measured_LRA=$(echo "$J"|jq -r .input_lra):measured_thresh=$(echo "$J"|jq -r .input_thresh):offset=$(echo "$J"|jq -r .target_offset):linear=true"
ffmpeg -framerate 30 -i /tmp/cuadros/f_%05d.jpg -i audio/mezcla-sin-voz.wav -c:v libx264 -preset slow -crf 19 -pix_fmt yuv420p \
  -af "$AF1" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest Atlas_Path_5_Consejos_IA-sin-voz.mp4
ffmpeg -i Atlas_Path_5_Consejos_IA-sin-voz.mp4 -i audio/mezcla-con-voz.wav -map 0:v -map 1:a -c:v copy \
  -af "$AF2" -c:a aac -b:a 192k -ar 48000 -movflags +faststart -shortest Atlas_Path_5_Consejos_IA.mp4
# 4) portada y recursos con transparencia
node tools/render.js http://localhost:8811/index.html . cover portada.png
node tools/render.js http://localhost:8811/index.html recursos assets
```

## Estructura

```
consejos-ia/
├─ index.html          animación completa (escenas, 3D, HUD, subtítulos, portada y recursos)
├─ assets/             logo oficial de Atlas Path y fotos W01–W10 (W05 pendiente)
├─ fonts/  vendor/     Space Grotesk, JetBrains Mono y Three.js r170 (sin dependencias en línea)
├─ audio/              voz-en-off.wav, musica-sola.wav, efectos-solos.wav, mezclas y tomas de voz (voz-raw/tomas)
├─ tools/              render.js, audio.py, guion.py, notas.md, timeline.json
├─ recursos/           PNG con transparencia de los objetos 3D
└─ portada.png, guion-con-tiempos.md, subtitulos.srt, videos MP4
```
