import { Keno, MAX_NUMBER, MAX_PICKS } from '../../src/games/keno/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const game = new Keno({ startingBankroll: 500 });
let pendingBet = 0;
let lastBankrollShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;

const dealerVoice = createDealerVoice({
  game: 'keno',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const paytableEl = document.getElementById('paytable');
const gridEl = document.getElementById('number-grid');
const picksReadoutEl = document.getElementById('picks-readout');
const resultMessageEl = document.getElementById('result-message');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const resultAreaEl = document.getElementById('result-area');
const btnDraw = document.getElementById('btn-draw');
const btnClearPicks = document.getElementById('btn-clear-picks');

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

/* ---------------------------------------------------------------- */
/* Grille de numéros                                                    */
/* ---------------------------------------------------------------- */
for (let n = 1; n <= MAX_NUMBER; n += 1) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'num-cell';
  btn.textContent = String(n);
  btn.dataset.number = String(n);
  btn.addEventListener('click', () => {
    game.togglePick(n);
    render();
  });
  gridEl.appendChild(btn);
}

/* ---------------------------------------------------------------- */
/* Rendu                                                               */
/* ---------------------------------------------------------------- */
function renderPaytable(picksCount, state) {
  paytableEl.innerHTML = '';
  if (picksCount === 0) {
    const hint = document.createElement('p');
    hint.className = 'paytable-hint';
    hint.textContent = 'Choisissez vos numéros pour découvrir la grille de gains.';
    paytableEl.appendChild(hint);
    return;
  }
  const row = state.paytableRow || {};
  Object.entries(row).forEach(([hits, mult]) => {
    const el = document.createElement('div');
    el.className = 'pay-row';
    if (state.phase === 'result' && state.hits === Number(hits)) el.classList.add('achieved');
    const nameEl = document.createElement('span');
    nameEl.className = 'pay-name';
    nameEl.textContent = `${hits} bons num.`;
    const multEl = document.createElement('span');
    multEl.className = 'pay-mult';
    multEl.textContent = `${mult}x`;
    el.append(nameEl, multEl);
    paytableEl.appendChild(el);
  });
}

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
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');

  const canPlay = state.phase === 'betting';
  const drawnSet = new Set(state.drawn);
  const picksSet = new Set(state.picks);
  [...gridEl.children].forEach((btn) => {
    const n = Number(btn.dataset.number);
    btn.classList.toggle('is-picked', picksSet.has(n));
    btn.classList.toggle('is-drawn', state.phase === 'result' && drawnSet.has(n));
    btn.classList.toggle('is-hit', state.phase === 'result' && drawnSet.has(n) && picksSet.has(n));
    btn.disabled = !canPlay || (!picksSet.has(n) && state.picks.length >= MAX_PICKS);
  });

  picksReadoutEl.textContent = state.phase === 'betting'
    ? `${state.picks.length} / ${MAX_PICKS} numéros choisis`
    : `${state.hits} bon(s) numéro(s) sur ${state.picks.length} choisis`;

  renderPaytable(state.picks.length, state);

  btnDraw.disabled = state.picks.length === 0 || pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  btnClearPicks.disabled = state.picks.length === 0;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  const isFreshResult = state.phase === 'result' && lastPhase !== 'result';
  if (isFreshResult) {
    const won = state.payout > 0;
    resultMessageEl.textContent = won
      ? `${state.hits} bons numéros — ${state.multiplier}x, vous gagnez ${state.payout} !`
      : `${state.hits} bons numéros — pas de gain cette fois.`;
    resultMessageEl.classList.toggle('is-lose', !won);
    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    if (won) {
      flashTable('win');
      burstConfetti();
      if (state.multiplier >= 500) dealerVoice.say('win_jackpot');
      else if (state.multiplier >= 20) dealerVoice.say('win_big');
      else dealerVoice.say('win_small');
    } else {
      flashTable('lose');
      dealerVoice.say('lose');
    }
  } else if (state.phase === 'betting') {
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

btnClearPicks.addEventListener('click', () => {
  game.clearPicks();
  render();
});

btnDraw.addEventListener('click', () => {
  const result = game.draw(pendingBet);
  if (result.ok) {
    pendingBet = 0;
    dealerVoice.say('dealing');
  }
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  game.newSession();
  pendingBet = 0;
  lastBankrollShown = null;
  lastPhase = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
