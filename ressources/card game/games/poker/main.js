import { VideoPoker } from '../../src/games/poker/engine.js';

const SPRITE_DIR = '../../assets/cards/';

const game = new VideoPoker({ startingBankroll: 500 });
let pendingBet = 0;

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
const paytableRows = document.querySelectorAll('#paytable tr[data-rank]');

function render() {
  const state = game.getState();

  bankrollEl.textContent = `Bankroll : ${state.bankroll}`;
  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet);

  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting');
  holdingAreaEl.classList.toggle('hidden', state.phase !== 'holding');
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');

  btnDeal.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  handEl.innerHTML = '';
  state.hand.forEach((entry, index) => {
    const slot = document.createElement('div');
    slot.className = 'card-slot';
    if (entry.held) slot.classList.add('held');

    const img = document.createElement('img');
    img.className = 'card';
    img.src = `${SPRITE_DIR}${entry.card.spriteFile}`;
    img.alt = entry.card.toString();
    if (state.phase === 'holding') {
      img.addEventListener('click', () => {
        game.toggleHold(index);
        render();
      });
    }
    slot.appendChild(img);

    const label = document.createElement('div');
    label.className = 'hold-label';
    label.textContent = 'GARDÉE';
    slot.appendChild(label);

    handEl.appendChild(slot);
  });

  paytableRows.forEach((row) => {
    row.classList.toggle('achieved', state.phase === 'result' && row.dataset.rank === state.handRank);
  });

  if (state.phase === 'result') {
    resultMessageEl.textContent = state.payout > 0
      ? `${state.handName} — vous gagnez ${state.payout} !`
      : `${state.handName} — perdu.`;
  } else {
    resultMessageEl.textContent = '';
  }

  statusEl.textContent = state.isGameOver
    ? 'Banqueroute. Cliquez sur "Nouvelle partie" pour recommencer.'
    : '';
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
  if (result.ok) pendingBet = 0;
  render();
});

btnDraw.addEventListener('click', () => {
  game.draw();
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
