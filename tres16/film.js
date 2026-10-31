// Funil jurídico (teste 8 s): função pura do tempo. Texto tirado do artigo da Três16.
import * as M from './lib/motion.js';

const { W, H, FORMAT, E, prog, lerp, springU, SPRING, font, layout, glyph, text, fill, rrect } = M;

// Paleta provisória (acento único). Trocar quando a identidade real chegar.
const C = { ink: '#0B1020', paper: '#F2EFE8', accent: '#F5A524', mute: '#8A93AD' };
const DISPLAY = 'Display', UI = 'UI';

const HITS = [
  [0, 'Seu anúncio', 'impact'],
  [1, 'traz lead.', 'pop', { pitch: 'A5' }],
  [2, 'Mas o', 'pop', { pitch: 'D6' }],
  [3, 'contrato?', 'impact'],
  [4, 'corte: tese', 'thud'],
  [6.5, 'campanha cai', 'whoosh', { len: 0.4 }],
  [7, 'sistema', 'bell', { pitch: 'D6' }],
  [8, 'corte: funil', 'thud'],
  [9, 'etapa 02', 'pop', { pitch: 'A5' }],
  [10, 'etapa 03', 'pop', { pitch: 'C6' }],
  [11, 'etapa 04', 'pop', { pitch: 'E6' }],
  [12, 'fecho', 'impact'],
  [13, 'marca', 'bell', { pitch: 'D6' }],
];

// Linhas de texto que sobem de dentro de uma máscara, uma por batida.
function lines(ctx, u, list, { size, y0, lh, u0, step = 1, x, exit = null }) {
  list.forEach((ln, i) => {
    const k = springU(u, u0 + i * step, SPRING.bouncy);
    if (k <= 0) return;
    const f = font(size, 800, DISPLAY), track = -0.03 * size;
    const base = y0 + i * lh;
    const ex = exit ? E.inBack(prog(u, exit + i * 0.06, exit + 0.4 + i * 0.06), 1.2) : 0;
    ctx.save();
    ctx.beginPath(); ctx.rect(0, base - size * 0.92, W, size * 1.2); ctx.clip();
    text(ctx, ln.t, x, base + (1 - k) * size * 1.1 - ex * size * 1.4, f, ln.c, 'left', track);
    ctx.restore();
  });
}

function sceneHook(ctx, u) {
  fill(ctx, C.ink);
  const s = FORMAT.safe;
  lines(ctx, u, [
    { t: 'Seu anúncio', c: C.paper }, { t: 'traz lead.', c: C.paper },
    { t: 'Mas o', c: C.mute }, { t: 'contrato?', c: C.accent },
  ], { size: 175, y0: s.y + 380, lh: 225, u0: -0.25, step: 0.8, x: s.x });
}

function sceneThesis(ctx, u) {
  fill(ctx, C.paper);
  const s = FORMAT.safe;
  const size = 132, lh = 190, y0 = s.y + 380, track = -0.03 * size;
  const f = font(size, 800, DISPLAY);
  const rows = ['Aquisição', 'previsível', 'não é uma', 'campanha.', 'É um sistema.'];
  rows.forEach((r, i) => {
    const k = springU(u, 3.6 + i * 0.35, SPRING.bouncy);
    if (k <= 0) return;
    const base = y0 + i * lh;
    let dy = (1 - k) * size * 1.1, col = C.ink;
    if (i === 3) {                                   // "campanha." é riscada e cai
      dy += E.inBack(prog(u, 6.5, 7), 1.6) * (H - base + 200);
    }
    if (i === 4) col = C.ink;
    ctx.save();
    ctx.beginPath(); ctx.rect(0, base - size * 0.92 - (i === 3 ? 0 : 0), W, i === 3 ? H : size * 1.2); ctx.clip();
    text(ctx, r, s.x, base + dy, f, col, 'left', track);
    if (i === 3) {
      const L = layout(ctx, r, f, track), p = E.outQuint(prog(u, 6, 6.4));
      ctx.fillStyle = C.accent; ctx.fillRect(s.x - 8, base + dy - size * 0.32, (L.width + 16) * p, 16);
    }
    ctx.restore();
    if (i === 4) {                                    // "sistema" ganha acento
      const L = layout(ctx, 'É um ', f, track), k2 = springU(u, 7, SPRING.bouncy);
      if (k2 > 0) {
        const L2 = layout(ctx, 'sistema.', f, track);
        const bw = L2.width + 30, bx = s.x + L.width - 12;
        rrect(ctx, bx, base - size * 0.82, bw * Math.min(1, k2), size * 1.0, 18);
        ctx.fillStyle = C.accent; ctx.fill();
        text(ctx, 'sistema.', bx + 15, base, f, C.ink, 'left', track);
      }
    }
  });
}

