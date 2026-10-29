// Mide cuánto tarda renderFrame(t) + la exportación JPEG en varios segundos, para estimar el render completo.
// Uso: node herramientas/tiempos_render.js http://localhost:8811/index.html 1.6,22.3,31.0
// (el primer cuadro siempre tarda más porque compila los shaders)
const { chromium } = require('playwright');
(async () => {
  const browser = await chromium.launch({ args: ['--enable-unsafe-swiftshader', '--ignore-gpu-blocklist'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto(process.argv[2] + '?render=1');
  await page.waitForFunction(() => window.isReady === true, null, { timeout: 180000 });
  for (const t of process.argv[3].split(',').map(Number)) {
    const ms = await page.evaluate(t => { const a = performance.now(); renderFrame(t); document.getElementById('c').toDataURL('image/jpeg', .95); return performance.now() - a; }, t);
    console.log('t', t, 'ms', Math.round(ms));
  }
  await browser.close();
})();
