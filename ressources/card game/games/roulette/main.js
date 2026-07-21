import { Roulette, numberColor, BET_LABELS } from '../../src/games/roulette/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const WIN_TIER_TO_DEALER_EVENT = {
  jackpot: 'win_jackpot',
  big: 'win_big',
  small: 'win_small',
  none: 'lose',
};

const game = new Roulette({ startingBankroll: 500 });
let pendingBet = null; // { kind, number? }
let pendingAmount = 0;
let lastBankrollShown = null;
let bankruptcyAnnounced = false;
let isSpinning = false;

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const wheelNumberEl = document.getElementById('wheel-number');
const historyEl = document.getElementById('history');
const resultMessageEl = document.getElementById('result-message');
const betSelectionLabelEl = document.getElementById('bet-selection-label');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const resultAreaEl = document.getElementById('result-area');
const btnSpin = document.getElementById('btn-spin');
const numberGridEl = document.getElementById('number-grid');
const tabNumbers = document.getElementById('tab-numbers');
const tabOutside = document.getElementById('tab-outside');
const panelNumbers = document.getElementById('panel-numbers');
const panelOutside = document.getElementById('panel-outside');

const dealerVoice = createDealerVoice({
  game: 'roulette',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

/* ---------------------------------------------------------------- */
/* Construction de la grille de numéros (0-36)                       */
/* ---------------------------------------------------------------- */
for (let n = 0; n <= 36; n += 1) {
  const cell = document.createElement('button');
  cell.type = 'button';
  cell.className = 'number-cell';
  cell.dataset.number = String(n);
  cell.dataset.color = numberColor(n);
  cell.textContent = String(n);
  cell.addEventListener('click', () => {
    pendingBet = { kind: 'straight', number: n };
    updateBetSelectionUI();
    render();
  });
  numberGridEl.appendChild(cell);
}

document.querySelectorAll('.outside-bet').forEach((btn) => {
  btn.addEventListener('click', () => {
    pendingBet = { kind: btn.dataset.kind };
    updateBetSelectionUI();
    render();
  });
});

/** Calcule le nombre de colonnes et la taille de case qui remplissent le
 * mieux l'espace RÉELLEMENT disponible dans .bet-panel (mesuré en JS,
 * comme le calcul d'espacement des piles du Solitaire) plutôt qu'une
 * estimation vw/dvh statique en CSS, qui ne peut pas connaître la place
 * déjà prise par la bannière, la bulle, l'historique et les onglets. */
function layoutNumberGrid() {
  const availW = panelNumbers.clientWidth;
  const availH = panelNumbers.clientHeight;
  if (availW <= 0 || availH <= 0) return;

  const GAP = 3;
  const TOTAL_CELLS = 37;
  let best = null;
  for (let cols = 4; cols <= 13; cols += 1) {
    const rows = Math.ceil(TOTAL_CELLS / cols);
    const cellFromWidth = (availW - (cols - 1) * GAP) / cols;
    const cellFromHeight = (availH - (rows - 1) * GAP) / rows;
    const cell = Math.min(cellFromWidth, cellFromHeight);
    if (cell <= 0) continue;
    if (!best || cell > best.cell) best = { cols, cell };
  }
  if (!best) return;

  const cellPx = Math.floor(best.cell);
  numberGridEl.style.gridTemplateColumns = `repeat(${best.cols}, ${cellPx}px)`;
  numberGridEl.style.gridAutoRows = `${cellPx}px`;
  const fontPx = Math.max(9, Math.round(cellPx * 0.34));
  numberGridEl.style.fontSize = `${fontPx}px`;
}

function updateBetSelectionUI() {
  document.querySelectorAll('.number-cell').forEach((el) => {
    el.classList.toggle('is-selected', !!pendingBet && pendingBet.kind === 'straight' && Number(el.dataset.number) === pendingBet.number);
  });
  document.querySelectorAll('.outside-bet').forEach((el) => {
    el.classList.toggle('is-selected', !!pendingBet && pendingBet.kind === el.dataset.kind);
  });
  betSelectionLabelEl.textContent = pendingBet
    ? (pendingBet.kind === 'straight' ? `Plein ${pendingBet.number}` : BET_LABELS[pendingBet.kind])
    : 'Choisissez une mise';
}

tabNumbers.addEventListener('click', () => {
  tabNumbers.classList.add('is-active');
  tabOutside.classList.remove('is-active');
  tabNumbers.setAttribute('aria-selected', 'true');
  tabOutside.setAttribute('aria-selected', 'false');
  panelNumbers.classList.remove('hidden');
  panelOutside.classList.add('hidden');
  layoutNumberGrid(); // le panneau vient de redevenir visible : ses dimensions n'étaient pas mesurables avant (display:none)
});
tabOutside.addEventListener('click', () => {
  tabOutside.classList.add('is-active');
  tabNumbers.classList.remove('is-active');
  tabOutside.setAttribute('aria-selected', 'true');
  tabNumbers.setAttribute('aria-selected', 'false');
  panelOutside.classList.remove('hidden');
  panelNumbers.classList.add('hidden');
});

/* ---------------------------------------------------------------- */
/* Confettis (mêmes principes que les autres jeux)                   */
/* ---------------------------------------------------------------- */
const fxCanvas = document.getElementById('fx-canvas');
const fxCtx = fxCanvas.getContext('2d');
let particles = [];
let fxRunning = false;

function resizeCanvas() {
  const dpr = window.devicePixelRatio || 1;
  fxCanvas.width = window.innerWidth * dpr;
  fxCanvas.height = window.innerHeight * dpr;
  fxCtx.setTransform(dpr, 0, 0, dpr, 0, 0);
}
window.addEventListener('resize', resizeCanvas);
resizeCanvas();

function burstConfetti() {
  if (prefersReducedMotion()) return;
  const rect = tableEl.getBoundingClientRect();
  const cx = rect.left + rect.width / 2;
  const cy = rect.top + rect.height / 2;
  const count = 30;
  for (let i = 0; i < count; i += 1) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.3;
    const speed = 2.2 + Math.random() * 2.8;
    particles.push({
      x: cx, y: cy,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 1.5,
      r: 3 + Math.random() * 3,
      life: 0,
      maxLife: 60 + Math.random() * 20,
    });
  }
  if (!fxRunning) { fxRunning = true; requestAnimationFrame(tickConfetti); }
}

function tickConfetti() {
  fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
  particles.forEach((p) => {
    p.vy += 0.09;
    p.x += p.vx;
    p.y += p.vy;
    p.life += 1;
    const alpha = Math.max(0, 1 - p.life / p.maxLife);
    fxCtx.beginPath();
    const gradient = fxCtx.createRadialGradient(p.x - p.r * 0.3, p.y - p.r * 0.3, 0.5, p.x, p.y, p.r);
    gradient.addColorStop(0, `rgba(255,213,79,${alpha})`);
    gradient.addColorStop(1, `rgba(234,122,69,${alpha})`);
    fxCtx.fillStyle = gradient;
    fxCtx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
    fxCtx.fill();
  });
  particles = particles.filter((p) => p.life < p.maxLife);
  if (particles.length > 0) requestAnimationFrame(tickConfetti);
  else fxRunning = false;
}

function flashTable(kind) {
  const cls = kind === 'win' ? 'is-win-flash' : 'is-lose-flash';
  tableEl.classList.remove('is-win-flash', 'is-lose-flash');
  void tableEl.offsetWidth;
  tableEl.classList.add(cls);
  tableEl.addEventListener('animationend', () => tableEl.classList.remove(cls), { once: true });
}

/* ---------------------------------------------------------------- */
/* Rendu                                                              */
/* ---------------------------------------------------------------- */

function render() {
  const state = game.getState();

  if (state.bankroll !== lastBankrollShown) {
    bankrollEl.textContent = state.bankroll;
    if (lastBankrollShown !== null) {
      bankrollEl.classList.remove('is-bump');
      void bankrollEl.offsetWidth;
      bankrollEl.classList.add('is-bump');
    }
    lastBankrollShown = state.bankroll;
  }

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingAmount : (state.bet ? state.bet.amount : 0));
  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting' || isSpinning);
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result' || isSpinning);

  btnSpin.disabled = !pendingBet || pendingAmount <= 0 || pendingAmount > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingAmount + amount > state.bankroll;
  });

  if (!isSpinning && state.winningNumber !== null) {
    wheelNumberEl.textContent = String(state.winningNumber);
    wheelNumberEl.dataset.color = state.winningColor;
  }

  historyEl.innerHTML = '';
  state.history.forEach((n) => {
    const dot = document.createElement('span');
    dot.className = 'history-item';
    dot.dataset.color = numberColor(n);
    dot.textContent = String(n);
    historyEl.appendChild(dot);
  });

  if (state.phase === 'result' && !isSpinning) {
    resultMessageEl.textContent = state.won ? `Gagné — ${state.payout} !` : 'Perdu.';
    resultMessageEl.classList.toggle('is-lose', !state.won);
  } else if (state.phase === 'betting') {
    resultMessageEl.textContent = '';
    resultMessageEl.classList.remove('is-lose');
  }

  statusEl.textContent = state.isGameOver
    ? 'Banqueroute. Cliquez sur « Nouvelle partie » pour recommencer.'
    : '';
  if (state.isGameOver && !bankruptcyAnnounced) {
    bankruptcyAnnounced = true;
    dealerVoice.say('bankruptcy');
  }
}

