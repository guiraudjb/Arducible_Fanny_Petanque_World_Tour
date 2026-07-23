import { Baccara, SIDE_LABELS } from '../../src/games/baccara/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const SPRITE_DIR = '../../assets/cards/';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const game = new Baccara({ startingBankroll: 500 });
let pendingBet = 0;
let selectedSide = null;
let lastBankrollShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;

const dealerVoice = createDealerVoice({
  game: 'baccara',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const bankerZoneEl = document.querySelector('.dealer-cluster');
const playerZoneEl = document.querySelector('.hand-zone[data-owner="player"]');
const bankerHandEl = document.getElementById('banker-hand');
const bankerTotalEl = document.getElementById('banker-total');
const playerHandEl = document.getElementById('player-hand');
const playerTotalEl = document.getElementById('player-total');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const roundOverAreaEl = document.getElementById('round-over-area');
const btnDeal = document.getElementById('btn-deal');

/* ---------------------------------------------------------------- */
/* Cartes                                                             */
/* ---------------------------------------------------------------- */
function buildCardElement(card, { animate, delay }) {
  const el = document.createElement('div');
  el.className = 'card';
  const img = document.createElement('img');
  img.className = 'card-face card-front';
  img.src = `${SPRITE_DIR}${card.spriteFile}`;
  img.alt = card.toString();
  el.appendChild(img);
  if (animate && !prefersReducedMotion()) {
    el.classList.add('is-dealing');
    el.style.setProperty('--deal-rot', `${(Math.random() * 12 - 6).toFixed(1)}deg`);
    el.style.animationDelay = `${delay}ms`;
    el.addEventListener('animationend', () => el.classList.remove('is-dealing'), { once: true });
  }
  return el;
}

function renderHand(container, cards, { staggerBase = 0 } = {}) {
  if (cards.length < container.children.length) container.innerHTML = '';
  const existing = container.children.length;
  for (let i = existing; i < cards.length; i += 1) {
    container.appendChild(buildCardElement(cards[i], { animate: true, delay: staggerBase + (i - existing) * 90 }));
  }
  const overlap = cards.length <= 4 ? -0.52 : Math.max(-0.78, -0.52 - (cards.length - 4) * 0.06);
  container.style.setProperty('--fan-overlap', overlap);
}

function collectHands(callback) {
  if ((bankerHandEl.children.length === 0 && playerHandEl.children.length === 0) || prefersReducedMotion()) {
    bankerHandEl.innerHTML = '';
    playerHandEl.innerHTML = '';
    callback();
    return;
  }
  bankerZoneEl.classList.add('is-collecting');
  playerZoneEl.classList.add('is-collecting');
  setTimeout(() => {
    bankerZoneEl.classList.remove('is-collecting');
    playerZoneEl.classList.remove('is-collecting');
    bankerHandEl.innerHTML = '';
    playerHandEl.innerHTML = '';
    callback();
  }, 380);
}

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

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet.amount);
  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting');
  roundOverAreaEl.classList.toggle('hidden', state.phase !== 'result');

  document.querySelectorAll('.side-btn').forEach((btn) => {
    btn.classList.toggle('is-selected', btn.dataset.side === selectedSide);
  });
  btnDeal.disabled = !selectedSide || pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  renderHand(bankerHandEl, state.bankerHand);
  bankerTotalEl.textContent = state.bankerHand.length ? `(${state.bankerTotal})` : '';
  renderHand(playerHandEl, state.playerHand, { staggerBase: state.bankerHand.length * 90 });
  playerTotalEl.textContent = state.playerHand.length ? `(${state.playerTotal})` : '';

  const isFreshResult = state.phase === 'result' && lastPhase !== 'result';
  if (isFreshResult) {
    const won = state.payout > state.bet.amount;
    const push = state.payout === state.bet.amount && state.bet.side !== 'tie' && state.winner === 'tie';
    const betLabel = SIDE_LABELS[state.bet.side];
    let message;
    if (push) {
      message = `Égalité — mise remboursée (misé sur ${betLabel}).`;
    } else if (won) {
      message = `${SIDE_LABELS[state.winner]} gagne ! Vous remportez ${state.payout}.`;
    } else {
      message = `${SIDE_LABELS[state.winner]} gagne. Perdu (misé sur ${betLabel}).`;
    }
    statusEl.textContent = message;
    statusEl.classList.remove('is-win', 'is-lose', 'pop');
    if (won) statusEl.classList.add('is-win');
    else if (!push) statusEl.classList.add('is-lose');
    void statusEl.offsetWidth;
    statusEl.classList.add('pop');

    if (won) {
      flashTable('win');
      burstConfetti();
      dealerVoice.say(state.winner === 'tie' ? 'win_jackpot' : 'win_small');
    } else if (push) {
      dealerVoice.say('push');
    } else {
      flashTable('lose');
      dealerVoice.say('lose');
    }
  } else if (state.phase === 'betting') {
    statusEl.textContent = '';
    statusEl.classList.remove('is-win', 'is-lose');
  }
  lastPhase = state.phase;

  if (state.isGameOver) {
    statusEl.textContent = 'Banqueroute. Cliquez sur « Nouvelle partie » pour recommencer.';
    if (!bankruptcyAnnounced) {
      bankruptcyAnnounced = true;
      dealerVoice.say('bankruptcy');
    }
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

btnDeal.addEventListener('click', () => {
  const result = game.deal({ side: selectedSide, amount: pendingBet });
  if (result.ok) {
    pendingBet = 0;
    dealerVoice.say('dealing');
  }
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  collectHands(() => {
    game.nextRound();
    pendingBet = Math.min(game.lastBet ? game.lastBet.amount : 0, game.bankroll) || 0;
    selectedSide = game.lastBet ? game.lastBet.side : null;
    render();
  });
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  collectHands(() => {
    game.newSession();
    pendingBet = 0;
    selectedSide = null;
    lastBankrollShown = null;
    lastPhase = null;
    bankruptcyAnnounced = false;
    render();
    dealerVoice.say('greeting');
  });
});

render();
dealerVoice.say('greeting');
