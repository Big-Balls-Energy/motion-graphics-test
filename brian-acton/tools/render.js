// Uso: node tools/render.js <url> <outDir> [snap t1,t2,...]  |  frames <from> <to>  |  cover [archivo.png]  |  assets
// (cover = portada 1080×1920; assets = recursos visuales en PNG con transparencia)
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [url, out, mode = 'snap', a, b] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('console', m => console.log('[page]', m.text()));
  page.on('pageerror', e => console.log('[err]', e.message));
  await page.goto(url + '?render=1');
  await page.waitForFunction(() => window.isReady === true, null, { timeout: 120000 });
  fs.writeFileSync(path.join(out, 'timeline.json'), JSON.stringify(await page.evaluate(() => window.TL), null, 1));
  const shot = async (t, file) => {
    const data = await page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/png'); }, t);
    fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
  };
  const png = async (fn, arg, file) => {
    const data = await page.evaluate(([fn, arg]) => { window[fn](arg); return document.getElementById('c').toDataURL('image/png'); }, [fn, arg]);
    fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
  };
  if (mode === 'snap') {
    for (const t of a.split(',').map(Number)) await shot(t, path.join(out, `snap_${t.toFixed(2)}.png`));
  } else if (mode === 'cover') {
    await png('renderCover', null, path.join(out, a || 'portada.png'));
  } else if (mode === 'assets') {
    for (const n of await page.evaluate(() => window.assetNames())) await png('renderAsset', n, path.join(out, `${n}.png`));
  } else {
    const jpg = async (t, file) => {
      const data = await page.evaluate(t => { renderFrame(t); return document.getElementById('c').toDataURL('image/jpeg', .95); }, t);
      fs.writeFileSync(file, Buffer.from(data.split(',')[1], 'base64'));
    };
    for (let f = +a; f < +b; f++) await jpg(f / 30, path.join(out, `f_${String(f).padStart(5, '0')}.jpg`));
  }
  await browser.close();
})();
