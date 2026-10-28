// "El efecto de progreso dotado" — 60 s, 1080x1920 motion graphic.
// render(t) is a pure function of time; all sync comes from window.TIMELINE
// (word-level voice timings produced by tools/build_voice.py).
(() => {
'use strict';

const W = 1080, H = 1920, DUR = 60;
const C = {
  cream: '#F5EFE6', paper: '#FFFBF4', ink: '#1A1A1A', orange: '#FF5A1F', green: '#22C55E',
  orangeTint: '#FFC9B3', greenTint: '#C9F2D8', inkFaint: 'rgba(26,26,26,0.14)',
};
// Instagram safe area: 250 px top, 400 px bottom, 120 px right (mirrored left for symmetry).
const SAFE = { top: 250, bottom: H - 400, left: 120, right: W - 120 };
const CX = 540;
const BPM = 112, BEAT = 60 / BPM;

const canvas = document.getElementById('reel');
let ctx = canvas.getContext('2d');   // `let`: withCtx() points helpers at offscreen canvases
function withCtx(c, fn) { const prev = ctx; ctx = c; try { fn(); } finally { ctx = prev; } }
const TL = window.TIMELINE;

// ---------------------------------------------------------------- helpers
const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
const lerp = (a, b, k) => a + (b - a) * k;
const E = {
  lin: k => k,
  out3: k => 1 - Math.pow(1 - k, 3),
  out5: k => 1 - Math.pow(1 - k, 5),
  in3: k => k * k * k,
  inOut3: k => (k < 0.5 ? 4 * k * k * k : 1 - Math.pow(-2 * k + 2, 3) / 2),
  back: k => { const s = 1.9; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); },
  backSoft: k => { const s = 1.2; return 1 + (s + 1) * Math.pow(k - 1, 3) + s * Math.pow(k - 1, 2); },
  elastic: k => (k <= 0 ? 0 : k >= 1 ? 1 : Math.pow(2, -9 * k) * Math.sin((k * 9 - 0.75) * (2 * Math.PI) / 3) + 1),
};
// eased progress of an animation that starts at t0 and lasts d seconds
const P = (t, t0, d, ease = E.out3) => ease(clamp((t - t0) / d));
const TAU = Math.PI * 2, DEG = Math.PI / 180;

function rng(seed) {
  return () => {
    seed = (seed + 0x6D2B79F5) | 0;
    let x = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    x = (x + Math.imul(x ^ (x >>> 7), 61 | x)) ^ x;
    return ((x ^ (x >>> 14)) >>> 0) / 4294967296;
  };
}

const norm = s => s.toLowerCase().replace(/[¿?¡!.,:;…]/g, '');
function tok(section, word, n = 0) {
  const hits = TL.tokens.filter(x => x.section === section && norm(x.text) === norm(word));
  if (!hits[n]) throw new Error(`token not found: ${section}/${word}/${n}`);
  return hits[n];
}
const SEC = Object.fromEntries(TL.sections.map(s => [s.id, s.start]));
const S = id => (id === 'hook' ? 0 : SEC[id] - 0.12);   // visuals lead the voice a hair

// -------------------------------------------------------- drawing helpers
function font(size, weight) { return `${weight} ${size}px Montserrat, "Inter", sans-serif`; }

// Text centered on (x, y) — `y` is the visual middle of capitals.
function txt(str, x, y, o = {}) {
  const { size = 60, weight = 900, color = C.ink, align = 'center', ls = 0, maxW = 0,
          shadow = 0, shadowColor = C.ink, stroke = 0, strokeColor = C.ink, alpha = 1 } = o;
  if (alpha <= 0) return size;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.letterSpacing = `${ls}px`;
  let s = size;
  ctx.font = font(s, weight);
  if (maxW) {
    const w = ctx.measureText(str).width;
    if (w > maxW) { s = (s * maxW) / w; ctx.font = font(s, weight); }
  }
  ctx.textAlign = align;
  ctx.textBaseline = 'alphabetic';
  const by = y + s * 0.36;
  const lx = align === 'center' ? x + ls / 2 : x;
  if (shadow) { ctx.fillStyle = shadowColor; ctx.fillText(str, lx + shadow * 0.5, by + shadow); }
  if (stroke) {
    ctx.lineJoin = 'round'; ctx.lineWidth = stroke; ctx.strokeStyle = strokeColor;
    ctx.strokeText(str, lx, by);
  }
  ctx.fillStyle = color;
  ctx.fillText(str, lx, by);
  ctx.restore();
  return s;
}

function measure(str, size, weight, ls = 0) {
  ctx.save();
  ctx.letterSpacing = `${ls}px`;
  ctx.font = font(size, weight);
  const w = ctx.measureText(str).width;
  ctx.restore();
  return w;
}

// Flat "sticker" panel: hard ink shadow, paper fill, ink outline.
function panel(x, y, w, h, r, o = {}) {
  const { fill = C.paper, stroke = C.ink, lw = 6, shadow = 14 } = o;
  if (shadow) {
    ctx.fillStyle = C.ink;
    ctx.beginPath(); ctx.roundRect(x + shadow, y + shadow, w, h, r); ctx.fill();
  }
  ctx.fillStyle = fill;
  ctx.beginPath(); ctx.roundRect(x, y, w, h, r); ctx.fill();
  if (lw) { ctx.lineWidth = lw; ctx.strokeStyle = stroke; ctx.stroke(); }
}

function pill(label, x, y, o = {}) {
  const { size = 34, weight = 800, fill = C.ink, color = C.paper, padX = 30, h = size * 2, ls = 3,
          alpha = 1, scale = 1, rot = 0 } = o;
  if (alpha <= 0 || scale <= 0) return;
  const w = measure(label, size, weight, ls) + padX * 2;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale);
  ctx.fillStyle = fill;
  ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, h / 2); ctx.fill();
  txt(label, 0, 0, { size, weight, color, ls });
  ctx.restore();
}

function star(x, y, R, r, n, fill) {
  ctx.beginPath();
  for (let i = 0; i < n * 2; i++) {
    const a = (i * Math.PI) / n - Math.PI / 2, rad = i % 2 ? r : R;
    ctx.lineTo(x + Math.cos(a) * rad, y + Math.sin(a) * rad);
  }
  ctx.closePath();
  ctx.fillStyle = fill;
  ctx.fill();
}

function sparkle(x, y, s, k) {           // 4-point twinkle, k in 0..1 life
  if (k <= 0 || k >= 1) return;
  const sc = Math.sin(k * Math.PI);
  ctx.save();
  ctx.translate(x, y); ctx.rotate(k * 0.8); ctx.scale(sc, sc);
  star(0, 0, s, s * 0.22, 4, C.orange);
  ctx.restore();
}

function checkBadge(x, y, r, k, color = C.green) {  // k: pop progress
  if (k <= 0) return;
  const sc = E.back(clamp(k));
  ctx.save();
  ctx.translate(x, y); ctx.scale(sc, sc);
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.fill();
  ctx.lineWidth = Math.max(4, r * 0.09); ctx.strokeStyle = C.ink; ctx.stroke();
  const d = clamp((k - 0.2) / 0.5);
  ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.lineWidth = r * 0.2; ctx.strokeStyle = '#fff';
  ctx.beginPath();
  const p0 = [-r * 0.42, 0], p1 = [-r * 0.1, r * 0.32], p2 = [r * 0.45, -r * 0.3];
  ctx.moveTo(...p0);
  if (d < 0.4) ctx.lineTo(lerp(p0[0], p1[0], d / 0.4), lerp(p0[1], p1[1], d / 0.4));
  else { ctx.lineTo(...p1); const e = (d - 0.4) / 0.6; ctx.lineTo(lerp(p1[0], p2[0], e), lerp(p1[1], p2[1], e)); }
  ctx.stroke();
  ctx.restore();
}

function burst(x, y, r, lt, color = C.orange, n = 10, seed = 1) {   // impact ring + spikes
  if (lt < 0 || lt > 0.5) return;
  const k = lt / 0.5, A = ctx.globalAlpha;
  ctx.save();
  ctx.translate(x, y);
  ctx.globalAlpha = A * (1 - k);
  ctx.lineWidth = 9 * (1 - k) + 1; ctx.strokeStyle = color;
  ctx.beginPath(); ctx.arc(0, 0, r * (1 + 1.1 * E.out3(k)), 0, TAU); ctx.stroke();
  const rand = rng(seed);
  ctx.lineCap = 'round'; ctx.strokeStyle = C.ink; ctx.lineWidth = 7;
  for (let i = 0; i < n; i++) {
    const a = (i / n) * TAU + rand() * 0.4;
    const d1 = r * (1.25 + 0.9 * E.out3(k)), d2 = d1 + 30 * (1 - k);
    ctx.beginPath(); ctx.moveTo(Math.cos(a) * d1, Math.sin(a) * d1); ctx.lineTo(Math.cos(a) * d2, Math.sin(a) * d2); ctx.stroke();
  }
  ctx.restore();
}

// Rubber stamp: falls in for 0.14 s, hits at lt = 0, then wobbles.
function stamp(x, y, r, lt, rot = 0, color = C.orange) {
  if (lt < -0.14) return;
  burst(x, y, r, lt, color, 9, Math.round(x + y));
  ctx.save();
  ctx.translate(x, y); ctx.rotate(rot);
  let sc;
  if (lt < 0) { const k = 1 + lt / 0.14; sc = lerp(2.6, 1, E.in3(k)); ctx.globalAlpha *= k; }
  else sc = 1 + 0.2 * Math.exp(-lt * 16) * Math.cos(lt * 42);
  ctx.scale(sc, sc);
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.fill();
  ctx.lineWidth = Math.max(4, r * 0.1); ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.setLineDash([r * 0.16, r * 0.14]);
  ctx.lineWidth = Math.max(2, r * 0.06); ctx.strokeStyle = 'rgba(255,255,255,0.8)';
  ctx.beginPath(); ctx.arc(0, 0, r * 0.76, 0, TAU); ctx.stroke();
  ctx.setLineDash([]);
  star(0, 0, r * 0.44, r * 0.19, 5, '#fff');
  ctx.restore();
}

function pumText(x, y, lt, rot) {
  if (lt < 0 || lt > 0.55) return;
  const sc = E.back(clamp(lt / 0.14)), a = 1 - clamp((lt - 0.38) / 0.17);
  ctx.save();
  ctx.translate(x, y); ctx.rotate(rot); ctx.scale(sc, sc);
  txt('¡PUM!', 0, 0, { size: 70, weight: 900, color: C.orange, stroke: 12, alpha: a, shadow: 8 });
  ctx.restore();
}

