# Ocarina of Time: la nostalgia es tu mejor arma — Atlas Path

Reel de 90 s, 1080×1920, 30 fps, en tres actos y un epílogo. El avatar Guillermo Arcos presenta y es el héroe, con la voz de Joaquín («Rich and Captivating», ElevenLabs `eleven_v4`). Todo el video sale de `index.html` (Three.js + canvas, determinista: el mismo segundo siempre da el mismo cuadro).

## Entregables

| Archivo | Qué es |
|---|---|
| `Atlas_Path_Ocarina_Nostalgia.mp4` | Video final con voz: H.264, AAC, subtítulos quemados, −14 LUFS |
| `Atlas_Path_Ocarina_Nostalgia-sin-voz.mp4` | Mismo video con música y efectos, sin voz |
| `portada.png` | Portada del reel, 1080×1920 |
| `guion-con-tiempos.md` | Guion, tiempos de cada bloque, verificación de datos y fuentes |
| `subtitulos.srt` | Subtítulos (también van quemados en el video) |
| `audio/` | Voz por bloques, música, efectos y mezclas por separado |

## Ver la animación en el navegador

```bash
cd ocarina-nostalgia
python3 -m http.server 8811
# abrir http://localhost:8811/  (clic para reproducir con audio · F pantalla completa · Espacio pausa · R reiniciar)
```

## Fotos que faltan

`Z06_bosque_neblina.jpg`, `Z07_cueva_antorchas.jpg` y `Z08_polaroids.png` no se adjuntaron: mientras falten, se ve un rectángulo gris con su nombre exacto. Para ponerlas basta copiarlas en `assets/fotos/` con ese nombre y volver a renderizar. Las fotos del avatar se usan tal cual (solo escala, posición, volteo, sombra y luz).

## Qué se puede editar (todo está al inicio del `<script>` de `index.html`)

- **Textos en pantalla**: objeto `T` (cifras, ventanas emergentes, títulos de acto, mapa, cintillo, CTA, leyenda y portada).
- **Colores**: objeto `C`: acto 1 `a1` #1B1036 con `gold` #F5C542, `pink` #FF3EA5 y `cyan` #3EF2FF; acto 2 `a2` #0B1530 y `teal` #22D3EE; acto 3 `gray`, `black`, `warm` y `torch`; epílogo `dawn` y `cream`.
- **Escenas y duración**: `SCENES` y `DUR`. Los tiempos siguen a la voz; si los mueves, ajusta también `SUBS_RAW` y los `SLOTS` de `voz-tools/voz_tomas.py`.
- **Subtítulos**: `SUBS_RAW` = `[entra, sale, texto, palabras clave, [voz desde, voz hasta]]` (el karaoke sigue a la voz).
- **Cifras y títulos fijos**: `HOLDS` (`sola: true` = sin subtítulo encima; `min` = segundos mínimos).
- **Fuentes en pantalla**: `SOURCES`. **Poses del avatar**: `AVS`. **Efectos de sonido**: las llamadas `sfx(tiempo, tipo, volumen, tono)`.

Después de editar, valida los subtítulos (3–5 palabras, ≥ 1.5 s, ≤ 2.3 palabras/s, cifras ≥ 2 s solas, «NOSTALGIA» ≥ 3 s, 0.5 s de pausa entre escenas):

```bash
node tools/render.js http://localhost:8811/index.html /tmp/tl snap 0 && cp /tmp/tl/timeline.json tools/timeline.json
python3 tools/guion.py tools/timeline.json tools/notas.md      # escribe guion-con-tiempos.md y subtitulos.srt
```

## Renderizar el video

Requisitos: Node + Playwright con Chromium, Python 3 con numpy y scipy, ffmpeg. Desde la raíz del repositorio:

```bash
bash herramientas/render_paralelo.sh ocarina-nostalgia /tmp/cuadros 90 4 8811        # 2700 cuadros
python3 ocarina-nostalgia/tools/audio.py ocarina-nostalgia/tools/timeline.json ocarina-nostalgia/audio
python3 voz-tools/voz_tomas.py ocarina-nostalgia                                     # voz por bloques + mezcla
bash herramientas/codificar.sh ocarina-nostalgia /tmp/cuadros Atlas_Path_Ocarina_Nostalgia.mp4 Atlas_Path_Ocarina_Nostalgia-sin-voz.mp4
node ocarina-nostalgia/tools/render.js http://localhost:8811/index.html ocarina-nostalgia cover portada.png
```

La música es original (101.33 BPM, 38 compases: el loop cierra): chiptune en el acto 1, orquesta en el acto 2, batalla con 1 s de silencio total antes del golpe final en el acto 3 y tema heroico con fanfarria en el epílogo.

Caso de estudio. Sin afiliación con Nintendo. Las marcas mencionadas pertenecen a sus dueños.
