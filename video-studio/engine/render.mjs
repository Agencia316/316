// Uso: node engine/render.mjs episodes/exemplo-classico.js [--fps 30] [--audio musica.mp3] [--out out/video.mp4] [--still 12.5]
import { createRequire } from 'node:module';
import { spawn } from 'node:child_process';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

// playwright local, ou global (npm root -g) se não estiver instalado no projeto
const req = createRequire(import.meta.url);
let pw; try { pw = req('playwright'); } catch { const { execSync } = await import('node:child_process'); pw = createRequire(execSync('npm root -g').toString().trim() + '/x.js')('playwright'); }
const { chromium } = pw;
const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const ep = args.find(a => !a.startsWith('--') && !args[args.indexOf(a) - 1]?.startsWith('--')) || 'episodes/exemplo-classico.js';
const opt = (n, d) => { const i = args.indexOf('--' + n); return i >= 0 ? args[i + 1] : d; };
const fps = +opt('fps', 30), audio = opt('audio'), still = opt('still');
const out = path.resolve(root, opt('out', 'out/' + path.basename(ep, '.js') + '.mp4'));

const browser = await chromium.launch({ args: ['--allow-file-access-from-files'] });
const page = await browser.newPage({ viewport: { width: 1080, height: 1920 } });
const url = pathToFileURL(path.join(root, 'engine/stage.html')).href + '?ep=' + encodeURIComponent(ep);
await page.goto(url);
await page.waitForFunction('window.READY === true');
const dur = await page.evaluate('Studio.duration(EPISODE)');
const clip = { x: 0, y: 0, width: 1080, height: 1920 };

if (still) {
  const png = out.replace(/\.mp4$/, `-t${still}.png`);
  await page.evaluate(t => Studio.render(EPISODE, t), +still);
  await page.screenshot({ path: png, clip });
  console.log('still ->', png); await browser.close(); process.exit(0);
}

const total = Math.round(dur * fps);
console.log(`${ep}: ${dur.toFixed(1)}s, ${total} frames @ ${fps}fps`);
const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(fps), '-c:v', 'mjpeg', '-i', '-',
  ...(audio ? ['-i', path.resolve(audio), '-shortest', '-c:a', 'aac', '-b:a', '192k'] : []),
  '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '17', '-preset', 'medium', '-movflags', '+faststart', out], { stdio: ['pipe', 'inherit', 'inherit'] });
const done = new Promise(r => ff.on('close', r));
for (let i = 0; i < total; i++) {
  await page.evaluate(t => Studio.render(EPISODE, t), i / fps);
  const buf = await page.screenshot({ type: 'jpeg', quality: 95, clip });
  if (!ff.stdin.write(buf)) await new Promise(r => ff.stdin.once('drain', r));
  if (i % 60 === 0) process.stdout.write(`\r${i}/${total}`);
}
ff.stdin.end(); await done; await browser.close();
console.log('\nok ->', out);
