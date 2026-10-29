# Guía de producción de reels — Atlas Path

Esta guía reúne todo lo aprendido al producir los 15 reels de este repositorio (28–29 de octubre de 2026). Sirve para que una sesión nueva de Claude Code siga trabajando igual, sin repetir errores.

**Antes de empezar un reel nuevo:**
1. Lee esta guía completa.
2. Lee `CLAUDE.md`, que tiene las reglas fijas.
3. Abre como referencia el reel más reciente, `consejos-ia/`. Es la base técnica más completa.

---

## 0. Arranque rápido en una sesión nueva

```bash
cd /home/user/motion-graphics-test
git fetch origin prueba-social-reel && git checkout prueba-social-reel && git pull origin prueba-social-reel
node -e "require('playwright'); console.log('playwright ok')"
python3 -c "import numpy, scipy, PIL, cv2; print('python ok')"
ffmpeg -version | head -1 && jq --version
```

1. Todo el trabajo va en la rama `prueba-social-reel`. **No abras PR** salvo que el usuario lo pida.
2. Crea una lista de tareas (TaskCreate) con las fases de la sección 4.
3. Crea la carpeta del reel con la base técnica del último: `bash herramientas/nuevo_reel.sh <carpeta-del-reel>`.
4. Al terminar, siempre: commit + push, enviar archivos con SendUserFile y mensaje final en español con fuentes como enlaces Markdown.

---

## 1. El repositorio

```
motion-graphics-test/
├─ CLAUDE.md             reglas fijas de todos los reels (se cargan solas en cada sesión)
├─ GUIA-REELS.md         esta guía
├─ herramientas/         scripts de apoyo (sección 1.1)
├─ voz-tools/            colocar la voz de ElevenLabs (sección 1.2)
└─ <reel>/               un reel por carpeta (sección 8)
   ├─ index.html         la animación completa (canvas 2D + Three.js), determinista
   ├─ assets/            AtlasPath_logo.png y fotos/ con los nombres exactos del brief
   ├─ fonts/  vendor/    tipografías y Three.js r170 (todo local, sin CDN)
   ├─ audio/             voz-raw/tomas/, voz-en-off.wav, musica-sola.wav, efectos-solos.wav, mezclas, .m4a
   ├─ tools/             render.js, audio.py, guion.py, timeline.json, notas.md
   ├─ <nombre>.mp4 y <nombre>-sin-voz.mp4
   └─ guion-con-tiempos.md, subtitulos.srt (y README.md, portada.png, recursos/ si el brief los pide)
```

### 1.1 `herramientas/`

| Script | Para qué |
|---|---|
| `nuevo_reel.sh <carpeta> [base]` | Crea la carpeta de un reel con vendor/, fuentes, logo, `render.js`, `guion.py`, `audio.py` e `index.html` del reel base (por defecto `consejos-ia`). |
| `servidor.sh iniciar <carpeta> [puerto]` / `detener [puerto]` | Servidor local (las páginas no funcionan con `file://`). Verifica que el puerto sirva la carpeta correcta. |
| `hoja.py <capturas> <salida.jpg> [cols]` | Hoja de contacto de capturas `snap_*.png` para revisarlas con Read. |
| `hoja_cuadros.py <cuadros> <salida.jpg> t0:t1:paso` | Hoja de contacto del render completo (revisar el movimiento). |
| `tiempos_render.js <url> t1,t2` | Mide ms por cuadro para estimar el render. |
| `render_paralelo.sh <reel> <cuadros> <dur_s> [procesos=4] [puerto]` | Renderiza todos los cuadros con 4 Chromium en paralelo y comprueba que no falte ninguno. |
| `codificar.sh <reel> <cuadros> <con-voz.mp4> <sin-voz.mp4>` | MP4 con y sin voz a −14 LUFS (dos pasadas) y `audio/mezcla-con-voz.m4a`; imprime LUFS y pico real. |
| `silencios.sh <voz-en-off.wav>` | Silencios de la voz colocada: de ahí salen los tramos del karaoke. |
| `pistas_mudas.py <reel> <dur_s>` | Música y efectos mudos para correr `voz_tomas.py` antes de tener la música. |
| `fotos.py info / fondo-blanco / borrar / recortar` | Recortes, borrar logotipos y marcas de agua, recortar PNG transparentes. |

### 1.2 `voz-tools/`

| Script | Para qué |
|---|---|
| `bajar_tomas.py <status.json> <carpeta_tomas> 'pref0\|pref1\|…'` | Descarga las tomas de ElevenLabs de un resultado de `creative_get_flow_run_status` guardado en archivo. Las nombra `NN-1.mp3`, `NN-2.mp3` (+ `.id`). |
| `voz_tomas.py <reel>` | **El método vigente.** Coloca una toma por bloque en su ventana (`SLOTS`), recorta por energía, acorta solo silencios, fundidos de 10 ms, acelera máx. 10 % y mezcla con música y efectos. |
| `voz_mix.py` + `cues.json` | Método viejo (una narración larga cortada en pausas). **No usar**: cortaba palabras. |

### 1.3 Commits

- El mensaje va en español y describe el reel (ver plantilla en la sección 7).
- Sin identificadores de modelo en el mensaje.
- Termina con las líneas de atribución que indique el sistema en esa sesión (`Co-Authored-By: …` y `Claude-Session: …`).
- Push: `git push -u origin prueba-social-reel`. Si falla por red, reintenta con espera de 2, 4, 8 y 16 s.
- Hay un *hook* que avisa si quedan archivos sin subir: siempre termina con commit + push.

---

## 2. Reglas fijas de cada reel (lo que el usuario ya pidió y aprobó)

**Formato:** vertical 1080×1920, 30 fps, H.264 + AAC, duración exacta del brief (60, 75, 80 o 90 s). Se entregan dos versiones:
- con voz: `<reel>-con-voz.mp4`, o el nombre exacto que pida el brief, por ejemplo `Atlas_Path_5_Consejos_IA.mp4`;
- sin voz: `<reel>-sin-voz.mp4`.

