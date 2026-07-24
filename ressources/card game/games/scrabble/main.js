import { Scrabble, ROUND_SECONDS, BOARD_SIZE, BONUS_LABELS, buildLetterIndex } from '../../src/games/scrabble/engine.js';
import { createDealerVoice, isMuted } from '../../src/dealer/dealerVoice.js';

const WORDS_URL = new URL('../../assets/scrabble/mots.txt', import.meta.url);
const DEFINITIONS_URL = new URL('../../assets/scrabble/definitions.csv', import.meta.url);
const ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('');

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const game = new Scrabble({ startingBankroll: 500 });
let pendingBet = 0;
let lastBankrollShown = null;
let bankruptcyAnnounced = false;
let wordsArray = [];
let wordSet = new Set();
let letterIndex = null;
let wordsLoaded = false;
let definitionsMap = new Map();
let selectedRackIndex = null;
let pendingBlankRackIndex = null;
let secondsLeft = ROUND_SECONDS;
let timerInterval = null;
let bestMoveComputing = false;

const dealerVoice = createDealerVoice({
  game: 'scrabble',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const timerEl = document.getElementById('timer');
const resultMessageEl = document.getElementById('result-message');
const bestMoveMessageEl = document.getElementById('best-move-message');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const playingAreaEl = document.getElementById('playing-area');
const resultAreaEl = document.getElementById('result-area');
const btnDeal = document.getElementById('btn-deal');
const btnSubmit = document.getElementById('btn-submit');
const hintEl = document.getElementById('hint');
const boardEl = document.getElementById('board');
const rackRowEl = document.getElementById('rack-row');
const paytableRows = document.querySelectorAll('.pay-row[data-tier]');
const blankPickerEl = document.getElementById('blank-picker');
const blankPickerGridEl = document.getElementById('blank-picker-grid');
const definitionPopupEl = document.getElementById('definition-popup');
const definitionWordEl = document.getElementById('definition-word');
const definitionListEl = document.getElementById('definition-list');
const webLookupPopupEl = document.getElementById('web-lookup-popup');
const webLookupTitleEl = document.getElementById('web-lookup-title');
const webLookupFrameEl = document.getElementById('web-lookup-frame');

/* ---------------------------------------------------------------- */
/* Confettis (mêmes principes que les autres jeux du casino)          */
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
/* Dictionnaire                                                        */
/* ---------------------------------------------------------------- */
/** Parseur CSV minimal mais correct sur les guillemets (les définitions
 * peuvent contenir des virgules) - suffisant pour un fichier généré par
 * nous-mêmes (voir tools/generate_scrabble_definitions.py), pas pensé pour
 * du CSV arbitraire externe. */
function parseCsv(text) {
  const rows = [];
  let row = [];
  let field = '';
  let inQuotes = false;
  for (let i = 0; i < text.length; i += 1) {
    const c = text[i];
    if (inQuotes) {
      if (c === '"' && text[i + 1] === '"') { field += '"'; i += 1; }
      else if (c === '"') { inQuotes = false; }
      else { field += c; }
    } else if (c === '"') {
      inQuotes = true;
    } else if (c === ',') {
      row.push(field); field = '';
    } else if (c === '\n') {
      row.push(field); field = '';
      rows.push(row); row = [];
    } else if (c !== '\r') {
      field += c;
    }
  }
  if (field.length > 0 || row.length > 0) { row.push(field); rows.push(row); }
  return rows;
}

fetch(DEFINITIONS_URL)
  .then((r) => r.text())
  .then((text) => {
    const rows = parseCsv(text);
    for (const [word, definition] of rows.slice(1)) {
      if (word) definitionsMap.set(word, definition);
    }
  })
  .catch(() => {}); // pas bloquant : le jeu marche sans définitions, juste sans l'infobulle

fetch(WORDS_URL)
  .then((r) => r.text())
  .then((text) => {
    wordsArray = text.split('\n').filter(Boolean);
    wordSet = new Set(wordsArray);
    letterIndex = buildLetterIndex(wordsArray);
    wordsLoaded = true;
    render();
  });

/* ---------------------------------------------------------------- */
/* Définitions : reconstruction des mots depuis la grille, popup        */
/* ---------------------------------------------------------------- */
/** Reconstruit le(s) mot(s) (2 lettres ou plus) passant par la case
 * (row, col) sur la grille actuelle : le mot horizontal et/ou vertical qui
 * la traverse - une case d'intersection peut appartenir aux deux à la
 * fois. Fonctionne sur n'importe quelle case remplie, posée ce tour-ci ou
 * lors d'une manche précédente (le plateau ne se vide jamais entre les
 * manches) - pas besoin de suivre un historique séparé des mots posés. */
function wordsThroughCell(board, row, col) {
  const letterAt = (r, c) => (board[r] && board[r][c] ? board[r][c].letter : null);
  if (!letterAt(row, col)) return [];

  const words = [];

  let left = col;
  while (letterAt(row, left - 1)) left -= 1;
  let right = col;
  while (letterAt(row, right + 1)) right += 1;
  if (right > left) {
    let text = '';
    for (let c = left; c <= right; c += 1) text += letterAt(row, c);
    words.push(text);
  }

  let top = row;
  while (letterAt(top - 1, col)) top -= 1;
  let bottom = row;
  while (letterAt(bottom + 1, col)) bottom += 1;
  if (bottom > top) {
    let text = '';
    for (let r = top; r <= bottom; r += 1) text += letterAt(r, col);
    words.push(text);
  }

  return words;
}

function openDefinitionPopup(words) {
  const unique = [...new Set(words)];
  if (unique.length === 0) return;
  definitionWordEl.textContent = unique.join(' / ');
  definitionListEl.innerHTML = '';
  for (const word of unique) {
    const p = document.createElement('p');
    const definition = definitionsMap.get(word);
    if (definition) {
      p.className = 'definition-entry';
      p.textContent = `${word} — ${definition}`;
    } else {
      p.className = 'definition-entry is-unavailable';
      p.textContent = `${word} — définition non disponible.`;
    }
    p.appendChild(document.createElement('br'));
    const lookupBtn = document.createElement('button');
    lookupBtn.type = 'button';
    lookupBtn.className = 'lookup-link';
    lookupBtn.textContent = '🔍 Recherche approfondie';
    lookupBtn.addEventListener('click', () => openWebLookup(word));
    p.appendChild(lookupBtn);
    definitionListEl.appendChild(p);
  }
  definitionPopupEl.classList.remove('hidden');
}
function closeDefinitionPopup() {
  definitionPopupEl.classList.add('hidden');
}
document.getElementById('btn-definition-close').addEventListener('click', closeDefinitionPopup);
definitionPopupEl.addEventListener('click', (event) => {
  if (event.target === definitionPopupEl) closeDefinitionPopup(); // clic sur le fond, pas le panneau
});

/* ---------------------------------------------------------------- */
/* Recherche approfondie : Wiktionnaire dans une frame fermable        */
/* (Google refuse d'être affiché dans une frame externe - vérifié -    */
/* Wiktionnaire, déjà notre source pour definitions.csv, ne bloque pas */
/* l'intégration). */
/* ---------------------------------------------------------------- */
function openWebLookup(word) {
  webLookupTitleEl.textContent = `Recherche approfondie : ${word}`;
  webLookupFrameEl.src = `https://fr.wiktionary.org/wiki/${encodeURIComponent(word.toLowerCase())}`;
  webLookupPopupEl.classList.remove('hidden');
}
function closeWebLookup() {
  webLookupPopupEl.classList.add('hidden');
  webLookupFrameEl.src = 'about:blank'; // stoppe le chargement/l'éventuel audio de la page intégrée
}
document.getElementById('btn-web-lookup-close').addEventListener('click', closeWebLookup);
webLookupPopupEl.addEventListener('click', (event) => {
  if (event.target === webLookupPopupEl) closeWebLookup(); // clic sur le fond, pas le panneau
});

/** Construit un petit bouton texte pour un mot (dans le message de
 * résultat ou le meilleur coup) qui ouvre sa définition au clic - le mot
 * garde l'orthographe déjà connue du moteur (majuscules, sans accent),
 * donc la clé de recherche dans definitionsMap est directe. */
function wordLink(word) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'word-link';
  btn.textContent = word;
  btn.addEventListener('click', () => openDefinitionPopup([word]));
  return btn;
}

/* ---------------------------------------------------------------- */
/* Minuteur                                                            */
/* ---------------------------------------------------------------- */
function updateTimerDisplay() {
  const state = game.getState();
  if (state.phase !== 'playing') { timerEl.textContent = ''; return; }
  timerEl.textContent = `⏱ ${secondsLeft}s`;
  timerEl.classList.toggle('is-urgent', secondsLeft <= 15);
}

function startTimer() {
  secondsLeft = ROUND_SECONDS;
  updateTimerDisplay();
  clearInterval(timerInterval);
  timerInterval = setInterval(() => {
    secondsLeft -= 1;
    if (secondsLeft <= 0) {
      secondsLeft = 0;
      clearInterval(timerInterval);
      timerInterval = null;
      updateTimerDisplay();
      doSubmit(true);
    } else {
      updateTimerDisplay();
    }
  }, 1000);
}

function stopTimer() {
  clearInterval(timerInterval);
  timerInterval = null;
}

/* ---------------------------------------------------------------- */
/* Jeton du joker (choix de la lettre)                                 */
/* ---------------------------------------------------------------- */
ALPHABET.forEach((letter) => {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'blank-picker-key';
  btn.textContent = letter;
  btn.addEventListener('click', () => {
    const rackIndex = pendingBlankRackIndex;
    closeBlankPicker();
    if (rackIndex === null) return;
    game.assignBlank(rackIndex, letter);
    selectedRackIndex = rackIndex;
    render();
  });
  blankPickerGridEl.appendChild(btn);
});

function openBlankPicker(rackIndex) {
  pendingBlankRackIndex = rackIndex;
  blankPickerEl.classList.remove('hidden');
}
function closeBlankPicker() {
  blankPickerEl.classList.add('hidden');
  pendingBlankRackIndex = null;
}
document.getElementById('btn-blank-cancel').addEventListener('click', closeBlankPicker);

/* ---------------------------------------------------------------- */
/* Glisser-déposer d'une lettre du chevalet vers la grille              */
/* (Pointer Events : un seul code pour souris ET écran tactile)         */
/* ---------------------------------------------------------------- */
const DRAG_START_THRESHOLD = 6; // px de mouvement avant de basculer du tap au glisser

function tileGhostFor(entry) {
  const ghost = document.createElement('div');
  ghost.className = 'tile drag-ghost';
  if (entry.isBlank) ghost.classList.add('is-blank');
  const letterEl = document.createElement('span');
  letterEl.className = 'tile-letter';
  letterEl.textContent = entry.display || (entry.isBlank ? '★' : '');
  ghost.appendChild(letterEl);
  const valueEl = document.createElement('span');
  valueEl.className = 'tile-value';
  valueEl.textContent = String(entry.value);
  ghost.appendChild(valueEl);
  document.body.appendChild(ghost);
  return ghost;
}

function boardCellFromPoint(clientX, clientY) {
  const el = document.elementFromPoint(clientX, clientY);
  const cell = el && el.closest ? el.closest('.board-cell') : null;
  return cell && boardEl.contains(cell) ? cell : null;
}

function clearDropHighlight() {
  const prev = boardEl.querySelector('.is-drop-target');
  if (prev) prev.classList.remove('is-drop-target');
}

/** Démarre un glisser potentiel depuis une lettre du chevalet. Un simple tap
 * (pas de mouvement au-delà du seuil) laisse le clic habituel gérer la
 * sélection - seul un vrai déplacement du pointeur bascule en mode glisser,
 * avec un jeton fantôme qui suit le doigt/la souris jusqu'à la case visée. */
function attachTileDrag(btn, index, entry) {
  btn.addEventListener('pointerdown', (event) => {
    if (event.button > 0 || btn.disabled) return;
    // Un joker pas encore assigné s'ouvre au tap (choix de la lettre) -
    // rien à glisser tant qu'il n'a pas de lettre affichée.
    if (entry.isBlank && !entry.display) return;

    const startX = event.clientX;
    const startY = event.clientY;
    const pointerId = event.pointerId;
    let dragging = false;
    let ghost = null;

    const onMove = (moveEvent) => {
      if (moveEvent.pointerId !== pointerId) return;
      const dx = moveEvent.clientX - startX;
      const dy = moveEvent.clientY - startY;
      if (!dragging) {
        if (Math.hypot(dx, dy) < DRAG_START_THRESHOLD) return;
        dragging = true;
        btn.classList.add('is-dragging-source');
        ghost = tileGhostFor(entry);
      }
      moveEvent.preventDefault();
      const rect = ghost.getBoundingClientRect();
      ghost.style.left = `${moveEvent.clientX - rect.width / 2}px`;
      ghost.style.top = `${moveEvent.clientY - rect.height / 2}px`;
      clearDropHighlight();
      const cell = boardCellFromPoint(moveEvent.clientX, moveEvent.clientY);
      if (cell && !cell.classList.contains('has-letter')) cell.classList.add('is-drop-target');
    };

    const onUp = (upEvent) => {
      if (upEvent.pointerId !== pointerId) return;
      window.removeEventListener('pointermove', onMove);
      window.removeEventListener('pointerup', onUp);
      window.removeEventListener('pointercancel', onUp);
      btn.classList.remove('is-dragging-source');
      clearDropHighlight();
      if (ghost) ghost.remove();
      if (!dragging) return; // simple tap : le gestionnaire de clic s'en charge

      const cell = boardCellFromPoint(upEvent.clientX, upEvent.clientY);
      if (cell && !cell.classList.contains('has-letter') && game.getState().phase === 'playing') {
        const row = Number(cell.dataset.row);
        const col = Number(cell.dataset.col);
        const res = game.placeTileFromRack(index, row, col);
        if (res.ok) selectedRackIndex = null;
        render();
      }
    };

    window.addEventListener('pointermove', onMove);
    window.addEventListener('pointerup', onUp);
    window.addEventListener('pointercancel', onUp);
  });
}

/* ---------------------------------------------------------------- */
/* Chevalet                                                             */
/* ---------------------------------------------------------------- */
function renderRack(rack, canPlay) {
  rackRowEl.innerHTML = '';
  rack.forEach((entry, index) => {
    const btn = document.createElement('button');
    btn.type = 'button';
    btn.className = 'tile';
    if (entry.isBlank) btn.classList.add('is-blank');
    if (canPlay && index === selectedRackIndex) btn.classList.add('is-selected');
    btn.disabled = !canPlay;

    const letterEl = document.createElement('span');
    letterEl.className = 'tile-letter';
    letterEl.textContent = entry.display || (entry.isBlank ? '★' : '');
    btn.appendChild(letterEl);

    const valueEl = document.createElement('span');
    valueEl.className = 'tile-value';
    valueEl.textContent = String(entry.value);
    btn.appendChild(valueEl);

    btn.addEventListener('click', () => {
      if (entry.isBlank) { openBlankPicker(index); return; }
      selectedRackIndex = selectedRackIndex === index ? null : index;
      render();
    });
    if (canPlay) attachTileDrag(btn, index, entry);
    rackRowEl.appendChild(btn);
  });
}

/* ---------------------------------------------------------------- */
/* Plateau                                                              */
/* ---------------------------------------------------------------- */
function renderBoard(state) {
  boardEl.innerHTML = '';
  const canPlay = state.phase === 'playing';
  const pendingMap = new Map(state.pending.map((p) => [`${p.row},${p.col}`, p]));
  const justPlayedMap = state.phase === 'result' && state.result && state.result.valid
    ? new Map(state.result.placedCells.map((p) => [`${p.row},${p.col}`, true]))
    : new Map();
  const bestMove = state.phase === 'result' && state.result ? state.result.bestMove : null;
  const ghostMap = bestMove
    ? new Map(bestMove.placements.map((p) => [`${p.row},${p.col}`, p]))
    : new Map();

  for (const rowCells of state.board) {
    for (const cell of rowCells) {
      const key = `${cell.row},${cell.col}`;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'board-cell';
      btn.dataset.row = String(cell.row);
      btn.dataset.col = String(cell.col);
      if (cell.isCenter) btn.classList.add('is-center');

      const pendingEntry = pendingMap.get(key);
      if (cell.letter) {
        btn.classList.add('has-letter');
        if (justPlayedMap.has(key)) btn.classList.add('is-new');
        // Reste cliquable (contrairement à avant) : affiche la ou les
        // définitions du/des mot(s) passant par cette case, reconstruits à
        // la volée depuis la grille (voir wordsThroughCell) - fonctionne
        // aussi bien pour les lettres posées ce tour-ci que lors d'une
        // manche précédente, sans suivi séparé de l'historique des mots.
        btn.disabled = false;
        const letterEl = document.createElement('span');
        letterEl.className = 'cell-letter is-clickable-word';
        letterEl.textContent = cell.letter;
        btn.appendChild(letterEl);
        btn.addEventListener('click', () => {
          openDefinitionPopup(wordsThroughCell(state.board, cell.row, cell.col));
        });
      } else if (pendingEntry) {
        btn.classList.add('has-letter', 'is-pending');
        btn.disabled = !canPlay;
        const letterEl = document.createElement('span');
        letterEl.className = 'cell-letter';
        letterEl.textContent = pendingEntry.display;
        btn.appendChild(letterEl);
        const valueEl = document.createElement('span');
        valueEl.className = 'cell-value';
        valueEl.textContent = String(pendingEntry.value);
        btn.appendChild(valueEl);
        if (canPlay) {
          btn.addEventListener('click', () => {
            game.returnPendingAt(cell.row, cell.col);
            render();
          });
        }
      } else {
        const ghostEntry = ghostMap.get(key);
        if (ghostEntry) {
          btn.classList.add('is-best-ghost');
          const letterEl = document.createElement('span');
          letterEl.className = 'cell-letter';
          letterEl.textContent = ghostEntry.letter;
          btn.appendChild(letterEl);
        } else if (cell.bonus) {
          btn.classList.add(`bonus-${cell.bonus}`);
          const bonusEl = document.createElement('span');
          bonusEl.className = 'cell-bonus';
          bonusEl.textContent = BONUS_LABELS[cell.bonus];
          btn.appendChild(bonusEl);
        } else if (cell.isCenter) {
          const starEl = document.createElement('span');
          starEl.className = 'cell-star';
          starEl.textContent = '★';
          btn.appendChild(starEl);
        }
        const canPlaceHere = canPlay && selectedRackIndex !== null;
        btn.disabled = !canPlaceHere;
        if (canPlaceHere) {
          btn.addEventListener('click', () => {
            const res = game.placeTileFromRack(selectedRackIndex, cell.row, cell.col);
            if (res.ok) selectedRackIndex = null;
            render();
          });
        }
      }
      boardEl.appendChild(btn);
    }
  }
}

/* ---------------------------------------------------------------- */
/* Voix de synthèse du navigateur pour le meilleur coup possible       */
/* ---------------------------------------------------------------- */
function speakBestMove(best) {
  if (!best || isMuted() || !('speechSynthesis' in window)) return;
  const text = best.bingo
    ? `Meilleur coup possible : ${best.word}, pour ${best.score} points, scrabble !`
    : `Meilleur coup possible : ${best.word}, pour ${best.score} points.`;
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = 'fr-FR';
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
}

/* ---------------------------------------------------------------- */
/* Soumission du mot                                                    */
/* ---------------------------------------------------------------- */
function doSubmit(isTimeout) {
  stopTimer();
  selectedRackIndex = null;
  const outcome = game.submitMove(wordSet);
  if (!outcome.ok) return;
  render();

  const state = game.getState();
  const r = state.result;
  // La voix de Fanny (mp3) et la synthèse vocale du meilleur coup partagent
  // le même haut-parleur : on attend que sa réplique soit terminée avant de
  // lancer la lecture du meilleur coup, plutôt que de jouer les deux en
  // même temps (voir dealerVoice.say, qui résout une fois le clip fini).
  let voiceDone;
  if (isTimeout) {
    voiceDone = dealerVoice.say('timeout');
  } else if (r.bingo && r.valid) {
    voiceDone = dealerVoice.say('bingo');
  } else if (r.tier.mult >= 10) {
    voiceDone = dealerVoice.say('win_jackpot');
  } else if (r.tier.mult >= 3) {
    voiceDone = dealerVoice.say('win_big');
  } else if (r.tier.mult >= 1) {
    voiceDone = dealerVoice.say('win_small');
  } else {
    voiceDone = dealerVoice.say('lose');
  }
  if (r.payout > 0) { flashTable('win'); burstConfetti(); } else { flashTable('lose'); }

  if (letterIndex) {
    bestMoveComputing = true;
    render();
    setTimeout(() => {
      game.computeBestMove(letterIndex, wordSet);
      bestMoveComputing = false;
      render();
      Promise.resolve(voiceDone).then(() => speakBestMove(game.result.bestMove));
    }, 20);
  }
}

/* ---------------------------------------------------------------- */
/* Rendu                                                               */
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

  btnDeal.disabled = !wordsLoaded || pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;
  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });

  const canPlay = state.phase === 'playing';
  renderBoard(state);
  renderRack(state.rack, canPlay);
  btnSubmit.disabled = !canPlay || state.pending.length === 0;
  if (canPlay) {
    hintEl.textContent = selectedRackIndex !== null
      ? 'Touchez une case vide de la grille pour poser cette lettre.'
      : 'Touchez une lettre du chevalet, puis une case pour la poser.';
  }

  updateTimerDisplay();

  paytableRows.forEach((row) => {
    row.classList.toggle(
      'achieved',
      state.phase === 'result' && !!state.result && state.result.valid && row.dataset.tier === state.result.tier.key,
    );
  });

  if (state.phase === 'result' && state.result) {
    const r = state.result;
    if (!r.valid) {
      const reasons = {
        'not-collinear': 'les lettres doivent être alignées.',
        gap: 'pas de trou dans le mot.',
        'not-connected': 'le mot doit toucher une lettre déjà posée.',
        occupied: 'case déjà occupée.',
        empty: 'aucune lettre posée.',
      };
      resultMessageEl.textContent = reasons[r.invalidWord]
        ? `Coup invalide : ${reasons[r.invalidWord]} — mise perdue.`
        : `« ${r.invalidWord} » n'est pas dans le dictionnaire — mise perdue.`;
      resultMessageEl.classList.add('is-lose');
    } else {
      const bingoTag = r.bingo ? ' — SCRABBLE !' : '';
      // Chaque mot formé ce tour-ci est un bouton cliquable (voir wordLink)
      // qui ouvre sa définition, entrelacé avec le texte du message.
      resultMessageEl.innerHTML = '';
      r.words.forEach((word, i) => {
        if (i > 0) resultMessageEl.appendChild(document.createTextNode(', '));
        resultMessageEl.appendChild(wordLink(word));
      });
      const suffix = r.payout > 0
        ? ` (${r.score} pts)${bingoTag} — ${r.tier.name}, vous gagnez ${r.payout} !`
        : ` (${r.score} pts)${bingoTag} — ${r.tier.name}, mise perdue.`;
      resultMessageEl.appendChild(document.createTextNode(suffix));
      resultMessageEl.classList.toggle('is-lose', r.payout === 0);
    }
    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    const best = r.bestMove;
    if (bestMoveComputing) {
      bestMoveMessageEl.textContent = 'Calcul du meilleur coup possible…';
    } else if (!best) {
      bestMoveMessageEl.textContent = '';
    } else if (r.valid && r.score >= best.score) {
      bestMoveMessageEl.textContent = 'Vous avez trouvé le meilleur mot possible, bravo !';
    } else {
      const bingoTag = best.bingo ? ' — SCRABBLE !' : '';
      bestMoveMessageEl.innerHTML = '';
      bestMoveMessageEl.appendChild(document.createTextNode('Meilleur coup possible : '));
      bestMoveMessageEl.appendChild(wordLink(best.word));
      bestMoveMessageEl.appendChild(document.createTextNode(` (${best.score} pts)${bingoTag}`));
    }
  } else {
    resultMessageEl.textContent = '';
    resultMessageEl.classList.remove('is-lose');
    bestMoveMessageEl.textContent = '';
  }

  statusEl.textContent = !wordsLoaded
    ? 'Chargement du dictionnaire…'
    : (state.isGameOver ? 'Banqueroute. Cliquez sur « Nouvelle partie » pour recommencer.' : '');
  if (state.isGameOver && !bankruptcyAnnounced) {
    bankruptcyAnnounced = true;
    dealerVoice.say('bankruptcy');
  }
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
  const result = game.startRound(pendingBet, wordsArray);
  if (result.ok) {
    pendingBet = 0;
    selectedRackIndex = null;
    dealerVoice.say('dealing');
    startTimer();
  }
  render();
});

document.getElementById('btn-shuffle').addEventListener('click', () => {
  game.shuffleRack();
  render();
});

document.getElementById('btn-clear-word').addEventListener('click', () => {
  selectedRackIndex = null;
  game.clearPending();
  render();
});

btnSubmit.addEventListener('click', () => doSubmit(false));

document.getElementById('btn-next-round').addEventListener('click', () => {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  closeDefinitionPopup();
  closeWebLookup();
  bestMoveComputing = false;
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  if ('speechSynthesis' in window) window.speechSynthesis.cancel();
  closeDefinitionPopup();
  closeWebLookup();
  stopTimer();
  selectedRackIndex = null;
  bestMoveComputing = false;
  game.newSession();
  pendingBet = 0;
  lastBankrollShown = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');

// PWA : portée volontairement limitée à ce dossier (sw.js n'est enregistré
// que depuis ici, donc son scope par défaut s'arrête à games/scrabble/ -
// les autres jeux du casino ne sont pas concernés).
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('./sw.js').catch(() => {
      // Hors-ligne indisponible cette fois (hébergement sans HTTPS en local,
      // navigateur incompatible...) : le jeu reste jouable en ligne.
    });
  });
}
