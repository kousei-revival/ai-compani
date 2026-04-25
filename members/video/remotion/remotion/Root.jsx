import React from 'react';
import {Composition} from 'remotion';
import {VideoFromPrompt} from './VideoFromPrompt';
import {getTotalsFromSpec} from './specUtils';
import videoPrompt from '../prompts/video-prompt.json';

// prompts/video-prompt.json から fps・尺・解像度を自動反映
const {fps, width, height, durationInFrames} = getTotalsFromSpec(videoPrompt);

export const RemotionRoot = () => {
  return (
    <>
      <Composition
        id="VideoFromPrompt"
        component={VideoFromPrompt}
        durationInFrames={durationInFrames}
        fps={fps}
        width={width}
        height={height}
      />
    </>
  );
};