function emptySlot(x, y, r, o = {}) {
  const { hi = 0, label = '', alpha = 1 } = o;
  if (alpha <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.fillStyle = hi > 0 ? `rgba(255,90,31,${0.12 * hi})` : 'rgba(26,26,26,0.03)';
  ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fill();
  ctx.setLineDash(hi > 0.5 ? [] : [r * 0.22, r * 0.18]);
  ctx.lineWidth = lerp(4, 7, hi);
  ctx.strokeStyle = hi > 0 ? C.orange : 'rgba(26,26,26,0.35)';
  ctx.stroke();
  ctx.setLineDash([]);
  if (label) txt(label, x, y, { size: r * 0.62, weight: 800, color: 'rgba(26,26,26,0.22)' });
  ctx.restore();
}

function cup(x, y, s, color = C.orange) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s / 60, s / 60);
  ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
  ctx.beginPath(); ctx.arc(26, 2, 11, -Math.PI / 2, Math.PI / 2); ctx.stroke();
  ctx.fillStyle = color;
  ctx.beginPath(); ctx.moveTo(-26, -12); ctx.lineTo(26, -12); ctx.lineTo(19, 22);
  ctx.quadraticCurveTo(0, 30, -19, 22); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.beginPath();
  ctx.moveTo(-8, -20); ctx.bezierCurveTo(-15, -28, -1, -33, -8, -42);
  ctx.moveTo(8, -20); ctx.bezierCurveTo(1, -28, 15, -33, 8, -42);
  ctx.stroke();
  ctx.restore();
}

// ------------------------------------------------------------ loyalty card
// Card centered at (x, y). slots: count; cols; stamps: [{i, t}] (impact times);
// reveal: {t0, step} pops slots in sequence; hi: 0..1 highlight on empty slots.
function loyaltyCard(t, o) {
  const { x, y, w, h, rot = 0, scale = 1, alpha = 1, slots = 10, cols = 5, r = 48, gapX = 140, gapY = 130,
          gridY = 50, stamps = [], reveal = null, hi = 0, title = 'TARJETA DE LEALTAD',
          sub = '10 sellos = 1 café gratis', header = 'landscape', footer = '', footerColor = C.ink,
          badge = '', icon = 'cup', dim = 0 } = o;
  if (alpha <= 0 || scale <= 0) return;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(x, y); ctx.rotate(rot); ctx.scale(scale, scale);
  panel(-w / 2, -h / 2, w, h, 40);
  if (header === 'landscape') {
    if (icon === 'cup') cup(-w / 2 + 78, -h / 2 + 80, 64);
    txt(title, -w / 2 + 140, -h / 2 + 64, { size: 40, weight: 900, align: 'left', maxW: w - 180 });
    txt(sub, -w / 2 + 140, -h / 2 + 110, { size: 28, weight: 500, align: 'left', color: 'rgba(26,26,26,0.7)' });
    ctx.strokeStyle = 'rgba(26,26,26,0.2)'; ctx.lineWidth = 4; ctx.setLineDash([12, 10]);
    ctx.beginPath(); ctx.moveTo(-w / 2 + 36, -h / 2 + 152); ctx.lineTo(w / 2 - 36, -h / 2 + 152); ctx.stroke();
    ctx.setLineDash([]);
  } else {
    txt(title, 0, -h / 2 + 62, { size: 36, weight: 900, maxW: w - 60 });
    txt(sub, 0, -h / 2 + 102, { size: 24, weight: 500, color: 'rgba(26,26,26,0.65)' });
  }
  const rows = Math.ceil(slots / cols);
  for (let i = 0; i < slots; i++) {
    const c = i % cols, rIdx = Math.floor(i / cols);
    const sx = (c - (cols - 1) / 2) * gapX, sy = gridY + (rIdx - (rows - 1) / 2) * gapY;
    let pop = 1;
    if (reveal) pop = E.back(clamp((t - reveal.t0 - i * reveal.step) / 0.22));
    if (pop <= 0) continue;
    const st = stamps.find(s => s.i === i);
    ctx.save();
    ctx.translate(sx, sy); ctx.scale(pop, pop);
    const stamped = st && t >= st.t - 0.14;
    if (!stamped || t < st.t) emptySlot(0, 0, r, { hi: st ? 0 : hi, label: String(i + 1) });
    if (stamped) stamp(0, 0, r, t - st.t, ((i * 37) % 21 - 10) * DEG);
    ctx.restore();
  }
  if (footer) txt(footer, 0, h / 2 - 36, { size: 28, weight: 800, color: footerColor, ls: 2 });
  if (badge) {
    ctx.fillStyle = C.ink;
    ctx.beginPath(); ctx.arc(-w / 2 + 6, -h / 2 + 6, 46, 0, TAU); ctx.fill();
    ctx.lineWidth = 6; ctx.strokeStyle = C.paper; ctx.stroke();
    txt(badge, -w / 2 + 6, -h / 2 + 6, { size: 50, weight: 900, color: C.paper });
  }
  if (dim > 0) {
    ctx.fillStyle = `rgba(245,239,230,${0.62 * dim})`;
    ctx.beginPath(); ctx.roundRect(-w / 2 - 56, -h / 2 - 56, w + 76, h + 76, 40); ctx.fill();
  }
  ctx.restore();
}

// -------------------------------------------------------------- illustrations
function car(x, y, s, t) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round';
  const bob = Math.sin(t * 14) * 2;
  ctx.translate(0, bob);
  ctx.fillStyle = C.orange;                                   // cabin
  ctx.beginPath(); ctx.moveTo(-95, -40); ctx.lineTo(-55, -105); ctx.lineTo(70, -105); ctx.lineTo(115, -40);
  ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.paper;                                    // windows
  ctx.beginPath(); ctx.moveTo(-72, -46); ctx.lineTo(-46, -90); ctx.lineTo(0, -90); ctx.lineTo(0, -46); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(14, -46); ctx.lineTo(14, -90); ctx.lineTo(62, -90); ctx.lineTo(92, -46); ctx.closePath(); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.orange;                                   // body
  ctx.beginPath(); ctx.roundRect(-175, -45, 350, 85, 30); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.paper;
  ctx.beginPath(); ctx.roundRect(140, -22, 30, 18, 6); ctx.fill(); ctx.stroke();   // headlight
  for (const wx of [-100, 100]) {                              // wheels
    ctx.save(); ctx.translate(wx, 42 - bob); ctx.rotate(t * 9);
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(0, 0, 42, 0, TAU); ctx.fill();
    ctx.fillStyle = C.paper; ctx.beginPath(); ctx.arc(0, 0, 17, 0, TAU); ctx.fill();
    ctx.fillStyle = C.ink; ctx.fillRect(-3, -17, 6, 34);
    ctx.restore();
  }
  ctx.restore();
}

function bubbles(x, y, t, t0, n = 12, seed = 7) {
  const rand = rng(seed);
  for (let i = 0; i < n; i++) {
    const delay = rand() * 1.2, life = 1.1 + rand() * 0.6, k = (t - t0 - delay) / life;
    const bx = x + (rand() - 0.5) * 520, by = y + 40 - rand() * 60, r = 12 + rand() * 22;
    if (k <= 0 || k >= 1) continue;
    const px = bx + Math.sin((t + i) * 4) * 12, py = by - k * 260;
    ctx.save();
    ctx.globalAlpha *= Math.sin(k * Math.PI);
    ctx.fillStyle = 'rgba(255,255,255,0.85)'; ctx.strokeStyle = C.ink; ctx.lineWidth = 4;
    ctx.beginPath(); ctx.arc(px, py, r * E.back(clamp(k * 4)), 0, TAU); ctx.fill(); ctx.stroke();
    ctx.fillStyle = C.orangeTint;
    ctx.beginPath(); ctx.arc(px - r * 0.35, py - r * 0.35, r * 0.22, 0, TAU); ctx.fill();
    ctx.restore();
  }
}

function gift(x, y, s, open = 0) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round';
  ctx.fillStyle = C.orange;
  ctx.beginPath(); ctx.roundRect(-110, -20, 220, 150, 14); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.paper;
  ctx.fillRect(-18, -20, 36, 150); ctx.strokeRect(-18, -20, 36, 150);
  ctx.save();
  ctx.translate(0, -20 - open * 60); ctx.rotate(-open * 0.35);
  ctx.fillStyle = C.orange;
  ctx.beginPath(); ctx.roundRect(-128, -50, 256, 50, 12); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.paper;
  ctx.fillRect(-18, -50, 36, 50); ctx.strokeRect(-18, -50, 36, 50);
  ctx.fillStyle = C.paper;                                    // bow
  for (const sgn of [-1, 1]) {
    ctx.beginPath(); ctx.ellipse(sgn * 42, -78, 44, 26, sgn * -0.5, 0, TAU); ctx.fill(); ctx.stroke();
  }
  ctx.beginPath(); ctx.arc(0, -62, 16, 0, TAU); ctx.fill(); ctx.stroke();
  ctx.restore();
  ctx.restore();
}

function gear(x, y, r, teeth, rot, fill) {
  ctx.save();
  ctx.translate(x, y); ctx.rotate(rot);
  ctx.beginPath();
  const rin = r * 0.78, step = Math.PI / teeth;
  for (let i = 0; i < teeth * 2; i++) {
    const rad = i % 2 ? rin : r, a0 = i * step, a1 = (i + 1) * step, pad = step * 0.16;
    ctx.lineTo(Math.cos(a0 + pad) * rad, Math.sin(a0 + pad) * rad);
    ctx.lineTo(Math.cos(a1 - pad) * rad, Math.sin(a1 - pad) * rad);
  }
  ctx.closePath();
  ctx.fillStyle = fill; ctx.fill();
  ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round'; ctx.stroke();
  ctx.fillStyle = C.paper;
  ctx.beginPath(); ctx.arc(0, 0, r * 0.3, 0, TAU); ctx.fill(); ctx.stroke();
  ctx.restore();
}

const BRAIN = [[-150, -40, 105], [-60, -120, 110], [60, -125, 110], [155, -45, 105], [130, 70, 100],
               [0, 40, 130], [-125, 75, 95], [-30, 120, 80], [70, 125, 75]];
function brain(x, y, s, t, spin) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = C.ink;   // union outline: fat ink circles under slightly smaller fills
  for (const [bx, by, r] of BRAIN) { ctx.beginPath(); ctx.arc(bx, by, r + 8, 0, TAU); ctx.fill(); }
  ctx.fillStyle = C.orangeTint;
  for (const [bx, by, r] of BRAIN) { ctx.beginPath(); ctx.arc(bx, by, r, 0, TAU); ctx.fill(); }
  ctx.lineCap = 'round'; ctx.lineWidth = 7; ctx.strokeStyle = 'rgba(26,26,26,0.55)';
  ctx.beginPath();
  ctx.moveTo(0, -200); ctx.bezierCurveTo(-25, -140, 25, -80, 0, -20);      // midline
  ctx.moveTo(-190, -10); ctx.bezierCurveTo(-150, -50, -110, 10, -80, -30);
  ctx.moveTo(190, -10); ctx.bezierCurveTo(150, -50, 110, 10, 80, -30);
  ctx.moveTo(-110, -150); ctx.bezierCurveTo(-90, -110, -60, -130, -40, -100);
  ctx.moveTo(110, -150); ctx.bezierCurveTo(90, -110, 60, -130, 40, -100);
  ctx.stroke();
  gear(-55, 60, 78, 10, spin, C.orange);
  gear(62, 10, 54, 8, -spin * 1.25 + 0.2, C.paper);
  ctx.restore();
}

