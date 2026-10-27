import React from 'react';

export const FacebookGlyph: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path
      fill="#fff"
      d="M56 92V58h11.5l1.8-13.5H56v-8.6c0-3.9 1.1-6.6 6.7-6.6h7.1V17.2c-1.2-.2-5.5-.5-10.4-.5-10.3 0-17.4 6.3-17.4 17.9v9.9H30.4V58H42v34z"
    />
  </svg>
);

export const InstagramGlyph: React.FC<{size: number}> = ({size}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <rect x="18" y="18" width="64" height="64" rx="19" fill="none" stroke="#fff" strokeWidth="7.5" />
    <circle cx="50" cy="50" r="15" fill="none" stroke="#fff" strokeWidth="7.5" />
    <circle cx="68.5" cy="31.5" r="4.6" fill="#fff" />
  </svg>
);

export const WhatsAppGlyph: React.FC<{size: number; color?: string}> = ({size, color = '#fff'}) => (
  <svg width={size} height={size} viewBox="0 0 100 100">
    <path
      fill="none"
      stroke={color}
      strokeWidth="6.5"
      strokeLinejoin="round"
      d="M50 13c20.4 0 37 16.1 37 36s-16.6 36-37 36c-6.4 0-12.4-1.6-17.6-4.3L15 86l5.4-16.2C16.4 63.9 13 56.8 13 49c0-19.9 16.6-36 37-36z"
    />
    <path
      fill={color}
      d="M37.6 31.5c-.9-2-1.9-2.1-2.8-2.1h-2.4c-.8 0-2.2.3-3.3 1.5-1.1 1.2-4.3 4.2-4.3 10.3s4.4 11.9 5 12.7c.6.8 8.5 13.6 21 18.5 10.4 4.1 12.5 3.3 14.8 3.1 2.3-.2 7.3-3 8.3-5.9 1-2.9 1-5.4.7-5.9-.3-.5-1.1-.8-2.4-1.4-1.3-.6-7.3-3.6-8.4-4-1.1-.4-1.9-.6-2.7.6-.8 1.2-3.1 4-3.8 4.8-.7.8-1.4.9-2.6.3-1.3-.6-5.3-2-10.1-6.3-3.7-3.3-6.3-7.5-7-8.7-.7-1.2-.1-1.9.6-2.5.6-.6 1.3-1.4 1.9-2.1.6-.7.8-1.2 1.3-2 .4-.8.2-1.5-.1-2.1-.3-.6-2.6-6.6-3.7-8.7z"
    />
  </svg>
);

export const Check: React.FC<{size: number; color?: string; progress?: number}> = ({
  size,
  color = '#fff',
  progress = 1,
}) => (
  <svg width={size} height={size} viewBox="0 0 24 24">
    <path
      d="M5 12.5l4.2 4.2L19 7"
      fill="none"
      stroke={color}
      strokeWidth="3"
      strokeLinecap="round"
      strokeLinejoin="round"
      pathLength={1}
      strokeDasharray={1}
      strokeDashoffset={1 - progress}
    />
  </svg>
);
