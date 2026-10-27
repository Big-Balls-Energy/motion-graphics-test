import React from 'react';
import {AbsoluteFill, random, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, lerp, prog} from '../theme';
import {fibonacciSphere, lerp3, project, rotX, rotY, V3} from '../lib/space';
import {DeepBackground, ParticleField, Vignette} from '../components/Atmosphere';
import {Reveal, TextBlock} from '../components/Reveal';

// Red tridimensional de datos: nodos aleatorios que se reorganizan en una esfera
const N = 96;
const START: V3[] = new Array(N).fill(0).map((_, i) => ({
  x: (random(`s1x${i}`) - 0.5) * 2200,
  y: (random(`s1y${i}`) - 0.5) * 3400,
  z: random(`s1z${i}`) * 2600 + 200,
}));
const SPHERE = fibonacciSphere(N, 980);
const EDGES: [number, number][] = (() => {
  const e: [number, number][] = [];
  for (let i = 0; i < N; i++) {
    const d = START.map((p, j) => ({j, d: Math.hypot(p.x - START[i].x, p.y - START[i].y, p.z - START[i].z)}))
      .filter((o) => o.j !== i)
      .sort((a, b) => a.d - b.d);
    for (let k = 0; k < 2; k++) {
      const j = d[k].j;
      if (!e.some(([a, b]) => (a === j && b === i) || (a === i && b === j))) e.push([i, j]);
    }
  }
  return e;
})();

const CHIPS = [
  {label: 'CTR', value: '2.4%', p: {x: -330, y: -560, z: 150}},
  {label: 'CPC', value: '$3.80', p: {x: 360, y: -380, z: 420}},
  {label: 'ROAS', value: '3.2x', p: {x: -380, y: 430, z: 560}},
  {label: 'ALCANCE', value: '18.4K', p: {x: 330, y: 600, z: 300}},
  {label: 'CONV.', value: '126', p: {x: 420, y: 80, z: 700}},
];