function store(x, y, s) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round';
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(-170 + 14, -60 + 14, 340, 250, 16); ctx.fill();
  ctx.fillStyle = C.paper; ctx.beginPath(); ctx.roundRect(-170, -60, 340, 250, 16); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.orangeTint; ctx.beginPath(); ctx.roundRect(-140, 10, 140, 110, 10); ctx.fill(); ctx.stroke();
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(30, 0, 100, 190, [10, 10, 0, 0]); ctx.fill();
  ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(110, 100, 8, 0, TAU); ctx.fill();
  for (let i = 0; i < 6; i++) {                                // striped awning
    const x0 = -200 + i * (400 / 6), w = 400 / 6;
    ctx.fillStyle = i % 2 ? C.paper : C.orange;
    ctx.beginPath(); ctx.moveTo(x0 + 10, -130); ctx.lineTo(x0 + w - 10 + 10, -130); ctx.lineTo(x0 + w, -60);
    ctx.arc(x0 + w / 2, -60, w / 2, 0, Math.PI); ctx.closePath(); ctx.fill(); ctx.stroke();
  }
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(-190, -160, 380, 36, 10); ctx.fill();
  txt('ABIERTO', -70, 66, { size: 22, weight: 900, color: C.ink, ls: 1 });
  ctx.restore();
}

function avatar(x, y, r) {
  ctx.save();
  ctx.translate(x, y);
  ctx.fillStyle = C.orange;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.fill();
  ctx.save(); ctx.clip();
  ctx.fillStyle = C.paper;
  ctx.beginPath(); ctx.arc(0, -r * 0.18, r * 0.36, 0, TAU); ctx.fill();
  ctx.beginPath(); ctx.ellipse(0, r * 0.78, r * 0.68, r * 0.55, 0, 0, TAU); ctx.fill();
  ctx.restore();
  ctx.lineWidth = Math.max(5, r * 0.06); ctx.strokeStyle = C.ink;
  ctx.beginPath(); ctx.arc(0, 0, r, 0, TAU); ctx.stroke();
  ctx.restore();
}

function cursor(x, y, s) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s); ctx.rotate(-0.12);
  ctx.beginPath();
  ctx.moveTo(0, 0); ctx.lineTo(0, 92); ctx.lineTo(24, 70); ctx.lineTo(42, 108); ctx.lineTo(60, 99);
  ctx.lineTo(42, 62); ctx.lineTo(74, 60); ctx.closePath();
  ctx.fillStyle = '#fff'; ctx.fill();
  ctx.lineWidth = 7; ctx.lineJoin = 'round'; ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.restore();
}

function flag(x, y, s) {
  ctx.save();
  ctx.translate(x, y); ctx.scale(s, s);
  ctx.fillStyle = C.ink; ctx.fillRect(-4, -110, 8, 120);
  const cw = 20;
  for (let r = 0; r < 3; r++) for (let c = 0; c < 4; c++) {
    ctx.fillStyle = (r + c) % 2 ? C.paper : C.ink;
    ctx.fillRect(4 + c * cw, -110 + r * cw, cw, cw);
  }
  ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.strokeRect(4, -110, cw * 4, cw * 3);
  ctx.restore();
}

function progressBar(x, y, w, h, k, o = {}) {   // x,y = left/center-y
  const { fill = C.orange, track = 'rgba(26,26,26,0.08)', lw = 6, shadow = 8 } = o;
  if (shadow) { ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(x + shadow, y - h / 2 + shadow, w, h, h / 2); ctx.fill(); }
  ctx.fillStyle = C.paper; ctx.beginPath(); ctx.roundRect(x, y - h / 2, w, h, h / 2); ctx.fill();
  ctx.fillStyle = track; ctx.fill();
  if (k > 0) {
    ctx.save();
    ctx.beginPath(); ctx.roundRect(x, y - h / 2, w, h, h / 2); ctx.clip();
    ctx.fillStyle = fill;
    ctx.beginPath(); ctx.roundRect(x - h, y - h / 2, w * k + h, h, h / 2); ctx.fill();
    ctx.restore();
  }
  ctx.lineWidth = lw; ctx.strokeStyle = C.ink;
  ctx.beginPath(); ctx.roundRect(x, y - h / 2, w, h, h / 2); ctx.stroke();
}

function sunburst(x, y, t, alpha, n = 18) {
  ctx.save();
  ctx.translate(x, y); ctx.rotate(t * 0.15);
  ctx.globalAlpha *= alpha;
  ctx.fillStyle = C.orange;
  for (let i = 0; i < n; i++) {
    ctx.rotate(TAU / n);
    ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(-90, -1400); ctx.lineTo(90, -1400); ctx.closePath(); ctx.fill();
  }
  ctx.restore();
}

function strike(x0, x1, y, k, o = {}) {   // hand-drawn strike-through
  const { lw = 20, color = C.orange, tilt = -0.04 } = o;
  if (k <= 0) return;
  ctx.save();
  ctx.lineCap = 'round'; ctx.lineWidth = lw; ctx.strokeStyle = color;
  ctx.beginPath(); ctx.moveTo(x0, y + (x1 - x0) * -tilt / 2);
  ctx.lineTo(lerp(x0, x1, k), y + (x1 - x0) * -tilt / 2 + (x1 - x0) * k * tilt);
  ctx.stroke();
  ctx.restore();
}

function confetti(x, y, lt, seed = 3) {
  if (lt < 0 || lt > 1.4) return;
  const rand = rng(seed), cols = [C.orange, C.green, C.ink, C.orangeTint];
  for (let i = 0; i < 34; i++) {
    const a = rand() * TAU, v = 500 + rand() * 700, rot = rand() * TAU;
    const px = x + Math.cos(a) * v * lt, py = y + Math.sin(a) * v * lt * 0.8 + 900 * lt * lt;
    ctx.save();
    ctx.globalAlpha *= 1 - clamp((lt - 0.9) / 0.5);
    ctx.translate(px, py); ctx.rotate(rot + lt * 8 * (rand() - 0.5));
    ctx.fillStyle = cols[i % cols.length];
    ctx.fillRect(-9, -5, 18, 10);
    ctx.restore();
  }
}

// ---------------------------------------------------------------- cues
// SFX cues (consumed by tools/build_audio.py) and camera shakes.
const CUES = [], SHAKES = [];
const cue = (t, type, gain = 1) => CUES.push({ t: +t.toFixed(3), type, gain });
const shake = (t, amp) => SHAKES.push({ t, amp });

// ---------------------------------------------------------------- timing
const T = {};
function buildTiming() {
  T.hook = { dos: tok('hook', 'dos').start, sellos: tok('hook', 'sellos').start,
             antes: tok('hook', 'antes').start, compres: tok('hook', 'compres').start, nada: tok('hook', 'nada').start };
  T.giro = { start: S('giro'), gen: tok('giro', 'generosidad'), psico: tok('giro', 'psicología').start,
             llama: tok('giro', 'llama').start, el: tok('giro', 'el').start, progreso: tok('giro', 'progreso').start,
             dotado: tok('giro', 'dotado') };
  T.exp = { start: S('experimento'), auto: tok('experimento', 'autolavado').start, rep: tok('experimento', 'repartió').start,
            una: tok('experimento', 'una').start, ocho: tok('experimento', '8').start,
            otra: tok('experimento', 'la').start, diez: tok('experimento', '10').start,
            pero: tok('experimento', 'pero').start, dos: tok('experimento', '2').start,
            sellados: tok('experimento', 'sellados').start,
            las: tok('resultado', 'las').start, exact: tok('resultado', 'exactamente').start,
            compras: tok('resultado', '8').start };
  T.chart = { start: tok('resultado', 'con').start - 0.12, blanco: tok('resultado', 'blanco').start,
              f19: tok('resultado', '19%'), con2: tok('resultado', 'con', 1).start,
              empezada: tok('resultado', 'empezada').start, f34: tok('resultado', '34%'),
              casi: tok('resultado', 'casi').start, doble: tok('resultado', 'doble') };
  T.brain = { start: S('porque'), avanzaste: tok('porque', 'avanzaste').start, cerebro: tok('porque', 'cerebro').start,
              dejar: tok('porque', 'dejar').start, medias: tok('porque', 'medias').start };
  T.bar = { start: tok('porque', 'ya', 1).start - 0.12, ocho: tok('porque', '8').start, pasos: tok('porque', 'pasos').start,
            por: tok('porque', 'por').start, meta: tok('porque', 'meta').start, f20: tok('porque', '20%'),
            cumplida: tok('porque', 'cumplida').start };
  T.donde = { start: S('donde'), perfiles: tok('donde', 'perfiles').start, p20: tok('donde', '20%'),
              apps: tok('donde', 'apps').start, puntos: tok('donde', 'puntos').start,
              cursos: tok('donde', 'cursos').start, primera: tok('donde', 'primera').start, lista: tok('donde', 'lista').start };
  T.app = { start: S('aplicacion'), negocio: tok('aplicacion', 'negocio').start, no: tok('aplicacion', 'no').start,
            desc: tok('aplicacion', 'descuentos'), regala: tok('aplicacion', 'regala').start,
            progreso: tok('aplicacion', 'progreso').start };
  T.cta = { start: S('cta'), sigueme: tok('cta', 'sígueme').start, psico: tok('cta', 'psicología').start,
            marcas: tok('cta', 'marcas').start, contigo: tok('cta', 'contigo') };
  T.cta.click = Math.max(T.cta.contigo.end + 0.05, T.cta.marcas + 0.6);
  T.cta.loop = Math.max(T.cta.click + 0.75, DUR - 0.9);
}

// ------------------------------------------------------------------ scenes
const SCENES = [];
function scene(id, start, end, draw, enter = 'zoom', exit = 'zoom') {
  SCENES.push({ id, start, end, draw, enter, exit });
}

// HOOK — card slams in, two stamps hit, "0 compras".
function drawHook(t) {
  const h = T.hook;
  const push = 1 + 0.08 * P(t, h.antes, 0.7, E.inOut3);
  ctx.translate(CX, 700); ctx.scale(push, push); ctx.translate(-CX, -700);
  const k = clamp(t / 0.42);
  const sc = lerp(1.35, 1, E.backSoft(k)), rot = lerp(-10, -4, E.out3(k)) * DEG;
  loyaltyCard(t, { x: CX, y: 700, w: 790, h: 500, rot, scale: sc, cols: 5, slots: 10,
                   stamps: [{ i: 0, t: h.dos }, { i: 1, t: h.sellos }] });
  // "¡PUM!" next to each stamp
  pumText(235, 390, t - h.dos, -12 * DEG);
  pumText(470, 362, t - h.sellos, 9 * DEG);
  // "COMPRAS: 0" tag
  const kt = P(t, h.compres - 0.1, 0.35, E.back);
  if (kt > 0) {
    const wig = Math.sin(clamp((t - h.nada) / 0.5) * Math.PI * 4) * 5 * DEG * (t > h.nada ? 1 : 0);
    ctx.save();
    ctx.translate(700, 1035); ctx.rotate(-6 * DEG + wig); ctx.scale(kt, kt);
    panel(-190, -52, 380, 104, 52, { fill: C.ink, lw: 0, shadow: 0 });
    txt('COMPRAS:', -40, 0, { size: 40, weight: 900, color: C.paper, ls: 2 });
    const bump = 1 + 0.35 * Math.exp(-Math.max(0, t - h.nada) * 8) * (t > h.nada ? 1 : 0);
    txt('0', 120, 0, { size: 64 * bump, weight: 900, color: C.orange });
    ctx.restore();
  }
  for (let i = 0; i < 5; i++) sparkle(170 + i * 170, 420 + (i % 2) * 520, 26, (t - h.sellos - 0.2 - i * 0.12) / 0.7);
}

