import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, lerp, prog} from '../theme';
import {project, rotX, rotY, rotZ, V3} from '../lib/space';
import {DeepBackground, ParticleField, Vignette} from '../components/Atmosphere';
import {Reveal, TextBlock} from '../components/Reveal';
import {Glass} from '../components/Glass';
import {FacebookGlyph, InstagramGlyph} from '../components/Icons';

const CORE = {cx: 540, cy: 1110};

// Icosaedro: estructura digital central
const PHI = (1 + Math.sqrt(5)) / 2;
const ICO: V3[] = [
  [-1, PHI, 0], [1, PHI, 0], [-1, -PHI, 0], [1, -PHI, 0],
  [0, -1, PHI], [0, 1, PHI], [0, -1, -PHI], [0, 1, -PHI],
  [PHI, 0, -1], [PHI, 0, 1], [-PHI, 0, -1], [-PHI, 0, 1],
].map(([x, y, z]) => ({x: x * 62, y: y * 62, z: z * 62}));
const ICO_E: [number, number][] = [];
for (let i = 0; i < 12; i++)
  for (let j = i + 1; j < 12; j++) {
    const d = Math.hypot(ICO[i].x - ICO[j].x, ICO[i].y - ICO[j].y, ICO[i].z - ICO[j].z);
    if (Math.abs(d - 124) < 2) ICO_E.push([i, j]);
  }

const ring = (r: number, n = 72): V3[] =>
  new Array(n + 1).fill(0).map((_, i) => ({x: Math.cos((i / n) * Math.PI * 2) * r, y: 0, z: Math.sin((i / n) * Math.PI * 2) * r}));

