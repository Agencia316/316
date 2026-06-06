/* ============ Estado ============ */
const state = {
  mode: "classico",          // "classico" | "almanaque"
  formationKey: "3-4-3",
  slots: [],                 // formação + {player}
  currentSquad: null,        // elenco sorteado (seleção × Copa)
  usedKeys: new Set(),       // "nome|seleção" já escalados
  activeSlot: null,          // índice do slot que está sendo escalado
  teamAvg: 0,                // força média do XI (definida ao finalizar)
};

const $ = (sel) => document.querySelector(sel);
const keyOf = (name, team) => name + "|" + team;

/* ============ Telas ============ */
function show(screenId) {
  document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
  $("#" + screenId).classList.add("active");
  $("#btnRestart").style.display = screenId === "screen-start" ? "none" : "inline-block";
}

/* ============ Tela inicial ============ */
function buildStartScreen() {
  const grid = $("#formGrid");
  grid.innerHTML = "";
  Object.keys(FORMATIONS).forEach((key) => {
    const counts = FORMATIONS[key].reduce((a, s) => (a[s.cat] = (a[s.cat] || 0) + 1, a), {});
    const desc = `${counts.DEF} def · ${counts.MID} meio · ${counts.FWD} atq`;
    const b = document.createElement("button");
    b.className = "opt" + (key === state.formationKey ? " sel" : "");
    b.innerHTML = `<b>${key}</b><small>${desc}</small>`;
    b.onclick = () => {
      state.formationKey = key;
      grid.querySelectorAll(".opt").forEach(o => o.classList.remove("sel"));
      b.classList.add("sel");
    };
    grid.appendChild(b);
  });

  $("#modeGrid").querySelectorAll(".opt").forEach(btn => {
    btn.onclick = () => {
      state.mode = btn.dataset.mode;
      $("#modeGrid").querySelectorAll(".opt").forEach(o => o.classList.remove("sel"));
      btn.classList.add("sel");
    };
  });
}

/* ============ Iniciar partida ============ */
function startGame() {
  state.slots = FORMATIONS[state.formationKey].map(s => ({ ...s, player: null }));
  state.usedKeys = new Set();
  state.currentSquad = null;
  state.activeSlot = state.slots.findIndex(s => !s.player);   // 1ª vaga
  renderPitch();
  updateProgress();
  drawSquad();
  show("screen-game");
}

/* ============ Sorteio de seleção × Copa (para a posição ativa) ============ */
function activeCat() {
  return state.activeSlot != null ? state.slots[state.activeSlot].cat : null;
}
// um elenco serve se tem jogador da posição ativa ainda não escalado
function squadHasCat(sq, cat) {
  return sq.players.some(p => p.c === cat && !state.usedKeys.has(keyOf(p.n, sq.team)));
}

function drawSquad() {
  const cat = activeCat();
  if (cat == null) { state.currentSquad = null; renderSquadComplete(); return; }
  let chosen = null;
  for (let t = 0; t < 80; t++) {
    const sq = SQUADS[Math.floor(Math.random() * SQUADS.length)];
    if (sq !== state.currentSquad && squadHasCat(sq, cat)) { chosen = sq; break; }
  }
  if (!chosen) {
    const ok = SQUADS.filter(sq => squadHasCat(sq, cat));
    chosen = ok.length ? ok[Math.floor(Math.random() * ok.length)] : null;
  }
  state.currentSquad = chosen;
  renderSquadPanel();
}

/* ============ Campo ============ */
function renderPitch() {
  const pitch = $("#pitch");
  pitch.querySelectorAll(".slot").forEach(el => el.remove());

  state.slots.forEach((slot, i) => {
    const el = document.createElement("div");
    const active = state.activeSlot === i && !slot.player;
    el.className = "slot" + (slot.player ? " filled" : "") + (active ? " active" : "");
    el.style.left = slot.x + "%";
    el.style.top = slot.y + "%";

    if (slot.player) {
      const showOvr = state.mode === "classico";
      el.innerHTML = `
        <div class="badge">${slot.player.flag}</div>
        <div class="nm">${shortName(slot.player.name)}</div>
        ${showOvr ? `<span class="ov">${slot.player.ovr}</span>` : ""}`;
      el.title = `${slot.player.name} — ${slot.player.nat} ${slot.player.year} · clique para trocar`;
      el.onclick = () => swapSlot(i);
    } else {
      el.innerHTML = `<div class="badge">${slot.label}</div><div class="nm"></div>`;
      el.onclick = () => focusSlot(i);
    }
    pitch.appendChild(el);
  });
}

