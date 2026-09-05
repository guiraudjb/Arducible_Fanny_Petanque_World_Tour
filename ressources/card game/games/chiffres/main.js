import { ChiffresGame, BIG_VALUES, ROUND_SECONDS } from '../../src/games/chiffres/engine.js';
import { createDealerVoice } from '../../src/dealer/dealerVoice.js';

const prefersReducedMotion = () =>
  window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const game = new ChiffresGame({ startingBankroll: 500 });
let pendingBet = 0;
let selected = []; // ids des jetons sélectionnés (0, 1 ou 2)
let lastBankrollShown = null;
let lastPhase = null;
let bankruptcyAnnounced = false;
let timerId = null;
let timeLeft = ROUND_SECONDS;

const dealerVoice = createDealerVoice({
  game: 'chiffres',
  bubbleEl: document.getElementById('dealer-bubble'),
  textEl: document.getElementById('dealer-bubble-text'),
  muteBtn: document.getElementById('btn-mute'),
});

const tableEl = document.getElementById('table');
const bankrollEl = document.getElementById('bankroll');
const statusEl = document.getElementById('status');
const timerEl = document.getElementById('timer');
const bigPickerEl = document.getElementById('big-picker');
const bettingPanelEl = document.getElementById('betting-panel');
const playPanelEl = document.getElementById('play-panel');
const resultPanelEl = document.getElementById('result-panel');
const targetValueEl = document.getElementById('target-value');
const plaquesRowEl = document.getElementById('plaques-row');
const opsRowEl = document.getElementById('ops-row');
const opHintEl = document.getElementById('op-hint');
const historyLogEl = document.getElementById('history-log');
const btnValidate = document.getElementById('btn-validate');
const resultMessageEl = document.getElementById('result-message');
const resultDetailEl = document.getElementById('result-detail');
const resultSolutionEl = document.getElementById('result-solution');
const betAmountEl = document.getElementById('bet-amount');
const bettingAreaEl = document.getElementById('betting-area');
const resultAreaEl = document.getElementById('result-area');
const btnStart = document.getElementById('btn-start');