/* ---------------------------------------------------------------- */
/* Interactions                                                       */
/* ---------------------------------------------------------------- */

document.querySelectorAll('.chip').forEach((btn) => {
  btn.addEventListener('click', () => {
    pendingAmount += Number(btn.dataset.chip);
    render();
  });
});

document.getElementById('btn-clear-bet').addEventListener('click', () => {
  pendingAmount = 0;
  pendingBet = null;
  updateBetSelectionUI();
  render();
});

const SPIN_ANIM_MS = 1100;

btnSpin.addEventListener('click', () => {
  if (!pendingBet || pendingAmount <= 0) return;
  isSpinning = true;
  dealerVoice.say('spinning');
  render();

  if (!prefersReducedMotion()) {
    wheelNumberEl.classList.add('is-spinning');
  }

  const settle = () => {
    wheelNumberEl.classList.remove('is-spinning');

    const result = game.spin({ ...pendingBet, amount: pendingAmount });
    if (!result.ok) {
      statusEl.textContent = 'Mise invalide.';
      isSpinning = false;
      render();
      return;
    }
    pendingAmount = 0;
    pendingBet = null;
    updateBetSelectionUI();
    isSpinning = false;
    render();

    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    const state = game.getState();
    const dealerEvent = WIN_TIER_TO_DEALER_EVENT[state.winTier];
    if (state.won) {
      flashTable('win');
      burstConfetti();
    } else {
      flashTable('lose');
    }
    if (dealerEvent) dealerVoice.say(dealerEvent);
  };

  setTimeout(settle, prefersReducedMotion() ? 0 : SPIN_ANIM_MS);
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  game.nextSpin();
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  game.newSession();
  pendingAmount = 0;
  pendingBet = null;
  updateBetSelectionUI();
  lastBankrollShown = null;
  bankruptcyAnnounced = false;
  wheelNumberEl.textContent = '?';
  wheelNumberEl.dataset.color = '';
  render();
  dealerVoice.say('greeting');
});

window.addEventListener('resize', () => {
  if (!panelNumbers.classList.contains('hidden')) layoutNumberGrid();
});

updateBetSelectionUI();
layoutNumberGrid();
render();
dealerVoice.say('greeting');
