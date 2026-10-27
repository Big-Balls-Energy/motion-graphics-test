import React from 'react';
import {Composition} from 'remotion';
import {MetaAds2026} from './Video';
import {FPS, H, W, TL} from './theme';
import './fonts';

export const Root: React.FC = () => (
  <Composition
    id="MetaAds2026"
    component={MetaAds2026}
    durationInFrames={TL.durationInFrames}
    fps={FPS}
    width={W}
    height={H}
  />
);