/* ---------------------------------------------------------------- */
/* Confettis (identique aux autres jeux du casino)                      */
/* ---------------------------------------------------------------- */
const fxCanvas = document.createElement('canvas');
fxCanvas.id = 'fx-canvas';
document.getElementById('table').appendChild(fxCanvas);
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
/* Sélecteur de grandes plaques (phase mise)                           */
/* ---------------------------------------------------------------- */
for (let n = 0; n <= BIG_VALUES.length; n += 1) {
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'big-btn';
  btn.textContent = String(n);
  btn.dataset.n = String(n);
  btn.addEventListener('click', () => {
    game.setBigCount(n);
    render();
  });
  bigPickerEl.appendChild(btn);
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
  playPanelEl.classList.toggle('hidden', state.phase !== 'playing');
  resultPanelEl.classList.toggle('hidden', state.phase !== 'result');
  bettingAreaEl.classList.toggle('hidden', state.phase !== 'betting');
  resultAreaEl.classList.toggle('hidden', state.phase !== 'result');
  timerEl.classList.toggle('hidden', state.phase !== 'playing');

  betAmountEl.textContent = String(state.phase === 'betting' ? pendingBet : state.bet);

  [...bigPickerEl.children].forEach((btn) => {
    btn.classList.toggle('is-selected', Number(btn.dataset.n) === state.bigCount);
    btn.disabled = state.phase !== 'betting';
  });

  document.querySelectorAll('.chip').forEach((btn) => {
    const amount = Number(btn.dataset.chip);
    btn.disabled = state.isGameOver || pendingBet + amount > state.bankroll;
  });
  btnStart.disabled = pendingBet <= 0 || pendingBet > state.bankroll || state.isGameOver;

  if (state.phase === 'playing') {
    targetValueEl.textContent = String(state.target);

    plaquesRowEl.innerHTML = '';
    state.tokens.forEach((t) => {
      const btn = document.createElement('button');
      btn.type = 'button';
      btn.className = 'plaque-btn' + (t.origin ? '' : ' is-result');
      btn.textContent = String(t.value);
      btn.dataset.id = String(t.id);
      btn.classList.toggle('is-selected', selected.includes(t.id));
      btn.addEventListener('click', () => onTokenClick(t.id));
      plaquesRowEl.appendChild(btn);
    });

    opsRowEl.querySelectorAll('.op-btn').forEach((btn) => {
      btn.disabled = selected.length !== 2;
    });
    opHintEl.textContent = selected.length === 2
      ? 'Choisissez une opération.'
      : 'Choisissez deux plaques puis une opération.';

    historyLogEl.innerHTML = '';
    state.history.forEach((h) => {
      const line = document.createElement('p');
      const opSym = { '+': '+', '-': '−', x: '×', '/': '÷' }[h.op] || h.op;
      line.textContent = `${h.a} ${opSym} ${h.b} = ${h.result}`;
      historyLogEl.appendChild(line);
    });
    historyLogEl.scrollTop = historyLogEl.scrollHeight;

    btnValidate.disabled = selected.length !== 1;
  }

  const isFreshResult = state.phase === 'result' && lastPhase !== 'result';
  if (isFreshResult) {
    stopTimer();
    const won = state.payout > 0;
    const diff = Math.abs(state.submittedValue - state.target);
    resultMessageEl.textContent = diff === 0
      ? `Compte exact : ${state.submittedValue} ! ${state.points} points, ${state.multiplier}x, vous gagnez ${state.payout} !`
      : won
        ? `Vous proposez ${state.submittedValue} (écart ${diff}) — la meilleure approche possible ! ${state.points} points, ${state.multiplier}x, vous gagnez ${state.payout} !`
        : `Vous proposez ${state.submittedValue} (écart ${diff}) — ${state.points} points, pas de gain cette fois.`;
    resultMessageEl.classList.toggle('is-lose', !won);

    resultDetailEl.textContent = state.canReachExact
      ? `Le compte exact était atteignable.`
      : `Le compte exact n'était pas atteignable — meilleur écart possible : ${state.bestDistance}.`;
    resultSolutionEl.textContent = state.bestExpr
      ? `Une solution possible : ${state.bestExpr} = ${state.bestValue}`
      : '';

    resultMessageEl.classList.remove('pop');
    void resultMessageEl.offsetWidth;
    resultMessageEl.classList.add('pop');

    if (won) {
      flashTable('win');
      burstConfetti();
      if (diff === 0) dealerVoice.say('exact');
      else dealerVoice.say('win_big');
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

function onTokenClick(id) {
  if (selected.includes(id)) {
    selected = selected.filter((x) => x !== id);
  } else if (selected.length < 2) {
    selected.push(id);
  } else {
    // Troisième clic : on repart d'une sélection propre avec ce nouveau jeton.
    selected = [id];
  }
  render();
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
    selected = [];
    startTimer();
    dealerVoice.say('dealing');
  }
  render();
});

opsRowEl.querySelectorAll('.op-btn').forEach((btn) => {
  btn.addEventListener('click', () => {
    if (selected.length !== 2) return;
    const [idA, idB] = selected;
    const result = game.combine(idA, idB, btn.dataset.op);
    if (result.ok) {
      selected = [result.token.id];
    } else {
      opHintEl.textContent = 'Opération impossible (résultat non entier ou négatif) — essayez autre chose.';
    }
    render();
  });
});

btnValidate.addEventListener('click', () => {
  if (selected.length !== 1) return;
  game.submit(selected[0]);
  selected = [];
  render();
});

document.getElementById('btn-next-round').addEventListener('click', () => {
  game.nextRound();
  pendingBet = Math.min(game.lastBet, game.bankroll) || 0;
  selected = [];
  render();
});

document.getElementById('btn-new-game').addEventListener('click', () => {
  stopTimer();
  game.newSession();
  pendingBet = 0;
  selected = [];
  lastBankrollShown = null;
  lastPhase = null;
  bankruptcyAnnounced = false;
  render();
  dealerVoice.say('greeting');
});

render();
dealerVoice.say('greeting');