**Marca de agua (siempre):**
- Logo oficial `assets/AtlasPath_logo.png`, arriba a la izquierda, 100×100 px.
- Opacidad 70 %, sobre placa clara redondeada en (40, 262), justo debajo de los 250 px superiores.
- El usuario pidió que sea discreta.
- Si el brief dice «si no adjunto el logo usa solo texto», igual se usa el logo oficial del repo (lo pide `CLAUDE.md`) y se le avisa al usuario.

**Cierre / CTA (siempre):**
- Logo grande en avatar circular, «ATLAS PATH», línea de servicios y **@Atlas_Path**.
- El usuario es **@Atlas_Path**, aunque el brief diga @ATLASPATH; se le avisa.
- Botón SEGUIR con cursor y clic, que pasa a «SIGUIENDO ✓».
- El último medio segundo regresa al primer cuadro (loop).

**Zonas seguras:** nada clave en los 250 px superiores, los 400 px inferiores (y > 1520) ni los 120 px de la derecha (x > 960).

**Subtítulos:**
- 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s.
- Karaoke: la palabra se ilumina al decirla, la palabra clave va en color de acento y las cifras en su color.
- Caja oscura semitransparente.
- 0.5 s sin subtítulo al final de cada escena.
- Se valida con `tools/guion.py`.

**Cifras y textos que se quedan solos:**
- Cada cifra clave y cada número de consejo se queda ≥ 2 s en pantalla.
- La frase clave y la palabra del CTA («IA», «WEB», «MENTE»…) se quedan ≥ 3 s solas, sin subtítulo encima.

**Voz:**
- ElevenLabs, «Fernanda – Smooth and Articulate» (`ARmPWZKt7WpXh6QDHA6x`), modelo `eleven_v4`, con etiquetas de tono.
- **Una toma independiente por bloque**; la narración nunca se corta después.
- Se acelera máx. 10 %. La mezcla final queda a −14 LUFS.
- El usuario la eligió porque «suena a narradora, no a IA»; pidió usarla en todo y sin fallos.

**Música:**
- Electrónica generada por código (sin derechos) a un BPM que cierre compases exactos.
- 15.5 % con texto, 19 % sin texto. Se apaga casi del todo justo antes de cada cifra y regresa con el golpe.
- Nunca tapa la voz: `voz_tomas.py` la baja 25 % mientras ella habla.

**Marcas y personas:**
- Sin logotipos, tipografías ni personajes reales: las marcas solo como texto.
- Las personas reales solo con las fotos que manda el usuario, sin retocar caras.
- Se borran logotipos de las fotos. Si una foto trae marca de agua de banco de imágenes, se borra si se puede y se avisa que conviene la versión con licencia.

**Datos:**
- Verificar todo antes de animarlo y no inventar cifras ni atribuciones.
- Estimaciones marcadas («estimación», «cifra reportada», «según X»).
- Lo futuro en condicional.
- Fuentes pequeñas abajo dentro de la zona segura (y ≈ 1502).

**Fotos que faltan:**
- Rectángulo gris con el nombre exacto, para que el usuario la reemplace.
- O un sustituto gráfico, si el brief lo permite.
- En los dos casos se avisa en el mensaje final.

**Entrega:**
- Envía con SendUserFile:
  - el MP4 con voz y la portada, con `display: render`;
  - el MP4 sin voz y el guion, con `display: attach`.
- Mensaje final en español:
  - qué se entregó y dónde (commit y rama);
  - qué se verificó;
  - decisiones que debe revisar;
  - fotos faltantes o con marca;
  - dominios bloqueados;
  - fuentes como enlaces Markdown.
- Avisa siempre que no viste el video de corrido ni escuchaste el audio, si es el caso.

**Si el brief dice «VERSIÓN: SIN VOZ»** (así eran los primeros briefs, para que el usuario grabe encima):
- no generes narración;
- respeta exactamente los tiempos de escena y las pausas de 0.5 s;
- deja la música más baja (10–15 %) donde hay más texto;
- entrega el guion limpio con marcas de tiempo (`guion-con-tiempos.md`) para leerlo mientras graba.

**Actitud:** el usuario pide «supera tus límites» y que cada reel sea mejor que el anterior. Hay que subir la calidad, pero siempre revisando cuadros reales antes de entregar.

---

## 3. El entorno (contenedor en la nube)

### Rutas

| Qué | Dónde |
|---|---|
| Repositorio | `/home/user/motion-graphics-test` |
| Imágenes que adjunta el usuario | `/root/.claude/uploads/<id-de-sesión>/<hash>-image.png` (el id cambia en cada sesión). Ábrelas una por una con Read para saber cuál es cuál (vienen en el orden en que las adjuntó) y cópialas con su nombre exacto. |
| Resultados grandes de herramientas MCP | Se guardan solos en `/root/.claude/projects/<proyecto>/<sesión>/tool-results/*.txt`; la ruta viene en el resultado. |
| Scratchpad (`<scratchpad>` en esta guía) | Carpeta temporal de la sesión; su ruta exacta viene en las instrucciones del sistema (algo como `/tmp/claude-0/…/scratchpad`). Ahí van capturas, cuadros y pruebas. No dejes ahí nada reutilizable: se pierde al cerrar la sesión (por eso existe `herramientas/`). |

### Instalado

- Node 22 con Playwright global: `require('playwright')` funciona desde cualquier carpeta; Chromium ya está instalado, **no corras `playwright install`**.
- ffmpeg 6.1, jq, Python con numpy, scipy, Pillow y OpenCV (`cv2`).
- 4 núcleos: 4 procesos de render en paralelo es lo óptimo.

### Tipografías instaladas

- **Inter** en todos los pesos, en `/usr/share/fonts/opentype/inter/` (Inter-Black.otf, Inter-Medium.otf…).
- **JetBrains Mono** en `/usr/share/fonts/truetype/jetbrains-mono/`.
- También DejaVu, Liberation y Noto.
- Para usarlas, cópialas a `<reel>/fonts/` y decláralas con `@font-face`.
- **Error de sesiones anteriores:** en dos reels se dijo que Inter no se podía descargar. Sí está instalada.

