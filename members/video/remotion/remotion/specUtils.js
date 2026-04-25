/**
 * prompts/video-prompt.json の内容から、Composition 用の長さ・解像度を求める
 * （package.json が commonjs のため、このファイルは CommonJS で書く）
 */

const DEFAULT_FPS = 30;
const DEFAULT_WIDTH = 1920;
const DEFAULT_HEIGHT = 1080;

function getTotalsFromSpec(spec) {
  const fps = typeof spec.fps === 'number' ? spec.fps : DEFAULT_FPS;
  const width = typeof spec.width === 'number' ? spec.width : DEFAULT_WIDTH;
  const height = typeof spec.height === 'number' ? spec.height : DEFAULT_HEIGHT;

  const scenes = Array.isArray(spec.scenes) ? spec.scenes : [];
  const totalSeconds = scenes.reduce((acc, scene) => {
    const sec =
      typeof scene.durationSeconds === 'number' ? scene.durationSeconds : 0;
    return acc + sec;
  }, 0);

  // 最低 1 フレームは確保（0 秒指定の事故防止）
  const durationInFrames = Math.max(1, Math.round(totalSeconds * fps));

  return {fps, width, height, durationInFrames};
}

module.exports = {getTotalsFromSpec};
