import {
  Belote, PLAYER, OPP1, FANNY, OPP2, SUITS, SUIT_SYMBOLS, SUIT_COLORS,
} from '../../src/games/belote/engine.js';
import { DecisionEngine } from '../../src/games/belote/ai.js';
import { createDealerVoice, isMuted } from '../../src/dealer/dealerVoice.js';
import { createDeckSelector } from '../../src/cards/deckSelector.js';

let SPRITE_DIR = '../../assets/cards/';
let BACK_SPRITE = `${SPRITE_DIR}back.png`;
const CARD_AUDIO_DIR = '../../assets/cards_audio/belote/';
const SUIT_TO_SPRITE = { coeur: 'hearts', carreau: 'diamonds', trefle: 'clubs', pique: 'spades' };
const SUIT_NAMES_FR = { coeur: 'Cœur', carreau: 'Carreau', trefle: 'Trèfle', pique: 'Pique' };
const SEAT_NAMES = { [PLAYER]: 'Vous', [OPP1]: 'Marcel', [FANNY]: 'Fanny', [OPP2]: 'Bernard' };
const AI_DELAY_MS = 850;
const TRICK_HOLD_MS = 5000; // au moins 5s avant de ramasser un pli
const FLY_DURATION_MS = 520;
const DEAL_FLY_MS = 380;
const DEAL_STAGGER_MS = 160;
const CUT_DURATION_MS = 750;
const TAKE_REVEAL_MS = 2200;
const TAKE_REVEAL_MS_REDUCED = 500; // toujours une vraie pause, même sans animation
const DEAL_IN_STAGGER_MS = 45;
const TOAST_HOLD_MS = 2000;
const TURNED_CARD_PAUSE_MS = 2400; // temps garanti pour observer la retourne avant toute enchère
const TURNED_CARD_PAUSE_MS_REDUCED = 700;
const LAST_TRICK_VOICE_GAP_MS = 2500; // laisse le temps d'entendre "X remporte le dernier pli" avant la voix de résultat
const SEAT_VOICE_SLUG = {
  [PLAYER]: 'vous', [OPP1]: 'marcel', [FANNY]: 'fanny', [OPP2]: 'bernard',
};

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

function cardSprite(card) {
  return `${SPRITE_DIR}${card.rank}-${SUIT_TO_SPRITE[card.suit]}.png`;
}

/** Annonce à la voix la carte retournée (« As de Cœur », etc.) - un clip
 * gTTS dédié par carte (voir tools/generate_card_audio.py), distinct des
 * répliques de Fanny puisque ce n'est pas une réplique mais un simple
 * nom de carte. Respecte le même mute que la voix de la croupière. */
const cardAnnounceAudio = new Audio();
function announceCardVoice(card) {
  if (isMuted()) return;
  cardAnnounceAudio.pause();
  cardAnnounceAudio.src = `${CARD_AUDIO_DIR}${card.rank}-${card.suit}.mp3`;
  cardAnnounceAudio.currentTime = 0;
  cardAnnounceAudio.play().catch(() => {});
}

/** Anime une carte qui s'envole en tournoyant de `sourceEl` à `destEl`,
 * puis se résout. Sert à la fois pour jouer une carte (main -> centre)
 * et pour la distribution (paquet -> main de chacun). */
