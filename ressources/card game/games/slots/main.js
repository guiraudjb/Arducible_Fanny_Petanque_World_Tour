import { SlotMachine, SYMBOL_GLYPHS } from '../../src/games/slots/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const WIN_TIER_TO_DEALER_EVENT = {
  jackpot: 'win_jackpot',
  big: 'win_big',
  small: 'win_small',
  none: 'lose',
};

const game = new SlotMachine({ startingBankroll: 500 });
let pendingBet = 0;
let lastBankrollShown = null;
let bankruptcyAnnounced = false;
let isSpinning = false;

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const reelEls = [0, 1, 2].map((i) => document.getElementById(`reel-${i}`));
const resultMessageEl = document.getElementById('result-message');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const resultAreaEl = document.getElementById('result-area');
const btnSpin = document.getElementById('btn-spin');
const paytableRows = document.querySelectorAll('.pay-row[data-symbol]');

const dealerVoice = createDealerVoice({
  game: 'slots',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
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

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet);
  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting' || isSpinning);
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result' || isSpinning);

  btnSpin.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  if (!isSpinning) {
    state.reels.forEach((symbol, i) => {
      const symbolEl = reelEls[i].querySelector('.reel-symbol');
      symbolEl.textContent = SYMBOL_GLYPHS[symbol];
      symbolEl.classList.toggle('is-seven', symbol === 'seven');
    });
  }

  const winning = state.phase === 'result' && state.payoutMultiplier > 0;
  reelEls.forEach((el) => el.classList.toggle('is-winning', winning && !isSpinning));

  paytableRows.forEach((row) => {
    const sym = row.dataset.symbol;
    let achieved = false;
    if (state.phase === 'result' && !isSpinning) {
      const [a, b, c] = state.reels;
      if (sym === 'cherry2') {
        achieved = state.payoutMultiplier === 2 && [a, b, c].filter((s) => s === 'cherry').length === 2;
      } else {
        achieved = a === sym && b === sym && c === sym;
      }
    }
    row.classList.toggle('achieved', achieved);
  });

  if (state.phase === 'result' && !isSpinning) {
    const won = state.payoutMultiplier > 0;
    resultMessageEl.textContent = won
      ? `Gagné — ${state.payout} !`
      : 'Perdu.';
    resultMessageEl.classList.toggle('is-lose', !won);
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
    pendingBet += Number(btn.dataset.chip);
    render();
  });
});

document.getElementById('btn-clear-bet').addEventListener('click', () => {
  pendingBet = 0;
  render();
});

const SPIN_ANIM_MS = 900;
const RANDOM_GLYPHS = Object.values(SYMBOL_GLYPHS);

btnSpin.addEventListener('click', () => {
  if (pendingBet <= 0) return;
  isSpinning = true;
  dealerVoice.say('spinning');
  render();

  let cycleTimer = null;
  if (!prefersReducedMotion()) {
    reelEls.forEach((el) => el.classList.add('is-spinning'));
    cycleTimer = setInterval(() => {
      reelEls.forEach((el) => {
        const glyph = RANDOM_GLYPHS[Math.floor(Math.random() * RANDOM_GLYPHS.length)];
        el.querySelector('.reel-symbol').textContent = glyph;
      });
    }, 90);
  }

  const settle = () => {
    if (cycleTimer) clearInterval(cycleTimer);
    reelEls.forEach((el) => el.classList.remove('is-spinning'));

    const result = game.spin(pendingBet);
    if (!result.ok) {
      statusEl.textContent = 'Mise invalide.';
      isSpinning = false;
      render();
      return;
    }
    pendingBet = 0;
    isSpinning = false;
    render();

    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    const state = game.getState();
    const dealerEvent = WIN_TIER_TO_DEALER_EVENT[state.winTier];
    if (state.payoutMultiplier > 0) {
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
  pendingBet = 0;
  lastBankrollShown = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