### Descargas (red con lista de permitidos)

**Funciona:**
- **npm**: `npm pack three@0.170.0` (Three.js) y `npm pack @fontsource/<fuente>` (fuentes de Google en woff2: Space Grotesk, Anton, Bebas Neue…).
- `fonts.googleapis.com` + `fonts.gstatic.com` para TTF:
  ```bash
  curl -sS "https://fonts.googleapis.com/css2?family=Montserrat:wght@600;800;900" -A "Mozilla/4.0" | grep -oE "url\([^)]+\)"
  ```
- Las URLs de descarga de ElevenLabs (`storage.googleapis.com`).

**No funciona:**
- `github.com/.../raw`, `cdn.jsdelivr.net` (403).
- Muchos sitios de noticias y empresas: WebFetch da `ENOTFOUND`.
- Para verificar datos usa **WebSearch**: modo `standard` y, si el resultado es pobre, `extended`.
- En el mensaje final, di qué dominios no se pudieron abrir y que el usuario puede agregarlos en *Allowed domains* de Network access (https://code.claude.com/docs/en/cloud-environments#network-access).
- Si surge una duda del entorno, consulta la herramienta `read_documentation` (tema `environment.network`).

### Procesos

- **Nunca** uses `pkill -f <patrón>` si el patrón aparece en tu propio comando: mata la terminal (código 144).
  - Usa `bash herramientas/servidor.sh detener 8811`.
  - O mata por PID: `ps -eo pid,comm,args | awk '$2 ~ /^python/ && /http\.server 8811/ {print $1}'`.
- **Nunca** lances un servidor con `(cd x && cmd &)` dentro de un script: queda un bash esperando con la salida abierta y el comando nunca termina. Usa `setsid python3 -m http.server PUERTO -d CARPETA >/dev/null 2>&1 < /dev/null &`, que ya hace `servidor.sh`.
- Un comando normal se corta a los 10 min. El render completo va con `run_in_background` y se espera la notificación.
  - Para esperar a algo corto, usa un `until …; do sleep 3; done` de menos de 10 min.

### Disco

- Cada cuadro JPEG pesa ~0.3 MB: 2400 cuadros ocupan ~0.75 GB.
- Renderiza en el scratchpad y borra carpetas de cuadros viejas.
- Si aparece «no space left», borra cuadros y renders de prueba.

---

## 4. Flujo completo, paso a paso

Orden probado (con los comandos exactos). En el reel `consejos-ia` todo esto tomó ~1.5 h.

### 4.1 Leer el brief y planear

Del brief saca:
- duración;
- escenas con sus tiempos;
- texto de la voz y textos en pantalla;
- cifras;
- **lista de imágenes con su nombre exacto y su uso** (recorte o fondo, y en qué segundos);
- objetos 3D pedidos;
- paleta, tipografías y audio;
- entregables extra: portada, PNG con transparencia, proyecto editable, README.

Haz la cuenta de tiempos:
- La voz de Fernanda va a ~2.6–3 palabras/s y los subtítulos a ≤ 2.3 palabras/s.
- **Los subtítulos casi siempre se condensan:** la voz dice el texto completo y el subtítulo una versión corta de 3–5 palabras.
- Los tiempos de escena **siguen a la voz**. Si se mueven respecto a la guía del brief, se avisa.

### 4.2 Verificar datos

- Busca cada cifra, fecha y atribución con WebSearch. Guarda las URL para el mensaje final y para `tools/notas.md`.
- Si algo no se confirma, reformúlalo sin perder impacto:
  - «hasta el doble», «más de», «≈», «según X», «cifra reportada»;
  - el ámbito exacto: «en tiendas de EE. UU.», «en productos de consumo»;
  - condicional para lo que no ha pasado.
- Una gráfica que solo tiene dos datos reales se rotula «trazo ilustrativo». Un medidor inventado se rotula «medidor ilustrativo».
- Nunca afirmes más de lo que dice la fuente. Ejemplo: tráfico desde IA no es igual a tráfico web total.

### 4.3 Voz por bloques en ElevenLabs

1. Divide la voz en bloques (una frase o golpe por bloque) y asigna a cada uno su ventana de tiempo.
2. Escribe el prompt:
   - números con letra («mil doscientos por ciento», «dos mil veinticuatro»);
   - marcas como se pronuncian;
   - etiquetas de tono suaves al inicio o a mitad de frase: `[curious]`, `[excited]`, `[warmly]`, `[intrigued]`, `[serious]`, `[dramatically]`;
   - puntos suspensivos para pausas naturales.
   - **No uses `[long pause]` para encadenar frases.**
3. Crea un flow por reel:
   ```
   mcp__ElevenLabs__creative_create_flow  {name: "Atlas Path · <reel> · voz por bloques", context: "…"}
   ```
4. Una llamada por bloque. Regresa al instante y genera 2 tomas. **No repitas una llamada para «reintentar»: cobra créditos otra vez.**
   ```
   mcp__ElevenLabs__creative_generate_speech {flow_id, voice_id: "ARmPWZKt7WpXh6QDHA6x", model_id: "eleven_v4",
                                              prompt: "[curious] ¿Creías que las páginas web estaban muriendo?", context: "Bloque 00 …"}
   ```
5. Espera a que termine:
   ```
   mcp__ElevenLabs__creative_get_flow_run_status {flow_id, session_ids: [...]}
   ```
   Repite cada `poll_after_seconds` hasta `all_completed`. El resultado es grande y se guarda en un archivo de `tool-results`.
6. Descarga con un fragmento de texto único por bloque, en orden:
   ```bash
   python3 voz-tools/bajar_tomas.py <archivo-tool-results.txt> <reel>/audio/voz-raw/tomas 'páginas web estaban|nueva razón|tiendas en línea|…'
   ```
7. Revisa la pronunciación de nombres propios (marcas, «Atlas Path», «Princeton»):
   ```
   mcp__ElevenLabs__creative_add_flow_asset_node {flow_id, generation_id, modality: "audio", label: "Bloque 18"}
   mcp__ElevenLabs__creative_transcribe_audio   {flow_id, model_id: "eleven_scribe_v1", connect_from: [<node_id>]}
   ```
   Lee la transcripción con `creative_get_flow_run_status`.
8. Si un bloque no cabe o suena mal:
   - rehaz solo ese bloque;
   - mueve las tomas viejas a `audio/voz-raw/descartadas/`;
   - si es una cifra, reescríbela para que suene justo cuando aparece en pantalla.

### 4.4 Colocar la voz (`voz_tomas.py`)

1. Agrega el reel a `SLOTS` en `voz-tools/voz_tomas.py`: una tupla `(inicio deseado, fin máximo)` por bloque, en el orden de las tomas.
   - **El fin del último slot define el largo del audio:** `N = ceil(último_fin + 0.6)` segundos.
   - Debe dar exactamente la duración del reel. Para 80 s el último fin es 79.4; con 79.45 sale 81 s y falla con *broadcast error*.
2. Si todavía no hay música:
   ```bash
   python3 herramientas/pistas_mudas.py <reel> <duración>
   ```
3. Corre:
   ```bash
   python3 voz-tools/voz_tomas.py <reel>
   ```
   Imprime una fila por bloque: inicio–fin, límite, tempo y OK/REVISAR. Al final debe decir `TODO OK`. De las dos tomas usa la que mejor cabe.
4. Si sale REVISAR: amplía la ventana, acorta el texto o rehaz la toma. Nunca pases de 10 % de aceleración.
5. Saca los silencios para el karaoke:
   ```bash
   bash herramientas/silencios.sh <reel>/audio/voz-en-off.wav
   ```
   Entre silencios está la voz. Para cada subtítulo anota `[voz desde, voz hasta]` en `SUBS_RAW`.

### 4.5 Fotos

1. Identifica cada imagen adjunta con Read y cópiala a `<reel>/assets/fotos/` con su **nombre exacto**:
   - fondos en `.jpg` (calidad 94);
   - recortes en `.png`.
2. Sin fondo, sobre blanco:
   ```bash
   python3 herramientas/fotos.py fondo-blanco entrada.png salida.png
   ```
   Conserva los blancos interiores, como la pantalla de un celular.
   - Para fondos de otro color: `bg_model` + `keep_largest` desde Python (`from herramientas.fotos import …`).
3. Logotipos, marcas y textos de marca:
   ```bash
   python3 herramientas/fotos.py borrar foto.jpg foto.jpg rect:562,993,624,1013 --sigma 4
   ```
   - Con `--sigma` grande el relleno jala colores lejanos, por ejemplo una pantalla blanca.
   - Revisa siempre un recorte ampliado (4×) del antes y el después con Read.
   - Si el logo toca piel u otro color, `smooth_fill` mancha. Usa máscaras por color: ver el arreglo de la tarjeta en W10 (sección 6, problema 16).
4. PNG con mucho margen transparente:
   ```bash
   python3 herramientas/fotos.py recortar entrada.png salida.png
   ```
5. Revisa todo:
   ```bash
   python3 herramientas/fotos.py info assets/fotos/*
   ```
6. **No retoques caras.** Una foto que parezca generada por IA va desenfocada de fondo.

**Integración en `index.html`** (`buildBG`, `buildCut`, `drawCut`):
- **Fondos:** desenfoque 8 px y 60 % más oscuros (`brightness(.4)`), gradación uniforme fría con toque cálido opcional por foto (`FONDOS[nombre].warm`), viñeta y zoom lento.
- **Recortes:** misma gradación, una sola luz principal arriba a la izquierda, *rim light* del color de acento en el borde derecho, sombra de silueta y sombra de contacto.

### 4.6 La animación (`index.html`)

Parte de `bash herramientas/nuevo_reel.sh <carpeta>`: copia `consejos-ia/index.html`. Conserva la infraestructura y reemplaza las escenas.

**Estructura del `<script type="module">`, en orden:**

1. **Bloque editable** al inicio:
   - `C`: colores.
   - `T`: todos los textos en pantalla.
   - `FONDOS`, `RECORTES`: fotos por nombre exacto.
   - `SCENES`: id, nombre, inicio, fin, descripción visual (va al guion).
   - `SUBS_RAW`: `[entra, sale, texto, [palabras clave], [voz desde, voz hasta]]`.
   - `HOLDS`: cifras y frases fijas; `sola: true` y `min: 3` para la frase y la palabra del CTA.
   - `SOURCES`, `METER` (si hay medidor), `sfx(t, tipo, volumen, tono)`, `window.TL` (con `musicDips` y `musicBoost` para el audio).
2. **Primitivas 2D:**
   - texto: `text`, `tw`, `fitSize`, `glowText`, `outlineNum` (número grande solo contorno con brillo);
   - figuras: `pill`, `hudFrame`, `icon` (íconos genéricos dibujados), `check`, `cursorArrow`;
   - efectos: `sparks`, `lensFlare`, `ring2D`, `godRays`, `motes`.
3. **Fotos:** `buildBG`, `fondo`, `buildCut`, `drawCut`, `placeholder`. Si es un celular: `SCR` (rectángulo de la pantalla en coordenadas de la foto), `drawPhone`, `phoneXf` e interfaces dibujadas dentro de la pantalla.
4. **Lienzos que se vuelven texturas:** sitios, tarjetas, fichas, calendarios, tableros. Se redibujan solo cuando cambia una clave (por ejemplo `T1KEY`), nunca en cada cuadro.
5. **Three.js:**
   - un renderer fuera de pantalla con `preserveDrawingBuffer`;
   - `draw3D(scene, cam, {glow, alpha, blur, zoom})` compone el 3D sobre el canvas 2D con *bloom* a media resolución y *zoom blur*;
   - helpers `proj`, `screenToZ`, `setCam`, `addLights`, `glassMat`, `reflMat`, `dissolveMat`, `pointsMat` / `makePts` / `morph` / `sampleScreen`, `makeCard`, `sprite`, `lines`, `path`.
6. **Escenas:** `buildX()` (construye una vez) + `sX(t)` (dibuja el segundo t), una por escena. La lista `DRAW` va en el mismo orden que `SCENES`.
7. **HUD:**
   - `tag` (chip arriba), `meter`, `tipHeader` (número de consejo grande que luego se encoge a una etiqueta), `sources`;
   - `subs` (karaoke con corte de línea equilibrado, sin dejar «y», «de», «un» al final de línea);
   - `post` (líneas de barrido, grano y viñeta), `shake`.
8. **`renderFrame(t)`:**
   - escena actual → loop: en los últimos 0.5 s funde hacia el cuadro 0;
   - después `post`, `sources`, `subs` y `hud` (marca de agua + barra de progreso).
9. **Opcional:**
   - `renderCover()`: portada 1080×1920;
   - `ASSETS` + `renderAsset(nombre)`: PNG transparentes. Revisa que cada función de `ASSETS` use objetos que todavía existan.
10. **Arranque:**
    - `window.ready` espera fuentes (`document.fonts.load`) e imágenes; después construye fondos, recortes y 3D y pone `window.isReady = true`;
    - con `?render=1` se oculta el botón de reproducir;
    - sin él, la página se reproduce con `audio/mezcla-con-voz.m4a`.

**Reglas de código:**
- **Determinista:** nada de `Math.random()` ni del reloj. Usa `rnd(i)` o `mulberry(semilla)`; `renderFrame(t)` depende solo de `t`. Así 4 procesos en paralelo dan el mismo video.
- Tiempos con helpers:
  - `p(t, a, b)` (0→1), `eo` / `eio` / `eback` (curvas), `bell`, `pop`;
  - `mono([[t, v], …])` para cámaras con varios puntos clave sin rebotes.
- Para poner un objeto 3D en un punto de la pantalla: `obj.position.copy(screenToZ(cam, x, y, z))`. Para poner texto 2D sobre un objeto 3D: `proj(vector, cam)`.

**Retícula de la pantalla** (coordenadas del canvas 1080×1920):

| Elemento | Posición |
|---|---|
| Marca de agua | x 40–140, y 262–362 |
| Chip de sección / etiqueta del consejo | y 404–456, centrado en x 500 |
| Medidor (si hay) | placa x 596–944, y 268–376 |
| Chip de dato (`tag`) | (160, 282) |
| Área visual principal | x 90–940, y ≈ 460–1330 |
| Número de consejo grande | número en y 510, título en 690, subtítulo en 746. **Mientras está grande, el contenido va debajo de y ≈ 790.** |
| Subtítulos | centro en y 1395 (caja ≈ 1342–1448); en el cierre, 1300 para no tapar el botón |
| Fuentes | y ≈ 1502 |
| Centro visual | x 500, no 540 (se deja libre la franja derecha de 120 px) |

**Transiciones:** usa una distinta por escena:
- destello blanco, *zoom blur*, iris circular, barrido radial, cortina que sube, giro;
- *dolly-zoom* (cambiar FOV mientras la cámara se acerca);
- partículas que se deshacen y se rearman, cámara que atraviesa el objeto.

Los movimientos rápidos van en las pausas de 0.5 s; con subtítulo, 3D lento.

### 4.7 Revisión visual (siempre, varias rondas)

```bash
bash herramientas/servidor.sh iniciar <reel> 8811
node <reel>/tools/render.js http://localhost:8811/index.html <scratchpad>/capturas snap 0.3,1.6,2.8,4.2   # una captura por segundo indicado
python3 herramientas/hoja.py <scratchpad>/capturas <scratchpad>/hoja.jpg 6                                   # y ábrela con Read
```

- Si la página no carga: `render.js` imprime `[err]` con el error de JavaScript.
- Para encontrar la línea, extrae el módulo y compílalo:
  ```bash
  python3 - <<'EOF'
  s=open('<reel>/index.html',encoding='utf-8').read(); a=s.index('<script type="module">')+22; b=s.index('</script>',a)
  open('<scratchpad>/mod.mjs','w',encoding='utf-8').write(s[a:b])
  EOF
  node --check <scratchpad>/mod.mjs
  ```
- El 404 de una foto faltante es normal (sale el marcador gris).

**Qué revisar en cada hoja** (los errores reales que aparecieron):
- [ ] Títulos encimados con el contenido 3D, sobre todo el número grande de cada consejo.
- [ ] Texto blanco sobre un panel blanco: usa placas o degradados oscuros detrás del texto.
- [ ] Objetos que se salen por la derecha (x > 960), por arriba (y < 250) o que tapan subtítulos.
- [ ] Cámara 3D demasiado cerca: objetos gigantes cortados. Aleja la cámara o reduce la escala.
- [ ] Partículas enormes cuando la cámara las atraviesa. Ya lo evita el `smoothstep` cerca de la cámara en `pointsMat`.
- [ ] Texto de partículas cortado: muéstrealo con `sampleScreen`, del tamaño exacto del texto final.
- [ ] Cifras legibles y quietas ≥ 2 s; frase y palabra del CTA ≥ 3 s solas.
- [ ] Etiquetas pegadas a íconos o a otras etiquetas.
- [ ] El último cuadro empata con el primero (loop).

Mide la velocidad para estimar el render:
```bash
node herramientas/tiempos_render.js http://localhost:8811/index.html 2,22,31,60
```
Cuadros de 300–1400 ms están bien.

### 4.8 Línea de tiempo y validación de subtítulos

`render.js` deja `timeline.json` en la carpeta de salida:

```bash
cp <scratchpad>/capturas/timeline.json <reel>/tools/timeline.json
cd <reel> && python3 tools/guion.py tools/timeline.json tools/notas.md
```

- Actualiza en `tools/guion.py` la lista `VOZ`, con los tiempos que imprimió `voz_tomas.py`.
- Escribe `tools/notas.md` con:
  - verificación de datos;
  - fotos y marcas;
  - tipografías;
  - fuentes con URL.
- La salida debe ser `fuera de regla: [] cifras cortas: [] solas con subtítulo: [] sin pausa: []`.
- `guion.py` escribe `guion-con-tiempos.md` y `subtitulos.srt`. El SRT trae los subtítulos y solo las frases «solas».
- Cada vez que cambies tiempos en `index.html`, vuelve a exportar `timeline.json` y a correr `guion.py` y `audio.py`.

### 4.9 Música y efectos (`tools/audio.py`)

1. Copia el del reel base y adapta:
   - `SEC`: secciones con su inicio, siguiendo el arco emocional del brief;
   - los acordes;
   - las curvas `*_g`;
   - los platillos y toms antes de cada número o cifra;
   - los *risers*;
   - las capas especiales (suspenso, «congelado»).
2. **El BPM cierra compases exactos:** `BPM = compases × 240 / duración`.
   - 39 compases en 80 s → 117 BPM;
   - 29 en 60 s → 116 BPM;
   - 39 en 90 s → 104 BPM.
   - Así el loop no salta.
3. **Cada tipo usado en `sfx(…)` debe existir en `GEN`**; si no, `KeyError`. Para ver los tipos:
   ```bash
   python3 -c "import json;print(sorted({e['type'] for e in json.load(open('tools/timeline.json'))['sfx']}))"
   ```
4. Corre:
   ```bash
   python3 tools/audio.py tools/timeline.json audio
   ```
   Escribe `musica-sola.wav`, `efectos-solos.wav` y `mezcla-sin-voz.wav`.
5. Luego, desde la raíz:
   ```bash
   python3 voz-tools/voz_tomas.py <reel>
   ```
   Rehace `voz-en-off.wav` y `mezcla-con-voz.wav` con la música real.

**Efectos ya hechos en `consejos-ia/tools/audio.py`, para reutilizar:**

| Grupo | Efectos |
|---|---|
| Interfaz | `whoosh`, `sweep`, `pop`, `tick`, `click`, `key`, `blip`, `lock`, `ping`, `send` |
| Golpes y acordes | `impact`, `hit`, `flash`, `chord`, `ding`, `chime`, `select` |
| Partículas y transformación | `scan`, `rise`, `assemble`, `morph`, `dissolve` |
| Ambiente | `pulse`, `paper`, `drone` |
| Consejos y conteos | `number` (acento de número), `count` (contador de 4 s), `meter` |
| Rastreador y puertas | `deny`, `unlock`, `door` |
| Calendario y edición | `flip`, `strike` |

En reels anteriores también hay `freeze`, `dolly`, `pass`, efectos de lata, vinilo, tanque, helicóptero, fichas, latido…: búscalos con `grep -n "def " */tools/audio.py`.

### 4.10 Render y codificación

```bash
# cuadros (en segundo plano: run_in_background; avisa al terminar)
bash herramientas/render_paralelo.sh <reel> <scratchpad>/cuadros <duración> 4 8811
# revisar el movimiento completo: hojas cada 0.5 s y abrirlas con Read
python3 herramientas/hoja_cuadros.py <scratchpad>/cuadros <scratchpad>/hoja_a.jpg 0:19.5:0.5
python3 herramientas/hoja_cuadros.py <scratchpad>/cuadros <scratchpad>/hoja_b.jpg 20:39.5:0.5   # … hasta el final
# MP4 con y sin voz a −14 LUFS
bash herramientas/codificar.sh <reel> <scratchpad>/cuadros <Nombre>.mp4 <Nombre>-sin-voz.mp4
```

Comprueba lo que imprime `codificar.sh`:
- `nb_frames` = duración × 30 y `duration` exacta;
- con voz: `I` ≈ −14 LUFS y pico real ≤ −1 dBFS;
- sin voz: ≈ −14 LUFS y ≈ −3 dBFS.

Los MP4 pesan ~50 MB (CRF 19).

### 4.11 Portada y recursos (si el brief los pide)

```bash
node <reel>/tools/render.js http://localhost:8811/index.html <reel> cover portada.png && rm <reel>/timeline.json   # render.js deja una copia de la línea de tiempo en la carpeta de salida
node <reel>/tools/render.js http://localhost:8811/index.html <reel>/recursos assets && rm <reel>/recursos/timeline.json
```

- **Portada:** tipográfica y minimalista, con el objeto principal.
- Revísala con Read: que el texto no toque la marca de agua y que no haya bordes duros en los degradados.

### 4.12 Documentos del reel

- `guion-con-tiempos.md` y `subtitulos.srt`: los genera `guion.py`.
- `README.md`, si el brief pide proyecto editable: qué editar en `index.html` y cómo renderizar (copia el de `consejos-ia/README.md`).
- Detén el servidor: `bash herramientas/servidor.sh detener 8811`.

### 4.13 Commit, push y entrega

```bash
git add <reel> voz-tools/voz_tomas.py   # voz_tomas cambia porque se agregó el SLOTS del reel
git commit -F mensaje.txt               # plantilla en la sección 7
git push -u origin prueba-social-reel
```

Después: SendUserFile y mensaje final (sección 7).

---

## 5. Recetario de técnicas (ver el código en `consejos-ia/index.html` salvo que se indique otro reel)

| Efecto | Cómo se hace | Dónde |
|---|---|---|
| Sitio que se desintegra «tipo Thanos» y se reconstruye | Shader `dissolveMat`: umbral = 0.62·(1−u) + 0.38·ruido por bloques. El ruido es una `DataTexture` generada en JS y las partículas usan el **mismo** ruido, así cada píxel que se apaga suelta su partícula. Borde cian. | `buildHook`, `hookFrame`, `HDIS` |
| Texto de partículas que se rompe y se recompone | Estados de partículas (`mkState`) + `morph(P, A, B, k, {turb, spread})`. Los textos se muestrean con `sampleScreen` (canvas del tamaño de la pantalla, al tamaño exacto del texto 2D final), así encajan con el texto nítido que aparece encima. La cámara atraviesa la nube. | `buildRev`, `sRevela` (también `ia-compras`) |
| Tarjetas que salen de la pantalla de un celular | Posición inicial = rectángulo de la tarjeta dentro de la pantalla (`phoneXf`) → `screenToZ`. Escala inicial igualada al ancho dibujado. | `sRevela` |
| Gráfica 3D de crecimiento | `TubeGeometry` sobre `CatmullRomCurve3` con `setDrawRange`, cortina de líneas, cabeza brillante. La cámara sigue la punta y se aleja (`setViewOffset` para bajar el encuadre). | `buildGraph`, `graphCam` |
| Barras de cristal con reflejo | `glassMat` (fresnel aditivo) + relleno + copia con `scale.y=-1` y `reflMat`. | `buildGraph` (también `ia-compras`) |
| Simulador de rastreador | Páginas 3D en fila con niebla, sonda de luz que recorre un `CatmullRomCurve3`. `getPoint(i/(n-1))` pasa exacto por cada página, con paradas definidas por `mono`. Barrido de escaneo, insignia ✓ y puerta con candado rojo → verde. | `buildT1`, `sT1` |
| Anillo de 100 segmentos (1 %) con *dolly-zoom* | `InstancedMesh` de segmentos con color por instancia. FOV = 2·atan(R·(H/2)/(radio_px·d)) mantiene el anillo del mismo tamaño mientras la cámara se acerca. | `makeRing`, `sT4` |
| Red de reputación | Nodos en un elipsoide, aristas por vecinos cercanos (kNN), rutas BFS hacia el centro que se iluminan, pulsos que viajan. Los nodos que caen sobre el HUD se descartan. | `buildT4` |
| Muro de cientos de sitios | `InstancedMesh` por variante de miniatura, color atenuado (0.42) para que destaque el elegido, recorrido de luz entre tarjetas. | `makeWall`, `sCta` |
| Árbol 3D del sitio | Nodos `RoundedBoxGeometry` + esferas, aristas curvas que se dibujan con `setDrawRange`, rama por rama. | `buildT5` |
| Número de consejo grande | `outlineNum` (solo contorno con brillo) ≥ 2 s; luego se encoge a una etiqueta `NN — TÍTULO` en y 404–456. | `tipHeader` |
| Medidor ilustrativo | Arco que sube por eventos (`METER`), destello al 100 %, con la etiqueta «medidor ilustrativo». | `meter` |
| Chat / comentarios en el celular | UI genérica dibujada en el rectángulo de pantalla de la foto (`SCR`), con muesca, tecleo letra por letra y cursor. | `drawPhone`, `screenChat`, `screenComments` |
| Palabra del CTA en grande | Sale del comentario del celular, crece a 330 px con anillos orbitando, destello y chispas, y se queda 3 s sola. | `sCta` |
| Cierre SEGUIR | Avatar con logo y anillo que pulsa, nombre, servicios, @Atlas_Path, botón con cursor, clic (onda) → «SIGUIENDO ✓». | `sCta` |
| Loop | En `renderFrame`, de 79.45 a 79.95 se funde hacia el cuadro 0 del gancho. | `renderFrame` |
| Más ejemplos 3D | Chip que se abre en capas, oblea, fábrica que se construye, Tierra con satélites, mapa holográfico. | `terafab/` |
| | Cerebro de cristal, túnel neuronal con cámara de montaña rusa, moléculas y sinapsis. | `neuroventas/` |
| | Globo de alambre con pines, siluetas, buscador → asistente. | `ia-compras/` |
| Técnica mixta 2D (fotos + motion) | Sombras proyectadas, 2.5D, papel rasgado, texturas. | `liquid-death/`, `brewdog/`, `dolor-pagar/`, `gary-vee/` |
| Ilustración plana y tipografía cinética | Montserrat, paleta crema. | `prueba-social/` y los primeros 7 reels |

---

## 6. Problemas conocidos y su solución

1. **La voz se cortaba a media palabra** (reel viral): una narración larga con `[long pause]` cortada después. **Solución:** una toma por bloque con `voz_tomas.py`. Nunca volver al método viejo.
2. **`voz_tomas.py` falla con *broadcast error* (shapes distintos):** el último `SLOTS` hace que el audio dure 1 s más que la música. Ajusta el último fin (duración − 0.6).
3. **Subtítulos que no cumplen la regla:** casi siempre el texto del brief es largo. Condensa el subtítulo; la voz dice la frase completa. `guion.py` lo valida.
4. **Contenido encimado con el número grande de cada consejo:** mientras está grande (2.25 s) el contenido va debajo de y ≈ 790; luego sube.
5. **Texto ilegible:** texto blanco sobre panel blanco o sobre una foto clara. Usa placas oscuras redondeadas o degradados detrás de títulos, etiquetas y medidor.
6. **Objetos fuera de zona segura o cortados:** cámara demasiado cerca o páginas muy separadas. Aleja la cámara (en el simulador: 8.4 detrás y 3.3 arriba de la sonda, FOV 46) y junta los objetos.
7. **Partículas gigantes al pasar la cámara:** en `pointsMat`, `vA = aA * smoothstep(.5, 2.8, -mv.z)` y tamaño máximo 160 px.
8. **Texto de partículas cortado o enorme:** muestrear un canvas chico con letra grande lo cortaba. Usa `sampleScreen` con el mismo tamaño y posición del texto 2D final.
9. **Signos ✓ ✕ sin glifo en la fuente:** dibuja el ícono (`check()`) o quita el signo.
10. **Error de sintaxis que no deja cargar la página** (`[err] Unexpected token`): extrae el módulo y corre `node --check` (sección 4.7).
11. **Propiedad pisada al combinar objetos:** `{lab, ...n}` reemplazó el sprite `lab` por el texto `n.lab`. Pon el *spread* primero: `{...n, m, lab}`.
12. **`renderAsset` o la portada fallan** porque usan objetos que ya se quitaron de una escena. Prueba `render.js … assets` y `cover` al final.
13. **La versión sin voz saturaba tras el AAC** (+0.4 dBTP): sin voz, los golpes quedan al frente. `codificar.sh` la comprime y la limita a −3 dBTP.
14. **Mover un objeto que la cámara sigue no lo mueve en pantalla:** si la cámara apunta al objeto, cambia el punto al que apunta (`target`), no el objeto.
15. **Fundir una tarjeta 3D:** el material del cuerpo es compartido. Usa `makeCard(tex, {own: true})` y `cd.fade(a)`.
16. **Borrar un logo que toca piel u otro color** (la tarjeta en W10): `smooth_fill` arrastró el color de la piel al dedo. **Solución:**
    - máscaras geométricas (elipses) + reglas de color: los píxeles oscuros de la marca → color de la tarjeta; los bordes rojizos → color de piel;
    - siempre partir del original subido, no de un intento previo;
    - revisar ampliado.
17. **Error en efectos de sonido (shapes al sumar arrays):** suma siempre con `add(buf, t, señal, ganancia)`, que recorta al largo del buffer.
18. **El comando se queda colgado:** servidor lanzado en un subshell (`(cd x && cmd &)`) que mantiene abierta la salida. Usa `servidor.sh`.
19. **`pkill -f` mató la terminal (código 144):** usa `servidor.sh detener` o mata por PID.
20. **WebFetch `ENOTFOUND`:** dominio no permitido por la red. Verifica con WebSearch y avisa al usuario qué dominios agregar.
21. **«Inter no se pudo descargar»** fue un error: está instalada en `/usr/share/fonts/opentype/inter/`.
22. **El primer cuadro tarda mucho** (2–3 s): compila los shaders; es normal.
23. **Cambios de tiempos sin reexportar:** `guion.py` y `audio.py` leen `tools/timeline.json`. Reexporta tras cada cambio de tiempos o de `sfx`.
24. **Dos fuentes no coinciden en una cifra:** usa la conservadora, marca «≈» o «cifra reportada» y explícalo en `notas.md`.

---

## 7. Plantillas

### Mensaje de commit

```
Reel <título corto>: <duración> s en Three.js con <2–3 rasgos visuales> y voz de Fernanda

- <reel>/index.html: <escenas y objetos 3D principales>
- Datos verificados: <fuentes principales y cifras>
- Música a <BPM> BPM (<compases> compases, loop exacto), efectos sincronizados, voz por bloques y mezclas a −14 LUFS; videos con y sin voz
- Fotos <rango> con marcas quitadas; <foto faltante> queda como marcador gris con su nombre
- voz_tomas.py: tiempos del reel <reel>

<líneas de atribución que indique el sistema en la sesión>
```

### Mensaje final al usuario (en español)

```
El reel «<título>» ya está terminado y exportado como MP4. Te lo envié aquí con <archivos>. Todo está subido a la rama
`prueba-social-reel` (commit `<hash>`); no abrí PR.

**Lo que entrego** (en `<reel>/`)
- `<Nombre>.mp4`: <dur> s, 1080×1920, 30 fps, H.264 + AAC, subtítulos quemados, voz de Fernanda, −14.x LUFS.
- `<Nombre>-sin-voz.mp4`: …
- <portada, recursos, proyecto editable, guion, SRT>

**Revisiones**
- <reglas de subtítulos, cifras ≥ 2 s, frase/palabra ≥ 3 s, voz dentro de su tiempo (aceleración máx.), BPM y loop>

**Lo que debes revisar**
- <fotos faltantes y cómo reemplazarlas>
- <logo / usuario @Atlas_Path / tipografía>
- <marcas quitadas de las fotos y fotos con marca de agua de banco>
- <datos reformulados y por qué>
- <tiempos que cambiaron respecto a la guía>
- <dominios que no se pudieron abrir + enlace a Allowed domains>

**Fuentes**
- [Título](URL)
```

---

## 8. Índice de reels hechos (para reutilizar)

| Carpeta | Dur. | BPM | Técnica | Qué reutilizar |
|---|---|---|---|---|
| `prueba-social/` | 60 s | 104 | 2D plano, tipografía cinética, Montserrat, crema/naranja | Primer reel; CTA con contador de seguidores |
| `aversion-perdida/` | 60 s | 106 | 2D plano | Moneda, reloj, cifras verdes y rojas |
| `reciprocidad/` | 60 s | 102 | 2D plano | Mesero animado, caja de regalo en el CTA |
| `tesla-robotaxi/` | 60 s | 116 | 2D oscuro tecnológico | «Última hora», letra chiquita con avisos |
| `reel-viral/` | 60 s | 112 | 2D autodemostrativo | Chip de sección, línea de tiempo, el video se cita a sí mismo |
| `arquetipos/` | 60 s | 104 | 2D, cartas que se voltean | 12 cartas × 2 s; primera voz de Fernanda |
| `viaje-heroe/` | 60 s | 104 | 2D, mapa de aventura | Primer reel con tomas por bloque desde el inicio |
| `liquid-death/` | 60 s | 132 | Técnica mixta, fotos de latas | Estética punk editorial, Anton y Bebas Neue |
| `brewdog/` | 60 s | 140 | Técnica mixta | Línea de valor, caída en rojo, efectos de quemado |
| `dolor-pagar/` | 60 s | 104 | Técnica mixta | Medidor de dolor, pantalla dividida, carrusel con parallax |
| `gary-vee/` | 75 s | 98 | Técnica mixta, caso de éxito | Radar de atención, tarjetas de clientes, mapa con pin |
| `terafab/` | 90 s | 117 | **Three.js** + fotos | Primer 3D: chip, oblea, fábrica, Tierra, cámara montaña rusa |
| `neuroventas/` | 90 s | 104 | Three.js | Cerebro de cristal, túnel, moléculas, ecualizador |
| `ia-compras/` | 60 s | 116 | Three.js | Globo, partículas que forman cifras, asistente, anillo 1 %, muro |
| `consejos-ia/` | 80 s | 117 | Three.js (base más completa) | Disolución por bloques, simulador, medidor, portada, recursos PNG, README editable |