function flyCard({ src, sourceEl, destEl, duration = FLY_DURATION_MS, zoomToDest = false }) {
  if (prefersReducedMotion() || !sourceEl || !destEl) return Promise.resolve();
  const sourceRect = sourceEl.getBoundingClientRect();
  const destRect = destEl.getBoundingClientRect();
  if (sourceRect.width === 0 || destRect.width === 0) return Promise.resolve();

  // zoomToDest : la carte part visuellement à la taille de la source (petite,
  // ex. une carte en main) et grossit progressivement jusqu'à la taille
  // d'arrivée (ex. une carte au centre du tapis, plus grande) - au lieu du
  // léger rétrécissement utilisé pour la distribution.
  const size = zoomToDest ? (destRect.width || sourceRect.width || 40) : (sourceRect.width || 40);
  const scaleFrom = zoomToDest ? (sourceRect.width || size) / size : 1;
  const scaleTo = zoomToDest ? 1 : 0.85;

  const img = document.createElement('img');
  img.className = 'flying-card';
  img.src = src;
  img.style.width = `${size}px`;
  img.style.left = `${sourceRect.left + sourceRect.width / 2 - size / 2}px`;
  img.style.top = `${sourceRect.top + sourceRect.height / 2 - (size * 1.4) / 2}px`;

  const dx = (destRect.left + destRect.width / 2) - (sourceRect.left + sourceRect.width / 2);
  const dy = (destRect.top + destRect.height / 2) - (sourceRect.top + sourceRect.height / 2);
  img.style.setProperty('--dx', `${dx}px`);
  img.style.setProperty('--dy', `${dy}px`);
  img.style.setProperty('--fly-duration', `${duration}ms`);
  img.style.setProperty('--scale-from', scaleFrom);
  img.style.setProperty('--scale-to', scaleTo);

  document.body.appendChild(img);
  void img.offsetWidth;
  img.classList.add('is-flying');

  return new Promise((resolve) => {
    img.addEventListener('animationend', () => { img.remove(); resolve(); }, { once: true });
    // Filet de sécurité si l'événement n'arrive pas (page masquée, etc.).
    setTimeout(() => { img.remove(); resolve(); }, duration + 300);
  });
}

function flyCardToCenter(card, sourceEl) {
  return flyCard({ src: cardSprite(card), sourceEl, destEl: trickRowEl, zoomToDest: true });
}

/* ---------------------------------------------------------------- */
/* Distribution animée : 3 cartes, puis coupe, puis 2 cartes            */
/* ---------------------------------------------------------------- */
function dealOrderFromDealer() {
  const order = [];
  let seat = (game.dealerSeat + 1) % 4;
  for (let i = 0; i < 4; i += 1) {
    order.push(seat);
    seat = (seat + 1) % 4;
  }
  return order;
}

async function dealRoundAnimation(cardsPerSeat) {
  const order = dealOrderFromDealer();
  for (let i = 0; i < cardsPerSeat; i += 1) {
    for (const seat of order) {
      flyCard({ src: BACK_SPRITE, sourceEl: deckPileEl, destEl: handElBySeat[seat], duration: DEAL_FLY_MS });
      // eslint-disable-next-line no-await-in-loop
      await new Promise((r) => setTimeout(r, DEAL_STAGGER_MS));
    }
  }
  await new Promise((r) => setTimeout(r, DEAL_FLY_MS));
}

async function animateCut() {
  announce('On coupe le paquet...');
  if (prefersReducedMotion()) {
    await new Promise((r) => setTimeout(r, 250));
    return;
  }
  deckPileEl.classList.add('is-cutting');
  await new Promise((r) => setTimeout(r, CUT_DURATION_MS));
  deckPileEl.classList.remove('is-cutting');
}

async function playDealAnimation() {
  [playerHandEl, fannyHandEl, opp1HandEl, opp2HandEl].forEach((el) => { el.innerHTML = ''; });
  deckPileEl.classList.remove('hidden');
  // La coupe clôt la mène précédente (avant la distribution elle-même),
  // pas une pause au milieu de la distribution en cours.
  await animateCut();
  announce('Distribution : trois cartes chacun...');
  await dealRoundAnimation(3);
  announce('Distribution : deux cartes chacun...');
  await dealRoundAnimation(2);
  deckPileEl.classList.add('hidden');
}

/** Une fois la prise actée (voir performBid), le donneur complète chaque
 * main jusqu'à 8 cartes : mêmes cartes qui s'envolent du talon vers chaque
 * joueur, comme pour la donne initiale - pas juste un fondu sur place. */
async function playCompletionDealAnimation() {
  deckPileEl.classList.remove('hidden');
  announce('Distribution : complément de la main...');
  await dealRoundAnimation(3);
  deckPileEl.classList.add('hidden');
}

const game = new Belote({ startingBankroll: 500 });
const botEngines = {
  [OPP1]: new DecisionEngine(OPP1),
  [FANNY]: new DecisionEngine(FANNY),
  [OPP2]: new DecisionEngine(OPP2),
};
let pendingBet = 0;
let lastBankrollShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;
let holdingTrick = null;
let lastTrickKey = null;
let lastBeloteState = null;
let aiTimer = null;
let justCompletedDeal = false;

