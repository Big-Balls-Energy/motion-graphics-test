# Producción automática de reels — checklist de cada corrida

Cada corrida de la tarea programada hace **un reel completo** sin preguntar nada al usuario. Sigue este orden.

## 0. Preparar
1. Repositorio en `/home/claude/motion-graphics-test` (si no existe: `add_repo` Big-Balls-Energy/motion-graphics-test con acceso push, y `git clone --depth 1 --no-single-branch` con timeout de 10 min). Rama `prueba-social-reel`. `git pull` antes de empezar.
2. Lee `CLAUDE.md`, `GUIA-REELS.md`, `REELS-HECHOS.md` y, en el proyecto de claude.ai, `claude/reglas-automatizacion-creditos.md` (reglas de créditos: mandan sobre todo lo demás).
3. Comprueba la red: `curl -sS -o /dev/null -m 10 -w "%{http_code}" https://storage.googleapis.com` y `https://d8j0ntlcm91z4.cloudfront.net`. `000` = bloqueado: no generes voz ni imágenes (no gastes créditos), haz el reel sin voz y avisa que hay que activar **Configuración → Capacidades → Allow network egress** en claude.ai.
4. Revisa el saldo de Higgsfield (`balance`).

## 1. Elegir el tema
- Categoría = la **siguiente en la rotación** después de la última fila de `REELS-HECHOS.md` (1 Noticia IA/tecnología → 2 Psicología del marketing → 3 Caso de marca → 4 Personaje/empresario → 5 Consejo práctico).
- Busca en la web (WebSearch) lo más fuerte y verificable **de esta semana** para noticias; para las demás, el tema con más potencial viral para emprendedores de México y Latinoamérica. **Nunca repitas** un tema de la tabla.
- Verifica cada dato en fuentes serias; lo futuro en condicional; estimaciones marcadas.

## 2. Producir (según `GUIA-REELS.md`, sección 4)
- `bash herramientas/nuevo_reel.sh <carpeta>` con base `precio-99` o `consejos-ia`. Duración 60 s (concepto), 75 s (caso o historia) u 80–90 s (noticia compleja).
- Estructura viral: hook 0–4 s, giro, dato con fuente, explicación, ejemplos, aplicación, CTA con palabra clave (≥ 3 s sola), loop.
- Fotos: **primero reutiliza** las de `*/assets/fotos/`; genera en Higgsfield solo lo que falte (`gpt_image_2_5` low 1k, recortes con fondo transparente, máx. 10, reserva de 20 créditos). Personas reales: solo siluetas o tipografía (no generar ni redibujar caras).
- Voz **obligatoria**: Fernanda (`ARmPWZKt7WpXh6QDHA6x`, `eleven_v4`), una llamada por bloque, máx. 20 bloques, **sin reintentos**. Error de créditos de ElevenLabs → para la voz, entrega sin voz, avisa y desactiva la tarea programada «Reel automático Atlas Path» (`list_triggers` → `update_trigger enabled=false`).
- Colocar voz: `bajar_tomas.py` → agregar `SLOTS` en `voz_tomas.py` → `silencios.sh` → ajustar karaoke `[voz desde, voz hasta]` en `SUBS_RAW`.
- Música: adapta `tools/audio.py` (BPM = compases × 240 / duración).
- Revisión visual con `render.js snap` + `hoja.py` (varias rondas: zonas seguras, textos legibles, nada encimado). `tools/guion.py` debe quedar sin errores.
- Render: `bash herramientas/render_paralelo.sh <carpeta> <scratchpad>/cuadros <dur> 2 8811` en segundo plano (2 núcleos). Revisa hojas de cuadros cada 3 s. Codifica con `herramientas/codificar.sh` (con y sin voz, −14 LUFS). Portada con `render.js … cover portada.png`.
- Entregables: `Atlas_Path_<Tema>.mp4`, `-sin-voz.mp4`, `portada.png`, `guion-con-tiempos.md`, `subtitulos.srt`, `descripcion-instagram.md` (descripción, CTA, hashtags y aviso de la respuesta por DM), `tools/notas.md` (datos, fuentes con URL, créditos gastados).

## 3. Entregar
1. Agrega la fila del reel a `REELS-HECHOS.md`.
2. `git add`, commit en español (plantilla de la guía, con las líneas de atribución de la sesión), `git pull --rebase origin prueba-social-reel` y `git push`. Si falla por red, reintenta con espera de 2, 4, 8 y 16 s.
3. Envía con SendUserFile el MP4 con voz y la portada (`display: render`) y la descripción (`attach`).
4. Mensaje final breve en español: tema, categoría, duración, palabra CTA, créditos gastados (ElevenLabs y Higgsfield), qué revisar y fuentes como enlaces.
5. Notificación al celular (PushNotification, menos de 200 caracteres): «Nuevo reel listo: <título> (<dur> s). Palabra CTA: <PALABRA>.»
