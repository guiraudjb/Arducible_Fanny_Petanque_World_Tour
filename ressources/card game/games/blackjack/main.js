import { Blackjack } from '../../src/games/blackjack/engine.js';

const SPRITE_DIR = '../../assets/cards/';
const BACK_SPRITE = `${SPRITE_DIR}back.png`;

const game = new Blackjack({ startingBankroll: 500 });
let pendingBet = 0;

const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
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

function cardImg({ card, hidden }) {
  const img = document.createElement('img');
  img.className = 'card';
  img.src = hidden ? BACK_SPRITE : `${SPRITE_DIR}${card.spriteFile}`;
  img.alt = hidden ? 'Carte cachée' : card.toString();
  return img;
}

function render() {
  const state = game.getState();

  bankrollEl.textContent = `Bankroll : ${state.bankroll}`;
  statusEl.textContent = state.message;

  dealerHandEl.innerHTML = '';
  state.dealerHand.forEach((entry) => dealerHandEl.appendChild(cardImg(entry)));
  dealerTotalEl.textContent = state.dealerHand.length ? `(${state.dealerTotal})` : '';

  playerHandEl.innerHTML = '';
  state.playerHand.forEach((entry) => playerHandEl.appendChild(cardImg(entry)));
  playerTotalEl.textContent = state.playerHand.length ? `(${state.playerTotal})` : '';

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
    statusEl.textContent = 'Banqueroute. Cliquez sur "Nouvelle partie" pour recommencer.';
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
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  game.newSession();
  pendingBet = 0;
  render();
});

render();
