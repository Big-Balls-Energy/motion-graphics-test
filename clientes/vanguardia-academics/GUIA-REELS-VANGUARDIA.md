# Guía de producción de reels — Vanguardia Academics

Esta guía adapta el método de producción de reels de Atlas Path (15 reels hechos en `prueba-social-reel`) a la marca del cliente **Vanguardia Academics** (viajes educativos al extranjero a la medida, @vanguardia.academics). La técnica, los scripts y los problemas conocidos son los mismos; cambian la marca, la paleta, el cierre, la voz y las reglas de contenido.

**Antes de empezar un reel nuevo:**
1. Lee esta guía completa.
2. Lee `clientes/vanguardia-academics/guia_prompts_reels_vanguardia_academics.md`, **sobre todo la sección 0** (educar, seguridad y experiencia sin decir «somos los mejores», discreción total con sus clientes, acción social), y `marca/INVENTARIO-FOTOS.md` (qué foto se puede usar y cómo).
3. Lee `CLAUDE.md` de la rama: sus reglas técnicas valen; **sus reglas de marca de Atlas Path (logo, @Atlas_Path, cierre) se reemplazan por las de la sección 2 de esta guía**.
4. Abre como referencia técnica el reel `consejos-ia/` (la base más completa).

---

## 0. Arranque rápido en una sesión nueva

```bash
cd /home/user/motion-graphics-test
# primera vez: crear la rama del cliente a partir de la rama con las herramientas
git fetch origin prueba-social-reel
git checkout -b vanguardia-reels origin/prueba-social-reel      # si ya existe: git fetch origin vanguardia-reels && git checkout vanguardia-reels && git pull origin vanguardia-reels
node -e "require('playwright'); console.log('playwright ok')"
python3 -c "import numpy, scipy, PIL, cv2; print('python ok')"
ffmpeg -version | head -1 && jq --version
```

1. Todo el trabajo del cliente va en la rama **`vanguardia-reels`** y en la carpeta **`clientes/vanguardia-academics/`**. **No abras PR** salvo que el usuario lo pida.
2. Crea una lista de tareas (TaskCreate) con las fases de la sección 4.
3. Crea la carpeta del reel con la base técnica: `bash herramientas/nuevo_reel.sh clientes/vanguardia-academics/<reel>`.
   - Luego **reemplaza** `assets/AtlasPath_logo.png` por los logos del cliente y borra el de Atlas Path:
     ```bash
     R=clientes/vanguardia-academics/<reel>; rm $R/assets/AtlasPath_logo.png; cp clientes/vanguardia-academics/marca/logos/*.png $R/assets/
     ```
4. **Fotos:** el repositorio es **público**, así que las fotos del cliente no están en git (`.gitignore`). Comprueba si existen en `clientes/vanguardia-academics/marca/fotos/`; si no, pídelas al usuario (las de Yucatán) y vuelve a bajar las del sitio (`marca/INVENTARIO-FOTOS.md`, sección 4). Copia a `<reel>/assets/fotos/` solo las que use el brief.
5. Al terminar, siempre: commit + push, enviar archivos con SendUserFile y mensaje final en español con fuentes como enlaces Markdown.

---

## 1. El repositorio

```
motion-graphics-test/   (rama vanguardia-reels)
├─ CLAUDE.md                     reglas técnicas fijas (las de marca son de Atlas Path: ver sección 2)
├─ GUIA-REELS.md                 guía original de Atlas Path
├─ herramientas/  voz-tools/     scripts compartidos (secciones 1.1 y 1.2)
├─ <reels de Atlas Path>/        referencias técnicas (sección 8)
└─ clientes/vanguardia-academics/
   ├─ GUIA-REELS-VANGUARDIA.md   esta guía
   ├─ guia_prompts_reels_vanguardia_academics.md
   ├─ .gitignore                 fotos, audio y videos fuera de git (el repo es público)
   ├─ marca/
   │  ├─ logos/                  logos del cliente en PNG (públicos, sí van en git)
   │  ├─ INVENTARIO-FOTOS.md     qué es cada foto, caras, logos a borrar y uso permitido
   │  └─ fotos/                  yucatan/ (Y01–Y16), sitio/ (S01–S24, E02–E17) — NO van en git
   └─ <reel>/                    un reel por carpeta
      ├─ index.html              animación completa (canvas 2D + Three.js), determinista
      ├─ assets/                 VanguardiaAcademics_logo.png, VanguardiaAcademics_imago.png y fotos/ con los nombres exactos del brief
      ├─ fonts/  vendor/         Nunito, Jost, JetBrains Mono y Three.js r170 (todo local, sin CDN)
      ├─ audio/                  voz-raw/tomas/, voz-en-off.wav, musica-sola.wav, efectos-solos.wav, mezclas, .m4a
      ├─ tools/                  render.js, audio.py, guion.py, timeline.json, notas.md
      ├─ Vanguardia_<Tema>.mp4 y Vanguardia_<Tema>-sin-voz.mp4
      └─ guion-con-tiempos.md, subtitulos.srt (y README.md, portada.png, recursos/ si el brief los pide)
```

> Si algún script asume que el reel está en la raíz (`<reel>/`), pásale la ruta completa `clientes/vanguardia-academics/<reel>`. Si falla por la ruta, ajusta el script con cuidado para que siga funcionando con los reels de Atlas Path.

### 1.1 `herramientas/`

