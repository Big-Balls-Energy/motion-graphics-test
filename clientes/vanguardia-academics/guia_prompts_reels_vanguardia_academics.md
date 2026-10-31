# Guía maestra: prompts de Reels animados para Vanguardia Academics

> **Cómo usar este archivo:** pégalo (o adjúntalo) al inicio de una nueva conversación y escribe: *"Lee esta guía y úsala para todo lo que te pida. Hoy quiero un prompt sobre [TEMA]."* Con eso, Claude retoma el método, el formato y las reglas de la marca.
>
> **Quién produce:** la agencia Atlas Path, para su cliente Vanguardia Academics. En pantalla solo aparece la marca del cliente; Atlas Path no firma los videos.

---

## 1. Contexto del cliente

- **Cliente:** Vanguardia Academics, empresa mexicana de **viajes educativos al extranjero diseñados a la medida de cada institución**.
- **Firma en video:** "VANGUARDIA ACADEMICS" · "VIAJES EDUCATIVOS A LA MEDIDA" · **@vanguardia.academics**.
- **Sitio:** https://vanguardiaacademics.com/ (consultarlo antes de cada guion de destino o programa).
- **Contacto que puede ir en el CTA o en la descripción:** WhatsApp +52 999 102 1067 · botón del sitio "Quiero conocer más".
- **Frases propias de la marca** (textuales del sitio, se pueden usar en pantalla):
  - "Viajar abre las puertas a nuevos aprendizajes." (titular, sirve como frase protagonista)
  - "Cada destino es un aula para los estudiantes."
  - "Transformando vidas a través de experiencias educativas globales." (misión)
  - "Tus inquietudes las hacemos propias."
  - "¡Comienza a hacer la diferencia con nosotros!"
- **Pilares de la marca** (del sitio): **Enfoque personalizado · Aprendizaje experiencial · Compromiso social**.
- **Sistemas académicos con los que trabajan:** Currículo Nacional (SEP, UNAM) y Bachillerato Internacional (PD y PAI).
- **Programas / experiencias eje** (se adaptan al currículo de cada escuela):

| Destino | Programa | Enfoque |
|---|---|---|
| Berlín y Praga | Green Thinking | Sostenibilidad en la gestión empresarial |
| Sicilia | Mundo de las humanidades (Culture, History & Heritage) | Arte e historia |
| Orlando | Programa en Disney Imagination Campus (el sitio lo llama "Disney Yes Program" y "Disney Youth Education Series": **confirmar nombre**) | Competencias creativas y pensamiento crítico |
| Madrid, Murcia, Valencia y Barcelona | Marketing y negocios deportivos | Industria del deporte |
| Montreal | Emprendimiento, liderazgo y creatividad | Negocios e innovación |
| Italia (Ferrari, Ducati, Pagani) | Diseño e ingenierías | Industria automotriz de alta gama |
| Mérida, Yucatán | Acción social | Servicio comunitario |

- **Audiencia (en este orden):**
  1. **Quien decide:** directores, coordinadores de programa, docentes y jefes de área de preparatorias y universidades en México ("Si diriges un programa académico…").
  2. **Quien influye:** padres de familia (seguridad, valor educativo, inversión).
  3. **Quien sueña:** estudiantes de preparatoria y universidad (aventura, destino, amigos).
- **Idioma:** español latino (mexicano neutro), **tuteo** (la marca habla de "tú"). Tono cercano e inspirador, con respaldo profesional; emotivo en acción social.
- **Líneas de contenido:**
  1. **El destino es el aula:** qué se aprende en cada programa (un destino por video).
  2. **Aprendizaje experiencial:** por qué viajar enseña (estudios reales sobre aprendizaje fuera del aula, habilidades globales, idiomas).
  3. **Guías para directores y docentes:** cómo planear un viaje académico, alinearlo con SEP/UNAM/IB (por ejemplo CAS en el PD), qué preguntar antes de contratar, seguridad y logística.
  4. **Historias del destino:** datos curiosos de historia, ciencia, arte, deporte o ingeniería de cada lugar, con verificación.
  5. **Acción social:** proyectos comunitarios en Mérida y lo que los estudiantes viven al ayudar.
  6. **Detrás de cámaras y testimonios** (solo con fotos y videos reales del cliente y con autorizaciones; ver sección 13).

