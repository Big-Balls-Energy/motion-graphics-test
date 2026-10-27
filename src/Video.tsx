import React from 'react';
import {AbsoluteFill, Audio, Sequence, staticFile, useCurrentFrame} from 'remotion';
import {C, EZ, SCENE, lerp, prog} from './theme';
import {Grain} from './components/Atmosphere';
import {S1Hook} from './scenes/S1Hook';
import {S2Course} from './scenes/S2Course';
import {S3Strategy} from './scenes/S3Strategy';
import {S4AI} from './scenes/S4AI';
import {S5Practice} from './scenes/S5Practice';
import {S6Exclusive} from './scenes/S6Exclusive';
import {S7Price} from './scenes/S7Price';
import {S8Close} from './scenes/S8Close';

const OVERLAP = 12; // la escena saliente sigue viva bajo la entrante (zoom-through)

const SCENES: {C: React.FC; light?: boolean}[] = [
  {C: S1Hook},
  {C: S2Course},
  {C: S3Strategy, light: true},
  {C: S4AI},
  {C: S5Practice, light: true},
  {C: S6Exclusive},
  {C: S7Price, light: true},
  {C: S8Close},
];

/** Envuelve cada escena con entrada (profundidad + desenfoque) y salida (zoom a través) */
const Shell: React.FC<{children: React.ReactNode; index: number}> = ({children, index}) => {
  const f = useCurrentFrame();
  const pin = index === 0 ? 1 : prog(f, 0, 11, EZ.out);
  const pout = prog(f, SCENE - 4, OVERLAP + 4, EZ.in);
  const scale = lerp(1.08, 1, pin) * lerp(1, 1.18, pout);
  const blur = (1 - pin) * 14 + pout * 10;
  return (
    <AbsoluteFill
      style={{
        opacity: pin,
        transform: `scale(${scale})`,
        filter: blur > 0.1 ? `blur(${blur}px)` : undefined,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

/** Barrido de luz entre escenas */
const LightSweep: React.FC<{light: boolean}> = ({light}) => {
  const f = useCurrentFrame(); // local: 0 = 8 frames antes del corte
  const t = prog(f, 0, 18, EZ.inOut);
  const a = Math.sin(t * Math.PI);
  return (
    <AbsoluteFill style={{pointerEvents: 'none', mixBlendMode: light ? 'normal' : 'screen'}}>
      <div
        style={{
          position: 'absolute',
          left: -600,
          top: lerp(-900, 2100, t),
          width: 2280,
          height: 520,
          transform: 'rotate(-18deg)',
          background: light
            ? 'linear-gradient(180deg, rgba(255,255,255,0), rgba(255,255,255,0.85), rgba(255,255,255,0))'
            : 'linear-gradient(180deg, rgba(47,140,255,0), rgba(108,182,255,0.55), rgba(255,255,255,0.35), rgba(47,140,255,0))',
          opacity: a,
          filter: 'blur(30px)',
        }}
      />
      <AbsoluteFill style={{background: light ? '#FFFFFF' : C.electric, opacity: a * (light ? 0.35 : 0.12)}} />
    </AbsoluteFill>
  );
};

const FadeOut: React.FC = () => {
  const f = useCurrentFrame();
  return <AbsoluteFill style={{background: '#000', opacity: prog(f, 1188, 12, EZ.inOut)}} />;
};

export const MetaAds2026: React.FC = () => (
  <AbsoluteFill style={{background: C.ink}}>
    {SCENES.map((s, i) => (
      <Sequence key={i} from={i * SCENE} durationInFrames={i === SCENES.length - 1 ? SCENE : SCENE + OVERLAP} layout="none">
        <Shell index={i}>
          <s.C />
        </Shell>
      </Sequence>
    ))}
    {SCENES.slice(1).map((s, i) => (
      <Sequence key={`sw${i}`} from={(i + 1) * SCENE - 8} durationInFrames={18} layout="none">
        <LightSweep light={!!s.light} />
      </Sequence>
    ))}
    <Grain opacity={0.07} />
    <FadeOut />
    <Audio src={staticFile('audio/soundtrack.wav')} />
  </AbsoluteFill>
);
