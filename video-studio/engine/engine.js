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
    home: { fill: '#7a2cff', ring: '#c9a4ff' },   // time "nosso" (roxo)
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
  C.dot = (px, py, team = 'home', { r = 17, ring = false, label = '', t = 0, op = 1, gk = false } = {}) => {
    const c = T[team];
    let s = `<g opacity="${f(op)}">`;
    if (ring) {
      const pulse = 1 + .12 * Math.sin(t * 6);
      s += `<circle cx="${f(px)}" cy="${f(py)}" r="${f(r * 2.1 * pulse)}" fill="${T.yellow}" fill-opacity=".12" stroke="${T.yellow}" stroke-width="3"/>`;
    }
    s += `<circle cx="${f(px)}" cy="${f(py)}" r="${gk ? r * .8 : r}" fill="${gk ? '#ff9f43' : c.fill}" stroke="${ring ? T.yellow : c.ring}" stroke-width="3"/>`;
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

  // Boneco chapado (estilo dos vídeos): cabeça, tronco com camisa, calção, pernas, meias.
  // kit: {shirt, shirt2?, stripes?, shorts, socks, skin, hair, number}
  // pose: 'idle' | 'armsUp' | 'crossed' | 'hands-on-head' | 'ball'
  C.figure = (cx, groundY, kit, { pose = 'idle', scale = 1, t = 0, label = '', bob = true, op = 1, coat = false } = {}) => {
    const s = scale, by = bob ? Math.sin(t * 3) * 3 * s : 0;
    const top = groundY - 520 * s + by;
    const P = (dx, dy) => `${f(cx + dx * s)},${f(top + dy * s)}`;
    const skin = kit.skin || '#c98f67', arm = (x1, y1, x2, y2, col = kit.sleeve || kit.shirt) =>
      `<line x1="${f(cx + x1 * s)}" y1="${f(top + y1 * s)}" x2="${f(cx + x2 * s)}" y2="${f(top + y2 * s)}" stroke="${col}" stroke-width="${30 * s}" stroke-linecap="round"/>`;
    let arms = '';
    if (pose === 'armsUp') arms = arm(-60, 150, -105, 30) + arm(60, 150, 105, 30);
    else if (pose === 'crossed') arms = arm(-60, 150, 40, 235) + arm(60, 150, -40, 235);
    else if (pose === 'hands-on-head') arms = arm(-60, 150, -45, 50) + arm(60, 150, 45, 50);
    else if (pose === 'ball') arms = arm(-60, 150, -120, 230) + arm(60, 150, 120, 230);
    else arms = arm(-60, 150, -80, 300) + arm(60, 150, 80, 300);
    const legs = `<rect x="${f(cx - 52 * s)}" y="${f(top + 330 * s)}" width="${34 * s}" height="${150 * s}" fill="${skin}"/><rect x="${f(cx + 18 * s)}" y="${f(top + 330 * s)}" width="${34 * s}" height="${150 * s}" fill="${skin}"/>` +
      `<rect x="${f(cx - 52 * s)}" y="${f(top + 420 * s)}" width="${34 * s}" height="${100 * s}" fill="${kit.socks}"/><rect x="${f(cx + 18 * s)}" y="${f(top + 420 * s)}" width="${34 * s}" height="${100 * s}" fill="${kit.socks}"/>`;
    const stripes = kit.stripes ? [-60, -20, 20, 60].map(d => `<rect x="${f(cx + (d - 10) * s)}" y="${f(top + 130 * s)}" width="${20 * s}" height="${200 * s}" fill="${kit.stripes}"/>`).join('') : '';
    const body = coat
      ? `<path d="M${P(-75, 130)} L${P(75, 130)} L${P(95, 480)} L${P(-95, 480)} Z" fill="${kit.shirt}"/>`
      : `<rect x="${f(cx - 75 * s)}" y="${f(top + 120 * s)}" width="${150 * s}" height="${215 * s}" rx="${22 * s}" fill="${kit.shirt}"/>${stripes}<rect x="${f(cx - 70 * s)}" y="${f(top + 310 * s)}" width="${140 * s}" height="${70 * s}" rx="${10 * s}" fill="${kit.shorts}"/>` +
        (kit.number ? text(cx, top + 365 * s, String(kit.number), { size: 34 * s, anchor: 'middle', fill: T.yellow, weight: 700 }) : '');
    const head = `<ellipse cx="${f(cx)}" cy="${f(top + 62 * s)}" rx="${46 * s}" ry="${54 * s}" fill="${skin}"/>` +
      `<path d="M${P(-48, 50)} Q${P(0, -26)} ${P(48, 50)} Q${P(0, 12)} ${P(-48, 50)} Z" fill="${kit.hair || '#2a1a12'}"/>`;
    const lab = label ? C.tag(cx, top - 24 * s, label, { color: T.white, anchor: 'middle', size: 20 }) : '';
    return `<g opacity="${f(op)}">${legs}${body}${arms}${head}${lab}</g>`;
  };
  // Kits prontos (troque cores = troque de time)
  C.kits = {
    barca: { shirt: '#a50044', stripes: '#004d98', sleeve: '#004d98', shorts: '#12306b', socks: '#12306b', number: 8, skin: '#d9a07a' },
    realAway: { shirt: '#f4f1ea', sleeve: '#f4f1ea', shorts: '#f4f1ea', socks: '#f4f1ea', number: 10, skin: '#8a5a3c', hair: '#1a1210' },
    coach: { shirt: '#1d2230', shorts: '#1d2230', socks: '#1d2230', skin: '#d8c9bd', hair: '#b9bdc4' },
    gk: { shirt: '#9be52a', sleeve: '#9be52a', shorts: '#222', socks: '#9be52a', skin: '#c98f67' },
    red: { shirt: '#d4202a', sleeve: '#d4202a', shorts: '#d4202a', socks: '#d4202a', number: 9, skin: '#e0b090' },
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