---

## 2. Flujo de trabajo para cada video

1. **Investigar primero, siempre.** Buscar en la web antes de escribir el guion: datos del destino, estudios sobre aprendizaje, cifras educativas. Verificar cada dato en fuentes serias (UNESCO, OCDE, universidades, sitios oficiales de turismo o museos).
2. **Datos de la empresa:** solo los que publica el cliente, atribuidos ("según Vanguardia Academics"). Si hay contradicción, preguntar (ver sección 12).
3. **Corregir premisas falsas con evidencia,** pero buscar de nuevo si el usuario insiste.
4. **Escribir el guion** con la estructura viral (sección 4) y los tiempos de lectura (sección 5).
5. **Armar el prompt base completo** en **un solo bloque de código** (sección 9).
6. **Agregar los dos bloques de versión de audio** (A sin voz / B voz IA), cada uno en su propio bloque (sección 10).
7. **Dar la lista de fotos** con nombres de archivo exactos y términos de búsqueda, separando **fotos del cliente** y **fotos de banco** (sección 8).
8. **Cerrar con notas breves:** datos verificados, matices o advertencias, **qué debe confirmar el cliente** y **lista de fuentes** con enlaces.

**Preferencias de entrega:**
- Un **solo prompt base** por video, nunca partido en varias piezas.
- Si se piden dos temas juntos, se combinan en **un solo video** ("Parte 1 / Parte 2").
- Respuesta directa: breve introducción, prompt, versiones A/B, lista de fotos, notas y fuentes.

---

## 3. Especificaciones técnicas fijas

- Formato vertical **9:16 · 1080 × 1920 px · 30 fps**.
- Exportable como **MP4 (H.264, audio AAC)**, con subtítulos integrados.
- Pedir siempre: *"Si puedes, entrégala exportable como MP4; si no, como animación reproducible a pantalla completa que yo pueda grabar."* En producción completa: *"Si no puedes exportar el MP4, dilo y entrega el proyecto ejecutable con instrucciones. No simules una exportación."*
- **Duración según contenido:**
  - Un concepto o un dato del destino: **60 s**.
  - Un programa completo o una historia de viaje: **75 s**.
  - Guía práctica con varios pasos o varios destinos: **80–90 s**.
- Nombre de archivo sugerido: `Vanguardia_[Tema].mp4`.

---

## 4. Estructura viral del guion

| Parte | Tiempo aprox. | Qué hace |
|---|---|---|
| **Hook** | 0–4 s | Pregunta o imagen que detiene el scroll. Ej.: "¿Y si tu próxima clase fuera en Praga?", "Este salón no tiene paredes". Movimiento y texto desde el primer cuadro. |
| **Giro / contexto** | 4–12 s | Nombra el destino, el programa o el concepto ("Se llama aprendizaje experiencial"). |
| **Dato o experiencia** | 12–30 s | Estudio real, dato verificado del destino o actividad concreta del programa, con fuente en pantalla. |
| **Explicación** | 30–45 s | Qué aprenden y por qué importa (competencia, materia o habilidad). |
| **Cómo se vive / ejemplos** | 45–55 s | Momentos del viaje: taller, visita, proyecto, convivencia. |
| **Aplicación** | 55–60 s | "¿Diriges un programa académico? ___" o "¿Tu escuela ya viaja? ___" |
| **CTA con palabra clave** | últimos 7–10 s | Comentar una palabra + seguir a @vanguardia.academics (o "envíaselo a tu coordinador"). |
| **Loop** | último cuadro | Regresa visualmente al primer cuadro. |

**Principios de retención (basados en lo que Instagram declara):**
- Las señales que más pesan en Reels son **tiempo de visualización, envíos por DM y likes**; los envíos pesan mucho para llegar a no seguidores. Para esta marca el envío natural es **alumno → papás, docente → director**: pedirlo en el CTA cuando aplique.
- Guardados: las guías para directores deben ser "guardables" (checklists, pasos numerados).
- Cambio visual cada **3–4 s**.
- Subtítulos siempre.
- Final en loop.
- Pregunta final o palabra clave para provocar comentarios.

