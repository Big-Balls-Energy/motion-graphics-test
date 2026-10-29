## Verificación de datos

- **«Si tienes entre 30 y 45 años»**: quien tenía entre 2 y 17 años en 1998 tiene hoy entre 30 y 45. Es una estimación del público, no un dato de ventas.
- **1998**: *The Legend of Zelda: Ocarina of Time* salió para Nintendo 64 en noviembre de 1998. «28 años después» = 2026.
- **99/100**: es la calificación más alta registrada en Metacritic (Guinness World Records: *most critically acclaimed videogame on Metacritic*; lista de GameSpot con los juegos mejor calificados de Metacritic). En pantalla: «METACRITIC · EL MEJOR CALIFICADO DE LA HISTORIA».
- **+7,600,000 copias**: cifra de Guinness World Records (7.6 millones). La voz dice «más de 7.6 millones», igual que la pantalla («+7,600,000»).
- **3X preventas**: según el comunicado de Nintendo of America de 1998, las preventas en Estados Unidos triplicaban las de cualquier otro juego anterior. En pantalla: «3X PREVENTAS · en EE. UU., frente al récord anterior · según Nintendo (1998)».
- **Remake para Switch 2, 5 de noviembre**: anunciado en el Nintendo Direct del 8 de septiembre de 2026 (Game Informer, GameSpot, Engadget y Gematsu). Gráficos nuevos, música orquestal, voces y tocar la ocarina tarareando al micrófono vienen de esa misma cobertura (Gearlive: «hum the songs»). En pantalla: «5 NOV 2026 · REMAKE PARA SWITCH 2».
- **Journal of Consumer Research**: Lasaleta, Sedikides y Vohs (2014), «Nostalgia Weakens the Desire for Money», *JCR* 41(3), 713–729, DOI 10.1086/677227. En sus experimentos, las personas a las que se les indujo nostalgia estuvieron dispuestas a pagar más por productos y le dieron menos valor al dinero. En pantalla: «resultado experimental».
- **«Nintendo lo sabe: vende recuerdos… y una primera aventura a sus hijos»**: es la lectura de marketing del caso (guion del brief), no una declaración de Nintendo. Las tarjetas «RECUERDOS · MILLENNIALS» y «PRIMERA AVENTURA · SUS HIJOS» son ilustrativas.
- **«Hace 20 años»** y el producto «retro → EDICIÓN 2026» del cofre son un ejemplo genérico, sin marca.
- **Leyenda final**: «Caso de estudio. Sin afiliación con Nintendo. Las marcas mencionadas pertenecen a sus dueños.»

## Fotos, marcas y tipografías

