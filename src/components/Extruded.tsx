import React from 'react';
import {FONT} from '../theme';

/** Número tipográfico con extrusión tridimensional (capas en profundidad) */
export const Extruded: React.FC<{
  text: string;
  size: number;
  depth?: number;
  face: string;
  side: string;
  sideDark: string;
  dx?: number;
  dy?: number;
  glow?: string;
}> = ({text, size, depth = 16, face, side, sideDark, dx = 1.3, dy = 1.5, glow}) => (
  <div style={{position: 'relative', fontFamily: FONT, fontWeight: 800, fontSize: size, lineHeight: 1, letterSpacing: '-0.02em'}}>
    {new Array(depth).fill(0).map((_, i) => {
      const k = depth - i;
      return (
        <div
          key={i}
          style={{
            position: i === 0 ? 'relative' : 'absolute',
            left: 0,
            top: 0,
            transform: `translate(${k * dx}px, ${k * dy}px)`,
            color: i === 0 ? sideDark : side,
            opacity: i === 0 ? 0.35 : 1,
            filter: i === 0 ? 'blur(14px)' : undefined,
          }}
        >
          {text}
        </div>
      );
    })}
    <div
      style={{
        position: 'absolute',
        left: 0,
        top: 0,
        color: 'transparent',
        backgroundImage: face,
        WebkitBackgroundClip: 'text',
        backgroundClip: 'text',
        filter: glow,
      }}
    >
      {text}
    </div>
  </div>
);