function shortName(name) {
  const parts = name.split(" ");
  return parts.length > 1 && name.length > 12 ? parts[parts.length - 1] : name;
}

// escolher qual posição vazia escalar agora
function focusSlot(i) {
  if (state.slots[i].player) return;
  state.activeSlot = i;
  drawSquad();
}

// trocar um jogador já escalado: libera a vaga e sorteia nova seleção
function swapSlot(i) {
  const slot = state.slots[i];
  if (!slot.player) return;
  state.usedKeys.delete(keyOf(slot.player.name, slot.player.nat));
  slot.player = null;
  state.activeSlot = i;
  updateProgress();
  drawSquad();
}

/* ============ Painel: jogadores da seleção sorteada na posição ativa ============ */
function renderSquadPanel() {
  const sq = state.currentSquad;
  if (state.activeSlot == null || !sq) { renderSquadComplete(); return; }
  const slot = state.slots[state.activeSlot];
  const cat = slot.cat;
  const filled = state.slots.filter(s => s.player).length;

  $("#sideTitle").innerHTML = `${sq.flag} ${sq.team} <span class="yr">Copa ${sq.year}</span>`;
  $("#sideSub").innerHTML =
    `Escalando <b>${slot.label}</b> (${CAT_NAMES[cat].toLowerCase()}) — faltam ${state.slots.length - filled}.<br/>` +
    `Escolha um jogador desta seleção:`;

  const showOvr = state.mode === "classico";
  const group = sq.players.filter(p => p.c === cat)
                  .sort((a, b) => b.o - a.o);

  let html = `<div class="squad-actions">
      <button class="btn ghost sm" id="btnReroll">🎲 Sortear outra seleção / Copa</button>
    </div><div class="squad-scroll"><div class="cards">`;
  group.forEach(p => {
    const used = state.usedKeys.has(keyOf(p.n, sq.team));
    html += `
      <div class="pcard ${used ? "disabled" : ""}" data-name="${encodeURIComponent(p.n)}" data-ovr="${p.o}">
        <span class="flag">${sq.flag}</span>
        <div class="info">
          <b>${p.n}</b>
          <small>${CAT_NAMES[cat]}${used ? " · já escalado" : ""}</small>
        </div>
        <div class="ovr ${showOvr ? "" : "hidden"}">${showOvr ? p.o : "?"}</div>
      </div>`;
  });
  html += `</div></div>`;

  $("#picker").innerHTML = html;
  $("#btnReroll").onclick = () => drawSquad();
  $("#picker").querySelectorAll(".pcard:not(.disabled)").forEach(card => {
    card.onclick = () => placeFromCard(card);
  });
  renderPitch();
}

function placeFromCard(card) {
  const name = decodeURIComponent(card.dataset.name);
  const ovr = parseInt(card.dataset.ovr, 10);
  const sq = state.currentSquad;
  const slot = state.slots[state.activeSlot];
  if (!slot || slot.player) return;

  slot.player = { name, cat: slot.cat, ovr, flag: sq.flag, nat: sq.team, year: sq.year };
  state.usedKeys.add(keyOf(name, sq.team));
  updateProgress();

  const next = state.slots.findIndex(s => !s.player);
  state.activeSlot = next;
  if (next === -1) { state.currentSquad = null; renderPitch(); renderSquadComplete(); }
  else drawSquad();   // sorteia uma nova seleção para a próxima posição
}

function renderSquadComplete() {
  $("#sideTitle").textContent = "Escalação completa! ✅";
  $("#sideSub").textContent = "Clique num jogador do campo para trocá-lo, ou finalize.";
  $("#picker").innerHTML = `<div class="picker-empty">Os 11 estão escalados. Boa sorte na goleada! 🏆</div>`;
  renderPitch();
}

function updateProgress() {
  const filled = state.slots.filter(s => s.player).length;
  const total = state.slots.length;
  $("#progBar").style.width = (filled / total * 100) + "%";
  $("#btnFinish").disabled = filled < total;
}

