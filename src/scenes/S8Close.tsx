import React from 'react';
import {AbsoluteFill, Img, random, staticFile, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, lerp, prog} from '../theme';
import {fibonacciSphere, lerp3, project, rotX, rotY, V3} from '../lib/space';
import {DeepBackground, ParticleField, Vignette} from '../components/Atmosphere';
import {Reveal, TextBlock} from '../components/Reveal';
import {WhatsAppGlyph} from '../components/Icons';

// Logotipo: 495×482 px original, escalado a 560 px de ancho
const LOGO_W = 560;
const LOGO_K = LOGO_W / 495;
const LOGO_TOP = 560;
const LOGO_LEFT = 540 - LOGO_W / 2;
const GLOBE = {x: LOGO_LEFT + 246 * LOGO_K, y: LOGO_TOP + 129 * LOGO_K, r: 128 * LOGO_K};

const N = 130;
const SPH = fibonacciSphere(N, 1);
const FROM: V3[] = new Array(N).fill(0).map((_, i) => {
  const a = random(`c8a${i}`) * Math.PI * 2;
  const d = 900 + random(`c8d${i}`) * 900;
  return {x: Math.cos(a) * d, y: Math.sin(a) * d * 1.4, z: (random(`c8z${i}`) - 0.3) * 1400};
});
const KIND = new Array(N).fill(0).map((_, i) => Math.floor(random(`c8k${i}`) * 3));

