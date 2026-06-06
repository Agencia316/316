/* ============ Estado ============ */
const state = {
  mode: "classico",          // "classico" | "almanaque"
  formationKey: "3-4-3",
  slots: [],                 // cópia da formação + {player, candidates}
  activeSlot: null,          // índice do slot em seleção
  usedNames: new Set(),
};

const $ = (sel) => document.querySelector(sel);
const shuffle = (arr) => arr.map(v => [Math.random(), v]).sort((a, b) => a[0] - b[0]).map(p => p[1]);

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
  Object.keys(FORMATIONS).forEach((key, i) => {
    const counts = FORMATIONS[key].reduce((a, s) => (a[s.cat] = (a[s.cat] || 0) + 1, a), {});
    const desc = `${counts.DEF} def · ${counts.MID} meio · ${counts.FWD} atq`;
    const b = document.createElement("button");
    b.className = "opt" + (key === state.formationKey ? " sel" : "");
    b.dataset.form = key;
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
  state.slots = FORMATIONS[state.formationKey].map(s => ({ ...s, player: null, candidates: null }));
  state.usedNames = new Set();
  state.activeSlot = null;
  renderPitch();
  // abre automaticamente o primeiro slot vazio
  selectSlot(0);
  updateProgress();
  show("screen-game");
}

/* ============ Campo ============ */
function renderPitch() {
  const pitch = $("#pitch");
  pitch.querySelectorAll(".slot").forEach(el => el.remove());

  state.slots.forEach((slot, i) => {
    const el = document.createElement("div");
    el.className = "slot" + (slot.player ? " filled" : "") + (state.activeSlot === i ? " active" : "");
    el.style.left = slot.x + "%";
    el.style.top = slot.y + "%";

    if (slot.player) {
      const showOvr = state.mode === "classico";
      el.innerHTML = `
        <div class="badge">${slot.player.flag}</div>
        <div class="nm">${shortName(slot.player.name)}</div>
        ${showOvr ? `<span class="ov">${slot.player.ovr}</span>` : ""}`;
    } else {
      el.innerHTML = `<div class="badge">${slot.label}</div><div class="nm"></div>`;
    }
    el.onclick = () => selectSlot(i);
    pitch.appendChild(el);
  });
}

function shortName(name) {
  const parts = name.split(" ");
  return parts.length > 1 && name.length > 12 ? parts[parts.length - 1] : name;
}

/* ============ Seleção de jogador ============ */
function selectSlot(i) {
  state.activeSlot = i;
  const slot = state.slots[i];

  // gera candidatos se ainda não há (mantém estável ao reabrir o slot)
  if (!slot.candidates) {
    const pool = PLAYERS.filter(p => p.cat === slot.cat && !state.usedNames.has(p.name));
    slot.candidates = shuffle(pool).slice(0, 4);
  }

  renderPitch();
  renderPicker(slot);
}

function renderPicker(slot) {
  $("#sideTitle").textContent = slot.player
    ? `Trocar ${CAT_NAMES[slot.cat].toLowerCase()}`
    : `Escolha um ${CAT_NAMES[slot.cat].toLowerCase()}`;
  $("#sideSub").textContent = slot.player
    ? `${slot.player.name} está nessa posição. Escolha outro para trocar.`
    : `Posição: ${slot.label}. Selecione um dos craques abaixo.`;

  const picker = $("#picker");
  if (!slot.candidates || slot.candidates.length === 0) {
    picker.innerHTML = `<div class="picker-empty">Acabaram os craques disponíveis para essa posição.</div>`;
    return;
  }

  const showOvr = state.mode === "classico";
  picker.innerHTML = `<div class="cards">` + slot.candidates.map((p, idx) => `
    <div class="pcard" data-idx="${idx}">
      <span class="flag">${p.flag}</span>
      <div class="info">
        <b>${p.name}</b>
        <small>${CAT_NAMES[p.cat]} · ${p.era}</small>
      </div>
      <div class="ovr ${showOvr ? "" : "hidden"}">${showOvr ? p.ovr : "?"}</div>
    </div>`).join("") + `</div>`;

  picker.querySelectorAll(".pcard").forEach(card => {
    card.onclick = () => pickPlayer(parseInt(card.dataset.idx, 10));
  });
}

function pickPlayer(idx) {
  const slot = state.slots[state.activeSlot];
  const chosen = slot.candidates[idx];

  // se já havia um jogador, devolve para o pool
  if (slot.player) state.usedNames.delete(slot.player.name);

  slot.player = chosen;
  state.usedNames.add(chosen.name);
  slot.candidates = null; // posição resolvida

  renderPitch();
  updateProgress();

  // pula para a próxima posição vazia, se houver
  const next = state.slots.findIndex(s => !s.player);
  if (next !== -1) {
    selectSlot(next);
  } else {
    state.activeSlot = null;
    renderPitch();
    $("#sideTitle").textContent = "Escalação completa! ✅";
    $("#sideSub").textContent = "Clique numa posição para trocar, ou finalize.";
    $("#picker").innerHTML = `<div class="picker-empty">Todos os 11 escalados. Boa sorte!</div>`;
  }
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
  // quanto maior o overall médio, maior a goleada
  let gf, ga, title, msg, stars;
  if (avg >= 92)      { gf = 7; ga = 0; stars = 5; title = "7 A 0! 🏆"; msg = "Goleada histórica! Você montou a maior seleção de todos os tempos e atropelou os adversários."; }
  else if (avg >= 90) { gf = 6; ga = 0; stars = 5; title = "Goleada épica!"; msg = "Quase a perfeição. Um timaço de craques que humilhou o adversário."; }
  else if (avg >= 88) { gf = 5; ga = 1; stars = 4; title = "Show de bola!"; msg = "Vitória convincente com direito a muita bola na rede."; }
  else if (avg >= 86) { gf = 4; ga = 1; stars = 4; title = "Vitória sólida"; msg = "Um time forte e equilibrado que dominou a partida."; }
  else if (avg >= 84) { gf = 3; ga = 2; stars = 3; title = "Vitória apertada"; msg = "Deu pra ganhar, mas a defesa tomou uns sustos. Dá pra melhorar o elenco!"; }
  else if (avg >= 82) { gf = 2; ga = 2; stars = 2; title = "Empate suado"; msg = "Faltou pegada. Tente escalar craques com overall mais alto."; }
  else                { gf = 1; ga = 3; stars = 1; title = "Derrota..."; msg = "O time não engrenou. Reveja a escalação e busque mais estrelas!"; }
  return { gf, ga, title, msg, stars };
}

/* ============ Compartilhar ============ */
function shareResult() {
  const txt = `⚽ 7a0 — ${$("#rScore").textContent} (${state.formationKey})\n` +
              `${$("#rTitle").textContent}\nOverall do time: ${$("#rOvr").textContent}\n` +
              state.slots.map(s => `${s.player.flag} ${s.player.name}`).join(" · ");
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