| Script | Para qué |
|---|---|
| `nuevo_reel.sh <carpeta> [base]` | Crea la carpeta de un reel con vendor/, fuentes, logo, `render.js`, `guion.py`, `audio.py` e `index.html` del reel base (por defecto `consejos-ia`). |
| `servidor.sh iniciar <carpeta> [puerto]` / `detener [puerto]` | Servidor local (las páginas no funcionan con `file://`). |
| `hoja.py <capturas> <salida.jpg> [cols]` | Hoja de contacto de capturas `snap_*.png`. |
| `hoja_cuadros.py <cuadros> <salida.jpg> t0:t1:paso` | Hoja de contacto del render completo. |
| `tiempos_render.js <url> t1,t2` | Mide ms por cuadro. |
| `render_paralelo.sh <reel> <cuadros> <dur_s> [procesos=4] [puerto]` | Render con 4 Chromium en paralelo. |
| `codificar.sh <reel> <cuadros> <con-voz.mp4> <sin-voz.mp4>` | MP4 con y sin voz a −14 LUFS y `audio/mezcla-con-voz.m4a`. |
| `silencios.sh <voz-en-off.wav>` | Silencios de la voz (tramos del karaoke). |
| `pistas_mudas.py <reel> <dur_s>` | Música y efectos mudos para correr `voz_tomas.py` antes de tener la música. |
| `fotos.py info / fondo-blanco / borrar / recortar` | Recortes, borrar logotipos y marcas de agua, recortar PNG. |

### 1.2 `voz-tools/`

| Script | Para qué |
|---|---|
| `bajar_tomas.py <status.json> <carpeta_tomas> 'pref0\|pref1\|…'` | Descarga las tomas de ElevenLabs (`NN-1.mp3`, `NN-2.mp3`). |
| `voz_tomas.py <reel>` | **Método vigente.** Una toma por bloque en su ventana (`SLOTS`), recorte por energía, máx. 10 % de aceleración y mezcla. |
| `voz_mix.py` + `cues.json` | Método viejo. **No usar**: cortaba palabras. |

### 1.3 Commits

- Mensaje en español que describe el reel y empieza con **«Vanguardia ·»** (plantilla en la sección 7).
- Sin identificadores de modelo en el mensaje.
- Termina con las líneas de atribución que indique el sistema en esa sesión.
- Push: `git push -u origin vanguardia-reels`. Si falla por red, reintenta con espera de 2, 4, 8 y 16 s.
- Siempre termina con commit + push.

---

## 2. Reglas fijas de cada reel del cliente

**Posicionamiento (lo primero que se revisa):**
- **Educativo:** cada reel enseña algo (beneficios de aprender viajando, lo que se aprende en un programa, cómo se planea un buen viaje). No es un anuncio.
- **Seguridad y experiencia** con hechos, detalle y calma; diseño elegante y ritmo sereno.
- **Nunca** «los mejores», «líderes», «número 1», «únicos», «garantizado», «100 % seguro», ni comparaciones. El liderazgo se demuestra, no se dice.
- **Discreción total con los clientes:** ninguna escuela o universidad se nombra, se muestra ni se insinúa (escudos, uniformes, gafetes legibles, colores institucionales, etiquetas, hashtags). La lista de instituciones del cliente es confidencial y **no se escribe en el repo** (es público).
- **Acción social** contada con dignidad y orgullo: la comunidad y el aprendizaje son los protagonistas.

**Formato:** vertical 1080×1920, 30 fps, H.264 + AAC, duración exacta del brief (60, 75, 80 o 90 s). Dos versiones:
- con voz: `Vanguardia_<Tema>.mp4` (o el nombre exacto del brief);
- sin voz: `Vanguardia_<Tema>-sin-voz.mp4`.

**Marca de agua (siempre):**
- **Imagotipo blanco del cliente** `assets/VanguardiaAcademics_imago.png`, arriba a la izquierda, 100×100 px.
- Opacidad 70 %, sobre placa **azul marino `#122C79` al 60 %** redondeada en (40, 262), justo debajo de los 250 px superiores. Si la escena es clara, usa la versión verde del imagotipo sin placa.
- Discreta: nunca compite con el contenido.
- En el sitio existen `logo.webp`, `logo-blanco-vertical.webp`, `imago-blanco.webp` e `imago-verde.webp` (carpeta `/_astro/` de vanguardiaacademics.com). **Pide al usuario los PNG en alta resolución.** Si no llegan, convierte los `.webp` a PNG (`python3 -c "from PIL import Image; …"`), revisa que no se vean pixelados y avísalo. Si no hay ningún logo, usa solo "VANGUARDIA ACADEMICS" en Nunito Black; **nunca inventes un logotipo**.

**Cierre / CTA (siempre):**
- Logo del cliente grande en avatar circular, «VANGUARDIA ACADEMICS», línea «VIAJES EDUCATIVOS A LA MEDIDA» y **@vanguardia.academics**.
- Opcional, en pequeño debajo: «Viajar abre las puertas a nuevos aprendizajes».
- Botón SEGUIR **naranja `#D1782D`** con cursor y clic, que pasa a «SIGUIENDO ✓» (dibuja el ✓ con `check()`).
- El último medio segundo regresa al primer cuadro (loop).
- **Atlas Path no aparece en pantalla** (ni logo ni @), salvo que el usuario lo pida.

**Paleta en `C` (bloque editable de `index.html`):**

| Clave sugerida | HEX | Uso |
|---|---|---|
| `navy` | `#122C79` | placas, cajas de subtítulo, fondos 2D |
| `deep` | `#081640` | fondo 3D y viñeta (derivado) |
| `teal` | `#189293` | acento, rim light, rutas, barra de progreso |
| `tealHi` | `#3FC1C2` | palabra clave del karaoke y texto turquesa sobre fondo oscuro (derivado) |
| `orange` | `#D1782D` | cifras, sellos, botón SEGUIR |
| `sand` | `#F4EDE3` | mapas, papel, pasaporte (derivado) |
| `white` | `#FFFFFF` | texto |

Los tres primeros y el blanco salen del CSS del sitio (`brand-100`, `brand-200`, `brand-300`); los derivados son propuesta y se avisan en el mensaje final hasta que el cliente los apruebe.