---

## 5. Tiempos de lectura y espacio para voz (prioridad)

- Ritmo máximo **~2.3 palabras por segundo**. Contar palabras por escena antes de asignar tiempos.
- Cada bloque de subtítulo: **mínimo 1.5 s** en pantalla.
- **Pausa de 0.5 s entre escenas** (solo movimiento, sin texto nuevo).
- Cifras clave: **mínimo 2 s** solas en pantalla.
- Palabra del CTA: **mínimo 3 s** sola y grande.
- Frases protagonistas (ej. "CADA DESTINO ES UN AULA"): **mínimo 3 s**.
- Mientras hay subtítulo, los movimientos 3D son lentos; los rápidos van en las pausas.

---

## 6. Zonas seguras y subtítulos

- Nada importante en los **250 px superiores** ni en los **400 px inferiores**; dejar libres **120 px a la derecha**.
- Subtítulos quemados en el **tercio medio-inferior**, máximo **3–5 palabras por bloque**.
- Texto blanco con caja azul marino oscuro semitransparente; **palabra clave en turquesa claro** (karaoke).
- Cifras en **naranja de marca** y con animación de conteo.

---

## 7. Técnica visual

### 7.1 Mixed media: fotos reales + motion graphics
- **RECORTE (PNG sin fondo):** estudiantes, monumentos, objetos del destino (casco, maqueta, pasaporte, mochila).
- **FONDO (JPG):** paisajes y lugares del destino, con blur de 6–10 px y oscurecidos al 60 %.
- Integración: sombra de contacto, **una sola luz arriba a la izquierda**, rim light turquesa, gradación uniforme, capas, parallax 2.5D, rotación de ±8° y desenfoque de movimiento.
- **Fotos reales de viajes del cliente:** las manda el cliente. Son la mejor prueba social de la marca: usarlas tal cual, sin retocar caras.

### 7.2 3D y efectos "wow" (adaptados a viajes educativos)
- Pedir **Three.js (WebGL) + línea de tiempo tipo GSAP**; si no, 2.5D.
- Definir **objetos 3D con nombre propio** en el prompt. Ideas para la marca:
  - `GLOBO_3D`: Tierra con **rutas de vuelo en arco** desde México hacia cada destino y pines que se encienden.
  - `PASAPORTE_3D`: pasaporte genérico (sin escudos oficiales) que se abre y recibe **sellos** por destino; cada sello es una competencia.
  - `AULA_3D`: salón de clases cuyas paredes se despliegan y se convierten en la ciudad del destino ("cada destino es un aula").
  - `BOLETO_3D` / pase de abordar con datos del programa (destino, enfoque, nivel).
  - `MAQUETA_3D`: ciudad isométrica que se arma bloque a bloque (Praga, Barcelona, Montreal).
  - `MOTOR_3D`: motor o chasis genérico en vista explosionada (programa de diseño e ingenierías, sin logotipos de marcas).
  - `ESTADIO_3D`: estadio low-poly con datos de negocio deportivo.
  - `HOJA_3D`: hoja o árbol de partículas que crece (Green Thinking, sostenibilidad).
  - `COLUMNA_3D`: columna o templo griego (Sicilia) que se reconstruye.
  - `MANOS_3D` / ladrillos que construyen un piso o una casa (acción social).
- Recursos que ya funcionaron en otros proyectos y aplican aquí:
  - **Simulador de camino:** la cámara vuela como avión sobre el globo y "aterriza" en el destino.
  - **Camino bifurcado:** clase tradicional gris contra viaje brillante que acelera.
  - **Vista explosionada** de objetos.
  - **Cifras hechas de partículas.**
  - **Elemento conductor:** pasaporte que se llena de sellos, mapa con ruta punteada, mochila que se llena, medidor de "competencias globales", chip de sección ("DESTINO → APRENDIZAJE → IMPACTO").
  - HUD tipo **pantalla de aeropuerto** (tablero de salidas con letras que giran, ideal para hooks).
