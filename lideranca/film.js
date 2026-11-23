// Liderança se aprende: pure function of time. window.seek(t) paints frame t (see lib/motion.js).
// Timing is in beats (u) on the measured grid (100 bpm); docs/shotlist.md is the plan.
import * as M from './lib/motion.js';

const { W, H, FORMAT, E, TAU, prog, clamp, lerp, springU, SPRING, wobble, font, layout, fitSize, text, fill, rrect, shake, noise1, hash01, mix } = M;

const C = { ink: '#0E1320', ink2: '#232C42', paper: '#F4EFE6', amber: '#FFB020', cold: '#4A5368', mute: '#8A93A8' };
const DISPLAY = 'Display', UI = 'UI';
const S = FORMAT.safe;
const SX = S.x, SW = S.w;

const HITS = [
  [0, 'quem mais', 'impact'],
  [0.9, 'entrega', 'thud'],
  [2, 'carimbo vira gestor', 'impact'],
  [3.7, 'carimbo vira tela', 'whoosh', { len: 0.4 }],
  [4.3, 'otimo no que faz', 'pop', { pitch: 'A5' }],
  [5.3, 'risco 1', 'click'],
  [5.5, 'risco 2', 'click'],
  [6, 'liderar e outra profissao', 'thud'],
  [7.7, 'wipe', 'whoosh', { len: 0.4 }],
  [8.6, 'conta', 'tick'], [9.2, 'conta', 'tick'], [9.8, 'conta', 'tick'], [10.4, 'conta', 'tick'], [11, 'conta', 'tick'],
  [11.6, '78 completo', 'thud'],
  [15, 'sobe pressao', 'riser', { len: 1.5 }],
  [16, '88', 'impact'],
  [17.4, 'pulso', 'tick'], [18.6, 'pulso', 'tick'],
  [21.7, 'wipe', 'whoosh', { len: 0.4 }],
  [22.1, 'card 1', 'pop', { pitch: 'D5' }],
  [25.7, 'whip', 'whoosh', { len: 0.35 }], [26.1, 'card 2', 'pop', { pitch: 'F5' }],
  [29.7, 'whip', 'whoosh', { len: 0.35 }], [30.1, 'card 3', 'pop', { pitch: 'A5' }],
  [33.7, 'whip', 'whoosh', { len: 0.35 }], [34.1, 'card 4', 'pop', { pitch: 'C6' }],
  [37.7, 'wipe', 'whoosh', { len: 0.4 }],
  [39, 'vende', 'thud'], [40.5, 'resolve', 'thud'], [42, 'lidera', 'thud'],
  [44.8, 'riser', 'riser', { len: 1.2 }],
  [46, 'liderança se aprende', 'impact'],
  [47.2, 'se aprende', 'bell', { pitch: 'D6' }],
  [51.7, 'whip', 'whoosh', { len: 0.35 }], [52.1, 'pergunta 1', 'pop', { pitch: 'D5' }],
  [57.7, 'whip', 'whoosh', { len: 0.35 }], [58.1, 'pergunta 2', 'pop', { pitch: 'F5' }],
  [63.7, 'whip', 'whoosh', { len: 0.35 }], [64.1, 'pergunta 3', 'pop', { pitch: 'A5' }],
  [69.7, 'whip', 'whoosh', { len: 0.35 }], [70.1, 'qual dessas', 'pop', { pitch: 'D5' }],
  [72.2, 'um', 'blip', { pitch: 'D5' }], [73.4, 'dois', 'blip', { pitch: 'F5' }], [74.6, 'tres', 'blip', { pitch: 'A5' }],
  [76, 'card final', 'impact'],
  [77.2, 'handle', 'bell', { pitch: 'D6' }],
];