// GIRO — "generosidad" crossed out, "psicología", title with shine.
let titleCanvas = null;
function drawGiro(t) {
  const g = T.giro;
  const flipK = clamp((t - (g.llama - 0.05)) / 0.24);      // phase A/B flip out
  if (t < g.llama + 0.2) {
    ctx.save();
    ctx.translate(CX, 720); ctx.scale(1 - E.in3(flipK) * 0.98, 1); ctx.translate(-CX, -720);
    const up = P(t, g.psico - 0.05, 0.35, E.out3);
    const kG = P(t, g.start, 0.35, E.back);
    ctx.save();
    ctx.globalAlpha *= 1 - 0.5 * P(t, g.gen.end + 0.2, 0.3);
    gift(CX, 480 - up * 40, kG * (1.05 - 0.3 * up), 0);
    ctx.restore();
    txt('NO ES', CX, 690 - up * 90, { size: 46, weight: 600, ls: 8, alpha: P(t, g.start, 0.2) });
    const genA = 1 - 0.55 * P(t, g.gen.end + 0.2, 0.3);
    txt('GENEROSIDAD', CX, 790 - up * 90, { size: 112, weight: 900, maxW: 820,
        alpha: P(t, g.gen.start - 0.1, 0.2) * genA, shadow: 0 });
    strike(130, 950, 790 - up * 90, P(t, g.gen.end - 0.05, 0.25, E.out3), { lw: 22 });
    const kP = P(t, g.psico - 0.05, 0.32, E.back);
    if (kP > 0) {
      ctx.save();
      ctx.translate(CX, 930); ctx.rotate(-3 * DEG); ctx.scale(lerp(1.7, 1, kP), lerp(1.7, 1, kP));
      ctx.globalAlpha *= clamp(kP * 3);
      txt('ES', 0, -70, { size: 44, weight: 600, ls: 8 });
      txt('PSICOLOGÍA', 0, 30, { size: 124, weight: 900, color: C.orange, maxW: 840, stroke: 0, shadow: 10 });
      ctx.restore();
    }
    ctx.restore();
  }
  if (t >= g.llama + 0.15) {
    const k = clamp((t - (g.llama + 0.15)) / 0.24);
    sunburst(CX, 720, t, 0.07 * k);
    ctx.save();
    ctx.translate(CX, 720); ctx.scale(E.out3(k), 1); ctx.rotate(-3 * DEG); ctx.translate(-CX, -720);
    // render title into an offscreen canvas so the shine only touches the letters
    if (!titleCanvas) { titleCanvas = document.createElement('canvas'); titleCanvas.width = W; titleCanvas.height = 700; }
    const kE = P(t, g.el - 0.08, 0.3, E.back), kPr = P(t, g.progreso - 0.08, 0.32, E.back), kD = P(t, g.dotado.start - 0.08, 0.34, E.back);
    withCtx(titleCanvas.getContext('2d'), () => {
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.clearRect(0, 0, W, 700);
      ctx.save(); ctx.translate(CX, 120); ctx.scale(kE, kE); txt('EL EFECTO DE', 0, 0, { size: 54, weight: 600, ls: 10 }); ctx.restore();
      ctx.save(); ctx.translate(CX, 290); ctx.scale(kPr, kPr); txt('PROGRESO', 0, 0, { size: 160, weight: 900, maxW: 860, shadow: 12, shadowColor: C.orange }); ctx.restore();
      ctx.save(); ctx.translate(CX, 480); ctx.scale(kD, kD); txt('DOTADO', 0, 0, { size: 196, weight: 900, color: C.orange, maxW: 860, shadow: 12 }); ctx.restore();
      const sh = (t - g.dotado.end + 0.1) / 0.75;                   // shine sweep, letters only
      if (sh > 0 && sh < 1) {
        ctx.save();
        ctx.globalCompositeOperation = 'source-atop';
        const sx = lerp(-300, W + 300, E.inOut3(sh));
        const gr = ctx.createLinearGradient(sx - 160, 0, sx + 160, 140);
        gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.85)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = gr; ctx.fillRect(0, 0, W, 700);
        ctx.restore();
      }
    });
    ctx.drawImage(titleCanvas, 0, 400);
    txt('(ENDOWED PROGRESS EFFECT)', CX, 1080, { size: 28, weight: 600, ls: 5, color: 'rgba(26,26,26,0.55)',
        alpha: P(t, g.dotado.end, 0.4) });
    ctx.restore();
    for (let i = 0; i < 6; i++) {
      const sx = [190, 880, 240, 860, 150, 920][i], sy = [470, 520, 1010, 960, 760, 760][i];
      sparkle(sx, sy, 30, (t - g.dotado.start - i * 0.15) / 0.8);
      sparkle(sx, sy, 22, (t - g.dotado.start - 1.0 - i * 0.15) / 0.8);
    }
  }
}

// EXPERIMENTO — car wash, two cards A (8) and B (10 with 2 stamped).
function drawExp(t) {
  const e = T.exp;
  const carOut = P(t, e.rep - 0.1, 0.35, E.in3);
  if (carOut < 1) {
    const cx = lerp(-300, CX, P(t, e.start, 0.6, E.out5)) - carOut * 0;
    ctx.save();
    ctx.globalAlpha *= 1 - carOut;
    ctx.translate(0, -carOut * 120);
    bubbles(CX, 760, t, e.auto - 0.3, 16);
    car(cx, 780, 1.25 * (1 - carOut * 0.5), t);
    txt('Nunes & Drèze (2006)', CX, 1040, { size: 30, weight: 600, color: 'rgba(26,26,26,0.55)', alpha: P(t, e.auto, 0.4) * (1 - carOut) });
    ctx.restore();
  }
  // focus: A while "una pedía 8", B while "la otra pedía 10" / stamps, both after "las dos"
  const fA = P(t, e.una - 0.1, 0.3) * (1 - P(t, e.otra - 0.1, 0.3)) ;
  const fB = P(t, e.otra - 0.1, 0.3) * (1 - P(t, e.las - 0.1, 0.3));
  const both = P(t, e.las - 0.1, 0.3);
  const cards = [
    { x: 330, rot: -3, slots: 8, gridY: 30, gapY: 86, stamps: [], focus: fA, other: fB, badge: 'A', t0: e.rep,
      reveal: e.una + 0.1, footer: '8 LAVADOS' },
    { x: 750, rot: 3, slots: 10, gridY: 42, gapY: 79, stamps: [{ i: 0, t: e.dos }, { i: 1, t: e.sellados }], focus: fB,
      other: fA, badge: 'B', t0: e.rep + 0.12, reveal: e.otra + 0.1, footer: '10 LAVADOS' },
  ];
  for (const c of cards) {
    const kIn = P(t, c.t0, 0.45, E.back);
    if (kIn <= 0) continue;
    const y = lerp(1500, 725, P(t, c.t0, 0.45, E.out5)), rot = lerp(c.rot * 5, c.rot, kIn) * DEG;
    const sc = (1 + 0.06 * c.focus - 0.06 * c.other) * lerp(1, 0.97, both);
    loyaltyCard(t, { x: c.x, y, w: 370, h: 600, rot, scale: sc, dim: c.other, slots: c.slots, cols: 2, r: 35,
                     gapX: 120, gapY: c.gapY, gridY: c.gridY, header: 'portrait', title: 'AUTOLAVADO',
                     sub: `Tarjeta ${c.badge}`, badge: c.badge, stamps: c.stamps,
                     reveal: { t0: c.reveal, step: 0.07 }, hi: P(t, e.exact, 0.3),
                     footer: t > c.reveal ? c.footer : '', footerColor: c.focus > 0.5 ? C.orange : C.ink });
  }
  pill('EL EXPERIMENTO', CX, 345, { size: 32, scale: P(t, e.start, 0.35, E.back) });
  // "¡2 de regalo!" sticker on card B
  const kS = P(t, e.sellados + 0.35, 0.3, E.back);
  if (kS > 0) pill('¡2 DE REGALO!', 820, 420, { size: 30, fill: C.green, color: '#fff', scale: kS * (1 - 0.15 * both), rot: 8 * DEG });
  // bracket + "= 8 compras"
  const kb = P(t, e.las + 0.2, 0.5, E.out3);
  if (kb > 0) {
    ctx.save();
    ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    const half = 370 * kb;
    ctx.beginPath();
    ctx.moveTo(CX - half, 1040); ctx.lineTo(CX - half, 1062); ctx.lineTo(CX + half, 1062); ctx.lineTo(CX + half, 1040);
    ctx.moveTo(CX, 1062); ctx.lineTo(CX, 1062 + 20 * kb);
    ctx.stroke();
    ctx.restore();
  }
  const kc = P(t, e.compras - 0.1, 0.35, E.back);
  if (kc > 0) {
    ctx.save();
    ctx.translate(CX, 1125); ctx.scale(kc, kc);
    const parts = [['=', 46, C.paper, 0], ['8', 62, C.orange, 0], ['COMPRAS', 44, C.paper, 2]];
    const ws = parts.map(([s, z, , ls]) => measure(s, z, 900, ls));
    const gap = 22, total = ws.reduce((a, b) => a + b, 0) + gap * 2;
    panel(-total / 2 - 40, -46, total + 80, 92, 46, { fill: C.ink, lw: 0, shadow: 0 });
    let px = -total / 2;
    parts.forEach(([s, z, col, ls], i) => { txt(s, px, 0, { size: z, weight: 900, color: col, ls, align: 'left' }); px += ws[i] + gap; });
    ctx.restore();
  }
}

