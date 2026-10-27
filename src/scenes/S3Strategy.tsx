import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, lerp, prog} from '../theme';
import {LightBackground} from '../components/Atmosphere';
import {Reveal, TextBlock} from '../components/Reveal';
import {Glass} from '../components/Glass';

type Solid = {cx: number; yT: number; yB: number; rT: number; rB: number; k: number};

const FUNNEL: Solid[] = [0, 1, 2, 3].map((i) => {
  const rT = 320 - i * 74;
  return {cx: 540, yT: 860 + i * 118, yB: 860 + i * 118 + 96, rT, rB: rT - 58, k: 0.27};
});
const BASE = 1330;
const BAR_X = [196, 333, 470, 607, 744];
const BAR_H = [130, 205, 285, 370, 470];
const BARS: Solid[] = BAR_X.map((x, i) => ({cx: x + 50, yT: BASE - BAR_H[i], yB: BASE, rT: 44, rB: 44, k: 0.32}));
const LABELS = ['TOFU', 'MOFU', 'BOFU'];

const mix = (a: Solid, b: Solid, t: number): Solid => ({
  cx: lerp(a.cx, b.cx, t),
  yT: lerp(a.yT, b.yT, t),
  yB: lerp(a.yB, b.yB, t),
  rT: lerp(a.rT, b.rT, t),
  rB: lerp(a.rB, b.rB, t),
  k: lerp(a.k, b.k, t),
});

const sidePath = (s: Solid) => {
  const ryT = s.rT * s.k;
  const ryB = s.rB * s.k;
  return `M${s.cx - s.rT},${s.yT} L${s.cx - s.rB},${s.yB} A${s.rB},${ryB} 0 0 0 ${s.cx + s.rB},${s.yB} L${s.cx + s.rT},${s.yT} A${s.rT},${ryT} 0 0 1 ${s.cx - s.rT},${s.yT} Z`;
};

const Solid3D: React.FC<{s: Solid; rot: number; idx: number; opacity: number}> = ({s, rot, idx, opacity}) => {
  const meridians = [];
  for (let m = 0; m < 10; m++) {
    const th = (m / 10) * Math.PI * 2 + rot;
    const sn = Math.sin(th);
    if (sn <= 0.05) continue;
    meridians.push(
      <line
        key={m}
        x1={s.cx + s.rT * Math.cos(th)}
        y1={s.yT + s.rT * s.k * sn}
        x2={s.cx + s.rB * Math.cos(th)}
        y2={s.yB + s.rB * s.k * sn}
        stroke="#fff"
        strokeWidth={1.4}
        opacity={0.35 * sn}
      />,
    );
  }
  return (
    <g opacity={opacity}>
      <path d={sidePath(s)} fill={`url(#s3side${idx % 2})`} />
      <path d={sidePath(s)} fill="url(#s3shade)" />
      {meridians}
      <ellipse cx={s.cx} cy={s.yT} rx={s.rT} ry={s.rT * s.k} fill="url(#s3top)" stroke={C.electricSoft} strokeWidth={2.2} />
      <ellipse cx={s.cx} cy={s.yT} rx={s.rT * 0.82} ry={s.rT * s.k * 0.82} fill="none" stroke="#fff" strokeWidth={1.2} opacity={0.5} />
    </g>
  );
};