// ----------------------------------------------------------------- helpers
// A line of display type that rises out of a mask at its baseline. exit: beat at which it leaves upward.
function rise(ctx, str, x, base, size, color, u, u0, o = {}) {
  const k = springU(u, u0, o.cfg || SPRING.snappy);
  if (k <= 0.001) return;
  const ex = o.exit != null ? E.inCubic(prog(u, o.exit, o.exit + (o.exitLen || 0.4))) : 0;
  if (ex >= 1) return;
  const track = (o.track ?? -0.03) * size;
  ctx.save();
  ctx.beginPath(); ctx.rect(0, base - size * 1.05, W, size * 1.4); ctx.clip();
  text(ctx, str, x, base + (1 - k) * size * 1.2 - ex * size * 1.4, font(size, 900, o.fam || DISPLAY), color, o.align || 'left', track);
  ctx.restore();
}
// Same, with coloured segments: segs = [[str, color], ...], laid out left to right.
function riseSegs(ctx, segs, x, base, size, u, u0, o = {}) {
  const track = (o.track ?? -0.03) * size, f = font(size, 900, DISPLAY);
  let cx = x;
  for (const [str, col] of segs) {
    rise(ctx, str, cx, base, size, col, u, u0, o);
    cx += layout(ctx, str, f, track).width + track;
  }
}
const fitAll = (ctx, strs, max, maxW = SW, track = -0.03) => Math.min(max, ...strs.map((s) => fitSize(ctx, s, 900, DISPLAY, maxW, max, track * 100 / 100)));
const dot = (ctx, x, y, r, color) => { if (r <= 0) return; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.fillStyle = color; ctx.fill(); };
const ring = (ctx, x, y, r, w, color) => { if (r <= 0) return; ctx.beginPath(); ctx.arc(x, y, r, 0, TAU); ctx.lineWidth = w; ctx.strokeStyle = color; ctx.stroke(); };
function arrow(ctx, x1, y1, x2, y2, w, color) {
  const a = Math.atan2(y2 - y1, x2 - x1), hl = w * 3.2;
  ctx.save(); ctx.strokeStyle = color; ctx.fillStyle = color; ctx.lineWidth = w; ctx.lineCap = 'round';
  ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2 - Math.cos(a) * hl * 0.6, y2 - Math.sin(a) * hl * 0.6); ctx.stroke();
  ctx.beginPath(); ctx.moveTo(x2, y2);
  ctx.lineTo(x2 - Math.cos(a - 0.45) * hl, y2 - Math.sin(a - 0.45) * hl);
  ctx.lineTo(x2 - Math.cos(a + 0.45) * hl, y2 - Math.sin(a + 0.45) * hl);
  ctx.closePath(); ctx.fill(); ctx.restore();
}

// ----------------------------------------------------------------- scene compositor
// Each scene is fn(ctx, u) painting a full frame. A scene's `tr` says how it replaces the previous one;
// during the transition BOTH are on screen (nothing blank between).
function compose(ctx, u, list) {
  let i = list.length - 1;
  while (i > 0 && list[i].u0 > u) i--;
  const s = list[i];
  if (i === 0 || !s.tr) { s.fn(ctx, u); return; }
  const p = prog(u, s.u0, s.u0 + s.tr.dur);
  if (p >= 1) { s.fn(ctx, u); return; }
  const prev = list[i - 1], k = s.tr.kind;
  if (k === 'iris') {
    prev.fn(ctx, u);
    const r0 = s.tr.r0 || 0, r = r0 + (s.tr.r1 - r0) * E.inQuad(p);
    ctx.save(); ctx.beginPath(); ctx.arc(s.tr.cx, s.tr.cy, r, 0, TAU); ctx.clip(); s.fn(ctx, u); ctx.restore();
  } else if (k === 'up') {
    const e = E.inOutCubic(p), y = H * (1 - e);
    ctx.save(); ctx.translate(0, -e * H * 0.1); prev.fn(ctx, u); ctx.restore();
    ctx.save(); ctx.beginPath(); ctx.rect(0, y, W, H); ctx.clip(); s.fn(ctx, u); ctx.restore();
    ctx.fillStyle = C.amber; ctx.fillRect(0, y - 6, W, 10);
  } else if (k === 'pushX') {
    const e = E.inOutCubic(p), d = s.tr.dir;
    ctx.save(); ctx.translate(-d * e * W, 0); prev.fn(ctx, u); ctx.restore();
    ctx.save(); ctx.translate(d * (1 - e) * W, 0); s.fn(ctx, u); ctx.restore();
  } else if (k === 'pushY') {
    const e = E.inOutCubic(p);
    ctx.save(); ctx.translate(0, -e * H); prev.fn(ctx, u); ctx.restore();
    ctx.save(); ctx.translate(0, (1 - e) * H); s.fn(ctx, u); ctx.restore();
  }
}

