import { Scrabble, ROUND_SECONDS, BOARD_SIZE, BONUS_LABELS, buildLetterIndex } from '../../src/games/scrabble/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const WORDS_URL = new URL('../../assets/scrabble/mots.txt', import.meta.url);
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

  for (const rowCells of state.board) {
    for (const cell of rowCells) {
      const key = `${cell.row},${cell.col}`;
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'board-cell';
      if (cell.isCenter) btn.classList.add('is-center');

      const pendingEntry = pendingMap.get(key);
      if (cell.letter) {
        btn.classList.add('has-letter');
        if (justPlayedMap.has(key)) btn.classList.add('is-new');
        btn.disabled = true;
        const letterEl = document.createElement('span');
        letterEl.className = 'cell-letter';
        letterEl.textContent = cell.letter;
        btn.appendChild(letterEl);
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
        if (cell.bonus) {
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
/* Soumission du mot                                                    */
/* ---------------------------------------------------------------- */
function doSubmit(isTimeout) {
  stopTimer();
  selectedRackIndex = null;
  const outcome = game.submitMove(wordSet);
  if (!outcome.ok) return;
  render();

  if (letterIndex) {
    bestMoveComputing = true;
    render();
    setTimeout(() => {
      game.computeBestMove(letterIndex, wordSet);
      bestMoveComputing = false;
      render();
    }, 20);
  }

  const state = game.getState();
  const r = state.result;
  if (isTimeout) {
    dealerVoice.say('timeout');
  } else if (r.bingo && r.valid) {
    dealerVoice.say('bingo');
  } else if (r.tier.mult >= 10) {
    dealerVoice.say('win_jackpot');
  } else if (r.tier.mult >= 3) {
    dealerVoice.say('win_big');
  } else if (r.tier.mult >= 1) {
    dealerVoice.say('win_small');
  } else {
    dealerVoice.say('lose');
  }
  if (r.payout > 0) { flashTable('win'); burstConfetti(); } else { flashTable('lose'); }
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
      const wordsText = r.words.join(', ');
      resultMessageEl.textContent = r.payout > 0
        ? `${wordsText} (${r.score} pts)${bingoTag} — ${r.tier.name}, vous gagnez ${r.payout} !`
        : `${wordsText} (${r.score} pts)${bingoTag} — ${r.tier.name}, mise perdue.`;
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
      bestMoveMessageEl.textContent = `Meilleur coup possible : ${best.word} (${best.score} pts)${bingoTag}`;
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
  bestMoveComputing = false;
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
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
