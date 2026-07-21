import { Blackjack } from '../../src/games/blackjack/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const SPRITE_DIR = '../../assets/cards/';
const BACK_SPRITE = `${SPRITE_DIR}back.png`;

const WIN_RESULTS = new Set(['blackjack', 'win', 'dealer-bust']);
const LOSE_RESULTS = new Set(['lose', 'bust', 'dealer-blackjack']);

const RESULT_TO_DEALER_EVENT = {
  blackjack: 'player_blackjack',
  win: 'win',
  'dealer-bust': 'dealer_bust',
  lose: 'lose',
  bust: 'player_bust',
  'dealer-blackjack': 'dealer_blackjack',
  push: 'push',
};

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const game = new Blackjack({ startingBankroll: 500 });
let pendingBet = 0;
let lastBankrollShown = null;
let lastStatusShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;

const dealerVoice = createDealerVoice({
  game: 'blackjack',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const dealerZoneEl = document.querySelector('.dealer-cluster');
const playerZoneEl = document.querySelector('.hand-zone[data-owner="player"]');
const dealerHandEl = document.getElementById('dealer-hand');
const dealerTotalEl = document.getElementById('dealer-total');
const playerHandEl = document.getElementById('player-hand');
const playerTotalEl = document.getElementById('player-total');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const actionAreaEl = document.getElementById('action-area');
const roundOverAreaEl = document.getElementById('round-over-area');
const btnDeal = document.getElementById('btn-deal');
const btnHit = document.getElementById('btn-hit');
const btnStand = document.getElementById('btn-stand');
const btnDouble = document.getElementById('btn-double');
const chipsWrapEl = document.querySelector('.chips');

/* ---------------------------------------------------------------- */
/* Cartes : création + rendu incrémental (jamais de innerHTML='')    */
/* ---------------------------------------------------------------- */

function buildCardElement(entry, { animate }) {
  const card = document.createElement('div');
  card.className = 'card';

  const inner = document.createElement('div');
  inner.className = 'card-inner';

  const front = document.createElement('img');
  front.className = 'card-face card-front';
  front.src = `${SPRITE_DIR}${entry.card.spriteFile}`;
  front.alt = entry.card.toString();

  const back = document.createElement('img');
  back.className = 'card-face card-back';
  back.src = BACK_SPRITE;
  back.alt = 'Dos de carte';

  inner.append(front, back);
  card.append(inner);

  if (entry.hidden) card.classList.add('is-hidden');

  if (animate && !prefersReducedMotion()) {
    card.classList.add('is-dealing');
    card.style.setProperty('--deal-rot', `${(Math.random() * 12 - 6).toFixed(1)}deg`);
    card.addEventListener('animationend', () => card.classList.remove('is-dealing'), { once: true });
  }

  return card;
}

/** Met à jour une main sans jamais vider le DOM : ajoute les nouvelles
 * cartes (avec animation de distribution) et révèle la carte cachée du
 * croupier via un flip 3D quand elle passe de hidden à visible. */
function renderHand(container, entries, { staggerBase = 0 } = {}) {
  if (entries.length < container.children.length) {
    // Cas défensif (ne devrait arriver que hors du flux "ramassage").
    container.innerHTML = '';
  }

  const existing = container.children.length;

  for (let i = 0; i < existing; i += 1) {
    const cardEl = container.children[i];
    const entry = entries[i];
    if (!entry) continue;
    if (!entry.hidden && cardEl.classList.contains('is-hidden')) {
      cardEl.classList.remove('is-hidden');
    }
  }

  for (let i = existing; i < entries.length; i += 1) {
    const cardEl = buildCardElement(entries[i], { animate: true });
    if (!prefersReducedMotion()) {
      cardEl.style.animationDelay = `${staggerBase + (i - existing) * 90}ms`;
    }
    container.appendChild(cardEl);
  }

  const overlap = entries.length <= 4 ? -0.52 : Math.max(-0.78, -0.52 - (entries.length - 4) * 0.06);
  container.style.setProperty('--fan-overlap', overlap);
}

function collectHands(callback) {
  const nothingToCollect = dealerHandEl.children.length === 0 && playerHandEl.children.length === 0;
  if (nothingToCollect || prefersReducedMotion()) {
    dealerHandEl.innerHTML = '';
    playerHandEl.innerHTML = '';
    callback();
    return;
  }
  dealerZoneEl.classList.add('is-collecting');
  playerZoneEl.classList.add('is-collecting');
  setTimeout(() => {
    dealerZoneEl.classList.remove('is-collecting');
    playerZoneEl.classList.remove('is-collecting');
    dealerHandEl.innerHTML = '';
    playerHandEl.innerHTML = '';
    callback();
  }, 380);
}

/* ---------------------------------------------------------------- */
/* Confettis discrets (petites boules) — API Canvas, sans librairie  */
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
      x: cx,
      y: cy,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 1.5,
      r: 3 + Math.random() * 3,
      life: 0,
      maxLife: 60 + Math.random() * 20,
    });
  }
  if (!fxRunning) {
    fxRunning = true;
    requestAnimationFrame(tickConfetti);
  }
}

