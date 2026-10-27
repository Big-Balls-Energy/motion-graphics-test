import React from 'react';
import {AbsoluteFill, useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, lerp, prog} from '../theme';
import {LightBackground} from '../components/Atmosphere';
import {Reveal} from '../components/Reveal';
import {Extruded} from '../components/Extruded';
import {Check} from '../components/Icons';

const NumberRow: React.FC<{num: string; delay: number; top: number; lines: string[]}> = ({num, delay, top, lines}) => {
  const f = useCurrentFrame();
  const p = prog(f, delay, 20, EZ.back);
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  const sway = Math.sin(f / 30 + delay) * 3;
  return (
    <div style={{position: 'absolute', top, left: 96, right: 60, display: 'flex', alignItems: 'center', gap: 44}}>
      <div
        style={{
          width: 330,
          display: 'flex',
          justifyContent: 'flex-end',
          transform: `perspective(1300px) rotateY(${-18 + sway}deg) rotateX(${(1 - p) * -80 + 6}deg) scale(${lerp(0.6, 1, Math.min(1, p))})`,
          transformOrigin: '50% 80%',
          opacity: Math.min(1, p * 2) * (1 - pe),
        }}
      >
        <Extruded
          text={num}
          size={250}
          face={`linear-gradient(170deg, ${C.electric} 0%, ${C.electricDeep} 45%, ${C.navy} 100%)`}
          side="#0D2A44"
          sideDark="#0B2A4A"
          depth={18}
        />
      </div>
      <div style={{display: 'flex', flexDirection: 'column', gap: 6}}>
        {lines.map((l, i) => (
          <Reveal key={l} text={l} delay={delay + 6 + i * 4} size={lines.length > 1 ? 62 : 80} weight={800} color={C.navy} align="left" />
        ))}
      </div>
    </div>
  );
};

const STEPS = ['Objetivo', 'Público', 'Creatividad', 'Lanzamiento'];

