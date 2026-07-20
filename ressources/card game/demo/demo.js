import { Deck } from '../src/cards/index.js';

const SPRITE_DIR = '../assets/cards/';
const BACK_SPRITE = `${SPRITE_DIR}back.png`;

const deck = new Deck({ jokers: 2 });

const deckEl = document.getElementById('deck');
const deckCountEl = document.getElementById('deck-count');
const handsEl = document.getElementById('hands');
const statusEl = document.getElementById('status');

function cardEl(card, { faceUp = true } = {}) {
  const img = document.createElement('img');
  img.className = 'card';
  img.src = faceUp ? `${SPRITE_DIR}${card.spriteFile}` : BACK_SPRITE;
  img.alt = faceUp ? card.toString() : 'Dos de carte';
  return img;
}

function renderDeck() {
  deckEl.innerHTML = '';
  for (let i = 0; i < deck.remaining; i += 1) {
    deckEl.appendChild(cardEl(null, { faceUp: false }));
  }
  deckCountEl.textContent = String(deck.remaining);
}

function setStatus(message = '') {
  statusEl.textContent = message;
}

function renderHand(label, cards) {
  const wrap = document.createElement('div');
  wrap.className = 'hand';
  const title = document.createElement('div');
  title.className = 'hand-label';
  title.textContent = label;
  wrap.appendChild(title);
  const row = document.createElement('div');
  row.className = 'card-row';
  for (const card of cards) {
    row.appendChild(cardEl(card));
  }
  wrap.appendChild(row);
  handsEl.appendChild(wrap);
}

document.getElementById('btn-reset').addEventListener('click', () => {
  deck.reset();
  handsEl.innerHTML = '';
  setStatus('Paquet réinitialisé.');
  renderDeck();
});

document.getElementById('btn-shuffle').addEventListener('click', () => {
  deck.shuffle();
  setStatus('Paquet mélangé.');
  renderDeck();
});

document.getElementById('btn-draw').addEventListener('click', () => {
  try {
    const card = deck.draw(1);
    renderHand(`Piochée à ${new Date().toLocaleTimeString()}`, [card]);
    setStatus('');
    renderDeck();
  } catch (err) {
    setStatus(err.message);
  }
});

document.getElementById('btn-deal').addEventListener('click', () => {
  try {
    const hands = deck.deal(4, 5);
    handsEl.innerHTML = '';
    hands.forEach((hand, i) => renderHand(`Main ${i + 1}`, hand));
    setStatus('');
    renderDeck();
  } catch (err) {
    setStatus(err.message);
  }
});

renderDeck();
