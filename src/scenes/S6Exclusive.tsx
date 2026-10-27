import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, lerp, prog} from '../theme';
import {project, rotX, rotY} from '../lib/space';
import {DeepBackground, ParticleField, Vignette} from '../components/Atmosphere';
import {Reveal, TextBlock} from '../components/Reveal';

const CENTER = {cx: 540, cy: 975};
const R = 440;
export const LIGHT_AT = (k: number) => 30 + k * 7;

export const S6Exclusive: React.FC = () => {
  const f = useCurrentFrame();
  const orbit = -f * 0.011 + 0.5; // movimiento orbital de cámara
  const tilt = lerp(0.62, 0.5, prog(f, 0, 150, EZ.inOut));
  const grow = prog(f, 6, 30, EZ.out);
  const cam = {cx: CENTER.cx, cy: CENTER.cy, fov: 1200};
  const P = (a: number, r = R) => project(rotX(rotY({x: Math.cos(a) * r * grow, y: 0, z: Math.sin(a) * r * grow}, orbit), tilt), cam);

  const dots = new Array(10).fill(0).map((_, k) => {
    const a = (k / 10) * Math.PI * 2 - Math.PI / 2;
    const p = P(a);
    const lit = prog(f, LIGHT_AT(k), 8, EZ.out);
    return {k, a, p, lit};
  });

  // Arco iluminado progresivo
  const arcEnd = prog(f, LIGHT_AT(0), LIGHT_AT(9) - LIGHT_AT(0), (t) => t);
  const ringPath = (r: number, from = 0, to = 1, n = 120) => {
    let d = '';
    for (let i = 0; i <= n; i++) {
      const t = from + (to - from) * (i / n);
      const p = P(t * Math.PI * 2 - Math.PI / 2, r);
      d += `${i ? 'L' : 'M'}${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    }
    return d;
  };

  const back = dots.filter((d) => d.p.z > 0);
  const front = dots.filter((d) => d.p.z <= 0);
  const Dot = ({d}: {d: (typeof dots)[number]}) => {
    const s = d.p.s;
    return (
      <g>
        <circle cx={d.p.x} cy={d.p.y} r={46 * s * d.lit} fill="url(#s6halo)" opacity={d.lit} />
        <circle cx={d.p.x} cy={d.p.y} r={15 * s} fill={d.lit > 0.5 ? '#fff' : '#22415C'} stroke={d.lit > 0.5 ? C.electricSoft : '#3A5D7C'} strokeWidth={3} />
      </g>
    );
  };

  const big = prog(f, 20, 18, EZ.out);
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  const yaw = Math.sin(orbit) * 10;

  return (
    <AbsoluteFill>
      <DeepBackground glowY={52} intensity={0.8} base="#041321" />
      <AbsoluteFill style={{background: '#01060C', opacity: prog(f, 0, 70, EZ.inOut) * 0.5}} />
      <AbsoluteFill style={{background: 'radial-gradient(40% 25% at 50% 52%, rgba(47,140,255,0.22), rgba(0,0,0,0))'}} />
      <ParticleField speed={2} opacity={0.35} />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="s6halo">
            <stop offset="0" stopColor="#fff" stopOpacity="0.9" />
            <stop offset="0.3" stopColor={C.electricSoft} stopOpacity="0.55" />
            <stop offset="1" stopColor={C.electric} stopOpacity="0" />
          </radialGradient>
          <filter id="s6glow" x="-20%" y="-20%" width="140%" height="140%">
            <feGaussianBlur stdDeviation="6" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
        </defs>
        <path d={ringPath(R * 1.22)} fill="none" stroke={C.electric} strokeWidth={1} opacity={0.18} />
        <path d={ringPath(R * 0.82)} fill="none" stroke={C.ice} strokeWidth={1} opacity={0.12} strokeDasharray="4 10" />
        <path d={ringPath(R)} fill="none" stroke="#3A5D7C" strokeWidth={2} opacity={0.6} />
        {arcEnd > 0 && <path d={ringPath(R, 0, arcEnd * 0.9 + 0.0001)} fill="none" stroke={C.electricSoft} strokeWidth={4} filter="url(#s6glow)" />}
        {back.map((d) => (
          <Dot key={d.k} d={d} />
        ))}
      </svg>

      {/* número protagonista */}
      <div
        style={{
          position: 'absolute',
          left: 0,
          right: 0,
          top: CENTER.cy - 230,
          display: 'flex',
          justifyContent: 'center',
          opacity: big * (1 - pe),
          transform: `perspective(1400px) rotateY(${yaw}deg) scale(${lerp(0.82, 1, big)})`,
          filter: big < 1 ? `blur(${(1 - big) * 14}px)` : undefined,
        }}
      >
        <div
          style={{
            fontFamily: FONT,
            fontWeight: 800,
            fontSize: 400,
            lineHeight: 1,
            letterSpacing: '-0.03em',
            color: 'transparent',
            backgroundImage: `linear-gradient(180deg, #FFFFFF 10%, ${C.ice} 60%, ${C.electricSoft} 100%)`,
            WebkitBackgroundClip: 'text',
            backgroundClip: 'text',
            filter: 'drop-shadow(0 0 40px rgba(47,140,255,0.55))',
          }}
        >
          10
        </div>
      </div>

      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <defs>
          <radialGradient id="s6halo">
            <stop offset="0" stopColor="#fff" stopOpacity="0.9" />
            <stop offset="0.3" stopColor={C.electricSoft} stopOpacity="0.55" />
            <stop offset="1" stopColor={C.electric} stopOpacity="0" />
          </radialGradient>
        </defs>
        {front.map((d) => (
          <Dot key={d.k} d={d} />
        ))}
      </svg>
      <Vignette strength={0.7} />

      <TextBlock top={300}>
        <Reveal text="SOLO 10 LUGARES." delay={6} size={104} weight={800} />
      </TextBlock>
      <TextBlock top={1395} gap={4}>
        <Reveal text="APRENDE EN UN" delay={40} size={60} weight={600} tracking={0.06} color={C.ice} />
        <Reveal text="GRUPO REDUCIDO." delay={44} size={60} weight={600} tracking={0.06} color={C.ice} />
      </TextBlock>
    </AbsoluteFill>
  );
};