- Barra de progreso delgada arriba (0 → 100 %), opcional con forma de **ruta de vuelo**.
- Máximo **un elemento principal entrando a la vez**.

### 7.3 Paleta y tipografía de la marca (tomadas del CSS del sitio)

| Función | Color | Origen |
|---|---|---|
| Azul marino (principal, fondos, placas) | `#122C79` | sitio (brand-200) |
| Turquesa / verde azulado (acento, palabra clave) | `#189293` | sitio (brand-100) |
| Naranja (cifras, botones, sellos) | `#D1782D` | sitio (brand-300) |
| Blanco | `#FFFFFF` | sitio |
| Fondo profundo para 3D | `#081640` | derivado del azul marino |
| Turquesa claro para texto sobre fondo oscuro | `#3FC1C2` | derivado (más legible que `#189293` sobre azul) |
| Arena / papel (versión clara, mapas, pasaporte) | `#F4EDE3` | derivado |

- Degradado de marca (el sitio lo usa): **turquesa → azul marino**, con naranja como acento.
- Las variantes "derivado" son propuesta de Atlas Path: confirmar con el cliente si tiene manual de marca.
- **Tipografías del sitio:** **Nunito** (títulos; el sitio la usa en `.font-title`, usar Black/ExtraBold) y **Jost** (textos y subtítulos, SemiBold/Bold). HUD y datos: **JetBrains Mono**. Las dos primeras son de Google Fonts.

---

## 8. Lista de fotos (formato fijo)

- Prefijo de letra por video + número + descripción: `A01_praga_puente_carlos.jpg`, `B03_estudiantes_taller.png`.
- `.png` = recorte sin fondo; `.jpg` = fondo completo.
- En el prompt va una sección **"IMÁGENES ADJUNTAS (USA EXACTAMENTE ESTOS NOMBRES)"** con nombre, tipo y escena. Además: *"Si falta alguna imagen, deja un placeholder gris con su nombre exacto."*
- Al usuario se le entrega la lista en **dos grupos**:
  1. **Fotos del cliente** (viajes reales, grupos, talleres, acción social): nombre de archivo, qué foto pedirle a Vanguardia Academics y si debe tener autorización de imagen.
  2. **Fotos de banco**: nombre, qué es y término de búsqueda en inglés (ej. *"Charles Bridge Prague sunrise"*).
- Bancos: Unsplash y Pexels (gratis, uso comercial), Freepik, Adobe Stock. Quitar fondos: remove.bg o Canva.
- Evitar fotos con logos visibles (aerolíneas, parques, marcas de autos, equipos de futbol).
- **Logo del cliente:** `VanguardiaAcademics_logo.png` (logo principal) y `VanguardiaAcademics_imago.png` (imagotipo). En el sitio existen versiones blanca y verde en `.webp`; pedir al cliente los PNG en alta resolución. Si no se adjuntan, usar solo el nombre en Nunito, sin inventar logotipo.

---

## 9. Plantilla del prompt base (copiar y completar)

