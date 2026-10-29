// Uso: node tools/render.js <url> <outDir> [snap t1,t2,...]  |  frames <from> <to>  |  cover [archivo.png]
// Igual que en los otros reels, pero antes de cada cuadro espera window.prepare(t): carga el cuadro del video y el matte de la persona.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [url, out, mode = 'snap', a, b] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[err]', e.message));
  await page.goto(url + '?render=1');
  await page.waitForFunction(() => window.isReady === true, null, { timeout: 120000 });
  fs.writeFileSync(path.join(out, 'timeline.json'), JSON.stringify(await page.evaluate(() => window.TL), null, 1));
  const grab = async (t, type) => page.evaluate(async ([t, type]) => {
    await window.prepare(t); renderFrame(t);
    return document.getElementById('c').toDataURL(type, .95);
  }, [t, type]);
  if (mode === 'snap') {
    for (const t of a.split(',').map(Number)) {
      const d = await grab(t, 'image/png'); fs.writeFileSync(path.join(out, `snap_${t.toFixed(2)}.png`), Buffer.from(d.split(',')[1], 'base64'));
    }
  } else if (mode === 'cover') {
    const d = await page.evaluate(async () => { await window.prepare(0); renderCover(); return document.getElementById('c').toDataURL('image/png'); });
    fs.writeFileSync(path.join(out, a || 'portada.png'), Buffer.from(d.split(',')[1], 'base64'));
  } else {
    for (let f = +a; f < +b; f++) {
      const d = await grab(f / 30, 'image/jpeg');
      fs.writeFileSync(path.join(out, `f_${String(f).padStart(5, '0')}.jpg`), Buffer.from(d.split(',')[1], 'base64'));
    }
  }
  await browser.close();
})();
