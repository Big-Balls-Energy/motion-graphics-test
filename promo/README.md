# Promo vertical · Big Balls Energy Art

Video promocional de 30 s en motion graphics para captar clientes potenciales.
Formato vertical 9:16 (1080×1920, 60 fps) para Reels, TikTok y Shorts.

**Video final:** [`out/promo-1080x1920-60fps.mp4`](out/promo-1080x1920-60fps.mp4)

> ⚠️ **Textos provisionales.** No fue posible acceder a `art.bigballsenergy.com`
> al crear esta versión, así que los textos de `content.js` son genéricos.
> Sustitúyelos por los del sitio y vuelve a renderizar.

## Guion (sincronizado a 120 BPM)

| Tiempo | Escena | Qué pasa |
|---|---|---|
| 0–4 s | Intro | Una bola cae y rebota a ritmo, llegan dos más, giran en espiral y explotan revelando el logo |
| 4–8 s | Gancho | "¿Tu marca se ve aburrida?" → una bola rompe "aburrida" → "¡Dale energía!" |
| 8–14 s | Servicios | Cuatro tarjetas entran una por beat |
| 14–20 s | Portafolio | Muro de obras en columnas con parallax |
| 20–25 s | Razones | Tres frases con barridos de color a pantalla completa |
| 25–30 s | Llamada a la acción | Logo, "¿Listo para destacar?", botón "Cotiza tu proyecto" y la URL |

## Archivos

| Archivo | Para qué |
|---|---|
| `content.js` | **Todos los textos y colores.** Es lo único que hace falta editar |
| `anim.js` | Motor de la animación (canvas, determinista) |
| `index.html` | Vista previa con reproducción y barra de tiempo |
| `music.py` | Banda sonora original sintetizada (sin samples, sin derechos de terceros) |
| `render.mjs` | Render cuadro a cuadro con Chromium + codificación con ffmpeg |
| `fonts/` | Anton e Inter (licencia SIL OFL) |

## Cambiar textos y volver a renderizar

1. Edita `content.js`. Para usar imágenes reales del portafolio, ponlas en
   `promo/assets/` y añade sus rutas a `portfolioImages`.
2. Revisa el resultado en la vista previa:
   ```bash
   cd promo && python3 -m http.server 8000
   # abre http://localhost:8000  (también acepta ?t=12.5 para un frame fijo)
   ```
3. Renderiza:
   ```bash
   python3 promo/music.py     # genera out/music.wav
   node promo/render.mjs      # genera out/promo-1080x1920-60fps.mp4
   ```
   Para sacar frames sueltos: `node promo/render.mjs --stills 2.5,6.3,27`.

Requisitos: Node 18+ con Playwright (Chromium), Python 3 con numpy, y ffmpeg.

## Especificaciones de salida

- H.264 High 4.2, 1080×1920, 60 fps, yuv420p, BT.709, CRF 15
- AAC 320 kbps, 48 kHz estéreo, normalizado a −14 LUFS / −1 dBTP (estándar de redes)
- `+faststart` para que empiece a reproducirse antes de descargarse entero
