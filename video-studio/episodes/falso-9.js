// O FALSO 9 — o centroavante que joga de meia. ~68 s, 10 cenas. Roteiro em roteiros/falso-9.md
(() => {
  const { F, mirror, morph, shift } = Formations;
  const ATK = F['4-2-3-1'], ATK0 = F['4-3-3'];       // time que ataca (roxo, de baixo)
  const DEF = mirror(F['4-4-2']);                     // defesa (branco, de cima)
  const kit9 = { ...Studio.C.kits.barca, number: 9 };                      // Barça: camisa 9
  const kitDef = { ...Studio.C.kits.realAway, number: 4 };                 // Real Madrid (defensor)
  const kitFalso = { ...Studio.C.kits.barca, number: 10, hair: '#2a1a12' };       // Barça: falso 9

  const teams = (a, pitch, home, away, t, hl = {}) => {
    let s = '';
    away.forEach((p, i) => { const [x, y] = pitch.P(...p); s += a.C.dot(x, y, 'away', { gk: i === 0, t, ...(hl.away?.[i] || {}) }); });
    home.forEach((p, i) => { const [x, y] = pitch.P(...p); s += a.C.dot(x, y, 'home', { gk: i === 0, t, ...(hl.home?.[i] || {}) }); });
    return s;
  };
  // zagueiro central direito do bloco defensivo (índice 2) é o que segue o 9
  const cbAt = (k) => { const p = DEF.map(q => q.slice()); p[2] = [42 - 6 * k, 21 + 18 * k]; return p; };
  const stAt = (k) => { const p = ATK.map(q => q.slice()); p[10] = [34, 40 + 20 * k]; return p; };
  const zone = (pitch) => { const [x, y] = pitch.P(6, 13), [x2, y2] = pitch.P(62, 31); return [x, y, x2 - x, y2 - y]; };

  window.EPISODE = {
    handle: 'seu.perfil', fade: .25,
    scenes: [
      // 1 — GANCHO
      { dur: 5, draw: (t, a) => { const { C, T, prog, E } = a;
        return C.title('O gancho', 'O CENTROAVANTE SUMIU.', 'NINGUÉM SABE QUEM MARCAR.', t) + C.floor(1500) +
          C.figure(300, 1500, kit9, { pose: 'crossed', scale: 1.15, t, label: 'BARÇA: CAMISA 9', op: prog(t, 1.2, .5) }) +
          C.figure(780, 1500, kitDef, { pose: { a: 'idle', b: 'hands-on-head', k: prog(t, 2.4, .6, E.back) }, scale: 1.15, t, label: 'REAL: MARCAR QUEM?', op: prog(t, 1.8, .5) }) +
          `<g opacity="${prog(t, 2.6, .4, a.E.back)}">${a.text(540, 1150, '?', { size: 260, font: T.display, anchor: 'middle', weight: 400, fill: T.yellow })}</g>`;
      } },
      // 2 — CENÁRIO: 4-3-3 no papel vira 4-2-3-1 no campo
      { dur: 6, draw: (t, a) => { const { C, T, prog, E } = a, pitch = C.pitch();
        const k = prog(t, 2.2, 1.6, E.inOut);
        return C.title('O cenário', '4-3-3 NO PAPEL.', '4-2-3-1 NO CAMPO.', t) + pitch.svg +
          teams(a, pitch, morph(ATK0, ATK, k), DEF, t) +
          `<g opacity="${prog(t, .8)}">${C.tag(330, 1735, t < 2.2 ? 'BARÇA · NO PAPEL · 4-3-3' : 'BARÇA · NO CAMPO · 4-2-3-1', { size: 18 })}</g>`;
      } },
      // 3 — PROBLEMA: zona tracejada sobre a linha de defesa
      { dur: 6, draw: (t, a) => { const { C, T, prog } = a, pitch = C.pitch(), [zx, zy, zw, zh] = zone(pitch);
        return C.title('O problema do zagueiro', 'MARCA O 9?', 'E O ESPAÇO NAS COSTAS?', t) + pitch.svg +
          C.zone(zx, zy, zw, zh, 'Linha de defesa', prog(t, 1)) +
          teams(a, pitch, ATK, DEF, t, { home: { 10: { ring: t > 2, label: t > 2 ? 'O 9' : '', t } } });
      } },
      // 4 — MOVIMENTO: o 9 recua, o zagueiro segue
      { dur: 7, draw: (t, a) => { const { C, T, prog, E } = a, pitch = C.pitch(), k = prog(t, 1.2, 2.2, E.inOut), [zx, zy, zw, zh] = zone(pitch);
        const a0 = pitch.P(34, 40), a1 = pitch.P(34, 60), d0 = pitch.P(42, 21), d1 = pitch.P(36, 39);
        return C.title('O movimento', 'O 9 RECUA.', 'O ZAGUEIRO SEGUE.', t) + pitch.svg +
          C.zone(zx, zy, zw, zh, 'Linha de defesa', .6) +
          teams(a, pitch, stAt(k), cbAt(k), t, { home: { 10: { ring: true, label: 'O 9', t } } }) +
          C.arrow(a0, a1, prog(t, 1.2, 2.2, E.out), { color: T.yellow, w: 7 }) +
          C.arrow(d0, d1, prog(t, 1.6, 2.2, E.out), { color: T.red, dashed: true, w: 6 }) +
          (t > 4 ? `<g opacity="${prog(t, 4, .4, E.back)}">${C.tag(540, 560, 'BURACO ABERTO', { anchor: 'middle', color: T.yellow, size: 26 })}</g>` : '');
      } },
      // 5 — ESPAÇO: pontas entram em diagonal
      { dur: 7, draw: (t, a) => { const { C, T, prog, E } = a, pitch = C.pitch();
        const p9 = stAt(1), d = cbAt(1);
        const l0 = pitch.P(10, 52), l1 = pitch.P(22, 26), r0 = pitch.P(58, 52), r1 = pitch.P(46, 24);
        const k1 = prog(t, 1, 1.4, E.inOut), k2 = prog(t, 1.4, 1.4, E.inOut);
        const home = p9.map(q => q.slice()); home[7] = [a.lerp(10, 22, k1), a.lerp(52, 26, k1)]; home[9] = [a.lerp(58, 46, k2), a.lerp(52, 24, k2)];
        return C.title('O espaço', 'AGORA TEM UM BURACO.', 'E ALGUÉM CHEGANDO.', t) + pitch.svg +
          teams(a, pitch, home, d, t, { home: { 7: { ring: t > 2.4, label: t > 2.4 ? 'PONTA ENTRA' : '', t } } }) +
          C.arrow(l0, l1, prog(t, 1, 1.4, E.out), { color: T.green, w: 6 }) +
          C.arrow(r0, r1, prog(t, 1.4, 1.4, E.out), { color: T.green, dashed: true, w: 6 });
      } },
      // 6 — RESULTADO: passe e gol
      { dur: 7, draw: (t, a) => { const { C, T, prog, E } = a, pitch = C.pitch();
        const am = pitch.P(34, 60), wg = pitch.P(22, 26), k = prog(t, 1, 1, E.inOut), ball = [a.lerp(am[0], wg[0], k), a.lerp(am[1], wg[1], k)];
        const home = stAt(1).map(q => q.slice()); home[7] = [22, 26]; home[9] = [46, 24];
        const gol = t > 3;
        return C.title('O resultado', 'UM PASSE.', 'O GOL.', t) + pitch.svg +
          teams(a, pitch, home, cbAt(1), t, { home: { 7: { ring: true, label: 'PONTA', t } } }) +
          C.arrow(am, wg, k, { color: T.yellow, w: 7 }) + `<circle cx="${ball[0]}" cy="${ball[1]}" r="9" fill="#fff"/>` +
          (gol ? `<g opacity="${prog(t, 3, .35, E.back)}" transform="translate(0,${(1 - prog(t, 3, .35, E.back)) * 30})">${a.text(540, 1100, 'GOL', { size: 260, font: T.display, anchor: 'middle', weight: 400, fill: T.yellow })}</g>` : '') +
          C.score(gol ? 'BAR 1 x 0 RMA' : 'BAR 0 x 0 RMA', gol ? "38'" : "37'", 1010, 440);
      } },
      // 7 — PROVA: número gigante (placeholder ilustrativo)
      { dur: 7, draw: (t, a) => { const { C, T, prog } = a;
        return C.title('A prova', '3 DE 4 ATAQUES', 'PASSAM POR ELE.', t) + C.floor(1500) +
          C.figure(300, 1500, kit9, { pose: 'crossed', scale: 1.2, t, label: 'BARÇA · FALSO 9' }) +
          C.bigNumber(3, t, .8, { x: 740, y: 1180, sub: 'de 4 ataques' }) +
          `<g opacity="${prog(t, 2)}">${C.tag(740, 1330, 'exemplo ilustrativo — troque pelo seu dado', { anchor: 'middle', size: 16, color: T.dim })}</g>`;
      } },
      // 8 — CUSTO: bola alta, área vazia
      { dur: 7, draw: (t, a) => { const { C, T, prog, E } = a, pitch = C.pitch();
        const s = pitch.P(62, 70), e = pitch.P(34, 8), k = prog(t, 1.2, 1.8, E.inOut);
        const ball = [a.lerp(s[0], e[0], k), a.lerp(s[1], e[1], k) - Math.sin(k * Math.PI) * 160];
        const [zx, zy] = pitch.P(14, 2), [zx2, zy2] = pitch.P(54, 17);
        return C.title('O custo', 'SEM CENTROAVANTE,', 'SEM ALVO NA ÁREA.', t) + pitch.svg +
          C.zone(zx, zy, zx2 - zx, zy2 - zy, 'Área vazia', prog(t, 2.4), T.red) +
          teams(a, pitch, stAt(1), DEF.map(q => shift([q], 0, 0)[0]), t) +
          `<circle cx="${ball[0]}" cy="${ball[1]}" r="${9 + Math.sin(k * Math.PI) * 6}" fill="#fff"/>` +
          (t > 3 ? `<g opacity="${prog(t, 3, .4, E.back)}">${a.text(540, 1000, '?', { size: 240, font: T.display, anchor: 'middle', weight: 400, fill: T.red })}</g>` : '');
      } },
      // 9 — CONTRASTE
      { dur: 8, draw: (t, a) => { const { C, T, prog } = a;
        return C.title('O contraste', 'PRENDE A DEFESA.', 'OU PERDE A ÁREA.', t) + C.floor(1500) +
          C.figure(280, 1500, kit9, { pose: 'crossed', scale: 1, t, label: 'COM O 9 FIXO', op: prog(t, .8) }) +
          a.text(540, 1250, 'VS', { size: 90, font: T.display, anchor: 'middle', weight: 400, fill: T.dim, op: prog(t, 1.2) }) +
          C.figure(800, 1500, kitFalso, { pose: 'shrug', scale: 1, t, label: 'COM O FALSO 9', op: prog(t, 1) });
      } },
      // 10 — PERGUNTA + CTA
      { dur: 8, draw: (t, a) => { const { C, T, prog } = a;
        return C.title('A pergunta', 'FALSO 9 FUNCIONA?', 'OU É MODA?', t) + C.floor(1500) +
          C.figure(280, 1500, kit9, { pose: 'crossed', scale: 1, t, label: 'BARÇA: FUNCIONA', op: prog(t, .8) }) +
          a.text(540, 1250, 'VS', { size: 90, font: T.display, anchor: 'middle', weight: 400, fill: T.dim, op: prog(t, 1.2) }) +
          C.figure(800, 1500, kitDef, { pose: 'crossed', scale: 1, t, label: 'REAL: É MODA', op: prog(t, 1) }) +
          C.cta(t, 2.2);
      } },
    ],
  };
})();