// ----------------------------------------------------------------- A  hook (u 0..4)
const STAMP = { cx: W / 2, cy: 1210 };
function sceneHook(ctx, u) {
  fill(ctx, C.ink);
  ctx.save();
  shake(ctx, u, 0, 10, 3); shake(ctx, u, 2, 22, 7, 0.16);
  const size = fitAll(ctx, ['QUEM MAIS', 'ENTREGA…'], 250);
  rise(ctx, 'QUEM MAIS', SX, 600, size, C.paper, u, -0.25, { cfg: SPRING.bouncy });
  rise(ctx, 'ENTREGA…', SX, 600 + size * 1.0, size, C.amber, u, 0.65, { cfg: SPRING.bouncy });
  // the stamp
  const k = springU(u, 1.8, SPRING.snappy);
  if (k > 0) {
    const sc = lerp(1.8, 1, Math.min(k, 1.1)), a = clamp(k * 3);
    ctx.save(); ctx.translate(STAMP.cx, STAMP.cy); ctx.rotate(-0.07); ctx.scale(sc, sc); ctx.globalAlpha = a;
    const ts = fitAll(ctx, ['VIRA GESTOR.'], 200, SW - 90);
    const bh = ts * 1.5;
    rrect(ctx, -SW / 2, -bh / 2, SW, bh, 14); ctx.fillStyle = C.amber; ctx.fill();
    text(ctx, 'VIRA GESTOR.', 0, ts * 0.36, font(ts, 900, DISPLAY), C.ink, 'center', -0.03 * ts);
    ctx.restore();
  }
  ctx.restore();
}

// ----------------------------------------------------------------- B  virada (u 4..8)
function sceneTurn(ctx, u) {
  fill(ctx, C.amber);
  const f1 = fitAll(ctx, ['Ótimo no', 'que faz.'], 190);
  const x = SX, b1 = 640, b2 = b1 + f1 * 1.02;
  const ex = 6.0;
  rise(ctx, 'Ótimo no', x, b1, f1, C.ink, u, 4.15, { exit: ex });
  rise(ctx, 'que faz.', x, b2, f1, C.ink, u, 4.3, { exit: ex + 0.05 });
  // strike-throughs, drawn as the line is read
  const tr = -0.03 * f1;
  [['Ótimo no', b1, 5.3], ['que faz.', b2, 5.5]].forEach(([s, b, u0]) => {
    const w = layout(ctx, s, font(f1, 900, DISPLAY), tr).width, p = E.outQuint(prog(u, u0, u0 + 0.35));
    const out = prog(u, ex, ex + 0.4);
    if (p > 0 && out < 1) { ctx.fillStyle = C.ink; ctx.fillRect(x - 14, b - f1 * 0.32 - 12 - out * f1 * 1.4, (w + 28) * p, 24); }
  });
  const f2 = fitAll(ctx, ['Liderar é', 'outra', 'profissão.'], 200);
  const base = 720;
  rise(ctx, 'Liderar é', SX, base, f2, C.ink, u, 6, { cfg: SPRING.bouncy });
  rise(ctx, 'outra', SX, base + f2 * 1.0, f2, C.ink, u, 6.25, { cfg: SPRING.bouncy });
  const kb = springU(u, 6.4, SPRING.snappy);
  if (kb > 0) {
    const w = layout(ctx, 'profissão.', font(f2, 900, DISPLAY), -0.03 * f2).width, bb = base + f2 * 2.1;
    ctx.save(); ctx.beginPath(); ctx.rect(0, 0, W, H); ctx.clip();
    rrect(ctx, SX - 22, bb - f2 * 0.86, (w + 44) * Math.min(kb, 1), f2 * 1.12, 16); ctx.fillStyle = C.ink; ctx.fill(); ctx.restore();
  }
  rise(ctx, 'profissão.', SX, base + f2 * 2.1, f2, C.paper, u, 6.5, { cfg: SPRING.bouncy });
}

