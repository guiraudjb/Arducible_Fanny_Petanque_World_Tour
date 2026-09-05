import { LettresGame, DRAW_COUNT, ROUND_SECONDS } from '../../src/games/lettres/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

// Dictionnaire mutualisé avec le Scrabble du Casino Fanny (même liste de
// référence, cf. src/games/lettres/engine.js).
const WORDS_URL = new URL('../../assets/scrabble/mots.txt', import.meta.url);

const game = new LettresGame({ startingBankroll: 500 });
let pendingBet = 0;
let dictionaryReady = false;
let lastBankrollShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;
let timerId = null;
let timeLeft = ROUND_SECONDS;
let usedTileIds = new Set();

const dealerVoice = createDealerVoice({
  game: 'lettres',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const timerEl = document.getElementById('timer');
const dictStatusEl = document.getElementById('dict-status');
const bettingPanelEl = document.getElementById('betting-panel');
const drawPanelEl = document.getElementById('draw-panel');
const playPanelEl = document.getElementById('play-panel');
const resultPanelEl = document.getElementById('result-panel');
const drawProgressEl = document.getElementById('draw-progress');
const drawnRowEl = document.getElementById('drawn-row');
const btnDrawVowel = document.getElementById('btn-draw-vowel');
const btnDrawConsonant = document.getElementById('btn-draw-consonant');
const drawHintEl = document.getElementById('draw-hint');
const lettersRowEl = document.getElementById('letters-row');
const wordInputEl = document.getElementById('word-input');
const btnValidate = document.getElementById('btn-validate');
const resultMessageEl = document.getElementById('result-message');
const resultDetailEl = document.getElementById('result-detail');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const resultAreaEl = document.getElementById('result-area');
const btnStart = document.getElementById('btn-start');

/* ---------------------------------------------------------------- */
/* Chargement du dictionnaire (mots.txt, partagé avec le Scrabble)      */
/* ---------------------------------------------------------------- */
fetch(WORDS_URL)
  .then((r) => r.text())
  .then((text) => {
    const wordsArray = text.split('\n').filter(Boolean);
    const wordSet = new Set(wordsArray);
    game.setDictionary(wordsArray, wordSet);
    dictionaryReady = true;
    dictStatusEl.textContent = `Dictionnaire chargé (${wordsArray.length.toLocaleString('fr-FR')} mots, même liste que le Scrabble du casino).`;
    render();
  })
  .catch(() => {
    dictStatusEl.textContent = 'Dictionnaire indisponible — rechargez la page.';
  });

/* ---------------------------------------------------------------- */
/* Confettis (identique aux autres jeux du casino)                      */
/* ---------------------------------------------------------------- */
const fxCanvas = document.createElement('canvas');
fxCanvas.id = 'fx-canvas';
tableEl.appendChild(fxCanvas);
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
/* Chrono                                                              */
/* ---------------------------------------------------------------- */
function stopTimer() {
  if (timerId) { clearInterval(timerId); timerId = null; }
}

function startTimer() {
  stopTimer();
  timeLeft = ROUND_SECONDS;
  timerEl.textContent = String(timeLeft);
  timerEl.classList.remove('hidden', 'is-urgent');
  timerId = setInterval(() => {
    timeLeft -= 1;
    timerEl.textContent = String(Math.max(0, timeLeft));
    if (timeLeft <= 10) timerEl.classList.add('is-urgent');
    if (timeLeft <= 0) {
      stopTimer();
      game.timeUp();
      render();
    }
  }, 1000);
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

  bettingPanelEl.classList.toggle('hidden', state.phase !== 'betting');
  drawPanelEl.classList.toggle('hidden', state.phase !== 'drawing');
  playPanelEl.classList.toggle('hidden', state.phase !== 'playing');
  resultPanelEl.classList.toggle('hidden', state.phase !== 'result');
  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting');
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');
  timerEl.classList.toggle('hidden', state.phase !== 'playing');

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet);

  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || !dictionaryReady || pendingBet + amount > state.bankroll;
  });
  btnStart.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver || !dictionaryReady;

  if (state.phase === 'drawing') {
    drawProgressEl.textContent = `Lettre ${state.letters.length + 1} / ${DRAW_COUNT}`;
    drawnRowEl.innerHTML = '';
    state.letters.forEach((l) => {
      const tile = document.createElement('span');
      tile.className = 'letter-tile';
      tile.textContent = l;
      drawnRowEl.appendChild(tile);
    });
    btnDrawConsonant.disabled = state.mustDrawVowel;
    drawHintEl.textContent = state.mustDrawVowel
      ? 'Il faut au moins 2 voyelles (Y compte comme voyelle) : voyelle obligatoire.'
      : `${state.vowelsDrawn} voyelle(s), ${state.consonantsDrawn} consonne(s) tirée(s).`;

  }

  // Le moteur bascule en phase 'playing' dès la 10e lettre tirée (avant
  // même le prochain rendu) : c'est donc ici, à l'entrée fraîche en phase
  // de jeu, qu'il faut peupler les tuiles - pas dans le bloc 'drawing'
  // ci-dessus, qui ne sera jamais revisité une fois le tirage complet.
  const isFreshPlaying = state.phase === 'playing' && lastPhase !== 'playing';
  if (isFreshPlaying) {
    lettersRowEl.innerHTML = '';
    usedTileIds = new Set();
    state.letters.forEach((l, idx) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'letter-tile letter-tile-btn';
      btn.textContent = l;
      btn.dataset.idx = String(idx);
      btn.addEventListener('click', () => {
        if (usedTileIds.has(idx)) return;
        usedTileIds.add(idx);
        btn.classList.add('is-used');
        wordInputEl.value += l;
        wordInputEl.focus();
        btnValidate.disabled = wordInputEl.value.trim().length === 0;
      });
      lettersRowEl.appendChild(btn);
    });
    wordInputEl.value = '';
    startTimer();
    dealerVoice.say('dealing');
  }

  if (state.phase === 'playing') {
    btnValidate.disabled = wordInputEl.value.trim().length === 0;
  }

  const isFreshResult = state.phase === 'result' && lastPhase !== 'result';
  if (isFreshResult) {
    stopTimer();
    const won = state.payout > 0;
    const foundWord = state.submittedWord;
    if (foundWord) {
      resultMessageEl.textContent = won
        ? `« ${foundWord} » — ${state.points} lettres, ${state.multiplier}x, vous gagnez ${state.payout} !`
        : `« ${foundWord} » — ${state.points} lettres, pas de gain cette fois.`;
    } else {
      resultMessageEl.textContent = 'Aucun mot valide proposé — pas de gain cette fois.';
    }
    resultMessageEl.classList.toggle('is-lose', !won);

    resultDetailEl.textContent = state.bestWord
      ? `Le meilleur mot possible avec ce tirage était « ${state.bestWord} » (${state.bestWord.length} lettres).`
      : '';

    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    if (won) {
      flashTable('win');
      burstConfetti();
      if (state.multiplier >= 12) dealerVoice.say('win_jackpot');
      else if (state.multiplier >= 3) dealerVoice.say('win_big');
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

btnStart.addEventListener('click', () => {
  const result = game.start(pendingBet);
  if (result.ok) {
    pendingBet = 0;
    dealerVoice.say('greeting_round');
  }
  render();
});

btnDrawVowel.addEventListener('click', () => {
  game.drawLetter('vowel');
  render();
});
btnDrawConsonant.addEventListener('click', () => {
  game.drawLetter('consonant');
  render();
});

wordInputEl.addEventListener('input', () => {
  wordInputEl.value = wordInputEl.value.toUpperCase().replace(/[^A-ZÀ-ÿ]/g, '');
  btnValidate.disabled = wordInputEl.value.trim().length === 0;
});

document.getElementById('btn-clear-word').addEventListener('click', () => {
  wordInputEl.value = '';
  usedTileIds = new Set();
  lettersRowEl.querySelectorAll('.letter-tile-btn').forEach((btn) => btn.classList.remove('is-used'));
  btnValidate.disabled = true;
  wordInputEl.focus();
});

btnValidate.addEventListener('click', () => {
  game.submit(wordInputEl.value);
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  stopTimer();
  game.newSession();
  pendingBet = 0;
  lastBankrollShown = null;
  lastPhase = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
