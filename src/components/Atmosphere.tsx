import React from 'react';
import {AbsoluteFill, Img, random, staticFile, useCurrentFrame} from 'remotion';
import {C} from '../theme';
import {project} from '../lib/space';

/** Fondo azul marino con iluminación volumétrica */
export const DeepBackground: React.FC<{
  glowX?: number;
  glowY?: number;
  intensity?: number;
  base?: string;
}> = ({glowX = 50, glowY = 45, intensity = 1, base = C.navy900}) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(120% 70% at ${glowX}% ${glowY}%, rgba(47,140,255,${0.22 * intensity}) 0%, rgba(16,46,66,${0.9}) 38%, ${base} 72%, ${C.ink} 100%)`,
    }}
  />
);

/** Fondo claro con detalles azul hielo */
export const LightBackground: React.FC<{glowY?: number}> = ({glowY = 40}) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(90% 55% at 50% ${glowY}%, #FFFFFF 0%, ${C.paper} 45%, #DDEAF7 100%)`,
    }}
  />
);

type Dust = {x: number; y: number; z: number; r: number; tw: number};
const makeDust = (n: number, seed: string): Dust[] =>
  new Array(n).fill(0).map((_, i) => ({
    x: (random(`${seed}x${i}`) - 0.5) * 2600,
    y: (random(`${seed}y${i}`) - 0.5) * 4200,
    z: random(`${seed}z${i}`) * 3000,
    r: 1 + random(`${seed}r${i}`) * 2.6,
    tw: random(`${seed}t${i}`) * Math.PI * 2,
  }));
const DUST = makeDust(170, 'dust');

/** Partículas luminosas en profundidad que avanzan hacia la cámara */
export const ParticleField: React.FC<{
  speed?: number;
  color?: string;
  opacity?: number;
  drift?: number;
}> = ({speed = 6, color = '#9FCBFF', opacity = 1, drift = 0}) => {
  const f = useCurrentFrame();
  return (
    <svg width={1080} height={1920} style={{position: 'absolute', inset: 0, opacity}}>
      <defs>
        <radialGradient id="dustG">
          <stop offset="0%" stopColor={color} stopOpacity="1" />
          <stop offset="100%" stopColor={color} stopOpacity="0" />
        </radialGradient>
      </defs>
      {DUST.map((d, i) => {
        let z = (d.z - f * speed) % 3000;
        if (z < 0) z += 3000;
        const p = project({x: d.x + Math.sin(f / 40 + d.tw) * 30 + drift * f, y: d.y, z: z - 200});
        if (!p.visible) return null;
        const near = 1 - z / 3000;
        const tw = 0.6 + 0.4 * Math.sin(f / 9 + d.tw);
        const a = Math.min(1, near * 1.4) * tw * Math.min(1, z / 300);
        const r = d.r * p.s * (1 + near * 1.5);
        return <circle key={i} cx={p.x} cy={p.y} r={r * 3} fill="url(#dustG)" opacity={a * 0.8} />;
      })}
    </svg>
  );
};

export const Vignette: React.FC<{strength?: number}> = ({strength = 0.55}) => (
  <AbsoluteFill
    style={{
      background: `radial-gradient(85% 60% at 50% 50%, rgba(0,0,0,0) 55%, rgba(0,6,14,${strength}) 100%)`,
      pointerEvents: 'none',
    }}
  />
);

/** Grano fílmico sutil (evita bandas en degradados al comprimir H.264) */
export const Grain: React.FC<{opacity?: number}> = ({opacity = 0.06}) => {
  const f = useCurrentFrame();
  const ox = Math.floor(random(`gx${f}`) * 512);
  const oy = Math.floor(random(`gy${f}`) * 512);
  return (
    <AbsoluteFill
      style={{
        backgroundImage: `url(${staticFile('fx/grain.png')})`,
        backgroundPosition: `${ox}px ${oy}px`,
        backgroundSize: '512px 512px',
        opacity,
        mixBlendMode: 'overlay',
        pointerEvents: 'none',
      }}
    />
  );
};

export {Img};