```
Actúa como director de motion graphics 3D de técnica mixta (mixed media) y estratega de contenido viral para Instagram Reels. Diseña una animación de [60/75/80/90] segundos, formato vertical 9:16 (1080x1920, 30 fps), que explique [TEMA]. Es para la cuenta de Vanguardia Academics (@vanguardia.academics), empresa mexicana de viajes educativos al extranjero diseñados a la medida de cada institución. Audiencia principal: directores, coordinadores y docentes de preparatorias y universidades en México; también padres y estudiantes. Habla de "tú". Si puedes, entrégala exportable como MP4; si no, como animación reproducible a pantalla completa que yo pueda grabar.

SITIO DE REFERENCIA (CONSÚLTALO ANTES DE DISEÑAR)
- https://vanguardiaacademics.com/ → programas, pilares (enfoque personalizado, aprendizaje experiencial, compromiso social) y frases de la marca. No copies logotipos de terceros.

TONO
- [ej. inspirador y cercano / curioso y revelador / práctico y confiable para directores / emotivo (acción social)]

VERIFICACIÓN DE DATOS
- Verifica cada dato del destino y cada estudio en fuentes serias (sitios oficiales, UNESCO, OCDE, universidades). No inventes estadísticas.
- Datos de la empresa solo los que te doy, atribuidos: "según Vanguardia Academics".
- No prometas precios, fechas, becas, seguridad absoluta ni acuerdos con marcas que no te haya confirmado.

TÉCNICA: 3D + FOTOS REALES + MOTION GRAPHICS
- Three.js (WebGL) + línea de tiempo tipo GSAP; si no es posible, 2.5D.
- Objetos 3D que debes crear (no son fotos): [NOMBRE_3D: descripción — ej. GLOBO_3D con rutas de vuelo desde México, PASAPORTE_3D con sellos]
- Integración de fotos: RECORTE (PNG) / FONDO (JPG, blur 6–10 px, oscurecido 60%), sombra de contacto, luz arriba a la izquierda, rim light turquesa, gradación uniforme, capas.
- Efectos extra: HUD tipo tablero de aeropuerto, partículas, profundidad de campo, dolly-zoom, morphing.

FOTOS REALES DEL CLIENTE
- Úsalas tal cual: no las redibujes ni cambies los rasgos de nadie. No generes personas ni estudiantes con IA.

IMÁGENES ADJUNTAS (USA EXACTAMENTE ESTOS NOMBRES)
- VanguardiaAcademics_logo.png (logo) → marca de agua discreta y cierre
- X01_nombre.jpg (fondo) → escena 0–4 s
- ...
- Si falta alguna imagen, deja un placeholder con su nombre exacto.

ESTILO VISUAL
- Paleta: azul marino #122C79 (principal), fondo profundo #081640, turquesa #189293 / turquesa claro #3FC1C2 (acento y palabra clave), naranja #D1782D (cifras, sellos, botón), blanco #FFFFFF, arena #F4EDE3 (mapas y papel).
- Tipografía: Nunito Black (titulares), Jost SemiBold (subtítulos y textos), JetBrains Mono (HUD y datos).
- Elemento conductor: [pasaporte con sellos / ruta de vuelo / mochila / medidor de competencias]
- Barra de progreso superior de 0 a 100% (puede ser una ruta de vuelo).
- Cambio visual cada 3–4 s; nunca más de un elemento principal a la vez.
- Sin logotipos ni marcas de terceros dibujados (Disney, Ferrari, aerolíneas, equipos): solo como texto.
- Leyenda final en pequeño: [fuentes / "Programas sujetos a disponibilidad" / "Sin afiliación con ___"]

TIEMPO DE LECTURA Y ESPACIO PARA VOZ (PRIORIDAD)
- ~2.3 palabras/seg · subtítulos ≥1.5 s · pausa de 0.5 s entre escenas · cifras ≥2 s · palabra del CTA ≥3 s · 3D lento mientras hay texto.

ZONAS SEGURAS
- Nada en los 250 px superiores ni en los 400 px inferiores; 120 px libres a la derecha.

SUBTÍTULOS
- Quemados, tercio medio-inferior, 3–5 palabras por bloque, caja azul marino semitransparente, palabra clave en turquesa claro (karaoke), cifras en naranja.

GUION Y ESCENAS (los tiempos son la guía de sincronía)
[0–4 s] HOOK
Texto/voz: "..."
Visual: ...
[...]
[últimos s] CTA CON PALABRA CLAVE
Texto/voz: "Comenta [PALABRA] y te [beneficio]. Síguenos en Vanguardia Academics."
Visual: burbuja de comentario que escribe la palabra → botón "SEGUIR" con cursor que le da clic + "VANGUARDIA ACADEMICS", "VIAJES EDUCATIVOS A LA MEDIDA" y @vanguardia.academics. El último cuadro regresa al primero (loop).

AUDIO DE APOYO
- Música [inspiradora / cinematográfica ligera / electrónica cálida con toques acústicos, BPM], al 15–20% de volumen.
- Efectos: [despegue de avión, sello de pasaporte, tablero de aeropuerto, pasar página, clic, whoosh — sincronizados con acciones].

[ENTREGA FINAL — en producciones completas: nombre de archivo MP4, especificaciones, proyecto editable, portada 1080x1920, "no simules una exportación"]
```