// ----------------------------------------------------------------- C  dados 78% / 88% (u 8..22)
function sceneData(ctx, u) {
  fill(ctx, C.ink);
  ctx.save();
  shake(ctx, u, 11.6, 9, 5); shake(ctx, u, 16, 20, 11, 0.16);
  const cell = 66, gx = SX, gy = 830, R = 22;
  const n = u < 16 ? 6 * Math.floor(13 * E.outCubic(prog(u, 8.3, 11.6)) + 1e-6) : 78 + 2 * Math.floor(5 * E.outCubic(prog(u, 16.3, 18)) + 1e-6);
  // number
  const size = 330, base = 580;
  const k = springU(u, 8.1, SPRING.gentle), exit = 0;
  if (k > 0 && exit < 1) {
    ctx.save(); ctx.beginPath(); ctx.rect(0, base - size * 1.0, W, size * 1.3); ctx.clip();
    text(ctx, `${Math.round(n)}%`, SX - 6, base + (1 - k) * size * 1.2 - exit * size * 1.4, font(size, 900, DISPLAY), C.amber, 'left', -0.04 * size);
    ctx.restore();
  }
  // captions
  rise(ctx, 'dos líderes assumiram o cargo', SX, 668, 54, C.paper, u, 9.2, { fam: UI, w: 600, track: 0, exit: 15.5, exitLen: 0.35, cfg: SPRING.snappy });
  rise(ctx, 'sem formação suficiente.', SX, 732, 54, C.paper, u, 9.5, { fam: UI, track: 0, exit: 15.6, exitLen: 0.35 });
  rise(ctx, 'trabalham sob pressão', SX, 668, 54, C.paper, u, 16.2, { fam: UI, track: 0 });
  rise(ctx, 'constante.', SX, 732, 54, C.paper, u, 16.4, { fam: UI, track: 0 });
  rise(ctx, 'Pesquisa 2026 · 750 profissionais', SX, 790, 34, C.mute, u, 9.9, { fam: UI, track: 0 });
  // grid of 100 people
  const ramp = prog(u, 17.6, 18.8);
  for (let i = 0; i < 100; i++) {
    const r = Math.floor(i / 10), c = i % 10;
    const gk = springU(u, 8.2 + r * 0.06 + c * 0.02, SPRING.snappy);
    if (gk <= 0) continue;
    const x = gx + cell * (c + 0.5), y = gy + cell * (r + 0.5);
    const lit = n > i;
    const age = n - i;
    let sc = 1;
    if (lit && age < 5) sc += 0.45 * (1 - age / 5);
    if (u >= 16.8 && lit) {
      const ph = 0.5 + 0.5 * Math.cos(TAU * (u * 2 - i * 0.025));
      sc += 0.2 * ph * ramp;
    }
    const jx = u >= 16.8 && lit ? 2.2 * ramp * noise1(u * 14 + i * 3.1, 2) : 0;
    const out = 0;
    dot(ctx, x + jx, y, R * sc * Math.min(gk, 1.05) * (1 - out), lit ? C.amber : C.ink2);
  }
  ctx.restore();
}

