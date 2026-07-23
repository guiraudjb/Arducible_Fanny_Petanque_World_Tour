import { Craps, SIDE_LABELS } from '../../src/games/craps/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

// Positions des points (pips) dans une grille CSS 3x3, par valeur de dé.
// Rendu en divs plutôt qu'en glyphes Unicode ⚀-⚅ (mal supportés par
// certaines polices système, qui affichent un rectangle de substitution).
const PIP_POSITIONS = {
  1: [5],
  2: [1, 9],
  3: [1, 5, 9],
  4: [1, 3, 7, 9],
  5: [1, 3, 5, 7, 9],
  6: [1, 3, 4, 6, 7, 9],
};

function renderDie(el, value) {
  el.innerHTML = '';
  const positions = PIP_POSITIONS[value] || [];
  for (let i = 1; i <= 9; i += 1) {
    const pip = document.createElement('span');
    pip.className = 'pip';
    if (positions.includes(i)) pip.classList.add('is-on');
    el.appendChild(pip);
  }
}

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const game = new Craps({ startingBankroll: 500 });
let pendingBet = 0;
let selectedSide = null;
let lastBankrollShown = null;
let lastPhase = null;
let lastRollCount = 0;
let bankruptcyAnnounced = false;

const dealerVoice = createDealerVoice({
  game: 'craps',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const pointReadoutEl = document.getElementById('point-readout');
const die1El = document.getElementById('die-1');
const die2El = document.getElementById('die-2');
const rollTotalEl = document.getElementById('roll-total');
const resultMessageEl = document.getElementById('result-message');
const rollHistoryEl = document.getElementById('roll-history');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const rollingAreaEl = document.getElementById('rolling-area');
const resultAreaEl = document.getElementById('result-area');
const hintEl = document.getElementById('hint');
const btnStart = document.getElementById('btn-start');
const btnRoll = document.getElementById('btn-roll');

/* ---------------------------------------------------------------- */
/* Confettis                                                           */
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
  const count = 26;
  for (let i = 0; i < count; i += 1) {
    const angle = (Math.PI * 2 * i) / count + Math.random() * 0.3;
    const speed = 2.2 + Math.random() * 2.6;
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
    gradient.addColorStop(0, `rgba(255,255,255,${alpha})`);
    gradient.addColorStop(1, `rgba(160,160,160,${alpha})`);
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

function shakeDice() {
  if (prefersReducedMotion()) return;
  [die1El, die2El].forEach((el, i) => {
    el.classList.remove('is-rolling');
    void el.offsetWidth;
    el.style.animationDelay = `${i * 40}ms`;
    el.classList.add('is-rolling');
  });
}

/* ---------------------------------------------------------------- */
/* Rendu                                                               */
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

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet);
  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting');
  rollingAreaEl.classList.toggle('hidden', state.phase !== 'rolling');
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');

  document.querySelectorAll('.side-btn').forEach((btn) => {
    btn.classList.toggle('is-selected', btn.dataset.side === selectedSide);
  });
  btnStart.disabled = !selectedSide || pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  if (state.side) {
    pointReadoutEl.textContent = state.point
      ? `${SIDE_LABELS[state.side]} — Point : ${state.point}`
      : SIDE_LABELS[state.side];
  } else {
    pointReadoutEl.textContent = '';
  }

  const isNewRoll = state.rolls.length > lastRollCount;
  if (isNewRoll && state.lastRoll) {
    renderDie(die1El, state.lastRoll.d1);
    renderDie(die2El, state.lastRoll.d2);
    rollTotalEl.textContent = `Total : ${state.lastRoll.total}`;
    shakeDice();
  }
  lastRollCount = state.rolls.length;

  rollHistoryEl.innerHTML = '';
  state.rolls.forEach((r) => {
    const chip = document.createElement('span');
    chip.className = 'history-chip';
    chip.textContent = r.total;
    rollHistoryEl.appendChild(chip);
  });

  if (state.phase === 'rolling') {
    hintEl.textContent = state.point
      ? `Il faut refaire ${state.point} avant un 7 pour gagner.`
      : 'Premier lancer : sortie.';
  }

  if (state.phase === 'result') {
    const label = SIDE_LABELS[state.side];
    let message;
    if (state.outcome === 'push') {
      message = `12 au sortie — ${label} : mise remboursée.`;
      resultMessageEl.classList.remove('is-lose');
    } else if (state.outcome === 'win') {
      message = `${label} gagne ! Vous remportez ${state.payout}.`;
      resultMessageEl.classList.remove('is-lose');
    } else {
      message = `${label} perd. Mise perdue.`;
      resultMessageEl.classList.add('is-lose');
    }
    resultMessageEl.textContent = message;
    if (lastPhase !== 'result') {
      resultMessageEl.classList.remove('pop');
      void resultMessageEl.offsetWidth;
      resultMessageEl.classList.add('pop');
      if (state.outcome === 'win') {
        flashTable('win');
        burstConfetti();
        dealerVoice.say('win');
      } else if (state.outcome === 'push') {
        dealerVoice.say('push');
      } else {
        flashTable('lose');
        dealerVoice.say('lose');
      }
    }
  } else {
    resultMessageEl.textContent = '';
    resultMessageEl.classList.remove('is-lose');
  }
  lastPhase = state.phase;

  if (state.isGameOver) {
    statusEl.textContent = 'Banqueroute. Cliquez sur « Nouvelle partie » pour recommencer.';
    if (!bankruptcyAnnounced) {
      bankruptcyAnnounced = true;
      dealerVoice.say('bankruptcy');
    }
  } else {
    statusEl.textContent = '';
  }
}

/* ---------------------------------------------------------------- */
/* Contrôles                                                           */
/* ---------------------------------------------------------------- */
document.querySelectorAll('.side-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    selectedSide = selectedSide === btn.dataset.side ? null : btn.dataset.side;
    render();
  });
});

document.querySelectorAll('.chip').forEach((btn) => {
  btn.addEventListener('click', () => {
    pendingBet += Number(btn.dataset.chip);
    render();
  });
});

document.getElementById('btn-clear-bet').addEventListener('click', () => {
  pendingBet = 0;
  render();
});

btnStart.addEventListener('click', () => {
  const result = game.startRound(selectedSide, pendingBet);
  if (result.ok) {
    pendingBet = 0;
    lastRollCount = 0;
    renderDie(die1El, 1);
    renderDie(die2El, 1);
    rollTotalEl.textContent = '';
    dealerVoice.say('dealing');
  }
  render();
});

btnRoll.addEventListener('click', () => {
  const wasEstablishing = game.point === null;
  game.roll();
  if (wasEstablishing && game.point !== null && game.phase === 'rolling') {
    dealerVoice.say('point_established');
  }
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  selectedSide = game.lastSide;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  game.newSession();
  pendingBet = 0;
  selectedSide = null;
  lastBankrollShown = null;
  lastPhase = null;
  lastRollCount = 0;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