/* ============ Resultado ============ */
function finish() {
  const players = state.slots.map(s => s.player);
  const avg = players.reduce((a, p) => a + p.ovr, 0) / players.length;
  state.teamAvg = avg;
  const r = computeResult(avg);
  const star = players.slice().sort((a, b) => b.ovr - a.ovr)[0];

  $("#rScore").textContent = `${r.gf} - ${r.ga}`;
  $("#rTitle").textContent = r.title;
  $("#rStars").textContent = "★".repeat(r.stars) + "☆".repeat(5 - r.stars);
  $("#rMsg").textContent = r.msg;
  $("#rOvr").textContent = avg.toFixed(1);
  $("#rForm").textContent = state.formationKey;
  $("#rStar").textContent = `${star.flag} ${shortName(star.name)}`;

  $("#rLineup").innerHTML = players
    .map(p => `<span class="chip">${p.flag} ${shortName(p.name)} <i>${p.ovr}</i></span>`)
    .join("");

  show("screen-result");
}

function computeResult(avg) {
  let gf, ga, title, msg, stars;
  if (avg >= 90)      { gf = 7; ga = 0; stars = 5; title = "7 A 0! 🏆"; msg = "Goleada histórica! Você montou a maior seleção de todos os tempos e atropelou os adversários."; }
  else if (avg >= 87) { gf = 6; ga = 0; stars = 5; title = "Goleada épica!"; msg = "Quase a perfeição. Um timaço que humilhou o adversário."; }
  else if (avg >= 85) { gf = 5; ga = 1; stars = 4; title = "Show de bola!"; msg = "Vitória convincente com direito a muita bola na rede."; }
  else if (avg >= 83) { gf = 4; ga = 1; stars = 4; title = "Vitória sólida"; msg = "Um time forte e equilibrado que dominou a partida."; }
  else if (avg >= 81) { gf = 3; ga = 2; stars = 3; title = "Vitória apertada"; msg = "Deu pra ganhar, mas a defesa tomou uns sustos. Dá pra melhorar o elenco!"; }
  else if (avg >= 79) { gf = 2; ga = 2; stars = 2; title = "Empate suado"; msg = "Faltou pegada. Tente escalar jogadores de overall mais alto."; }
  else                { gf = 1; ga = 3; stars = 1; title = "Derrota..."; msg = "O time não engrenou. Reveja a escalação e busque mais estrelas!"; }
  return { gf, ga, title, msg, stars };
}

/* ============ Compartilhar ============ */
function shareResult() {
  const txt = `⚽ 7a0 — ${$("#rScore").textContent} (${state.formationKey})\n` +
              `${$("#rTitle").textContent}\nOverall do time: ${$("#rOvr").textContent}\n` +
              state.slots.map(s => `${s.player.flag} ${s.player.name} (${s.player.nat} ${s.player.year})`).join(" · ");
  navigator.clipboard?.writeText(txt).then(
    () => { const b = $("#btnShare"); b.textContent = "✅ Copiado!"; setTimeout(() => b.textContent = "📋 Copiar resultado", 1600); },
    () => alert(txt)
  );
}

/* ============ Simulação da Copa 2026 ============ */
let NATIONS = null;

function buildNations() {
  if (NATIONS) return NATIONS;
  const ratingOf = (sq) => {
    const by = { GK: [], DEF: [], MID: [], FWD: [] };
    sq.players.forEach(p => by[p.c].push(p.o));
    for (const k in by) by[k].sort((a, b) => b - a);
    const xi = [...by.GK.slice(0, 1), ...by.DEF.slice(0, 4), ...by.MID.slice(0, 3), ...by.FWD.slice(0, 3)];
    return xi.length ? xi.reduce((a, b) => a + b, 0) / xi.length : 70;
  };
  const best = {};
  SQUADS.forEach(sq => {
    const r = ratingOf(sq);
    if (!best[sq.team] || r > best[sq.team].rating)
      best[sq.team] = { team: sq.team, flag: sq.flag, rating: r, year: sq.year };
  });
  NATIONS = Object.values(best).sort((a, b) => b.rating - a.rating);
  return NATIONS;
}

const rnd = (n) => Math.floor(Math.random() * n);
function shuffle(a) { a = a.slice(); for (let i = a.length - 1; i > 0; i--) { const j = rnd(i + 1); [a[i], a[j]] = [a[j], a[i]]; } return a; }
function poisson(l) { const L = Math.exp(-l); let k = 0, p = 1; do { k++; p *= Math.random(); } while (p > L); return k - 1; }

