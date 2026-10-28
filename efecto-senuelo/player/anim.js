// Motor de animación determinista: render(t) dibuja el cuadro exacto del segundo t.
(function () {
  const W = 1080, H = 1920, CX = 520; // CX centrado en la zona segura (deja 120 px libres a la derecha)
  const C = { bg: '#F5EFE6', ink: '#1A1A1A', or: '#FF5A1F', gr: '#22C55E', gy: '#9CA3AF', gyL: '#D6D9DE', wh: '#FFFFFF', paper: '#FFFBF5' };
  const F = 'APInter';
  const TL = window.TIMELINE;

  // ---------- utilidades ----------
  const clamp = (x, a = 0, b = 1) => Math.max(a, Math.min(b, x));
  const lerp = (a, b, k) => a + (b - a) * k;
  const prog = (t, a, b) => clamp((t - a) / (b - a));
  const eOut = x => 1 - Math.pow(1 - x, 3);
  const eOut5 = x => 1 - Math.pow(1 - x, 5);
  const eInOut = x => (x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
  const eIn = x => x * x * x;
  const eBack = x => { const c1 = 1.70158, c3 = c1 + 1; return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2); };
  const eElastic = x => (x === 0 || x === 1) ? x : Math.pow(2, -10 * x) * Math.sin((x * 10 - 0.75) * (2 * Math.PI) / 3) + 1;
  const eBounce = x => {
    const n1 = 7.5625, d1 = 2.75;
    if (x < 1 / d1) return n1 * x * x;
    if (x < 2 / d1) return n1 * (x -= 1.5 / d1) * x + 0.75;
    if (x < 2.5 / d1) return n1 * (x -= 2.25 / d1) * x + 0.9375;
    return n1 * (x -= 2.625 / d1) * x + 0.984375;
  };
  // entra con pop (0→1 con rebote), sale con desvanecido
  const popIn = (t, a, d = 0.35) => eBack(prog(t, a, a + d));
  const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16)];
  const mix = (h1, h2, k) => { const a = hex(h1), b = hex(h2); return `rgb(${a.map((v, i) => Math.round(lerp(v, b[i], k))).join(',')})`; };
  const rnd = s => { const x = Math.sin(s * 127.1 + 311.7) * 43758.5453; return x - Math.floor(x); };

  let ctx, logoImg;

  function font(size, weight = 900) { return `${weight} ${size}px ${F}`; }
  function text(str, x, y, o = {}) {
    ctx.save();
    ctx.font = font(o.size || 60, o.weight || 900);
    ctx.fillStyle = o.color || C.ink;
    ctx.textAlign = o.align || 'center';
    ctx.textBaseline = o.base || 'middle';
    ctx.letterSpacing = (o.ls || 0) + 'px';
    if (o.maxW) {
      const w = ctx.measureText(str).width;
      if (w > o.maxW) { const k = o.maxW / w; ctx.translate(x, y); ctx.scale(k, k); x = 0; y = 0; }
    }
    if (o.stroke) { ctx.lineWidth = o.strokeW || 10; ctx.strokeStyle = o.stroke; ctx.lineJoin = 'round'; ctx.strokeText(str, x, y); }
    ctx.fillText(str, x, y);
    ctx.restore();
  }
  function measure(str, size, weight = 900, ls = 0) {
    ctx.save(); ctx.font = font(size, weight); ctx.letterSpacing = ls + 'px';
    const w = ctx.measureText(str).width; ctx.restore(); return w;
  }
  function rr(x, y, w, h, r) {
    ctx.beginPath();
    ctx.roundRect(x, y, w, h, r);
  }
  function tf(x, y, s, rot, alpha, fn) {
    if (alpha <= 0.001 || s <= 0.001) return;
    ctx.save();
    ctx.translate(x, y);
    if (rot) ctx.rotate(rot);
    if (s !== 1) ctx.scale(s, s);
    ctx.globalAlpha *= clamp(alpha);
    fn();
    ctx.restore();
  }
  function glow(color, blur) { ctx.shadowColor = color; ctx.shadowBlur = blur; }
  function noGlow() { ctx.shadowColor = 'transparent'; ctx.shadowBlur = 0; }
  function shadowCard() { ctx.shadowColor = 'rgba(26,26,26,0.18)'; ctx.shadowBlur = 30; ctx.shadowOffsetY = 12; }

  // ---------- ilustraciones ----------
  // Vaso de palomitas. (x, yb) = centro inferior. g = 0..1 nivel de gris (señuelo)
  function cup(x, yb, w, h, o = {}) {
    const g = o.gray || 0;
    const stripeA = mix(C.or, C.gy, g), stripeB = mix(C.paper, C.gyL, g);
    const top = yb - h, bw = w * 0.72;
    ctx.save();
    // brillo de selección
    if (o.glow) {
      ctx.save();
      ctx.globalAlpha *= o.glowA ?? 1;
      ctx.strokeStyle = o.glow; ctx.lineWidth = 26; ctx.lineJoin = 'round';
      glow(o.glow, 40);
      ctx.beginPath(); ctx.moveTo(x - w / 2, top); ctx.lineTo(x + w / 2, top); ctx.lineTo(x + bw / 2, yb); ctx.lineTo(x - bw / 2, yb); ctx.closePath(); ctx.stroke();
      ctx.restore();
    }
    // palomitas
    const pr = w * 0.15;
    const pts = [[-0.34, 0.05], [-0.12, -0.02], [0.12, -0.02], [0.34, 0.05], [-0.24, -0.32], [0.0, -0.36], [0.24, -0.32], [-0.1, -0.6], [0.14, -0.58]];
    for (let i = 0; i < pts.length; i++) {
      const [px, py] = pts[i];
      ctx.beginPath(); ctx.arc(x + px * w, top + py * w * 0.55, pr * (0.95 + 0.15 * rnd(i + w)), 0, Math.PI * 2);
      ctx.fillStyle = mix('#FFF4D6', '#EEF0F2', g); ctx.fill();
      ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke();
    }
    // cuerpo con rayas
    ctx.save();
    ctx.beginPath(); ctx.moveTo(x - w / 2, top); ctx.lineTo(x + w / 2, top); ctx.lineTo(x + bw / 2, yb); ctx.lineTo(x - bw / 2, yb); ctx.closePath();
    ctx.fillStyle = stripeB; ctx.fill();
    ctx.clip();
    const n = 5;
    for (let i = 0; i < n; i++) {
      if (i % 2) continue;
      const a0 = -0.5 + i / n, a1 = -0.5 + (i + 1) / n;
      ctx.beginPath();
      ctx.moveTo(x + a0 * w, top); ctx.lineTo(x + a1 * w, top); ctx.lineTo(x + a1 * bw, yb); ctx.lineTo(x + a0 * bw, yb); ctx.closePath();
      ctx.fillStyle = stripeA; ctx.fill();
    }
    ctx.restore();
    ctx.beginPath(); ctx.moveTo(x - w / 2, top); ctx.lineTo(x + w / 2, top); ctx.lineTo(x + bw / 2, yb); ctx.lineTo(x - bw / 2, yb); ctx.closePath();
    ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round'; ctx.stroke();
    // borde superior
    rr(x - w / 2 - 8, top - 6, w + 16, 26, 10); ctx.fillStyle = mix(C.paper, C.gyL, g); ctx.fill(); ctx.lineWidth = 6; ctx.stroke();
    ctx.restore();
  }

  // Vaso de café. (x, yb) = centro inferior
  function coffee(x, yb, w, h, o = {}) {
    const g = o.gray || 0, top = yb - h, bw = w * 0.78;
    ctx.save();
    if (o.glow) {
      ctx.save(); ctx.globalAlpha *= o.glowA ?? 1; ctx.strokeStyle = o.glow; ctx.lineWidth = 24; glow(o.glow, 36);
      ctx.beginPath(); ctx.moveTo(x - w / 2, top); ctx.lineTo(x + w / 2, top); ctx.lineTo(x + bw / 2, yb); ctx.lineTo(x - bw / 2, yb); ctx.closePath(); ctx.stroke(); ctx.restore();
    }
    ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x - w / 2, top); ctx.lineTo(x + w / 2, top); ctx.lineTo(x + bw / 2, yb); ctx.lineTo(x - bw / 2, yb); ctx.closePath();
    ctx.fillStyle = mix(C.paper, C.gyL, g); ctx.fill(); ctx.stroke();
    // faja
    const y0 = top + h * 0.38, y1 = top + h * 0.68;
    const wAt = yy => lerp(w, bw, (yy - top) / h);
    ctx.beginPath(); ctx.moveTo(x - wAt(y0) / 2, y0); ctx.lineTo(x + wAt(y0) / 2, y0); ctx.lineTo(x + wAt(y1) / 2, y1); ctx.lineTo(x - wAt(y1) / 2, y1); ctx.closePath();
    ctx.fillStyle = mix(C.or, C.gy, g); ctx.fill(); ctx.stroke();
    // tapa
    rr(x - w / 2 - 10, top - 26, w + 20, 30, 12); ctx.fillStyle = mix(C.ink, C.gy, g * 0.7); ctx.fill();
    rr(x - w / 2 + 10, top - 44, w - 20, 22, 10); ctx.fill();
    // vapor
    ctx.strokeStyle = mix(C.ink, C.gy, 0.6); ctx.lineWidth = 5; ctx.lineCap = 'round';
    for (let i = -1; i <= 1; i++) {
      ctx.beginPath(); const sx = x + i * w * 0.22;
      ctx.moveTo(sx, top - 56); ctx.bezierCurveTo(sx - 14, top - 76, sx + 14, top - 92, sx, top - 112); ctx.stroke();
    }
    ctx.restore();
  }

  // Ícono de revista (genérica)
  function magazine(x, y, w, h, o = {}) {
    const g = o.gray || 0;
    ctx.save();
    rr(x - w / 2, y - h / 2, w, h, w * 0.06);
    ctx.fillStyle = mix(C.wh, C.gyL, g); ctx.fill();
    ctx.lineWidth = Math.max(4, w * 0.035); ctx.strokeStyle = C.ink; ctx.stroke();
    rr(x - w / 2, y - h / 2, w, h * 0.22, [w * 0.06, w * 0.06, 0, 0]);
    ctx.fillStyle = mix(C.or, C.gy, g); ctx.fill(); ctx.stroke();
    // "titular"
    ctx.fillStyle = C.ink;
    rr(x - w * 0.36, y - h * 0.18, w * 0.72, h * 0.32, w * 0.03); ctx.fillStyle = mix('#FFD9C7', C.gyL, g); ctx.fill(); ctx.stroke();
    ctx.fillStyle = C.ink;
    for (let i = 0; i < 3; i++) { rr(x - w * 0.36, y + h * (0.2 + i * 0.09), w * (i === 2 ? 0.45 : 0.72), h * 0.04, 4); ctx.fill(); }
    ctx.restore();
  }
  // Ícono de pantalla/teléfono
  function phone(x, y, w, h, o = {}) {
    const g = o.gray || 0;
    ctx.save();
    rr(x - w / 2, y - h / 2, w, h, w * 0.16); ctx.fillStyle = C.ink; ctx.fill();
    rr(x - w / 2 + w * 0.09, y - h / 2 + h * 0.08, w * 0.82, h * 0.8, w * 0.06); ctx.fillStyle = mix('#FFE3D6', C.gyL, g); ctx.fill();
    ctx.fillStyle = mix(C.or, C.gy, g);
    for (let i = 0; i < 3; i++) { rr(x - w * 0.3, y - h * 0.3 + i * h * 0.2, w * 0.6, h * 0.1, 5); ctx.fill(); }
    ctx.beginPath(); ctx.arc(x, y + h / 2 - h * 0.06, w * 0.05, 0, Math.PI * 2); ctx.fillStyle = C.wh; ctx.fill();
    ctx.restore();
  }
  // Anzuelo
  function fishHook(x, y, s, color = C.ink) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.strokeStyle = color; ctx.lineWidth = 9; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.arc(0, -40, 9, 0, Math.PI * 2); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0, -31); ctx.lineTo(0, 30); ctx.arc(-24, 30, 24, 0, Math.PI, false); ctx.lineTo(-48, 14); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-48, 10); ctx.lineTo(-58, 26); ctx.moveTo(-48, 10); ctx.lineTo(-38, 24); ctx.stroke();
    ctx.restore();
  }
  function checkBadge(x, y, r, color = C.gr) {
    ctx.save(); ctx.beginPath(); ctx.arc(x, y, r, 0, Math.PI * 2); ctx.fillStyle = color; ctx.fill();
    ctx.lineWidth = r * 0.12; ctx.strokeStyle = C.ink; ctx.stroke();
    ctx.strokeStyle = C.wh; ctx.lineWidth = r * 0.22; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
    ctx.beginPath(); ctx.moveTo(x - r * 0.42, y + r * 0.02); ctx.lineTo(x - r * 0.1, y + r * 0.34); ctx.lineTo(x + r * 0.46, y - r * 0.32); ctx.stroke();
    ctx.restore();
  }
  function star(x, y, r1, r2, n, rot = 0) {
    ctx.beginPath();
    for (let i = 0; i < n * 2; i++) {
      const r = i % 2 ? r2 : r1, a = rot + i * Math.PI / n - Math.PI / 2;
      i ? ctx.lineTo(x + Math.cos(a) * r, y + Math.sin(a) * r) : ctx.moveTo(x + Math.cos(a) * r, y + Math.sin(a) * r);
    }
    ctx.closePath();
  }
  function pill(x, y, label, o = {}) {
    const size = o.size || 34, padX = o.padX ?? size * 0.7, h = o.h || size * 1.7;
    const w = measure(label, size, o.weight || 900, o.ls || 1) + padX * 2;
    ctx.save();
    rr(x - w / 2, y - h / 2, w, h, h / 2); ctx.fillStyle = o.bg || C.ink; ctx.fill();
    if (o.border) { ctx.lineWidth = 5; ctx.strokeStyle = o.border; ctx.stroke(); }
    ctx.restore();
    text(label, x, y + size * 0.04, { size, color: o.color || C.wh, weight: o.weight || 900, ls: o.ls ?? 1 });
    return w;
  }
  function sparkles(x, y, t, a, seed, spread = 160, n = 10, color = C.or) {
    const k = prog(t, a, a + 0.7);
    if (k <= 0 || k >= 1) return;
    for (let i = 0; i < n; i++) {
      const ang = rnd(seed + i) * Math.PI * 2, d = spread * (0.5 + 0.6 * rnd(seed + i * 3)) * eOut(k);
      ctx.save(); ctx.globalAlpha *= 1 - k;
      ctx.fillStyle = i % 3 === 0 ? C.gr : color;
      star(x + Math.cos(ang) * d, y + Math.sin(ang) * d, 16 * (1 - k * 0.5), 6, 4, k * 3);
      ctx.fill(); ctx.restore();
    }
  }
  // Número grande "solo" con conteo
  function bigNumber(t, a, d, from, to, fmt, x, y, size, color = C.ink) {
    const k = eOut(prog(t, a, a + d));
    const v = lerp(from, to, k);
    const landed = prog(t, a + d, a + d + 0.25);
    const s = 1 + 0.12 * Math.sin(landed * Math.PI);
    tf(x, y, s, 0, 1, () => text(fmt(Math.round(v)), 0, 0, { size, color, weight: 900, ls: -4 }));
  }
  function overlay(alpha) {
    if (alpha <= 0) return;
    ctx.save(); ctx.globalAlpha = alpha * 0.94; ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H); ctx.restore();
  }

  // ---------- fondo / UI permanente ----------
  function background(t) {
    ctx.fillStyle = C.bg; ctx.fillRect(0, 0, W, H);
    ctx.save(); ctx.fillStyle = 'rgba(26,26,26,0.06)';
    const off = (t * 12) % 60;
    for (let y = -60; y < H + 60; y += 60) for (let x = -60; x < W + 60; x += 60) {
      ctx.beginPath(); ctx.arc(x + off, y + off, 3, 0, Math.PI * 2); ctx.fill();
    }
    ctx.restore();
  }
  function progressBar(t) {
    ctx.save();
    ctx.fillStyle = 'rgba(26,26,26,0.12)'; ctx.fillRect(0, 0, W, 10);
    ctx.fillStyle = C.or; ctx.fillRect(0, 0, W * clamp(t / TL.duration), 10);
    ctx.restore();
  }
  function logo(t) {
    if (!logoImg) return;
    // esquina superior izquierda, justo debajo de los 250 px de interfaz (el lado derecho queda para los botones)
    const h = 124, w = h * logoImg.width / logoImg.height;
    ctx.save();
    ctx.globalAlpha = 0.96;
    rr(48, 262, w + 24, h + 20, 24); ctx.fillStyle = 'rgba(255,255,255,0.55)'; ctx.fill();
    ctx.drawImage(logoImg, 60, 272, w, h);
    ctx.restore();
  }
  function wipe(t) {
    // barrido diagonal naranja/negro que tapa el corte entre escenas
    for (const b of [8, 20, 30, 42, 52, 57]) {
      const k = prog(t, b - 0.2, b + 0.2);
      if (k <= 0 || k >= 1) continue;
      const x = lerp(-900, W + 300, eInOut(k));
      ctx.save();
      ctx.fillStyle = C.ink;
      ctx.beginPath(); ctx.moveTo(x - 80, 0); ctx.lineTo(x + 520, 0); ctx.lineTo(x + 220, H); ctx.lineTo(x - 380, H); ctx.closePath(); ctx.fill();
      ctx.fillStyle = C.or;
      ctx.beginPath(); ctx.moveTo(x + 520, 0); ctx.lineTo(x + 640, 0); ctx.lineTo(x + 340, H); ctx.lineTo(x + 220, H); ctx.closePath(); ctx.fill();
      ctx.restore();
    }
  }

  // ---------- subtítulos estilo karaoke ----------
  const SUB_Y = 1395, SUB_SIZE = 64, SUB_MAXW = 800;
  function parseSub(str) {
    return str.split(' ').map(w => {
      const key = /\*/.test(w);
      return { w: w.replace(/\*/g, ''), key };
    });
  }
  function subtitles(t) {
    const s = TL.subs.find(b => t >= b[0] && t < b[1]);
    if (!s) return;
    const [a, b, str] = s;
    const words = parseSub(str);
    ctx.save();
    ctx.font = font(SUB_SIZE, 800);
    const space = Math.max(ctx.measureText(' ').width, SUB_SIZE * 0.3);
    words.forEach(o => o.width = ctx.measureText(o.w).width);
    // repartir en líneas
    const lines = [[]]; let lw = 0;
    for (const o of words) {
      const add = (lines[lines.length - 1].length ? space : 0) + o.width;
      if (lw + add > SUB_MAXW - 60 && lines[lines.length - 1].length) { lines.push([o]); lw = o.width; }
      else { lines[lines.length - 1].push(o); lw += add; }
    }
    const lh = SUB_SIZE * 1.22;
    const widths = lines.map(l => l.reduce((s, o, i) => s + o.width + (i ? space : 0), 0));
    const boxW = Math.max(...widths) + 64, boxH = lines.length * lh + 34;
    // tiempos por palabra (proporcional a letras) dentro del 80% inicial del bloque
    const total = words.reduce((s, o) => s + o.w.length + 2, 0);
    let acc = 0;
    const span = (b - a) * 0.8;
    words.forEach(o => { o.t0 = a + span * acc / total; acc += o.w.length + 2; });
    const kIn = a === 0 ? 1 : eBack(prog(t, a, a + 0.18));
    const kOut = prog(t, b - 0.08, b);
    const sc = lerp(0.85, 1, kIn) * (1 - 0.05 * kOut);
    ctx.translate(CX, SUB_Y);
    ctx.scale(sc, sc);
    ctx.globalAlpha = (a === 0 ? 1 : clamp(prog(t, a, a + 0.1))) * (1 - kOut);
    rr(-boxW / 2, -boxH / 2, boxW, boxH, 26);
    ctx.fillStyle = 'rgba(26,26,26,0.80)'; ctx.fill();
    ctx.textBaseline = 'middle'; ctx.textAlign = 'left';
    let wi = 0;
    lines.forEach((l, li) => {
      let x = -widths[li] / 2;
      const y = -boxH / 2 + 17 + lh * (li + 0.5) + 3;
      l.forEach(o => {
        const on = t >= o.t0;
        const kw = prog(t, o.t0, o.t0 + 0.16);
        const pulse = 1 + 0.06 * Math.sin(kw * Math.PI);
        ctx.save();
        ctx.translate(x + o.width / 2, y);
        ctx.scale(pulse, pulse);
        ctx.fillStyle = on ? (o.key ? C.or : C.wh) : 'rgba(255,255,255,0.45)';
        ctx.textAlign = 'center';
        ctx.fillText(o.w, 0, 0);
        ctx.restore();
        x += o.width + space; wi++;
      });
    });
    ctx.restore();
  }

  // ---------- ESCENA 1 + 2: vasos de palomitas ----------
  const CUPS = [
    { x: CX - 285, w: 170, h: 220, name: 'CHICO', price: '$3' },
    { x: CX, w: 210, h: 280, name: 'MEDIANO', price: '$6.50' },
    { x: CX + 285, w: 250, h: 340, name: 'GRANDE', price: '$7' },
  ];
  const CUP_YB = 1130;
  function cupsEntryOffset(u, i) {
    // u: tiempo relativo al loop (u<0 = final del video anterior). Entran de golpe desde abajo.
    const p = prog(u, -0.3 + i * 0.06, 0.32 + i * 0.06);
    return (1 - eBack(p)) * 1000;
  }
  function drawMenuCups(t, u, o = {}) {
    // u = tiempo de entrada (para el loop); o.gray, o.blink, o.bigGlow
    CUPS.forEach((c, i) => {
      const dy = cupsEntryOffset(u, i);
      const land = prog(u, 0.08 + i * 0.06, 0.38 + i * 0.06);
      const squash = 1 - 0.12 * Math.sin(land * Math.PI) * (1 - land);
      const opts = {};
      if (i === 1) {
        opts.gray = o.gray || 0;
        if (o.blink) { opts.glow = C.or; opts.glowA = o.blink; }
      }
      if (i === 2 && o.bigGlow) { opts.glow = C.gr; opts.glowA = o.bigGlow; }
      const pulse = i === 2 && o.bigPulse ? 1 + 0.07 * o.bigPulse : 1;
      ctx.save();
      ctx.translate(c.x, CUP_YB + dy);
      ctx.scale(pulse * (2 - squash), squash * pulse);
      cup(0, 0, c.w, c.h, opts);
      ctx.restore();
      const la = clamp(prog(u, 0.25 + i * 0.06, 0.5 + i * 0.06)) * (o.labelA ?? 1);
      tf(c.x, CUP_YB + 46 + dy * 1.1, 1, 0, la, () => {
        text(c.name, 0, 0, { size: 30, weight: 800, color: i === 1 ? mix(C.ink, C.gy, o.gray || 0) : C.ink, ls: 2 });
        text(c.price, 0, 58, { size: 58, weight: 900, color: i === 1 ? mix(C.ink, C.gy, o.gray || 0) : (o.bigGlow && i === 2 ? C.gr : C.ink) });
      });
    });
  }

  function sceneHook(t) {
    const u = t;
    // cartel "MENÚ"
    const mk = popIn(t, 0.2, 0.4);
    tf(CX, 520, mk, 0, mk, () => {
      pill(0, 0, '★  MENÚ  ★', { size: 46, bg: C.ink, h: 92, ls: 6 });
    });
    const blink = t > 0.6 ? 0.5 + 0.5 * Math.sign(Math.sin((t - 0.6) * Math.PI * 4)) : 0;
    drawMenuCups(t, u, { blink: blink * clamp(prog(t, 0.6, 0.7)) });
    // signo de interrogación sobre el vaso mediano
    const q = popIn(t, 0.7, 0.4);
    const bob = Math.sin(t * 7) * 10;
    tf(CX, 700 + bob, q, Math.sin(t * 5) * 0.12, q, () => {
      ctx.beginPath(); ctx.arc(0, 0, 66, 0, Math.PI * 2); ctx.fillStyle = C.or; ctx.fill();
      ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.stroke();
      ctx.beginPath(); ctx.moveTo(-14, 58); ctx.lineTo(0, 92); ctx.lineTo(16, 58); ctx.fillStyle = C.or; ctx.fill();
      text('?', 0, 4, { size: 100, color: C.wh });
    });
  }

  function sceneGiro(t) {
    // 3.0–5.6: vasos; el mediano se vuelve gris + etiqueta SEÑUELO con anzuelo
    const out = eIn(prog(t, 5.5, 5.85));
    if (out < 1) {
      ctx.save();
      ctx.translate(0, out * 900); ctx.globalAlpha *= 1 - out;
      const gray = eOut(prog(t, 3.15, 3.55));
      const big = eOut(prog(t, 4.25, 4.55));
      drawMenuCups(t, 10, { gray, bigGlow: big, bigPulse: Math.sin(prog(t, 4.25, 4.6) * Math.PI) });
      // "?" se va
      const q = 1 - prog(t, 3.0, 3.2);
      tf(CX, 700, q, 0, q, () => { ctx.beginPath(); ctx.arc(0, 0, 66, 0, Math.PI * 2); ctx.fillStyle = C.or; ctx.fill(); text('?', 0, 4, { size: 100, color: C.wh }); });
      // hilo + etiqueta SEÑUELO
      const drop = eBack(prog(t, 3.3, 3.75));
      const swing = Math.sin((t - 3.3) * 6) * 0.22 * Math.exp(-(t - 3.3) * 1.3) * (t > 3.3);
      const anchorY = 430;
      const len = lerp(0, 300, drop);
      if (len > 1) {
        ctx.save(); ctx.translate(CX, anchorY); ctx.rotate(swing);
        ctx.strokeStyle = C.ink; ctx.lineWidth = 4; ctx.beginPath(); ctx.moveTo(0, -200); ctx.lineTo(0, len); ctx.stroke();
        rr(-150, len, 300, 92, 18); ctx.fillStyle = C.gy; ctx.fill(); ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
        text('SEÑUELO', 0, len + 48, { size: 50, color: C.ink, ls: 3 });
        fishHook(0, len + 150, 0.9);
        ctx.restore();
      }
      // "+$" sobre el vaso grande
      const m = popIn(t, 4.3, 0.35);
      const rise = prog(t, 4.3, 5.5) * 40;
      tf(CUPS[2].x + 10, 650 - rise, m, 0, m, () => {
        pill(0, 0, '+ $', { size: 56, bg: C.gr, color: C.wh, h: 96, padX: 34, border: C.ink });
        ctx.save(); ctx.fillStyle = C.gr; ctx.strokeStyle = C.ink; ctx.lineWidth = 5;
        ctx.beginPath(); ctx.moveTo(100, 10); ctx.lineTo(130, -40); ctx.lineTo(160, 10); ctx.closePath(); ctx.fill(); ctx.stroke();
        ctx.fillRect(118, 8, 24, 40); ctx.strokeRect(118, 8, 24, 40); ctx.restore();
      });
      ctx.restore();
    }
    // 5.5–8: título
    const sl = eOut(prog(t, 5.55, 5.9));
    const slUp = eInOut(prog(t, 6.7, 7.0));
    tf(CX, lerp(780, 620, slUp), lerp(0.7, 1, sl) * lerp(1, 0.75, slUp), 0, sl, () => {
      const dots = '.'.repeat(1 + Math.floor(clamp((t - 5.6) * 4, 0, 2)));
      text('SE LLAMA' + dots, 0, 0, { size: 84, weight: 900, color: C.ink, ls: 4 });
    });
    const k1 = eBack(prog(t, 6.75, 7.05));
    tf(CX, 790, lerp(1.6, 1, k1), 0, prog(t, 6.75, 6.85), () => {
      text('EL EFECTO', 0, 0, { size: 104, weight: 900, color: C.ink, ls: 2 });
    });
    const k2 = eBack(prog(t, 6.85, 7.2));
    tf(CX, 960, lerp(2.0, 1, k2), lerp(-0.12, -0.03, k2), prog(t, 6.85, 6.95), () => {
      const size = 160;
      text('SEÑUELO', 6, 8, { size, color: C.ink, maxW: 820, ls: -2 });
      text('SEÑUELO', 0, 0, { size, color: C.or, maxW: 820, ls: -2 });
      // brillo
      const sh = prog(t, 7.25, 7.75);
      if (sh > 0 && sh < 1) {
        ctx.save();
        ctx.font = font(size, 900); ctx.letterSpacing = '-2px'; ctx.textAlign = 'center'; ctx.textBaseline = 'middle';
        const mw = ctx.measureText('SEÑUELO').width;
        const sc = Math.min(1, 820 / mw); ctx.scale(sc, sc);
        const gx = lerp(-mw, mw, sh);
        const gr = ctx.createLinearGradient(gx - 120, 0, gx + 120, 0);
        gr.addColorStop(0, 'rgba(255,255,255,0)'); gr.addColorStop(0.5, 'rgba(255,255,255,0.95)'); gr.addColorStop(1, 'rgba(255,255,255,0)');
        ctx.fillStyle = gr; ctx.fillText('SEÑUELO', 0, 0);
        ctx.restore();
      }
    });
    // subrayado + anzuelo
    const ul = eOut(prog(t, 7.0, 7.35));
    ctx.save(); ctx.fillStyle = C.ink; rr(CX - 360 * ul, 1065, 720 * ul, 16, 8); ctx.fill(); ctx.restore();
    const hk = popIn(t, 7.1, 0.4);
    tf(CX, 1150, hk, Math.sin(t * 4) * 0.15, hk, () => fishHook(30, 40, 1.3, C.or));
    sparkles(CX, 960, t, 7.25, 77, 420, 14);
  }

  // ---------- ESCENA 3/4: tarjetas de precio ----------
  const CARD_W = 258, CARD_GAP = 22;
  const cardX = i => CX + (i - 1) * (CARD_W + CARD_GAP);
  const PLANS = [
    { l1: 'SOLO', l2: 'DIGITAL', price: 59 },
    { l1: 'SOLO', l2: 'IMPRESA', price: 125 },
    { l1: 'IMPRESA', l2: '+ DIGITAL', price: 125 },
  ];
  // c: 0 = tarjeta completa, 1 = compacta (arriba, para el gráfico de barras)
  function card(i, x, c, o = {}) {
    const p = PLANS[i];
    const h = lerp(400, 230, c), y = lerp(640, 450, c);
    const g = o.gray || 0;
    ctx.save();
    shadowCard();
    rr(x - CARD_W / 2, y, CARD_W, h, 28);
    ctx.fillStyle = mix(C.wh, '#ECEDEF', g); ctx.fill();
    noGlow();
    ctx.lineWidth = 6; ctx.strokeStyle = o.border || mix(C.ink, C.gy, g); ctx.stroke();
    if (o.borderGlow) { ctx.save(); glow(o.borderGlow, 40); ctx.lineWidth = 12; ctx.strokeStyle = o.borderGlow; ctx.globalAlpha *= o.borderGlowA ?? 1; ctx.stroke(); ctx.restore(); }
    // íconos
    const ia = 1 - c;
    if (ia > 0.01) {
      ctx.save(); ctx.globalAlpha *= ia;
      const iy = y + 120;
      if (i === 0) phone(x, iy, 90, 150, { gray: g });
      if (i === 1) magazine(x, iy, 110, 150, { gray: g });
      if (i === 2) { magazine(x - 42, iy, 100, 136, { gray: g }); phone(x + 56, iy + 20, 70, 118, { gray: g }); }
      ctx.restore();
    }
    const ty = lerp(y + 235, y + 52, c);
    text(p.l1, x, ty, { size: 34, weight: 900, color: mix(C.ink, C.gy, g), ls: 1, maxW: CARD_W - 30 });
    text(p.l2, x, ty + 40, { size: 34, weight: 900, color: mix(C.ink, C.gy, g), ls: 1, maxW: CARD_W - 30 });
    if (o.priceA) {
      tf(x, lerp(y + 345, y + 168, c), 1, 0, o.priceA, () => text('$' + p.price, 0, 0, { size: 76, weight: 900, color: o.priceColor || mix(C.or, C.gy, g), ls: -2 }));
    }
    ctx.restore();
  }

  function sceneExperimento(t) {
    // revista grande → encabezado
    const mIn = eBack(prog(t, 8.1, 8.55));
    const toHead = eInOut(prog(t, 9.45, 9.95));
    const mx = lerp(CX, CX - 310, toHead), my = lerp(820, 530, toHead), ms = lerp(1, 0.32, toHead);
    tf(mx, my, ms, lerp(-0.4, -0.05, mIn) * (1 - toHead), 1, () => {
      ctx.save(); ctx.scale(Math.max(0.02, mIn), 1);
      magazine(0, 0, 330, 440, {});
      text('REVISTA', 0, -188, { size: 54, color: C.wh, ls: 4 });
      ctx.restore();
    });
    const sIn = popIn(t, 8.95, 0.35);
    tf(lerp(CX, CX + 50, toHead), lerp(1140, 530, toHead), sIn * lerp(1, 0.9, toHead), 0, sIn, () => {
      ctx.save();
      const w3 = measure('3', 96), ws = measure('SUSCRIPCIONES', 64, 900, 1), gap = 22, tot = w3 + gap + ws;
      text('3', -tot / 2 + w3 / 2, 0, { size: 96, color: C.or });
      text('SUSCRIPCIONES', -tot / 2 + w3 + gap + ws / 2, 4, { size: 64, color: C.ink, ls: 1 });
      ctx.restore();
    });
    // tarjetas
    const big = [
      { a: 11.2, i: 0, to: 59 },
      { a: 13.9, i: 1, to: 125 },
      { a: 17.0, i: 2, to: 125 },
    ];
    const cin = [10.0, 12.6, 15.3];
    const hl = eOut(prog(t, 18.1, 18.4));
    const zoom = 1 + 0.06 * eInOut(prog(t, 18.2, 19.5));
    ctx.save();
    ctx.translate(CX + 140, 900); ctx.scale(zoom, zoom); ctx.translate(-(CX + 140), -900);
    cin.forEach((a, i) => {
      const k = popIn(t, a, 0.4);
      const flyEnd = big[i].a + (i === 2 ? 1.05 : 1.25);
      const priceA = t >= flyEnd ? 1 : 0;
      const isHl = i > 0 ? hl : 0;
      tf(cardX(i), 840, k, 0, clamp(k), () => {
        ctx.translate(-cardX(i), -840);
        card(i, cardX(i), 0, { priceA, borderGlow: isHl ? C.or : null, borderGlowA: isHl, border: isHl > 0.5 ? C.or : null, priceColor: i > 0 && hl > 0 ? C.or : null });
      });
    });
    // "¿?" entre los dos $125
    const q = popIn(t, 18.15, 0.45);
    if (q > 0) {
      const qx = (cardX(1) + cardX(2)) / 2, qy = 1150;
      ctx.save(); ctx.globalAlpha *= clamp(q);
      ctx.strokeStyle = C.or; ctx.lineWidth = 7; ctx.lineCap = 'round';
      const ext = eOut(prog(t, 18.15, 18.5));
      ctx.beginPath(); ctx.moveTo(cardX(1), 1060); ctx.lineTo(cardX(1), lerp(1060, 1150, ext)); ctx.lineTo(lerp(cardX(1), qx - 70, ext), lerp(1060, 1150, ext)); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(cardX(2), 1060); ctx.lineTo(cardX(2), lerp(1060, 1150, ext)); ctx.lineTo(lerp(cardX(2), qx + 70, ext), lerp(1060, 1150, ext)); ctx.stroke();
      ctx.restore();
      tf(qx, qy, q, Math.sin(t * 6) * 0.1, clamp(q), () => {
        ctx.beginPath(); ctx.arc(0, 0, 66, 0, Math.PI * 2); ctx.fillStyle = C.or; ctx.fill(); ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
        text('¿?', 0, 4, { size: 70, color: C.wh });
      });
      tf(qx, 1236, 1, 0, prog(t, 18.6, 18.9), () => text('= MISMO PRECIO', 0, 0, { size: 36, color: C.ink, ls: 2 }));
    }
    ctx.restore();
    // cifras grandes, solas, con conteo
    big.forEach(b => {
      const dur = b.i === 2 ? 1.05 : 1.25;
      const end = b.a + dur;
      if (t < b.a || t > end) return;
      const ov = prog(t, b.a, b.a + 0.12) * (1 - prog(t, end - 0.28, end));
      overlay(ov);
      const fly = eInOut(prog(t, end - 0.28, end));
      const tx = cardX(b.i), ty = 640 + 345;
      const x = lerp(CX, tx, fly), y = lerp(900, ty, fly), size = lerp(300, 76, fly);
      bigNumber(t, b.a + 0.03, 0.6, 0, b.to, v => '$' + v, x, y, size, fly > 0.5 ? C.or : C.ink);
    });
  }

  // gráfico de barras
  const BAR_BASE = 1255, BAR_MAX = 440;
  function bar(x, pct, color, label, labelColor, a = 1) {
    const h = BAR_MAX * pct / 100;
    ctx.save(); ctx.globalAlpha *= a;
    ctx.fillStyle = 'rgba(26,26,26,0.08)'; rr(x - 80, BAR_BASE - BAR_MAX, 160, BAR_MAX, 18); ctx.fill();
    if (h > 1) { ctx.fillStyle = color; rr(x - 80, BAR_BASE - h, 160, h, Math.min(18, h / 2)); ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke(); }
    ctx.fillStyle = C.ink; ctx.fillRect(x - 100, BAR_BASE, 200, 6);
    text(label, x, BAR_BASE - h - 44, { size: 54, color: labelColor || C.ink });
    ctx.restore();
  }
  function sceneResultado(t) {
    const comp = eInOut(prog(t, 20.0, 20.4));
    const gray1 = eOut(prog(t, 20.3, 20.6));
    // poof de la tarjeta "solo impresa"
    const poof = prog(t, 25.85, 26.3);
    const shake = t > 24.6 && t < 25.85 ? Math.sin(t * 60) * 6 * prog(t, 24.6, 25.4) : 0;
    const regroup = eInOut(prog(t, 26.1, 26.6));
    const xs = [lerp(cardX(0), CX - 165, regroup), cardX(1), lerp(cardX(2), CX + 165, regroup)];
    // porcentajes
    const pDig = lerp(0, 16, eOut(prog(t, 20.7, 21.1)));
    const grow = eOut(prog(t, 23.0, 23.8));
    const fall = eBounce(prog(t, 28.0, 28.7));
    let pBun = lerp(0, 84, grow);
    if (t >= 28.0) pBun = lerp(84, 32, fall);
    const pDig2 = t >= 28.0 ? lerp(16, 68, eOut(prog(t, 28.0, 28.6))) : pDig;
    const punch = 1 + 0.05 * eInOut(prog(t, 29.0, 29.9));
    ctx.save();
    ctx.translate(CX, 860); ctx.scale(punch, punch); ctx.translate(-CX, -860);
    // tarjetas compactas
    [0, 1, 2].forEach(i => {
      if (i === 1 && poof >= 1) return;
      const a = i === 1 ? 1 - poof : 1;
      const s = i === 1 ? 1 + 0.25 * eOut(poof) : 1;
      const isWin = i === 2 && t >= 23.0;
      const win = isWin ? (t >= 28.0 ? 1 - prog(t, 28.0, 28.4) : eOut(prog(t, 23.0, 23.3))) : 0;
      tf(xs[i] + (i === 1 ? shake : 0), 560, s, 0, a, () => {
        ctx.translate(-xs[i], -560);
        card(i, xs[i], comp, { priceA: 1, gray: i === 1 ? gray1 : 0, borderGlow: win > 0 ? C.gr : null, borderGlowA: win, border: win > 0.5 ? C.gr : null, priceColor: i === 1 ? mix(C.or, C.gy, gray1) : C.or });
      });
      // barras
      const ba = clamp(prog(t, 20.2, 20.5));
      if (i === 0) bar(xs[0], pDig2, C.ink, Math.round(pDig2) + '%', C.ink, ba);
      if (i === 1) bar(xs[1] + shake, 0, C.gy, '0%', C.gy, ba * (1 - poof));
      if (i === 2) {
        const col = t >= 28.0 ? mix(C.gr, C.or, prog(t, 28.0, 28.4)) : C.gr;
        bar(xs[2], pBun, col, Math.round(pBun) + '%', t >= 28.0 ? C.or : C.gr, ba);
      }
    });
    // sello 0%
    const st = popIn(t, 20.4, 0.35) * (1 - poof);
    tf(cardX(1) + shake, 1000, lerp(2, 1, clamp(st)), -0.2, clamp(st), () => {
      rr(-120, -50, 240, 100, 16); ctx.lineWidth = 9; ctx.strokeStyle = C.ink; ctx.stroke();
      text('NADIE', 0, 4, { size: 54, color: C.ink, ls: 3 });
    });
    // partículas del poof
    if (poof > 0 && poof < 1) {
      for (let i = 0; i < 16; i++) {
        const ang = (i / 16) * Math.PI * 2 + rnd(i) * 0.4, d = 60 + 230 * eOut(poof) * (0.6 + 0.5 * rnd(i + 9));
        ctx.save(); ctx.globalAlpha *= 1 - poof;
        ctx.beginPath(); ctx.arc(cardX(1) + Math.cos(ang) * d, 800 + Math.sin(ang) * d, 40 * (1 - poof) + 8, 0, Math.PI * 2);
        ctx.fillStyle = i % 2 ? C.gy : C.gyL; ctx.fill(); ctx.restore();
      }
      text('POOF!', cardX(1), 800, { size: lerp(60, 120, eOut(poof)), color: C.ink });
    }
    ctx.restore();
    // cifras grandes: 84% (conteo) y 32% (caída)
    if (t >= 21.6 && t < 22.85) {
      overlay(prog(t, 21.6, 21.72) * (1 - prog(t, 22.6, 22.85)));
      bigNumber(t, 21.65, 0.6, 0, 84, v => v + '%', CX, 880, 330, C.gr);
      tf(CX, 1100, 1, 0, prog(t, 21.7, 21.9) * (1 - prog(t, 22.6, 22.85)), () => text('ELIGIÓ EL PAQUETE', 0, 0, { size: 44, color: C.ink, ls: 3 }));
    }
    if (t >= 27.0 && t < 28.0) {
      overlay(prog(t, 27.0, 27.12) * (1 - prog(t, 27.78, 28.0)));
      const k = prog(t, 27.05, 27.7);
      const drop = eBounce(k);
      ctx.save(); ctx.globalAlpha *= 1 - prog(t, 27.78, 28.0);
      bigNumber(t, 27.05, 0.6, 84, 32, v => v + '%', CX, lerp(760, 900, drop), 330, mix(C.gr, C.or, k));
      // flecha de caída
      ctx.fillStyle = C.or;
      const ay = lerp(1010, 1150, drop);
      ctx.beginPath(); ctx.moveTo(CX, ay + 60); ctx.lineTo(CX - 60, ay); ctx.lineTo(CX + 60, ay); ctx.closePath(); ctx.fill();
      ctx.fillRect(CX - 18, ay - 80, 36, 84);
      ctx.restore();
    }
  }

  // ---------- ESCENA 5: cerebro + balanza ----------
  function brain(x, y, s) {
    ctx.save(); ctx.translate(x, y); ctx.scale(s, s);
    ctx.lineWidth = 9; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
    ctx.fillStyle = '#FFD3C2';
    const lobes = [[-70, -40, 80], [0, -70, 85], [72, -40, 80], [-80, 30, 72], [80, 30, 72], [0, 30, 80]];
    ctx.beginPath(); lobes.forEach(([lx, ly, r]) => { ctx.moveTo(lx + r, ly); ctx.arc(lx, ly, r, 0, Math.PI * 2); });
    ctx.lineWidth = 18; ctx.stroke(); ctx.fill(); ctx.lineWidth = 9;
    ctx.globalAlpha *= 0.55;
    [[-60, -10, 50], [60, -10, 50]].forEach(([lx, ly, r]) => { ctx.beginPath(); ctx.arc(lx, ly, r, Math.PI * 1.1, Math.PI * 1.9); ctx.stroke(); });
    ctx.globalAlpha /= 0.55;
    ctx.beginPath(); ctx.moveTo(0, -140); ctx.bezierCurveTo(-20, -60, 20, 0, 0, 100); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(-110, -20); ctx.bezierCurveTo(-70, -10, -60, 30, -30, 40); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(110, -20); ctx.bezierCurveTo(70, -10, 60, 30, 30, 40); ctx.stroke();
    ctx.restore();
  }
  function priceTag(x, y, s, rot, label, o = {}) {
    tf(x, y, s, rot, 1, () => {
      ctx.beginPath();
      ctx.moveTo(-130, -60); ctx.lineTo(90, -60); ctx.lineTo(140, 0); ctx.lineTo(90, 60); ctx.lineTo(-130, 60); ctx.closePath();
      ctx.fillStyle = o.bg || C.or; ctx.fill(); ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.stroke();
      ctx.beginPath(); ctx.arc(95, 0, 11, 0, Math.PI * 2); ctx.fillStyle = C.bg; ctx.fill(); ctx.stroke();
      text(label, -22, 4, { size: 70, color: C.wh });
    });
  }
  function scaleItem(x, y, i, o = {}) {
    // mini tarjeta sobre el plato
    const g = o.gray || 0;
    ctx.save();
    if (o.glow) { glow(C.gr, 50 * o.glow); }
    rr(x - 115, y - 150, 230, 150, 22); ctx.fillStyle = mix(C.wh, '#ECEDEF', g); ctx.fill();
    noGlow();
    ctx.lineWidth = o.glow ? lerp(6, 12, o.glow) : 6; ctx.strokeStyle = o.glow ? mix(C.ink, C.gr, o.glow) : mix(C.ink, C.gy, g); ctx.stroke();
    const p = PLANS[i];
    text(i === 1 ? 'IMPRESA' : 'IMPRESA + DIG.', x, y - 112, { size: 28, color: mix(C.ink, C.gy, g), maxW: 210 });
    text('$125', x, y - 54, { size: 64, color: o.glow ? mix(C.or, C.gr, o.glow) : mix(C.or, C.gy, g) });
    ctx.restore();
  }
  function scenePorque(t) {
    const toScale = eInOut(prog(t, 33.0, 33.5));
    // cerebro: grande al centro → se encoge y corona la balanza
    const bIn = popIn(t, 30.0, 0.45);
    const bx = CX, by = lerp(820, 560, toScale), bs = lerp(1.25, 0.5, toScale) * bIn;
    const wob = Math.sin(t * 3) * 0.04 * (1 - toScale);
    // signos de pregunta alrededor
    const qa = clamp(prog(t, 30.3, 30.6)) * (1 - toScale);
    for (let i = 0; i < 3; i++) {
      const ang = -2.3 + i * 0.95 + Math.sin(t * 2 + i) * 0.1;
      tf(bx + Math.cos(ang) * 280, by + Math.sin(ang) * 230 + Math.sin(t * 4 + i) * 10, popIn(t, 30.3 + i * 0.12, 0.3), 0, qa, () => text('?', 0, 0, { size: 96, color: C.or, stroke: C.ink, strokeW: 8 }));
    }
    // etiqueta de precio con dígitos que no paran ("¿cuánto vale?")
    const tagA = popIn(t, 31.5, 0.4) * (1 - toScale);
    if (tagA > 0.01) {
      const digits = t < 33 ? '$' + (10 + Math.floor(rnd(Math.floor(t * 12)) * 190)) : '$?';
      priceTag(CX + 40, 1130, clamp(tagA) * 0.9, Math.sin(t * 5) * 0.08, digits);
    }
    // balanza
    const sIn = eOut(prog(t, 33.0, 33.5));
    const PIV = { x: CX, y: 720 };
    let ang = 0;
    if (t > 34.4 && t < 36.0) ang = Math.sin((t - 34.4) * 9) * 0.07 * Math.exp(-(t - 34.4) * 1.5);
    const tilt = eElastic(prog(t, 37.7, 38.9));
    ang += 0.2 * tilt; // se inclina hacia el paquete (derecha)
    if (t > 36.1 && t < 37.6) ang += -0.05 * Math.sin(prog(t, 36.1, 36.6) * Math.PI);
    const push = 1 + 0.08 * eInOut(prog(t, 40.3, 41.7));
    ctx.save();
    ctx.translate(CX + 60, 900); ctx.scale(push, push); ctx.translate(-(CX + 60), -900);
    ctx.globalAlpha *= sIn;
    ctx.translate(0, (1 - sIn) * 200);
    // poste y base
    ctx.fillStyle = C.ink;
    rr(PIV.x - 12, PIV.y, 24, 480, 10); ctx.fill();
    rr(PIV.x - 150, 1200, 300, 44, 20); ctx.fill();
    const L = 270;
    const ends = [-1, 1].map(sg => ({ x: PIV.x + sg * L * Math.cos(ang), y: PIV.y + sg * L * Math.sin(ang) }));
    // cuerdas y platos
    ends.forEach((e, idx) => {
      const panY = e.y + 250;
      ctx.strokeStyle = C.ink; ctx.lineWidth = 5;
      ctx.beginPath(); ctx.moveTo(e.x, e.y); ctx.lineTo(e.x - 105, panY); ctx.moveTo(e.x, e.y); ctx.lineTo(e.x + 105, panY); ctx.stroke();
      ctx.beginPath(); ctx.moveTo(e.x - 125, panY); ctx.quadraticCurveTo(e.x, panY + 85, e.x + 125, panY); ctx.closePath();
      ctx.fillStyle = idx === 1 && t > 39.2 ? mix(C.or, C.gr, prog(t, 39.2, 39.5)) : C.or; ctx.fill(); ctx.lineWidth = 7; ctx.stroke();
      // objetos
      if (idx === 0) {
        const d = eBounce(prog(t, 36.0, 36.5));
        if (t >= 36.0) scaleItem(e.x, lerp(panY - 500, panY, d), 1, { gray: 1 });
        const lab = popIn(t, 36.3, 0.3);
        if (t >= 36.3) tf(e.x, panY + 120, clamp(lab), 0, clamp(lab), () => pill(0, 0, 'SEÑUELO', { size: 32, bg: C.gy, color: C.ink, border: C.ink }));
      } else {
        const d = eBounce(prog(t, 37.6, 38.1));
        const gl = eOut(prog(t, 39.2, 39.5));
        if (t >= 37.6) scaleItem(e.x, lerp(panY - 500, panY, d), 2, { glow: gl });
      }
    });
    // viga
    ctx.save(); ctx.translate(PIV.x, PIV.y); ctx.rotate(ang);
    ctx.fillStyle = C.ink; rr(-L - 10, -12, 2 * L + 20, 24, 12); ctx.fill();
    ctx.restore();
    ctx.beginPath(); ctx.arc(PIV.x, PIV.y, 24, 0, Math.PI * 2); ctx.fillStyle = C.or; ctx.fill(); ctx.lineWidth = 6; ctx.strokeStyle = C.ink; ctx.stroke();
    // "VS"
    const vs = popIn(t, 34.4, 0.35) * (1 - prog(t, 37.6, 37.9));
    tf(PIV.x, PIV.y + 230, clamp(vs), 0, clamp(vs), () => {
      ctx.beginPath(); ctx.arc(0, 0, 60, 0, Math.PI * 2); ctx.fillStyle = C.ink; ctx.fill();
      text('VS', 0, 3, { size: 52, color: C.wh });
    });
    // ¡GANGA!
    const gg = popIn(t, 39.2, 0.45);
    if (t >= 39.2) {
      const e = ends[1];
      tf(e.x - 70, e.y - 330, clamp(gg) * (1 + 0.04 * Math.sin(t * 10)), -0.12, clamp(gg), () => {
        ctx.fillStyle = C.gr; star(0, 0, 135, 108, 16, t * 0.6); ctx.fill(); ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.stroke();
        text('¡GANGA!', 0, 4, { size: 54, color: C.wh, stroke: C.ink, strokeW: 8 });
      });
      sparkles(e.x, e.y + 100, t, 39.25, 31, 260, 14, C.gr);
    }
    ctx.restore();
    // cerebro (encima)
    if (bs > 0.01) tf(bx, by, bs, wob, 1, () => brain(0, 0, 1));
  }

  // ---------- ESCENA 6: carrusel de ejemplos ----------
  function legend(a) {
    tf(CX, 470, 1, 0, a, () => {
      const w1 = measure('SEÑUELO', 30, 900, 1) + 46, w2 = measure('LA QUE QUIEREN QUE COMPRES', 30, 900, 1) + 46;
      const gap = 18, tot = w1 + w2 + gap;
      pill(-tot / 2 + w1 / 2, 0, 'SEÑUELO', { size: 30, bg: C.gy, color: C.ink, padX: 23, h: 60 });
      pill(-tot / 2 + w1 + gap + w2 / 2, 0, 'LA QUE QUIEREN QUE COMPRES', { size: 30, bg: C.gr, color: C.wh, padX: 23, h: 60 });
    });
  }
  function panel(x, title, fn) {
    const pw = 800, ph = 680, py = 545;
    ctx.save();
    shadowCard(); rr(x - pw / 2, py, pw, ph, 40); ctx.fillStyle = C.wh; ctx.fill(); noGlow();
    ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.stroke();
    rr(x - pw / 2, py, pw, 96, [40, 40, 0, 0]); ctx.fillStyle = C.ink; ctx.fill();
    for (let i = 0; i < 3; i++) { ctx.beginPath(); ctx.arc(x - pw / 2 + 50 + i * 36, py + 48, 11, 0, Math.PI * 2); ctx.fillStyle = [C.or, C.gy, C.gr][i]; ctx.fill(); }
    text(title, x + 40, py + 50, { size: 40, color: C.wh, ls: 4 });
    fn(py);
    ctx.restore();
  }
  function markLabels(x, y, kind, k) {
    if (k <= 0) return;
    tf(x, y, eBack(clamp(k)), 0, clamp(k * 3), () => {
      if (kind === 'decoy') pill(0, 0, 'SEÑUELO', { size: 26, bg: C.gy, color: C.ink, padX: 16, h: 50 });
      else checkBadge(0, 0, 34);
    });
  }
  function sceneDonde(t) {
    legend(clamp(prog(t, 42.1, 42.4)));
    const pos = eInOut(prog(t, 46.2, 46.6)) + eInOut(prog(t, 49.0, 49.4));
    const exitK = prog(t, 51.8, 52);
    const off = i => CX + (i - pos) * 1150;
    // 1) palomitas
    if (Math.abs(0 - pos) < 1.2) panel(off(0), 'CINE', py => {
      const x0 = off(0);
      const items = [{ dx: -250, w: 130, h: 170, p: '$3' }, { dx: 0, w: 160, h: 220, p: '$6.50' }, { dx: 250, w: 190, h: 270, p: '$7' }];
      items.forEach((it, i) => {
        const k = popIn(t, 42.2 + i * 0.1, 0.35);
        const g = i === 1 ? eOut(prog(t, 43.6, 43.9)) : 0;
        const gl = i === 2 ? eOut(prog(t, 44.9, 45.2)) : 0;
        tf(x0 + it.dx, py + 470, clamp(k), 0, clamp(k), () => {
          cup(0, 0, it.w, it.h, { gray: g, glow: gl ? C.gr : null, glowA: gl });
          text(it.p, 0, 70, { size: 58, color: gl > 0.5 ? C.gr : mix(C.ink, C.gy, g) });
        });
        if (i === 1) markLabels(x0 + it.dx, py + 620, 'decoy', prog(t, 43.6, 43.95));
        if (i === 2) markLabels(x0 + it.dx + 100, py + 170, 'target', prog(t, 44.9, 45.25));
      });
    });
    // 2) streaming
    if (Math.abs(1 - pos) < 1.2) panel(off(1), 'STREAMING', py => {
      const x0 = off(1);
      // pantalla
      ctx.fillStyle = C.ink; rr(x0 - 360, py + 130, 720, 440, 26); ctx.fill();
      rr(x0 - 60, py + 570, 120, 30, 6); ctx.fill(); rr(x0 - 140, py + 596, 280, 20, 10); ctx.fill();
      const plans = [{ n: 'BÁSICO', p: '$8', f: 1 }, { n: 'ESTÁNDAR', p: '$15', f: 2 }, { n: 'PREMIUM', p: '$17', f: 4 }];
      plans.forEach((pl, i) => {
        const k = popIn(t, 46.4 + i * 0.1, 0.35);
        const g = i === 1 ? eOut(prog(t, 47.0, 47.3)) : 0;
        const gl = i === 2 ? eOut(prog(t, 47.6, 47.9)) : 0;
        const x = x0 + (i - 1) * 228;
        tf(x, py + 350, clamp(k) * (1 + 0.06 * gl), 0, clamp(k), () => {
          ctx.save();
          if (gl) glow(C.gr, 40 * gl);
          rr(-100, -190, 200, 380, 20); ctx.fillStyle = gl ? mix(C.wh, '#E9FBEF', gl) : mix(C.wh, '#E5E7EB', g); ctx.fill(); noGlow();
          ctx.lineWidth = gl ? 9 : 5; ctx.strokeStyle = gl ? C.gr : mix(C.or, C.gy, g); ctx.stroke();
          ctx.restore();
          text(pl.n, 0, -146, { size: 30, color: mix(C.ink, C.gy, g), maxW: 180 });
          text(pl.p, 0, -76, { size: 66, color: gl ? C.gr : mix(C.or, C.gy, g) });
          for (let f = 0; f < 4; f++) {
            ctx.fillStyle = f < pl.f ? mix(C.ink, C.gy, g) : 'rgba(26,26,26,0.12)';
            rr(-70, -10 + f * 42, 140, 18, 9); ctx.fill();
          }
        });
        if (i === 1) markLabels(x, py + 580, 'decoy', prog(t, 47.0, 47.35));
        if (i === 2) markLabels(x + 90, py + 160, 'target', prog(t, 47.6, 47.95));
      });
    });
    // 3) café
    if (Math.abs(2 - pos) < 1.2) {
      ctx.save(); ctx.globalAlpha *= 1 - exitK;
      panel(off(2), 'CAFETERÍA', py => {
        const x0 = off(2);
        const items = [{ dx: -250, w: 110, h: 150, p: '$3.00' }, { dx: 0, w: 135, h: 195, p: '$4.50' }, { dx: 250, w: 160, h: 245, p: '$4.80' }];
        items.forEach((it, i) => {
          const k = popIn(t, 49.2 + i * 0.1, 0.35);
          const g = i === 1 ? eOut(prog(t, 49.8, 50.1)) : 0;
          const gl = i === 2 ? eOut(prog(t, 50.4, 50.7)) : 0;
          tf(x0 + it.dx, py + 480, clamp(k), 0, clamp(k), () => {
            coffee(0, 0, it.w, it.h, { gray: g, glow: gl ? C.gr : null, glowA: gl });
            text(it.p, 0, 64, { size: 54, color: gl > 0.5 ? C.gr : mix(C.ink, C.gy, g) });
          });
          if (i === 1) markLabels(x0 + it.dx, py + 615, 'decoy', prog(t, 49.8, 50.15));
          if (i === 2) markLabels(x0 + it.dx + 95, py + 170, 'target', prog(t, 50.4, 50.75));
        });
      });
      ctx.restore();
    }
    // puntos del carrusel
    for (let i = 0; i < 3; i++) {
      const act = 1 - clamp(Math.abs(i - pos));
      ctx.fillStyle = mix(C.gy, C.or, act);
      rr(CX - 60 + i * 50 - 10 - act * 12, 1262, 20 + act * 24, 20, 10); ctx.fill();
    }
  }

  // ---------- ESCENA 7: aplicación ----------
  function sceneAplicacion(t) {
    // ¿TIENES UN NEGOCIO?
    const qOut = eIn(prog(t, 53.1, 53.35));
    const w1 = popIn(t, 52.05, 0.35), w2 = popIn(t, 52.25, 0.4);
    ctx.save(); ctx.globalAlpha *= 1 - qOut; ctx.translate(0, -qOut * 200);
    tf(CX, 700, clamp(w1), 0, clamp(w1), () => text('¿TIENES UN', 0, 0, { size: 104, color: C.ink }));
    tf(CX, 830, clamp(w2), lerp(0.2, -0.04, clamp(w2)), clamp(w2), () => text('NEGOCIO?', 0, 0, { size: 140, color: C.or, maxW: 820 }));
    // tienda
    const st = popIn(t, 52.4, 0.4);
    tf(CX, 1080, clamp(st), 0, clamp(st), () => {
      ctx.lineWidth = 7; ctx.strokeStyle = C.ink;
      rr(-150, -40, 300, 160, 10); ctx.fillStyle = C.wh; ctx.fill(); ctx.stroke();
      for (let i = 0; i < 5; i++) { ctx.beginPath(); ctx.moveTo(-170 + i * 68, -100); ctx.lineTo(-102 + i * 68, -100); ctx.lineTo(-102 + i * 68, -40); ctx.arc(-136 + i * 68, -40, 34, 0, Math.PI); ctx.closePath(); ctx.fillStyle = i % 2 ? C.wh : C.or; ctx.fill(); ctx.stroke(); }
      rr(-40, 20, 80, 100, 6); ctx.fillStyle = C.ink; ctx.fill();
    });
    ctx.restore();
    // BAJAR PRECIO tachado
    const bIn = popIn(t, 53.2, 0.35), bOut = eIn(prog(t, 54.3, 54.55));
    if (t >= 53.2 && bOut < 1) {
      tf(CX, 860, clamp(bIn) * (1 - bOut * 0.3), 0, clamp(bIn) * (1 - bOut), () => {
        text('BAJAR', 0, -70, { size: 130, color: C.ink });
        text('PRECIO', 0, 70, { size: 130, color: C.ink, maxW: 820 });
        const s = eOut(prog(t, 53.7, 53.95));
        ctx.strokeStyle = C.or; ctx.lineWidth = 34; ctx.lineCap = 'round';
        ctx.beginPath(); ctx.moveTo(-400, 40); ctx.lineTo(lerp(-400, 400, s), lerp(40, -50, s)); ctx.stroke();
        const x = popIn(t, 53.95, 0.3);
        tf(320, -170, clamp(x), 0.2, clamp(x), () => {
          ctx.beginPath(); ctx.arc(0, 0, 62, 0, Math.PI * 2); ctx.fillStyle = C.ink; ctx.fill();
          ctx.strokeStyle = C.or; ctx.lineWidth = 16;
          ctx.beginPath(); ctx.moveTo(-24, -24); ctx.lineTo(24, 24); ctx.moveTo(24, -24); ctx.lineTo(-24, 24); ctx.stroke();
        });
      });
    }
    // tabla de 3 opciones
    const tiers = [
      { n: 'BÁSICO', p: '$19', f: 2, kind: 'base' },
      { n: 'PLUS', p: '$45', f: 3, kind: 'decoy' },
      { n: 'PRO', p: '$49', f: 5, kind: 'target' },
    ];
    const hi = eOut(prog(t, 55.6, 55.9));
    const exitK = prog(t, 56.85, 57);
    ctx.save(); ctx.globalAlpha *= 1 - exitK;
    tiers.forEach((tr, i) => {
      if (t < 54.4) return;
      const k = popIn(t, 54.45 + i * 0.15, 0.35);
      const x = CX + (i - 1) * 275 - (i === 2 ? 14 * hi : 0);
      const isT = tr.kind === 'target', isD = tr.kind === 'decoy';
      const s = clamp(k) * (isT ? 1 + 0.1 * hi : 1);
      tf(x, 870, s, 0, clamp(k), () => {
        ctx.save();
        if (isT && hi) glow(C.gr, 50 * hi);
        rr(-125, -270, 250, 520, 28);
        ctx.fillStyle = isD ? '#ECEDEF' : (isT ? mix(C.wh, '#E9FBEF', hi) : C.wh); ctx.fill(); noGlow();
        ctx.lineWidth = isT ? lerp(6, 11, hi) : 6; ctx.strokeStyle = isT ? mix(C.ink, C.gr, hi) : (isD ? C.gy : C.ink); ctx.stroke();
        ctx.restore();
        const col = isD ? C.gy : C.ink;
        text(tr.n, 0, -200, { size: 44, color: col, ls: 2 });
        text(tr.p, 0, -110, { size: 86, color: isD ? C.gy : (isT ? mix(C.or, C.gr, hi) : C.or) });
        for (let f = 0; f < 5; f++) {
          const on = f < tr.f;
          if (on) checkBadge(-70, -10 + f * 52, 15, isD ? C.gy : (isT ? C.gr : C.ink));
          else { ctx.strokeStyle = 'rgba(26,26,26,0.2)'; ctx.lineWidth = 5; ctx.beginPath(); ctx.moveTo(-82, -10 + f * 52); ctx.lineTo(-58, -10 + f * 52); ctx.stroke(); }
          ctx.fillStyle = on ? (isD ? C.gyL : 'rgba(26,26,26,0.25)') : 'rgba(26,26,26,0.08)';
          rr(-40, -19 + f * 52, 120, 18, 9); ctx.fill();
        }
      });
      if (isT) {
        const rb = popIn(t, 55.6, 0.4);
        tf(x, 870 - 270 * (1 + 0.1 * hi) - 6, clamp(rb), 0, clamp(rb), () => {
          pill(0, 0, 'MÁS POPULAR', { size: 26, bg: C.gr, color: C.wh, border: C.ink, padX: 20, h: 58 });
        });
        tf(x + 112, 870 - 360, clamp(rb) * 0.9, t * 1.5, clamp(rb), () => { ctx.fillStyle = C.or; star(0, 0, 44, 20, 5); ctx.fill(); ctx.lineWidth = 5; ctx.strokeStyle = C.ink; ctx.stroke(); });
        sparkles(x, 700, t, 55.65, 51, 240, 14, C.gr);
      }
      if (isD) {
        const dl = popIn(t, 54.9, 0.3);
        tf(x, 870 + 300, clamp(dl), 0, clamp(dl), () => pill(0, 0, 'SEÑUELO', { size: 28, bg: C.gy, color: C.ink, padX: 18, h: 54 }));
      }
    });
    ctx.restore();
  }

  // ---------- ESCENA 8: CTA ----------
  function cursor(x, y, s) {
    tf(x, y, s, -0.1, 1, () => {
      ctx.beginPath(); ctx.moveTo(0, 0); ctx.lineTo(0, 92); ctx.lineTo(24, 70); ctx.lineTo(42, 108); ctx.lineTo(60, 99); ctx.lineTo(42, 62); ctx.lineTo(74, 60); ctx.closePath();
      ctx.fillStyle = C.wh; ctx.fill(); ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.lineJoin = 'round'; ctx.stroke();
    });
  }
  function sceneCTA(t) {
    const cin = popIn(t, 57.05, 0.45);
    const out = eInOut(prog(t, 59.2, 59.7));
    // la tarjeta se va hacia el logo (arriba izquierda)
    const x = lerp(CX, 120, out), y = lerp(840, 330, out), s = clamp(cin) * lerp(1, 0.12, out);
    tf(x, y, s, 0, clamp(cin) * (1 - out * 0.6), () => {
      const pw = 800, ph = 640;
      ctx.save(); shadowCard(); rr(-pw / 2, -ph / 2, pw, ph, 44); ctx.fillStyle = C.wh; ctx.fill(); noGlow();
      ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.stroke(); ctx.restore();
      // avatar con logo
      const ay = -170;
      ctx.save();
      ctx.beginPath(); ctx.arc(0, ay, 118, 0, Math.PI * 2); ctx.fillStyle = C.bg; ctx.fill();
      ctx.lineWidth = 10; const ring = ctx.createLinearGradient(-118, ay - 118, 118, ay + 118); ring.addColorStop(0, C.or); ring.addColorStop(1, C.gr); ctx.strokeStyle = ring; ctx.stroke();
      if (logoImg) { const lh = 170, lw = lh * logoImg.width / logoImg.height; ctx.drawImage(logoImg, -lw / 2, ay - lh / 2 - 4, lw, lh); }
      ctx.restore();
      const hk = eBack(prog(t, 57.3, 57.65));
      tf(0, 20, hk, 0, clamp(hk * 2), () => text('@Atlas_path', 0, 0, { size: 92, color: C.ink, maxW: 720, ls: -1 }));
      tf(0, 92, 1, 0, prog(t, 57.5, 57.8), () => text('PSICOLOGÍA DETRÁS DE LO QUE COMPRAS', 0, 0, { size: 28, weight: 800, color: C.gy, ls: 2, maxW: 700 }));
      // botón
      const clicked = t >= 58.3;
      const press = 1 - 0.1 * Math.sin(prog(t, 58.25, 58.45) * Math.PI);
      const bpop = popIn(t, 57.45, 0.35);
      tf(0, 205, clamp(bpop) * press * (1 + 0.03 * Math.sin(t * 9) * (t < 58.3)), 0, clamp(bpop), () => {
        rr(-230, -62, 460, 124, 62); ctx.fillStyle = clicked ? C.gr : C.or; ctx.fill(); ctx.lineWidth = 7; ctx.strokeStyle = C.ink; ctx.stroke();
        text(clicked ? 'SIGUIENDO ✓' : 'SEGUIR', 0, 4, { size: 56, color: C.wh, ls: 3 });
      });
      // onda del clic
      const rp = prog(t, 58.3, 58.8);
      if (rp > 0 && rp < 1) { ctx.save(); ctx.globalAlpha *= 1 - rp; ctx.strokeStyle = C.gr; ctx.lineWidth = 10; rr(-230 - 60 * rp, 143 - 60 * rp, 460 + 120 * rp, 124 + 120 * rp, 62 + 60 * rp); ctx.stroke(); ctx.restore(); }
      // cursor
      if (t >= 57.55) {
        const mv = eOut(prog(t, 57.55, 58.2));
        const cs = 1 - 0.15 * Math.sin(prog(t, 58.25, 58.45) * Math.PI);
        cursor(lerp(330, 40, mv), lerp(560, 200, mv), cs);
      }
    });
    sparkles(CX, 1045, t, 58.35, 91, 320, 16, C.or);
    // loop: los vasos vuelven a entrar como en el primer cuadro
    if (t > 59.6) drawMenuCups(t, t - 60, { labelA: 0 });
  }

  // ---------- render ----------
  function render(t) {
    t = clamp(t, 0, TL.duration - 1e-6);
    background(t);
    // micro-sacudida en impactos
    let shake = 0;
    for (const a of [0.1, 6.8, 25.85, 28.05]) { const k = prog(t, a, a + 0.3); if (k > 0 && k < 1) shake += Math.sin(k * 40) * 10 * (1 - k); }
    // zoom punch suave en algunos cortes
    let zoom = 1;
    for (const a of [1.6, 3.0, 11.2, 39.2]) { const k = prog(t, a, a + 0.5); if (k > 0 && k < 1) zoom += 0.04 * Math.sin(k * Math.PI); }
    ctx.save();
    ctx.translate(CX, 860); ctx.scale(zoom, zoom); ctx.translate(-CX + shake, -860);
    if (t < 3) sceneHook(t);
    else if (t < 8) sceneGiro(t);
    else if (t < 20) sceneExperimento(t);
    else if (t < 30) sceneResultado(t);
    else if (t < 42) scenePorque(t);
    else if (t < 52) sceneDonde(t);
    else if (t < 57) sceneAplicacion(t);
    else sceneCTA(t);
    ctx.restore();
    wipe(t);
    logo(t);
    subtitles(t);
    progressBar(t);
  }

  function drawSafeZones() {
    ctx.save();
    ctx.fillStyle = 'rgba(255,0,0,0.18)';
    ctx.fillRect(0, 0, W, 250); ctx.fillRect(0, H - 400, W, 400); ctx.fillRect(W - 120, 250, 120, H - 650);
    ctx.restore();
  }

  async function init(canvas) {
    ctx = canvas.getContext('2d');
    const faces = [['Inter-Black.otf', 900], ['Inter-ExtraBold.otf', 800], ['Inter-SemiBold.otf', 600], ['Inter-Medium.otf', 500]];
    await Promise.all(faces.map(async ([f, w]) => {
      const ff = new FontFace(F, `url(fonts/${f})`, { weight: String(w) });
      await ff.load(); document.fonts.add(ff);
    }));
    logoImg = await new Promise(res => { const im = new Image(); im.onload = () => res(im); im.onerror = () => res(null); im.src = 'assets/logo-atlas-path.png'; });
  }

  window.Anim = { init, render, drawSafeZones, W, H };
})();
