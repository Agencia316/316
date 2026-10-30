// Uso:
//   node render.js                 -> gera out/video.mp4 (1080x1920, 30fps)
//   node render.js --still 0.5,12  -> salva PNGs de teste em out/still_<t>.png
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const path = require('path');
const fs = require('fs');

const FPS = 30;
const out = path.join(__dirname, 'out');
fs.mkdirSync(out, { recursive: true });

(async () => {
  const browser = await chromium.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
  await page.goto('file://' + path.join(__dirname, 'index.html'));
  await page.evaluate(() => document.fonts.ready);
  const total = await page.evaluate(() => window.TOTAL);

  const si = process.argv.indexOf('--still');
  if (si > -1) {
    for (const t of process.argv[si + 1].split(',').map(Number)) {
      await page.evaluate(t => window.render(t), t);
      await page.locator('#c').screenshot({ path: path.join(out, `still_${t}.png`) });
    }
    await browser.close();
    return;
  }

  const n = Math.round(total * FPS);
  console.log(`duração ${total.toFixed(1)}s, ${n} frames`);
  const ff = spawn('ffmpeg', ['-v', 'error', '-y', '-f', 'image2pipe', '-framerate', String(FPS), '-i', '-',
    '-f', 'lavfi', '-i', 'anullsrc=r=44100:cl=stereo', '-shortest',
    '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '16', '-preset', 'medium', '-c:a', 'aac', '-b:a', '128k',
    '-movflags', '+faststart', path.join(out, 'video.mp4')], { stdio: ['pipe', 'inherit', 'inherit'] });
  const done = new Promise(r => ff.on('close', r));
  for (let f = 0; f < n; f++) {
    await page.evaluate(t => window.render(t), f / FPS);
    const buf = await page.locator('#c').screenshot({ type: 'png' });
    if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
    if (f % 150 === 0) console.log(`frame ${f}/${n}`);
  }
  ff.stdin.end(); await done; await browser.close();
  console.log('ok -> out/video.mp4');
})();
