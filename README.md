# Meta Ads 2026 · Atlas Path — Motion Graphics 40 s

Spot promocional vertical para el curso presencial **“Meta Ads 2026: Facebook & Instagram Ads”** de Atlas Path (Xalapa, Veracruz).

**Entregable final:** `out/AtlasPath_MetaAds2026_40s.mp4`

| Especificación | Valor |
| --- | --- |
| Duración | 40.0 s (1,200 frames) |
| Resolución | 1080 × 1920 (9:16) |
| Velocidad | 30 fps |
| Video | H.264 (yuv420p, CRF 16) |
| Audio | AAC 320 kbps, 48 kHz estéreo, ≈ -14 LUFS |

## Storyboard (8 escenas × 5 s)

| # | Tiempo | Mensaje | Animación principal |
| --- | --- | --- | --- |
| 1 | 00–05 | DEJA DE IMPROVISAR. / EMPIEZA A **DOMINAR** META ADS. | Red 3D de datos con vuelo de cámara que se reorganiza en esfera |
| 2 | 05–10 | META ADS 2026 / FACEBOOK + INSTAGRAM ADS / CURSO PRESENCIAL · ATLAS PATH | Escenario con suelo en perspectiva, núcleo icosaédrico, íconos 3D en órbita, Administrador de anuncios conceptual |
| 3 | 10–15 | CREA CAMPAÑAS CON ESTRATEGIA. / ANALIZA. OPTIMIZA. ESCALA. | Embudo 3D (TOFU/MOFU/BOFU) que se transforma en barras 3D + curva de crecimiento + KPIs ilustrativos |
| 4 | 15–20 | ADVANTAGE+ · ANDROMEDA / INTELIGENCIA ARTIFICIAL CON CLAUDE | Red neuronal 3D con pulsos de activación, paneles de análisis/reporte, onda luminosa |
| 5 | 20–25 | 10 SESIONES. / 20 HORAS PRESENCIALES. / TU CAMPAÑA REAL. | Números extruidos 3D, línea de tiempo de 10 sesiones que se transforma en interfaz de campaña → “Campaña activa” |
| 6 | 25–30 | SOLO 10 LUGARES. / APRENDE EN UN GRUPO REDUCIDO. | Anillo 3D de 10 puntos que se iluminan con órbita de cámara |
| 7 | 30–35 | PRIMERA GENERACIÓN / $3,490 MXN / IVA INCLUIDO | Fondo claro, contador tipo rodillo que se fija en $3,490, “Antes $4,900” tachado, luz recorriendo el contorno |
| 8 | 35–40 | TU PRÓXIMA CAMPAÑA COMIENZA AQUÍ. / ATLAS PATH · XALAPA / APARTA TU LUGAR. | Elementos que convergen en una esfera de conexiones → morphing al logotipo; CTA con indicador de WhatsApp; salida a negro |

Las métricas de las gráficas (CTR, CPC, ROAS, etc.) son **ilustrativas** y así se rotulan en pantalla.

## Estructura del proyecto

```
src/
  timeline.json        fuente única de tiempos (escenas + efectos de sonido)
  theme.ts             paleta Atlas Path, tipografía Jost, easing
  lib/space.ts         motor 2.5D (rotación + proyección en perspectiva)
  components/          tipografía cinética, glassmorphism, partículas, íconos
  scenes/S1…S8         una composición por escena
  Video.tsx            secuencias, transiciones (zoom-through + barrido de luz), audio
audio/
  generate_soundtrack.py  música y efectos sintetizados desde cero (sin samples)
public/
  brand/               logotipo original + capas claras (globo, manos, texto) para el morphing
  fonts/               Jost (la tipografía del folleto)
  audio/soundtrack.wav
```

## Cómo editar y volver a renderizar

```bash
npm install
npm run studio            # editor visual de Remotion (vista previa en vivo)
npm run audio             # regenera la banda sonora (requiere python3 + numpy + scipy)
npm run render            # exporta out/AtlasPath_MetaAds2026_40s.mp4
```

Si Remotion no puede descargar su Chromium, apunta a uno local:
`REMOTION_BROWSER=/ruta/a/chrome-headless-shell npm run render`.

Para cambiar textos, edita la escena correspondiente en `src/scenes/`. Para mover un efecto de sonido, cambia su frame en `src/timeline.json` y ejecuta `npm run audio`.
