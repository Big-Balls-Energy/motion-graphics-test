import React, {CSSProperties} from 'react';
import {useCurrentFrame} from 'remotion';
import {C, EZ, FONT, TEXT_EXIT, prog} from '../theme';

type RevealProps = {
  text: string;
  delay: number;
  size: number;
  weight?: number;
  color?: string;
  tracking?: number; // em
  exit?: number | null;
  stagger?: number;
  gradient?: string;
  glow?: string;
  dur?: number;
  align?: 'left' | 'center' | 'right';
  style?: CSSProperties;
  lineHeight?: number;
};

/**
 * Línea de tipografía cinética: cada palabra entra a través de una máscara
 * (desplazamiento + desenfoque) en ~0.5 s y después queda totalmente estática.
 */
export const Reveal: React.FC<RevealProps> = ({
  text,
  delay,
  size,
  weight = 800,
  color = C.white,
  tracking = 0,
  exit = TEXT_EXIT,
  stagger = 2.5,
  gradient,
  glow,
  dur = 16,
  align = 'center',
  style,
  lineHeight = 1.0,
}) => {
  const f = useCurrentFrame();
  const words = text.split(' ');
  const pe = exit == null ? 0 : prog(f, exit, 9, EZ.in);
  return (
    <div
      style={{
        fontFamily: FONT,
        fontSize: size,
        fontWeight: weight,
        letterSpacing: `${tracking}em`,
        lineHeight,
        textAlign: align,
        whiteSpace: 'nowrap',
        transform: `translateY(${-pe * size * 0.45}px)`,
        opacity: 1 - pe,
        filter: pe > 0 ? `blur(${pe * 8}px)` : undefined,
        ...style,
      }}
    >
      {words.map((w, i) => {
        const p = prog(f, delay + i * stagger, dur, EZ.out);
        const blur = (1 - p) * 10;
        return (
          <span
            key={i}
            style={{
              display: 'inline-block',
              overflow: 'hidden',
              padding: `${size * 0.3}px ${size * 0.04}px ${size * 0.1}px`,
              margin: `${-size * 0.3}px 0 ${-size * 0.1}px`,
              verticalAlign: 'top',
            }}
          >
            <span
              style={{
                display: 'inline-block',
                transform: `translateY(${(1 - p) * 115}%) rotate(${(1 - p) * 4}deg)`,
                transformOrigin: '0% 100%',
                filter: blur > 0.05 ? `blur(${blur}px)` : undefined,
                color: gradient ? 'transparent' : color,
                backgroundImage: gradient,
                WebkitBackgroundClip: gradient ? 'text' : undefined,
                backgroundClip: gradient ? 'text' : undefined,
                textShadow: glow,
                paddingTop: gradient ? size * 0.3 : undefined,
                marginTop: gradient ? -size * 0.3 : undefined,
              }}
            >
              {w}
            </span>
            {i < words.length - 1 ? <span>&nbsp;</span> : null}
          </span>
        );
      })}
    </div>
  );
};

/** Bloque de texto centrado y anclado a una coordenada vertical */
export const TextBlock: React.FC<{
  top: number;
  children: React.ReactNode;
  gap?: number;
  left?: number;
  right?: number;
  align?: 'center' | 'flex-start';
}> = ({top, children, gap = 10, left = 70, right = 70, align = 'center'}) => (
  <div
    style={{
      position: 'absolute',
      top,
      left,
      right,
      display: 'flex',
      flexDirection: 'column',
      alignItems: align,
      gap,
    }}
  >
    {children}
  </div>
);
