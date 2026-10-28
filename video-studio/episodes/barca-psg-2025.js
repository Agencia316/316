// BARÇA 1 x 2 PSG — Champions 2025/26, rodada 2, 01/10/2025 (Montjuïc). Versão enxuta: só fatos confirmados.
// Posições das bolinhas são ILUSTRATIVAS (escalações/formações não confirmadas).
(() => {
  const { F, mirror } = Formations, { T, C } = Studio;
  T.away = { fill: '#3d8bff', ring: '#ffffff' };           // PSG: azul claro, distinto das listras do Barça
  const BAR = F['4-3-3'], PSG = mirror(F['4-3-3']);
  const kBar = { ...C.kits.barca, number: 7 };
  const kPsg = { shirt: '#14346b', band: '#d4202a', sleeve: '#14346b', shorts: '#f4f1ea', socks: '#d4202a', number: 9, numColor: '#14346b', skin: '#c98f67', hair: '#1a1210' };
  const dots = (a, pitch, home, away, t, hl = {}) => {
    let s = '';
    away.forEach((p, i) => { const [x, y] = pitch.P(...p); s += a.C.dot(x, y, 'away', { gk: i === 0, t, ...(hl.away?.[i] || {}) }); });
    home.forEach((p, i) => { const [x, y] = pitch.P(...p); s += a.C.dot(x, y, 'home', { gk: i === 0, t, ...(hl.home?.[i] || {}) }); });
    return s;
  };
  const mv = (p, to, k) => [p[0] + (to[0] - p[0]) * k, p[1] + (to[1] - p[1]) * k];
  const note = (a, t) => `<g opacity="${a.prog(t, .6)}">${C.tag(540, 1740, 'posições ilustrativas', { anchor: 'middle', size: 16, color: T.dim })}</g>`;
  const score = (s, m) => C.score(s, m, 1010, 440);

  window.EPISODE = { handle: 'seu.perfil', fade: .25, scenes: [
    // 1 — GANCHO
    { dur: 5, draw: (t, a) => { const { prog } = a;
      return C.title('Champions · 01/10/2025', 'O BARÇA ABRIU.', 'O PSG VIROU.', t) +
        `<g opacity="${prog(t, 1.1)}">${a.text(540, 640, 'BARÇA 1 x 2 PSG', { size: 60, font: T.display, anchor: 'middle', weight: 400 })}${C.tag(540, 700, 'FASE DE LIGA · RODADA 2 · MONTJUÏC', { anchor: 'middle', size: 18, color: T.dim })}</g>` +
        C.floor(1500) + C.figure(300, 1500, kBar, { pose: 'hands-on-head', scale: 1.15, t, label: 'BARÇA', op: prog(t, 1.6, .5) }) +
        C.figure(780, 1500, kPsg, { pose: 'cheer', scale: 1.15, t, label: 'PSG', op: prog(t, 2, .5) }); } },
    // 2 — PSG desfalcado
    { dur: 5, draw: (t, a) => { const { prog, E } = a, pitch = C.pitch();
      const out = [8, 9, 10];                                                   // 3 atacantes "somem"
      const away = PSG.map((p, i) => out.includes(i) ? mv(p, [p[0], p[1] - 30], prog(t, 2, 1, E.inOut)) : p);
      const hl = {}; out.forEach(i => hl[i] = { op: 1 - prog(t, 2, 1) * .85 });
      return C.title('O cenário', 'O PSG CHEGOU', 'DESFALCADO.', t) + pitch.svg + dots(a, pitch, BAR, away, t, { away: hl }) +
        `<g opacity="${prog(t, 2.8)}">${C.tag(540, 560, 'sem parte do ataque titular · segundo a imprensa', { anchor: 'middle', size: 18, color: T.yellow })}</g>` + note(a, t); } },
    // 3 — 19' Torres, assist Rashford
    { dur: 7, draw: (t, a) => { const { prog, E } = a, pitch = C.pitch();
      const k1 = prog(t, 1.2, 1, E.inOut), k2 = prog(t, 2.4, .8, E.inOut), gol = t > 3.2;
      const home = BAR.map(p => p.slice()); home[10] = mv(BAR[10], [58, 22], k1); home[9] = mv(BAR[9], [36, 12], k1);
      const rash = pitch.P(...home[10]), tor = pitch.P(...home[9]), ball = [a.lerp(rash[0], tor[0], k2), a.lerp(rash[1], tor[1], k2)];
      return C.title("19'", 'UMA ASSISTÊNCIA.', 'UM GOL. 1 x 0.', t) + pitch.svg +
        dots(a, pitch, home, PSG, t, { home: { 9: { ring: t > 1.4, label: t > 1.4 ? 'TORRES' : '', t }, 10: { label: t > 1.4 ? 'RASHFORD' : '', t } } }) +
        C.arrow(rash, tor, k2, { color: T.yellow, w: 7 }) + `<circle cx="${ball[0]}" cy="${ball[1]}" r="9" fill="#fff"/>` +
        (gol ? `<g opacity="${prog(t, 3.2, .35, E.back)}">${a.text(540, 1060, 'GOL', { size: 240, font: T.display, anchor: 'middle', weight: 400, fill: T.yellow })}</g>` : '') +
        score(gol ? 'BAR 1 x 0 PSG' : 'BAR 0 x 0 PSG', "19'") + note(a, t); } },
    // 4 — 38' Mayulu, assist Nuno Mendes
    { dur: 7, draw: (t, a) => { const { prog, E } = a, pitch = C.pitch();
      const k1 = prog(t, 1.2, 1.2, E.inOut), k2 = prog(t, 2.6, .8, E.inOut), gol = t > 3.4;
      const psg = PSG.map(p => p.slice()); psg[4] = mv(PSG[4], [60, 76], k1); psg[9] = mv(PSG[9], [34, 92], k1);
      const nm = pitch.P(...psg[4]), may = pitch.P(...psg[9]), ball = [a.lerp(nm[0], may[0], k2), a.lerp(nm[1], may[1], k2)];
      return C.title("38'", 'O EMPATE ANTES', 'DO INTERVALO.', t) + pitch.svg +
        dots(a, pitch, BAR.map(([x, y]) => [x, y + 4]), psg, t, { away: { 9: { ring: t > 1.6, label: t > 1.6 ? 'MAYULU' : '', t }, 4: { label: t > 1.6 ? 'N. MENDES' : '', t } } }) +
        C.arrow(nm, may, k2, { color: T.yellow, w: 7 }) + `<circle cx="${ball[0]}" cy="${ball[1]}" r="9" fill="#fff"/>` +
        (gol ? `<g opacity="${prog(t, 3.4, .35, E.back)}">${a.text(540, 1060, 'GOL', { size: 240, font: T.display, anchor: 'middle', weight: 400, fill: T.yellow })}</g>` : '') +
        score(gol ? 'BAR 1 x 1 PSG' : 'BAR 1 x 0 PSG', "38'") + note(a, t); } },
    // 5 — 90'+ Ramos
    { dur: 8, draw: (t, a) => { const { prog, E } = a, pitch = C.pitch();
      const k1 = prog(t, 1.4, 1.6, E.inOut), k2 = prog(t, 3.2, .8, E.inOut), gol = t > 4;
      const psg = PSG.map(p => p.slice()); psg[9] = mv(PSG[9], [38, 94], k1);
      const from = pitch.P(...PSG[6]), ram = pitch.P(...psg[9]), ball = [a.lerp(from[0], ram[0], k2), a.lerp(from[1], ram[1], k2)];
      return C.title("90'+", 'O GOL NO ÚLTIMO LANCE.', '1 x 2.', t) + pitch.svg +
        dots(a, pitch, BAR.map(([x, y]) => [x, y - 8]), psg, t, { away: { 9: { ring: t > 1.6, label: t > 1.6 ? 'RAMOS' : '', t } } }) +
        C.arrow(from, ram, k2, { color: T.yellow, w: 7 }) + `<circle cx="${ball[0]}" cy="${ball[1]}" r="9" fill="#fff"/>` +
        (gol ? `<g opacity="${prog(t, 4, .35, E.back)}">${a.text(540, 1060, 'GOL', { size: 240, font: T.display, anchor: 'middle', weight: 400, fill: T.yellow })}</g>` : '') +
        score(gol ? 'BAR 1 x 2 PSG' : 'BAR 1 x 1 PSG', "90'+") + note(a, t); } },
    // 6 — frescor
    { dur: 6, draw: (t, a) => { const { prog } = a;
      return C.title('A leitura', 'O BARÇA PAGOU POR', 'FALTA DE FRESCOR?', t) + C.floor(1500) +
        C.figure(300, 1500, kBar, { pose: 'hands-on-head', scale: 1.1, t, label: 'BARÇA: SEM FRESCOR?', op: prog(t, 1) }) +
        C.figure(780, 1500, kPsg, { pose: 'crossed', scale: 1.1, t, label: 'PSG: DESFALCADO', op: prog(t, 1.4) }) +
        `<g opacity="${prog(t, 2.4)}">${C.tag(540, 760, 'relato da imprensa francesa · Pedri saiu cansado', { anchor: 'middle', size: 18, color: T.yellow })}</g>`; } },
    // 7 — pergunta + CTA
    { dur: 8, draw: (t, a) => { const { prog } = a;
      return C.title('A pergunta', 'O BARÇA CANSOU', 'OU O PSG FOI MAIS ESPERTO?', t) + C.floor(1500) +
        C.figure(280, 1500, kBar, { pose: 'hands-on-head', scale: 1, t, label: 'CANSOU', op: prog(t, .8) }) +
        a.text(540, 1250, 'VS', { size: 90, font: T.display, anchor: 'middle', weight: 400, fill: T.dim, op: prog(t, 1.2) }) +
        C.figure(800, 1500, kPsg, { pose: 'cheer', scale: 1, t, label: 'FOI ESPERTO', op: prog(t, 1) }) + C.cta(t, 2.2); } },
  ] };
})();