// RESULTADO — bar chart 19% vs 34%, "casi el doble".
function drawChart(t) {
  const c = T.chart;
  const base = 1020, px = 13;
  txt('TERMINARON LA TARJETA', CX, 345, { size: 36, weight: 800, ls: 4, alpha: P(t, c.start, 0.3) });
  // axis + gridlines
  const kAx = P(t, c.start, 0.5, E.out3);
  ctx.save();
  ctx.strokeStyle = 'rgba(26,26,26,0.12)'; ctx.lineWidth = 3; ctx.setLineDash([10, 10]);
  for (const v of [10, 20, 30, 40]) {
    ctx.beginPath(); ctx.moveTo(170, base - v * px); ctx.lineTo(170 + 740 * kAx, base - v * px); ctx.stroke();
  }
  ctx.setLineDash([]);
  ctx.lineWidth = 8; ctx.strokeStyle = C.ink; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(CX - 370 * kAx, base); ctx.lineTo(CX + 370 * kAx, base); ctx.stroke();
  ctx.restore();
  const bars = [
    { x: 340, v: 19, f: c.f19, label: 'A · EN BLANCO', color: C.ink, on: c.blanco },
    { x: 740, v: 34, f: c.f34, label: 'B · CON 2 SELLOS', color: C.orange, on: c.empezada },
  ];
  for (const b of bars) {
    const ghost = P(t, c.start + 0.2, 0.3) * (1 - P(t, b.f.start - 0.1, 0.2));
    if (ghost > 0) {
      ctx.save();
      ctx.globalAlpha *= ghost;
      ctx.setLineDash([14, 12]); ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(26,26,26,0.35)';
      ctx.beginPath(); ctx.roundRect(b.x - 110, base - 300, 220, 300, [22, 22, 0, 0]); ctx.stroke();
      ctx.setLineDash([]);
      const bob = Math.sin(t * 5 + b.x) * 6;
      txt('?', b.x, base - 150 + bob, { size: 120, weight: 900, color: 'rgba(26,26,26,0.25)' });
      ctx.restore();
    }
    const dur = Math.max(0.6, b.f.end - b.f.start);
    const k = P(t, b.f.start, dur, E.out3);
    const settle = 1 + 0.06 * Math.exp(-Math.max(0, t - b.f.start - dur) * 7) * Math.sin(Math.max(0, t - b.f.start - dur) * 30);
    const hgt = b.v * px * k * settle;
    ctx.save();
    if (hgt > 1) {
      ctx.fillStyle = C.ink;
      ctx.beginPath(); ctx.roundRect(b.x - 110 + 12, base - hgt + 12, 220, hgt - 12, [22, 22, 0, 0]); ctx.fill();
      ctx.fillStyle = b.color;
      ctx.beginPath(); ctx.roundRect(b.x - 110, base - hgt, 220, hgt, [22, 22, 0, 0]); ctx.fill();
      ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
    }
    if (t >= b.f.start - 0.05)
      txt(`${Math.round(b.v * k)}%`, b.x, base - hgt - 56, { size: 66, weight: 900, color: b.color === C.ink ? C.ink : C.orange,
          shadow: b.color === C.ink ? 0 : 6 });
    const kl = P(t, c.start + (b.x > CX ? 0.15 : 0), 0.35, E.back);
    const hl = P(t, b.on - 0.05, 0.25);
    ctx.translate(b.x, 1068); ctx.scale(kl, kl);
    txt(b.label, 0, 0, { size: 30, weight: 800, ls: 1, color: hl > 0.5 ? C.orange : C.ink });
    if (hl > 0) { ctx.fillStyle = C.orange; ctx.fillRect(-140 * hl, 30, 280 * hl, 6); }
    ctx.restore();
  }
  // "casi el doble": arrow from A to B + "×1.8" badge (34 / 19)
  const ka = P(t, c.casi - 0.05, 0.45, E.out3);
  if (ka > 0) {
    const p0 = [395, 655], p1 = [450, 440], p2 = [640, 515];
    ctx.save();
    ctx.lineWidth = 9; ctx.strokeStyle = C.ink; ctx.lineCap = 'round'; ctx.setLineDash([2, 18]);
    ctx.beginPath();
    const N = 30;
    for (let i = 0; i <= N * ka; i++) {
      const u = i / N, x = (1 - u) ** 2 * p0[0] + 2 * (1 - u) * u * p1[0] + u * u * p2[0];
      const y = (1 - u) ** 2 * p0[1] + 2 * (1 - u) * u * p1[1] + u * u * p2[1];
      i ? ctx.lineTo(x, y) : ctx.moveTo(x, y);
    }
    ctx.stroke();
    ctx.setLineDash([]);
    if (ka >= 0.98) {                                  // arrow head
      ctx.translate(p2[0], p2[1]); ctx.rotate(Math.atan2(p2[1] - p1[1], p2[0] - p1[0]));
      ctx.fillStyle = C.ink; ctx.beginPath(); ctx.moveTo(14, 0); ctx.lineTo(-22, -18); ctx.lineTo(-22, 18); ctx.closePath(); ctx.fill();
    }
    ctx.restore();
    const kbdg = P(t, c.doble.start - 0.05, 0.35, E.back);
    if (kbdg > 0) {
      burst(460, 485, 56, t - c.doble.start, C.green, 10, 5);
      pill('×1.8', 460, 485, { size: 58, weight: 900, fill: C.green, color: '#fff', h: 108, padX: 36, scale: kbdg, rot: -8 * DEG, ls: 0 });
    }
  }
}

// POR QUÉ — brain with gears, then "a medias".
function drawBrain(t) {
  const b = T.brain;
  const kIn = P(t, b.start, 0.45, E.back);
  const zoom = 1 + 0.1 * P(t, b.cerebro - 0.1, 0.5, E.inOut3) - 0.1 * P(t, b.dejar - 0.1, 0.4, E.inOut3);
  const spinRate = 0.8 + 3.2 * P(t, b.cerebro - 0.1, 0.4);
  const spin = (t - b.start) * spinRate;
  const lift = P(t, b.dejar - 0.1, 0.4, E.out3);
  ctx.save();
  ctx.translate(CX, 700 - lift * 60); ctx.scale(kIn * zoom, kIn * zoom);
  // motion lines while the gears race
  const race = P(t, b.cerebro, 0.3) * (1 - P(t, b.dejar, 0.3));
  if (race > 0) {
    ctx.save(); ctx.globalAlpha *= race; ctx.strokeStyle = C.ink; ctx.lineWidth = 8; ctx.lineCap = 'round';
    for (let i = 0; i < 3; i++) {
      const off = ((t * 3 + i / 3) % 1) * 30;
      ctx.beginPath(); ctx.moveTo(-300 - off, -60 + i * 60); ctx.lineTo(-250 - off, -60 + i * 60);
      ctx.moveTo(250 + off, -60 + i * 60); ctx.lineTo(300 + off, -60 + i * 60); ctx.stroke();
    }
    ctx.restore();
  }
  brain(0, 0, 1.08, t, spin);
  checkBadge(210, -200, 54, (t - b.avanzaste) / 0.45);
  ctx.restore();
  // "!" alert + half-finished bar
  const kM = P(t, b.dejar - 0.05, 0.35, E.back);
  if (kM > 0) {
    const wig = Math.sin((t - b.dejar) * 26) * 4 * DEG * Math.exp(-Math.max(0, t - b.medias) * 1.5);
    ctx.save();
    ctx.translate(310 - 0, 470); ctx.rotate(wig); ctx.scale(kM, kM);
    ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(0, 0, 52, 0, TAU); ctx.fill();
    ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
    txt('!', 0, 0, { size: 72, weight: 900, color: '#fff' });
    ctx.restore();
    const kb = P(t, b.dejar, 0.4, E.out3);
    ctx.save();
    ctx.globalAlpha *= clamp(kb * 2);
    progressBar(170, 1040, 740, 70, 0.5 * P(t, b.dejar + 0.1, 0.5, E.out3));
    // pause symbol at the stall point
    const pulse = 0.6 + 0.4 * Math.sin(t * 10);
    ctx.fillStyle = C.ink; ctx.globalAlpha *= clamp((t - b.medias) / 0.2) * pulse;
    ctx.fillRect(170 + 370 + 22, 1040 - 20, 12, 40); ctx.fillRect(170 + 370 + 42, 1040 - 20, 12, 40);
    ctx.restore();
    txt('A MEDIAS', 170 + 555, 960, { size: 34, weight: 900, ls: 4, color: C.orange, alpha: P(t, b.medias, 0.25) });
  }
}

// POR QUÉ (2) — 8 steps to do → a 10-step bar already 20% done.
function drawBar(t) {
  const b = T.bar;
  const morph = P(t, b.por - 0.05, 0.5, E.inOut3);
  const segW = 74, x0 = 170, barY = 800;
  const kBar = E.out3(clamp((morph - 0.35) / 0.65));
  if (kBar > 0) {                                     // the 10-step bar grows in under the boxes
    ctx.save();
    ctx.translate(CX, barY); ctx.scale(kBar, 1); ctx.translate(-CX, -barY);
    ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(x0 - 12 + 10, barY - 62 + 10, 764, 124, 30); ctx.fill();
    ctx.fillStyle = C.paper; ctx.beginPath(); ctx.roundRect(x0 - 12, barY - 62, 764, 124, 30); ctx.fill();
    ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
    for (let i = 0; i < 2; i++) {                     // the two "gifted" slots
      ctx.setLineDash([8, 8]); ctx.lineWidth = 5; ctx.strokeStyle = 'rgba(26,26,26,0.3)';
      ctx.beginPath(); ctx.roundRect(x0 + i * segW + 5, barY - 50, segW - 10, 100, 16); ctx.stroke(); ctx.setLineDash([]);
    }
    ctx.restore();
  }
  flag(905, barY - 64, 0.9 * P(t, b.por + 0.3, 0.3, E.back));
  txt('TU META', 790, barY - 125, { size: 30, weight: 800, ls: 4, alpha: P(t, b.meta - 0.1, 0.3) });
  txt('PASOS POR HACER', CX, 400, { size: 40, weight: 800, ls: 4, alpha: P(t, b.pasos - 0.1, 0.3) * (1 - morph) });
  for (let i = 0; i < 8; i++) {                       // the 8 steps to do → slots 3..10
    const gx = 270 + (i % 4) * 180, gy = 590 + Math.floor(i / 4) * 200;
    const bx = x0 + (i + 2) * segW + segW / 2;
    const pop = P(t, b.ocho - 0.1 + i * 0.06, 0.25, E.back);
    if (pop <= 0) continue;
    const m = E.inOut3(clamp((t - (b.por - 0.05) - i * 0.025) / 0.45));
    const x = lerp(gx, bx, m), y = lerp(gy, barY, m);
    const w = lerp(150, segW - 10, m), h = lerp(150, 100, m), r = lerp(26, 16, m);
    ctx.save();
    ctx.translate(x, y); ctx.scale(pop, pop);
    ctx.fillStyle = C.paper; ctx.beginPath(); ctx.roundRect(-w / 2, -h / 2, w, h, r); ctx.fill();
    ctx.setLineDash(m > 0.6 ? [8, 8] : []);
    ctx.lineWidth = lerp(6, 5, m); ctx.strokeStyle = m > 0.6 ? 'rgba(26,26,26,0.3)' : C.ink; ctx.stroke();
    ctx.setLineDash([]);
    txt(String(i + 1), 0, 0, { size: 64, weight: 900, alpha: 1 - m });
    ctx.restore();
  }
  // gifted slots fill 0 → 20 %, then turn green with a check
  const f = b.f20, dur = Math.max(0.6, f.end - f.start);
  const fill = P(t, f.start, dur, E.out3);
  const green = P(t, b.cumplida, 0.3);
  for (let i = 0; i < 2; i++) {
    const k = clamp(fill * 2 - i);
    if (k <= 0) continue;
    ctx.fillStyle = green > 0.5 ? C.green : C.orange;
    ctx.beginPath(); ctx.roundRect(x0 + i * segW + 5, barY - 50, Math.max((segW - 10) * k, 1), 100, 16); ctx.fill();
    ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
  }
  if (t > f.start - 0.05)
    txt(`${Math.round(20 * fill)}%`, x0 + 2 * segW * fill, barY - 120, { size: 64, weight: 900,
        color: green > 0.5 ? C.green : C.orange, shadow: 6 });
  checkBadge(x0 + segW, barY + 165, 62, (t - b.cumplida) / 0.45);
  burst(x0 + segW, barY + 165, 62, t - b.cumplida - 0.1, C.green, 10, 9);
}

