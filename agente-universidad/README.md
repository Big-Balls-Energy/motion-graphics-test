# Agente de IA para una universidad — edición con motion graphics (Atlas Path)

Edición del video de contenido (persona hablando a cámara) para Instagram, pensada para retener y compartir: gancho desde el primer cuadro, algo nuevo cada 2–3 s, subtítulos palabra por palabra, gráficos que muestran al agente trabajando, un resumen para guardar y un final que regresa al inicio (loop). 1080×1920, 30 fps, 54.6 s.

## Entregables

| Archivo | Qué es |
|---|---|
| `Atlas_Path_Agente_IA_Universidad.mp4` | Video final: voz original + música original + efectos, −14 LUFS |
| `Atlas_Path_Agente_IA_Universidad-sin-musica.mp4` | Igual, sin música (voz + efectos), para poner encima un audio en tendencia desde Instagram |
| `portada.png` | Portada (primer cuadro, con el gancho «¿PIERDES VENTAS?») |
| `guion-con-tiempos.md` | Secciones, gráficos y subtítulos con tiempos, y la transcripción |
| `subtitulos.srt` | Subtítulos (también van quemados en el video) |
| `audio/` | Voz, música, efectos y mezclas por separado |
| `fuente/video_original.mp4` | El video que se editó |

## Qué se hizo

- **Ritmo:** se quitaron las pausas de más de 0.22 s sin cortar palabras (55.77 s → 54.57 s); cada corte alterna zoom medio y cerrado para que no se note el salto.
- **Cámara:** encuadre estable centrado en la cara (detector YuNet) y compuesto por sección: ella a la izquierda cuando los gráficos van a la derecha y al revés, para no taparle nunca la cara. Zoom máximo 1.32×.
- **Profundidad:** con el recorte de la persona (Robust Video Matting) los títulos «¿PIERDES VENTAS?», «AGENTE IA» y «LO MÁS IMPORTANTE» pasan detrás de su cabeza.
- **Gráficos** (diseño propio, sin logotipos de apps reales): notificaciones sin responder, contador 99+, gráfica de ventas, tareas que se amontonan, etiqueta de Atlas Path, «CASO REAL · UNIVERSIDAD», chat del agente, base de datos, visita agendada, sistema del equipo comercial, lista «TU AGENTE IA», sello «VENTA CERRADA», toque en pantalla y tarjeta de cierre con SEGUIR → SIGUIENDO ✓.
- **Ilustrativo:** los nombres de las notificaciones, la conversación del chat (carrera «Ingeniería», visita «jueves 10:00»), los datos enmascarados y el tablero son ejemplos visuales, no datos del cliente. No se muestra ninguna cifra.
- **Subtítulos:** literales (transcripción de ElevenLabs Scribe con tiempo por palabra; «Atlas Pad» corregido a «Atlas Path»), en bloques de 1–5 palabras, con la palabra clave en amarillo y algún emoji. Como ella habla a ~3.3 palabras/s, no aplica el tope de 2.3 palabras/s de los reels narrados.
- **Marca:** logo de Atlas Path como marca de agua (40, 262; 100 px; 70 %) y cierre con logo, @Atlas_Path, ESCRÍBENOS y SEGUIR; el último medio segundo regresa al primer cuadro.
- **Audio:** voz original recortada con los mismos tramos (cruces de 6 ms), sin graves de ruido y nivelada; música house/pop original a 123 BPM (28 compases: el loop cierra) y efectos propios. La voz queda en promedio 22 dB por encima de la música y los efectos en la banda de la palabra (nunca menos de 3.4 dB).

## Cómo se reproduce

Requisitos: Node + Playwright con Chromium, Python 3 con numpy, scipy, OpenCV y onnxruntime, ffmpeg y jq. Desde `agente-universidad/`:

```bash
W=/tmp/agente; M=/tmp/modelos
python3 tools/preprocesar.py fuente/video_original.mp4 $W $M     # cuadros, cortes, cara y matte (descarga YuNet y RVM)
ln -sfn $W/src src; ln -sfn $W/mat mat                            # la página los lee desde aquí (no se versionan)
python3 tools/plan.py                                             # ritmo, encuadre y subtítulos → tools/plan.js
bash ../herramientas/render_paralelo.sh agente-universidad /tmp/cuadros 54.567 4 8812   # 1637 cuadros
cp /tmp/cuadros/timeline.json tools/timeline.json
python3 tools/audio.py tools/plan.json tools/timeline.json audio
bash tools/codificar.sh /tmp/cuadros
python3 tools/guion.py
```

`tools/transcripcion_palabras.json` es la transcripción de Scribe (costó unos 307 créditos de ElevenLabs); no hace falta repetirla.
Modelos: YuNet (OpenCV Zoo) y Robust Video Matting (GPL-3.0); se descargan al correr `preprocesar.py` y no se guardan en el repositorio.

## Qué se puede editar (al inicio del `<script>` de `index.html`)

- **Textos:** objeto `T`. **Colores:** objeto `C`. **Tiempos de cada gráfico:** objeto `S`, anclado a las palabras (`ws(i)` = cuando empieza la palabra `i`).
- **Golpes de zoom:** `EMPH` (índices de palabras). **Transiciones:** `TR`. **Efectos de sonido:** las llamadas `sfx(...)`.
- **Encuadre por sección:** `LAYOUT` en `tools/plan.py`. **Palabras clave y emojis de los subtítulos:** `KEY` y `EMOJI` en `tools/plan.py`.
