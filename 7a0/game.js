/* ============ Estado ============ */
const state = {
  mode: "classico",          // "classico" | "almanaque"
  formationKey: "3-4-3",
  slots: [],                 // formação + {player}
  currentSquad: null,        // elenco sorteado (seleção × Copa)
  usedKeys: new Set(),       // "nome|seleção" já escalados
  swapCat: null,             // categoria que está sendo trocada (destaque)
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
  state.swapCat = null;
  renderPitch();
  updateProgress();
  drawSquad();
  show("screen-game");
}

/* ============ Sorteio de seleção × Copa ============ */
function openCats() {
  const set = new Set();
  state.slots.forEach(s => { if (!s.player) set.add(s.cat); });
  return set;
}

// um elenco é "útil" se tem algum jogador de categoria ainda aberta e não usado
function squadIsUseful(sq, cats) {
  return sq.players.some(p => cats.has(p.c) && !state.usedKeys.has(keyOf(p.n, sq.team)));
}

function drawSquad() {
  const cats = openCats();
  if (cats.size === 0) { state.currentSquad = null; renderSquadComplete(); return; }
  let chosen = null;
  for (let t = 0; t < 60; t++) {
    const sq = SQUADS[Math.floor(Math.random() * SQUADS.length)];
    if (sq !== state.currentSquad && squadIsUseful(sq, cats)) { chosen = sq; break; }
  }
  if (!chosen) {
    const ok = SQUADS.filter(sq => squadIsUseful(sq, cats));
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
    const highlight = state.swapCat === null && !slot.player && openCats().has(slot.cat);
    el.className = "slot" + (slot.player ? " filled" : "") + (highlight ? " open" : "");
    el.style.left = slot.x + "%";
    el.style.top = slot.y + "%";

    if (slot.player) {
      const showOvr = state.mode === "classico";
      el.innerHTML = `
        <div class="badge">${slot.player.flag}</div>
        <div class="nm">${shortName(slot.player.name)}</div>
        ${showOvr ? `<span class="ov">${slot.player.ovr}</span>` : ""}`;
      el.title = `${slot.player.name} — ${slot.player.nat} ${slot.player.year} · clique para trocar`;
      el.onclick = () => removePlayer(i);
    } else {
      el.innerHTML = `<div class="badge">${slot.label}</div><div class="nm"></div>`;
    }
    pitch.appendChild(el);
  });
}

function shortName(name) {
  const parts = name.split(" ");
  return parts.length > 1 && name.length > 12 ? parts[parts.length - 1] : name;
}

/* ============ Painel do elenco sorteado ============ */
const GROUP_ORDER = ["GK", "DEF", "MID", "FWD"];

function renderSquadPanel() {
  const sq = state.currentSquad;
  const cats = openCats();
  const filled = state.slots.filter(s => s.player).length;

  if (!sq) { renderSquadComplete(); return; }

  $("#sideTitle").innerHTML = `${sq.flag} ${sq.team} <span class="yr">Copa ${sq.year}</span>`;
  $("#sideSub").textContent = state.swapCat
    ? `Trocando ${CAT_NAMES[state.swapCat].toLowerCase()}: escolha um jogador deste elenco (ou sorteie outra seleção).`
    : `Escolha um jogador deste elenco para uma posição em aberto. Faltam ${state.slots.length - filled}.`;

  const showOvr = state.mode === "classico";
  let html = `<div class="squad-actions">
      <button class="btn ghost sm" id="btnReroll">🎲 Trocar seleção / Copa</button>
    </div><div class="squad-scroll">`;

  GROUP_ORDER.forEach(cat => {
    const group = sq.players.filter(p => p.c === cat);
    if (!group.length) return;
    html += `<div class="grp-label">${CAT_NAMES[cat]}</div><div class="cards">`;
    group.forEach((p) => {
      const used = state.usedKeys.has(keyOf(p.n, sq.team));
      const placeable = cats.has(cat) && !used;
      html += `
        <div class="pcard ${placeable ? "" : "disabled"}" data-name="${encodeURIComponent(p.n)}" data-cat="${cat}" data-ovr="${p.o}">
          <span class="flag">${sq.flag}</span>
          <div class="info">
            <b>${p.n}</b>
            <small>${CAT_NAMES[cat]}${used ? " · já escalado" : (placeable ? "" : " · posição cheia")}</small>
          </div>
          <div class="ovr ${showOvr ? "" : "hidden"}">${showOvr ? p.o : "?"}</div>
        </div>`;
    });
    html += `</div>`;
  });
  html += `</div>`;

  $("#picker").innerHTML = html;
  $("#btnReroll").onclick = () => { state.swapCat = null; renderPitch(); drawSquad(); };
  $("#picker").querySelectorAll(".pcard:not(.disabled)").forEach(card => {
    card.onclick = () => placeFromCard(card);
  });
  renderPitch();
}

function placeFromCard(card) {
  const name = decodeURIComponent(card.dataset.name);
  const cat = card.dataset.cat;
  const ovr = parseInt(card.dataset.ovr, 10);
  const sq = state.currentSquad;

  // preenche a vaga: a que está em troca (se for da mesma categoria) ou a 1ª aberta
  let idx = state.swapCat === cat ? state.slots.findIndex(s => !s.player && s.cat === cat) : -1;
  if (idx === -1) idx = state.slots.findIndex(s => !s.player && s.cat === cat);
  if (idx === -1) return;

  state.slots[idx].player = { name, cat, ovr, flag: sq.flag, nat: sq.team, year: sq.year };
  state.usedKeys.add(keyOf(name, sq.team));
  state.swapCat = null;
  updateProgress();

  if (openCats().size === 0) { state.currentSquad = null; renderPitch(); renderSquadComplete(); }
  else drawSquad();   // sorteia uma nova seleção para a próxima vaga
}

function removePlayer(i) {
  const slot = state.slots[i];
  if (!slot.player) return;
  state.usedKeys.delete(keyOf(slot.player.name, slot.player.nat));
  slot.player = null;
  state.swapCat = slot.cat;       // foco em recompor essa posição
  updateProgress();
  drawSquad();                    // novo sorteio para a posição trocada
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

/* ============ Eventos ============ */
$("#btnStart").onclick = startGame;
$("#btnFinish").onclick = finish;
$("#btnAgain").onclick = () => show("screen-start");
$("#btnShare").onclick = shareResult;
$("#btnRestart").onclick = () => { if (confirm("Recomeçar e perder a escalação atual?")) show("screen-start"); };

buildStartScreen();