// DÓNDE — three generic mockups in a carousel.
function mockFrame(w, h) {
  panel(-w / 2, -h / 2, w, h, 44);
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(-60, -h / 2 + 18, 120, 14, 7); ctx.fill();
}
function mockProfile(t, d) {
  mockFrame(500, 640);
  avatar(0, -170, 72);
  ctx.fillStyle = 'rgba(26,26,26,0.14)';
  ctx.beginPath(); ctx.roundRect(-110, -70, 220, 22, 11); ctx.fill();
  ctx.beginPath(); ctx.roundRect(-75, -34, 150, 18, 9); ctx.fill();
  txt('Perfil completo', -200, 30, { size: 30, weight: 700, align: 'left' });
  const k = 0.2 * P(t, d.p20.start, Math.max(0.5, d.p20.end - d.p20.start), E.out3);
  progressBar(-200, 85, 330, 36, k / 1, { shadow: 0, lw: 5 });
  txt(`${Math.round(k * 100)}%`, 150, 85, { size: 32, weight: 900, color: C.orange, align: 'left' });
  const rows = [['Cuenta creada', true], ['Foto de perfil', false], ['Biografía', false], ['Intereses', false]];
  rows.forEach(([label, done], i) => {
    const y = 150 + i * 46;
    if (done) checkBadge(-185, y, 16, 1); else emptySlot(-185, y, 15, {});
    txt(label, -155, y, { size: 26, weight: 500, align: 'left', color: done ? C.ink : 'rgba(26,26,26,0.6)' });
  });
}
function mockPoints(t, d) {
  mockFrame(500, 640);
  txt('¡BIENVENIDO!', 0, -215, { size: 44, weight: 900 });
  const kc = P(t, d.apps + 0.1, 0.4, E.back);
  ctx.save(); ctx.translate(0, -95); ctx.scale(kc, kc); ctx.rotate(Math.sin(t * 3) * 0.08);
  ctx.fillStyle = C.ink; ctx.beginPath(); ctx.arc(8, 8, 82, 0, TAU); ctx.fill();
  ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(0, 0, 82, 0, TAU); ctx.fill();
  ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
  ctx.beginPath(); ctx.arc(0, 0, 60, 0, TAU); ctx.strokeStyle = 'rgba(255,255,255,0.7)'; ctx.lineWidth = 4; ctx.stroke();
  star(0, 0, 38, 16, 5, '#fff');
  ctx.restore();
  const kp = P(t, d.puntos - 0.1, 0.35, E.back);
  ctx.save(); ctx.translate(0, 45); ctx.scale(kp, kp);
  txt('+500 PTS', 0, 0, { size: 72, weight: 900, color: C.orange, shadow: 6 });
  ctx.restore();
  txt('de bienvenida', 0, 100, { size: 28, weight: 500, alpha: kp });
  const k = 0.25 * P(t, d.puntos, 0.6, E.out3);
  progressBar(-200, 175, 400, 36, k, { shadow: 0, lw: 5 });
  txt('500 / 2000 para tu premio', 0, 230, { size: 24, weight: 600, color: 'rgba(26,26,26,0.65)' });
}
function mockCourse(t, d) {
  mockFrame(500, 640);
  txt('MI CURSO', 0, -225, { size: 42, weight: 900 });
  txt('10 lecciones', 0, -180, { size: 26, weight: 500, color: 'rgba(26,26,26,0.65)' });
  const kChk = (t - d.lista + 0.05) / 0.45;
  for (let i = 0; i < 4; i++) {
    const y = -105 + i * 82;
    ctx.fillStyle = i === 0 && kChk > 0 ? C.greenTint : 'rgba(26,26,26,0.04)';
    ctx.beginPath(); ctx.roundRect(-210, y - 32, 420, 64, 18); ctx.fill();
    ctx.lineWidth = 4; ctx.strokeStyle = 'rgba(26,26,26,0.18)'; ctx.stroke();
    if (i === 0) {
      emptySlot(-170, y, 18, { alpha: kChk > 0.3 ? 0 : 1 });
      checkBadge(-170, y, 20, kChk);
    } else emptySlot(-170, y, 18, {});
    txt(`Lección ${i + 1}`, -135, y, { size: 28, weight: 700, align: 'left', color: i === 0 ? C.ink : 'rgba(26,26,26,0.55)' });
    if (i === 0) pill('LISTA', 140, y, { size: 22, fill: C.green, color: '#fff', h: 40, padX: 16, ls: 2, scale: P(t, d.lista, 0.3, E.back) });
  }
  const k = 0.1 * P(t, d.lista, 0.5, E.out3);
  progressBar(-200, 245, 330, 36, k, { shadow: 0, lw: 5, fill: C.green });
  txt(`${Math.round(k * 10)}/10`, 150, 245, { size: 30, weight: 900, align: 'left', color: C.green });
}
function drawDonde(t) {
  const d = T.donde;
  pill('¿DÓNDE LO VES?', CX, 345, { size: 34, scale: P(t, d.start, 0.35, E.back) });
  const switches = [d.start, d.apps - 0.35, d.cursos - 0.35];
  let active = 0;
  switches.forEach((s, i) => { active += i ? P(t, s, 0.4, E.out3) : 0; });
  const enter = P(t, d.start, 0.45, E.out3);
  const mocks = [mockProfile, mockPoints, mockCourse];
  for (let i = 0; i < 3; i++) {
    const off = i - active + (1 - enter) * 1.2;
    if (Math.abs(off) > 1.3) continue;
    ctx.save();
    ctx.translate(CX + off * 660, 770 + Math.abs(off) * 40);
    ctx.rotate(off * 7 * DEG);
    const s = 1 - 0.2 * Math.min(1, Math.abs(off));
    ctx.scale(s, s);
    mocks[i](t, d);
    const veil = 0.6 * Math.min(1, Math.abs(off));
    if (veil > 0.01) {
      ctx.fillStyle = `rgba(245,239,230,${veil})`;
      ctx.beginPath(); ctx.roundRect(-262, -332, 540, 690, 44); ctx.fill();
    }
    ctx.restore();
  }
  // carousel dots
  for (let i = 0; i < 3; i++) {
    const on = 1 - Math.min(1, Math.abs(i - active));
    ctx.fillStyle = on > 0.5 ? C.orange : 'rgba(26,26,26,0.25)';
    ctx.beginPath(); ctx.roundRect(CX - 60 + i * 50 - 8 - on * 8, 1135 - 8, 16 + on * 16, 16, 8); ctx.fill();
  }
}

// APLICACIÓN — store → "descuentos" crossed out → "PROGRESO" with stamps.
const RING = [[190, 500, -12], [880, 470, 10], [150, 1000, 8], [900, 980, -9], [CX, 1090, 4]];
function drawApp(t) {
  const a = T.app;
  const out = P(t, a.regala - 0.12, 0.22, E.in3);
  if (out < 1) {
    ctx.save();
    ctx.globalAlpha *= 1 - out;
    ctx.translate(0, -out * 200);
    const up = P(t, a.no - 0.1, 0.4, E.inOut3);
    const ks = P(t, a.start, 0.45, E.back);
    store(CX, lerp(720, 470, up), ks * lerp(1.25, 0.72, up));
    sparkle(820, 520, 34, (t - a.negocio) / 0.7);
    sparkle(250, 600, 26, (t - a.negocio - 0.15) / 0.7);
    const kD = P(t, a.no - 0.05, 0.3, E.back);
    if (kD > 0) {
      ctx.save(); ctx.translate(CX, 860); ctx.scale(kD, kD);
      txt('DESCUENTOS', 0, 0, { size: 130, weight: 900, maxW: 800, alpha: 1 - 0.5 * P(t, a.desc.end, 0.3) });
      ctx.restore();
      strike(140, 940, 860, P(t, a.desc.end - 0.12, 0.25, E.out3), { lw: 24 });
      // -20% tag that falls off once crossed out
      const fall = P(t, a.desc.end + 0.1, 0.6, E.in3);
      ctx.save();
      ctx.translate(850, lerp(735, 1400, fall)); ctx.rotate((14 + fall * 80) * DEG); ctx.scale(kD, kD);
      ctx.globalAlpha *= 1 - fall;
      ctx.fillStyle = C.ink; ctx.beginPath(); ctx.roundRect(-82 + 8, -44 + 8, 164, 88, 18); ctx.fill();
      ctx.fillStyle = C.orange; ctx.beginPath(); ctx.roundRect(-82, -44, 164, 88, 18); ctx.fill();
      ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
      txt('-20%', 0, 0, { size: 48, weight: 900, color: '#fff' });
      ctx.restore();
    }
    ctx.restore();
  }
  if (t >= a.regala - 0.1) {
    sunburst(CX, 760, t, 0.07 * P(t, a.progreso, 0.3));
    const kR = P(t, a.regala - 0.08, 0.3, E.back), kP = P(t, a.progreso - 0.08, 0.36, E.back);
    txt('REGALA', CX, 620, { size: 60, weight: 600, ls: 12, alpha: clamp(kR * 2) });
    ctx.save(); ctx.translate(CX, 770); ctx.scale(lerp(1.8, 1, kP), lerp(1.8, 1, kP)); ctx.globalAlpha *= clamp(kP * 3);
    txt('PROGRESO', 0, 0, { size: 170, weight: 900, maxW: 820, shadow: 12, shadowColor: C.orange });
    ctx.restore();
    const ku = P(t, a.progreso + 0.25, 0.4, E.out3);
    ctx.fillStyle = C.green; ctx.beginPath(); ctx.roundRect(CX - 300 * ku, 880, 600 * ku, 18, 9); ctx.fill();
    RING.forEach(([x, y, r], i) => stamp(x, y, 62, t - (a.progreso + 0.18 + i * 0.14), r * DEG, i % 2 ? C.green : C.orange));
  }
}

