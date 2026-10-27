// EPISÓDIO DE EXEMPLO — reproduz a "gramática" dos vídeos de referência (clássico BAR x RMA).
// Dados/textos são só ilustrativos: troque pelo seu tema. Cada cena = { dur, draw(t, api) }.
(() => {
  const { F, mirror, morph, shift } = Formations;
  const HOME = F['4-3-3'];                 // time de baixo (roxo)
  const AWAY = mirror(F['4-4-2']);         // time de cima (branco)

  // Desenha os dois times a partir de listas de posições (já em coordenadas do mundo)
  const teams = (api, pitch, home, away, t, hl = {}) => {
    const { C } = api; let s = '';
    away.forEach((p, i) => { const [x, y] = pitch.P(...p); s += C.dot(x, y, 'away', { gk: i === 0, t, ...(hl.away?.[i] || {}) }); });
    home.forEach((p, i) => { const [x, y] = pitch.P(...p); s += C.dot(x, y, 'home', { gk: i === 0, t, ...(hl.home?.[i] || {}) }); });
    return s;
  };

  window.EPISODE = {
    handle: 'seu.perfil', fade: .25,
    scenes: [
      // 1 — GANCHO: dois personagens + título que entra em 2 linhas
      { dur: 4.5, draw: (t, a) => {
        const { C, T, prog, E } = a;
        return C.title('O clássico', 'O BARÇA TEVE A BOLA.', 'O MOURINHO TEVE O JOGO.', t) +
          C.tag(540, 560, 'FINAL · CAMP NOU · 25/10', { anchor: 'middle', color: T.dim, size: 18, op: prog(t, 1.2) }) +
          `<g opacity="${prog(t, 1.2)}">${a.text(540, 640, 'BAR 1 x 2 RMA', { size: 56, font: T.display, anchor: 'middle', weight: 400 })}</g>` +
          C.floor(1500) +
          C.figure(300, 1500, C.kits.barca, { pose: 'ball', scale: 1.15, t, label: 'BARÇA: A BOLA', op: prog(t, 1.8, .5) }) +
          C.figure(780, 1500, C.kits.coach, { pose: 'crossed', scale: 1.15, t, coat: true, label: 'MOURINHO: O JOGO', op: prog(t, 2.2, .5) });
      } },

      // 2 — CENÁRIO: campo + times entram deslizando; sequência de V's
      { dur: 5, draw: (t, a) => {
        const { C, T, prog, E, lerp } = a, pitch = C.pitch();
        const k = prog(t, .3, 1.2, E.inOut);
        const home = HOME.map(([x, y]) => [x, lerp(125, y, k)]), away = AWAY.map(([x, y]) => [x, lerp(-20, y, k)]);
        const wins = Array.from({ length: 9 }, (_, i) => { const p = prog(t, 1.3 + i * .18, .25, E.back);
          return `<rect x="${70 + i * 40}" y="${425}" width="34" height="34" rx="5" fill="${T.green}" opacity="${p}"/>${a.text(87 + i * 40, 450, 'V', { size: 20, anchor: 'middle', fill: '#041', op: p })}`; }).join('');
        return C.title('O cenário', '9 JOGOS.', '9 VITÓRIAS.', t) + pitch.svg + teams(a, pitch, home, away, t) + wins +
          C.tag(300, 1730, 'BARÇA · 4-3-3', { size: 18 }) +
          C.score('BAR 0 x 0 RMA', '', 1010, 440);
      } },

      // 3 — PLANO: bloco baixo do adversário (zona tracejada) + stats subindo
      { dur: 6, draw: (t, a) => {
        const { C, T, prog, E } = a, pitch = C.pitch();
        const k = prog(t, .4, 1.2, E.inOut);
        const away = morph(AWAY, shift(AWAY, 0, -4, .72, 0), k);      // bloco comprime e recua
        const [zx, zy] = pitch.P(8, 2), [zx2, zy2] = pitch.P(60, 30);
        const poss = Math.round(51 + 8 * prog(t, .5, 4, E.lin)), shots = Math.round(9 * prog(t, .5, 4, E.lin));
        return C.title('O plano', 'DEIXA ELE', 'TER A BOLA.', t) + pitch.svg +
          C.zone(zx, zy, zx2 - zx, zy2 - zy, 'Real compacto', prog(t, 1.2, .5)) +
          teams(a, pitch, HOME, away, t) +
          a.text(60, 390, `POSSE ${poss}%`, { size: 24, fill: T.yellow }) + a.text(300, 390, `CHUTES ${shots}`, { size: 24, fill: T.dim }) +
          C.score('BAR 0 x 0 RMA', "1' TEMPO", 1010, 440);
      } },

      // 4 — LANCE: destaque (ring) + passe amarelo desenhando + etiquetas
      { dur: 5.5, draw: (t, a) => {
        const { C, T, prog, E } = a, pitch = C.pitch();
        const striker = pitch.P(30, 92), from = pitch.P(60, 78), cross = prog(t, 1, .9, E.inOut);
        const ball = [a.lerp(from[0], striker[0], cross), a.lerp(from[1], striker[1], cross)];
        const hl = { away: { 9: { ring: t > 1.6, label: 'MBAPPÉ', t } }, home: { 4: { label: t > 1.6 ? 'G. MARTÍN' : '' } } };
        return C.title('O primeiro gol', 'UM CRUZAMENTO.', 'UM DESVIO.', t) + pitch.svg +
          teams(a, pitch, HOME.map(([x, y]) => [x, y - 6]), shift(AWAY, 0, 40, 1), t, hl) +
          C.arrow(from, striker, cross, { color: T.yellow, w: 7 }) +
          `<circle cx="${ball[0]}" cy="${ball[1]}" r="9" fill="#fff"/>` +
          (t > 3.2 ? `<g opacity="${prog(t, 3.2, .3, E.back)}">${a.text(540, 1050, 'GOL', { size: 220, font: T.display, anchor: 'middle', weight: 400, fill: T.yellow })}</g>` : '') +
          C.score(t > 3.2 ? 'BAR 0 x 1 RMA' : 'BAR 0 x 0 RMA', "41'", 1010, 440);
      } },

      // 5 — CONTRA-ATAQUE: setas verdes (corrida) sólidas + tracejadas
      { dur: 5, draw: (t, a) => {
        const { C, T, prog, E } = a, pitch = C.pitch();
        const s = pitch.P(34, 56), runs = [[pitch.P(34, 56), pitch.P(34, 92)], [pitch.P(18, 60), pitch.P(18, 94)], [pitch.P(50, 60), pitch.P(50, 94)]];
        return C.title('O contra-ataque', 'O BARÇA PERDEU A BOLA.', 'O REAL JÁ ESTAVA CORRENDO.', t) + a.text(0, 0, '') + pitch.svg +
          teams(a, pitch, shift(HOME, 0, -20, .8), shift(AWAY, 0, 22, 1.1), t, { away: { 8: { ring: true, label: 'CAMAVINGA', t } } }) +
          runs.map(([p, q], i) => C.arrow(p, q, prog(t, 1 + i * .25, .9, E.out), { color: T.green, dashed: i > 0 })).join('') +
          C.score('BAR 1 x 1 RMA', "88'", 1010, 440);
      } },

      // 6 — NÚMERO: boneco + contador gigante
      { dur: 4.5, draw: (t, a) => {
        const { C, T, prog } = a;
        return C.title('A prova', '8 GOLS EM', '7 CLÁSSICOS.', t) + C.floor(1500) +
          C.figure(300, 1500, C.kits.realAway, { pose: 'crossed', scale: 1.2, t, label: 'MBAPPÉ' }) +
          C.bigNumber(8, t, .8, { x: 740, y: 1180, sub: 'gols em 7 clássicos' }) +
          `<g opacity="${prog(t, 2.6)}">${C.tag(740, 1330, '1ª vitória do Real no Camp Nou', { anchor: 'middle', size: 16 })}</g>`;
      } },

      // 7 — GRÁFICO: barras comparativas
      { dur: 4.5, draw: (t, a) => {
        const { C, T } = a;
        return C.title('Os números', '73 GOLS.', '65 JOGOS.', t) +
          C.bars([{ label: 'REFERÊNCIA', value: 82, color: '#8d8f99' }, { label: 'AGORA', value: 73, color: T.yellow }], t, .6, { x: 190, base: 1500 }) +
          C.tag(540, 1620, 'Exemplo ilustrativo — troque pelos seus dados', { anchor: 'middle', size: 16, color: T.dim });
      } },

      // 8 — PERGUNTA + VS + CTA
      { dur: 6, draw: (t, a) => {
        const { C, T, prog } = a;
        return C.title('A pergunta', 'POSSE GANHA JOGO?', '', t) + C.floor(1500) +
          C.figure(280, 1500, C.kits.coach, { pose: 'crossed', coat: true, scale: 1, t, label: 'SEM A BOLA', op: prog(t, .8) }) +
          a.text(540, 1250, 'VS', { size: 90, font: T.display, anchor: 'middle', weight: 400, fill: T.dim, op: prog(t, 1.2) }) +
          C.figure(800, 1500, C.kits.barca, { pose: 'ball', scale: 1, t, label: 'COM A BOLA', op: prog(t, 1) }) +
          C.cta(t, 2);
      } },
    ],
  };
})();
