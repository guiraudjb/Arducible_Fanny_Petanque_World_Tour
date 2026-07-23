import {
  Belote, PLAYER, OPP1, FANNY, OPP2, SUITS, SUIT_SYMBOLS, SUIT_COLORS,
  chooseAiBid, chooseAiCard,
} from '../../src/games/belote/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const SPRITE_DIR = '../../assets/cards/';
const BACK_SPRITE = `${SPRITE_DIR}back.png`;
const SUIT_TO_SPRITE = { coeur: 'hearts', carreau: 'diamonds', trefle: 'clubs', pique: 'spades' };
const SUIT_NAMES_FR = { coeur: 'Cœur', carreau: 'Carreau', trefle: 'Trèfle', pique: 'Pique' };
const SEAT_NAMES = { [PLAYER]: 'Vous', [OPP1]: 'Marcel', [FANNY]: 'Fanny', [OPP2]: 'Bernard' };
const AI_DELAY_MS = 650;
const TRICK_HOLD_MS = 900;

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function cardSprite(card) {
  return `${SPRITE_DIR}${card.rank}-${SUIT_TO_SPRITE[card.suit]}.png`;
}

const game = new Belote({ startingBankroll: 500 });
let pendingBet = 0;
let lastBankrollShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;
let holdingTrick = null;
let lastTrickKey = null;
let aiTimer = null;

const dealerVoice = createDealerVoice({
  game: 'belote',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const hudTrumpEl = document.getElementById('hud-trump');
const teamAScoreEl = document.getElementById('team-a-score');
const teamBScoreEl = document.getElementById('team-b-score');
const pileAEl = document.getElementById('pile-a');
const pileBEl = document.getElementById('pile-b');
const trickCounterEl = document.getElementById('trick-counter');
const fannyHandEl = document.getElementById('fanny-hand');
const opp1HandEl = document.getElementById('opp1-hand');
const opp2HandEl = document.getElementById('opp2-hand');
const playerHandEl = document.getElementById('player-hand');
const trickSlots = {
  player: document.getElementById('trick-player'),
  fanny: document.getElementById('trick-fanny'),
  opp1: document.getElementById('trick-opp1'),
  opp2: document.getElementById('trick-opp2'),
};
const biddingPanelEl = document.getElementById('bidding-panel');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const biddingAreaEl = document.getElementById('bidding-area');
const biddingHintEl = document.getElementById('bidding-hint');
const biddingButtonsEl = document.getElementById('bidding-buttons');
const playingAreaEl = document.getElementById('playing-area');
const resultAreaEl = document.getElementById('result-area');
const resultMessageEl = document.getElementById('result-message');
const hintEl = document.getElementById('hint');
const btnDeal = document.getElementById('btn-deal');
const dealerTagEls = {
  [PLAYER]: document.getElementById('player-dealer-tag'),
  [OPP1]: document.getElementById('opp1-dealer-tag'),
  [FANNY]: document.getElementById('fanny-dealer-tag'),
  [OPP2]: document.getElementById('opp2-dealer-tag'),
};

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
/* Rendu des mains                                                      */
/* ---------------------------------------------------------------- */
function renderBackHand(el, count) {
  el.innerHTML = '';
  for (let i = 0; i < count; i += 1) {
    const img = document.createElement('img');
    img.className = 'card back-card';
    img.src = BACK_SPRITE;
    img.alt = 'Carte cachée';
    el.appendChild(img);
  }
}

function renderPlayerHand(hand, legalIds, canPlay) {
  playerHandEl.innerHTML = '';
  const legalSet = new Set(legalIds);
  const n = hand.length;
  const mid = (n - 1) / 2;
  hand.forEach((card, i) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'card-btn';
    const angle = (i - mid) * 6; // degrés par carte, éventail
    const lift = Math.abs(i - mid) * Math.abs(i - mid) * 1.1; // arc : les extrémités descendent légèrement
    btn.style.transform = `rotate(${angle}deg) translateY(${lift}px)`;
    btn.style.zIndex = String(100 - Math.abs(i - mid));
    const img = document.createElement('img');
    img.className = 'card';
    img.src = cardSprite(card);
    img.alt = `${card.rank} de ${SUIT_NAMES_FR[card.suit]}`;
    btn.appendChild(img);
    const isLegal = canPlay && legalSet.has(card.id);
    btn.disabled = !isLegal;
    if (canPlay && !legalSet.has(card.id)) btn.classList.add('is-dimmed');
    if (isLegal) {
      btn.addEventListener('click', () => {
        game.playCard(PLAYER, card.id);
        handlePostAction();
      });
    }
    playerHandEl.appendChild(btn);
  });
}

function renderTrickCard(el, entry) {
  el.innerHTML = '';
  if (!entry) return;
  const img = document.createElement('img');
  img.className = 'card';
  img.src = cardSprite(entry.card);
  img.alt = `${entry.card.rank} de ${SUIT_NAMES_FR[entry.card.suit]}`;
  el.appendChild(img);
}

/* ---------------------------------------------------------------- */
/* Enchères                                                             */
/* ---------------------------------------------------------------- */
function renderBiddingPanel(state) {
  biddingPanelEl.innerHTML = '';
  if (state.phase !== 'bidding' && state.phase !== 'playing' && state.phase !== 'result') {
    return;
  }
  if (!state.turnedCard) return;

  const label = document.createElement('p');
  label.className = 'bidding-turned-label';
  label.textContent = state.phase === 'bidding' ? 'Carte retournée' : 'Atout';
  biddingPanelEl.appendChild(label);

  const img = document.createElement('img');
  img.className = 'card turned-card';
  img.src = cardSprite(state.turnedCard);
  img.alt = `${state.turnedCard.rank} de ${SUIT_NAMES_FR[state.turnedCard.suit]}`;
  biddingPanelEl.appendChild(img);

  if (state.phase === 'bidding') {
    const log = document.createElement('p');
    log.className = 'bidding-log';
    log.id = 'bidding-log-text';
    biddingPanelEl.appendChild(log);
  }
}

function renderBiddingControls(state) {
  biddingAreaEl.classList.toggle('hidden', state.phase !== 'bidding');
  if (state.phase !== 'bidding') return;

  const isPlayerTurn = state.biddingTurn === PLAYER;
  biddingHintEl.textContent = isPlayerTurn
    ? (state.biddingRound === 1
      ? `À vous : prendre à ${SUIT_SYMBOLS[state.turnedCard.suit]} ou passer ?`
      : 'Personne n\'a pris : à vous d\'annoncer une autre couleur, ou de passer.')
    : `${SEAT_NAMES[state.biddingTurn]} réfléchit...`;

  biddingButtonsEl.innerHTML = '';
  if (!isPlayerTurn) return;

  if (state.biddingRound === 1) {
    const takeBtn = document.createElement('button');
    takeBtn.type = 'button';
    takeBtn.className = 'btn btn-primary';
    takeBtn.textContent = `Prendre ${SUIT_SYMBOLS[state.turnedCard.suit]}`;
    takeBtn.addEventListener('click', () => {
      game.bid(PLAYER, { type: 'take', suit: state.turnedCard.suit });
      handlePostAction();
    });
    biddingButtonsEl.appendChild(takeBtn);
  } else {
    SUITS.filter((s) => s !== state.turnedCard.suit).forEach((suit) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `btn btn-primary suit-${SUIT_COLORS[suit]}`;
      btn.textContent = `Prendre ${SUIT_SYMBOLS[suit]}`;
      btn.addEventListener('click', () => {
        game.bid(PLAYER, { type: 'take', suit });
        handlePostAction();
      });
      biddingButtonsEl.appendChild(btn);
    });
  }
  const passBtn = document.createElement('button');
  passBtn.type = 'button';
  passBtn.className = 'btn btn-ghost';
  passBtn.textContent = 'Passer';
  passBtn.addEventListener('click', () => {
    game.bid(PLAYER, { type: 'pass' });
    handlePostAction();
  });
  biddingButtonsEl.appendChild(passBtn);
}