// CTA — profile, "SEGUIR" click → "SIGUIENDO", then the loyalty card flies in (loop).
function drawCta(t) {
  const c = T.cta;
  const fade = P(t, c.loop, 0.35, E.in3);
  ctx.save();
  ctx.translate(CX, 760); ctx.scale(1 - fade * 0.4, 1 - fade * 0.4); ctx.translate(-CX, -760);
  ctx.globalAlpha *= 1 - fade;
  sunburst(CX, 520, t, 0.06 * P(t, c.start, 0.4));
  const kA = P(t, c.start, 0.4, E.back);
  ctx.save(); ctx.translate(CX, 520); ctx.scale(kA, kA);
  ctx.setLineDash([16, 14]); ctx.lineDashOffset = -t * 40; ctx.lineWidth = 6; ctx.strokeStyle = C.orange;
  ctx.beginPath(); ctx.arc(0, 0, 150, 0, TAU); ctx.stroke(); ctx.setLineDash([]);
  avatar(0, 0, 122);
  ctx.restore();
  const kH = P(t, c.start + 0.12, 0.4, E.back);
  ctx.save(); ctx.translate(CX, 745); ctx.scale(kH, kH);
  txt('@TUCUENTA', 0, 0, { size: 100, weight: 900, maxW: 820, shadow: 8, shadowColor: C.orange });
  ctx.restore();
  txt('Psicología de marcas', CX, 830, { size: 36, weight: 500, color: 'rgba(26,26,26,0.7)', alpha: P(t, c.psico - 0.1, 0.3) });
  // three mini tiles recapping the video ("más trucos")
  for (let i = 0; i < 3; i++) {
    const k = P(t, c.psico - 0.1 + i * 0.12, 0.35, E.back) * (1 - P(t, c.click - 0.6, 0.3));
    if (k <= 0) continue;
    ctx.save();
    ctx.translate(CX + (i - 1) * 190, 1135); ctx.rotate((i - 1) * 4 * DEG); ctx.scale(k, k);
    panel(-68, -60, 136, 120, 22, { lw: 5, shadow: 8 });
    if (i === 0) {
      for (let j = 0; j < 4; j++) {
        const x = -36 + (j % 2) * 72 - 0, y = -24 + Math.floor(j / 2) * 48;
        if (j < 2) { ctx.fillStyle = C.orange; ctx.beginPath(); ctx.arc(x, y, 16, 0, TAU); ctx.fill(); ctx.lineWidth = 3; ctx.strokeStyle = C.ink; ctx.stroke(); }
        else emptySlot(x, y, 15, {});
      }
    } else if (i === 1) {
      ctx.fillStyle = C.ink; ctx.fillRect(-40, 2, 30, 38);
      ctx.fillStyle = C.orange; ctx.fillRect(8, -32, 30, 72);
      ctx.lineWidth = 3; ctx.strokeStyle = C.ink; ctx.strokeRect(8, -32, 30, 72);
      ctx.fillRect(-48, 40, 96, 4);
    } else {
      progressBar(-50, 18, 100, 22, 0.2, { shadow: 0, lw: 3, fill: C.green });
      checkBadge(0, -22, 20, 1);
    }
    ctx.restore();
  }
  // follow button
  const kB = P(t, c.start + 0.25, 0.4, E.back);
  const followed = t >= c.click + 0.08;
  const press = t >= c.click && t < c.click + 0.16 ? 0.92 : 1;
  const beatPulse = followed ? 1 : 1 + 0.035 * Math.max(0, Math.cos(((t % BEAT) / BEAT) * Math.PI));
  ctx.save();
  ctx.translate(CX, 975); ctx.scale(kB * press * beatPulse, kB * press * beatPulse);
  panel(-230, -66, 460, 132, 66, { fill: followed ? C.green : C.orange, shadow: 12 });
  if (followed) {
    txt('SIGUIENDO', -28, 0, { size: 48, weight: 900, color: '#fff', ls: 3 });
    ctx.lineCap = 'round'; ctx.lineJoin = 'round'; ctx.lineWidth = 10; ctx.strokeStyle = '#fff';
    ctx.beginPath(); ctx.moveTo(150, 0); ctx.lineTo(166, 16); ctx.lineTo(196, -18); ctx.stroke();
  } else txt('SEGUIR', 0, 0, { size: 60, weight: 900, color: '#fff', ls: 3 });
  ctx.restore();
  burst(CX, 975, 120, t - c.click, C.green, 12, 11);
  confetti(CX, 975, t - c.click - 0.05);
  // cursor glides in and clicks
  const kc = P(t, c.click - 0.85, 0.75, E.inOut3);
  if (t > c.click - 0.85) {
    const cx = lerp(860, 600, kc), cy = lerp(1320, 990, kc);
    const cs = t >= c.click && t < c.click + 0.14 ? 0.85 : 1;
    if (t >= c.click) {
      const rk = clamp((t - c.click) / 0.4);
      ctx.save(); ctx.globalAlpha *= 1 - rk; ctx.strokeStyle = C.ink; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.arc(cx, cy, 20 + rk * 50, 0, TAU); ctx.stroke(); ctx.restore();
    }
    cursor(cx, cy, cs);
  }
  ctx.restore();
  // loop: the hook's loyalty card rushes toward the camera, ending exactly at frame 0's pose
  if (t >= c.loop) {
    const k = clamp((t - c.loop) / (DUR - c.loop));
    const e = E.in3(k);
    loyaltyCard(t, { x: CX, y: lerp(975, 700, E.out3(k)), w: 790, h: 500, rot: lerp(0, -10, e) * DEG,
                     scale: lerp(0.12, 1.35, e), alpha: clamp(k * 5), cols: 5, slots: 10 });
  }
}

function registerScenes() {
  scene('hook', 0, S('giro'), drawHook, 'none', 'zoomThrough');
  scene('giro', S('giro'), S('experimento'), drawGiro, 'zoom', 'cut');
  scene('exp', S('experimento'), T.chart.start, drawExp, 'cut', 'zoomOut');
  scene('chart', T.chart.start, S('porque'), drawChart, 'zoom', 'cut');
  scene('brain', S('porque'), T.bar.start, drawBrain, 'cut', 'slide');
  scene('bar', T.bar.start, S('donde'), drawBar, 'slide', 'cut');
  scene('donde', S('donde'), S('aplicacion'), drawDonde, 'cut', 'zoomThrough');
  scene('app', S('aplicacion'), S('cta'), drawApp, 'zoom', 'cut');
  scene('cta', S('cta'), DUR + 1, drawCta, 'cut', 'none');
}
const WIPES = [];   // [{t, color}] — scene cuts hidden behind a diagonal band

function registerCues() {
  const h = T.hook;
  cue(0.0, 'thud', 0.8); shake(0.3, 10);
  cue(h.dos - 0.02, 'pum'); shake(h.dos, 16);
  cue(h.sellos - 0.02, 'pum'); shake(h.sellos, 16);
  cue(h.compres - 0.1, 'pop', 0.6);
  const g = T.giro;
  cue(S('giro') - 0.15, 'whoosh');
  cue(g.gen.end - 0.08, 'scratch', 0.7);
  cue(g.psico - 0.08, 'pop', 0.8);
  cue(g.llama - 0.08, 'whoosh', 0.6);
  cue(g.dotado.end, 'shine', 0.6);
  for (const s of [S('experimento'), S('porque'), S('donde'), S('cta')]) { cue(s - 0.2, 'whoosh'); }
  WIPES.push({ t: S('experimento'), color: C.orange }, { t: S('porque'), color: C.ink },
             { t: S('donde'), color: C.orange }, { t: S('cta'), color: C.ink });
  const e = T.exp;
  cue(e.start + 0.05, 'car', 0.55);
  cue(e.rep - 0.05, 'whoosh', 0.7);
  cue(e.ocho - 0.15, 'pops', 0.5); cue(e.diez - 0.15, 'pops', 0.5);
  cue(e.dos - 0.02, 'pum'); shake(e.dos, 14);
  cue(e.sellados - 0.02, 'pum'); shake(e.sellados, 14);
  cue(e.compras - 0.05, 'ding');
  const c = T.chart;
  cue(c.start - 0.15, 'whoosh');
  cue(c.f19.start, 'rise', 0.5); cue(Math.max(c.f19.start + 0.6, c.f19.end), 'ding');
  cue(c.f34.start, 'rise', 0.5); cue(Math.max(c.f34.start + 0.6, c.f34.end), 'ding');
  cue(c.doble.start - 0.02, 'pum'); shake(c.doble.start, 12);
  const b = T.brain;
  cue(b.avanzaste, 'ding', 0.7);
  cue(b.dejar, 'pop', 0.7);
  const br = T.bar;
  cue(br.start - 0.15, 'whoosh');
  cue(br.ocho - 0.1, 'pops', 0.5);
  cue(br.por - 0.05, 'whoosh', 0.5);
  cue(br.f20.start, 'rise', 0.5);
  cue(br.cumplida, 'ding'); shake(br.cumplida, 6);
  const d = T.donde;
  cue(d.apps - 0.4, 'whoosh', 0.7); cue(d.cursos - 0.4, 'whoosh', 0.7);
  cue(d.lista, 'ding');
  const a = T.app;
  cue(S('aplicacion') - 0.15, 'whoosh');
  cue(a.desc.end - 0.1, 'scratch', 0.8);
  cue(a.regala - 0.12, 'whoosh', 0.6);
  RING.forEach((_, i) => { const tt = a.progreso + 0.18 + i * 0.14; cue(tt - 0.02, 'pum', i ? 0.75 : 1); shake(tt, i ? 8 : 14); });
  const ct = T.cta;
  cue(ct.click, 'click'); cue(ct.click + 0.06, 'ding', 0.7);
  cue(ct.loop + 0.1, 'whoosh', 1.0);
  CUES.sort((x, y) => x.t - y.t);
}

// --------------------------------------------------------------- frame
// Applies the enter/exit transform for a scene; returns the scene's opacity.
function transition(type, k, isExit) {
  const cy = 760;
  const zoom = sc => { ctx.translate(CX, cy); ctx.scale(sc, sc); ctx.translate(-CX, -cy); };
  if (!isExit) {
    if (type === 'zoom') { zoom(lerp(1.25, 1, E.out3(k))); return clamp(k * 2.5); }
    if (type === 'slide') ctx.translate((1 - E.out3(k)) * W, 0);
  } else {
    if (type === 'zoomThrough') { zoom(lerp(1, 2.6, E.in3(k))); return 1 - k; }
    if (type === 'zoomOut') { zoom(lerp(1, 0.75, E.in3(k))); return 1 - k; }
    if (type === 'slide') ctx.translate(-E.in3(k) * W, 0);
  }
  return 1;
}

// Scenes fading in/out are drawn on a layer first, so overlapping shapes fade as
// one group instead of showing through each other.
let layer = null;
function drawScenes(t) {
  for (const s of SCENES) {
    const exitDur = s.exit === 'cut' || s.exit === 'none' ? 0 : 0.24;
    if (t < s.start || t >= s.end + exitDur) continue;
    ctx.save();
    let alpha = 1;
    if (t < s.start + 0.32) alpha *= transition(s.enter, (t - s.start) / 0.32, false);
    if (t >= s.end) alpha *= transition(s.exit, (t - s.end) / exitDur, true);
    if (alpha >= 0.999) s.draw(t);
    else if (alpha > 0.001) {
      if (!layer) { layer = document.createElement('canvas'); layer.width = W; layer.height = H; }
      const m = ctx.getTransform();
      withCtx(layer.getContext('2d'), () => {
        ctx.setTransform(1, 0, 0, 1, 0, 0);
        ctx.clearRect(0, 0, W, H);
        ctx.setTransform(m);
        s.draw(t);
      });
      ctx.setTransform(1, 0, 0, 1, 0, 0);
      ctx.globalAlpha = alpha;
      ctx.drawImage(layer, 0, 0);
    }
    ctx.restore();
  }
}