- **Avatar (AV01–AV09)**: se usan tal cual, sin redibujar ni cambiar rostro, ropa, colores o estilo; solo escala, posición, volteo (AV01 en el epílogo), sombra de contacto, rim light dorado y la gradación de cada acto. AV01 es el recorte de alta resolución; AV02–AV09 salen de la hoja de personaje (más suaves al ampliarlos). La mano del pulgar de AV08 se recortó aparte para el clic de «SEGUIR». La hoja dice «JUAN CARLOS»; el cintillo usa «GUILLERMO ARCOS · CEO DE ATLAS PATH», como pide el brief.
- **Lip-sync**: no hay herramienta de animación facial disponible, así que el avatar cambia de pose y respira, sin simular la boca.
- **Z01_sala_tv_90s**: desenfocada; los carteles y la pantalla con personajes de terceros quedaron tapados. **Z03_consola_n64** y **Z05_consola_switch2**: se quitaron los logotipos. **Z04_ocarina_barro**: se quitó una marca de agua de banco de imágenes; conviene usar la foto con licencia. **Z02_nino_jugando_90s**, **Z09** y **Z10**: fondos con desenfoque y la gradación del acto.
- **Scripts de preparación** (se corrieron una vez sobre los originales adjuntos, que quedan en `assets/fotos/originales/`): `tools/preparar_fotos/` (`poses.py` recorta AV02–AV09 de la hoja, `av01.py` quita el fondo de AV01, `fotos_oc.py` limpia Z01 y Z03, `z04.py` y `z05.py`).
- **Faltan Z06_bosque_neblina.jpg, Z07_cueva_antorchas.jpg y Z08_polaroids.png**: aparecen como marcadores grises con su nombre exacto. Para reemplazarlos basta copiar los archivos en `assets/fotos/` con esos nombres y volver a renderizar.
- **Nintendo y Zelda**: ningún personaje, villano, criatura, escenario, arma, objeto icónico, logotipo, captura, arte oficial ni música de la saga. El nombre del juego solo aparece como texto. La tele, el cartucho genérico «1998», el mapa, el portal, el mundo low-poly, EL OLVIDO, el arma de la nostalgia y el cofre son diseños originales; las consolas solo aparecen en las fotos adjuntas.
- **Música y efectos**: todo es original (`tools/audio.py`). La ocarina toca tres notas genéricas (Mi–Re–Sol) que no son ninguna canción existente, y la fanfarria también es propia.
- **Logo**: no se adjuntó `AtlasPath_logo.png`, así que se usa el logo oficial del repositorio (`assets/AtlasPath_logo.png`), como marca de agua y en el cierre. El usuario del cierre es **@Atlas_Path** (regla de la marca), no «@ATLASPATH».
- **Tipografías** (licencia OFL, en `fonts/`): Cinzel Bold/Black para los títulos de acto, Montserrat 500/700/900 para textos y subtítulos, y Press Start 2P solo para ventanas emergentes, años y contadores.
- **Tiempos**: los actos siguen la voz y terminan en 31.0, 47.0 y 64.2 s; el brief los marcaba en 28, 45 y 62 s.

## Fuentes

- Game Informer — The Legend of Zelda: Ocarina of Time remake launches this November: https://www.gameinformer.com/nintendo-direct/2026/09/08/the-legend-of-zelda-ocarina-of-time-remake-launches-this-november
- Engadget — The Switch 2 remake of Ocarina of Time arrives November 5: https://engadget.com/2252620/switch-2-remake-of-legend-of-zelda-ocarina-of-time-arrives-november-5
- Gematsu — The Legend of Zelda: Ocarina of Time remake launches November 5: https://www.gematsu.com/2026/09/the-legend-of-zelda-ocarina-of-time-remake-launches-november-5
- Gearlive — Ocarina of Time on Switch 2, November 5: hum the songs: https://www.gearlive.com/news/article/ocarina-of-time-switch-2-november-5-hum-the-songs
- GameSpot — The best video games of all time, according to Metacritic: https://gamespot.com/articles/the-best-video-games-of-all-time-according-to-metacritic/1100-6501371/
- Guinness World Records — Most critically acclaimed videogame (Metacritic): https://www.guinnessworldrecords.com/world-records/455351-most-critically-acclaimed-videogame-metacritic
- Guinness World Records — Best-selling action-adventure videogame on a Nintendo platform: https://guinnessworldrecords.com/world-records/105392-best-selling-action-adventure-videogame-on-a-nintendo-platform
- Nintendo of America (1998) — Press Release: Nintendo Promises More 'Zelda' on the Way (copia): https://morguefile.wiki/wiki/Press_Release:_Nintendo_Promises_More_%27Zelda%27_on_the_Way
- Nintendo World Report — Zelda pre-orders look strong: https://www.nintendoworldreport.com/pr/8279/zelda-pre-orders-look-strong
- Lasaleta, Sedikides y Vohs (2014), Journal of Consumer Research (PDF): https://carlsonschool.umn.edu/sites/carlsonschool.umn.edu/files/2026-01/vohs-et-al-2014-nostalgia-weakens-desire-money.pdf
- DOI del artículo: https://doi.org/10.1086/677227
- Phys.org — The nostalgia effect: Do consumers spend more?: https://phys.org/news/2014-07-nostalgia-effect-consumers.html