// ----------------------------------------------------------------- D  na prática (u 22..38)
function illResolve(ctx, u, u0, cx, cy) {
  const k = springU(u, u0 - 0.2, SPRING.bouncy), R = lerp(400, 150, E.inOutCubic(prog(u, u0 + 0.3, u0 + 3.6)));
  for (let i = 0; i < 16; i++) {
    const a = (i / 16) * TAU + (u - u0) * 0.5 + hash01(i, 4) * 0.8;
    const rr = R * (0.8 + 0.4 * hash01(i, 9)), s = 40 + hash01(i, 2) * 14;
    const x = cx + Math.cos(a) * rr, y = cy + Math.sin(a) * rr * 0.8;
    ctx.save(); ctx.translate(x, y); ctx.rotate(a * 1.3); rrect(ctx, -s / 2, -s / 2, s, s, 9); ctx.fillStyle = C.cold; ctx.fill(); ctx.restore();
  }
  dot(ctx, cx, cy, 78 * k * (1 - 0.15 * prog(u, u0 + 0.5, u0 + 3.6)), C.amber);
}
function illExpect(ctx, u, u0, cx, cy) {
  const tx = cx + 140, k = springU(u, u0, SPRING.snappy);
  ctx.save(); ctx.setLineDash([22, 18]); ring(ctx, tx, cy, 120 * k, 9, C.mute); ctx.restore();
  text(ctx, '?', tx, cy + 62 * k, font(190 * k, 900, DISPLAY), C.paper, 'center');
  const a = springU(u, u0 + 0.6, SPRING.gentle);
  const wob = 22 * noise1(u * 2.2, 6), ay = cy + 120 * noise1(u * 1.3 + 4, 8) * (1 - 0.3 * a);
  const x1 = cx - 330 + a * 120, x2 = cx - 90 + a * 150;
  if (a > 0) arrow(ctx, x1, ay + wob, x2, ay + wob * 0.2 + 30 * Math.sin(u * 1.7), 18, C.amber);
}
function illAvoid(ctx, u, u0, cx, cy) {
  const g = E.inQuad(prog(u, u0 + 0.2, u0 + 3.7));
  dot(ctx, cx + 60, cy + 10, lerp(30, 230, g), C.amber);
  const s = lerp(1, 0.36, E.inOutCubic(prog(u, u0 + 0.4, u0 + 3.2))), k = springU(u, u0, SPRING.bouncy);
  const bx = lerp(cx - 20, cx - 215, E.inOutCubic(prog(u, u0 + 0.4, u0 + 3.2))), by = lerp(cy - 20, cy - 190, E.inOutCubic(prog(u, u0 + 0.4, u0 + 3.2)));
  ctx.save(); ctx.translate(bx, by); ctx.scale(s * k, s * k);
  rrect(ctx, -170, -100, 340, 200, 44); ctx.fillStyle = C.paper; ctx.fill();
  ctx.beginPath(); ctx.moveTo(-70, 96); ctx.lineTo(-120, 175); ctx.lineTo(-10, 98); ctx.closePath(); ctx.fill();
  for (let i = 0; i < 3; i++) dot(ctx, -70 + i * 70, 0, 18 * (0.6 + 0.4 * Math.max(0, Math.sin(TAU * (u * 1.2 - i * 0.18)))), C.ink);
  ctx.restore();
}
function illMood(ctx, u, u0, cx, cy) {
  const g = E.inOutCubic(prog(u, u0 + 0.3, u0 + 3.2));
  for (let r = 0; r < 6; r++) for (let c = 0; c < 6; c++) {
    const i = r * 6 + c, k = springU(u, u0 + i * 0.02, SPRING.snappy);
    const d = Math.hypot(r - 2.5, c - 2.5) / 3.6;
    const col = mix(C.amber, C.cold, clamp(g * 1.4 - (1 - d) * 0.4));
    const jit = 6 * g * noise1(u * 9 + i * 5.3, 3);
    dot(ctx, cx - 225 + c * 90 + jit, cy - 225 + r * 90 + 0.7 * jit, 31 * Math.min(k, 1.05) * (1 - 0.18 * g), col);
  }
}
const CARDS = [
  { lines: ['Resolve', 'tudo', 'sozinho.'], ill: illResolve, hl: 2 },
  { lines: ['Cobra sem', 'explicar o', 'que espera.'], ill: illExpect, hl: 2 },
  { lines: ['Evita', 'conversas', 'difíceis.'], ill: illAvoid, hl: 2 },
  { lines: ['A equipe sente', 'e o clima', 'piora.'], ill: illMood, hl: 2 },
];
function makeCard(i, u0) {
  return (ctx, u) => {
    fill(ctx, C.ink);
    const c = CARDS[i];
    c.ill(ctx, u, u0, W / 2, 700);
    const size = fitAll(ctx, c.lines, 150);
    c.lines.forEach((l, j) => rise(ctx, l, SX, 1140 + j * size * 1.02, size, j === c.hl ? C.amber : C.paper, u, u0 - 0.15 + j * 0.2, { cfg: SPRING.bouncy }));
  };
}
const CARD_LIST = [
  { u0: 22, fn: makeCard(0, 22) },
  { u0: 26, fn: makeCard(1, 26), tr: { kind: 'pushX', dir: 1, dur: 0.5 } },
  { u0: 30, fn: makeCard(2, 30), tr: { kind: 'pushY', dur: 0.5 } },
  { u0: 34, fn: makeCard(3, 34), tr: { kind: 'pushX', dir: -1, dur: 0.5 } },
];
function sceneCards(ctx, u) {
  compose(ctx, u, CARD_LIST);
  const lk = springU(u, 21.9, SPRING.snappy);
  if (lk <= 0) return;
  text(ctx, 'NA PRÁTICA', SX, 330, font(42, 700, UI), C.amber, 'left', 5);
  const cur = Math.min(3, Math.floor((u - 22) / 4));
  for (let i = 0; i < 4; i++) dot(ctx, S.x + S.w - 12 - (3 - i) * 36, 316, i === cur ? 11 : 7, i === cur ? C.amber : C.cold);
}