function simMatch(a, b) {
  const d = a.rating - b.rating;
  const la = Math.max(0.12, Math.min(5, 1.35 + d * 0.06));
  const lb = Math.max(0.12, Math.min(5, 1.35 - d * 0.06));
  return { ga: poisson(la), gb: poisson(lb) };
}
function knockout(a, b) {
  const { ga, gb } = simMatch(a, b);
  if (ga !== gb) return { ga, gb, pen: null, winner: ga > gb ? a : b };
  const pa = Math.max(0.15, Math.min(0.85, 0.5 + (a.rating - b.rating) * 0.02));
  return Math.random() < pa ? { ga, gb, pen: [4, 3], winner: a } : { ga, gb, pen: [3, 4], winner: b };
}
function roundName(n) {
  return n >= 32 ? "16-avos de final" : n >= 16 ? "Oitavas de final" :
         n >= 8 ? "Quartas de final" : n >= 4 ? "Semifinal" : "Final";
}

function playGroup(teams) {
  const st = teams.map(t => ({ t, pts: 0, gf: 0, ga: 0, j: 0, v: 0, e: 0, d: 0 }));
  const matches = [];
  for (let i = 0; i < teams.length; i++)
    for (let j = i + 1; j < teams.length; j++) {
      const r = simMatch(teams[i], teams[j]);
      matches.push({ a: teams[i], b: teams[j], ga: r.ga, gb: r.gb });
      const A = st[i], B = st[j];
      A.j++; B.j++; A.gf += r.ga; A.ga += r.gb; B.gf += r.gb; B.ga += r.ga;
      if (r.ga > r.gb) { A.pts += 3; A.v++; B.d++; }
      else if (r.ga < r.gb) { B.pts += 3; B.v++; A.d++; }
      else { A.pts++; B.pts++; A.e++; B.e++; }
    }
  st.forEach(s => s.gd = s.gf - s.ga);
  st.sort((x, y) => y.pts - x.pts || y.gd - x.gd || y.gf - x.gf || Math.random() - 0.5);
  return { st, matches };
}

function playCup(yourRating) {
  const you = { team: "Sua Seleção", flag: "⭐", rating: yourRating, isYou: true };
  const pool = buildNations().slice(0, 47).map(n => ({ ...n }));
  const all = [you, ...pool];                         // 48 seleções
  const sorted = all.slice().sort((a, b) => b.rating - a.rating);
  const pots = [sorted.slice(0, 12), sorted.slice(12, 24), sorted.slice(24, 36), sorted.slice(36, 48)].map(shuffle);
  const groups = [];
  for (let g = 0; g < 12; g++) groups.push([pots[0][g], pots[1][g], pots[2][g], pots[3][g]]);

  const results = groups.map(playGroup);
  const winners = [], runners = [], thirds = [];
  results.forEach(r => { winners.push(r.st[0].t); runners.push(r.st[1].t); thirds.push(r.st[2]); });
  thirds.sort((x, y) => y.pts - x.pts || y.gd - x.gd || y.gf - x.gf || Math.random() - 0.5);
  const advancers = [...winners, ...runners, ...thirds.slice(0, 8).map(s => s.t)];   // 32

  const yourGroupIdx = groups.findIndex(g => g.some(t => t.isYou));
  const yg = results[yourGroupIdx];
  const yourRank = yg.st.findIndex(s => s.t.isYou);
  const advanced = advancers.includes(you);

  const path = [];
  let eliminatedAt = null;
  let teams = shuffle(advancers);
  while (teams.length > 1) {
    const name = roundName(teams.length);
    const next = [];
    for (let i = 0; i < teams.length; i += 2) {
      const a = teams[i], b = teams[i + 1];
      const r = knockout(a, b);
      next.push(r.winner);
      if (a.isYou || b.isYou) {
        const gf = a.isYou ? r.ga : r.gb, ga = a.isYou ? r.gb : r.ga;
        const pen = r.pen ? (a.isYou ? `${r.pen[0]}-${r.pen[1]}` : `${r.pen[1]}-${r.pen[0]}`) : null;
        path.push({ round: name, opp: a.isYou ? b : a, gf, ga, pen, won: r.winner.isYou });
        if (!r.winner.isYou) eliminatedAt = name;
      }
    }
    teams = next;
  }
  return { you, group: { idx: yourGroupIdx, table: yg.st, matches: yg.matches, rank: yourRank, advanced },
           path, champion: teams[0], eliminatedAt };
}

