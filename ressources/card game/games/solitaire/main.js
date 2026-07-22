import { Solitaire } from '../../src/games/solitaire/engine.js';

const SPRITE_DIR = '../../assets/cards/';
const BACK_SPRITE = `${SPRITE_DIR}back.png`;

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/** Largeur RÉELLEMENT résolue d'une carte, en px. `--card-w` est un
 * clamp() : getComputedStyle(...).getPropertyValue('--card-w') renvoie le
 * texte brut de l'expression ("clamp(34px, ...)"), pas sa valeur calculée
 * - parseFloat() de ce texte échoue silencieusement (NaN, la chaîne ne
 * commence pas par un chiffre) et ne doit jamais servir de source de
 * vérité pour la mise en page. On lit plutôt la largeur RÉSOLUE d'un
 * élément qui applique `width: var(--card-w)` (le talon), qui donne
 * toujours la vraie valeur en pixels pour la taille d'écran actuelle. */
function resolveCardWidth() {
  return parseFloat(getComputedStyle(stockEl).width) || 60;
}

const game = new Solitaire({ drawCount: 1 });
let selected = null; // { type: 'waste' } | { type: 'tableau', pile, cardIndex }
let pendingFoundationPulse = null;
let wasWon = false;

const tableEl = document.getElementById('table');
const stockEl = tableEl.querySelector('.pile.stock');
const wasteEl = tableEl.querySelector('.pile.waste');
const foundationEls = Array.from(tableEl.querySelectorAll('.pile.foundation'));
const tableauRowEl = document.getElementById('tableau-row');
const movesEl = document.getElementById('moves');
const statusEl = document.getElementById('status');
const winBannerEl = document.getElementById('win-banner');

/* ---------------------------------------------------------------- */
/* Confettis (identiques aux autres jeux de cartes)                  */
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
  const cx = window.innerWidth / 2;
  const cy = window.innerHeight / 2;
  const count = 60;
  for (let i = 0; i < count; i += 1) {
    const angle = Math.random() * Math.PI * 2;
    const speed = 2 + Math.random() * 4;
    particles.push({
      x: cx, y: cy,
      vx: Math.cos(angle) * speed,
      vy: Math.sin(angle) * speed - 2,
      r: 2.5 + Math.random() * 3,
      life: 0,
      maxLife: 70 + Math.random() * 40,
    });
  }
  if (!fxRunning) { fxRunning = true; requestAnimationFrame(tickConfetti); }
}