**Tipografías:**
- **Nunito** (títulos; el sitio la usa en `.font-title`): Black 900 y ExtraBold 800.
- **Jost** (textos y subtítulos): SemiBold 600 y Bold 700.
- **JetBrains Mono** (HUD, tablero de aeropuerto, fuentes): instalada en el sistema.
- Nunito y Jost se bajan de Google Fonts (sección 3) y se copian a `<reel>/fonts/` y a `marca/`.

**Zonas seguras:** nada clave en los 250 px superiores, los 400 px inferiores (y > 1520) ni los 120 px de la derecha (x > 960).

**Subtítulos:**
- 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s.
- Karaoke: palabra al decirla, palabra clave en `tealHi`, cifras en `orange`.
- Caja azul marino (`navy`) semitransparente.
- 0.5 s sin subtítulo al final de cada escena.
- Se valida con `tools/guion.py`.

**Cifras y textos que se quedan solos:**
- Cada cifra clave y cada número de paso o destino ≥ 2 s.
- La frase clave («CADA DESTINO ES UN AULA») y la palabra del CTA («VIAJE», «AULA», «PRAGA»…) ≥ 3 s solas, sin subtítulo encima.

**Voz:**
- ElevenLabs, modelo `eleven_v4`, con etiquetas de tono, **una toma independiente por bloque**, aceleración máx. 10 %, mezcla final a −14 LUFS.
- **Voz por defecto:** «Fernanda – Smooth and Articulate» (`ARmPWZKt7WpXh6QDHA6x`), cálida y clara, buena para una marca educativa.
- **Pendiente:** que el cliente apruebe la voz. Si elige otra, búscala con `creative_list_voices`, anota aquí su nombre e id, y úsala en todos sus reels. Nunca imites la voz de una persona real.
- Tono: sereno, cálido y culto, de quien no necesita convencer; curioso en los destinos, pausado en las guías para directores, emotivo en acción social. Etiquetas útiles: `[warmly]`, `[curious]`, `[calm]`, `[inspired]`, `[softly]`. Evita `[excited]` salvo en un hook puntual.
- Pronunciación: «Vanguardia Academics» en español + inglés («vanguardia acádemics»); revisa con transcripción cada nombre propio (Praga, Sicilia, Montreal, Ducati, Pagani, Imagination Campus). Escribe en el prompt los nombres en inglés como se pronuncian si salen mal.

**Música:**
- Generada por código (sin derechos), a un BPM que cierre compases exactos.
- Estilo de la marca: **cinematográfica ligera / acústica cálida** (piano, pads, cuerdas suaves, guitarra pulsada, percusión ligera). Serena y elegante, mucho menos agresiva que la de Atlas Path: transmite confianza, no adrenalina. 84–104 BPM.
- Acción social: más íntima (piano y cuerdas sintetizadas), sin golpes fuertes.
- 15.5 % con texto, 19 % sin texto. Se apaga casi del todo antes de cada cifra y regresa con el golpe.
- Nunca tapa la voz: `voz_tomas.py` la baja 25 % mientras habla.

**Marcas, lugares y personas:**
- Sin logotipos de terceros (parques temáticos, marcas de autos y motos, clubes, aerolíneas, marcas de ropa, escuelas): solo como texto. Leyenda «Sin afiliación con ___» si el cliente no confirma un acuerdo. Las fotos del sitio `S13`, `S16` y `S18` no se usan (llenas de logos).
- Se borran logotipos y textos de las fotos (playeras, lanchas, bicis, letreros) y **los gafetes** (pueden identificar al grupo o la escuela).
- **Usa la columna «Uso recomendado» de `marca/INVENTARIO-FOTOS.md`:** `libre`, `fondo` (desenfocada y oscurecida), `autorización` (solo si el usuario confirma permiso de imagen) o `no usar`.
- **Menores de edad:** caras reconocibles solo con autorización confirmada. **Nunca** menores en traje de baño (`Y12`, `Y13` no se usan con personas), en momentos vulnerables o en actividades que se vean riesgosas (`Y04` no va en piezas de seguridad). Nunca nombres, edades ni escuelas.
- **No se generan estudiantes ni personas con IA.** Sin rostros retocados. Las fotos de banco nunca se presentan como viajes del cliente.
- **Equipo (`E02`–`E17`):** solo con permiso de cada persona.
- Acción social y cultura local (jarana, sitios mayas): con dignidad y respeto; niños de la comunidad solo de fondo o con permiso.

**Datos:**
- Verificar todo antes de animarlo; no inventar cifras ni atribuciones.
- Datos de la empresa con «según Vanguardia Academics». **Años de experiencia: «más de 20 años»** hasta que el cliente confirme (el sitio dice 23, 25+ y 27).
- No mencionar precios, fechas, becas, duración ni acuerdos con marcas sin datos del cliente.
- Lo futuro en condicional o como posibilidad («podrás vivir…»).
- Fuentes pequeñas abajo dentro de la zona segura (y ≈ 1502).
- Leyenda habitual: «Programas adaptables a cada institución y sujetos a disponibilidad.»

**Fotos que faltan:**
- Rectángulo gris con el nombre exacto, para que el usuario la reemplace, o un sustituto gráfico si el brief lo permite. Se avisa en el mensaje final.

**Entrega:**
- Los MP4, audios, portada y fotos **no se suben a git** (`.gitignore`): el repo es público y los videos no están aprobados por el cliente. Se entregan solo por SendUserFile. En git van `index.html`, `tools/`, guion, SRT y notas.
- SendUserFile: el MP4 con voz y la portada con `display: render`; el MP4 sin voz y el guion con `display: attach`.
- Mensaje final en español: qué se entregó y dónde (commit y rama `vanguardia-reels`), qué se verificó, decisiones a revisar, **pendientes del cliente** (logo, voz, colores derivados, autorizaciones de imagen, datos de la empresa), fotos faltantes o con marca, dominios bloqueados y fuentes como enlaces Markdown.
- Avisa siempre que no viste el video de corrido ni escuchaste el audio, si es el caso.