export const S5Practice: React.FC = () => {
  const f = useCurrentFrame();
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);

  // Línea de tiempo → interfaz de campaña
  const line = prog(f, 26, 20, EZ.inOut);
  const fill = prog(f, 40, 30, EZ.inOut);
  const morph = prog(f, 72, 20, EZ.inOut);
  const cardTop = lerp(1124, 1030, morph);
  const cardH = lerp(8, 450, morph);
  const cardL = lerp(120, 100, morph);
  const cardW = lerp(840, 880, morph);

  const nodeX = (i: number) => 120 + (i < 5 ? i * 88 : 480 + (i - 5) * 88);
  const stepY = (j: number) => 1030 + 96 + j * 74;

  return (
    <AbsoluteFill>
      <LightBackground glowY={35} />
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: 0.6}}>
        {new Array(9).fill(0).map((_, i) => (
          <circle key={i} cx={540} cy={1260} r={160 + i * 120} fill="none" stroke={C.electric} strokeWidth={1.2} opacity={0.08} />
        ))}
      </svg>

      <NumberRow num="10" delay={4} top={250} lines={['SESIONES.']} />
      <NumberRow num="20" delay={14} top={540} lines={['HORAS', 'PRESENCIALES.']} />
      <div style={{position: 'absolute', top: 860, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
        <Reveal
          text="TU CAMPAÑA REAL."
          delay={30}
          size={96}
          weight={800}
          gradient={`linear-gradient(90deg, ${C.electricDeep}, ${C.electric})`}
        />
      </div>

      {/* tarjeta / línea de tiempo */}
      <div
        style={{
          position: 'absolute',
          left: cardL,
          top: cardTop,
          width: cardW * (morph > 0 ? 1 : line),
          height: cardH,
          borderRadius: lerp(4, 34, morph),
          background: morph > 0 ? `rgba(255,255,255,${lerp(0.4, 0.88, morph)})` : 'rgba(16,46,66,0.12)',
          border: morph > 0 ? `1.5px solid rgba(47,140,255,${0.25 * morph})` : undefined,
          boxShadow: `0 30px 70px rgba(16,46,66,${0.16 * morph})`,
          overflow: 'hidden',
          opacity: 1 - pe,
        }}
      >
        {morph === 0 && (
          <div style={{position: 'absolute', left: 0, top: 0, height: '100%', width: `${fill * 100}%`, background: `linear-gradient(90deg, ${C.electricDeep}, ${C.electric})`}} />
        )}
        {morph > 0 && (
          <div style={{opacity: prog(f, 84, 10), fontFamily: FONT}}>
            <div style={{display: 'flex', justifyContent: 'space-between', padding: '30px 40px 0', fontSize: 22, letterSpacing: '0.2em', fontWeight: 600, color: C.navy600}}>
              <span>NUEVA CAMPAÑA</span>
              <span>META ADS</span>
            </div>
            {STEPS.map((s, j) => {
              const done = prog(f, 90 + j * 6, 8, EZ.out);
              return (
                <div key={s} style={{position: 'absolute', left: 110, top: stepY(j) - 1030 - 26, fontSize: 40, fontWeight: 600, color: C.navy, display: 'flex', alignItems: 'center', gap: 20, width: 690}}>
                  <span style={{flex: 1}}>{s}</span>
                  <div style={{width: 200, height: 12, borderRadius: 6, background: 'rgba(16,46,66,0.1)', overflow: 'hidden'}}>
                    <div style={{width: `${done * 100}%`, height: '100%', background: `linear-gradient(90deg, ${C.electricDeep}, ${C.electric})`}} />
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* nodos: sesiones en la línea, pasos en la tarjeta */}
      <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity: 1 - pe}}>
        {morph === 0 &&
          ['SEMANA 1', 'SEMANA 2'].map((w, k) => (
            <text key={w} x={nodeX(k * 5) - 10} y={1076} fontFamily={FONT} fontSize={24} fontWeight={600} letterSpacing={4} fill={C.navy600} opacity={prog(f, 34 + k * 8, 10)}>
              {w}
            </text>
          ))}
        {new Array(10).fill(0).map((_, i) => {
          const j = Math.floor((i * 4) / 10);
          const lead = [0, 3, 5, 8].includes(i);
          const x = lerp(nodeX(i), 150, morph);
          const y = lerp(1128, stepY(j), morph);
          const pop = prog(f, 30 + i * 2.5, 10, EZ.back);
          const on = fill * 10 > i + 0.2;
          const done = prog(f, 90 + j * 6, 8, EZ.out);
          const a = morph > 0 && !lead ? 1 - morph : 1;
          const r = lerp(16, 22, morph) * pop;
          return (
            <g key={i} opacity={a}>
              <circle cx={x} cy={y} r={r + 8} fill={C.electric} opacity={on ? 0.18 : 0} />
              <circle cx={x} cy={y} r={r} fill={on || done > 0 ? C.electric : '#fff'} stroke={C.electricDeep} strokeWidth={3} />
              {morph > 0.9 && lead && (
                <g transform={`translate(${x - 14},${y - 14})`}>
                  <foreignObject width={28} height={28}>
                    <Check size={28} progress={done} />
                  </foreignObject>
                </g>
              )}
            </g>
          );
        })}
      </svg>

      <ActivePill />
    </AbsoluteFill>
  );
};

/** Confirmación visual de campaña activa */
const ActivePill: React.FC = () => {
  const f = useCurrentFrame();
  const p = prog(f, 114, 12, EZ.back);
  const pe = prog(f, TEXT_EXIT, 9, EZ.in);
  const pulse = ((f - 114) % 24) / 24;
  return (
    <div
      style={{
        position: 'absolute',
        top: 1404,
        left: 0,
        right: 0,
        display: 'flex',
        justifyContent: 'center',
        opacity: Math.min(1, p) * (1 - pe),
        transform: `scale(${lerp(0.7, 1, Math.min(1.1, p))})`,
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: 18,
          padding: '18px 36px',
          borderRadius: 999,
          background: C.navy,
          color: '#fff',
          fontFamily: FONT,
          fontSize: 34,
          fontWeight: 700,
          letterSpacing: '0.12em',
          boxShadow: '0 18px 40px rgba(16,46,66,0.35)',
        }}
      >
        <div style={{position: 'relative', width: 22, height: 22}}>
          <div style={{position: 'absolute', inset: 0, borderRadius: 11, background: '#2FD58A'}} />
          {f > 114 && <div style={{position: 'absolute', inset: 0, borderRadius: 11, border: '3px solid #2FD58A', transform: `scale(${1 + pulse * 1.6})`, opacity: 1 - pulse}} />}
        </div>
        CAMPAÑA ACTIVA
      </div>
    </div>
  );
};