function renderCup(res) {
  const g = res.group;
  let html = "";

  // desfecho
  let banner;
  if (g.advanced && res.champion.isYou)
    banner = `<div class="cup-out champ"><div class="big">CAMPEÃ! 🏆</div><p>Sua seleção dos sonhos é campeã da Copa 2026 — rumo ao 7 a 0!</p></div>`;
  else if (!g.advanced)
    banner = `<div class="cup-out elim"><div class="big">Eliminada na fase de grupos 😞</div><p>Terminou em ${g.rank + 1}º do grupo. Campeã: ${res.champion.flag} ${res.champion.team}.</p></div>`;
  else if (res.eliminatedAt === "Final")
    banner = `<div class="cup-out vice"><div class="big">Vice-campeã 🥈</div><p>Chegou à final! Campeã: ${res.champion.flag} ${res.champion.team}.</p></div>`;
  else
    banner = `<div class="cup-out elim"><div class="big">Eliminada — ${res.eliminatedAt}</div><p>Campeã do torneio: ${res.champion.flag} ${res.champion.team}.</p></div>`;

  // grupo
  html += `<div class="cup-block"><h3>Fase de grupos · Grupo ${String.fromCharCode(65 + g.idx)}</h3>`;
  html += `<table class="grp-table"><thead><tr><th>#</th><th>Seleção</th><th>Pts</th><th>J</th><th>V</th><th>E</th><th>D</th><th>SG</th></tr></thead><tbody>`;
  g.table.forEach((s, i) => {
    html += `<tr class="${s.t.isYou ? "me" : ""} ${i < 2 ? "adv" : ""}"><td>${i + 1}</td>` +
            `<td>${s.t.flag} ${s.t.isYou ? "Sua Seleção" : s.t.team}</td>` +
            `<td><b>${s.pts}</b></td><td>${s.j}</td><td>${s.v}</td><td>${s.e}</td><td>${s.d}</td>` +
            `<td>${s.gd > 0 ? "+" : ""}${s.gd}</td></tr>`;
  });
  html += `</tbody></table><div class="cup-matches">`;
  g.matches.filter(m => m.a.isYou || m.b.isYou).forEach(m => {
    const opp = m.a.isYou ? m.b : m.a, gf = m.a.isYou ? m.ga : m.gb, ga = m.a.isYou ? m.gb : m.ga;
    const r = gf > ga ? "w" : gf < ga ? "l" : "d";
    html += `<div class="cup-m ${r}"><span>⭐ Sua Seleção</span><b>${gf} - ${ga}</b><span>${opp.flag} ${opp.team}</span></div>`;
  });
  html += `</div></div>`;

  // mata-mata
  if (g.advanced) {
    html += `<div class="cup-block"><h3>Mata-mata</h3><div class="cup-matches">`;
    res.path.forEach(p => {
      html += `<div class="cup-m ${p.won ? "w" : "l"}"><span class="rd">${p.round}</span>` +
              `<span>⭐ Sua Seleção</span><b>${p.gf} - ${p.ga}${p.pen ? ` <small>(${p.pen} pên)</small>` : ""}</b>` +
              `<span>${p.opp.flag} ${p.opp.team}</span></div>`;
    });
    html += `</div></div>`;
  }

  $("#cupBody").innerHTML = banner + html;
  $("#cupRating").textContent = res.you.rating.toFixed(1);
}

function playAndShowCup() {
  renderCup(playCup(state.teamAvg));
  show("screen-cup");
}

/* ============ Eventos ============ */
$("#btnStart").onclick = startGame;
$("#btnFinish").onclick = finish;
$("#btnAgain").onclick = () => show("screen-start");
$("#btnShare").onclick = shareResult;
$("#btnCup").onclick = playAndShowCup;
$("#btnCupAgain").onclick = playAndShowCup;
$("#btnCupNew").onclick = () => show("screen-start");
$("#btnCupBack").onclick = () => show("screen-result");
$("#btnRestart").onclick = () => { if (confirm("Recomeçar e perder a escalação atual?")) show("screen-start"); };

buildStartScreen();