function drawWipes(t) {
  for (const w of WIPES) {
    const k = (t - (w.t - 0.24)) / 0.48;
    if (k <= 0 || k >= 1) continue;
    const x = lerp(-1.75 * W, 1.75 * W, E.inOut3(k));
    ctx.save();
    ctx.translate(CX + x, H / 2); ctx.rotate(-0.24);
    ctx.fillStyle = w.color; ctx.fillRect(-W * 0.82, -H * 1.1, W * 1.64, H * 2.2);
    ctx.fillStyle = w.color === C.ink ? C.orange : C.ink;
    ctx.fillRect(-W * 0.82 - 60, -H * 1.1, 34, H * 2.2);
    ctx.restore();
  }
}

function cameraShake(t) {
  let dx = 0, dy = 0, rot = 0;
  for (const s of SHAKES) {
    const lt = t - s.t;
    if (lt < 0 || lt > 0.5) continue;
    const a = s.amp * Math.exp(-lt * 11);
    dx += a * Math.sin(lt * 71 + s.t); dy += a * Math.cos(lt * 63 + s.t * 2); rot += a * 0.0012 * Math.sin(lt * 50);
  }
  ctx.translate(CX + dx, 760 + dy); ctx.rotate(rot); ctx.translate(-CX, -760);
}

function drawBackground(t) {
  ctx.fillStyle = C.cream;
  ctx.fillRect(0, 0, W, H);
  // soft drifting blobs — every motion here completes whole cycles in 60 s so the loop is seamless
  const w = n => (TAU * n) / DUR;
  const beat = Math.exp(-((t % BEAT) / BEAT) * 5);
  ctx.fillStyle = 'rgba(255,90,31,0.07)';
  ctx.beginPath(); ctx.arc(160 + Math.sin(t * w(4)) * 60, 520 + Math.cos(t * w(3)) * 80, 260 + beat * 8, 0, TAU); ctx.fill();
  ctx.fillStyle = 'rgba(34,197,94,0.06)';
  ctx.beginPath(); ctx.arc(930 + Math.cos(t * w(3)) * 50, 1250 + Math.sin(t * w(2)) * 90, 300 + beat * 8, 0, TAU); ctx.fill();
  // dot grid drifting downward (13.5 px/s = 15 grid steps per loop)
  const sp = 54, off = (t * 13.5) % sp;
  ctx.fillStyle = 'rgba(26,26,26,0.075)';
  for (let y = -sp + off; y < H + sp; y += sp)
    for (let x = 27; x < W; x += sp) { ctx.beginPath(); ctx.arc(x, y, 2.4, 0, TAU); ctx.fill(); }
}

function drawTopProgress(t) {
  const x0 = SAFE.left, x1 = SAFE.right, y = 268, hh = 10;
  const k = clamp(t / DUR), done = t > DUR - 0.45;
  ctx.fillStyle = 'rgba(26,26,26,0.14)';
  ctx.beginPath(); ctx.roundRect(x0, y - hh / 2, x1 - x0, hh, hh / 2); ctx.fill();
  ctx.fillStyle = done ? C.green : C.orange;
  ctx.beginPath(); ctx.roundRect(x0, y - hh / 2, Math.max(hh, (x1 - x0) * k), hh, hh / 2); ctx.fill();
  for (const s of TL.sections.slice(1)) {                       // milestones per section
    const mx = x0 + (x1 - x0) * (S(s.id) / DUR), passed = t >= S(s.id);
    ctx.fillStyle = passed ? C.paper : 'rgba(26,26,26,0.3)';
    ctx.beginPath(); ctx.arc(mx, y, 3, 0, TAU); ctx.fill();
  }
  const hx = x0 + (x1 - x0) * k;
  ctx.fillStyle = C.paper; ctx.strokeStyle = done ? C.green : C.orange; ctx.lineWidth = 4;
  ctx.beginPath(); ctx.arc(hx, y, 9, 0, TAU); ctx.fill(); ctx.stroke();
}

// ------------------------------------------------------------- captions
const CAP = { y: 1350, size: 64, weight: 600, maxW: 790, lineH: 84, padX: 38, padY: 24 };

function wordState(t, tk) {
  if (t < tk.start) return { a: 0.42, s: 1, color: '#fff' };
  const en = Math.max(tk.end, tk.start + 0.15);
  const up = E.out3(clamp((t - tk.start) / 0.12)), down = clamp((t - en) / 0.15);
  return { a: 1, s: 1 + 0.07 * up * (1 - down), color: tk.kw ? C.orange : '#fff' };
}

function layoutWords(toks, size, weight, maxW) {
  const space = measure(' ', size, weight) + size * 0.16;
  const lines = [[]];
  let lw = 0;
  for (const tk of toks) {
    const w = measure(tk.text, size, weight);
    if (lines[lines.length - 1].length && lw + space + w > maxW) { lines.push([]); lw = 0; }
    const line = lines[lines.length - 1];
    lw += (line.length ? space : 0) + w;
    line.push({ tk, w });
  }
  return { lines, space, widths: lines.map(l => l.reduce((s, x) => s + x.w, 0) + space * (l.length - 1)) };
}

function captionBox(t, toks, cx, cy, o) {
  const { size, weight, maxW, lineH, padX, padY, pop = 1, alpha = 1 } = o;
  const L = layoutWords(toks, size, weight, maxW);
  const bw = Math.max(...L.widths) + padX * 2, bh = L.lines.length * lineH + padY * 2;
  ctx.save();
  ctx.globalAlpha *= alpha;
  ctx.translate(cx, cy); ctx.scale(pop, pop);
  ctx.fillStyle = 'rgba(26,26,26,0.88)';
  ctx.beginPath(); ctx.roundRect(-bw / 2, -bh / 2, bw, bh, 28); ctx.fill();
  L.lines.forEach((line, li) => {
    let x = -L.widths[li] / 2;
    const y = -bh / 2 + padY + lineH * (li + 0.5);
    for (const { tk, w } of line) {
      const st = wordState(t, tk);
      ctx.save();
      ctx.translate(x + w / 2, y); ctx.scale(st.s, st.s);
      txt(tk.text, 0, 0, { size, weight, color: st.color, alpha: st.a });
      ctx.restore();
      x += w + L.space;
    }
  });
  ctx.restore();
}

function bigFigure(t, figs) {
  const f0 = figs[0];
  const m = f0.text.match(/^(\d+)(.*?)[.,…]*$/);
  if (m) {                                            // numeric: count up while spoken
    const v = +m[1], suf = m[2];
    const appear = P(t, f0.start - 0.12, 0.28, E.back);
    if (appear <= 0) return;
    const dur = Math.max(0.6, f0.end - f0.start);
    const k = P(t, f0.start, dur, E.out3);
    const lt = t - f0.start - dur;
    const bump = lt > 0 ? 1 + 0.08 * Math.exp(-lt * 9) : 1;
    ctx.save();
    ctx.translate(CX, 1326); ctx.scale(appear * bump, appear * bump);
    txt(`${Math.round(v * k)}${suf}`, 0, 0, { size: 214, weight: 900, color: C.orange, stroke: 16, shadow: 12 });
    ctx.restore();
    for (let i = 0; i < 4; i++) sparkle([300, 790, 260, 820][i], [1260, 1240, 1420, 1430][i], 26, (lt - i * 0.08) / 0.6);
  } else {                                            // words: "CASI EL / DOBLE"
    const lines = [figs.slice(0, -1), figs.slice(-1)];
    const sizes = [120, 196], ys = [1262, 1420];
    lines.forEach((line, li) => {
      const words = line.map(tk => tk.text.replace(/[.,…]/g, '').toUpperCase());
      const widths = words.map(w => measure(w, sizes[li], 900) + 28);
      let x = CX - widths.reduce((a, b) => a + b, 0) / 2 + 14;
      line.forEach((tk, i) => {
        const k = P(t, tk.start - 0.06, 0.26, E.back);
        if (k > 0) {
          ctx.save();
          ctx.translate(x + widths[i] / 2 - 14, ys[li]); ctx.scale(k, k); ctx.rotate(-3 * DEG);
          txt(words[i], 0, 0, { size: sizes[li], weight: 900, color: C.orange, stroke: 14, shadow: 12 });
          ctx.restore();
        }
        x += widths[i];
      });
    });
  }
}

function drawCaptions(t) {
  const blk = TL.blocks.find(b => t >= b.start && t < b.end);
  if (!blk) return;
  const toks = blk.tokens.map(i => TL.tokens[i]);
  const lt = t - blk.start;
  const pop = lerp(0.82, 1, E.back(clamp(lt / 0.2))), alpha = clamp(lt / 0.08);
  if (!blk.figure) {
    captionBox(t, toks, CX, CAP.y, { ...CAP, pop, alpha });
    return;
  }
  const first = toks.findIndex(x => x.fig);
  const last = toks.length - 1 - [...toks].reverse().findIndex(x => x.fig);
  const pre = toks.slice(0, first), figs = toks.slice(first, last + 1), post = toks.slice(last + 1);
  const small = { size: 44, weight: 600, maxW: 820, lineH: 58, padX: 28, padY: 10, pop, alpha };
  if (pre.length) captionBox(t, pre, CX, 1180, small);
  bigFigure(t, figs);
  if (post.length) captionBox(t, post, CX, 1478, { ...small, alpha: alpha * P(t, post[0].start - 0.2, 0.15) });
}

// ------------------------------------------------------------- overlay
function drawSafeOverlay() {
  ctx.save();
  ctx.fillStyle = 'rgba(255,0,0,0.18)';
  ctx.fillRect(0, 0, W, SAFE.top); ctx.fillRect(0, SAFE.bottom, W, H - SAFE.bottom);
  ctx.fillRect(SAFE.right, SAFE.top, W - SAFE.right, SAFE.bottom - SAFE.top);
  ctx.restore();
}

let showSafe = false;
function render(t) {
  t = Math.min(Math.max(t, 0), DUR - 1e-6);
  ctx.setTransform(1, 0, 0, 1, 0, 0);
  ctx.globalAlpha = 1;
  drawBackground(t);
  ctx.save();
  cameraShake(t);
  drawScenes(t);
  ctx.restore();
  drawWipes(t);
  drawCaptions(t);
  drawTopProgress(t);
  if (showSafe) drawSafeOverlay();
}

buildTiming();
registerScenes();
registerCues();

window.REEL = {
  W, H, DUR, CUES, render,
  toggleSafe() { showSafe = !showSafe; },
};
})();