export const S8Close: React.FC = () => {
  const f = useCurrentFrame();
  const conv = prog(f, 0, 34, EZ.inOut);
  const ry = f * 0.03;
  const morph = prog(f, 38, 22, EZ.inOut);
  const radius = lerp(300, GLOBE.r, morph);
  const cx = lerp(540, GLOBE.x, morph);
  const cy = lerp(900, GLOBE.y, morph);
  const sphereFade = 1 - prog(f, 52, 12, EZ.inOut);
  const logoGlobe = prog(f, 50, 14, EZ.inOut);
  const hands = prog(f, 56, 16, EZ.out);
  const word = prog(f, 62, 14, EZ.inOut);
  const flash = prog(f, 54, 6) * (1 - prog(f, 60, 18));

  const cam = {cx, cy, fov: 1100};
  const pts = SPH.map((p, i) => {
    const onSphere = rotX(rotY({x: p.x * radius, y: p.y * radius, z: p.z * radius}, ry), 0.3);
    const from = FROM[i];
    const q = lerp3({x: from.x + (540 - cx), y: from.y + (900 - cy), z: from.z}, onSphere, prog(f, (i % 13) * 0.8, 30, EZ.inOut));
    return project(q, cam);
  });

  // Meridianos y paralelos de la esfera de conexiones
  const wire = prog(f, 22, 22, EZ.out);
  const circle = (fn: (t: number) => V3) => {
    let d = '';
    for (let i = 0; i <= 64; i++) {
      const p = project(rotX(rotY(fn((i / 64) * Math.PI * 2), ry), 0.3), cam);
      d += `${i ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    }
    return d;
  };
  const wires: string[] = [];
  for (let m = 0; m < 4; m++) {
    const a = (m / 4) * Math.PI;
    wires.push(circle((t) => ({x: Math.cos(t) * Math.cos(a) * radius, y: Math.sin(t) * radius, z: Math.cos(t) * Math.sin(a) * radius})));
  }
  [-0.5, 0, 0.5].forEach((lat) => {
    const rr = Math.cos(Math.asin(lat)) * radius;
    wires.push(circle((t) => ({x: Math.cos(t) * rr, y: lat * radius, z: Math.sin(t) * rr})));
  });

  return (
    <AbsoluteFill>
      <DeepBackground glowY={36} intensity={1.15} />
      <ParticleField speed={3} opacity={0.5} />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: sphereFade}}>
        <defs>
          <filter id="s8glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g filter="url(#s8glow)">
          {wires.map((d, i) => (
            <path key={i} d={d} fill="none" stroke={C.ice} strokeWidth={2} opacity={0.55 * wire} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - wire} />
          ))}
          {pts.map((p, i) => {
            if (!p.visible) return null;
            const s = p.s;
            const k = KIND[i];
            const settle = conv;
            const size = lerp(k === 1 ? 22 : 12, 5, settle) * s;
            if (k === 1 && settle < 0.95)
              return <rect key={i} x={p.x - size / 4} y={p.y - size} width={size / 2} height={size} rx={2} fill={C.electricSoft} opacity={0.85} />;
            if (k === 2 && settle < 0.95)
              return <rect key={i} x={p.x - size / 2} y={p.y - size / 2} width={size} height={size} rx={size * 0.3} fill="none" stroke={C.ice} strokeWidth={2} />;
            return <circle key={i} cx={p.x} cy={p.y} r={Math.max(2.5, size)} fill="#fff" opacity={0.9} />;
          })}
        </g>
      </svg>

      {/* destello del morphing */}
      <div
        style={{
          position: 'absolute',
          left: GLOBE.x - 400,
          top: GLOBE.y - 400,
          width: 800,
          height: 800,
          borderRadius: 400,
          background: 'radial-gradient(circle, rgba(255,255,255,0.9) 0%, rgba(108,182,255,0.4) 30%, rgba(47,140,255,0) 65%)',
          opacity: flash,
        }}
      />

      {/* logotipo Atlas Path (versión clara para fondo oscuro) */}
      <div style={{position: 'absolute', left: LOGO_LEFT, top: LOGO_TOP, width: LOGO_W, height: 482 * LOGO_K}}>
        <Img src={staticFile('brand/logo-globe-light.png')} style={{position: 'absolute', inset: 0, width: '100%', opacity: logoGlobe, transform: `scale(${lerp(1.12, 1, logoGlobe)})`, transformOrigin: `${(246 / 495) * 100}% ${(129 / 482) * 100}%`, filter: `drop-shadow(0 0 ${lerp(30, 10, logoGlobe)}px rgba(108,182,255,0.6))`}} />
        <Img src={staticFile('brand/logo-hands-light.png')} style={{position: 'absolute', inset: 0, width: '100%', opacity: hands, transform: `translateY(${(1 - hands) * 70}px)`}} />
        <Img src={staticFile('brand/logo-text-light.png')} style={{position: 'absolute', inset: 0, width: '100%', clipPath: `inset(0 ${(1 - word) * 100}% 0 0)`, filter: `blur(${(1 - word) * 6}px)`}} />
      </div>

      <Vignette />

      <TextBlock top={290} gap={4}>
        <Reveal text="TU PRÓXIMA CAMPAÑA" delay={12} size={80} weight={800} exit={null} />
        <Reveal
          text="COMIENZA AQUÍ."
          delay={18}
          size={80}
          weight={800}
          exit={null}
          gradient={`linear-gradient(90deg, ${C.electricSoft}, #FFFFFF)`}
        />
      </TextBlock>

      <TextBlock top={1150}>
        <Reveal text="ATLAS PATH · XALAPA" delay={60} size={38} weight={600} tracking={0.3} color={C.ice} exit={null} />
      </TextBlock>
      <Cta />
    </AbsoluteFill>
  );
};

/** Llamado a la acción con indicador animado de WhatsApp (sin número inventado) */
const Cta: React.FC = () => {
  const f = useCurrentFrame();
  const p = prog(f, 64, 14, EZ.back);
  const sweep = prog(f, 68, 16, EZ.inOut);
  const pulse = ((f - 70) % 30) / 30;
  return (
    <div style={{position: 'absolute', top: 1250, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
      <div
        style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center',
          gap: 26,
          padding: '22px 52px 22px 24px',
          borderRadius: 999,
          background: `linear-gradient(100deg, ${C.electricDeep}, ${C.electric})`,
          boxShadow: '0 20px 60px rgba(47,140,255,0.45), inset 0 2px 0 rgba(255,255,255,0.35)',
          opacity: Math.min(1, p * 1.5),
          transform: `scale(${lerp(0.7, 1, p)})`,
          overflow: 'visible',
        }}
      >
        <div style={{position: 'relative', width: 88, height: 88}}>
          {f > 70 && (
            <div style={{position: 'absolute', inset: 0, borderRadius: 44, border: `4px solid ${C.whatsapp}`, transform: `scale(${1 + pulse * 0.7})`, opacity: (1 - pulse) * 0.9}} />
          )}
          <div style={{position: 'absolute', inset: 0, borderRadius: 44, background: C.whatsapp, display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 24px rgba(37,211,102,0.55)'}}>
            <WhatsAppGlyph size={60} />
          </div>
        </div>
        <div style={{fontFamily: FONT, fontSize: 56, fontWeight: 800, color: '#fff', letterSpacing: '0.04em', whiteSpace: 'nowrap'}}>APARTA TU LUGAR.</div>
        <div style={{position: 'absolute', inset: 0, borderRadius: 999, overflow: 'hidden', pointerEvents: 'none'}}>
          <div style={{position: 'absolute', top: -20, bottom: -20, width: 120, left: `${lerp(-20, 110, sweep)}%`, transform: 'skewX(-20deg)', background: 'linear-gradient(90deg, rgba(255,255,255,0), rgba(255,255,255,0.5), rgba(255,255,255,0))', opacity: sweep > 0 && sweep < 1 ? 1 : 0}} />
        </div>
      </div>
    </div>
  );
};
