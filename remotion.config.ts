import {Config} from '@remotion/cli/config';

Config.setVideoImageFormat('jpeg');
Config.setJpegQuality(95);
Config.setOverwriteOutput(true);
Config.setCodec('h264');
Config.setPixelFormat('yuv420p');
Config.setCrf(16);
Config.setAudioCodec('aac');
Config.setAudioBitrate('320k');
Config.setChromiumOpenGlRenderer('swangle');
// En entornos sin descarga de Chrome, define REMOTION_BROWSER con la ruta de un Chromium local.
if (process.env.REMOTION_BROWSER) {
  Config.setBrowserExecutable(process.env.REMOTION_BROWSER);
}
