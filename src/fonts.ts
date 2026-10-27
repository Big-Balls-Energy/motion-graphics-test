import {loadFont} from '@remotion/fonts';
import {staticFile} from 'remotion';

const weights = [300, 400, 500, 600, 700, 800] as const;

export const fontsReady = Promise.all(
  weights.map((w) =>
    loadFont({
      family: 'Jost',
      url: staticFile(`fonts/jost-latin-${w}-normal.woff2`),
      weight: String(w),
      style: 'normal',
    }),
  ),
);