---

## 10. Bloques de versión de audio (van aparte, después del prompt base)

**Versión A — la voz la graba el cliente o alguien de su equipo**
```
VERSIÓN: SIN VOZ
- No generes narración. Deja solo música, efectos y subtítulos.
- Respeta estrictamente los tiempos de cada escena y las pausas de 0.5 s entre escenas para que se pueda grabar encima con calma.
- Entrega además el guion limpio con marcas de tiempo, para leerlo mientras se graba.
- Mantén la música más baja (10–15%) en las partes con más texto para que la voz se escuche clara.
```

**Versión B — voz generada con IA**
```
VERSIÓN: CON VOZ IA
- Genera la narración del guion con voz IA en español latino (mexicano neutro), voz [femenina/masculina], tono cálido, cercano y confiable, como una guía de viaje que también es maestra. No imites la voz de ninguna persona real.
- Ritmo pausado-ágil (~2.3 palabras/seg) con pausas en [momentos clave].
- Sincroniza subtítulos palabra por palabra con la voz y ajusta las escenas a la duración real del audio, sin pasar de [duración] s.
- Aplica ducking: la música baja automáticamente cuando habla la voz.
```
Nota: la voz IA requiere una herramienta de voz conectada (ej. ElevenLabs). Conviene que el cliente apruebe una sola voz y se use en todos sus videos.

---

## 11. CTAs para la marca

- **Palabra clave + beneficio** (el cliente debe tener lista la respuesta por DM antes de publicar):
  - "Comenta **VIAJE** y te mandamos los destinos de este año."
  - "Comenta **PRAGA** / **SICILIA** / **MONTREAL**… y te enviamos el programa."
  - "Comenta **AULA** y te mandamos la guía para planear un viaje académico."
  - "Comenta **IB** y te explicamos cómo conectar el viaje con tu programa."
- **Envío por DM:** "Envíaselo al coordinador de tu escuela" / "Mándaselo a tus papás".
- **Pregunta de debate:** "¿A qué destino llevarías a tu grupo? Te leo en comentarios."
- **Contacto directo** (solo en la descripción o como texto pequeño): WhatsApp +52 999 102 1067.
- Cierre fijo: **botón SEGUIR + cursor + VANGUARDIA ACADEMICS + @vanguardia.academics**, con loop al primer cuadro.

---

## 12. Reglas de precisión y pendientes del cliente

- **Verificar cada dato** del destino y citar la fuente en pantalla (pequeña) y en las notas finales con enlaces.
- **Aclarar el universo de los datos** ("estudiantes encuestados en EE. UU.", "según la OCDE").
- **Atribuir los datos de la empresa:** "según Vanguardia Academics".
- **Lo que no ha pasado se dice como posibilidad** ("podrás", "el programa incluye", nunca "garantizado").
- **Pendientes que hay que confirmar con el cliente antes de usarlos en un video:**
  - **Años de experiencia:** el sitio dice "más de 23 años" (inicio), "27 años" y "25+ años" (Quiénes somos). Mientras no se confirme, usar **"más de 20 años"**, que es cierto en los tres casos.
  - **Nombre del programa de Disney:** "Disney Yes Program" o "Disney Youth Education Series", y si existe un acuerdo formal. Hasta confirmarlo: "talleres en Disney Imagination Campus" y leyenda de sin afiliación.
  - **Ferrari, Ducati y Pagani:** si son visitas acordadas con las marcas o visitas abiertas al público. Solo texto, sin logos.
  - **Cifras de acción social:** "más de 10,000 personas ayudadas", "50+ proyectos al año", "100 % participación estudiantil": usarlas con "según Vanguardia Academics".
  - **Precios, duración, fechas, niveles escolares, seguros y acompañamiento:** no aparecen en el sitio; no mencionarlos sin datos del cliente.
  - **Testimonios:** el sitio no tiene; pedirlos con nombre, escuela y permiso.
- **Contradicciones en prompts del usuario:** resolverlas y avisar en una línea.

