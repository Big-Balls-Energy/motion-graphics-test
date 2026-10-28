// Render the reel to video with headless Chromium.
//   node render.js PAGE.html OUT_DIR [--workers 3]      -> OUT_DIR/video.mp4 + cues.json
//   node render.js PAGE.html OUT_DIR --snap 1.5,3,10     -> OUT_DIR/snap_<t>.png
const { chromium } = require('playwright');
const { spawn, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const FPS = 30;
const args = process.argv.slice(2);
const [htmlPath, outDir] = args;
const opt = name => { const i = args.indexOf(name); return i >= 0 ? args[i + 1] : null; };
const workers = +(opt('--workers') || 3);
const snap = opt('--snap');

async function openPage(browser) {
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  page.on('pageerror', e => { console.error('page error:', e.message); process.exit(1); });
  await page.goto('file://' + path.resolve(htmlPath) + '?render');
  await page.waitForFunction('window.READY === true');
  return page;
}

const grab = (page, t) => page.evaluate(t => {
  window.REEL.render(t);
  return document.getElementById('reel').toDataURL('image/png').slice('data:image/png;base64,'.length);
}, t);

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch();
  const page0 = await openPage(browser);
  const { cues, dur } = await page0.evaluate(() => ({ cues: window.REEL.CUES, dur: window.REEL.DUR }));
  fs.writeFileSync(path.join(outDir, 'cues.json'), JSON.stringify(cues, null, 1));
  if (snap) {
    for (const t of snap.split(',').map(Number)) {
      fs.writeFileSync(path.join(outDir, `snap_${t.toFixed(2)}.png`), Buffer.from(await grab(page0, t), 'base64'));
    }
    await browser.close();
    return;
  }
  await page0.close();
  const total = Math.round(dur * FPS), per = Math.ceil(total / workers);
  const t0 = Date.now();
  let done = 0;
  await Promise.all([...Array(workers).keys()].map(async w => {
    const a = w * per, b = Math.min(total, a + per);
    const page = await openPage(browser);
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png',
      '-i', '-', '-c:v', 'libx264', '-preset', 'slow', '-crf', '15', '-profile:v', 'high', '-pix_fmt', 'yuv420p',
      '-g', '60', path.join(outDir, `part${w}.mp4`)], { stdio: ['pipe', 'inherit', 'inherit'] });
    for (let f = a; f < b; f++) {
      const buf = Buffer.from(await grab(page, f / FPS), 'base64');
      if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
      if (++done % 150 === 0) console.log(`${done}/${total} frames, ${((Date.now() - t0) / 1000).toFixed(0)} s`);
    }
    ff.stdin.end();
    await new Promise(r => ff.on('close', r));
    await page.close();
  }));
  await browser.close();
  const list = path.join(outDir, 'parts.txt');
  fs.writeFileSync(list, [...Array(workers).keys()].map(w => `file 'part${w}.mp4'`).join('\n'));
  execFileSync('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list, '-c', 'copy',
    path.join(outDir, 'video.mp4')]);
  console.log(`video.mp4 rendered in ${((Date.now() - t0) / 1000).toFixed(0)} s`);
})();
