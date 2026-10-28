// Motor de animação determinístico (roda no navegador).
// Modo imediato: a cada frame, redesenha o SVG inteiro em função do tempo t.
// Nada de setTimeout/CSS animation -> o renderizador pode pular para qualquer frame.
(() => {
  const W = 1080, H = 1920;

  // ---------- tema (cores/fontes extraídas dos vídeos de referência) ----------
  const T = {
    bg: '#0b0b10', bg2: '#15151d', line: 'rgba(255,255,255,.14)',
    white: '#f4f1ea', dim: 'rgba(244,241,234,.45)', yellow: '#f5b81c',
    red: '#ff4d4d', green: '#35d07f',
    home: { fill: '#a50044', stripes: '#004d98', ring: '#ffffff' },   // time que ataca (padrão: blaugrana)
    away: { fill: '#f4f1ea', ring: '#ffffff' },   // adversário (branco)
    display: "'Anton','Impact',sans-serif",
    mono: "'JetBrains Mono','DejaVu Sans Mono',monospace",
  };

  // ---------- easing / tween ----------
  const clamp = (x, a = 0, b = 1) => Math.min(b, Math.max(a, x));
  const E = {
    lin: x => x,
    out: x => 1 - Math.pow(1 - x, 3),
    inOut: x => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2),
    back: x => { const c = 1.70158; return 1 + (c + 1) * Math.pow(x - 1, 3) + c * Math.pow(x - 1, 2); },
    elastic: x => x === 0 || x === 1 ? x : Math.pow(2, -9 * x) * Math.sin((x * 10 - .75) * (2 * Math.PI) / 3) + 1,
  };
  // progresso 0..1 de uma janela [t0, t0+d] com easing
  const prog = (t, t0, d = .5, ease = E.out) => ease(clamp((t - t0) / d));
  const lerp = (a, b, k) => a + (b - a) * k;

  // ---------- helpers SVG ----------
  const f = n => (Math.round(n * 100) / 100);
  const g = (attrs, inner) => `<g ${attrs}>${inner}</g>`;
  const esc = s => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;');

  const text = (x, y, s, { size = 28, fill = T.white, font = T.mono, weight = 700, anchor = 'start', op = 1, ls = 0 } = {}) =>
    `<text x="${f(x)}" y="${f(y)}" font-family="${font}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}" opacity="${f(op)}" letter-spacing="${ls}">${esc(s)}</text>`;

  // ---------- componentes ----------
  const C = {};

  // Cabeçalho fixo (@perfil) + rodapé com ícone do Instagram
  C.chrome = (handle, t) => {
    const ig = (x, y) => `<g transform="translate(${x},${y})" fill="none" stroke="${T.white}" stroke-width="5">
      <rect x="0" y="0" width="52" height="52" rx="15"/><circle cx="26" cy="26" r="12"/><circle cx="40" cy="12" r="2" fill="${T.white}"/></g>`;
    return `<circle cx="52" cy="62" r="14" fill="none" stroke="${T.white}" stroke-width="3"/>` +
      text(80, 70, '@' + handle, { size: 24, weight: 500, fill: T.white, op: .9 }) +
      ig(60, 1735) + text(60, 1830, '@' + handle.toUpperCase(), { size: 22, weight: 500 });
  };

  // Título em duas linhas: branca + amarela, com "kicker" pequeno acima.
  // Cada linha sobe e aparece com atraso (stagger), como nos vídeos.
  C.title = (kicker, l1, l2, t, t0 = 0) => {
    const row = (s, y, col, d) => {
      const k = prog(t, t0 + d, .45, E.out);
      return `<g opacity="${f(k)}" transform="translate(0,${f((1 - k) * 36)})">${text(40, y, s, { size: 84, font: T.display, fill: col, weight: 400, ls: 1 })}</g>`;
    };
    const kk = prog(t, t0, .3);
    return `<g opacity="${f(kk)}"><circle cx="46" cy="132" r="6" fill="${T.yellow}"/>${text(66, 140, kicker.toUpperCase(), { size: 22, fill: T.dim, ls: 3 })}</g>` +
      row(l1, 228, T.white, .1) + (l2 ? row(l2, 318, T.yellow, .35) : '');
  };

  // Campo de futebol (vista de cima, vertical). Retorna svg + função de mapeamento.
  // Coordenadas do mundo: x 0..68 (largura), y 0..105 (0 = gol de cima, 105 = gol de baixo).
  C.pitch = (box = { x: 60, y: 400, w: 960, h: 1280 }, opts = {}) => {
    const sx = box.w / 68, sy = box.h / 105;
    const P = (x, y) => [box.x + x * sx, box.y + y * sy];
    const ln = (x1, y1, x2, y2) => { const a = P(x1, y1), b = P(x2, y2); return `<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}"/>`; };
    const rc = (x, y, w, h) => { const a = P(x, y); return `<rect x="${a[0]}" y="${a[1]}" width="${w * sx}" height="${h * sy}"/>`; };
    const [cx, cy] = P(34, 52.5);
    const svg = `<g fill="none" stroke="${T.line}" stroke-width="3" opacity="${opts.op ?? 1}">
      ${rc(0, 0, 68, 105)}${ln(0, 52.5, 68, 52.5)}<circle cx="${cx}" cy="${cy}" r="${9.15 * sx}"/>
      ${rc(13.84, 0, 40.32, 16.5)}${rc(13.84, 88.5, 40.32, 16.5)}${rc(24.84, 0, 18.32, 5.5)}${rc(24.84, 99.5, 18.32, 5.5)}</g>`;
    return { svg, P, sx, sy };
  };

  // Jogador (bolinha). team: 'home' | 'away'. opts.ring destaca, opts.label coloca etiqueta.
  let dotId = 0;
  C.dot = (px, py, team = 'home', { r = 17, ring = false, label = '', t = 0, op = 1, gk = false } = {}) => {
    const c = T[team];
    let s = `<g opacity="${f(op)}">`;
    if (ring) {
      const pulse = 1 + .12 * Math.sin(t * 6);
      s += `<circle cx="${f(px)}" cy="${f(py)}" r="${f(r * 2.1 * pulse)}" fill="${T.yellow}" fill-opacity=".12" stroke="${T.yellow}" stroke-width="3"/>`;
    }
    const rr = gk ? r * .8 : r, cid = 'dt' + (dotId++);
    s += `<circle cx="${f(px)}" cy="${f(py)}" r="${rr}" fill="${gk ? '#ff9f43' : c.fill}"/>`;
    if (c.stripes && !gk) s += `<clipPath id="${cid}"><circle cx="${f(px)}" cy="${f(py)}" r="${rr}"/></clipPath><g clip-path="url(#${cid})"><rect x="${f(px - rr * .55)}" y="${f(py - rr)}" width="${f(rr * .5)}" height="${rr * 2}" fill="${c.stripes}"/><rect x="${f(px + rr * .05)}" y="${f(py - rr)}" width="${f(rr * .5)}" height="${rr * 2}" fill="${c.stripes}"/></g>`;
    s += `<circle cx="${f(px)}" cy="${f(py)}" r="${rr}" fill="none" stroke="${ring ? T.yellow : c.ring}" stroke-width="3"/>`;
    if (label) s += C.tag(px + r * 2.4, py + 6, label, { color: T.yellow });
    return s + '</g>';
  };

  // Etiqueta com borda arredondada (estilo "MBAPPÉ", "REAL COMPACTO")
  C.tag = (x, y, s, { color = T.white, size = 20, anchor = 'start', op = 1 } = {}) => {
    const w = s.length * size * .66 + 24;
    const x0 = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x;
    return `<g opacity="${f(op)}"><rect x="${f(x0)}" y="${f(y - size - 6)}" width="${f(w)}" height="${size + 18}" rx="7" fill="rgba(11,11,16,.85)" stroke="${color}" stroke-width="2"/>` +
      text(x0 + w / 2, y + 2, s.toUpperCase(), { size, fill: color, anchor: 'middle', weight: 700 }) + '</g>';
  };

  // Seta animada (desenha-se de a para b conforme k 0..1)
  C.arrow = (a, b, k, { color = T.green, dashed = false, w = 6 } = {}) => {
    const x = lerp(a[0], b[0], k), y = lerp(a[1], b[1], k);
    const ang = Math.atan2(b[1] - a[1], b[0] - a[0]), hs = 22;
    const head = k > .02 ? `<polygon points="${f(x)},${f(y)} ${f(x - hs * Math.cos(ang - .45))},${f(y - hs * Math.sin(ang - .45))} ${f(x - hs * Math.cos(ang + .45))},${f(y - hs * Math.sin(ang + .45))}" fill="${color}"/>` : '';
    return `<line x1="${f(a[0])}" y1="${f(a[1])}" x2="${f(x)}" y2="${f(y)}" stroke="${color}" stroke-width="${w}" stroke-linecap="round" ${dashed ? 'stroke-dasharray="14 12"' : ''}/>` + head;
  };

  // Caixa tracejada (ex.: "REAL COMPACTO")
  C.zone = (x, y, w, h, label, k = 1, color = T.yellow) =>
    `<g opacity="${f(k)}"><rect x="${x}" y="${y}" width="${w}" height="${h}" rx="10" fill="${color}" fill-opacity=".10" stroke="${color}" stroke-width="3" stroke-dasharray="12 8"/>` +
    text(x + 14, y - 12, label.toUpperCase(), { size: 18, fill: color, ls: 1 }) + '</g>';

  // Placar compacto (BAR 0 x 0 RMA) + minuto
  C.score = (s, minute, x = 1020, y = 395) =>
    `<rect x="${x - 230}" y="${y - 40}" width="230" height="56" rx="8" fill="rgba(11,11,16,.9)" stroke="${T.line}" stroke-width="2"/>` +
    text(x - 115, y - 2, s, { size: 28, anchor: 'middle' }) +
    (minute ? `<rect x="${x - 76}" y="${y + 24}" width="76" height="36" rx="6" fill="${T.yellow}"/>` + text(x - 38, y + 50, minute, { size: 22, anchor: 'middle', fill: '#111' }) : '');

  // Número gigante amarelo (contagem animada)
  C.bigNumber = (value, t, t0, { x = 700, y = 1180, size = 560, sub = '', dur = 1.2 } = {}) => {
    const k = prog(t, t0, dur, E.out);
    const v = Math.round(value * k);
    const pop = prog(t, t0, .4, E.back);
    return `<g opacity="${f(clamp(pop))}">${text(x, y, String(v), { size, font: T.display, fill: T.yellow, anchor: 'middle', weight: 400 })}` +
      (sub ? text(x, y + 70, sub.toUpperCase(), { size: 28, anchor: 'middle', fill: T.dim, ls: 3 }) : '') + '</g>';
  };

  // Barras comparativas [{label,value,color}]
  C.bars = (items, t, t0, { x = 200, base = 1500, maxH = 700, bw = 240, gap = 60 } = {}) => {
    const max = Math.max(...items.map(i => i.value));
    return items.map((it, i) => {
      const k = prog(t, t0 + i * .25, .9, E.out), h = (it.value / max) * maxH * k, bx = x + i * (bw + gap);
      return `<rect x="${bx}" y="${f(base - h)}" width="${bw}" height="${f(h)}" rx="6" fill="${it.color}"/>` +
        text(bx + bw / 2, base - h - 20, String(Math.round(it.value * k)), { size: 56, font: T.display, anchor: 'middle', weight: 400, fill: T.white }) +
        text(bx + bw / 2, base + 40, it.label, { size: 22, anchor: 'middle', fill: T.dim });
    }).join('');
  };

  // Piso/palco dos bonecos (gradiente cinza no chão)
  C.floor = (y = 1500) =>
    `<rect x="0" y="${y}" width="${W}" height="6" fill="rgba(255,255,255,.12)"/><rect x="0" y="${y + 6}" width="${W}" height="200" fill="url(#floorg)"/>`;

  // ---------- Boneco v2 (articulado) ----------
  // Origem nos pés. Braços/pernas são 2 segmentos (ângulo a partir da vertical p/ baixo; + = para fora).
  // pose: nome | { a:'idle', b:'armsUp', k:0..1 } (transição suave). Poses: idle, armsUp, crossed,
  // hands-on-head, ball (embaixadinha), point, shrug, cheer, hip.
  // kit: shirt, sleeve, stripes (vertical), hoops (horizontal), shorts, socks, skin, hair, hairStyle
  //      ('short'|'long'|'bald'), number, longSleeve, boots, collar.
  const POSES = {
    //            braço dir [alto, antebraço]   braço esq          perna dir [coxa, canela]  perna esq
    idle:           { r: [8, 4],     l: [8, 4],      rl: [2, 0],   ll: [-2, 0] },
    armsUp:         { r: [150, 172], l: [150, 172],  rl: [4, 0],   ll: [-4, 0] },
    cheer:          { r: [135, 160], l: [135, 160],  rl: [6, 0],   ll: [-6, 0] },
    crossed:        { r: [22, -92],  l: [22, -96],   rl: [2, 0],   ll: [-2, 0] },
    'hands-on-head':{ r: [112, 246], l: [112, 246],  rl: [3, 0],   ll: [-3, 0] },
    ball:           { r: [58, 40],   l: [64, 50],    rl: [-24, 30], ll: [-2, 0] },
    point:          { r: [96, 98],   l: [10, 4],     rl: [2, 0],   ll: [-2, 0] },
    shrug:          { r: [60, 120],  l: [60, 120],   rl: [2, 0],   ll: [-2, 0] },
    hip:            { r: [50, -60],  l: [50, -60],   rl: [2, 0],   ll: [-2, 0] },
  };
  const poseVals = (p) => {
    if (typeof p === 'string') return POSES[p] || POSES.idle;
    const A = POSES[p.a] || POSES.idle, B = POSES[p.b] || POSES.idle, k = p.k;
    const m = (x, y) => x.map((v, i) => v + (y[i] - v) * k);
    return { r: m(A.r, B.r), l: m(A.l, B.l), rl: m(A.rl, B.rl), ll: m(A.ll, B.ll) };
  };
  let figId = 0;
  C.figure = (cx, groundY, kit, { pose = 'idle', scale = 1, t = 0, label = '', bob = true, op = 1, coat = false, flip = false } = {}) => {
    const s = scale, id = 'fg' + (figId++), P = poseVals(pose);
    const skin = kit.skin || '#d9a07a', dark = (c, a = .18) => `<rect x="-200" y="-600" width="200" height="620" fill="#000" opacity="${a}" clip-path="url(#${id}b)"/>`;
    const isCoat = coat || kit.coat;
    const sway = bob ? Math.sin(t * 2.2) * 2 : 0, breathe = bob ? Math.sin(t * 3) * 2 : 0;
    const dir = (deg, side) => [side * Math.sin(deg * Math.PI / 180), Math.cos(deg * Math.PI / 180)];
    const cap = (x1, y1, x2, y2, w, col, extra = '') => `<line x1="${f(x1)}" y1="${f(y1)}" x2="${f(x2)}" y2="${f(y2)}" stroke="${col}" stroke-width="${w}" stroke-linecap="round" ${extra}/>`;
    const sleeveCol = kit.sleeve || kit.shirt, edge = isCoat ? 'rgba(255,255,255,.22)' : '';
    // ----- membros -----
    const limb = (hip, [a1, a2], l1, l2, side) => { const d1 = dir(a1, side), d2 = dir(a2, side); const kx = hip[0] + d1[0] * l1, ky = hip[1] + d1[1] * l1; return { k: [kx, ky], e: [kx + d2[0] * l2, ky + d2[1] * l2] }; };
    const legR = limb([22, -222], P.rl, 100, 100, 1), legL = limb([-22, -222], P.ll, 100, 100, 1);
    const sh = -400 + breathe;
    const armR = limb([62, sh + 6], P.r, 86, 80, 1), armL = limb([-62, sh + 6], P.l, 86, 80, -1);
    const sockCol = kit.socks || kit.shorts, boot = kit.boots || '#0c0c0f';
    const legSvg = (hip, L, side) => {
      const ex = L.e[0], ey = L.e[1], sx = L.k[0] + (ex - L.k[0]) * .22, sy = L.k[1] + (ey - L.k[1]) * .22;
      if (isCoat) return cap(hip[0], hip[1], L.k[0], L.k[1], 38, '#2b3144') + cap(L.k[0], L.k[1], ex, ey, 34, '#2b3144') +
        `<ellipse cx="${f(ex + side * 4)}" cy="${f(ey - 6)}" rx="26" ry="13" fill="${boot}"/>`;
      return cap(hip[0], hip[1], L.k[0], L.k[1], 28, skin) + cap(L.k[0], L.k[1], ex, ey, 26, skin) +
        cap(sx, sy, ex, ey, 31, sockCol) + `<ellipse cx="${f(ex + side * 5)}" cy="${f(ey - 4)}" rx="25" ry="12" fill="${boot}"/>`;
    };
    // ----- tronco -----
    const shirtPath = `M-66,${sh + 2} Q0,${sh - 12} 66,${sh + 2} L58,-262 Q0,-250 -58,-262 Z`;
    let shirtFill = `<path d="${shirtPath}" fill="${kit.shirt}"/>`;
    const clip = `<clipPath id="${id}b"><path d="${shirtPath}"/></clipPath>`;
    if (kit.stripes) for (let i = -3; i <= 3; i++) if (i % 2 === 0) shirtFill += `<rect x="${i * 24 - 12}" y="-420" width="24" height="170" fill="${kit.stripes}" clip-path="url(#${id}b)"/>`;
    if (kit.hoops) for (let i = 0; i < 6; i++) if (i % 2 === 0) shirtFill += `<rect x="-80" y="${sh + 14 + i * 22}" width="160" height="22" fill="${kit.hoops}" clip-path="url(#${id}b)"/>`;
    shirtFill += dark(0, .08);
    const collarC = kit.collar || skin;
    const neck = `<rect x="-14" y="${sh - 34}" width="28" height="44" rx="10" fill="${skin}"/>`;
    const vneck = isCoat
      ? `<path d="M-26,${sh} L0,${sh + 56} L26,${sh} L16,${sh - 6} L0,${sh + 22} L-16,${sh - 6} Z" fill="#e8e8ee" opacity=".9"/>`
      : `<path d="M-24,${sh - 2} L0,${sh + 38} L24,${sh - 2} Q0,${sh + 10} -24,${sh - 2} Z" fill="${skin}"/>`;
    const shorts = isCoat ? '' :
      `<rect x="-62" y="-270" width="124" height="62" rx="12" fill="${kit.shorts}"/><rect x="-62" y="-270" width="124" height="62" rx="12" fill="#000" opacity=".1"/>` +
      (kit.number != null ? text(-36, -226, String(kit.number), { size: 34, anchor: 'middle', fill: kit.numColor || T.yellow }) : '');
    const coatBody = isCoat
      ? `<path d="M-72,${sh} Q0,${sh - 14} 72,${sh} L96,-70 Q0,-52 -96,-70 Z" fill="${kit.shirt}" stroke="rgba(255,255,255,.28)" stroke-width="3"/>` +
        `<path d="M0,${sh + 10} L0,-62" stroke="rgba(255,255,255,.18)" stroke-width="3"/><circle cx="0" cy="-250" r="5" fill="rgba(255,255,255,.3)"/><circle cx="0" cy="-190" r="5" fill="rgba(255,255,255,.3)"/>` : '';
    // ----- braços -----
    const armSvg = (A, side) => {
      const sc = kit.longSleeve || isCoat;
      const sx = side * 62, sy = sh + 6;
      let out = '';
      // braço de pele (parte exposta) + manga
      out += cap(A.k[0], A.k[1], A.e[0], A.e[1], 24, skin);
      out += cap(sx, sy, A.k[0], A.k[1], 26, skin);
      if (sc) { out += cap(A.k[0], A.k[1], A.e[0], A.e[1], 30, sleeveCol) + cap(sx, sy, A.k[0], A.k[1], 33, sleeveCol); if (isCoat) out += cap(A.k[0], A.k[1], A.e[0], A.e[1], 30, 'none', 'stroke="rgba(255,255,255,.2)" stroke-width="2"'); }
      else { out += cap(sx, sy, sx + (A.k[0] - sx) * .55, sy + (A.k[1] - sy) * .55, 31, sleeveCol); }
      out += `<circle cx="${f(A.e[0])}" cy="${f(A.e[1])}" r="${sc ? 15 : 13}" fill="${skin}"/>`;
      return out;
    };
    // ----- cabeça -----
    const hy = sh - 70, hairC = kit.hair || '#2a1a12', hs = kit.hairStyle || 'short';
    let head = `<circle cx="-40" cy="${hy + 8}" r="9" fill="${skin}"/><circle cx="40" cy="${hy + 8}" r="9" fill="${skin}"/><ellipse cx="0" cy="${hy}" rx="38" ry="46" fill="${skin}"/>`;
    if (hs === 'short') head += `<path d="M-40,${hy - 4} Q-42,${hy - 56} 0,${hy - 56} Q42,${hy - 56} 40,${hy - 4} Q30,${hy - 30} 0,${hy - 28} Q-30,${hy - 30} -40,${hy - 4} Z" fill="${hairC}"/>`;
    if (hs === 'long') head += `<path d="M-44,${hy + 40} Q-52,${hy - 60} 0,${hy - 58} Q52,${hy - 60} 44,${hy + 40} L32,${hy + 12} Q30,${hy - 26} 0,${hy - 26} Q-30,${hy - 26} -32,${hy + 12} Z" fill="${hairC}"/>`;
    // ----- composição -----
    const body = `<ellipse cx="0" cy="2" rx="${isCoat ? 120 : 92}" ry="13" fill="#000" opacity=".4"/>` +
      legSvg([-22, -222], legL, -1) + legSvg([22, -222], legR, 1) +
      (isCoat ? coatBody : `<defs>${clip}</defs>${shirtFill}${shorts}`) +
      (isCoat ? `<defs>${clip}</defs>` : '') + neck + (isCoat ? '' : '') + vneck +
      armSvg(armL, -1) + armSvg(armR, 1) + head;
    const lab = label ? C.tag(cx, groundY - 575 * s, label, { color: T.white, anchor: 'middle', size: 20 }) : '';
    const tf = `translate(${f(cx + sway)},${f(groundY)}) scale(${flip ? -s : s},${s})`;
    return `<g opacity="${f(op)}"><g transform="${tf}">${body}</g>${lab}</g>`;
  };
  C.kits = {
    barca:    { shirt: '#a50044', stripes: '#004d98', sleeve: '#004d98', shorts: '#12306b', socks: '#12306b', number: 8, skin: '#d9a07a', hair: '#4a2c1c', collar: '#d9a07a' },
    realAway: { shirt: '#f4f1ea', sleeve: '#f4f1ea', shorts: '#f4f1ea', socks: '#f4f1ea', number: 10, numColor: '#444', skin: '#8a5a3c', hair: '#16100e' },
    coach:    { shirt: '#1d2230', shorts: '#1d2230', socks: '#1d2230', skin: '#e0cdbd', hair: '#b9bdc4', coat: true, longSleeve: true },
    gk:       { shirt: '#9be52a', sleeve: '#9be52a', shorts: '#1c1c20', socks: '#9be52a', skin: '#d9a07a', hair: '#3a2416', hairStyle: 'long', longSleeve: true, numColor: '#fff' },
    red:      { shirt: '#d4202a', sleeve: '#d4202a', shorts: '#d4202a', socks: '#d4202a', number: 9, skin: '#e0b090', hair: '#7a4a28', numColor: '#fff' },
    flamengo: { shirt: '#d4202a', hoops: '#111', sleeve: '#d4202a', shorts: '#f4f1ea', socks: '#111', number: 9, numColor: '#111', skin: '#b87a52', hair: '#1a1210' },
  };

  // CTA final: "COMENTA AÍ" + "SEGUE PRA PRÓXIMA ANÁLISE"
  C.cta = (t, t0) => {
    const k = prog(t, t0, .4, E.back);
    return `<g opacity="${f(clamp(k))}" transform="translate(0,${f((1 - k) * 20)})">` +
      C.tag(W / 2, 700, 'comenta aí', { anchor: 'middle', size: 26 }) +
      C.tag(W / 2, 770, '● segue pra próxima análise', { anchor: 'middle', color: T.yellow, size: 20 }) + '</g>';
  };

  // ---------- compositor de cenas ----------
  // episode = { handle, scenes:[{dur, draw(t, api)}], fade: .25 }
  function frame(ep, time) {
    let acc = 0, scene = ep.scenes[ep.scenes.length - 1], lt = 0, idx = ep.scenes.length - 1;
    for (let i = 0; i < ep.scenes.length; i++) {
      if (time < acc + ep.scenes[i].dur) { scene = ep.scenes[i]; lt = time - acc; idx = i; break; }
      acc += ep.scenes[i].dur;
      if (i === ep.scenes.length - 1) lt = scene.dur;
    }
    const fade = ep.fade ?? .25;
    const fin = idx === 0 ? 1 : clamp(lt / fade), fout = clamp((scene.dur - lt) / fade);
    const api = { T, E, C, W, H, prog, lerp, clamp, text, f, g };
    const body = scene.draw(lt, api);
    const defs = `<defs><linearGradient id="floorg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2a2a33"/><stop offset="1" stop-color="${T.bg}"/></linearGradient>
      <radialGradient id="vig" cx="50%" cy="38%" r="75%"><stop offset="0" stop-color="#1a1a24"/><stop offset="1" stop-color="${T.bg}"/></radialGradient></defs>`;
    return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${H}" viewBox="0 0 ${W} ${H}">${defs}` +
      `<rect width="${W}" height="${H}" fill="url(#vig)"/>` +
      `<g opacity="${f(Math.min(fin, fout))}">${body}</g>${C.chrome ? '' : ''}` +
      (scene.chrome === false ? '' : `<g>${C.chrome(ep.handle, lt)}</g>`) + '</svg>';
  }

  window.Studio = { frame, T, E, C, W, H, prog, lerp, clamp, text,
    duration: ep => ep.scenes.reduce((a, s) => a + s.dur, 0),
    render(ep, t) { document.getElementById('stage').innerHTML = frame(ep, t); } };
})();