function tickConfetti() {
  fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
  particles.forEach((p) => {
    p.vy += 0.09; // gravité
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
  if (particles.length > 0) {
    requestAnimationFrame(tickConfetti);
  } else {
    fxRunning = false;
  }
}

/* ---------------------------------------------------------------- */
/* Rendu principal                                                   */
/* ---------------------------------------------------------------- */

function flashTable(kind) {
  const cls = kind === 'win' ? 'is-win-flash' : 'is-lose-flash';
  tableEl.classList.remove('is-win-flash', 'is-lose-flash');
  // reflow pour permettre de rejouer l'animation si elle vient de tourner
  void tableEl.offsetWidth;
  tableEl.classList.add(cls);
  tableEl.addEventListener('animationend', () => tableEl.classList.remove(cls), { once: true });
}

function popChipFeedback(amount) {
  const pop = document.createElement('span');
  pop.className = 'chip-pop';
  pop.textContent = `+${amount}`;
  chipsWrapEl.appendChild(pop);
  pop.addEventListener('animationend', () => pop.remove(), { once: true });
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

  // Un même résultat (ex. deux "Perdu." de suite) produit un texte identique :
  // se fier au texte seul raterait le redéclenchement du flash/confettis/voix
  // sur cette deuxième occurrence. La vraie transition, c'est l'ENTRÉE en
  // 'round-over', détectée ici indépendamment du contenu du message.
  const isFreshRoundOver = state.phase === 'round-over' && lastPhase !== 'round-over';

  if (state.message !== lastStatusShown || isFreshRoundOver) {
    statusEl.textContent = state.message;
    statusEl.classList.remove('is-win', 'is-lose', 'pop');
    if (state.result && WIN_RESULTS.has(state.result)) statusEl.classList.add('is-win');
    if (state.result && LOSE_RESULTS.has(state.result)) statusEl.classList.add('is-lose');
    if (state.message) {
      void statusEl.offsetWidth;
      statusEl.classList.add('pop');
    }
    lastStatusShown = state.message;
  }

  if (isFreshRoundOver) {
    if (WIN_RESULTS.has(state.result)) {
      flashTable('win');
      burstConfetti();
    } else if (LOSE_RESULTS.has(state.result)) {
      flashTable('lose');
      if (state.result === 'bust') {
        playerZoneEl.classList.remove('is-bust');
        void playerZoneEl.offsetWidth;
        playerZoneEl.classList.add('is-bust');
      }
    }

    const dealerEvent = RESULT_TO_DEALER_EVENT[state.result];
    if (dealerEvent) dealerVoice.say(dealerEvent);
  }

  lastPhase = state.phase;

  renderHand(dealerHandEl, state.dealerHand);
  dealerTotalEl.textContent = state.dealerHand.length ? `(${state.dealerTotal})` : '';

  renderHand(playerHandEl, state.playerHand, { staggerBase: state.dealerHand.length * 90 });
  playerTotalEl.textContent = state.playerHand.length ? `(${state.playerTotal})` : '';

  playerZoneEl.classList.toggle('is-active', state.phase === 'player-turn');

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet);

  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting');
  actionAreaEl.classList.toggle('hidden', state.phase !== 'player-turn');
  roundOverAreaEl.classList.toggle('hidden', state.phase !== 'round-over');

  btnDeal.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  btnDouble.disabled = state.playerHand.length !== 2 || state.bet > state.bankroll;

  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  if (state.isGameOver) {
    statusEl.textContent = 'Banqueroute. Cliquez sur « Nouvelle partie » pour recommencer.';
    if (!bankruptcyAnnounced) {
      bankruptcyAnnounced = true;
      dealerVoice.say('bankruptcy');
    }
  }
}

/* ---------------------------------------------------------------- */
/* Interactions                                                      */
/* ---------------------------------------------------------------- */

document.querySelectorAll('.chip').forEach((btn) => {
  btn.addEventListener('click', () => {
    const amount = Number(btn.dataset.chip);
    pendingBet += amount;
    popChipFeedback(amount);
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
  } else {
    statusEl.textContent = 'Mise invalide.';
  }
  render();
});

btnHit.addEventListener('click', () => {
  game.hit();
  render();
});

btnStand.addEventListener('click', () => {
  game.stand();
  render();
});

btnDouble.addEventListener('click', () => {
  const result = game.double();
  if (!result.ok) statusEl.textContent = 'Doublement impossible.';
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  collectHands(() => {
    game.nextRound();
    pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
    lastStatusShown = null; // permet au message vide de "reprendre" proprement
    render();
  });
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  collectHands(() => {
    game.newSession();
    pendingBet = 0;
    lastBankrollShown = null;
    lastStatusShown = null;
    lastPhase = null;
    bankruptcyAnnounced = false;
    render();
    dealerVoice.say('greeting');
  });
});

render();
dealerVoice.say('greeting');
