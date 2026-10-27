import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, lerp, prog} from '../theme';
import {LightBackground} from '../components/Atmosphere';
import {Reveal} from '../components/Reveal';

const CARD = {x: 90, y: 590, w: 900, h: 680, r: 56};
const DIGIT_H = 240;
// Precio exacto del folleto: $3,490 MXN · IVA incluido (antes $4,900)
const TARGET = ['3', ',', '4', '9', '0'];
export const LAND = [28, 0, 31, 34, 37];

const RollingDigit: React.FC<{target: number; land: number; spins: number}> = ({target, land, spins}) => {
  const f = useCurrentFrame();
  const t = prog(f, 6, land - 6, EZ.out);
  const total = spins * 10 + target;
  const pos = t * total;
  const vel = prog(f + 1, 6, land - 6, EZ.out) * total - pos;
  return (
    <div style={{height: DIGIT_H, overflow: 'hidden', position: 'relative', width: '0.6em'}}>
      <div
        style={{
          transform: `translateY(${-pos * DIGIT_H}px)`,
          filter: vel > 0.05 ? `blur(${Math.min(10, vel * 9)}px)` : undefined,
        }}
      >
        {new Array(total + 1).fill(0).map((_, i) => (
          <div key={i} style={{height: DIGIT_H, lineHeight: `${DIGIT_H}px`, textAlign: 'center'}}>
            {i % 10}
          </div>
        ))}
      </div>
    </div>
  );
};

export const S7Price: React.FC = () => {
  const f = useCurrentFrame();
  const card = prog(f, 0, 18, EZ.out);
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  const outline = prog(f, 10, 34, EZ.inOut);
  const strike = prog(f, 48, 12, EZ.inOut);
  const per = 2 * (CARD.w + CARD.h);

  return (
    <AbsoluteFill>
      <LightBackground glowY={48} />
      {/* arcos de globo inspirados en el logotipo */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        <g transform={`rotate(${f * 0.08} 540 950)`} opacity={0.5}>
          {[0, 1, 2, 3].map((i) => (
            <ellipse key={i} cx={540} cy={950} rx={760 - i * 150} ry={760} fill="none" stroke={C.electric} strokeWidth={1.4} opacity={0.12} />
          ))}
          <circle cx={540} cy={950} r={760} fill="none" stroke={C.electric} strokeWidth={1.6} opacity={0.16} />
          {[-380, 0, 380].map((y) => (
            <line key={y} x1={-200} x2={1280} y1={950 + y} y2={950 + y} stroke={C.electric} strokeWidth={1.2} opacity={0.1} />
          ))}
        </g>
        {[{x: 150, y: 380, r: 90}, {x: 940, y: 1500, r: 130}, {x: 960, y: 420, r: 46}].map((o, i) => (
          <circle key={i} cx={o.x} cy={o.y + Math.sin(f / 25 + i) * 10} r={o.r} fill={C.ice} opacity={0.35} />
        ))}
      </svg>

      {/* tarjeta de precio */}
      <div
        style={{
          position: 'absolute',
          left: CARD.x,
          top: CARD.y,
          width: CARD.w,
          height: CARD.h,
          borderRadius: CARD.r,
          background: 'linear-gradient(165deg, rgba(255,255,255,0.95), rgba(234,243,252,0.8))',
          boxShadow: '0 50px 110px rgba(16,46,66,0.2), inset 0 2px 0 #fff',
          opacity: card * (1 - pe),
          transform: `perspective(1600px) rotateX(${(1 - card) * 16}deg) translateY(${(1 - card) * 60}px)`,
        }}
      />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: 1 - pe}}>
        <defs>
          <filter id="s7glow" x="-10%" y="-10%" width="120%" height="120%">
            <feGaussianBlur stdDeviation="7" result="b" />
            <feMerge>
              <feMergeNode in="b" />
              <feMergeNode in="SourceGraphic" />
            </feMerge>
          </filter>
          <linearGradient id="s7line" x1="0" x2="1" y1="0" y2="1">
            <stop offset="0" stopColor={C.electricSoft} />
            <stop offset="1" stopColor={C.electricDeep} />
          </linearGradient>
        </defs>
        <rect x={CARD.x} y={CARD.y} width={CARD.w} height={CARD.h} rx={CARD.r} fill="none" stroke={C.electric} strokeOpacity={0.25} strokeWidth={2} pathLength={1} strokeDasharray={1} strokeDashoffset={1 - outline} />
        {/* destello que recorre el contorno */}
        <rect
          x={CARD.x}
          y={CARD.y}
          width={CARD.w}
          height={CARD.h}
          rx={CARD.r}
          fill="none"
          stroke="url(#s7line)"
          strokeWidth={5}
          strokeLinecap="round"
          strokeDasharray={`${per * 0.16} ${per * 0.84}`}
          strokeDashoffset={-per * (0.12 + f / 110)}
          filter="url(#s7glow)"
          opacity={prog(f, 12, 12)}
        />
      </svg>

      <div style={{position: 'absolute', left: CARD.x, width: CARD.w, top: CARD.y + 84, display: 'flex', flexDirection: 'column', alignItems: 'center', fontFamily: FONT}}>
        <div
          style={{
            padding: '16px 38px',
            borderRadius: 999,
            background: C.navy,
            color: '#fff',
            fontSize: 40,
            fontWeight: 700,
            letterSpacing: '0.16em',
            opacity: prog(f, 8, 12) * (1 - pe),
            clipPath: `inset(0 ${(1 - prog(f, 8, 16)) * 50}% round 999px)`,
          }}
        >
          PRIMERA GENERACIÓN
        </div>

        <div style={{height: 46}} />
        <div style={{position: 'relative', fontSize: 46, fontWeight: 500, color: C.navy600, opacity: prog(f, 40, 10) * (1 - pe), letterSpacing: '0.04em'}}>
          ANTES{' '}
          <span style={{position: 'relative'}}>
            $4,900
            <span
              style={{
                position: 'absolute',
                left: -6,
                top: '52%',
                height: 4,
                width: `calc(${strike * 100}% + 12px)`,
                background: '#E0475B',
                borderRadius: 2,
                transform: 'rotate(-8deg)',
              }}
            />
          </span>
        </div>

        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            fontSize: 236,
            fontWeight: 800,
            color: C.navy,
            letterSpacing: '-0.02em',
            height: DIGIT_H,
            marginTop: 6,
            opacity: prog(f, 4, 8) * (1 - pe),
            fontVariantNumeric: 'tabular-nums',
          }}
        >
          <div style={{height: DIGIT_H, lineHeight: `${DIGIT_H}px`, fontSize: 150, alignSelf: 'flex-start', marginRight: 6, color: C.electricDeep}}>$</div>
          {TARGET.map((d, i) =>
            d === ',' ? (
              <div key={i} style={{height: DIGIT_H, lineHeight: `${DIGIT_H}px`, width: '0.24em', textAlign: 'center'}}>
                ,
              </div>
            ) : (
              <RollingDigit key={i} target={Number(d)} land={LAND[i]} spins={2 + i} />
            ),
          )}
        </div>
        <div style={{display: 'flex', gap: 22, alignItems: 'center', marginTop: 12, opacity: 1 - pe}}>
          <Reveal text="MXN" delay={36} size={60} weight={700} color={C.electricDeep} tracking={0.1} exit={null} />
          <div style={{width: 3, height: 50, background: C.navy, opacity: 0.2 * prog(f, 40, 8)}} />
          <Reveal text="IVA INCLUIDO" delay={40} size={60} weight={700} color={C.navy} tracking={0.1} exit={null} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