**Si el brief dice «VERSIÓN: SIN VOZ»:**
- no generes narración;
- respeta exactamente los tiempos de escena y las pausas de 0.5 s;
- música más baja (10–15 %) donde hay más texto;
- entrega `guion-con-tiempos.md` limpio para que el cliente grabe encima.

**Actitud:** cada reel debe superar al anterior en calidad, pero siempre revisando cuadros reales antes de entregar. La marca debe verse **profesional y confiable para un director de escuela**, no solo espectacular.

---

## 3. El entorno (contenedor en la nube)

### Rutas

| Qué | Dónde |
|---|---|
| Repositorio | `/home/user/motion-graphics-test` |
| Imágenes adjuntas | `/root/.claude/uploads/<id-de-sesión>/<hash>-image.png`. Ábrelas una por una con Read para saber cuál es cuál y cópialas con su nombre exacto. |
| Resultados grandes de herramientas MCP | `/root/.claude/projects/<proyecto>/<sesión>/tool-results/*.txt` |
| Scratchpad | Carpeta temporal de la sesión (ruta en las instrucciones del sistema). Capturas, cuadros y pruebas; no dejes ahí nada reutilizable. |

### Instalado

- Node 22 con Playwright global; Chromium instalado, **no corras `playwright install`**.
- ffmpeg 6.1, jq, Python con numpy, scipy, Pillow y OpenCV.
- 4 núcleos: 4 procesos de render en paralelo.

### Tipografías

- Instaladas: Inter, JetBrains Mono (`/usr/share/fonts/truetype/jetbrains-mono/`), DejaVu, Liberation, Noto.
- **Nunito y Jost** (de la marca) se bajan de Google Fonts:
  ```bash
  curl -sS "https://fonts.googleapis.com/css2?family=Nunito:wght@800;900&family=Jost:wght@600;700" -A "Mozilla/4.0" | grep -oE "url\([^)]+\)"
  ```
  Descarga cada URL de `fonts.gstatic.com`, guárdalas en `clientes/vanguardia-academics/marca/fonts/` y cópialas a `<reel>/fonts/` con `@font-face`.
- Alternativa: `npm pack @fontsource/nunito` y `npm pack @fontsource/jost` (woff2).

### Descargas (red con lista de permitidos)

**Funciona:** npm (`npm pack three@0.170.0`, `@fontsource/*`), `fonts.googleapis.com` + `fonts.gstatic.com`, las URLs de descarga de ElevenLabs (`storage.googleapis.com`) y, en la sesión en que se escribió esta guía, `vanguardiaacademics.com` con curl.