export const S2Course: React.FC = () => {
  const f = useCurrentFrame();
  const enter = prog(f, 0, 40, EZ.out);
  const camZ = lerp(-700, 0, enter);
  const cam = {cx: CORE.cx, cy: CORE.cy, z: camZ, fov: 1100};
  const ry = f * 0.018;

  // Suelo en perspectiva
  const floorY = 520;
  const gridLines: React.ReactNode[] = [];
  for (let gx = -2400; gx <= 2400; gx += 240) {
    const a = project({x: gx, y: floorY, z: 150}, cam);
    const b = project({x: gx, y: floorY, z: 4200}, cam);
    gridLines.push(<line key={`v${gx}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={C.electric} strokeWidth={1.2} opacity={0.22} />);
  }
  for (let k = 0; k < 18; k++) {
    let z = (k * 240 - f * 9) % 4320;
    if (z < 0) z += 4320;
    z += 150;
    const a = project({x: -2600, y: floorY, z}, cam);
    const b = project({x: 2600, y: floorY, z}, cam);
    gridLines.push(
      <line key={`h${k}`} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke={C.electricSoft} strokeWidth={1.4 * a.s} opacity={0.3 * Math.min(1, a.s * 1.2)} />,
    );
  }

  const coreScale = prog(f, 8, 26, EZ.back);
  const icoPts = ICO.map((p) => project(rotX(rotY({x: p.x * coreScale, y: p.y * coreScale, z: p.z * coreScale}, ry * 1.6), 0.4), cam));
  const rings = [
    {r: 170, tilt: 0.35, spin: 1, w: 2},
    {r: 215, tilt: -0.6, spin: -0.7, w: 1.4},
    {r: 255, tilt: 1.2, spin: 0.5, w: 1},
  ].map((rg, i) => {
    const pts = ring(rg.r * prog(f, 12 + i * 5, 26, EZ.out)).map((p) => project(rotZ(rotX(rotY(p, ry * rg.spin), rg.tilt), 0.2 * i), cam));
    return {d: pts.map((p, k) => `${k ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(''), w: rg.w};
  });

  // Íconos de Facebook e Instagram orbitando
  const orbitR = 340 * prog(f, 14, 34, EZ.out);
  const tiles = [
    {kind: 'fb', phase: 0},
    {kind: 'ig', phase: Math.PI},
  ].map((t) => {
    const a = f * 0.03 + t.phase + 0.6;
    const p3 = rotX({x: Math.cos(a) * orbitR, y: 0, z: Math.sin(a) * orbitR}, 0.26);
    const p = project(p3, cam);
    return {...t, p, a, front: p3.z < 0};
  });

  const Tile = ({t}: {t: (typeof tiles)[number]}) => {
    const size = 150;
    const bg =
      t.kind === 'fb'
        ? 'linear-gradient(145deg, #3B8BFF, #1460E0)'
        : 'linear-gradient(45deg, #F7B84B 0%, #EE4E5A 40%, #C536A4 70%, #6A4FE0 100%)';
    const yaw = -Math.cos(t.a) * 35;
    const depth = 10;
    return (
      <div
        style={{
          position: 'absolute',
          left: t.p.x,
          top: t.p.y,
          width: size,
          height: size,
          transform: `translate(-50%,-50%) scale(${t.p.s}) perspective(800px) rotateY(${yaw}deg) rotateX(8deg)`,
          opacity: prog(f, 14, 12) * (t.front ? 1 : 0.75),
          filter: t.front ? undefined : 'blur(1.2px) brightness(0.8)',
        }}
      >
        {new Array(depth).fill(0).map((_, i) => (
          <div
            key={i}
            style={{
              position: 'absolute',
              inset: 0,
              borderRadius: 38,
              background: t.kind === 'fb' ? '#0B3E99' : '#5B1F7A',
              transform: `translate(${(depth - i) * 1.4}px, ${(depth - i) * 1.6}px)`,
            }}
          />
        ))}
        <div
          style={{
            position: 'absolute',
            inset: 0,
            borderRadius: 38,
            background: bg,
            boxShadow: '0 0 50px rgba(47,140,255,0.45), inset 0 2px 0 rgba(255,255,255,0.45)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          {t.kind === 'fb' ? <FacebookGlyph size={108} /> : <InstagramGlyph size={112} />}
          <div
            style={{
              position: 'absolute',
              inset: 0,
              borderRadius: 38,
              background: 'linear-gradient(160deg, rgba(255,255,255,0.35), rgba(255,255,255,0) 45%)',
            }}
          />
        </div>
      </div>
    );
  };

  const coreSvg = (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
      <defs>
        <filter id="s2glow" x="-50%" y="-50%" width="200%" height="200%">
          <feGaussianBlur stdDeviation="5" result="b" />
          <feMerge>
            <feMergeNode in="b" />
            <feMergeNode in="SourceGraphic" />
          </feMerge>
        </filter>
        <radialGradient id="s2core">
          <stop offset="0%" stopColor={C.electricSoft} stopOpacity="0.75" />
          <stop offset="60%" stopColor={C.electric} stopOpacity="0.12" />
          <stop offset="100%" stopColor={C.electric} stopOpacity="0" />
        </radialGradient>
      </defs>
      <circle cx={CORE.cx} cy={CORE.cy} r={240 * coreScale} fill="url(#s2core)" opacity={0.55 + 0.1 * Math.sin(f / 6)} />
      <g filter="url(#s2glow)">
        {rings.map((r, i) => (
          <path key={i} d={r.d} fill="none" stroke={i === 0 ? C.electricSoft : C.ice} strokeWidth={r.w} opacity={0.6} />
        ))}
        {ICO_E.map(([a, b], i) => (
          <line key={i} x1={icoPts[a].x} y1={icoPts[a].y} x2={icoPts[b].x} y2={icoPts[b].y} stroke={C.white} strokeWidth={1.6} opacity={0.75} />
        ))}
        {icoPts.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r={4.5 * p.s} fill={C.white} />
        ))}
      </g>
    </svg>
  );

  return (
    <AbsoluteFill>
      <DeepBackground glowY={56} intensity={1.3} />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <defs>
          <linearGradient id="s2fade" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0" stopColor="#000" stopOpacity="1" />
            <stop offset="1" stopColor="#000" stopOpacity="0" />
          </linearGradient>
        </defs>
        <g opacity={prog(f, 0, 20)}>{gridLines}</g>
        <rect x={0} y={1180} width={1080} height={120} fill={C.electric} opacity={0.08} />
      </svg>
      <ParticleField speed={5} opacity={0.6} />
      {tiles.filter((t) => !t.front).map((t) => <Tile key={t.kind} t={t} />)}
      {coreSvg}
      {tiles.filter((t) => t.front).map((t) => <Tile key={t.kind} t={t} />)}

      <AdPanel />
      <Vignette />

      <TextBlock top={300} gap={6}>
        <Reveal text="META ADS" delay={6} size={172} weight={800} tracking={0.0} />
        <Reveal
          text="2026"
          delay={11}
          size={172}
          weight={800}
          tracking={0.06}
          gradient={`linear-gradient(90deg, ${C.electricSoft}, ${C.white} 55%, ${C.ice})`}
          style={{filter: 'drop-shadow(0 0 26px rgba(47,140,255,0.5))'}}
        />
        <div style={{height: 22}} />
        <Reveal text="FACEBOOK + INSTAGRAM ADS" delay={20} size={50} weight={600} tracking={0.1} color={C.ice} />
        <div style={{height: 22}} />
        <Pill delay={28} />
      </TextBlock>
    </AbsoluteFill>
  );
};

const Pill: React.FC<{delay: number}> = ({delay}) => {
  const f = useCurrentFrame();
  const p = prog(f, delay, 14);
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  return (
    <div
      style={{
        padding: '16px 34px',
        borderRadius: 999,
        border: '1.5px solid rgba(170,210,255,0.4)',
        background: 'rgba(47,140,255,0.14)',
        fontFamily: FONT,
        fontSize: 34,
        fontWeight: 600,
        letterSpacing: '0.16em',
        color: C.white,
        whiteSpace: 'nowrap',
        opacity: p * (1 - pe),
        transform: `scale(${lerp(0.9, 1, p)}) translateY(${-pe * 20}px)`,
        clipPath: `inset(0 ${(1 - p) * 50}% 0 ${(1 - p) * 50}% round 999px)`,
      }}
    >
      CURSO PRESENCIAL · ATLAS PATH
    </div>
  );
};

/** Interfaz conceptual del Administrador de anuncios con campañas que se activan */
const AdPanel: React.FC = () => {
  const f = useCurrentFrame();
  const p = prog(f, 30, 20, EZ.out);
  const rows = [
    {name: 'Reconocimiento', on: 40, bars: [0.4, 0.55, 0.5, 0.7, 0.8]},
    {name: 'Tráfico', on: 55, bars: [0.3, 0.45, 0.6, 0.58, 0.75]},
    {name: 'Mensajes', on: 70, bars: [0.35, 0.5, 0.62, 0.8, 0.92]},
  ];
  return (
    <Glass
      style={{
        left: 120,
        width: 840,
        top: 1360,
        height: 250,
        padding: '22px 30px',
        opacity: p,
        transform: `translateY(${(1 - p) * 80}px) perspective(1200px) rotateX(${(1 - p) * 30 + 8}deg)`,
        transformOrigin: '50% 100%',
      }}
    >
      <div style={{display: 'flex', justifyContent: 'space-between', fontFamily: FONT, color: C.ice, fontSize: 21, letterSpacing: '0.14em', fontWeight: 600, marginBottom: 14}}>
        <span>ADMINISTRADOR DE ANUNCIOS</span>
        <span style={{color: C.electricSoft}}>● EN VIVO</span>
      </div>
      {rows.map((r, i) => {
        const on = prog(f, r.on, 8);
        return (
          <div key={i} style={{display: 'flex', alignItems: 'center', height: 58, borderTop: '1px solid rgba(170,210,255,0.14)', gap: 20}}>
            <div style={{width: 64, height: 34, borderRadius: 20, background: on > 0.5 ? C.electric : 'rgba(255,255,255,0.18)', position: 'relative', boxShadow: on > 0.5 ? `0 0 18px ${C.electric}` : undefined}}>
              <div style={{position: 'absolute', top: 4, left: lerp(4, 34, on), width: 26, height: 26, borderRadius: 13, background: C.white}} />
            </div>
            <div style={{flex: 1, fontFamily: FONT, fontSize: 28, fontWeight: 500, color: C.white}}>{r.name}</div>
            <div style={{display: 'flex', alignItems: 'flex-end', gap: 7, height: 40}}>
              {r.bars.map((b, k) => (
                <div key={k} style={{width: 14, borderRadius: 3, height: 40 * b * prog(f, r.on + 4 + k * 2, 10), background: `linear-gradient(0deg, ${C.electric}, ${C.electricSoft})`}} />
              ))}
            </div>
          </div>
        );
      })}
    </Glass>
  );
};
