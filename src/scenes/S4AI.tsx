import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, lerp, prog} from '../theme';
import {project, rotX, rotY, V3} from '../lib/space';
import {DeepBackground, ParticleField, Vignette} from '../components/Atmosphere';
import {Reveal, TextBlock} from '../components/Reveal';
import {Glass} from '../components/Glass';

const CENTER = {cx: 540, cy: 1110};
const LAYERS = [4, 6, 6, 4];
const LX = [-400, -135, 135, 400];
const LR = [150, 235, 235, 150];

const NODES: {p: V3; l: number}[] = [];
LAYERS.forEach((n, l) => {
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2 + l * 0.4;
    NODES.push({p: {x: LX[l], y: Math.cos(a) * LR[l], z: Math.sin(a) * LR[l]}, l});
  }
});
const EDGES: {a: number; b: number; l: number}[] = [];
NODES.forEach((na, i) =>
  NODES.forEach((nb, j) => {
    if (nb.l === na.l + 1) EDGES.push({a: i, b: j, l: na.l});
  }),
);

export const S4AI: React.FC = () => {
  const f = useCurrentFrame();
  const ry = 0.55 * Math.sin(f / 55) + f * 0.004 - 0.2;
  const camZ = lerp(500, 0, prog(f, 0, 50, EZ.out));
  const cam = {cx: CENTER.cx, cy: CENTER.cy, z: camZ};
  const pts = NODES.map((n) => project(rotX(rotY(n.p, ry), 0.18), cam));

  // Onda de activación que recorre la red
  const wave = (f - 64) / 13; // capas por frame
  const waveLocal = wave < 0 ? -10 : wave % 5;

  const ring = prog(f, 118, 30, EZ.out);

  return (
    <AbsoluteFill>
      <DeepBackground glowY={58} intensity={1.2} />
      <ParticleField speed={4} opacity={0.55} />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <defs>
          <filter id="s4glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="5" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <radialGradient id="s4node">
            <stop offset="0" stopColor="#FFFFFF" />
            <stop offset="0.45" stopColor={C.electricSoft} />
            <stop offset="1" stopColor={C.electric} stopOpacity="0" />
          </radialGradient>
        </defs>
        <circle cx={CENTER.cx} cy={CENTER.cy} r={420} fill={C.electric} opacity={0.06} />
        <g filter="url(#s4glow)">
          {EDGES.map((e, i) => {
            const pa = pts[e.a];
            const pb = pts[e.b];
            const t = prog(f, 22 + e.l * 9 + (i % 7), 16, EZ.out);
            if (t <= 0) return null;
            const depth = Math.min(1, (pa.s + pb.s) / 2.2);
            const u = waveLocal - e.l; // posición del pulso sobre la arista
            const hot = u > 0 && u < 1;
            const u0 = Math.max(0, u - 0.35);
            return (
              <g key={i}>
                <line
                  x1={pa.x}
                  y1={pa.y}
                  x2={lerp(pa.x, pb.x, t)}
                  y2={lerp(pa.y, pb.y, t)}
                  stroke={C.electricSoft}
                  strokeWidth={1.2}
                  opacity={0.28 * depth}
                />
                {hot && (
                  <line
                    x1={lerp(pa.x, pb.x, u0)}
                    y1={lerp(pa.y, pb.y, u0)}
                    x2={lerp(pa.x, pb.x, Math.min(1, u))}
                    y2={lerp(pa.y, pb.y, Math.min(1, u))}
                    stroke="#fff"
                    strokeWidth={3}
                    strokeLinecap="round"
                    opacity={0.95 * depth}
                  />
                )}
              </g>
            );
          })}
          {pts.map((p, i) => {
            const l = NODES[i].l;
            const a = prog(f, 6 + l * 7 + (i % 4) * 2, 12, EZ.back);
            const lit = Math.max(0, 1 - Math.abs(waveLocal - l) * 1.6);
            const r = (9 + lit * 6) * p.s * a;
            return (
              <g key={i}>
                <circle cx={p.x} cy={p.y} r={r * 3.4} fill="url(#s4node)" opacity={0.35 + lit * 0.5} />
                <circle cx={p.x} cy={p.y} r={r} fill={lit > 0.3 ? '#fff' : C.ice} stroke={C.electric} strokeWidth={2} />
              </g>
            );
          })}
        </g>
        {/* conexiones hacia los paneles de salida */}
        {[220, 540, 860].map((x, i) => {
          const t = prog(f, 54 + i * 4, 18, EZ.inOut);
          return (
            <path
              key={i}
              d={`M${CENTER.cx},${CENTER.cy + 150} C${CENTER.cx},${CENTER.cy + 260} ${x},${1300} ${x},${1395}`}
              fill="none"
              stroke={C.electricSoft}
              strokeWidth={2}
              strokeDasharray="6 10"
              strokeDashoffset={-f * 1.5}
              opacity={0.55 * t}
              pathLength={undefined}
              style={{clipPath: `inset(0 0 ${(1 - t) * 100}% 0)`}}
            />
          );
        })}
        {/* onda luminosa de salida */}
        {ring > 0 && (
          <g>
            <circle cx={CENTER.cx} cy={CENTER.cy} r={ring * 1500} fill="none" stroke={C.electricSoft} strokeWidth={40 * (1 - ring) + 4} opacity={1 - ring} filter="url(#s4glow)" />
            <circle cx={CENTER.cx} cy={CENTER.cy} r={ring * 1200} fill="none" stroke="#fff" strokeWidth={6} opacity={(1 - ring) * 0.8} />
          </g>
        )}
      </svg>

      <Panels />
      <Vignette />

      <TextBlock top={300} gap={4}>
        <Reveal text="ADVANTAGE+ · ANDROMEDA" delay={4} size={54} weight={700} tracking={0.1} color={C.ice} />
        <div style={{height: 34}} />
        <Reveal text="INTELIGENCIA" delay={14} size={112} weight={800} />
        <Reveal text="ARTIFICIAL" delay={18} size={112} weight={800} />
        <div style={{display: 'flex', gap: 30}}>
          <Reveal text="CON" delay={22} size={112} weight={800} />
          <Reveal
            text="CLAUDE"
            delay={25}
            size={112}
            weight={800}
            gradient={`linear-gradient(90deg, ${C.electricSoft}, #FFFFFF)`}
            style={{filter: 'drop-shadow(0 0 22px rgba(47,140,255,0.6))'}}
          />
        </div>
      </TextBlock>
    </AbsoluteFill>
  );
};

