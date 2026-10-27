// Motor de la animación: render(t) dibuja el frame del segundo t (0–30) en un
// canvas 1080×1920. Es determinista (sin Math.random ni relojes), así que el
// render cuadro a cuadro y la vista previa en tiempo real son idénticos.
(() => {
  const W = 1080, H = 1920, DURATION = 30;
  const P = window.PROMO, C = P.colors;
  const FD = '"Anton", "Inter", sans-serif';
  const FB = '"Inter", sans-serif';
  const TAU = Math.PI * 2;
  const BEAT = 0.5; // 120 BPM: todo cae en múltiplos de 0.5 s

  let ctx;

  // ---------------------------------------------------------------- math
  const clamp = (v, a = 0, b = 1) => Math.min(b, Math.max(a, v));
  const lerp = (a, b, p) => a + (b - a) * p;
  const prog = (t, a, b) => clamp((t - a) / (b - a));
  const E = {
    outCubic: p => 1 - Math.pow(1 - p, 3),
    inCubic: p => p * p * p,
    inOutCubic: p => (p < 0.5 ? 4 * p * p * p : 1 - Math.pow(-2 * p + 2, 3) / 2),
    outBack: (p, s = 1.70158) => 1 + (s + 1) * Math.pow(p - 1, 3) + s * Math.pow(p - 1, 2),
    outElastic: p => (p <= 0 ? 0 : p >= 1 ? 1 : Math.pow(2, -10 * p) * Math.sin((p * 10 - 0.75) * (TAU / 3)) + 1),
    outExpo: p => (p >= 1 ? 1 : 1 - Math.pow(2, -10 * p)),
    inExpo: p => (p <= 0 ? 0 : Math.pow(2, 10 * p - 10)),
  };
  function rng(seed) {
    return () => {
      seed = (seed + 0x6d2b79f5) | 0;
      let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
      t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
      return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
    };
  }
  // 1 justo en cada beat, decae rápido hasta el siguiente
  const beatPulse = (t, from = 0) => (t < from ? 0 : Math.exp(-((t - from) % BEAT) * 9));
  // golpe que decae a partir de t0
  const hit = (t, t0, k = 10) => (t < t0 ? 0 : Math.exp(-(t - t0) * k));

  // --------------------------------------------------------------- color
  function hex(h) {
    const n = parseInt(h.slice(1), 16);
    return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
  }
  function rgba(h, a = 1) {
    const [r, g, b] = hex(h);
    return `rgba(${r},${g},${b},${a})`;
  }
  function mix(h1, h2, p) {
    const a = hex(h1), b = hex(h2);
    return "#" + a.map((v, i) => Math.round(lerp(v, b[i], p)).toString(16).padStart(2, "0")).join("");
  }
  const PALETTE = [C.orange, C.magenta, C.yellow, C.cyan];

  // ------------------------------------------------------------- drawing
  function ball(x, y, r, color, sx = 1, sy = 1, glow = 1) {
    if (r <= 0.5) return;
    ctx.save();
    ctx.translate(x, y);
    if (glow > 0) {
      const g = ctx.createRadialGradient(0, 0, r * 0.6, 0, 0, r * 2.4);
      g.addColorStop(0, rgba(color, 0.45 * glow));
      g.addColorStop(1, rgba(color, 0));
      ctx.fillStyle = g;
      ctx.beginPath();
      ctx.arc(0, 0, r * 2.4, 0, TAU);
      ctx.fill();
    }
    ctx.scale(sx, sy);
    const g = ctx.createRadialGradient(-r * 0.35, -r * 0.4, r * 0.05, 0, 0, r);
    g.addColorStop(0, mix(color, "#ffffff", 0.55));
    g.addColorStop(0.45, color);
    g.addColorStop(1, mix(color, "#000000", 0.45));
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(0, 0, r, 0, TAU);
    ctx.fill();
    ctx.fillStyle = "rgba(255,255,255,.55)";
    ctx.beginPath();
    ctx.ellipse(-r * 0.38, -r * 0.45, r * 0.22, r * 0.13, -0.6, 0, TAU);
    ctx.fill();
    ctx.restore();
  }

  function shadow(x, floorY, r, alpha) {
    ctx.save();
    ctx.translate(x, floorY);
    ctx.scale(1, 0.18);
    const g = ctx.createRadialGradient(0, 0, 0, 0, 0, r * 1.3);
    g.addColorStop(0, `rgba(0,0,0,${alpha})`);
    g.addColorStop(1, "rgba(0,0,0,0)");
    ctx.fillStyle = g;
    ctx.beginPath();
    ctx.arc(0, 0, r * 1.3, 0, TAU);
    ctx.fill();
    ctx.restore();
  }

  const font = (size, fam = FD, weight = 400) => `${weight} ${size}px ${fam}`;

  function fit(str, fam, weight, maxSize, maxW, ls = 0) {
    ctx.font = font(maxSize, fam, weight);
    ctx.letterSpacing = ls + "px";
    const w = ctx.measureText(str).width - ls;
    ctx.letterSpacing = "0px";
    return w > maxW ? (maxSize * maxW) / w : maxSize;
  }

  function measure(str, size, fam = FD, weight = 400, ls = 0) {
    ctx.font = font(size, fam, weight);
    ctx.letterSpacing = ls + "px";
    const w = ctx.measureText(str).width - ls;
    ctx.letterSpacing = "0px";
    return w;
  }

  // Degradado de marca para textos grandes, a lo ancho del texto
  function brandGradient(cx, w, colors = [C.orange, C.magenta, C.yellow]) {
    const g = ctx.createLinearGradient(cx - w / 2, 0, cx + w / 2, 0);
    colors.forEach((c, i) => g.addColorStop(i / (colors.length - 1), c));
    return g;
  }

  function text(str, x, y, size, o = {}) {
    const {
      fam = FD, weight = 400, color = C.white, align = "center", ls = 0,
      alpha = 1, scale = 1, rot = 0, gradient = null, stroke = null, lw = 0,
    } = o;
    if (alpha <= 0 || scale <= 0) return;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.translate(x, y);
    if (rot) ctx.rotate(rot);
    if (scale !== 1) ctx.scale(scale, scale);
    ctx.font = font(size, fam, weight);
    ctx.letterSpacing = ls + "px";
    ctx.textAlign = align;
    ctx.textBaseline = "middle";
    // el letterSpacing añade espacio al final: compensa al centrar
    const dx = align === "center" ? ls / 2 : 0;
    if (stroke) {
      ctx.strokeStyle = stroke;
      ctx.lineWidth = lw;
      ctx.lineJoin = "round";
      ctx.strokeText(str, dx, 0);
    } else {
      ctx.fillStyle = gradient ? gradient(ctx.measureText(str).width) : color;
      ctx.fillText(str, dx, 0);
    }
    ctx.restore();
  }

  // Texto que sube desde detrás de una máscara (revelado tipo "línea")
  function revealText(str, x, y, size, p, o = {}) {
    if (p <= 0) return;
    ctx.save();
    ctx.beginPath();
    ctx.rect(0, y - size * 0.62, W, size * 1.24);
    ctx.clip();
    text(str, x, y + (1 - E.outCubic(p)) * size * 1.2, size, o);
    ctx.restore();
  }

  // Posición del centro de cada carácter de una línea centrada en x
  function charLayout(str, x, size, fam = FD, weight = 400) {
    ctx.font = font(size, fam, weight);
    const total = ctx.measureText(str).width;
    let cursor = x - total / 2;
    return [...str].map(ch => {
      const w = ctx.measureText(ch).width;
      const c = { ch, x: cursor + w / 2, w };
      cursor += w;
      return c;
    });
  }

  function pill(cx, cy, w, h, fill, alpha = 1, scale = 1) {
    if (scale <= 0) return;
    ctx.save();
    ctx.globalAlpha *= alpha;
    ctx.translate(cx, cy);
    ctx.scale(scale, scale);
    ctx.fillStyle = fill;
    ctx.beginPath();
    ctx.roundRect(-w / 2, -h / 2, w, h, h / 2);
    ctx.fill();
    ctx.restore();
  }

  function sunburst(cx, cy, rays, rot, color, alpha, radius = 2200) {
    if (alpha <= 0) return;
    ctx.save();
    ctx.translate(cx, cy);
    ctx.rotate(rot);
    ctx.fillStyle = rgba(color, alpha);
    const step = TAU / rays;
    ctx.beginPath();
    for (let i = 0; i < rays; i += 2) {
      ctx.moveTo(0, 0);
      ctx.arc(0, 0, radius, i * step, (i + 1) * step);
      ctx.closePath();
    }
    ctx.fill();
    ctx.restore();
  }

  function glowSpot(x, y, r, color, alpha) {
    const g = ctx.createRadialGradient(x, y, 0, x, y, r);
    g.addColorStop(0, rgba(color, alpha));
    g.addColorStop(1, rgba(color, 0));
    ctx.fillStyle = g;
    ctx.fillRect(x - r, y - r, r * 2, r * 2);
  }

  function background(base, t, glow1 = C.magenta, glow2 = C.orange, strength = 1) {
    ctx.fillStyle = base;
    ctx.fillRect(0, 0, W, H);
    // manchas de luz que flotan despacio
    glowSpot(540 + Math.sin(t * 0.7) * 260, 520 + Math.cos(t * 0.5) * 140, 900, glow1, 0.22 * strength);
    glowSpot(540 + Math.cos(t * 0.6) * 300, 1450 + Math.sin(t * 0.8) * 160, 1000, glow2, 0.18 * strength);
  }

  function ring(x, y, r, lw, color, alpha) {
    if (alpha <= 0 || r <= 0) return;
    ctx.save();
    ctx.strokeStyle = rgba(color, alpha);
    ctx.lineWidth = lw;
    ctx.beginPath();
    ctx.arc(x, y, r, 0, TAU);
    ctx.stroke();
    ctx.restore();
  }

  // Explosión de partículas calculada analíticamente (sin estado)
  function makeBurst(seed, n, speedMin, speedMax, sizeMin, sizeMax) {
    const r = rng(seed);
    return Array.from({ length: n }, () => ({
      a: r() * TAU,
      v: lerp(speedMin, speedMax, r()),
      s: lerp(sizeMin, sizeMax, r()),
      c: PALETTE[Math.floor(r() * PALETTE.length)],
      life: lerp(0.7, 1.4, r()),
    }));
  }
  function drawBurst(parts, x, y, dt, drag = 3.2, gravity = 900) {
    if (dt < 0) return;
    for (const p of parts) {
      const life = 1 - dt / p.life;
      if (life <= 0) continue;
      const d = (p.v * (1 - Math.exp(-drag * dt))) / drag;
      const px = x + Math.cos(p.a) * d;
      const py = y + Math.sin(p.a) * d + 0.5 * gravity * dt * dt;
      ctx.fillStyle = rgba(p.c, Math.min(1, life * 1.5));
      ctx.beginPath();
      ctx.arc(px, py, p.s * (0.4 + 0.6 * life), 0, TAU);
      ctx.fill();
    }
  }

  // ------------------------------------------------------------ the logo
  // Logo de marca centrado en (cx, cy). Entra con un "golpe" a partir de t0.
  function logo(cx, cy, s, t0, t) {
    const p1 = prog(t, t0, t0 + 0.45);
    const p2 = prog(t, t0 + 0.1, t0 + 0.55);
    const p3 = prog(t, t0 + 0.35, t0 + 0.8);
    const pulse = 1 + 0.025 * beatPulse(t, t0 + 1);
    ctx.save();
    ctx.translate(cx, cy);
    ctx.scale(s * pulse, s * pulse);
    const s1 = fit(P.brand.line1, FD, 400, 240, 940);
    const s2 = fit(P.brand.line2, FD, 400, 330, 940);
    text(P.brand.line1, 0, -170, s1, {
      scale: lerp(1.7, 1, E.outBack(p1)), alpha: prog(t, t0, t0 + 0.12),
    });
    text(P.brand.line2, 0, 60, s2, {
      scale: lerp(1.8, 1, E.outBack(p2)), alpha: prog(t, t0 + 0.1, t0 + 0.22),
      gradient: w => brandGradient(0, w),
    });
    const tagW = measure(P.brand.tag, 60, FB, 900, 18) + 110;
    pill(0, 270, tagW, 104, C.cyan, 1, E.outBack(p3, 2.4));
    text(P.brand.tag, 0, 272, 60, {
      fam: FB, weight: 900, ls: 18, color: C.bg, scale: E.outBack(p3, 2.4),
    });
    ctx.restore();
  }

  // ============================================================ SCENE 1
  // 0–4 s: una bola cae y rebota a ritmo, llegan dos más, giran en espiral
  // y explotan revelando el logo.
  const FLOOR = 1320;
  const LANDS = [0.5, 1.0, 1.5];
  const burst1 = makeBurst(11, 90, 900, 2700, 6, 22);

  function bounceY(u) {
    // y del punto de contacto (base de la bola)
    if (u < 0.5) { const p = u / 0.5; return lerp(-260, FLOOR, p * p); }
    if (u < 1.0) { const p = (u - 0.5) / 0.5; return FLOOR - 560 * 4 * p * (1 - p); }
    if (u < 1.5) { const p = (u - 1.0) / 0.5; return FLOOR - 240 * 4 * p * (1 - p); }
    return FLOOR;
  }
  const squashAt = u => LANDS.reduce((m, L) => Math.max(m, hit(u, L, 16)), 0);

  function scene1(t) {
    background(C.bg, t, C.magenta, C.orange, 0.9 + 0.4 * prog(t, 1.8, 2.2));
    sunburst(540, 900, 24, t * 0.15, C.orange, 0.06 * prog(t, 2.0, 2.6));
    // línea de suelo luminosa que se enciende con cada rebote
    const floorA = (1 - prog(t, 1.6, 2.0)) * (0.35 + 0.65 * squashAt(t));
    if (floorA > 0) {
      const g = ctx.createLinearGradient(0, 0, W, 0);
      g.addColorStop(0, rgba(C.orange, 0));
      g.addColorStop(0.5, rgba(C.orange, floorA));
      g.addColorStop(1, rgba(C.orange, 0));
      ctx.fillStyle = g;
      ctx.fillRect(0, FLOOR + 4, W, 4);
      glowSpot(540, FLOOR + 6, 520, C.orange, 0.22 * floorA);
    }

    const spiral = prog(t, 1.5, 2.0);
    const balls = [
      { r: 115, c: C.orange },
      { r: 75, c: C.magenta },
      { r: 75, c: C.yellow },
    ];
    // posición en el suelo antes de la espiral
    const ground = [
      () => ({ x: 540, y: bounceY(t), sq: squashAt(t) }),
      () => {
        const p = E.outCubic(prog(t, 0.75, 1.45));
        const hop = t < 1.0 ? 0 : t < 1.5 ? 4 * ((t - 1) / 0.5) * (1 - (t - 1) / 0.5) * 130 : 0;
        return { x: lerp(-160, 250, p), y: FLOOR - hop, sq: hit(t, 1.5, 16) };
      },
      () => {
        const p = E.outCubic(prog(t, 0.75, 1.45));
        const hop = t < 1.0 ? 0 : t < 1.5 ? 4 * ((t - 1) / 0.5) * (1 - (t - 1) / 0.5) * 130 : 0;
        return { x: lerp(1240, 830, p), y: FLOOR - hop, sq: hit(t, 1.5, 16) };
      },
    ];

    if (t < 2.0) {
      const e = E.inCubic(spiral);
      balls.forEach((b, i) => {
        const g = ground[i]();
        let sy = 1 - 0.38 * g.sq, sx = 1 + 0.38 * g.sq;
        let x = g.x, y = g.y - b.r * sy, r = b.r;
        if (spiral > 0) {
          const s0 = i === 0 ? { x: 540, y: FLOOR - b.r } : { x: i === 1 ? 250 : 830, y: FLOOR - b.r };
          const cx = 540, cy = 900;
          const dx = s0.x - cx, dy = s0.y - cy;
          const ang = e * TAU * 1.25;
          const k = 1 - e;
          x = cx + (dx * Math.cos(ang) - dy * Math.sin(ang)) * k;
          y = cy + (dx * Math.sin(ang) + dy * Math.cos(ang)) * k;
          r = b.r * lerp(1, 0.45, e);
          sx = sy = 1;
        }
        if (spiral < 0.3) shadow(g.x, FLOOR + 6, b.r, 0.5 * (1 - (FLOOR - g.y) / 1600) * (1 - spiral / 0.3));
        ball(x, y, r, b.c, sx, sy, 0.8);
      });
      // anillos de impacto en cada rebote
      LANDS.forEach(L => {
        const d = t - L;
        if (d > 0 && d < 0.5) ring(540, FLOOR + 4, 120 + d * 700, 6, C.orange, 0.5 * (1 - d / 0.5));
      });
    }

    // explosión + logo
    if (t >= 2.0) {
      const d = t - 2.0;
      [0, 0.07, 0.14].forEach((o, i) => {
        const p = prog(d, o, o + 0.9);
        ring(540, 900, 1500 * E.outExpo(p), 30 * (1 - p) + 2, PALETTE[i], 1 - p);
      });
      drawBurst(burst1, 540, 900, d);
      // las tres bolas orbitan el logo
      balls.forEach((b, i) => {
        const pop = E.outElastic(prog(t, 2.25 + i * 0.12, 3.1 + i * 0.12));
        const a = t * 0.9 + (i * TAU) / 3;
        const x = 540 + Math.cos(a) * 455;
        const y = 920 + Math.sin(a) * 520;
        if (Math.sin(a) < 0) ball(x, y, b.r * 0.42 * pop, b.c, 1, 1, 0.7);
      });
      logo(540, 900, 1, 2.0, t);
      balls.forEach((b, i) => {
        const pop = E.outElastic(prog(t, 2.25 + i * 0.12, 3.1 + i * 0.12));
        const a = t * 0.9 + (i * TAU) / 3;
        const x = 540 + Math.cos(a) * 455;
        const y = 920 + Math.sin(a) * 520;
        if (Math.sin(a) >= 0) ball(x, y, b.r * 0.42 * pop, b.c, 1, 1, 0.7);
      });
    }
  }

  // ============================================================ SCENE 2
  // 4–8 s: "¿Tu marca se ve aburrida?" — una bola rompe "aburrida" y entra
  // "¡Dale energía!".
  const IMPACT = 6.0;
  const hookSize = () => Math.min(...P.hook.map(l => fit(l, FD, 400, 215, 960)));
  const shatter = (() => {
    const r = rng(23);
    return Array.from({ length: 40 }, () => ({
      vx: (r() - 0.5) * 900, vy: -500 - r() * 1100, w: (r() - 0.5) * 14,
    }));
  })();
  const ballAt = t => {
    // bola que entra volando desde abajo a la derecha y rebota hacia arriba
    if (t < IMPACT) {
      const p = prog(t, 5.55, IMPACT);
      return { x: lerp(1300, 700, p), y: lerp(1900, 1090, p), on: p > 0 };
    }
    const p = prog(t, IMPACT, IMPACT + 0.55);
    return { x: lerp(700, -250, p), y: lerp(1090, 120, E.outCubic(p)), on: p < 1 };
  };

  function scene2(t) {
    background(C.bg2, t, C.magenta, C.cyan, 0.7);
    const size = hookSize();
    const ys = [650, 870, 1090];
    const answered = t >= IMPACT + 0.25;
    sunburst(540, 930, 20, t * 0.25, C.orange, 0.1 * E.outCubic(prog(t, IMPACT + 0.25, IMPACT + 0.7)));

    // líneas 1 y 2: entran, luego se caen tras el impacto
    for (let i = 0; i < 2; i++) {
      const p = prog(t, 4.0 + i * 0.5, 4.45 + i * 0.5);
      const fall = E.inCubic(prog(t, IMPACT + 0.05 + i * 0.04, IMPACT + 0.5 + i * 0.04));
      if (fall >= 1) continue;
      ctx.save();
      ctx.translate(0, fall * 1400);
      ctx.translate(540, ys[i]);
      ctx.rotate(fall * (i ? 0.4 : -0.3));
      ctx.translate(-540, -ys[i]);
      revealText(P.hook[i], 540, ys[i], size, p);
      ctx.restore();
    }

    // línea 3: gris, "triste", y estalla letra a letra
    const line3 = P.hook[2];
    if (t < IMPACT) {
      const p = prog(t, 5.0, 5.45);
      const droop = prog(t, 5.3, IMPACT) * 0.05;
      ctx.save();
      ctx.translate(540, ys[2]);
      ctx.rotate(Math.sin(t * 3) * droop);
      ctx.translate(-540, -ys[2]);
      revealText(line3, 540, ys[2], size, p, { color: C.muted });
      ctx.restore();
    } else {
      const d = t - IMPACT;
      charLayout(line3, 540, size).forEach((c, i) => {
        const s = shatter[i % shatter.length];
        const vx = s.vx + (c.x - 700) * 2.2;
        const x = c.x + vx * d;
        const y = ys[2] + s.vy * d + 0.5 * 3600 * d * d;
        if (y > H + 300) return;
        text(c.ch, x, y, size, { color: C.muted, rot: s.w * d });
      });
    }

    // la bola, con estela
    for (let k = 5; k >= 0; k--) {
      const b = ballAt(t - k * 0.018);
      ctx.globalAlpha = k === 0 ? 1 : 0.3 * (1 - k / 6);
      if (b.on) ball(b.x, b.y, 95, C.orange, 1, 1, k === 0 ? 1 : 0);
      ctx.globalAlpha = 1;
    }
    if (t >= IMPACT) {
      const d = t - IMPACT;
      ring(700, 1090, 100 + d * 1600, 26 * (1 - prog(d, 0, 0.5)) + 2, C.yellow, 1 - prog(d, 0, 0.5));
    }

    // respuesta
    if (answered) {
      const pulse = 1 + 0.03 * beatPulse(t, 7.0);
      const sA = fit(P.answer[0], FD, 400, 250, 900);
      const sB = fit(P.answer[1], FD, 400, 330, 900);
      const pA = prog(t, IMPACT + 0.25, IMPACT + 0.6);
      const pB = prog(t, IMPACT + 0.5, IMPACT + 0.85);
      text(P.answer[0], 540, 770, sA, {
        scale: lerp(2.4, 1, E.outBack(pA)) * pulse, alpha: prog(t, IMPACT + 0.25, IMPACT + 0.35),
      });
      text(P.answer[1], 540, 1060, sB, {
        scale: lerp(2.4, 1, E.outBack(pB)) * pulse, alpha: prog(t, IMPACT + 0.5, IMPACT + 0.6),
        gradient: w => brandGradient(0, w),
      });
      [IMPACT + 0.25, IMPACT + 0.5].forEach((t0, i) => {
        const p = prog(t, t0, t0 + 0.6);
        if (p > 0 && p < 1) ring(540, i ? 1060 : 770, 200 + E.outExpo(p) * 900, 16 * (1 - p), i ? C.magenta : C.white, 1 - p);
      });
    }
  }

  // ============================================================ SCENE 3
  // 8–14 s: servicios en tarjetas que entran a ritmo.
  function scene3(t) {
    background(C.bg, t, C.orange, C.magenta, 0.55);
    // retícula diagonal en movimiento
    ctx.save();
    ctx.strokeStyle = "rgba(255,255,255,.045)";
    ctx.lineWidth = 2;
    const off = (t * 60) % 120;
    ctx.beginPath();
    for (let x = -H; x < W + H; x += 120) {
      ctx.moveTo(x + off, 0);
      ctx.lineTo(x + off - H * 0.6, H);
    }
    ctx.stroke();
    ctx.restore();

    const hp = prog(t, 8.0, 8.4);
    revealText(P.servicesTitle, 540, 330, 50, hp, { fam: FB, weight: 900, ls: 10, color: C.yellow });
    const lw = 320 * E.inOutCubic(prog(t, 8.15, 8.65));
    ctx.fillStyle = C.yellow;
    ctx.fillRect(540 - lw / 2, 378, lw, 6);

    const colors = [C.orange, C.magenta, C.yellow, C.cyan];
    const runner = t >= 10.5 ? Math.floor((t - 10.5) / BEAT) % 4 : -1;
    P.services.forEach((s, i) => {
      const t0 = 8.5 + i * 0.5;
      const p = prog(t, t0 - 0.1, t0 + 0.5);
      if (p <= 0) return;
      const x = 70 + 1150 * (1 - E.outBack(p, 1.2));
      const y = 450 + i * 290;
      const w = 940, h = 250;
      const active = i === runner ? beatPulse(t, 10.5) : 0;
      const c = colors[i];

      ctx.save();
      ctx.fillStyle = `rgba(255,255,255,${0.06 + 0.06 * active})`;
      ctx.beginPath();
      ctx.roundRect(x, y, w, h, 40);
      ctx.fill();
      const g = ctx.createLinearGradient(x, y, x + w, y + h);
      g.addColorStop(0, rgba(c, 0.9));
      g.addColorStop(1, rgba(c, 0.15 + 0.5 * active));
      ctx.strokeStyle = g;
      ctx.lineWidth = 3 + 3 * active;
      ctx.stroke();
      ctx.restore();

      const pop = E.outElastic(prog(t, t0 + 0.15, t0 + 1.0));
      const bob = beatPulse(t, 10.5) * (i === runner ? 1 : 0.25);
      ball(x + 135, y + h / 2, 72 * pop, c, 1 + 0.18 * bob, 1 - 0.18 * bob, 0.6 + 0.5 * active);

      text(`0${i + 1}`, x + w - 44, y + 56, 34, { fam: FB, weight: 900, color: c, align: "right", ls: 4 });
      const ts = fit(s.title, FD, 400, 100, 560);
      text(s.title, x + 250, y + 112, ts, { align: "left" });
      const ss = fit(s.sub, FB, 400, 36, 640);
      text(s.sub, x + 250, y + 188, ss, { fam: FB, color: "rgba(255,246,236,.72)", align: "left" });
    });

    const fp = prog(t, 11.0, 11.5);
    revealText(P.servicesFooter, 540, 1700, 44, fp, { fam: FB, weight: 700, color: "rgba(255,246,236,.85)" });
  }

  // ============================================================ SCENE 4
  // 14–20 s: muro de "obras" en columnas con parallax.
  const images = [];
  const KINDS = ["blobs", "rings", "stripes", "dots", "burst", "ball"];
  const columns = (() => {
    const r = rng(77);
    const heights = [320, 400, 480, 560];
    let n = 0;
    return [0, 1, 2].map(ci => {
      const tiles = [];
      let y = -2300 + ci * 140;
      while (y < 2300) {
        const h = heights[Math.floor(r() * heights.length)];
        const a = Math.floor(r() * 4);
        tiles.push({
          y, h, kind: KINDS[Math.floor(r() * KINDS.length)],
          c1: PALETTE[a], c2: PALETTE[(a + 1 + Math.floor(r() * 3)) % 4],
          seed: r() * 100, img: n++,
        });
        y += h + 30;
      }
      return tiles;
    });
  })();

  function tileArt(tile, w, h, t) {
    const { kind, c1, c2, seed } = tile;
    const tt = t + seed;
    if (images.length) {
      const img = images[tile.img % images.length];
      if (img.complete && img.naturalWidth) {
        const s = Math.max(w / img.naturalWidth, h / img.naturalHeight) * (1.05 + 0.03 * Math.sin(tt));
        const iw = img.naturalWidth * s, ih = img.naturalHeight * s;
        ctx.drawImage(img, (w - iw) / 2, (h - ih) / 2, iw, ih);
        return;
      }
    }
    switch (kind) {
      case "blobs": {
        ctx.fillStyle = mix(c1, "#000000", 0.35);
        ctx.fillRect(0, 0, w, h);
        for (let i = 0; i < 3; i++) {
          const x = w * (0.3 + 0.4 * Math.sin(tt * 0.9 + i * 2.1));
          const y = h * (0.3 + 0.4 * Math.cos(tt * 0.7 + i * 1.7));
          glowSpot(x, y, w * 0.75, i % 2 ? c2 : c1, 0.95);
        }
        break;
      }
      case "rings": {
        ctx.fillStyle = C.bg2;
        ctx.fillRect(0, 0, w, h);
        for (let i = 9; i >= 0; i--) {
          ctx.fillStyle = i % 2 ? c1 : c2;
          ctx.beginPath();
          ctx.arc(w / 2, h / 2, Math.max(0, i * 42 + ((tt * 40) % 84) - 20), 0, TAU);
          ctx.fill();
        }
        break;
      }
      case "stripes": {
        ctx.fillStyle = c1;
        ctx.fillRect(0, 0, w, h);
        ctx.save();
        ctx.translate(w / 2, h / 2);
        ctx.rotate(-0.6);
        ctx.fillStyle = c2;
        const o = (tt * 50) % 80;
        for (let x = -900; x < 900; x += 80) ctx.fillRect(x + o, -900, 36, 1800);
        ctx.restore();
        ball(w * 0.5, h * 0.5, w * 0.2, C.bg2, 1, 1, 0);
        break;
      }
      case "dots": {
        ctx.fillStyle = c1;
        ctx.fillRect(0, 0, w, h);
        ctx.fillStyle = C.bg;
        for (let y = 20; y < h; y += 36)
          for (let x = 20; x < w; x += 36) {
            const d = Math.hypot(x - w / 2, y - h / 2);
            const s = 4 + 12 * (0.5 + 0.5 * Math.sin(d * 0.03 - tt * 3));
            ctx.beginPath();
            ctx.arc(x, y, s, 0, TAU);
            ctx.fill();
          }
        break;
      }
      case "burst": {
        ctx.fillStyle = c1;
        ctx.fillRect(0, 0, w, h);
        sunburst(w / 2, h / 2, 16, tt * 0.6, c2, 1, 900);
        ball(w / 2, h / 2, w * 0.18, C.white, 1, 1, 0);
        break;
      }
      default: {
        const g = ctx.createLinearGradient(0, 0, 0, h);
        g.addColorStop(0, mix(c2, "#000000", 0.2));
        g.addColorStop(1, mix(c2, "#000000", 0.7));
        ctx.fillStyle = g;
        ctx.fillRect(0, 0, w, h);
        const b = Math.abs(Math.sin(tt * 2.6)) * h * 0.25;
        shadow(w / 2, h * 0.82, w * 0.22, 0.45);
        ball(w / 2, h * 0.82 - w * 0.22 - b, w * 0.22, c1, 1, 1, 0.5);
      }
    }
  }

  function scene4(t) {
    background(C.bg, t, C.magenta, C.orange, 0.8);
    const colW = 330, gap = 30;
    const speeds = [-95, 75, -115];
    ctx.save();
    ctx.translate(540, 1080);
    ctx.rotate(-0.14);
    columns.forEach((tiles, ci) => {
      const x = (ci - 1) * (colW + gap) - colW / 2;
      const scroll = (t - 14) * speeds[ci] + (1 - E.outCubic(prog(t, 13.6, 14.8))) * (ci === 1 ? -500 : 500);
      tiles.forEach(tile => {
        const y = tile.y + scroll;
        if (y > 1500 || y + tile.h < -1500) return;
        const dist = Math.hypot(x + colW / 2, y + tile.h / 2);
        const d0 = 14.0 + dist / 2200;
        const s = E.outBack(prog(t, d0, d0 + 0.5));
        if (s <= 0) return;
        ctx.save();
        ctx.translate(x + colW / 2, y + tile.h / 2);
        ctx.scale(s, s);
        ctx.translate(-colW / 2, -tile.h / 2);
        ctx.beginPath();
        ctx.roundRect(0, 0, colW, tile.h, 30);
        ctx.clip();
        tileArt(tile, colW, tile.h, t);
        ctx.restore();
      });
    });
    ctx.restore();

    // bandas oscuras arriba y abajo para que el texto se lea
    let g = ctx.createLinearGradient(0, 0, 0, 720);
    g.addColorStop(0, rgba(C.bg, 0.97));
    g.addColorStop(0.65, rgba(C.bg, 0.85));
    g.addColorStop(1, rgba(C.bg, 0));
    ctx.fillStyle = g;
    ctx.fillRect(0, 0, W, 720);
    g = ctx.createLinearGradient(0, H - 420, 0, H);
    g.addColorStop(0, rgba(C.bg, 0));
    g.addColorStop(1, rgba(C.bg, 0.95));
    ctx.fillStyle = g;
    ctx.fillRect(0, H - 420, W, 420);

    const s = Math.min(fit(P.portfolioTitle[0], FD, 400, 200, 960), fit(P.portfolioTitle[1], FD, 400, 200, 960));
    revealText(P.portfolioTitle[0], 540, 270, s, prog(t, 14.1, 14.5));
    revealText(P.portfolioTitle[1], 540, 470, s, prog(t, 14.35, 14.75), { gradient: w => brandGradient(0, w) });

    const cp = E.outBack(prog(t, 15.0, 15.5));
    const cs = fit(P.portfolioCaption, FB, 900, 34, 820, 6);
    const cw = measure(P.portfolioCaption, cs, FB, 900, 6) + 90;
    pill(540, 1770, cw, 92, C.white, 1, cp);
    text(P.portfolioCaption, 540, 1772, cs, { fam: FB, weight: 900, ls: 6, color: C.bg, scale: cp });
  }

  // ============================================================ SCENE 5
  // 20–25 s: tres razones, cada una con su barrido de color.
  const SEG = [20.0, 21.5, 23.0];
  const SEG_COLORS = [C.orange, C.magenta, C.yellow];

  function valueSegment(k, t) {
    const s0 = SEG[k];
    ctx.fillStyle = SEG_COLORS[k];
    ctx.fillRect(0, 0, W, H);
    sunburst(540, 1150, 18, t * 0.2 + k, "#ffffff", 0.08);

    text(`0${k + 1}`, 1030, 700, 520, {
      align: "right", stroke: rgba(C.bg, 0.16), lw: 6,
      alpha: prog(t, s0, s0 + 0.3),
    });
    text(P.valuesTitle, 540, 250, 36, {
      fam: FB, weight: 900, ls: 10, color: rgba(C.bg, 0.75),
    });

    // bola que cae y aterriza en el beat
    const land = s0 + 0.5;
    const floor = 860;
    let y;
    if (t < land) { const p = prog(t, s0, land); y = lerp(-200, floor, p * p); }
    else { const p = ((t - land) % 0.5) / 0.5; y = floor - 4 * p * (1 - p) * 140 * Math.exp(-(t - land) * 1.5); }
    const sq = hit(t, land, 16);
    const r = 85;
    shadow(540, floor + 8, r, 0.35);
    ball(540, y - r * (1 - 0.35 * sq), r, C.bg2, 1 + 0.35 * sq, 1 - 0.35 * sq, 0);

    const lines = P.values[k].split("\n");
    const size = Math.min(...lines.map(l => fit(l, FD, 400, 270, 940)));
    let ci = 0;
    lines.forEach((line, li) => {
      const y0 = 1130 + li * size * 1.02;
      charLayout(line, 540, size).forEach(c => {
        const d0 = s0 + 0.05 + ci++ * 0.025;
        const p = prog(t, d0, d0 + 0.4);
        if (p <= 0) return;
        text(c.ch, c.x, y0 + (1 - E.outBack(p)) * 160, size, {
          color: C.bg, alpha: prog(t, d0, d0 + 0.1),
        });
      });
    });
  }

  function scene5(t) {
    for (let k = 0; k < SEG.length; k++) {
      if (k > 0 && t < SEG[k] - 0.3) break;
      if (k + 1 < SEG.length && t >= SEG[k + 1]) continue;
      if (k === 0) { valueSegment(0, t); continue; }
      const q = E.inOutCubic(prog(t, SEG[k] - 0.3, SEG[k] + 0.05));
      const edge = lerp(-500, W + 500, q);
      ctx.save();
      ctx.beginPath();
      ctx.moveTo(-10, -10);
      ctx.lineTo(edge + 250, -10);
      ctx.lineTo(edge - 250, H + 10);
      ctx.lineTo(-10, H + 10);
      ctx.closePath();
      ctx.clip();
      valueSegment(k, t);
      ctx.restore();
    }
  }

  // ============================================================ SCENE 6
  // 25–30 s: llamada a la acción.
  function scene6(t) {
    background(C.bg, t, C.orange, C.magenta, 1);
    sunburst(540, 1330, 28, t * 0.12, C.magenta, 0.07 * prog(t, 25, 25.6));

    const decor = [
      { x: 120, y: 700, r: 42, c: C.magenta, d: 25.0 },
      { x: 955, y: 640, r: 58, c: C.yellow, d: 25.12 },
      { x: 150, y: 1790, r: 52, c: C.orange, d: 25.24 },
      { x: 935, y: 1800, r: 36, c: C.cyan, d: 25.36 },
    ];
    decor.forEach((b, i) => {
      const p = E.outElastic(prog(t, b.d, b.d + 0.9));
      ball(b.x, b.y + Math.sin(t * 2.2 + i) * 18, b.r * p, b.c, 1, 1, 0.8);
    });

    logo(540, 400, 0.55, 25.0, t);

    const sA = fit(P.ctaTitle[0], FD, 400, 160, 960);
    const sB = fit(P.ctaTitle[1], FD, 400, 230, 960);
    revealText(P.ctaTitle[0], 540, 830, sA, prog(t, 25.5, 25.9));
    revealText(P.ctaTitle[1], 540, 1030, sB, prog(t, 26.0, 26.4), { gradient: w => brandGradient(0, w) });

    // botón
    const bp = E.outBack(prog(t, 26.5, 27.0), 2.2);
    const bpulse = 1 + 0.035 * beatPulse(t, 27.0) - 0.04 * hit(t, 28.0, 12);
    const bw = 880, bh = 170, by = 1330;
    if (bp > 0) {
      ctx.save();
      ctx.translate(540, by);
      ctx.scale(bp * bpulse, bp * bpulse);
      glowSpot(0, 0, 620, C.magenta, 0.35);
      ctx.beginPath();
      ctx.roundRect(-bw / 2, -bh / 2, bw, bh, bh / 2);
      const g = ctx.createLinearGradient(-bw / 2, 0, bw / 2, 0);
      g.addColorStop(0, C.orange);
      g.addColorStop(1, C.magenta);
      ctx.fillStyle = g;
      ctx.fill();
      // brillo que cruza el botón cada 2 s
      ctx.save();
      ctx.clip();
      const sh = ((t - 27.0) % 2) / 0.6;
      if (t > 27.0 && sh < 1) {
        const sx = lerp(-bw, bw, sh);
        const sg = ctx.createLinearGradient(sx - 120, 0, sx + 120, 0);
        sg.addColorStop(0, "rgba(255,255,255,0)");
        sg.addColorStop(0.5, "rgba(255,255,255,.45)");
        sg.addColorStop(1, "rgba(255,255,255,0)");
        ctx.fillStyle = sg;
        ctx.fillRect(-bw / 2, -bh / 2, bw, bh);
      }
      ctx.restore();
      const ts = fit(P.ctaButton, FB, 900, 58, bw - 140, 3);
      text(P.ctaButton, 0, 3, ts, { fam: FB, weight: 900, ls: 3, color: C.white });
      ctx.restore();
    }
    // "toque" de dedo sobre el botón
    const tp = prog(t, 28.0, 28.7);
    if (tp > 0 && tp < 1) {
      ring(700, by + 20, 30 + 260 * E.outCubic(tp), 10 * (1 - tp), C.white, 1 - tp);
      ring(700, by + 20, 20 + 140 * E.outCubic(tp), 6 * (1 - tp), C.white, 0.6 * (1 - tp));
    }

    // URL que se escribe sola
    const url = P.brand.url;
    const n = Math.floor(url.length * prog(t, 27.0, 28.0));
    const us = fit(url, FB, 700, 54, 900);
    const shown = url.slice(0, n);
    if (t >= 27.0) {
      ctx.font = font(us, FB, 700);
      const full = ctx.measureText(url).width;
      text(shown, 540 - full / 2, 1560, us, { fam: FB, weight: 700, align: "left" });
      const caret = Math.floor(t * 2.5) % 2 === 0 || t < 28.0;
      if (caret && t < 29.2) {
        const cx = 540 - full / 2 + ctx.measureText(shown).width + 8;
        ctx.fillStyle = C.yellow;
        ctx.fillRect(cx, 1560 - us * 0.5, 6, us);
      }
      const ul = full * E.inOutCubic(prog(t, 28.0, 28.5));
      ctx.fillStyle = C.yellow;
      ctx.fillRect(540 - full / 2, 1560 + us * 0.62, ul, 5);
    }
  }

  // ======================================================== composition
  const SCENES = [
    { start: 0, draw: scene1 },
    { start: 4, draw: scene2 },
    { start: 8, draw: scene3 },
    { start: 14, draw: scene4 },
    { start: 20, draw: scene5 },
    { start: 25, draw: scene6 },
  ];
  // barrido circular que termina justo en el beat de cada cambio de escena
  const WIPES = [
    { x: 540, y: 900, c: C.magenta },
    { x: 700, y: 1090, c: C.orange },
    { x: 540, y: 1700, c: C.yellow },
    { x: 540, y: 1770, c: C.cyan },
    { x: 540, y: 860, c: C.white },
  ];
  const WIPE_DUR = 0.45;
  const IMPACTS = [{ t: 2.0, a: 26 }, { t: IMPACT, a: 18 }, { t: 20.0, a: 10 }, { t: 25.0, a: 8 }];

  function render(t) {
    t = clamp(t, 0, DURATION - 1e-6);
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.globalAlpha = 1;
    ctx.fillStyle = C.bg;
    ctx.fillRect(0, 0, W, H);

    // sacudida de cámara en los impactos
    let sx = 0, sy = 0;
    IMPACTS.forEach((im, i) => {
      const h = hit(t, im.t, 9) * im.a;
      sx += Math.sin((t - im.t) * 70 + i) * h;
      sy += Math.cos((t - im.t) * 83 + i * 2) * h;
    });
    ctx.save();
    ctx.translate(sx, sy);

    let idx = 0;
    for (let i = 0; i < SCENES.length; i++) if (t >= SCENES[i].start) idx = i;
    SCENES[idx].draw(t);

    const next = SCENES[idx + 1];
    if (next && t >= next.start - WIPE_DUR) {
      const w = WIPES[idx];
      const p = E.inOutCubic(prog(t, next.start - WIPE_DUR, next.start));
      const maxR = Math.hypot(Math.max(w.x, W - w.x), Math.max(w.y, H - w.y)) + 60;
      const r = maxR * p;
      ctx.save();
      ctx.beginPath();
      ctx.arc(w.x, w.y, r, 0, TAU);
      ctx.clip();
      next.draw(t);
      ctx.restore();
      ring(w.x, w.y, r, 50 * (1 - p) + 10, w.c, 1);
    }
    ctx.restore();

    // destello blanco en la explosión del logo
    const flash = hit(t, 2.0, 7);
    if (flash > 0.01) {
      ctx.fillStyle = `rgba(255,246,236,${flash})`;
      ctx.fillRect(0, 0, W, H);
    }

    // viñeta
    const v = ctx.createRadialGradient(540, 960, 600, 540, 960, 1250);
    v.addColorStop(0, "rgba(0,0,0,0)");
    v.addColorStop(1, "rgba(0,0,0,.38)");
    ctx.fillStyle = v;
    ctx.fillRect(0, 0, W, H);
  }

  async function init(canvas) {
    canvas.width = W;
    canvas.height = H;
    ctx = canvas.getContext("2d");
    const faces = [
      new FontFace("Anton", "url(fonts/anton-latin-400-normal.woff2)", { weight: "400" }),
      new FontFace("Inter", "url(fonts/inter-latin-400-normal.woff2)", { weight: "400" }),
      new FontFace("Inter", "url(fonts/inter-latin-700-normal.woff2)", { weight: "700" }),
      new FontFace("Inter", "url(fonts/inter-latin-900-normal.woff2)", { weight: "900" }),
    ];
    await Promise.all(faces.map(f => f.load().then(ff => document.fonts.add(ff))));
    await Promise.all(
      (P.portfolioImages || []).map(src => new Promise(res => {
        const img = new Image();
        img.onload = img.onerror = () => res();
        img.src = src;
        images.push(img);
      })),
    );
    images.splice(0, images.length, ...images.filter(i => i.naturalWidth));
  }

  window.Promo = { W, H, DURATION, init, render };
})();
