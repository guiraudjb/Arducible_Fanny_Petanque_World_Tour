import { Solitaire } from '../../src/games/solitaire/engine.js';

const SPRITE_DIR = '../../assets/cards/';
const BACK_SPRITE = `${SPRITE_DIR}back.png`;

const game = new Solitaire({ drawCount: 1 });
let selected = null; // { type: 'waste' } | { type: 'tableau', pile, cardIndex }

const boardEl = document.getElementById('board');
const tableauRowEl = document.getElementById('tableau-row');
const stockEl = boardEl.querySelector('.pile.stock');
const wasteEl = boardEl.querySelector('.pile.waste');
const foundationEls = Array.from(boardEl.querySelectorAll('.pile.foundation'));
const movesEl = document.getElementById('moves');
const statusEl = document.getElementById('status');
const winBannerEl = document.getElementById('win-banner');

function spriteUrl(card) {
  return `${SPRITE_DIR}${card.spriteFile}`;
}

function makeCardImg(card, { faceUp = true, cardIndex = null } = {}) {
  const img = document.createElement('img');
  img.className = 'card';
  img.src = faceUp ? spriteUrl(card) : BACK_SPRITE;
  img.alt = faceUp ? card.toString() : 'Dos de carte';
  if (cardIndex !== null) img.dataset.cardIndex = String(cardIndex);
  return img;
}

function setStatus(message = '') {
  statusEl.textContent = message;
}

function clearSelection() {
  selected = null;
}

function render() {
  const state = game.getState();
  movesEl.textContent = `Coups : ${state.moves}`;

  stockEl.innerHTML = '';
  if (state.stockCount > 0) {
    stockEl.appendChild(makeCardImg(null, { faceUp: false }));
  } else if (state.wasteTop) {
    const hint = document.createElement('div');
    hint.className = 'recycle-hint';
    hint.textContent = '↺';
    stockEl.appendChild(hint);
  }

  wasteEl.innerHTML = '';
  if (state.wasteTop) {
    const img = makeCardImg(state.wasteTop, { faceUp: true });
    if (selected && selected.type === 'waste') img.classList.add('selected');
    wasteEl.appendChild(img);
  }

  for (const foundationEl of foundationEls) {
    const suit = foundationEl.dataset.suit;
    const entry = state.foundations.find((f) => f.suit === suit);
    const existing = foundationEl.querySelector('img.card');
    if (existing) existing.remove();
    if (entry && entry.topCard) {
      foundationEl.appendChild(makeCardImg(entry.topCard, { faceUp: true }));
    }
  }

  tableauRowEl.innerHTML = '';
  state.tableau.forEach((pile, pileIndex) => {
    const pileEl = document.createElement('div');
    pileEl.className = 'tableau-pile';
    pileEl.dataset.zone = 'tableau';
    pileEl.dataset.pileIndex = String(pileIndex);
    const height = pile.length
      ? (pile.length - 1) * 28 + 126
      : 126;
    pileEl.style.height = `${height}px`;

    pile.forEach((entry, cardIndex) => {
      const img = makeCardImg(entry.card, { faceUp: entry.faceUp, cardIndex });
      img.style.top = `${cardIndex * 28}px`;
      if (
        entry.faceUp &&
        selected &&
        selected.type === 'tableau' &&
        selected.pile === pileIndex &&
        cardIndex >= selected.cardIndex
      ) {
        img.classList.add('selected');
      }
      pileEl.appendChild(img);
    });

    tableauRowEl.appendChild(pileEl);
  });

  if (state.isWon) {
    winBannerEl.classList.remove('hidden');
  } else {
    winBannerEl.classList.add('hidden');
  }
}

function onWasteClick() {
  if (selected && selected.type === 'waste') {
    clearSelection();
  } else if (game.waste.length > 0) {
    selected = { type: 'waste' };
    setStatus('');
  }
  render();
}

function onFoundationClick() {
  if (!selected) {
    render();
    return;
  }
  let result;
  if (selected.type === 'waste') {
    result = game.moveWasteToFoundation();
  } else {
    const pile = game.tableau[selected.pile];
    if (selected.cardIndex !== pile.length - 1) {
      result = { ok: false, reason: 'multi-card' };
    } else {
      result = game.moveTableauToFoundation(selected.pile);
    }
  }
  setStatus(result.ok ? '' : 'Coup invalide.');
  if (result.ok) clearSelection();
  render();
}

function onTableauClick(pileIndex, cardIndex) {
  if (!selected) {
    if (cardIndex === null) return;
    const seq = game.getMovableSequence(pileIndex, cardIndex);
    if (seq) {
      selected = { type: 'tableau', pile: pileIndex, cardIndex };
      setStatus('');
    }
    render();
    return;
  }

  if (selected.type === 'tableau' && selected.pile === pileIndex) {
    if (cardIndex === selected.cardIndex) {
      clearSelection();
    } else if (cardIndex !== null) {
      const seq = game.getMovableSequence(pileIndex, cardIndex);
      selected = seq ? { type: 'tableau', pile: pileIndex, cardIndex } : null;
    } else {
      clearSelection();
    }
    render();
    return;
  }

  const result = selected.type === 'waste'
    ? game.moveWasteToTableau(pileIndex)
    : game.moveTableauToTableau(selected.pile, selected.cardIndex, pileIndex);

  setStatus(result.ok ? '' : 'Coup invalide.');
  if (result.ok) clearSelection();
  render();
}

boardEl.addEventListener('click', (event) => {
  const pileEl = event.target.closest('[data-zone]');
  if (!pileEl) return;
  const zone = pileEl.dataset.zone;

  if (zone === 'stock') {
    game.drawFromStock();
    clearSelection();
    setStatus('');
    render();
    return;
  }

  if (zone === 'waste') {
    onWasteClick();
    return;
  }

  if (zone === 'foundation') {
    onFoundationClick();
    return;
  }

  if (zone === 'tableau') {
    const cardEl = event.target.closest('[data-card-index]');
    const pileIndex = Number(pileEl.dataset.pileIndex);
    const cardIndex = cardEl ? Number(cardEl.dataset.cardIndex) : null;
    onTableauClick(pileIndex, cardIndex);
  }
});

boardEl.addEventListener('dblclick', (event) => {
  const cardEl = event.target.closest('[data-card-index]');
  const pileEl = event.target.closest('[data-zone]');
  if (!pileEl) return;

  if (pileEl.dataset.zone === 'waste' && game.waste.length > 0) {
    const result = game.moveWasteToFoundation();
    setStatus(result.ok ? '' : 'Coup invalide.');
    if (result.ok) clearSelection();
    render();
    return;
  }

  if (pileEl.dataset.zone === 'tableau' && cardEl) {
    const pileIndex = Number(pileEl.dataset.pileIndex);
    const cardIndex = Number(cardEl.dataset.cardIndex);
    const pile = game.tableau[pileIndex];
    if (cardIndex === pile.length - 1) {
      const result = game.moveTableauToFoundation(pileIndex);
      setStatus(result.ok ? '' : 'Coup invalide.');
      if (result.ok) clearSelection();
      render();
    }
  }
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  game.newGame();
  clearSelection();
  setStatus('');
  render();
});

render();
