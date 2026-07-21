import { VideoPoker } from '../../src/games/poker/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const SPRITE_DIR = '../../assets/cards/';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const HAND_RANK_TO_DEALER_EVENT = {
  'royal-flush': 'win_jackpot',
  'straight-flush': 'win_jackpot',
  'four-of-a-kind': 'win_jackpot',
  'full-house': 'win_big',
  flush: 'win_big',
  straight: 'win_big',
  'three-of-a-kind': 'win_small',
  'two-pair': 'win_small',
  'jacks-or-better': 'win_small',
  nothing: 'lose',
};

const game = new VideoPoker({ startingBankroll: 500 });
let pendingBet = 0;
let lastBankrollShown = null;
let bankruptcyAnnounced = false;

const dealerVoice = createDealerVoice({
  game: 'poker',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const handEl = document.getElementById('hand');
const resultMessageEl = document.getElementById('result-message');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const holdingAreaEl = document.getElementById('holding-area');
const resultAreaEl = document.getElementById('result-area');
const btnDeal = document.getElementById('btn-deal');
const btnDraw = document.getElementById('btn-draw');
const paytableRows = document.querySelectorAll('.pay-row[data-rank]');

/* ---------------------------------------------------------------- */
/* Confettis (mêmes principes que le Blackjack)                      */
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
/* Cartes                                                             */
/* ---------------------------------------------------------------- */

function buildCardSlot(entry, index) {
  const slot = document.createElement('div');
  slot.className = 'card-slot';
  if (entry.held) slot.classList.add('held');

  const card = document.createElement('div');
  card.className = 'card';

  const img = document.createElement('img');
  img.src = `${SPRITE_DIR}${entry.card.spriteFile}`;
  img.alt = entry.card.toString();
  img.addEventListener('click', () => {
    if (game.getState().phase !== 'holding') return;
    game.toggleHold(index);
    render();
  });
  card.appendChild(img);
  slot.appendChild(card);

  const label = document.createElement('div');
  label.className = 'hold-label';
  label.textContent = 'GARDÉE';
  slot.appendChild(label);

  return slot;
}

let lastHandKey = null; // signature pour détecter une nouvelle donne complète

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
  holdingAreaEl.classList.toggle('hidden', state.phase !== 'holding');
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');

  btnDeal.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  const handKey = state.hand.map((e) => e.card.toString()).join('|') + `#${state.phase}`;
  const isFreshDeal = state.hand.length > 0 && handEl.children.length === 0;

  if (handEl.children.length === 0 && state.hand.length > 0) {
    // Nouvelle donne : on construit les 5 cartes avec l'animation de distribution.
    state.hand.forEach((entry, index) => {
      const slot = buildCardSlot(entry, index);
      if (isFreshDeal && !prefersReducedMotion()) {
        const cardEl = slot.querySelector('.card');
        cardEl.classList.add('is-dealing');
        cardEl.style.setProperty('--deal-rot', `${(Math.random() * 12 - 6).toFixed(1)}deg`);
        cardEl.style.animationDelay = `${index * 90}ms`;
        cardEl.addEventListener('animationend', () => cardEl.classList.remove('is-dealing'), { once: true });
      }
      handEl.appendChild(slot);
    });
  } else if (state.hand.length === 0) {
    handEl.innerHTML = '';
  } else {
    // Mise à jour en place : held-state + éventuel remplacement de carte (tirage).
    state.hand.forEach((entry, index) => {
      const slot = handEl.children[index];
      if (!slot) return;
      slot.classList.toggle('held', entry.held);
      const img = slot.querySelector('img');
      const newSrc = `${SPRITE_DIR}${entry.card.spriteFile}`;
      if (img.dataset.currentCard !== entry.card.toString() && !entry.held) {
        // La carte a changé (tirage) : petite animation de "swap" façon flip.
        if (prefersReducedMotion()) {
          img.src = newSrc;
          img.alt = entry.card.toString();
        } else {
          img.classList.add('is-swap-out');
          img.addEventListener('animationend', function onOut() {
            img.removeEventListener('animationend', onOut);
            img.src = newSrc;
            img.alt = entry.card.toString();
            img.classList.remove('is-swap-out');
            img.classList.add('is-swap-in');
            img.addEventListener('animationend', () => img.classList.remove('is-swap-in'), { once: true });
          }, { once: true });
        }
      }
      img.dataset.currentCard = entry.card.toString();
    });
  }

  paytableRows.forEach((row) => {
    row.classList.toggle('achieved', state.phase === 'result' && row.dataset.rank === state.handRank);
  });

  if (state.phase === 'result') {
    const won = state.payout > 0;
    resultMessageEl.textContent = won
      ? `${state.handName} — vous gagnez ${state.payout} !`
      : `${state.handName} — perdu.`;
    resultMessageEl.classList.toggle('is-lose', !won);
    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');
    if (handKey !== lastHandKey) {
      if (won) { flashTable('win'); burstConfetti(); } else { flashTable('lose'); }
      const dealerEvent = HAND_RANK_TO_DEALER_EVENT[state.handRank];
      if (dealerEvent) dealerVoice.say(dealerEvent);
    }
  } else {
    resultMessageEl.textContent = '';
    resultMessageEl.classList.remove('is-lose');
  }
  lastHandKey = handKey;

  statusEl.textContent = state.isGameOver
    ? 'Banqueroute. Cliquez sur « Nouvelle partie » pour recommencer.'
    : '';
  if (state.isGameOver && !bankruptcyAnnounced) {
    bankruptcyAnnounced = true;
    dealerVoice.say('bankruptcy');
  }
}

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
  const result = game.startRound(pendingBet);
  if (result.ok) {
    pendingBet = 0;
    dealerVoice.say('dealing');
  }
  render();
});

btnDraw.addEventListener('click', () => {
  game.draw();
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  handEl.innerHTML = '';
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  lastHandKey = null;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  handEl.innerHTML = '';
  game.newSession();
  pendingBet = 0;
  lastBankrollShown = null;
  lastHandKey = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