export const S1Hook: React.FC = () => {
  const f = useCurrentFrame();
  // Cámara: vuelo a través de la red
  const fly = prog(f, 0, 62, EZ.inOut);
  const camZ = lerp(-500, 900, fly);
  const reorg = prog(f, 30, 50, EZ.inOut);
  const rot = f * 0.006;
  const build = prog(f, 0, 34, EZ.outSoft);

  const pts = START.map((p, i) => {
    const sp = rotX(rotY(SPHERE[i], rot), 0.25);
    const target = {x: sp.x, y: sp.y - 60, z: sp.z + 2300};
    const q = lerp3(p, target, reorg);
    return project(q, {z: camZ, cy: 960});
  });
  const dim = lerp(1, 0.6, prog(f, 40, 30));

  return (
    <AbsoluteFill>
      <DeepBackground glowY={48} intensity={1.1} />
      <ParticleField speed={14} opacity={0.8} />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: dim}}>
        <defs>
          <filter id="s1glow" x="-50%" y="-50%" width="200%" height="200%">
            <feGaussianBlur stdDeviation="4" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <g filter="url(#s1glow)">
          {EDGES.map(([a, b], k) => {
            const pa = pts[a];
            const pb = pts[b];
            if (!pa.visible || !pb.visible) return null;
            const t = Math.max(0, Math.min(1, build * 1.6 - (k / EDGES.length) * 0.6));
            if (t <= 0) return null;
            const depth = Math.min(1, Math.min(pa.s, pb.s) * 1.3);
            return (
              <line
                key={k}
                x1={pa.x}
                y1={pa.y}
                x2={lerp(pa.x, pb.x, t)}
                y2={lerp(pa.y, pb.y, t)}
                stroke={C.electricSoft}
                strokeWidth={Math.max(0.6, 1.6 * depth)}
                opacity={0.55 * depth}
              />
            );
          })}
          {pts.map((p, i) => {
            if (!p.visible) return null;
            const appear = prog(f, (i / N) * 24, 10);
            const r = (3 + (i % 5 === 0 ? 4 : 0)) * p.s * 1.4 * appear;
            return (
              <g key={i}>
                <circle cx={p.x} cy={p.y} r={r * 3.2} fill={C.electric} opacity={0.18 * appear} />
                <circle cx={p.x} cy={p.y} r={r} fill={i % 5 === 0 ? C.white : C.ice} opacity={Math.min(1, p.s * 1.5)} />
              </g>
            );
          })}
        </g>
      </svg>

      {/* Indicadores de anuncios que pasan junto a la cámara */}
      {CHIPS.map((c, i) => {
        const p = project(c.p, {z: camZ});
        if (!p.visible || p.s > 2.6) return null;
        const a = Math.min(1, (2.6 - p.s) / 1.0) * prog(f, 2 + i * 3, 10) * (1 - prog(f, 30, 14));
        return (
          <div
            key={i}
            style={{
              position: 'absolute',
              left: p.x,
              top: p.y,
              transform: `translate(-50%,-50%) scale(${p.s})`,
              opacity: a,
              filter: p.s > 1.6 ? `blur(${(p.s - 1.6) * 3}px)` : undefined,
              padding: '14px 22px',
              borderRadius: 18,
              background: 'linear-gradient(160deg, rgba(120,175,240,0.22), rgba(16,46,66,0.55))',
              border: '1.5px solid rgba(170,210,255,0.3)',
              fontFamily: FONT,
              color: C.white,
              display: 'flex',
              gap: 12,
              alignItems: 'baseline',
              whiteSpace: 'nowrap',
            }}
          >
            <span style={{fontSize: 20, letterSpacing: '0.18em', color: C.ice, fontWeight: 600}}>{c.label}</span>
            <span style={{fontSize: 32, fontWeight: 700}}>{c.value}</span>
          </div>
        );
      })}

      {/* Zona de lectura protegida */}
      <AbsoluteFill
        style={{
          background: 'radial-gradient(60% 26% at 50% 50%, rgba(3,12,22,0.72) 0%, rgba(3,12,22,0) 100%)',
          opacity: prog(f, 6, 20),
        }}
      />
      <Vignette />

      <TextBlock top={600} gap={34}>
        <Reveal text="DEJA DE IMPROVISAR." delay={4} size={70} weight={600} tracking={0.05} color={C.ice} />
        <div style={{height: 40}} />
        <Reveal text="EMPIEZA A" delay={28} size={104} weight={700} />
        <Dominar />
        <Reveal text="META ADS." delay={40} size={104} weight={700} />
      </TextBlock>
    </AbsoluteFill>
  );
};

/** Palabra protagonista con brillo de barrido único y subrayado luminoso */
const Dominar: React.FC = () => {
  const f = useCurrentFrame();
  const sweep = prog(f, 56, 26, EZ.inOut);
  const line = prog(f, 46, 20, EZ.out);
  const pulse = prog(f, 34, 14) * (1 - prog(f, 48, 30));
  return (
    <div style={{position: 'relative'}}>
      <Reveal
        text="DOMINAR"
        delay={34}
        size={178}
        weight={800}
        tracking={0.01}
        dur={14}
        gradient={`linear-gradient(100deg, #FFFFFF 0%, #FFFFFF ${sweep * 120 - 30}%, ${C.electricSoft} ${sweep * 120 - 10}%, #FFFFFF ${sweep * 120 + 10}%, #DCEBFF 100%)`}
        style={{filter: `drop-shadow(0 0 ${18 + pulse * 30}px rgba(47,140,255,0.55))`}}
      />
      <div
        style={{
          position: 'absolute',
          left: '50%',
          bottom: -6,
          height: 8,
          width: 760 * line,
          transform: 'translateX(-50%)',
          borderRadius: 8,
          background: `linear-gradient(90deg, rgba(47,140,255,0), ${C.electric}, ${C.electricSoft}, rgba(47,140,255,0))`,
          boxShadow: `0 0 24px ${C.electric}`,
          opacity: line * (1 - prog(f, 134, 9)),
        }}
      />
    </div>
  );
};