**No funciona:** `github.com/.../raw`, `cdn.jsdelivr.net` (403) y muchos sitios de noticias o turismo (`ENOTFOUND`). Verifica datos con **WebSearch** (`standard`, y `extended` si el resultado es pobre). En el mensaje final, di qué dominios no se pudieron abrir y que se pueden agregar en *Allowed domains* de Network access (https://code.claude.com/docs/en/cloud-environments#network-access). Dudas del entorno: herramienta `read_documentation` (tema `environment.network`).

### Procesos

- **Nunca** `pkill -f <patrón>` si el patrón aparece en tu propio comando (mata la terminal, código 144). Usa `bash herramientas/servidor.sh detener 8811` o mata por PID.
- **Nunca** lances un servidor con `(cd x && cmd &)` dentro de un script; usa `servidor.sh`.
- Un comando normal se corta a los 10 min: el render completo va con `run_in_background`.
- `git fetch` de ramas con muchos MP4 puede tardar más de 2 min: lánzalo con `run_in_background` o con `timeout` largo.

### Disco

- ~0.3 MB por cuadro JPEG: 2400 cuadros ≈ 0.75 GB. Renderiza en el scratchpad y borra cuadros viejos. Si aparece «no space left», borra cuadros y renders de prueba.

---

## 4. Flujo completo, paso a paso

### 4.1 Leer el brief y planear

Del brief saca: duración; escenas y tiempos; texto de voz y textos en pantalla; cifras; **lista de imágenes con nombre exacto y uso** (y cuáles son del cliente); objetos 3D (`GLOBO_3D`, `PASAPORTE_3D`, `AULA_3D`…); entregables extra.

Cuenta de tiempos:
- La voz va a ~2.6–3 palabras/s y los subtítulos a ≤ 2.3 palabras/s.
- **Los subtítulos casi siempre se condensan.**
- Los tiempos de escena **siguen a la voz**; si se mueven respecto al brief, se avisa.

### 4.2 Verificar datos

- Busca cada cifra, fecha y atribución con WebSearch: datos de destinos (fechas históricas, cifras de turismo, industrias), estudios de aprendizaje experiencial (OCDE, UNESCO, universidades), requisitos de IB/SEP.
- Datos del cliente: solo los del sitio o los que dé el usuario, con «según Vanguardia Academics».
- Si algo no se confirma, reformúlalo: «más de», «≈», «según X», ámbito exacto, condicional.
- Gráficas con pocos datos reales → «trazo ilustrativo»; medidores inventados → «medidor ilustrativo».
- Guarda las URL para el mensaje final y `tools/notas.md`.

### 4.3 Voz por bloques en ElevenLabs

1. Divide la voz en bloques y asigna a cada uno su ventana de tiempo.
2. Prompt: números con letra («tres mil años», «dos mil veintiséis»), nombres extranjeros como se pronuncian, etiquetas de tono suaves (`[warmly]`, `[excited]`, `[curious]`, `[inspired]`, `[softly]`), puntos suspensivos para pausas. **No uses `[long pause]` para encadenar frases.**
3. Un flow por reel:
   ```
   mcp__ElevenLabs__creative_create_flow  {name: "Vanguardia Academics · <reel> · voz por bloques", context: "…"}
   ```
4. Una llamada por bloque (genera 2 tomas). **No repitas una llamada para «reintentar»: cobra créditos otra vez.**
   ```
   mcp__ElevenLabs__creative_generate_speech {flow_id, voice_id: "<voz aprobada>", model_id: "eleven_v4",
                                              prompt: "[curious] ¿Y si tu próxima clase fuera en Praga?", context: "Bloque 00 …"}
   ```
5. Espera con `creative_get_flow_run_status` cada `poll_after_seconds` hasta `all_completed`.
6. Descarga:
   ```bash
   python3 voz-tools/bajar_tomas.py <archivo-tool-results.txt> clientes/vanguardia-academics/<reel>/audio/voz-raw/tomas 'próxima clase|cada destino|…'
   ```
7. Revisa la pronunciación de «Vanguardia Academics» y de cada nombre extranjero con `creative_add_flow_asset_node` + `creative_transcribe_audio` (`eleven_scribe_v1`).
8. Si un bloque no cabe o suena mal: rehaz solo ese bloque y mueve las tomas viejas a `audio/voz-raw/descartadas/`.

### 4.4 Colocar la voz (`voz_tomas.py`)

1. Agrega el reel a `SLOTS` en `voz-tools/voz_tomas.py` con su ruta: una tupla `(inicio deseado, fin máximo)` por bloque.
   - **El fin del último slot define el largo del audio:** `N = ceil(último_fin + 0.6)`. Para 80 s el último fin es 79.4.
2. Sin música todavía: `python3 herramientas/pistas_mudas.py <reel> <duración>`.
3. `python3 voz-tools/voz_tomas.py <reel>` → debe decir `TODO OK`.
4. Si sale REVISAR: amplía la ventana, acorta el texto o rehaz la toma. Nunca más de 10 % de aceleración.
5. Silencios para el karaoke: `bash herramientas/silencios.sh <reel>/audio/voz-en-off.wav` → `[voz desde, voz hasta]` en `SUBS_RAW`.

### 4.5 Fotos

1. Identifica cada imagen adjunta con Read y cópiala a `<reel>/assets/fotos/` con su **nombre exacto** (fondos `.jpg` calidad 94, recortes `.png`).
2. Para cada foto con estudiantes, anota en `tools/notas.md` si el usuario confirmó la autorización de imagen.
3. Sin fondo, sobre blanco: `python3 herramientas/fotos.py fondo-blanco entrada.png salida.png`.
4. Logotipos (aerolíneas, autos, camisetas): `python3 herramientas/fotos.py borrar foto.jpg foto.jpg rect:x0,y0,x1,y1 --sigma 4`. Revisa siempre un recorte ampliado 4×.
5. PNG con mucho margen: `python3 herramientas/fotos.py recortar entrada.png salida.png`.
6. Revisa todo: `python3 herramientas/fotos.py info assets/fotos/*`.
7. **No retoques caras.**

**Integración en `index.html`:**
- **Fondos:** desenfoque 8 px, `brightness(.4)`, gradación uniforme **azul-turquesa** con toque cálido naranja opcional (atardeceres de destino), viñeta y zoom lento.
- **Recortes:** misma gradación, luz arriba a la izquierda, *rim light* turquesa, sombra de silueta y de contacto.

### 4.6 La animación (`index.html`)

Parte de `nuevo_reel.sh`. Conserva la infraestructura y reemplaza escenas, paleta (`C`), tipografías y textos.

**Estructura del `<script type="module">`:**
1. **Bloque editable:** `C` (paleta de la sección 2), `T` (textos), `FONDOS`, `RECORTES`, `SCENES`, `SUBS_RAW`, `HOLDS`, `SOURCES`, `METER`, `sfx(t, tipo, volumen, tono)`, `window.TL`.
2. **Primitivas 2D:** `text`, `tw`, `fitSize`, `glowText`, `outlineNum`, `pill`, `hudFrame`, `icon`, `check`, `cursorArrow`, `sparks`, `lensFlare`, `ring2D`, `godRays`, `motes`.
3. **Fotos:** `buildBG`, `fondo`, `buildCut`, `drawCut`, `placeholder`.
4. **Lienzos que se vuelven texturas:** pasaporte, pase de abordar, tablero de salidas, mapa, ficha del programa. Se redibujan solo cuando cambia una clave.
5. **Three.js:** renderer fuera de pantalla con `preserveDrawingBuffer`, `draw3D(...)` con *bloom* y *zoom blur*, helpers `proj`, `screenToZ`, `setCam`, `addLights`, `glassMat`, `reflMat`, `dissolveMat`, `pointsMat` / `makePts` / `morph` / `sampleScreen`, `makeCard`, `sprite`, `lines`, `path`.
6. **Escenas:** `buildX()` + `sX(t)`; `DRAW` en el mismo orden que `SCENES`.
7. **HUD:** `tag`, `meter`, `tipHeader`, `sources`, `subs`, `post`, `shake`.
8. **`renderFrame(t)`:** escena → loop (últimos 0.5 s funden al cuadro 0) → `post`, `sources`, `subs`, `hud` (marca de agua del cliente + barra de progreso turquesa).
9. **Opcional:** `renderCover()`, `ASSETS` + `renderAsset(nombre)`.
10. **Arranque:** `window.ready` espera fuentes (`document.fonts.load('900 80px Nunito')`, `'600 40px Jost'`) e imágenes; `?render=1` oculta el botón de reproducir.

**Reglas de código:**
- **Determinista:** nada de `Math.random()` ni del reloj; usa `rnd(i)` o `mulberry(semilla)`.
- Tiempos con `p(t,a,b)`, `eo` / `eio` / `eback`, `bell`, `pop`, `mono([[t,v],…])`.
- `obj.position.copy(screenToZ(cam, x, y, z))` y `proj(vector, cam)`.

**Retícula** (canvas 1080×1920):

| Elemento | Posición |
|---|---|
| Marca de agua (imagotipo) | x 40–140, y 262–362 |
| Chip de sección / destino | y 404–456, centrado en x 500 |
| Medidor (si hay) | placa x 596–944, y 268–376 |
| Chip de dato (`tag`) | (160, 282) |
| Área visual principal | x 90–940, y ≈ 460–1330 |
| Número de paso grande | número y 510, título 690, subtítulo 746; contenido debajo de y ≈ 790 mientras está grande |
| Subtítulos | centro y 1395 (caja ≈ 1342–1448); en el cierre, 1300 |
| Fuentes | y ≈ 1502 |
| Centro visual | x 500 |

**Transiciones propias de la marca** (una distinta por escena):
- despegue: la cámara sube entre nubes y baja en el destino;
- sello de pasaporte que golpea la pantalla y cambia de escena;
- página de pasaporte o de cuaderno que se voltea;
- tablero de aeropuerto cuyas letras giran hasta formar el título;
- ruta punteada que se dibuja sobre el mapa y hace zoom al pin;
- paredes del aula que se abren hacia la ciudad (dolly-zoom);
- además las de siempre: destello, *zoom blur*, iris, barrido radial, cortina, partículas que se rearman.

Movimientos rápidos en las pausas de 0.5 s; con subtítulo, 3D lento.

### 4.7 Revisión visual (siempre, varias rondas)

```bash
bash herramientas/servidor.sh iniciar clientes/vanguardia-academics/<reel> 8811
node clientes/vanguardia-academics/<reel>/tools/render.js http://localhost:8811/index.html <scratchpad>/capturas snap 0.3,1.6,2.8,4.2
python3 herramientas/hoja.py <scratchpad>/capturas <scratchpad>/hoja.jpg 6
```

- `[err]` en `render.js` = error de JavaScript. Extrae el módulo y corre `node --check` (como en `GUIA-REELS.md` 4.7).
- El 404 de una foto faltante es normal.

**Qué revisar en cada hoja:**
- [ ] Títulos encimados con el contenido 3D.
- [ ] Texto turquesa `#189293` sobre azul marino: poco contraste; usa `tealHi` o blanco.
- [ ] Texto blanco sobre panel arena o foto clara: placa azul marino detrás.
- [ ] Objetos fuera de zona segura o que tapan subtítulos.
- [ ] Cámara 3D demasiado cerca.
- [ ] Partículas enormes al pasar la cámara.
- [ ] Cifras ≥ 2 s; frase y palabra del CTA ≥ 3 s solas.
- [ ] Logos de terceros, gafetes, escudos o uniformes visibles en fotos o texturas.
- [ ] Caras de menores sin autorización confirmada; nada de traje de baño.
- [ ] Ningún superlativo ni autoelogio en textos y voz:
      `grep -n -i -E "mejor|líder|lider|número 1|#1|únic|garantiz|100 ?% seguro" <reel>/index.html` (revisa cada coincidencia a mano).
- [ ] Ningún nombre de institución cliente en textos, notas o nombres de archivo.
- [ ] El reel enseña algo concreto (si se quita la marca, ¿sigue siendo útil?).
- [ ] Marca de agua y cierre con logo y @ del cliente, sin rastro de Atlas Path.
- [ ] Último cuadro igual al primero (loop).

Velocidad: `node herramientas/tiempos_render.js http://localhost:8811/index.html 2,22,31,60` (300–1400 ms por cuadro está bien).

### 4.8 Línea de tiempo y validación de subtítulos

```bash
cp <scratchpad>/capturas/timeline.json clientes/vanguardia-academics/<reel>/tools/timeline.json
cd clientes/vanguardia-academics/<reel> && python3 tools/guion.py tools/timeline.json tools/notas.md
```

- Actualiza `VOZ` en `tools/guion.py` con los tiempos de `voz_tomas.py`.
- `tools/notas.md`: verificación de datos, fotos y autorizaciones, marcas quitadas, tipografías, pendientes del cliente, fuentes con URL.
- Salida esperada: `fuera de regla: [] cifras cortas: [] solas con subtítulo: [] sin pausa: []`.
- Reexporta `timeline.json` y corre `guion.py` y `audio.py` tras cada cambio de tiempos.

### 4.9 Música y efectos (`tools/audio.py`)

1. Adapta el del reel base: `SEC` (secciones), acordes (progresiones mayores luminosas, por ejemplo I–V–vi–IV), curvas `*_g`, *risers*, capas.
   - Cambia el carácter: menos golpes duros, más pads, piano, *plucks* y percusión suave.
2. **BPM = compases × 240 / duración** (ej. 25 compases en 60 s → 100 BPM; 30 en 75 s → 96 BPM; 33 en 80 s → 99 BPM).
3. **Cada tipo usado en `sfx(…)` debe existir en `GEN`.** Efectos nuevos útiles para la marca (agrégalos a `GEN` si no existen): `plane` (despegue / paso de avión), `stamp` (sello de pasaporte), `board` (tablero de aeropuerto con aletas que giran), `page` (pasar página; parecido a `paper`/`flip`), `zipper` (mochila), `camera` (obturador). Revísalos con:
   ```bash
   python3 -c "import json;print(sorted({e['type'] for e in json.load(open('tools/timeline.json'))['sfx']}))"
   ```
4. `python3 tools/audio.py tools/timeline.json audio` → `musica-sola.wav`, `efectos-solos.wav`, `mezcla-sin-voz.wav`.
5. Desde la raíz: `python3 voz-tools/voz_tomas.py <reel>`.

Efectos existentes en `consejos-ia/tools/audio.py`: `whoosh`, `sweep`, `pop`, `tick`, `click`, `key`, `blip`, `lock`, `ping`, `send`, `impact`, `hit`, `flash`, `chord`, `ding`, `chime`, `select`, `scan`, `rise`, `assemble`, `morph`, `dissolve`, `pulse`, `paper`, `drone`, `number`, `count`, `meter`, `deny`, `unlock`, `door`, `flip`, `strike`. Más en otros reels: `grep -n "def " */tools/audio.py`.

### 4.10 Render y codificación

```bash
bash herramientas/render_paralelo.sh clientes/vanguardia-academics/<reel> <scratchpad>/cuadros <duración> 4 8811   # run_in_background
python3 herramientas/hoja_cuadros.py <scratchpad>/cuadros <scratchpad>/hoja_a.jpg 0:19.5:0.5                      # … hasta el final
bash herramientas/codificar.sh clientes/vanguardia-academics/<reel> <scratchpad>/cuadros Vanguardia_<Tema>.mp4 Vanguardia_<Tema>-sin-voz.mp4
```

Comprueba: `nb_frames` = duración × 30; con voz ≈ −14 LUFS y pico ≤ −1 dBFS; sin voz ≈ −14 LUFS y ≈ −3 dBFS. ~50 MB por MP4.

### 4.11 Portada y recursos (si el brief los pide)

```bash
node <reel>/tools/render.js http://localhost:8811/index.html <reel> cover portada.png && rm <reel>/timeline.json
node <reel>/tools/render.js http://localhost:8811/index.html <reel>/recursos assets && rm <reel>/recursos/timeline.json
```

- **Portada:** fondo azul marino profundo, título corto en Nunito Black (destino o pregunta), el objeto principal (globo, pasaporte, monumento) y un acento naranja. Coherente entre reels para que la cuadrícula del perfil se vea ordenada.

### 4.12 Documentos del reel

- `guion-con-tiempos.md` y `subtitulos.srt` (de `guion.py`).
- `README.md` si se pide proyecto editable.
- Detén el servidor: `bash herramientas/servidor.sh detener 8811`.

### 4.13 Commit, push y entrega

```bash
git add clientes/vanguardia-academics/<reel> voz-tools/voz_tomas.py   # el .gitignore deja fuera fotos, audio y MP4
git status --short   # confirma que no entra ninguna foto ni video
git commit -F mensaje.txt
git push -u origin vanguardia-reels
```

Después: SendUserFile y mensaje final (sección 7).

---

## 5. Recetario de técnicas

Las técnicas de `GUIA-REELS.md` sección 5 valen todas (disolución por bloques, partículas que forman texto, tarjetas que salen del celular, gráficas 3D, barras de cristal, simulador de camino, anillo con dolly-zoom, red de nodos, muro de miniaturas, árbol 3D, número grande, medidor, chat en celular, palabra del CTA, cierre SEGUIR, loop). Cómo se traducen a esta marca:

| Efecto para Vanguardia | Cómo se hace | Basado en |
|---|---|---|
| `GLOBO_3D` con rutas de vuelo desde México | Esfera de alambre o puntos, arcos `QuadraticBezierCurve3` elevados con `TubeGeometry` + `setDrawRange`, avión-sprite que recorre el arco, pin que se enciende al llegar | Tierra con satélites (`terafab/`), globo con pines (`ia-compras/`) |
| Cámara que «vuela» y aterriza en el destino | Simulador de camino sobre `CatmullRomCurve3` con paradas por `mono`, nubes de partículas que la cámara atraviesa | Rastreador (`consejos-ia/`), montaña rusa (`terafab/`) |
| `PASAPORTE_3D` con sellos | Libro de dos planos con bisagra, textura de lienzo arena; cada sello es un lienzo naranja/turquesa que golpea con `eback` + `shake` + sfx `stamp` | `makeCard`, `tipHeader` |
| Tablero de salidas (hook) | Lienzo con celdas de letras que giran (flip) hasta formar «PRAGA 08:40»; JetBrains Mono, letras blancas en placas azul marino | Calendario y `flip` (`consejos-ia/`) |
| `AULA_3D` que se abre a la ciudad | Caja de 4 planos (paredes con pizarrón) que rotan hacia afuera; detrás, fondo del destino; dolly-zoom | Chip que se abre en capas (`terafab/`), anillo dolly-zoom |
| Ciudad o monumento que se arma | Bloques `RoundedBoxGeometry` isométricos que caen en orden | Fábrica que se construye (`terafab/`) |
| Ruta punteada sobre mapa | Lienzo arena con costas simplificadas, línea discontinua animada con `setLineDash` | Mapa con pin (`gary-vee/`) |
| Competencias que se llenan | Medidor ilustrativo «COMPETENCIAS GLOBALES» con eventos por escena | `meter` |
| Cifras de impacto social | Cifra de partículas (`10,000+`) con «según Vanguardia Academics» debajo | Partículas que forman cifras (`ia-compras/`) |
| Palabra del CTA | Sale de la burbuja de comentario, crece con anillos turquesa y chispas naranja, 3 s sola | `sCta` |

---

## 6. Problemas conocidos y su solución

Todos los de `GUIA-REELS.md` sección 6 siguen vigentes (voz cortada → tomas por bloque; *broadcast error* → último `SLOTS`; subtítulos largos → condensar; contenido encimado; texto ilegible; objetos fuera de zona segura; partículas gigantes; ✓ sin glifo; errores de sintaxis; propiedades pisadas en *spread*; `renderAsset` roto; saturación sin voz; cámara que sigue al objeto; fundir tarjetas con `own: true`; logos sobre piel; `add()` en audio; comandos colgados; `pkill -f`; `ENOTFOUND`; primer cuadro lento; reexportar `timeline.json`; cifras que no coinciden). Además, para este cliente:

1. **Quedó el logo o el @ de Atlas Path:** `nuevo_reel.sh` copia `AtlasPath_logo.png` y el cierre del reel base. Busca y reemplaza antes de la primera captura:
   ```bash
   grep -rn -i "atlas" clientes/vanguardia-academics/<reel>/index.html
   ```
2. **Turquesa de marca ilegible sobre azul marino:** `#189293` tiene poco contraste con `#122C79`. Para texto usa `#3FC1C2` o blanco; `#189293` solo para líneas, brillos y rellenos.
3. **Nunito o Jost no cargan** (sale una fuente del sistema): falta el `@font-face` o el peso. Declara cada peso y espera con `document.fonts.load` en `window.ready`.
4. **Logo `.webp` pixelado** al agrandarlo en el cierre: pide el PNG o SVG al cliente; mientras, no lo muestres a más de su tamaño original.
5. **Años de experiencia distintos en el sitio (23, 25+, 27):** usa «más de 20 años» y avísalo hasta que el cliente confirme.
6. **Nombre del programa de Disney inconsistente:** usa «Disney Imagination Campus» como lugar, sin logo, con leyenda de sin afiliación, hasta que el cliente confirme.
7. **Repositorio público:** cualquier foto, video o dato confidencial que entre a git queda expuesto (y en el historial aunque se borre después). Antes de cada commit: `git status --short` y `git diff --cached --stat`. Si algo se subió por error, avisa al usuario de inmediato; borrarlo del historial requiere reescribirlo y es decisión suya.
8. **Una sesión nueva no tiene las fotos:** están fuera de git. Pídelas o bájalas del sitio (sección 0, paso 4).
9. **Un lugar cambió sus reglas:** por ejemplo, la escalinata del Nohoch Mul (Cobá) estuvo cerrada años y el INAH abrió una nueva en dic. 2025. Verifica el estado actual antes de describir una actividad.

---

## 7. Plantillas

### Mensaje de commit

```
Vanguardia · Reel <título corto>: <duración> s en Three.js con <2–3 rasgos visuales> y voz de <voz>

- clientes/vanguardia-academics/<reel>/index.html: <escenas y objetos 3D principales>
- Datos verificados: <fuentes principales y cifras>
- Música a <BPM> BPM (<compases> compases, loop exacto), efectos sincronizados, voz por bloques y mezclas a −14 LUFS; videos con y sin voz
- Fotos <rango>: <del cliente / de banco>, marcas quitadas; <foto faltante> queda como marcador gris con su nombre
- voz_tomas.py: tiempos del reel <reel>

<líneas de atribución que indique el sistema en la sesión>
```

### Mensaje final al usuario (en español)

```
El reel «<título>» para Vanguardia Academics ya está terminado y exportado como MP4. Te lo envié aquí con <archivos>.
Todo está subido a la rama `vanguardia-reels` (commit `<hash>`); no abrí PR.

**Lo que entrego** (en `clientes/vanguardia-academics/<reel>/`)
- `Vanguardia_<Tema>.mp4`: <dur> s, 1080×1920, 30 fps, H.264 + AAC, subtítulos quemados, voz <voz>, −14.x LUFS.
- `Vanguardia_<Tema>-sin-voz.mp4`: …
- <portada, recursos, proyecto editable, guion, SRT>

**Revisiones**
- <reglas de subtítulos, cifras ≥ 2 s, frase/palabra ≥ 3 s, voz dentro de su tiempo, BPM y loop, sin rastro de Atlas Path>

**Pendientes del cliente**
- <logo en PNG, voz aprobada, colores derivados, autorizaciones de imagen, datos de seguridad y acompañamiento, años de experiencia, nombres de programas>

**Filtro de marca**
- <sin superlativos, sin instituciones, sin gafetes ni logos, fotos usadas según el inventario>

**Lo que debes revisar**
- <fotos faltantes y cómo reemplazarlas>
- <marcas quitadas de las fotos y fotos con marca de agua de banco>
- <datos reformulados y por qué>
- <tiempos que cambiaron respecto a la guía>
- <dominios que no se pudieron abrir + enlace a Allowed domains>

**Fuentes**
- [Título](URL)
```

---

## 8. Índices de reels

### 8.1 Reels de Vanguardia Academics (actualizar al terminar cada uno)

| Carpeta | Dur. | BPM | Técnica | Palabra CTA | Qué reutilizar |
|---|---|---|---|---|---|
| _(ninguno todavía)_ | | | | | |

El banco de ideas está en `guia_prompts_reels_vanguardia_academics.md`, sección 14.

### 8.2 Reels de Atlas Path que sirven de base técnica

| Carpeta | Para qué sirve en esta marca |
|---|---|
| `consejos-ia/` | **Base técnica más completa**: simulador, medidor, portada, recursos PNG, README editable. Guías para directores con pasos numerados. |
| `terafab/` | Tierra con satélites, cámara montaña rusa, fábrica que se construye → globo con rutas, vuelo al destino, ciudad que se arma. |
| `ia-compras/` | Globo con pines, cifras de partículas, muro → mapa de destinos, cifras de impacto social. |
| `gary-vee/` | Mapa con pin, tarjetas → ruta sobre mapa, fichas de programa. |
| `neuroventas/` | Túnel y moléculas → «lo que pasa en el cerebro cuando aprendes viajando». |
| `viaje-heroe/` | Mapa de aventura 2D → historia del estudiante que viaja. |
| `prueba-social/` y primeros reels | 2D plano y tipografía cinética → versiones ligeras y rápidas. |