---

## 13. Reglas legales y éticas

- **Menores de edad:** muchos estudiantes son menores. Usar fotos o videos con caras solo si el cliente confirma que tiene **autorización de imagen de padres o tutores** y de la escuela. Si no, usar fotos de espaldas, a contraluz, de grupo lejano, manos o desenfocadas. Nunca poner nombres completos, escuelas ni ubicaciones en tiempo real de menores.
- **No generar estudiantes ni personas con IA** que parezcan alumnos reales del cliente: se vería como testimonio falso.
- **Sin logotipos de terceros** dibujados por la IA: Disney, Ferrari, Ducati, Pagani, aerolíneas, universidades, equipos deportivos, solo como texto y con leyenda "Sin afiliación con ___" si no hay acuerdo confirmado.
- **Monumentos y lugares:** usar fotos de banco con licencia; algunos lugares (por ejemplo la Torre Eiffel iluminada o parques temáticos) tienen restricciones de uso comercial: evitarlos o confirmarlo.
- **Promesas comerciales:** no prometer resultados académicos, admisiones universitarias, becas ni "100 % seguro".
- **Acción social:** mostrar a las comunidades con dignidad y con permiso; nada de "pobreza como espectáculo". Fotos reales del cliente, no de banco, presentadas como si fueran sus proyectos.
- Leyendas en el último cuadro, según el caso:
  - "Programas sujetos a disponibilidad y adaptables a cada institución."
  - "Sin afiliación con [marca]."
  - "Datos según [fuente]."
  - "Fotos de viajes de Vanguardia Academics." / "Imágenes de referencia."
- Sorteos y regalos: reglas en la descripción y aclaración de que Instagram no patrocina ni administra la dinámica.

---

## 14. Banco de ideas de videos (aún no producidos)

| # | Tema | Línea | Palabra CTA | Duración |
|---|---|---|---|---|
| 1 | "Cada destino es un aula": qué es el aprendizaje experiencial y por qué funciona | Aprendizaje | AULA | 60 s |
| 2 | Berlín y Praga: Green Thinking, la sostenibilidad vista desde las empresas | Destino | VERDE | 75 s |
| 3 | Sicilia: 3,000 años de historia en una isla (griegos, romanos, árabes, normandos) | Destino / historia | SICILIA | 75 s |
| 4 | Orlando: cómo se aprende creatividad en Disney Imagination Campus | Destino | CREAR | 60 s |
| 5 | España: el negocio detrás del deporte (marketing, estadios, patrocinios) | Destino | GOL | 75 s |
| 6 | Montreal: emprendimiento y liderazgo en una ciudad bilingüe | Destino | MONTREAL | 60 s |
| 7 | Italia y la ingeniería de alta gama: del boceto al motor | Destino | MOTOR | 75 s |
| 8 | Mérida: lo que un estudiante aprende construyendo un piso de cemento | Acción social | AYUDA | 60 s |
| 9 | 5 preguntas que todo director debe hacer antes de contratar un viaje académico | Guía | GUÍA | 80 s |
| 10 | Cómo conectar un viaje con el currículo IB (CAS, PAI) o SEP | Guía | IB | 80 s |
| 11 | Qué habilidades desarrolla viajar (idiomas, autonomía, pensamiento global) según estudios | Aprendizaje | VIAJE | 60 s |
| 12 | Mapa de los 7 destinos de Vanguardia en 60 s (globo 3D con rutas) | Marca | VIAJE | 60 s |

---

## 15. Instrucción para arrancar una nueva sesión

> "Eres el director creativo de Reels de Atlas Path para su cliente Vanguardia Academics. Sigue esta guía al pie de la letra: investiga y verifica el tema en la web, escribe el guion con la estructura viral y los tiempos de lectura, entrégame **un solo prompt base** en un bloque de código con fotos reales + 3D, después las versiones A y B de audio por separado, la lista de fotos (del cliente y de banco) con nombres de archivo y términos de búsqueda, y al final notas breves con los datos verificados, lo que debe confirmar el cliente y las fuentes. El tema de hoy es: **[TEMA]**."