const dealerVoice = createDealerVoice({
  game: 'belote',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const atoutBadgeEls = {
  [PLAYER]: document.getElementById('player-atout-badge'),
  [OPP1]: document.getElementById('opp1-atout-badge'),
  [FANNY]: document.getElementById('fanny-atout-badge'),
  [OPP2]: document.getElementById('opp2-atout-badge'),
};
const teamAScoreEl = document.getElementById('team-a-score');
const teamBScoreEl = document.getElementById('team-b-score');
const pileAEl = document.getElementById('pile-a');
const pileBEl = document.getElementById('pile-b');
const teamAMatchTotalEl = document.getElementById('team-a-match-total');
const teamBMatchTotalEl = document.getElementById('team-b-match-total');
const trickCounterEl = document.getElementById('trick-counter');
const fannyHandEl = document.getElementById('fanny-hand');
const opp1HandEl = document.getElementById('opp1-hand');
const opp2HandEl = document.getElementById('opp2-hand');
const playerHandEl = document.getElementById('player-hand');
const trickRowEl = document.getElementById('trick-row');
const handElBySeat = { [PLAYER]: playerHandEl, [FANNY]: fannyHandEl, [OPP1]: opp1HandEl, [OPP2]: opp2HandEl };
const deckPileEl = document.getElementById('deck-pile');
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
const seatLabelEls = {
  [PLAYER]: document.getElementById('player-seat-label'),
  [OPP1]: document.getElementById('opp1-seat-label'),
  [FANNY]: document.getElementById('fanny-seat-label'),
  [OPP2]: document.getElementById('opp2-seat-label'),
};
const turnToastEl = document.getElementById('turn-toast');

/** Bannière animée annonçant l'action de chacun (enchère, tour qui
 * commence...) - pour qu'on suive clairement qui fait quoi, pas juste un
 * texte statique qui change silencieusement. */
let toastTimer = null;
function announce(text) {
  clearTimeout(toastTimer);
  turnToastEl.textContent = text;
  turnToastEl.classList.remove('is-showing');
  void turnToastEl.offsetWidth;
  turnToastEl.classList.add('is-showing');
  toastTimer = setTimeout(() => turnToastEl.classList.remove('is-showing'), TOAST_HOLD_MS);
}

function highlightActiveSeat(activeSeat) {
  Object.entries(seatLabelEls).forEach(([seat, el]) => {
    el.classList.toggle('is-active-turn', activeSeat !== null && Number(seat) === activeSeat);
  });
}

function announceLeadIfNeeded(seat) {
  if (game.trick.length !== 0) return;
  announce(seat === PLAYER ? 'Vous entamez le pli.' : `${SEAT_NAMES[seat]} entame le pli.`);
}

function bidActionText(seat, action) {
  const who = seat === PLAYER ? 'Vous' : SEAT_NAMES[seat];
  if (action.type === 'pass') return `${who} ${seat === PLAYER ? 'passez' : 'passe'}.`;
  const verb = seat === PLAYER ? 'prenez' : 'prend';
  return `${who} ${verb} ${SUIT_SYMBOLS[action.suit]} !`;
}

/** Grand symbole de couleur qui s'affiche puis s'efface au centre de la
 * table - sert de "révélation" pour le 2e tour d'enchères, où il n'y a pas
 * de carte retournée correspondante à mettre en valeur (la couleur est
 * annoncée librement, pas montrée). */
function showSuitBurst(suit) {
  if (prefersReducedMotion()) return;
  const el = document.createElement('div');
  el.className = `suit-burst suit-${SUIT_COLORS[suit]}`;
  el.textContent = SUIT_SYMBOLS[suit];
  tableEl.appendChild(el);
  el.addEventListener('animationend', () => el.remove(), { once: true });
  setTimeout(() => el.remove(), 1600); // filet de sécurité
}

/** Temporise et met en scène la prise (qu'elle vienne du joueur ou d'un
 * bot) : le paquet et la carte retournée restent affichés à l'écran (on
 * n'a pas encore ré-affiché la main complétée), le texte d'enchère devient
 * une grosse confirmation, et la carte retournée (1er tour) ou un gros
 * symbole de couleur (2e tour) est mis en évidence quelques secondes -
 * le temps de bien voir QUI a pris et QUELLE couleur, avant que le plateau
 * ne bascule sur la main complétée et le début du jeu. */
async function revealTrumpChoice(seat, suit, round) {
  biddingButtonsEl.innerHTML = '';
  const who = seat === PLAYER ? 'Vous' : SEAT_NAMES[seat];
  const verb = seat === PLAYER ? 'prenez' : 'prend';
  biddingHintEl.textContent = `${who} ${verb} l'atout : ${SUIT_NAMES_FR[suit]} ${SUIT_SYMBOLS[suit]} !`;
  biddingHintEl.classList.add('is-reveal', `suit-${SUIT_COLORS[suit]}`);

  // Narration audio dédiée quand un BOT prend (le joueur, lui, sait déjà
  // ce qu'il vient de choisir) - annonce qui prend et à quelle couleur,
  // en plus du texte/de la mise en scène visuelle ci-dessus.
  if (seat !== PLAYER) dealerVoice.say(`take_${SEAT_VOICE_SLUG[seat]}_${suit}`);

  if (round === 1) {
    const turnedImg = biddingPanelEl.querySelector('.turned-card');
    if (turnedImg) turnedImg.classList.add('is-revealed');
  } else {
    showSuitBurst(suit);
  }

  await new Promise((r) => setTimeout(r, prefersReducedMotion() ? TAKE_REVEAL_MS_REDUCED : TAKE_REVEAL_MS));

  biddingHintEl.classList.remove('is-reveal', 'suit-red', 'suit-black');
}

/** Juste après la donne, laisse la carte retournée bien visible (grand
 * format, halo qui pulse doucement) pendant un temps garanti, AVANT que
 * la moindre enchère (même la toute première, d'un bot) ne commence -
 * sinon un bot rapide au premier tour ne laisse presque aucun temps de
 * lecture entre l'apparition de la carte et la mise en scène de la prise. */
async function pauseOnTurnedCard(turnedCard) {
  const turnedImg = biddingPanelEl.querySelector('.turned-card');
  if (turnedImg && !prefersReducedMotion()) turnedImg.classList.add('is-just-dealt');
  announce(`Carte retournée : ${SUIT_NAMES_FR[turnedCard.suit]} ${SUIT_SYMBOLS[turnedCard.suit]}`);
  announceCardVoice(turnedCard);
  await new Promise((r) => setTimeout(r, prefersReducedMotion() ? TURNED_CARD_PAUSE_MS_REDUCED : TURNED_CARD_PAUSE_MS));
}

/** Point d'entrée unique pour toute annonce d'enchère (joueur ou bot) :
 * applique la décision au moteur, annonce le toast, et - seulement pour
 * une prise - marque une vraie pause de mise en scène avant de faire
 * apparaître la main complétée (voir revealTrumpChoice). */
async function performBid(seat, action, round) {
  game.bid(seat, action);
  announce(bidActionText(seat, action));
  if (action.type === 'take') {
    await revealTrumpChoice(seat, action.suit, round);
    await playCompletionDealAnimation();
    justCompletedDeal = true;
  }
  handlePostAction();
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
/* Rendu des mains                                                      */
/* ---------------------------------------------------------------- */
/** `arriving` : vient-on de compléter la donne après une prise ? Si oui, les
 * cartes fraîchement reçues (talon + carte retournée) apparaissent avec un
 * petit flash/fondu en cascade, plutôt que de surgir instantanément - pour
 * qu'on ait le temps de les voir arriver. */
function renderBackHand(el, count, arriving) {
  el.innerHTML = '';
  for (let i = 0; i < count; i += 1) {
    const img = document.createElement('img');
    img.className = 'card back-card';
    img.src = BACK_SPRITE;
    img.alt = 'Carte cachée';
    if (arriving && !prefersReducedMotion()) {
      img.classList.add('is-dealing-in');
      img.style.animationDelay = `${i * DEAL_IN_STAGGER_MS}ms`;
    }
    el.appendChild(img);
  }
}

function renderPlayerHand(hand, legalIds, canPlay, arriving) {
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
    if (arriving && !prefersReducedMotion()) {
      img.classList.add('is-dealing-in');
      img.style.animationDelay = `${i * DEAL_IN_STAGGER_MS}ms`;
    }
    btn.appendChild(img);
    const isLegal = canPlay && legalSet.has(card.id);
    btn.disabled = !isLegal;
    if (canPlay && !legalSet.has(card.id)) btn.classList.add('is-dimmed');
    if (isLegal) {
      btn.addEventListener('click', () => {
        btn.style.visibility = 'hidden'; // la carte volante prend le relais visuellement
        flyCardToCenter(card, btn).then(() => {
          announceLeadIfNeeded(PLAYER);
          game.playCard(PLAYER, card.id);
          handlePostAction();
        });
      });
    }
    playerHandEl.appendChild(btn);
  });
}

function renderTrickRow(entries) {
  trickRowEl.innerHTML = '';
  entries.forEach((entry) => {
    const slot = document.createElement('div');
    slot.className = 'trick-slot';
    const img = document.createElement('img');
    img.className = 'card';
    img.src = cardSprite(entry.card);
    img.alt = `${entry.card.rank} de ${SUIT_NAMES_FR[entry.card.suit]}`;
    slot.appendChild(img);
    const label = document.createElement('span');
    label.className = 'trick-owner';
    label.textContent = SEAT_NAMES[entry.seat];
    slot.appendChild(label);
    trickRowEl.appendChild(slot);
  });
}

/* ---------------------------------------------------------------- */
/* Enchères                                                             */
/* ---------------------------------------------------------------- */
function renderBiddingPanel(state) {
  biddingPanelEl.innerHTML = '';
  // La carte retournée n'a de sens que pendant les enchères - une fois
  // l'atout décidé, elle ne doit pas rester en permanence au milieu de
  // la table (l'écusson "Atout" du HUD suffit à s'en souvenir).
  if (state.phase !== 'bidding' || !state.turnedCard) return;

  const label = document.createElement('p');
  label.className = 'bidding-turned-label';
  label.textContent = 'Carte retournée';
  biddingPanelEl.appendChild(label);

  const img = document.createElement('img');
  img.className = 'card turned-card';
  img.src = cardSprite(state.turnedCard);
  img.alt = `${state.turnedCard.rank} de ${SUIT_NAMES_FR[state.turnedCard.suit]}`;
  biddingPanelEl.appendChild(img);
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
      performBid(PLAYER, { type: 'take', suit: state.turnedCard.suit }, 1);
    });
    biddingButtonsEl.appendChild(takeBtn);
  } else {
    SUITS.filter((s) => s !== state.turnedCard.suit).forEach((suit) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = `btn btn-primary suit-${SUIT_COLORS[suit]}`;
      btn.textContent = `Prendre ${SUIT_SYMBOLS[suit]}`;
      btn.addEventListener('click', () => {
        performBid(PLAYER, { type: 'take', suit }, 2);
      });
      biddingButtonsEl.appendChild(btn);
    });
  }
  const passBtn = document.createElement('button');
  passBtn.type = 'button';
  passBtn.className = 'btn btn-ghost';
  passBtn.textContent = 'Passer';
  passBtn.addEventListener('click', () => {
    performBid(PLAYER, { type: 'pass' }, state.biddingRound);
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

  const activeSeat = state.phase === 'bidding' ? state.biddingTurn
    : (state.phase === 'playing' && !holdingTrick ? state.turn : null);
  highlightActiveSeat(activeSeat);

  Object.values(atoutBadgeEls).forEach((el) => { el.textContent = ''; el.className = 'atout-badge'; });
  if (state.trumpSuit && state.preneur !== null) {
    const badge = atoutBadgeEls[state.preneur];
    badge.textContent = `Atout ${SUIT_SYMBOLS[state.trumpSuit]}`;
    badge.classList.add(`suit-${SUIT_COLORS[state.trumpSuit]}`);
  }

  teamAScoreEl.textContent = state.teamScores.A;
  teamBScoreEl.textContent = state.teamScores.B;
  pileAEl.textContent = `${state.tricksWonBy.A} pli(s)`;
  pileBEl.textContent = `${state.tricksWonBy.B} pli(s)`;
  teamAMatchTotalEl.textContent = `Partie : ${state.matchScores.A} / 500`;
  teamBMatchTotalEl.textContent = `Partie : ${state.matchScores.B} / 500`;
  trickCounterEl.textContent = state.phase === 'playing' || state.phase === 'result'
    ? `Pli ${Math.min(state.trickNum + 1, 8)} / 8` : '';

  const arriving = justCompletedDeal;
  justCompletedDeal = false;
  renderBackHand(fannyHandEl, state.handCounts[FANNY], arriving);
  renderBackHand(opp1HandEl, state.handCounts[OPP1], arriving);
  renderBackHand(opp2HandEl, state.handCounts[OPP2], arriving);
  renderPlayerHand(state.playerHand, state.legalCardIds, state.phase === 'playing' && !holdingTrick && state.turn === PLAYER, arriving);

  renderBiddingPanel(state);
  renderBiddingControls(state);

  renderTrickRow(holdingTrick ? holdingTrick.cards : state.trick);

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
    const partieTag = r.partieWinner
      ? (r.partieWinner === 'A'
        ? ` — Partie remportée par votre équipe, ${r.matchScores.A} à ${r.matchScores.B} !`
        : ` — Partie remportée par l'équipe adverse, ${r.matchScores.B} à ${r.matchScores.A} !`)
      : ` — Partie en cours : ${r.matchScores.A} à ${r.matchScores.B}.`;
    resultMessageEl.textContent = (r.won
      ? `Votre équipe gagne la manche ${r.teamAScore} à ${r.teamBScore}${chuteTag}${capotTag}${beloteTag} — ${r.tier.name}, vous remportez ${r.payout} !`
      : `L'équipe adverse gagne la manche ${r.teamBScore} à ${r.teamAScore}${chuteTag}${beloteTag} — mise perdue.`) + partieTag;
    resultMessageEl.classList.toggle('is-lose', !r.won);
    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    if (r.won) {
      flashTable('win');
      burstConfetti();
    } else {
      flashTable('lose');
    }
    // La voix de résultat (gagné/perdu) est déclenchée par
    // checkForCompletedTrick(), pas ici - un léger délai après l'annonce
    // du gagnant du dernier pli évite que les deux répliques audio ne se
    // coupent la parole (la manche se termine TOUJOURS au 8e pli, donc
    // cette annonce a toujours déjà été programmée à ce stade).
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
/** Voix "gagné/perdu" de fin de manche - extraite pour pouvoir être
 * déclenchée avec un léger retard après l'annonce du gagnant du dernier
 * pli (voir checkForCompletedTrick), plutôt que de se couper la parole. */
function announceResultVoice() {
  const r = game.result;
  if (!r) return;
  let voiceDone;
  if (r.won) {
    if (r.tier.mult >= 8) voiceDone = dealerVoice.say('win_jackpot');
    else if (r.tier.mult >= 3) voiceDone = dealerVoice.say('win_big');
    else voiceDone = dealerVoice.say('win_small');
  } else {
    voiceDone = dealerVoice.say('lose');
  }
  // La partie (500 points) se termine rarement en même temps que la
  // manche : quand ça arrive, on attend que la réplique de manche soit
  // finie avant d'enchaîner (voir dealerVoice.say, qui résout à la fin
  // du clip), plutôt que de jouer les deux voix en même temps.
  if (r.partieWinner) {
    Promise.resolve(voiceDone).then(() => {
      dealerVoice.say(r.partieWinner === 'A' ? 'partie_won' : 'partie_lost');
    });
  }
}

function checkForCompletedTrick() {
  const state = game.getState();
  if (state.trick.length !== 0 || !state.lastTrick) return false;
  const key = `${state.lastTrick.cards.map((c) => c.card.id).join(',')}#${state.trickNum}`;
  if (key === lastTrickKey) return false;
  lastTrickKey = key;
  holdingTrick = state.lastTrick;

  // La manche se termine toujours au 8e pli (dix de der) : on annonce
  // explicitement qui l'a remporté, à la voix et au toast, avant que la
  // voix de résultat ne parle par-dessus (voir announceResultVoice). Pour
  // les 7 autres plis, une réplique plus courte suffit (voir SEAT_VOICE_SLUG).
  const winnerSeat = holdingTrick.winnerSeat;
  const isFinalTrick = state.phase === 'result';
  if (isFinalTrick) {
    announce(winnerSeat === PLAYER ? 'Vous remportez le dernier pli !' : `${SEAT_NAMES[winnerSeat]} remporte le dernier pli !`);
    dealerVoice.say(`last_trick_${SEAT_VOICE_SLUG[winnerSeat]}`);
  } else {
    dealerVoice.say(`trick_win_${SEAT_VOICE_SLUG[winnerSeat]}`);
  }

  render();

  if (isFinalTrick) setTimeout(announceResultVoice, LAST_TRICK_VOICE_GAP_MS);

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
      const action = botEngines[seat].decideBid(game);
      performBid(seat, action, state.biddingRound);
    }, AI_DELAY_MS);
  } else if (state.phase === 'playing' && state.turn !== PLAYER) {
    clearTimeout(aiTimer);
    aiTimer = setTimeout(() => {
      const seat = state.turn;
      const card = botEngines[seat].decideCard(game);
      flyCardToCenter(card, handElBySeat[seat]).then(() => {
        announceLeadIfNeeded(seat);
        game.playCard(seat, card.id);
        handlePostAction();
      });
    }, AI_DELAY_MS);
  }
}