// ----------------------------------------------------------------- E  PMEs (u 38..46)
const BIG = { size: 0, cx: 0, cy: 0 };
function pmeGeom(ctx) {
  const size = fitAll(ctx, ['RESOLVE.'], 240), b0 = 820, step = size * 1.03;
  const L = layout(ctx, 'LIDERA.', font(size, 900, DISPLAY), -0.03 * size), g = L.glyphs[L.glyphs.length - 1];
  BIG.size = size; BIG.cx = SX + g.cx; BIG.cy = b0 + step * 2 - size * 0.06;
}
function scenePME(ctx, u) {
  fill(ctx, '#161E32');
  rise(ctx, 'Em pequenas e médias empresas,', SX, 380, 44, C.mute, u, 37.9, { fam: UI, track: 0 });
  rise(ctx, 'quem lidera também:', SX, 440, 44, C.mute, u, 38.1, { fam: UI, track: 0 });
  const size = fitAll(ctx, ['RESOLVE.'], 240);
  const b0 = 820, step = size * 1.03;
  rise(ctx, 'VENDE.', SX, b0, size, C.paper, u, 38.85, { cfg: SPRING.bouncy });
  rise(ctx, 'RESOLVE.', SX, b0 + step, size, C.paper, u, 40.35, { cfg: SPRING.bouncy });
  rise(ctx, 'LIDERA.', SX, b0 + step * 2, size, C.amber, u, 41.85, { cfg: SPRING.bouncy });
  // the full stop of LIDERA. grows into the next scene
  pmeGeom(ctx);
  const p = E.inCubic(prog(u, 43.4, 46));
  if (p > 0) dot(ctx, BIG.cx, BIG.cy, lerp(size * 0.09, 230, p), C.amber);
}

// ----------------------------------------------------------------- F  liderança se aprende (u 46..52)
function sceneLearn(ctx, u) {
  fill(ctx, C.amber);
  ctx.save(); shake(ctx, u, 46, 16, 4, 0.14);
  const s1 = fitAll(ctx, ['Liderança'], 260), s2 = fitAll(ctx, ['se aprende.'], 260);
  rise(ctx, 'Liderança', SX, 700, s1, C.ink, u, 45.9, { cfg: SPRING.bouncy });
  const kb = springU(u, 46.5, SPRING.snappy), by = 700 + s2 * 1.2;
  if (kb > 0) {
    const w = layout(ctx, 'se aprende.', font(s2, 900, DISPLAY), -0.03 * s2).width;
    rrect(ctx, SX - 22, by - s2 * 0.86, (w + 44) * Math.min(kb, 1), s2 * 1.12, 18); ctx.fillStyle = C.ink; ctx.fill();
  }
  rise(ctx, 'se aprende.', SX, by, s2, C.paper, u, 46.6, { cfg: SPRING.bouncy });
  rise(ctx, 'Comece com 3 perguntas simples.', SX, 1150, 50, C.ink, u, 48.4, { fam: UI, track: 0 });
  for (let i = 0; i < 3; i++) {
    const k = springU(u, 49 + i * 0.35, SPRING.bouncy);
    if (k > 0) { dot(ctx, SX + 52 + i * 128, 1290, 52 * k, C.ink); text(ctx, String(i + 1), SX + 52 + i * 128, 1290 + 20 * k, font(60 * k, 900, DISPLAY), C.amber, 'center'); }
  }
  ctx.restore();
}

