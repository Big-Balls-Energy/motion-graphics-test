# Prueba de HyperFrames (1 nov 2026)

HyperFrames (de HeyGen, código abierto) es otra forma de hacer video con HTML: se escribe HTML + GSAP y la CLI lo renderiza a MP4. Esta carpeta es una **prueba de combinación** con nuestro sistema de canvas. **No sustituye nada del flujo actual.**

Resultado: `Atlas_Path_Prueba_HyperFrames.mp4` (15.8 s, 1080×1920, 30 fps, −13.3 LUFS).

| Tramo | Hecho con | Qué hace |
|---|---|---|
| 0–3.4 s | **HyperFrames** (`compositions/gancho.html`) | Gancho de tipografía cinética: «¿Tu negocio ya sale en FOTOS de Google?» con visor y escaneo |
| 3.2–11.5 s | **Nuestro reel 69** (canvas) metido como video dentro de HyperFrames | Fragmento 17.75–26.05 s de `busqueda-visual`, con destello de entrada y *punch-ins* de cámara hechos en HyperFrames sobre las cifras |
| 11.4–15.8 s | **HyperFrames** (`compositions/cta.html`) | Cierre con logo, ATLAS PATH, @Atlas_Path y botón SEGUIR con cursor y clic |

Audio: la mezcla con voz del reel 69 bajo su fragmento; la música y el clic del mismo reel en el gancho y el cierre. Al final se normalizó con `loudnorm` (HyperFrames no normaliza a −14 LUFS por sí solo).

## Instalación en este entorno
```bash
npm i -g hyperframes            # v0.8.226
hyperframes telemetry disable   # para que no mande datos de uso
# No puede bajar su propio Chrome (storage.googleapis.com bloqueado para él); usar el Chromium de Playwright:
export HYPERFRAMES_BROWSER_PATH=/opt/pw-browsers/chromium-1243/chrome-linux64/chrome
```
También se instalaron sus skills (`hyperframes`, `hyperframes-cli`, `hyperframes-registry`, `media-use`).

## Recrear la prueba
Copiar a `assets/` desde `busqueda-visual/`: `Atlas_Path_Busqueda_Visual-sin-voz.mp4` → `reel.mp4`, `audio/mezcla-con-voz.wav` → `mezcla.wav`, `audio/musica-sola.wav` → `musica.wav` y `audio/efectos-solos.wav` → `efectos.wav` (no se suben al repo por su peso). Después:
```bash
hyperframes check --json
hyperframes snapshot --at 1.2,5.1,13.8 --no-end
hyperframes render -w 2 -o raw.mp4
ffmpeg -i raw.mp4 -af loudnorm=I=-14:TP=-1.5:LRA=11 -c:v copy -c:a aac -b:a 192k out.mp4
```

## Lo que aprendí
- **Velocidad:** 15.8 s en 77 s con 2 núcleos (≈ 4.9 s de cómputo por segundo de video). Nuestro `render_paralelo.sh` tarda ≈ 8 s por segundo.
- **Combinar funciona bien:** un MP4 nuestro entra como `<video>` (hijo directo del root, con `data-media-start` para recortar) y HyperFrames le pone transiciones, zooms y escenas antes y después. También se puede al revés: renderizar un tramo en HyperFrames y unirlo con ffmpeg a un reel nuestro.
- **Registro de ~450 bloques** (`hyperframes catalog --query "…"`): transiciones, subtítulos tipo karaoke, contadores, tarjetas sociales, efectos. Algunos dibujan logotipos reales (p. ej. `instagram-follow`). Desde el 1 nov 2026 los logos se permiten en uso editorial (ver `CLAUDE.md`), pero en el CTA propio de Atlas Path seguimos usando nuestro botón SEGUIR.
- **Revisión integrada:** `check` detectó errores reales (un tween de `letterSpacing` que da saltos, textos que se quedan muy poco tiempo en pantalla) y `snapshot` arma hojas de contacto.
- **Cuidados:**
  - `fromTo` dentro de un `for` necesita `immediateRender: false`, si no aparece un punto fantasma antes de tiempo (pasó sobre «SEGUIR»).
  - GSAP debe ir local (`assets/gsap.min.js`): en un render la CDN falló.
  - No usar sus funciones de nube, `publish` ni las de HeyGen (cobran créditos de HeyGen); todo aquí fue local y gratis.

## Ideas para combinarlo en reels futuros
1. **Ganchos y cierres** en HyperFrames (rápidos de iterar y con plantillas) y el cuerpo en nuestro canvas.
2. **Transiciones y zooms** de HyperFrames sobre el MP4 de canvas, sin volver a renderizar el canvas.
3. **Subtítulos** del registro (`caption-pill-karaoke`, `caption-highlight`) como alternativa a los nuestros.
