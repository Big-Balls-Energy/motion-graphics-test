# Reporte de control de calidad — Arias_Medical_Clinic_Escleroterapia_60s.mp4

Detalle técnico automático: `qa_tecnico.json` (generado con `scripts/qa_video.py`).

## Verificación obligatoria
| # | Requisito | Resultado | Cómo se verificó |
|---|---|---|---|
| 1 | El archivo existe y se puede abrir | ✅ Decodifica completo sin errores | `ffmpeg -v error -i … -f null -` sin mensajes |
| 2 | Duración exacta de 60 s | ✅ Vídeo 60,000 s (1800 cuadros) · Audio 60,000 s · inicio de ambas pistas en 0,000 s | `ffprobe` |
| 3 | 1080 × 1920, relación 9:16 | ✅ 1080×1920, 30 fps, yuv420p (BT.709) | `ffprobe` |
| 4 | Vídeo H.264 y audio AAC | ✅ H.264 High @ ~9,9 Mbps · AAC-LC 48 kHz estéreo 262 kbps · `faststart` | `ffprobe` |
| 5 | Narración y subtítulos sincronizados | ✅ Los 22 subtítulos caen dentro de su frase de locución (tiempos medidos del audio real, cortes alineados con las pausas) | `qa_video.py` |
| 6 | Sin cuadros negros accidentales ni cortes abruptos | ✅ `blackdetect` y `freezedetect` sin incidencias; transiciones con fundido/zoom de 0,4 s entre todos los planos | `ffmpeg` |
| 7 | Logotipo y textos legibles en teléfono | ✅ Textos revisados a 360×640 (tamaño de teléfono); títulos ≥ 60 px, subtítulos 44 px con fondo, etiquetas 32 px con fondo, aviso legal 29 px; todo dentro de las áreas seguras de Reels (márgenes superior/inferior y columna de botones). ⚠️ Logotipo oficial: ver nota | Revisión visual de cuadros extraídos del MP4 |

## Audio
- Sonoridad integrada −14,0 LUFS, pico real −1,5 dBTP (objetivo de plataformas sociales).
- Inteligibilidad en la mezcla final (con música y efectos): transcripción automática con Whisper-small,
  WER medio 1,6 %, idéntico a la voz aislada. Las dos discrepancias ("várices" → "válvices",
  "Arias" → "áreas") son sesgos conocidos del reconocedor; aparecen también con voces nativas grabadas.
- Seseo latinoamericano forzado en la síntesis (c/z → /s/), verificado acústicamente.

## Nota sobre el logotipo
El entorno de producción tenía bloqueado el dominio `ariasmedical.com`, por lo que **no fue posible
descargar el archivo oficial del logotipo**. Para no inventarlo ni alterarlo, el cierre presenta el nombre
"ARIAS MEDICAL CLINIC" en tipografía. Integrarlo solo requiere recomponer (≈5 min, sin volver a renderizar
el 3D): ver README → "Logotipo oficial".

## Revisión médica
Ver `control_calidad_medica.md` (anatomía, dirección del reflujo, válvulas, acceso intravascular, mecanismo
endotelial, cierre no instantáneo, circulación por venas funcionales, distinción frente a otras técnicas y
ausencia de promesas de resultados).
