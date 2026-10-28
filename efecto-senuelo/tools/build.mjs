// Genera: reproductor HTML autónomo (fuentes, logo y audio embebidos) + guion con marcas de tiempo.
import fs from 'fs';
import path from 'path';
const dir = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const P = f => path.join(dir, 'player', f);
const out = path.join(dir, process.argv[2] || 'entregables');
fs.mkdirSync(out, { recursive: true });
const b64 = (f, mime) => `data:${mime};base64,` + fs.readFileSync(P(f)).toString('base64');

// --- HTML autónomo ---
let html = fs.readFileSync(P('index.html'), 'utf8');
let anim = fs.readFileSync(P('anim.js'), 'utf8');
for (const f of ['Inter-Black.otf', 'Inter-ExtraBold.otf', 'Inter-SemiBold.otf', 'Inter-Medium.otf'])
  anim = anim.replace('`url(fonts/${f})`', () => '`url(${FONTS[f]})`');
const fonts = Object.fromEntries(['Inter-Black.otf', 'Inter-ExtraBold.otf', 'Inter-SemiBold.otf', 'Inter-Medium.otf'].map(f => [f, b64('fonts/' + f, 'font/otf')]));
anim = `const FONTS = ${JSON.stringify(fonts)};\n` + anim.replace("'assets/logo-atlas-path.png'", () => JSON.stringify(b64('assets/logo-atlas-path.png', 'image/png')));
html = html
  .replace('<script src="timeline.js"></script>', () => `<script>${fs.readFileSync(P('timeline.js'), 'utf8')}</script>`)
  .replace('<script src="anim.js"></script>', () => `<script>${anim}</script>`)
  .replace('src="audio/musica_y_efectos.m4a"', () => `src="${b64('audio/musica_y_efectos.m4a', 'audio/mp4')}"`);
fs.writeFileSync(path.join(out, 'reproductor_pantalla_completa.html'), html);

// --- Guion ---
global.window = {};
await import(P('timeline.js'));
const TL = window.TIMELINE;
const ts = s => { const m = Math.floor(s / 60), r = s - m * 60; return `${String(m).padStart(2, '0')}:${r.toFixed(2).padStart(5, '0')}`; };
let md = `# Guion — "El efecto señuelo" (Reel 60 s · versión sin voz)\n\n`;
md += `Lee cada línea cuando aparezca su subtítulo. Las palabras en **negrita** salen en naranja en pantalla (énfasis de voz).\n`;
md += `Volumen de música: ${TL.musicGain.map(([a, b, g]) => `${a}–${b} s → ${Math.round(g * 100)} %`).join(' · ')}.\n\n`;
for (const sc of TL.scenes) {
  md += `## [${sc.start}–${sc.end} s] ${sc.title}\n\n`;
  for (const [a, b, s] of TL.subs.filter(x => x[0] >= sc.start && x[0] < sc.end))
    md += `- \`${ts(a)} → ${ts(b)}\`  ${s.replace(/\*([^*]+)\*/g, '**$1**')}\n`;
  md += '\n';
}
md += `## Texto corrido (para ensayar)\n\n`;
for (const sc of TL.scenes)
  md += `**${sc.start}–${sc.end} s:** ` + TL.subs.filter(x => x[0] >= sc.start && x[0] < sc.end).map(x => x[2].replace(/\*/g, '')).join(' ') + '\n\n';
fs.writeFileSync(path.join(out, 'guion_con_tiempos.md'), md);
console.log('ok');
