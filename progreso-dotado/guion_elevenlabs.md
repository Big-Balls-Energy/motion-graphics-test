# Narración para ElevenLabs — "El efecto de progreso dotado" (Atlas Path)

**Ajustes sugeridos**
- Modelo: Eleven Multilingual v2 (respeta las etiquetas `<break>`).
- Voz: femenina, español latinoamericano/mexicano. En la Voice Library filtra por *Spanish* + acento latinoamericano, con uso tipo *Social media* o *Narrative*.
- Stability 40 % · Similarity 75 % · Style 35 % · Speaker boost activado · Speed 1.05. Así suena animada pero profesional.
- Duración objetivo: 58 s como máximo. Si queda un poco más larga, el script la acelera hasta un 8 % sin cambiar el tono.
- Exporta en MP3 (44.1 kHz, 128 kbps o más).

**Texto (copiar tal cual)**

```
¿Por qué esta cafetería te regala dos sellos… antes de que compres nada?
No es generosidad. Es psicología. Se llama: el efecto de progreso dotado.
En un estudio, un autolavado repartió dos tarjetas. Una pedía ocho lavados. La otra pedía diez… pero ya traía dos sellados.
Las dos pedían exactamente… <break time="0.2s" /> ocho compras.
Con la tarjeta en blanco, solo el… <break time="0.3s" /> diecinueve por ciento la terminó.
Con la tarjeta empezada: el… <break time="0.3s" /> treinta y cuatro por ciento. <break time="0.3s" /> Casi el doble.
Cuando sientes que ya avanzaste, tu cerebro no quiere dejar algo a medias.
Ya no ves ocho pasos por hacer: ves una meta… <break time="0.2s" /> veinte por ciento cumplida.
Está en perfiles que empiezan al veinte por ciento, en apps que te regalan puntos de bienvenida, y en cursos que marcan la primera lección como lista.
¿Tienes un negocio? No regales descuentos. <break time="0.4s" /> Regala progreso.
Sigue a Atlas Path para más trucos de psicología que usan las marcas contigo.
```

**Para meterla en el video:** `VOICE_FILE=narracion.mp3 WHISPER_DIR=/ruta/whisper ./make.sh`.
Whisper transcribe la narración, la alinea palabra por palabra con el guion y la animación se ajusta sola.
