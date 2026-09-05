/** Mini-jeu "Le compte est bon" (épreuve des chiffres de "Des chiffres et
 * des lettres") du Casino Fanny : 6 plaques sont tirées (petites 1-10 en
 * double exemplaire, grandes 25/50/75/100 à l'unité) et il faut s'approcher
 * au mieux d'une cible à trois chiffres (101-999) en combinant les plaques
 * avec +, -, x, ÷ (division exacte uniquement, résultat intermédiaire
 * toujours un entier strictement positif, une plaque ou un résultat déjà
 * utilisé ne peut pas resservir - conforme au règlement du plateau).
 *
 * Barème du plateau TV : 10 points si compte exact OU meilleure approche
 * possible quand la cible est infaisable, 7 points pour toute autre
 * réponse valide, 0 sinon. Converti ici en palier de gain façon paytable
 * de vidéo poker (choix maison, comme les autres jeux du casino).
 *
 * Sources : https://en.wikipedia.org/wiki/Des_chiffres_et_des_lettres,
 * https://dcdl-toulouse.over-blog.com/2021/01/regles-du-jeu-en-quelques-mots.html,
 * http://cybercl.free.fr/reglem/freglem.html */

export const SMALL_VALUES = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10];
export const BIG_VALUES = [25, 50, 75, 100];
export const PLAQUES_COUNT = 6;
export const ROUND_SECONDS = 45;
export const TARGET_MIN = 101;
export const TARGET_MAX = 999;

// Palier de gain : mult est le multiplicateur de la mise. Le premier
// palier dont le score atteint `min` l'emporte (score = points du barème
// officiel, 10 ou 7 ou 0).
export const TIERS = [
  { key: 'exact', name: 'Compte exact !', min: 10, mult: 8 },
  { key: 'approche', name: 'Bonne approche', min: 7, mult: 2 },
  { key: 'rate', name: 'Hors compte', min: 0, mult: 0 },
];

