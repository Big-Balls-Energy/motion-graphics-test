import {Easing, interpolate} from 'remotion';
import timeline from './timeline.json';

export const W = 1080;
export const H = 1920;
export const FPS = timeline.fps;
export const SCENE = timeline.sceneLength;
export const BEAT = (60 / timeline.bpm) * FPS; // 18.75 frames
export const TL = timeline;

// Paleta tomada del folleto de Atlas Path
export const C = {
  ink: '#030C16',
  navy900: '#06182A',
  navy: '#102E42', // azul marino principal del PDF
  navy700: '#173B54',
  navy600: '#1F4A68',
  steel: '#5180B3', // azul de las manos del logotipo
  electric: '#2F8CFF',
  electricDeep: '#1A63D8',
  electricSoft: '#6CB6FF',
  ice: '#BFDDFB',
  iceLight: '#EAF3FC',
  paper: '#F5F8FC',
  white: '#FFFFFF',
  whatsapp: '#25D366',
};

export const FONT = 'Jost';

// Ventana de lectura común: los textos salen en este frame local
export const TEXT_EXIT = 134;

export const EZ = {
  out: Easing.bezier(0.16, 1, 0.3, 1),
  outSoft: Easing.bezier(0.22, 1, 0.36, 1),
  inOut: Easing.bezier(0.65, 0, 0.35, 1),
  in: Easing.bezier(0.55, 0, 1, 0.45),
  back: Easing.bezier(0.34, 1.45, 0.64, 1),
};

export const prog = (
  f: number,
  start: number,
  dur: number,
  easing: (t: number) => number = EZ.out,
) =>
  interpolate(f, [start, start + dur], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
    easing,
  });

export const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
export const clamp01 = (t: number) => Math.max(0, Math.min(1, t));