function sceneFunnel(ctx, u) {
  fill(ctx, C.ink);
  const s = FORMAT.safe;
  const t0 = springU(u, 7.6, SPRING.gentle);
  text(ctx, 'Onde o funil quebra?', s.x, s.y + 140 + (1 - t0) * 60, font(84, 800, DISPLAY), C.paper, 'left', -2.5);
  const stages = [
    ['01', 'Impressão → clique', 'mensagem e intenção'],
    ['02', 'Clique → lead', 'página e oferta'],
    ['03', 'Lead → qualificado', 'segmentação e triagem'],
    ['04', 'Qualificado → contrato', 'atendimento e follow-up'],
  ];
  const widths = [s.w, s.w * 0.84, s.w * 0.68, s.w * 0.52];
  const bh = 250, gap = 34, y0 = s.y + 280;
  stages.forEach(([n, a, b], i) => {
    const k = springU(u, 8 + i, SPRING.snappy);
    if (k <= 0) return;
    const w = widths[i], x = s.x + (s.w - w) / 2, y = y0 + i * (bh + gap);
    const last = i === 3;
    ctx.save();
    ctx.translate(0, (1 - k) * 80); ctx.globalAlpha = Math.min(1, k * 1.5);
    rrect(ctx, x, y, w * 1, bh, 26);
    ctx.fillStyle = last ? C.accent : '#18203A'; ctx.fill();
    const ink = last ? C.ink : C.paper;
    text(ctx, n, x + 40, y + 82, font(48, 800, DISPLAY), last ? C.ink : C.accent);
    text(ctx, a, x + 40, y + 150, font(w < 540 ? 40 : 52, 700, UI), ink);
    text(ctx, b, x + 40, y + 205, font(34, 500, UI), last ? '#3a2a05' : C.mute);
    ctx.restore();
  });
}

function sceneEnd(ctx, u) {
  fill(ctx, C.accent);
  const s = FORMAT.safe;
  lines(ctx, u, [{ t: 'Uma métrica', c: C.ink }, { t: 'por etapa.', c: C.ink }],
    { size: 150, y0: s.y + 420, lh: 190, u0: 11.6, step: 0.5, x: s.x });
  const k = E.outQuint(prog(u, 13.4, 14));
  if (k > 0) {
    ctx.save(); ctx.globalAlpha = k;
    text(ctx, 'Três16 Mídia', s.x, s.y + 880 + (1 - k) * 40, font(76, 800, DISPLAY), C.ink, 'left', -2);
    text(ctx, 'Tráfego pago para advogados', s.x, s.y + 950 + (1 - k) * 40, font(40, 500, UI), C.ink);
    ctx.restore();
  }
}

M.film({
  fonts: [font(100, 800, DISPLAY), font(40, 500, UI), font(40, 700, UI)],
  images: {},
  hits: HITS,
  draw(ctx, u) {
    if (u < 4) sceneHook(ctx, u);
    else if (u < 8) sceneThesis(ctx, u);
    else if (u < 12) sceneFunnel(ctx, u);
    else sceneEnd(ctx, u);
  },
});
