# Reels de Atlas Path — convenciones

Cada carpeta (`prueba-social/`, `arquetipos/`, `viaje-heroe/`…) es un reel de 60 s, 1080×1920, 30 fps, hecho con `index.html` (canvas determinista) y renderizado con `tools/render.js` + ffmpeg.

## Siempre
- Marca de agua: logo de Atlas Path arriba a la izquierda, chico (100 px) y semitransparente (70 %), sobre placa clara, justo debajo de los 250 px superiores.
- Cierre/CTA: logo grande en avatar + «ATLAS PATH» + `@Atlas_Path` + botón SEGUIR con cursor y clic; el último medio segundo regresa al primer cuadro (loop).
- Zonas seguras: nada clave en los 250 px superiores, los 400 px inferiores ni los 120 px de la derecha.
- Subtítulos: 3–5 palabras por bloque, ≥ 1.5 s, ≤ 2.3 palabras/s, karaoke con palabra clave resaltada; 0.5 s de pausa entre escenas. Validar con `tools/guion.py`.
- Sin logotipos, tipografías ni personajes reales: las marcas solo como texto.
- Verificar los datos de noticias o estadísticas antes de animarlos y marcar las estimaciones como tales.

## Voz en off (ElevenLabs)
- Voz: «Fernanda – Smooth and Articulate» (`ARmPWZKt7WpXh6QDHA6x`), modelo `eleven_v4`, con etiquetas de tono suaves.
- Generar **una toma independiente por bloque** (nunca una narración larga cortada después): así no hay palabras cortadas.
- Armar con `voz-tools/voz_tomas.py <proyecto>` (agregar los tiempos del proyecto en `SLOTS`): recorta por energía, acorta solo silencios, fundidos de 10 ms, acelera como máximo 10 %.
- Mezcla final normalizada a −14 LUFS; entregar `<proyecto>-con-voz.mp4` y `<proyecto>-sin-voz.mp4`.
