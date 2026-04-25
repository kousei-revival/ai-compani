import React from 'react';
import {
  AbsoluteFill,
  Sequence,
  interpolate,
  useCurrentFrame,
  useVideoConfig,
  Img,
  staticFile,
  Html5Audio,
} from 'remotion';
import videoPrompt from '../prompts/video-prompt.json';

const DEFAULT_GAP = 24;

/**
 * 1シーン分の枠。背景色 or 背景画像＋薄い黒のディム、フェードイン・アウト（シーン頭尾 0.3 秒）
 */
const SceneFrame = ({
  backgroundColor,
  backgroundImage,
  backgroundImageFit = 'cover',
  backgroundDim = 0,
  durationInFrames,
  children,
}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const fadeFrames = fps * 0.3;

  const fadeInOpacity = interpolate(frame, [0, fadeFrames], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const fadeOutOpacity = interpolate(
    frame,
    [durationInFrames - fadeFrames, durationInFrames],
    [1, 0],
    {
      extrapolateLeft: 'clamp',
      extrapolateRight: 'clamp',
    }
  );

  const opacity = Math.min(fadeInOpacity, fadeOutOpacity);
  const fit =
    backgroundImageFit === 'contain' ? 'contain' : 'cover';
  const dimOpacity =
    typeof backgroundDim === 'number'
      ? Math.max(0, Math.min(1, backgroundDim))
      : 0;

  return (
    <AbsoluteFill style={{opacity}}>
      {!backgroundImage ? (
        <AbsoluteFill style={{backgroundColor}} />
      ) : (
        <>
          {/* contain のときの余白用。画像の下に敷く色 */}
          <AbsoluteFill style={{backgroundColor: backgroundColor ?? '#000000'}} />
          <AbsoluteFill>
            <Img
              src={staticFile(backgroundImage)}
              alt=""
              style={{
                width: '100%',
                height: '100%',
                objectFit: fit,
              }}
            />
          </AbsoluteFill>
          {dimOpacity > 0 ? (
            <AbsoluteFill
              style={{
                backgroundColor: '#000000',
                opacity: dimOpacity,
              }}
            />
          ) : null}
        </>
      )}
      <AbsoluteFill
        style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          flexDirection: 'column',
          zIndex: 1,
        }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/**
 * テロップ1ブロック。冒頭 0.5 秒でフェード＋下からスライド
 */
const SceneText = ({text, color, fontSize}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();

  const opacity = interpolate(frame, [0, fps * 0.5], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  const translateY = interpolate(frame, [0, fps * 0.5], [30, 0], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <div
      style={{
        opacity,
        transform: `translateY(${translateY}px)`,
        fontSize,
        fontWeight: 'bold',
        color,
        textAlign: 'center',
        paddingLeft: 80,
        paddingRight: 80,
      }}
    >
      {text}
    </div>
  );
};

/**
 * シーン内に置く画像（ロゴ・写真など）。public/ からの相対パスを src に書く
 */
const SceneInlineImage = ({el}) => {
  const frame = useCurrentFrame();
  const {fps} = useVideoConfig();
  const src = el.src;
  if (!src) {
    return null;
  }

  const opacity = interpolate(frame, [0, fps * 0.4], [0, 1], {
    extrapolateLeft: 'clamp',
    extrapolateRight: 'clamp',
  });

  return (
    <Img
      src={staticFile(src)}
      alt=""
      style={{
        opacity,
        maxWidth: el.maxWidth ?? 'min(80%, 1200px)',
        maxHeight: el.maxHeight ?? 700,
        borderRadius: el.borderRadius ?? 0,
        objectFit: el.objectFit || 'contain',
      }}
    />
  );
};

/**
 * elements の1件を描画（type 省略時はテキスト）
 */
const renderSceneElement = (el, index) => {
  const type = el.type || 'text';
  const marginTop = typeof el.marginTop === 'number' ? el.marginTop : 0;

  if (type === 'image') {
    return (
      <div key={index} style={{marginTop}}>
        <SceneInlineImage el={el} />
      </div>
    );
  }

  return (
    <div key={index} style={{marginTop}}>
      <SceneText
        text={String(el.text ?? '')}
        color={el.color || '#FFFFFF'}
        fontSize={el.fontSize ?? 72}
      />
    </div>
  );
};

/**
 * video-prompt.json の scenes をそのままタイムラインに並べるメインコンポジション
 */
export const VideoFromPrompt = () => {
  const {fps} = useVideoConfig();
  const scenes = Array.isArray(videoPrompt.scenes) ? videoPrompt.scenes : [];

  let startFrame = 0;

  const bgm = videoPrompt.bgm;
  const bgmSrc =
    bgm &&
    typeof bgm.src === 'string' &&
    bgm.src.trim().length > 0
      ? bgm.src.trim()
      : null;

  return (
    <AbsoluteFill
      style={{
        fontFamily: 'Arial, sans-serif',
      }}
    >
      {/* 動画全体の BGM（public/ 内の mp3 / wav / ogg など） */}
      {bgmSrc ? (
        <Html5Audio
          src={staticFile(bgmSrc)}
          volume={
            typeof bgm?.volume === 'number' ? bgm.volume : 0.28
          }
          loop={bgm.loop !== false}
        />
      ) : null}

      {scenes.map((scene, index) => {
        const durationSeconds =
          typeof scene.durationSeconds === 'number' ? scene.durationSeconds : 0;
        const durationInFrames = Math.max(1, Math.round(durationSeconds * fps));
        const from = startFrame;
        startFrame += durationInFrames;

        const bg = scene.backgroundColor || '#000000';
        const bgImage =
          typeof scene.backgroundImage === 'string'
            ? scene.backgroundImage
            : null;
        const bgFit =
          scene.backgroundImageFit === 'contain' ? 'contain' : 'cover';
        const bgDim = scene.backgroundDim;

        const elements = Array.isArray(scene.elements) ? scene.elements : [];
        const gap =
          typeof scene.gap === 'number' && scene.gap >= 0 ? scene.gap : DEFAULT_GAP;
        const flexGap = elements.length > 1 ? gap : 0;

        const sceneAudio = scene.sceneAudio;
        const sceneAudioSrc =
          sceneAudio && typeof sceneAudio.src === 'string'
            ? sceneAudio.src
            : null;

        return (
          <Sequence
            key={index}
            from={from}
            durationInFrames={durationInFrames}
          >
            {/* シーン限定の効果音など（任意） */}
            {sceneAudioSrc ? (
              <Html5Audio
                src={staticFile(sceneAudioSrc)}
                volume={
                  typeof sceneAudio.volume === 'number'
                    ? sceneAudio.volume
                    : 0.6
                }
                loop={sceneAudio.loop === true}
              />
            ) : null}

            <SceneFrame
              backgroundColor={bg}
              backgroundImage={bgImage}
              backgroundImageFit={bgFit}
              backgroundDim={bgDim}
              durationInFrames={durationInFrames}
            >
              {elements.length === 0 ? null : (
                <AbsoluteFill
                  style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    flexDirection: 'column',
                    gap: flexGap,
                  }}
                >
                  {elements.map((el, i) => renderSceneElement(el, i))}
                </AbsoluteFill>
              )}
            </SceneFrame>
          </Sequence>
        );
      })}
    </AbsoluteFill>
  );
};