/** Interfaces flotantes: análisis, organización y reportes */
const Panels: React.FC = () => {
  const f = useCurrentFrame();
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  const spark = [0.3, 0.42, 0.36, 0.55, 0.5, 0.68, 0.62, 0.8, 0.9];
  const data = [
    {
      title: 'ANÁLISIS',
      body: (t: number) => (
        <svg width={250} height={86}>
          <path
            d={spark.map((v, i) => `${i ? 'L' : 'M'}${i * 30 + 5},${80 - v * 72}`).join('')}
            fill="none"
            stroke={C.electricSoft}
            strokeWidth={4}
            strokeLinejoin="round"
            pathLength={1}
            strokeDasharray={1}
            strokeDashoffset={1 - t}
          />
          <circle cx={8 * 30 + 5} cy={80 - 0.9 * 72} r={7 * t} fill="#fff" />
        </svg>
      ),
    },
    {
      title: 'ORGANIZA',
      body: (t: number) => (
        <div style={{display: 'flex', flexDirection: 'column', gap: 12, paddingTop: 6}}>
          {[0.9, 0.7, 0.8].map((w, i) => (
            <div key={i} style={{display: 'flex', alignItems: 'center', gap: 10}}>
              <div style={{width: 16, height: 16, borderRadius: 5, background: i < Math.round(t * 3) ? C.electric : 'rgba(255,255,255,0.2)'}} />
              <div style={{height: 10, width: 200 * w * Math.min(1, t * 1.3), borderRadius: 5, background: 'rgba(191,221,251,0.55)'}} />
            </div>
          ))}
        </div>
      ),
    },
    {
      title: 'REPORTE',
      body: (t: number) => (
        <div style={{display: 'flex', alignItems: 'flex-end', gap: 12, height: 86}}>
          {[0.35, 0.55, 0.45, 0.75, 0.95].map((v, i) => (
            <div
              key={i}
              style={{
                width: 32,
                height: 84 * v * prog(t * 30, i * 3, 14, EZ.out),
                borderRadius: 6,
                background: i === 4 ? `linear-gradient(0deg, ${C.electric}, #fff)` : `linear-gradient(0deg, ${C.electricDeep}, ${C.electricSoft})`,
              }}
            />
          ))}
        </div>
      ),
    },
  ];
  return (
    <>
      {data.map((d, i) => {
        const p = prog(f, 62 + i * 6, 16, EZ.back);
        const t = prog(f, 70 + i * 6, 30, EZ.out);
        const bob = Math.sin(f / 18 + i * 1.7) * 6;
        return (
          <Glass
            key={d.title}
            radius={24}
            style={{
              left: 60 + i * 330,
              top: 1395 + bob + (i === 1 ? 30 : 0),
              width: 300,
              height: 172,
              padding: '18px 24px',
              opacity: Math.min(1, p) * (1 - pe),
              transform: `translateY(${(1 - p) * 60}px) scale(${lerp(0.9, 1, Math.min(1, p))})`,
            }}
          >
            <div style={{fontFamily: FONT, color: C.ice, fontSize: 20, fontWeight: 600, letterSpacing: '0.2em', marginBottom: 10}}>{d.title}</div>
            {d.body(t)}
          </Glass>
        );
      })}
    </>
  );
};
