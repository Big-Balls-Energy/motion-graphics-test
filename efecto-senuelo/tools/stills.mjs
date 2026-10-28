// Renderiza cuadros sueltos para revisión: node tools/stills.mjs out_dir t1 t2 ...
import { createRequire } from 'module';
const { chromium } = createRequire(import.meta.url)('playwright');
import fs from 'fs';
import path from 'path';
import http from 'http';
const root = path.resolve(path.dirname(new URL(import.meta.url).pathname), '../player');
const types = { '.html': 'text/html', '.js': 'text/javascript', '.png': 'image/png', '.otf': 'font/otf', '.m4a': 'audio/mp4' };
const srv = http.createServer((req, res) => {
  const p = path.join(root, decodeURIComponent(req.url.split('?')[0]));
  fs.readFile(p, (e, d) => { if (e) { res.writeHead(404); res.end(); return; } res.writeHead(200, { 'Content-Type': types[path.extname(p)] || 'application/octet-stream' }); res.end(d); });
}).listen(0);
const port = srv.address().port;
const [out, ...ts] = process.argv.slice(2);
fs.mkdirSync(out, { recursive: true });
const browser = await chromium.launch();
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
page.on('console', m => console.log('console:', m.text()));
page.on('pageerror', e => console.log('pageerror:', e.message));
await page.goto(`http://localhost:${port}/index.html?render=1`);
await page.waitForFunction(() => window.ready === true);
for (const t of ts) {
  const url = await page.evaluate(t => window.frameData(+t), t);
  fs.writeFileSync(path.join(out, `t${(+t).toFixed(2).padStart(6, '0')}.png`), Buffer.from(url.split(',')[1], 'base64'));
}
await browser.close(); srv.close();