function tickConfetti() {
  fxCtx.clearRect(0, 0, fxCanvas.width, fxCanvas.height);
  particles.forEach((p) => {
    p.vy += 0.07;
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

/* ---------------------------------------------------------------- */
/* Helpers cartes                                                     */
/* ---------------------------------------------------------------- */

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

function flashInvalid(el) {
  if (!el || prefersReducedMotion()) return;
  el.classList.remove('invalid');
  void el.offsetWidth;
  el.classList.add('invalid');
  el.addEventListener('animationend', () => el.classList.remove('invalid'), { once: true });
}

function pulseFoundation(suit) {
  const el = foundationEls.find((f) => f.dataset.suit === suit);
  if (!el || prefersReducedMotion()) return;
  el.classList.remove('just-scored');
  void el.offsetWidth;
  el.classList.add('just-scored');
  el.addEventListener('animationend', () => el.classList.remove('just-scored'), { once: true });
}

/* ---------------------------------------------------------------- */
/* Rendu                                                              */
/* ---------------------------------------------------------------- */

let prevSnapshot = null; // capturé APRÈS chaque rendu, comparé au suivant
let isFirstRender = true;

function snapshotOf(state) {
  return {
    wasteTopKey: state.wasteTop ? state.wasteTop.toString() : null,
    tableauTops: state.tableau.map((pile) => {
      const top = pile[pile.length - 1];
      return top ? `${top.card.toString()}#${top.faceUp}` : null;
    }),
    tableauLens: state.tableau.map((pile) => pile.length),
  };
}

function computeStackStep(maxLen) {
  // clientHeight INCLUT le padding vertical du conteneur (haut + bas) : ce
  // n'est pas de l'espace disponible pour empiler des cartes, il faut le
  // retrancher. Sans ça, la pile la plus longue est systématiquement
  // calculée ~1 padding trop haute - resté invisible tant que le tapis
  // avait de la marge, mais fait déborder la page en paysage mobile très
  // bas (~390px de hauteur), où cette marge n'existe plus.
  const rowStyle = getComputedStyle(tableauRowEl);
  const verticalPadding = parseFloat(rowStyle.paddingTop) + parseFloat(rowStyle.paddingBottom);
  const containerHeight = Math.max(0, (tableauRowEl.clientHeight || 0) - verticalPadding);
  const cardW = resolveCardWidth();
  const cardH = cardW * (7 / 5);
  // Plafond confortable (cartes pas trop écartées) et plancher de lisibilité
  // (rang/couleur toujours visible même sur une pile très longue).
  const maxStep = cardH * 0.85;
  const minStep = 10;
  if (maxLen <= 1 || containerHeight <= 0) return maxStep;
  const available = Math.max(0, containerHeight - cardH);
  const fitStep = available / (maxLen - 1);
  // Utilise tout l'espace vertical disponible (jusqu'au plafond) plutôt que
  // de rester compact quand une pile est courte — évite un tapis à moitié vide.
  return Math.max(minStep, Math.min(maxStep, fitStep));
}

function render() {
  const state = game.getState();
  const snapshot = snapshotOf(state);

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

  const wasteChanged = !isFirstRender && snapshot.wasteTopKey !== null && snapshot.wasteTopKey !== prevSnapshot.wasteTopKey;
  wasteEl.innerHTML = '';
  if (state.wasteTop) {
    const img = makeCardImg(state.wasteTop, { faceUp: true });
    if (selected && selected.type === 'waste') img.classList.add('selected');
    if (wasteChanged && !prefersReducedMotion()) img.classList.add('is-flipping');
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

  const maxLen = Math.max(1, ...state.tableau.map((p) => p.length));
  const step = computeStackStep(maxLen);

  tableauRowEl.innerHTML = '';
  state.tableau.forEach((pile, pileIndex) => {
    const pileEl = document.createElement('div');
    pileEl.className = 'tableau-pile';
    pileEl.dataset.zone = 'tableau';
    pileEl.dataset.pileIndex = String(pileIndex);

    const cardW = resolveCardWidth();
    const cardH = cardW * (7 / 5);
    const height = pile.length ? (pile.length - 1) * step + cardH : cardW;
    pileEl.style.height = `${height}px`;

    const prevTopKey = !isFirstRender ? prevSnapshot.tableauTops[pileIndex] : null;
    const prevLen = !isFirstRender ? prevSnapshot.tableauLens[pileIndex] : 0;
    const newTop = pile[pile.length - 1];
    const newTopKey = newTop ? `${newTop.card.toString()}#${newTop.faceUp}` : null;
    const revealed = !isFirstRender
      && newTop && newTop.faceUp
      && pile.length < prevLen
      && newTopKey !== prevTopKey;

    pile.forEach((entry, cardIndex) => {
      const img = makeCardImg(entry.card, { faceUp: entry.faceUp, cardIndex });
      img.style.top = `${cardIndex * step}px`;
      if (
        entry.faceUp &&
        selected &&
        selected.type === 'tableau' &&
        selected.pile === pileIndex &&
        cardIndex >= selected.cardIndex
      ) {
        img.classList.add('selected');
      }
      if (isFirstRender && !prefersReducedMotion()) {
        img.classList.add('is-dealing');
        img.style.setProperty('--deal-rot', `${(Math.random() * 10 - 5).toFixed(1)}deg`);
        img.style.animationDelay = `${pileIndex * 55}ms`;
      } else if (revealed && cardIndex === pile.length - 1 && !prefersReducedMotion()) {
        img.classList.add('is-flipping');
      }
      pileEl.appendChild(img);
    });

    tableauRowEl.appendChild(pileEl);
  });

  if (pendingFoundationPulse) {
    pulseFoundation(pendingFoundationPulse);
    pendingFoundationPulse = null;
  }

  if (state.isWon) {
    winBannerEl.classList.remove('hidden');
    if (!wasWon) burstConfetti();
  } else {
    winBannerEl.classList.add('hidden');
  }
  wasWon = state.isWon;

  prevSnapshot = snapshot;
  isFirstRender = false;
}

/* ---------------------------------------------------------------- */
/* Interactions                                                       */
/* ---------------------------------------------------------------- */

function onWasteClick() {
  if (selected && selected.type === 'waste') {
    clearSelection();
  } else if (game.waste.length > 0) {
    selected = { type: 'waste' };
    setStatus('');
  }
  render();
}

function onFoundationClick(foundationEl) {
  if (!selected) { render(); return; }
  let result;
  let suit = null;
  if (selected.type === 'waste') {
    suit = game.waste.length ? game.waste[game.waste.length - 1].suit : null;
    result = game.moveWasteToFoundation();
  } else {
    const pile = game.tableau[selected.pile];
    if (selected.cardIndex !== pile.length - 1) {
      result = { ok: false, reason: 'multi-card' };
    } else {
      suit = pile.length ? pile[pile.length - 1].card.suit : null;
      result = game.moveTableauToFoundation(selected.pile);
    }
  }
  if (!result.ok) {
    setStatus('Coup invalide.');
    flashInvalid(foundationEl);
  } else {
    setStatus('');
    clearSelection();
    if (suit) pulseFoundationAfterRender(suit);
  }
  render();
}

function pulseFoundationAfterRender(suit) {
  pendingFoundationPulse = suit;
}

function onTableauClick(pileEl, pileIndex, cardIndex) {
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

  if (!result.ok) {
    setStatus('Coup invalide.');
    flashInvalid(pileEl);
  } else {
    setStatus('');
    clearSelection();
  }
  render();
}

tableEl.addEventListener('click', (event) => {
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
    onFoundationClick(pileEl);
    return;
  }

  if (zone === 'tableau') {
    const cardEl = event.target.closest('[data-card-index]');
    const pileIndex = Number(pileEl.dataset.pileIndex);
    const cardIndex = cardEl ? Number(cardEl.dataset.cardIndex) : null;
    onTableauClick(pileEl, pileIndex, cardIndex);
  }
});

tableEl.addEventListener('dblclick', (event) => {
  const cardEl = event.target.closest('[data-card-index]');
  const pileEl = event.target.closest('[data-zone]');
  if (!pileEl) return;

  if (pileEl.dataset.zone === 'waste' && game.waste.length > 0) {
    const suit = game.waste[game.waste.length - 1].suit;
    const result = game.moveWasteToFoundation();
    if (!result.ok) { setStatus('Coup invalide.'); flashInvalid(pileEl); }
    else { setStatus(''); clearSelection(); pulseFoundationAfterRender(suit); }
    render();
    return;
  }

  if (pileEl.dataset.zone === 'tableau' && cardEl) {
    const pileIndex = Number(pileEl.dataset.pileIndex);
    const cardIndex = Number(cardEl.dataset.cardIndex);
    const pile = game.tableau[pileIndex];
    if (cardIndex === pile.length - 1) {
      const suit = pile[pile.length - 1].card.suit;
      const result = game.moveTableauToFoundation(pileIndex);
      if (!result.ok) { setStatus('Coup invalide.'); flashInvalid(pileEl); }
      else { setStatus(''); clearSelection(); pulseFoundationAfterRender(suit); }
      render();
    }
  }
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  game.newGame();
  clearSelection();
  setStatus('');
  isFirstRender = true;
  prevSnapshot = null;
  render();
});

document.getElementById('btn-win-again').addEventListener('click', () => {
  game.newGame();
  clearSelection();
  setStatus('');
  isFirstRender = true;
  prevSnapshot = null;
  render();
});

window.addEventListener('resize', () => render());

render();

// Filet de sécurité : le tout premier calcul de l'espacement des piles
// (computeStackStep) peut légèrement sous-estimer la hauteur réellement
// disponible avant que la mise en page ne soit stabilisée (constaté en
// paysage mobile très bas, où la marge est de quelques pixels) - un
// second rendu juste après capture la bonne valeur. Sans effet visible
// sur le jeu : l'état n'a pas changé entre les deux appels.
requestAnimationFrame(() => requestAnimationFrame(render));