export const S3Strategy: React.FC = () => {
  const f = useCurrentFrame();
  const rot = f * 0.03;
  const tilt = lerp(-6, 6, prog(f, 0, 150, EZ.inOut));

  const solids = FUNNEL.map((fs, i) => {
    const drop = prog(f, 6 + i * 5, 20, EZ.back);
    const built: Solid = {...fs, yT: fs.yT - (1 - drop) * 220, yB: fs.yB - (1 - drop) * 220};
    const m = prog(f, 74 + i * 4, 24, EZ.inOut);
    return {s: mix(built, BARS[i], m), o: drop, m};
  });
  const bar5 = prog(f, 96, 18, EZ.back);
  const fifth: Solid = {...BARS[4], yT: BASE - BAR_H[4] * bar5};
  const morphAll = prog(f, 74, 30, EZ.inOut);

  // Partículas que atraviesan el embudo (conversiones)
  const parts = [];
  if (morphAll < 1) {
    for (let i = 0; i < 46; i++) {
      const u = ((f - 16) / 46 + i / 46) % 1;
      if (f < 16 + (i / 46) * 10) continue;
      const y = lerp(760, 1360, u);
      const lane = Math.sin(i * 12.9898) * 0.9;
      const tier = Math.max(0, Math.min(3, (y - 860) / 118));
      const r = y < 860 ? 340 : lerp(320, 320 - 3 * 74 - 58, tier / 3.6);
      const x = 540 + lane * r * 0.8;
      const conv = u > 0.86;
      parts.push(
        <circle key={i} cx={x} cy={y} r={conv ? 7 : 4.5} fill={conv ? C.electric : C.electricSoft} opacity={(1 - morphAll) * (conv ? 1 : 0.7) * Math.min(1, u * 6)} />,
      );
    }
  }

  // Curva de crecimiento
  const curvePts = BARS.map((b) => ({x: b.cx, y: b.yT - 70}));
  let d = `M${curvePts[0].x},${curvePts[0].y}`;
  for (let i = 1; i < curvePts.length; i++) {
    const a = curvePts[i - 1];
    const b = curvePts[i];
    d += ` C${a.x + 60},${a.y} ${b.x - 60},${b.y} ${b.x},${b.y}`;
  }
  const curve = prog(f, 104, 22, EZ.inOut);

  return (
    <AbsoluteFill>
      <LightBackground glowY={55} />
      {/* retícula sutil */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
        {new Array(13).fill(0).map((_, i) => (
          <line key={i} x1={0} x2={1080} y1={700 + i * 60} y2={700 + i * 60} stroke={C.navy} strokeWidth={1} opacity={0.05} />
        ))}
      </svg>
      <div style={{position: 'absolute', inset: 0, transform: `perspective(1600px) rotateY(${tilt}deg)`, transformOrigin: '50% 60%'}}>
        <svg width={1080} height={1920} style={{position: 'absolute', inset: 0}}>
          <defs>
            <linearGradient id="s3side0" x1="0" x2="1">
              <stop offset="0" stopColor={C.navy} />
              <stop offset="0.55" stopColor={C.electricDeep} />
              <stop offset="1" stopColor={C.navy600} />
            </linearGradient>
            <linearGradient id="s3side1" x1="0" x2="1">
              <stop offset="0" stopColor={C.navy700} />
              <stop offset="0.55" stopColor={C.electric} />
              <stop offset="1" stopColor={C.navy} />
            </linearGradient>
            <linearGradient id="s3shade" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0" stopColor="#fff" stopOpacity="0.18" />
              <stop offset="1" stopColor="#000" stopOpacity="0.18" />
            </linearGradient>
            <radialGradient id="s3top">
              <stop offset="0" stopColor="#FFFFFF" />
              <stop offset="1" stopColor={C.ice} />
            </radialGradient>
            <linearGradient id="s3curve" x1="0" x2="1">
              <stop offset="0" stopColor={C.electricSoft} />
              <stop offset="1" stopColor={C.electricDeep} />
            </linearGradient>
            <filter id="s3glow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="6" result="b" />
              <feMerge>
                <feMergeNode in="b" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>
          {/* sombra de contacto */}
          <ellipse cx={540} cy={1352} rx={lerp(220, 380, morphAll)} ry={26} fill={C.navy} opacity={0.12} />
          {/* eje base del gráfico */}
          <line x1={170} x2={lerp(170, 910, prog(f, 84, 20))} y1={BASE + 2} y2={BASE + 2} stroke={C.navy} strokeWidth={3} opacity={0.35} />
          {parts}
          {solids
            .map((o, i) => ({...o, i}))
            .reverse()
            .map((o) => (
              <Solid3D key={o.i} s={o.s} rot={rot + o.i} idx={o.i} opacity={o.o} />
            ))}
          {bar5 > 0 && <Solid3D s={fifth} rot={rot} idx={4} opacity={Math.min(1, bar5 * 3)} />}
          {/* etiquetas del embudo */}
          {LABELS.map((l, i) => {
            const s = solids[i].s;
            const a = prog(f, 22 + i * 5, 10) * (1 - prog(f, 72, 8));
            return (
              <g key={l} opacity={a}>
                <line x1={s.cx + s.rT + 8} x2={s.cx + s.rT + 40} y1={s.yT + 30} y2={s.yT + 30} stroke={C.electricDeep} strokeWidth={2} />
                <text x={s.cx + s.rT + 48} y={s.yT + 40} fontFamily={FONT} fontWeight={700} fontSize={28} letterSpacing={3} fill={C.navy}>
                  {l}
                </text>
              </g>
            );
          })}
          {/* curva ascendente */}
          <g filter="url(#s3glow)">
            <path d={d} fill="none" stroke="url(#s3curve)" strokeWidth={7} strokeLinecap="round" pathLength={1} strokeDasharray={1} strokeDashoffset={1 - curve} />
            {curvePts.map((p, i) => {
              const a = prog(f, 104 + i * 4.5, 8, EZ.back);
              return <circle key={i} cx={p.x} cy={p.y} r={11 * a} fill="#fff" stroke={C.electric} strokeWidth={5} />;
            })}
          </g>
          {/* flecha final */}
          <g opacity={prog(f, 124, 6)} transform={`translate(${curvePts[4].x + 26},${curvePts[4].y - 18}) rotate(-38)`}>
            <path d="M-14,-12 L14,0 L-14,12" fill="none" stroke={C.electricDeep} strokeWidth={7} strokeLinecap="round" strokeLinejoin="round" />
          </g>
        </svg>
      </div>

      <Kpis />

      <TextBlock top={290} gap={6}>
        <Reveal text="CREA CAMPAÑAS" delay={4} size={102} weight={800} color={C.navy} />
        <Reveal
          text="CON ESTRATEGIA."
          delay={9}
          size={102}
          weight={800}
          gradient={`linear-gradient(90deg, ${C.navy}, ${C.electricDeep} 70%)`}
        />
        <div style={{height: 26}} />
        <div style={{display: 'flex', gap: 26}}>
          {['ANALIZA.', 'OPTIMIZA.', 'ESCALA.'].map((w, i) => (
            <Reveal key={w} text={w} delay={22 + i * 9} size={54} weight={700} tracking={0.06} color={C.electricDeep} />
          ))}
        </div>
      </TextBlock>
    </AbsoluteFill>
  );
};

const Kpis: React.FC = () => {
  const f = useCurrentFrame();
  const items = [
    {k: 'CTR', v: 2.8, fmt: (n: number) => `${n.toFixed(1)}%`},
    {k: 'CPC', v: 3.4, fmt: (n: number) => `$${n.toFixed(2)}`},
    {k: 'ROAS', v: 4.1, fmt: (n: number) => `${n.toFixed(1)}x`},
  ];
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  return (
    <>
      {items.map((it, i) => {
        const p = prog(f, 92 + i * 5, 14, EZ.back);
        const n = prog(f, 94 + i * 5, 22, EZ.out) * it.v;
        return (
          <Glass
            key={it.k}
            light
            radius={24}
            style={{
              left: 110 + i * 295,
              top: 1400,
              width: 270,
              height: 118,
              opacity: Math.min(1, p) * (1 - pe),
              transform: `translateY(${(1 - p) * 40}px)`,
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'center',
              paddingLeft: 30,
              fontFamily: FONT,
            }}
          >
            <div style={{fontSize: 22, letterSpacing: '0.2em', fontWeight: 600, color: C.navy600}}>{it.k}</div>
            <div style={{fontSize: 48, fontWeight: 700, color: C.navy, fontVariantNumeric: 'tabular-nums'}}>{it.fmt(n)}</div>
          </Glass>
        );
      })}
      <div
        style={{
          position: 'absolute',
          top: 1536,
          width: '100%',
          textAlign: 'center',
          fontFamily: FONT,
          fontSize: 22,
          letterSpacing: '0.14em',
          color: C.navy600,
          opacity: prog(f, 110, 10) * 0.7 * (1 - pe),
        }}
      >
        VALORES ILUSTRATIVOS
      </div>
    </>
  );
};
