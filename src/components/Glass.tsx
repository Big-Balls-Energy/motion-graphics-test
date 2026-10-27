import React, {CSSProperties} from 'react';

export const Glass: React.FC<{
  style?: CSSProperties;
  children?: React.ReactNode;
  light?: boolean;
  radius?: number;
}> = ({style, children, light = false, radius = 28}) => (
  <div
    style={{
      position: 'absolute',
      borderRadius: radius,
      background: light
        ? 'linear-gradient(160deg, rgba(255,255,255,0.86), rgba(234,243,252,0.62))'
        : 'linear-gradient(160deg, rgba(120,175,240,0.16), rgba(16,46,66,0.30) 60%, rgba(8,24,40,0.42))',
      border: light ? '1.5px solid rgba(47,140,255,0.22)' : '1.5px solid rgba(170,210,255,0.22)',
      boxShadow: light
        ? '0 30px 70px rgba(16,46,66,0.16), inset 0 1px 0 rgba(255,255,255,0.9)'
        : '0 30px 80px rgba(0,0,0,0.38), inset 0 1px 0 rgba(255,255,255,0.18)',
      backdropFilter: 'blur(16px)',
      overflow: 'hidden',
      ...style,
    }}
  >
    {children}
  </div>
);