export function tierForScore(score) {
  return TIERS.find((t) => score >= t.min);
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function buildSmallPool() {
  // Deux exemplaires de chaque plaque 1-10, comme au plateau TV.
  const pool = [];
  SMALL_VALUES.forEach((v) => { pool.push(v, v); });
  return pool;
}

/** Tire les 6 plaques : `bigCount` grandes (25/50/75/100, une seule de
 * chaque possible) et le reste en petites (1-10, deux exemplaires dispo). */
export function drawPlaques(bigCount = 2) {
  const nBig = Math.max(0, Math.min(BIG_VALUES.length, bigCount));
  const bigDraw = shuffle(BIG_VALUES).slice(0, nBig);
  const smallDraw = shuffle(buildSmallPool()).slice(0, PLAQUES_COUNT - nBig);
  return shuffle([...bigDraw, ...smallDraw]);
}

export function drawTarget() {
  return TARGET_MIN + Math.floor(Math.random() * (TARGET_MAX - TARGET_MIN + 1));
}

/* ------------------------------------------------------------------ */
/* Résolveur : explore récursivement toutes les combinaisons du         */
/* multi-ensemble de plaques (algorithme classique du "compte est bon", */
/* mémoïsé sur la signature valeurs-triées pour rester rapide même sans */
/* worker) et retient, pour chaque valeur atteignable, une expression   */
/* qui permet de l'obtenir (utile pour la reprise en fin de manche).    */
/* ------------------------------------------------------------------ */
function combineAll(numbers) {
  const results = new Map(); // value -> expr (première trouvée)
  const visited = new Set();

  function recordAll(nums) {
    nums.forEach(({ value, expr }) => {
      if (!results.has(value)) results.set(value, expr);
    });
  }

  // Enrobe une sous-expression composite de parenthèses pour que
  // l'expression finale reste lisible sans ambiguïté de priorité
  // (utile dès qu'on mélange - ou ÷, non associatifs, dans la chaîne).
  const wrap = (n) => (n.leaf ? n.expr : `(${n.expr})`);

  function recurse(nums) {
    const key = nums.map((n) => n.value).slice().sort((a, b) => a - b).join(',');
    if (visited.has(key)) return;
    visited.add(key);
    recordAll(nums);
    if (nums.length === 1) return;

    for (let i = 0; i < nums.length; i += 1) {
      for (let j = i + 1; j < nums.length; j += 1) {
        const rest = nums.filter((_, k) => k !== i && k !== j);
        const a = nums[i];
        const b = nums[j];
        const candidates = [];
        candidates.push({ value: a.value + b.value, expr: `${wrap(a)} + ${wrap(b)}`, leaf: false });
        candidates.push({ value: a.value * b.value, expr: `${wrap(a)} × ${wrap(b)}`, leaf: false });
        if (a.value !== b.value) {
          const [hi, lo] = a.value > b.value ? [a, b] : [b, a];
          candidates.push({ value: hi.value - lo.value, expr: `${wrap(hi)} - ${wrap(lo)}`, leaf: false });
        }
        if (a.value % b.value === 0) {
          candidates.push({ value: a.value / b.value, expr: `${wrap(a)} ÷ ${wrap(b)}`, leaf: false });
        } else if (b.value % a.value === 0) {
          candidates.push({ value: b.value / a.value, expr: `${wrap(b)} ÷ ${wrap(a)}`, leaf: false });
        }
        candidates.forEach((c) => {
          if (c.value > 0) recurse([...rest, c]);
        });
      }
    }
  }

  recurse(numbers.map((v) => ({ value: v, expr: String(v), leaf: true })));
  return results;
}

/** Calcule, pour un tirage de plaques et une cible donnés, si le compte
 * exact est atteignable et le meilleur écart possible sinon, plus une
 * expression exemple permettant d'y arriver. */
export function solve(plaques, target) {
  const results = combineAll(plaques);
  const canReachExact = results.has(target);
  let bestDistance = Infinity;
  let bestValue = null;
  let bestExpr = null;
  results.forEach((expr, value) => {
    const d = Math.abs(value - target);
    if (d < bestDistance) {
      bestDistance = d;
      bestValue = value;
      bestExpr = expr;
    }
  });
  return {
    canReachExact,
    bestDistance,
    bestValue: canReachExact ? target : bestValue,
    bestExpr: canReachExact ? results.get(target) : bestExpr,
  };
}

/* ------------------------------------------------------------------ */
/* État de la manche                                                    */
/* ------------------------------------------------------------------ */

export class ChiffresGame {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.bigCount = 2;
    this.phase = 'betting'; // 'betting' | 'playing' | 'result'
    this.plaques = [];
    this.target = 0;
    this.solverStats = null;
    this.tokens = []; // { id, value, origin: bool }
    this.history = []; // { a, b, op, result }
    this.nextTokenId = 1;
    this.submittedValue = null;
    this.points = 0;
    this.multiplier = 0;
    this.payout = 0;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  setBigCount(n) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    this.bigCount = Math.max(0, Math.min(BIG_VALUES.length, Math.round(n)));
    return { ok: true };
  }

  start(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) return { ok: false, reason: 'bad-bet' };

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;

    this.plaques = drawPlaques(this.bigCount);
    this.target = drawTarget();
    this.solverStats = solve(this.plaques, this.target);
    this.tokens = this.plaques.map((v) => ({ id: this.nextTokenId += 1, value: v, origin: true }));
    this.history = [];
    this.submittedValue = null;
    this.points = 0;
    this.multiplier = 0;
    this.payout = 0;
    this.phase = 'playing';
    return { ok: true };
  }

  combine(idA, idB, op) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const ta = this.tokens.find((t) => t.id === idA);
    const tb = this.tokens.find((t) => t.id === idB);
    if (!ta || !tb || ta === tb) return { ok: false, reason: 'bad-token' };

    const a = ta.value;
    const b = tb.value;
    let result;
    if (op === '+') result = a + b;
    else if (op === 'x') result = a * b;
    else if (op === '-') {
      if (a === b) return { ok: false, reason: 'zero-result' };
      result = Math.abs(a - b);
    } else if (op === '/') {
      if (a % b === 0) result = a / b;
      else if (b % a === 0) result = b / a;
      else return { ok: false, reason: 'not-integer' };
    } else {
      return { ok: false, reason: 'bad-op' };
    }
    if (!(result > 0)) return { ok: false, reason: 'non-positive' };

    this.tokens = this.tokens.filter((t) => t !== ta && t !== tb);
    const newToken = { id: this.nextTokenId += 1, value: result, origin: false };
    this.tokens.push(newToken);
    this.history.push({ a, b, op, result });
    return { ok: true, token: newToken };
  }

  _bestToken() {
    if (this.tokens.length === 0) return null;
    return this.tokens.reduce((best, t) => (
      Math.abs(t.value - this.target) < Math.abs(best.value - this.target) ? t : best
    ));
  }

  submit(tokenId) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const t = tokenId != null ? this.tokens.find((x) => x.id === tokenId) : this._bestToken();
    if (!t) return { ok: false, reason: 'no-token' };
    this._finish(t.value);
    return { ok: true };
  }

  timeUp() {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const t = this._bestToken();
    this._finish(t ? t.value : 0);
    return { ok: true };
  }

  _finish(value) {
    this.submittedValue = value;
    const diff = Math.abs(value - this.target);
    const { bestDistance } = this.solverStats;
    if (diff === 0 || diff === bestDistance) this.points = 10;
    else this.points = 7;
    const tier = tierForScore(this.points);
    this.multiplier = tier.mult;
    this.payout = this.bet * this.multiplier;
    this.bankroll += this.payout;
    this.phase = 'result';
  }

  nextRound() {
    this.phase = 'betting';
    this.plaques = [];
    this.target = 0;
    this.solverStats = null;
    this.tokens = [];
    this.history = [];
    this.submittedValue = null;
    this.points = 0;
    this.multiplier = 0;
    this.payout = 0;
    this.bet = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      bigCount: this.bigCount,
      plaques: [...this.plaques],
      target: this.target,
      tokens: this.tokens.map((t) => ({ ...t })),
      history: [...this.history],
      submittedValue: this.submittedValue,
      points: this.points,
      multiplier: this.multiplier,
      payout: this.payout,
      bestDistance: this.solverStats ? this.solverStats.bestDistance : null,
      canReachExact: this.solverStats ? this.solverStats.canReachExact : null,
      bestExpr: this.solverStats ? this.solverStats.bestExpr : null,
      bestValue: this.solverStats ? this.solverStats.bestValue : null,
    };
  }
}