// ----------------------------------------------------------------- G H I  as três perguntas (u 52..70)
function questionScene({ u0, n, lines, segs, ill }) {
  return (ctx, u) => {
    fill(ctx, C.ink);
    ctx.save(); shake(ctx, u, u0, 12, 5 + n, 0.14);
    const k = springU(u, u0 - 0.1, SPRING.bouncy);
    if (k > 0) text(ctx, String(n), SX - 20, 740, font(560 * Math.min(k, 1.1), 900, DISPLAY), C.amber, 'left', -0.04 * 560);
    ill(ctx, u, u0, 700, 520);
    const size = fitAll(ctx, lines, 100);
    lines.forEach((l, j) => {
      const at = u0 + 0.5 + j * 0.3;
      if (segs[j]) riseSegs(ctx, segs[j], SX, 940 + j * size * 1.08, size, u, at);
      else rise(ctx, l, SX, 940 + j * size * 1.08, size, C.paper, u, at);
    });
    ctx.restore();
  };
}
function illTarget(ctx, u, u0, cx, cy) {
  [150, 110, 70].forEach((r, i) => ring(ctx, cx, cy, r * springU(u, u0 + 0.2 + i * 0.15, SPRING.snappy), 10, C.mute));
  dot(ctx, cx, cy, 32 * springU(u, u0 + 0.7, SPRING.bouncy), C.amber);
  const a = springU(u, u0 + 1.2, SPRING.snappy);
  if (a > 0) {
    const sx = cx + 330, sy = cy - 260, hx = sx + (cx - sx) * a, hy = sy + (cy - sy) * a, t0 = Math.max(0, a - 0.45);
    arrow(ctx, sx + (cx - sx) * t0, sy + (cy - sy) * t0, hx, hy, 14, C.paper);
  }
  const pg = prog(u, u0 + 1.9, u0 + 3);
  if (pg > 0 && pg < 1) ring(ctx, cx, cy, 40 + 130 * pg, 8 * (1 - pg), C.amber);
}
function illTimeline(ctx, u, u0, cx, cy) {
  const x0 = 420, x1 = 930, y = cy + 60;
  ctx.fillStyle = C.cold; ctx.fillRect(x0, y - 4, (x1 - x0) * E.outQuint(prog(u, u0, u0 + 0.6)), 8);
  const m = springU(u, u0 + 1.0, SPRING.gentle), mx = lerp(x0 + 20, 660, m);
  if (m > 0) { dot(ctx, mx, y, 30, C.amber); ring(ctx, mx, y, 30 + 50 * prog(u, u0 + 2.2, u0 + 3.2), 7 * (1 - prog(u, u0 + 2.2, u0 + 3.2)), C.amber); }
  rise(ctx, 'retorno', mx - 70, y - 70, 38, C.amber, u, u0 + 1.6, { fam: UI, track: 0 });
  const pk = springU(u, u0 + 3.6, SPRING.bouncy);
  dot(ctx, x1 - 20, y, 34 * pk, C.cold);
  rise(ctx, 'problema', x1 - 160, y + 100, 38, C.mute, u, u0 + 3.9, { fam: UI, track: 0 });
}
function illWaves(ctx, u, u0, cx, cy) {
  const x0 = 420, x1 = 930;
  const a = prog(u, u0 + 0.5, u0 + 2), b = prog(u, u0 + 2, u0 + 3.8);
  ctx.save(); ctx.lineWidth = 10; ctx.lineJoin = 'round'; ctx.lineCap = 'round';
  ctx.strokeStyle = C.cold; ctx.beginPath();
  for (let x = x0; x <= x0 + (x1 - x0) * a; x += 4) {
    const ph = Math.floor((x - x0) / 46), yy = cy - 110 + (ph % 2 ? -34 : 34);
    if (x === x0) ctx.moveTo(x, yy); else { ctx.lineTo(x, yy); }
  }
  ctx.stroke();
  ctx.strokeStyle = C.amber; ctx.beginPath();
  for (let x = x0; x <= x0 + (x1 - x0) * b; x += 4) {
    const yy = cy + 90 + 40 * Math.sin(((x - x0) / 90 - u * 0.6) * TAU * 0.5);
    if (x === x0) ctx.moveTo(x, yy); else ctx.lineTo(x, yy);
  }
  ctx.stroke(); ctx.restore();
  rise(ctx, 'cobrar', x0, cy - 170, 42, C.mute, u, u0 + 0.6, { fam: UI, track: 0 });
  rise(ctx, 'ouvir', x0, cy + 190, 42, C.amber, u, u0 + 2.1, { fam: UI, track: 0 });
}
const Q1 = questionScene({ u0: 52, n: 1, lines: ['Minha equipe', 'sabe exatamente', 'o que espero', 'dela?'], segs: { 1: [['sabe ', C.paper], ['exatamente', C.amber]] }, ill: illTarget });
const Q2 = questionScene({ u0: 58, n: 2, lines: ['Dou retorno', 'antes de o', 'problema', 'aparecer?'], segs: { 1: [['antes ', C.amber], ['de o', C.paper]] }, ill: illTimeline });
const Q3 = questionScene({ u0: 64, n: 3, lines: ['Tenho espaço', 'para ouvir,', 'não só', 'cobrar?'], segs: { 1: [['para ', C.paper], ['ouvir,', C.amber]] }, ill: illWaves });