/* ---------------------------------------------------------------- */
/* Rendu principal                                                     */
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
  playingAreaEl.classList.toggle('hidden', state.phase !== 'playing');
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');

  btnDeal.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  Object.entries(dealerTagEls).forEach(([seat, el]) => {
    el.textContent = Number(seat) === state.dealerSeat ? '🂠 distributeur' : '';
  });

  if (state.trumpSuit) {
    hudTrumpEl.innerHTML = '';
    const badge = document.createElement('span');
    badge.className = `trump-badge suit-${SUIT_COLORS[state.trumpSuit]}`;
    badge.textContent = `Atout ${SUIT_SYMBOLS[state.trumpSuit]}`;
    hudTrumpEl.appendChild(badge);
  } else {
    hudTrumpEl.innerHTML = '';
  }

  teamAScoreEl.textContent = state.teamScores.A;
  teamBScoreEl.textContent = state.teamScores.B;
  pileAEl.textContent = `${state.tricksWonBy.A} pli(s)`;
  pileBEl.textContent = `${state.tricksWonBy.B} pli(s)`;
  trickCounterEl.textContent = state.phase === 'playing' || state.phase === 'result'
    ? `Pli ${Math.min(state.trickNum + 1, 8)} / 8` : '';

  renderBackHand(fannyHandEl, state.handCounts[FANNY]);
  renderBackHand(opp1HandEl, state.handCounts[OPP1]);
  renderBackHand(opp2HandEl, state.handCounts[OPP2]);
  renderPlayerHand(state.playerHand, state.legalCardIds, state.phase === 'playing' && state.turn === PLAYER);

  renderBiddingPanel(state);
  renderBiddingControls(state);

  const trickToShow = holdingTrick ? holdingTrick.cards : state.trick;
  const bySeat = { player: null, fanny: null, opp1: null, opp2: null };
  const seatKey = { [PLAYER]: 'player', [FANNY]: 'fanny', [OPP1]: 'opp1', [OPP2]: 'opp2' };
  trickToShow.forEach((entry) => { bySeat[seatKey[entry.seat]] = entry; });
  Object.entries(trickSlots).forEach(([key, el]) => renderTrickCard(el, bySeat[key]));

  if (state.phase === 'playing') {
    hintEl.textContent = holdingTrick
      ? `${SEAT_NAMES[holdingTrick.winnerSeat]} remporte le pli.`
      : (state.turn === PLAYER ? 'À vous de jouer.' : `${SEAT_NAMES[state.turn]} réfléchit...`);
  }

  const isFreshResult = state.phase === 'result' && lastPhase !== 'result';
  if (isFreshResult) {
    const r = state.result;
    const capotTag = r.capotTeam ? (r.capotTeam === 'A' ? ' — CAPOT pour votre équipe !' : ' — Capot pour l\'équipe adverse.') : '';
    const beloteTag = r.beloteTeam ? (r.beloteTeam === 'A' ? ' (Belote-Rebelote pour votre équipe, +20)' : ' (Belote-Rebelote pour l\'équipe adverse, +20)') : '';
    const chuteTag = r.chute ? (r.preneurTeam === 'A' ? ' — vous avez chuté !' : ' — l\'équipe adverse a chuté !') : '';
    resultMessageEl.textContent = r.won
      ? `Votre équipe gagne la manche ${r.teamAScore} à ${r.teamBScore}${chuteTag}${capotTag}${beloteTag} — ${r.tier.name}, vous remportez ${r.payout} !`
      : `L'équipe adverse gagne la manche ${r.teamBScore} à ${r.teamAScore}${chuteTag}${beloteTag} — mise perdue.`;
    resultMessageEl.classList.toggle('is-lose', !r.won);
    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    if (r.won) {
      flashTable('win');
      burstConfetti();
      if (r.tier.mult >= 8) dealerVoice.say('win_jackpot');
      else if (r.tier.mult >= 3) dealerVoice.say('win_big');
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
/* Orchestration IA + délai d'affichage des plis                       */
/* ---------------------------------------------------------------- */
function checkForCompletedTrick() {
  const state = game.getState();
  if (state.trick.length !== 0 || !state.lastTrick) return false;
  const key = `${state.lastTrick.cards.map((c) => c.card.id).join(',')}#${state.trickNum}`;
  if (key === lastTrickKey) return false;
  lastTrickKey = key;
  holdingTrick = state.lastTrick;
  render();
  clearTimeout(aiTimer);
  aiTimer = setTimeout(() => {
    holdingTrick = null;
    render();
    scheduleAiIfNeeded();
  }, TRICK_HOLD_MS);
  return true;
}

function scheduleAiIfNeeded() {
  const state = game.getState();
  if (state.phase === 'bidding' && state.biddingTurn !== PLAYER) {
    clearTimeout(aiTimer);
    aiTimer = setTimeout(() => {
      const seat = state.biddingTurn;
      const action = chooseAiBid(game.hands[seat], state.biddingRound, state.turnedCard);
      game.bid(seat, action);
      handlePostAction();
    }, AI_DELAY_MS);
  } else if (state.phase === 'playing' && state.turn !== PLAYER) {
    clearTimeout(aiTimer);
    aiTimer = setTimeout(() => {
      const seat = state.turn;
      const card = chooseAiCard(game.hands[seat], game.trick, game.trumpSuit, seat);
      game.playCard(seat, card.id);
      handlePostAction();
    }, AI_DELAY_MS);
  }
}

function handlePostAction() {
  const wasBidding = lastPhase === 'bidding';
  const state = game.getState();
  if (wasBidding && state.phase === 'playing') {
    dealerVoice.say('dealing');
  }
  const trickHeld = checkForCompletedTrick();
  render();
  if (!trickHeld) scheduleAiIfNeeded();
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

btnDeal.addEventListener('click', () => {
  const result = game.startRound(pendingBet);
  if (result.ok) {
    pendingBet = 0;
    lastTrickKey = null;
    holdingTrick = null;
    render();
    scheduleAiIfNeeded();
  } else {
    render();
  }
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  clearTimeout(aiTimer);
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  clearTimeout(aiTimer);
  game.newSession();
  pendingBet = 0;
  lastBankrollShown = null;
  lastPhase = null;
  lastTrickKey = null;
  holdingTrick = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