function handlePostAction() {
  const wasBidding = lastPhase === 'bidding';
  const state = game.getState();
  if (wasBidding && state.phase === 'playing') {
    dealerVoice.say('dealing');
  }
  // Belote (1re carte du Roi/Dame d'atout jouée) puis Rebelote (la
  // seconde) - annoncé au moment précis où la carte tombe, peu importe
  // le pli où ça arrive dans la mène.
  if (state.beloteState !== lastBeloteState && state.beloteState !== null) {
    const label = state.beloteState === 'belote' ? 'Belote' : 'Rebelote';
    announce(`${label} !`);
    dealerVoice.say(state.beloteState === 'belote' ? 'belote_call' : 'rebelote_call');
  }
  lastBeloteState = state.beloteState;
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

btnDeal.addEventListener('click', async () => {
  const result = game.startRound(pendingBet);
  if (!result.ok) { render(); return; }

  pendingBet = 0;
  lastTrickKey = null;
  holdingTrick = null;
  lastBeloteState = null;

  bettingAreaEl.classList.add('hidden');
  biddingAreaEl.classList.remove('hidden');
  biddingButtonsEl.innerHTML = '';
  biddingHintEl.textContent = 'Distribution des cartes...';

  await playDealAnimation();

  render();
  await pauseOnTurnedCard(game.turnedCard);
  scheduleAiIfNeeded();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  clearTimeout(aiTimer);
  clearTimeout(toastTimer);
  turnToastEl.classList.remove('is-showing');
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  clearTimeout(aiTimer);
  clearTimeout(toastTimer);
  turnToastEl.classList.remove('is-showing');
  game.newSession();
  pendingBet = 0;
  lastBankrollShown = null;
  lastPhase = null;
  lastTrickKey = null;
  holdingTrick = null;
  lastBeloteState = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

createDeckSelector({
  selectEl: document.getElementById('deck-select'),
  onChange: (spriteDir) => {
    SPRITE_DIR = spriteDir;
    BACK_SPRITE = `${SPRITE_DIR}back.png`;
    deckPileEl.querySelectorAll('.deck-card').forEach((img) => { img.src = BACK_SPRITE; });
    render();
  },
});
dealerVoice.say('greeting');

// PWA : portée volontairement limitée à ce dossier (sw.js n'est enregistré
// que depuis ici, donc son scope par défaut s'arrête à games/belote/ - les
// autres jeux du casino ne sont pas concernés).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(() => {
      // Hors-ligne indisponible cette fois (hébergement sans HTTPS en local,
      // navigateur incompatible...) : le jeu reste jouable en ligne.
    });
  });
}