// ----------------------------------------------------------------- J  pergunta final (u 70..76)
function sceneAsk(ctx, u) {
  fill(ctx, C.ink);
  const lines = ['Qual dessas', 'três é a mais', 'difícil pra', 'você hoje?'];
  const size = fitAll(ctx, lines, 120);
  lines.forEach((l, j) => {
    const y = 520 + j * size * 1.08, at = 69.8 + j * 0.25, o = { cfg: SPRING.bouncy };
    if (j === 2) riseSegs(ctx, [['difícil ', C.amber], ['pra', C.paper]], SX, y, size, u, at, o);
    else rise(ctx, l, SX, y, size, C.paper, u, at, o);
  });
  for (let i = 0; i < 3; i++) {
    const s = 72.2 + i * 1.2, on = u >= s && u < s + 1.1, k = springU(u, s, SPRING.bouncy);
    const cx = SX + 80 + i * 200, cy = 1260, r = 80 * (on ? 1 + 0.18 * Math.min(k, 1.2) : 1);
    const appear = springU(u, 71.2 + i * 0.15, SPRING.snappy);
    if (appear <= 0) continue;
    if (on) dot(ctx, cx, cy, r * appear, C.amber); else ring(ctx, cx, cy, 76 * appear, 8, C.cold);
    text(ctx, String(i + 1), cx, cy + 34 * appear, font(100 * appear, 900, DISPLAY), on ? C.ink : C.mute, 'center');
  }
}

// ----------------------------------------------------------------- K  card final (u 76..80)
function sceneEnd(ctx, u) {
  fill(ctx, C.paper);
  const lines = ['Me siga', 'para mais', 'conteúdos.'];
  const size = fitAll(ctx, lines, 220);
  lines.forEach((l, j) => rise(ctx, l, SX, 640 + j * size * 1.02, size, j === 2 ? C.ink : C.ink, u, 75.8 + j * 0.25, { cfg: SPRING.bouncy }));
  const handle = '@stephaniesonsin.psi', f = font(50, 700, UI);
  const L = layout(ctx, handle, f, 0), pw = L.width + 100, ph = 112, k = springU(u, 77, SPRING.bouncy);
  if (k > 0) {
    ctx.save(); ctx.translate(SX + pw / 2, 640 + size * 2.02 + 190); ctx.scale(Math.min(k, 1.1), Math.min(k, 1.1));
    rrect(ctx, -pw / 2, -ph / 2, pw, ph, ph / 2); ctx.fillStyle = C.amber; ctx.fill();
    text(ctx, handle, 0, 18, f, C.ink, 'center');
    ctx.restore();
  }
}

// ----------------------------------------------------------------- timeline
const MAIN = [
  { u0: 0, fn: sceneHook },
  { u0: 4, fn: sceneTurn, tr: { kind: 'iris', dur: 0.7, cx: STAMP.cx, cy: STAMP.cy, r1: 1800 } },
  { u0: 8, fn: sceneData, tr: { kind: 'up', dur: 0.55 } },
  { u0: 22, fn: sceneCards, tr: { kind: 'up', dur: 0.55 } },
  { u0: 38, fn: scenePME, tr: { kind: 'up', dur: 0.55 } },
  { u0: 46, fn: sceneLearn, tr: { kind: 'iris', dur: 0.7, cx: 0, cy: 0, r0: 230, r1: 2400 } },
  { u0: 52, fn: Q1, tr: { kind: 'pushX', dir: 1, dur: 0.5 } },
  { u0: 58, fn: Q2, tr: { kind: 'pushX', dir: 1, dur: 0.5 } },
  { u0: 64, fn: Q3, tr: { kind: 'pushX', dir: 1, dur: 0.5 } },
  { u0: 70, fn: sceneAsk, tr: { kind: 'pushY', dur: 0.5 } },
  { u0: 76, fn: sceneEnd },
];

M.film({
  fonts: [font(100, 900, DISPLAY), font(40, 600, UI)],
  hits: HITS,
  draw(ctx, u) {
    // the iris into scene F opens from the full stop of "LIDERA." (laid out by scenePME)
    pmeGeom(ctx); MAIN[5].tr.cx = BIG.cx; MAIN[5].tr.cy = BIG.cy;
    compose(ctx, u, MAIN);
  },
});
