// Renderiza la animación cuadro a cuadro con Chromium (Playwright) y la
// codifica con ffmpeg.
//
//   node promo/render.mjs                    → promo/out/promo-1080x1920-60fps.mp4
//   node promo/render.mjs --stills 1,2.5,6   → PNGs sueltos en promo/out/stills/
//   node promo/render.mjs --fps 30 --workers 2
import { createRequire } from "node:module";
import { spawn } from "node:child_process";
import { createServer } from "node:http";
import { readFile, mkdir, writeFile, access } from "node:fs/promises";
import { extname, join, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("playwright");

const ROOT = dirname(fileURLToPath(import.meta.url));
const OUT = join(ROOT, "out");
const args = process.argv.slice(2);
const opt = (name, def) => {
  const i = args.indexOf(`--${name}`);
  return i >= 0 ? args[i + 1] : def;
};
const FPS = Number(opt("fps", 60));
const WORKERS = Number(opt("workers", 3));
const STILLS = opt("stills", null);
const OUTFILE = opt("out", join(OUT, `promo-1080x1920-${FPS}fps.mp4`));
const AUDIO = join(OUT, "music.wav");

// servidor estático mínimo: las fuentes no cargan bien desde file://
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".woff2": "font/woff2", ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp", ".wav": "audio/wav" };
const server = createServer(async (req, res) => {
  try {
    const path = join(ROOT, decodeURIComponent(new URL(req.url, "http://x").pathname));
    if (!path.startsWith(ROOT)) throw new Error("outside root");
    const body = await readFile(path);
    res.writeHead(200, { "content-type": TYPES[extname(path)] || "application/octet-stream" });
    res.end(body);
  } catch {
    res.writeHead(404);
    res.end();
  }
});
await new Promise(r => server.listen(0, "127.0.0.1", r));
const URL_BASE = `http://127.0.0.1:${server.address().port}/index.html?render=1`;

const browser = await chromium.launch();
async function newPage() {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 }, deviceScaleFactor: 1 });
  page.on("pageerror", e => console.error("pageerror:", e.message));
  await page.goto(URL_BASE);
  await page.evaluate(() => window.ready);
  return page;
}
// El PNG se codifica dentro de cada página (cada una en su propio proceso), no
// con page.screenshot, que serializa todo en el proceso principal del navegador.
async function grab(page, t) {
  const dataUrl = await page.evaluate(time => {
    window.renderFrame(time);
    return document.getElementById("c").toDataURL("image/png");
  }, t);
  return Buffer.from(dataUrl.slice(dataUrl.indexOf(",") + 1), "base64");
}

await mkdir(OUT, { recursive: true });

if (STILLS) {
  const dir = join(OUT, "stills");
  await mkdir(dir, { recursive: true });
  const page = await newPage();
  for (const s of STILLS.split(",").map(Number)) {
    const file = join(dir, `t${s.toFixed(2).padStart(5, "0")}.png`);
    await writeFile(file, await grab(page, s));
    console.log(file);
  }
} else {
  const total = Math.round(30 * FPS);
  const hasAudio = await access(AUDIO).then(() => true, () => false);
  if (!hasAudio) console.warn(`(sin audio: no existe ${AUDIO}; genera la música con promo/music.py)`);
  const ff = spawn("ffmpeg", [
    "-y", "-loglevel", "error",
    "-f", "image2pipe", "-framerate", String(FPS), "-i", "-",
    ...(hasAudio ? ["-i", AUDIO] : []),
    "-vf", "scale=in_range=full:out_range=tv:out_color_matrix=bt709,format=yuv420p",
    "-c:v", "libx264", "-preset", "slower", "-crf", "12", "-tune", "animation",
    "-x264-params", "aq-mode=3", "-profile:v", "high", "-level", "4.2",
    "-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv",
    "-r", String(FPS), "-g", String(FPS),
    ...(hasAudio ? ["-c:a", "aac", "-b:a", "320k", "-ar", "48000"] : []),
    "-t", "30", "-movflags", "+faststart", OUTFILE,
  ], { stdio: ["pipe", "inherit", "inherit"] });
  const ffDone = new Promise((res, rej) => ff.on("close", c => (c === 0 ? res() : rej(new Error(`ffmpeg salió con ${c}`)))));

  // varios workers renderizan en paralelo; los frames se escriben en orden
  const pages = await Promise.all(Array.from({ length: WORKERS }, newPage));
  const ready = new Map();
  let nextToWrite = 0, nextToRender = 0;
  const started = Date.now();
  async function flush() {
    while (ready.has(nextToWrite)) {
      const buf = ready.get(nextToWrite);
      ready.delete(nextToWrite++);
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once("drain", r));
      if (nextToWrite % FPS === 0) {
        const el = (Date.now() - started) / 1000;
        process.stdout.write(`\r${nextToWrite}/${total} frames · ${el.toFixed(0)} s`);
      }
    }
  }
  let writing = Promise.resolve();
  await Promise.all(pages.map(async page => {
    while (nextToRender < total) {
      const i = nextToRender++;
      // no dejes que la cola en memoria crezca sin límite
      while (i - nextToWrite > WORKERS * 8) await new Promise(r => setTimeout(r, 5));
      ready.set(i, await grab(page, i / FPS));
      writing = writing.then(flush);
    }
  }));
  await writing;
  ff.stdin.end();
  await ffDone;
  console.log(`\n${OUTFILE}`);
}

await browser.close();
server.close();
