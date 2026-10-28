// Renderiza los 1800 cuadros (30 fps) y los codifica a MP4 con el audio: node tools/render.mjs audio.wav salida.mp4
import { createRequire } from 'module';
import { spawn } from 'child_process';
import fs from 'fs';
import path from 'path';
import http from 'http';
const { chromium } = createRequire(import.meta.url)('playwright');
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../player');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.otf': 'font/otf' };
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
}).listen(0);
const [audio, out] = process.argv.slice(2);
const FPS = 30, FRAMES = 60 * FPS;
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
  ...(audio ? ['-i', audio] : []),
  '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-profile:v', 'high', '-r', String(FPS),
  '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
  ...(audio ? ['-c:a', 'aac', '-b:a', '256k', '-ar', '48000', '-shortest'] : ['-an']),
  '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.goto(`http://localhost:${srv.address().port}/index.html?render=1`);
await page.waitForFunction(() => window.ready === true);
for (let f = 0; f < FRAMES; f++) {
  const url = await page.evaluate(t => window.frameData(t), f / FPS);
  const buf = Buffer.from(url.split(',')[1], 'base64');
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (f % 150 === 0) console.log(`cuadro ${f}/${FRAMES}`);
}
ff.stdin.end();
await new Promise(r => ff.on('close', r));
await browser.close(); srv.close();
console.log('listo', out);
