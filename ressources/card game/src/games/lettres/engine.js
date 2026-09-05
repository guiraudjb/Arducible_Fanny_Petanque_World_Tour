/** Mini-jeu "Le mot le plus long" (épreuve des lettres de "Des chiffres et
 * des lettres") du Casino Fanny : 10 lettres sont tirées une à une - le
 * joueur choisit "voyelle" ou "consonne" à chaque tirage - avec un minimum
 * réglementaire de 2 voyelles (le Y compte comme voyelle), et il faut
 * former le mot valide le plus long possible avant la fin du temps
 * imparti. Score officiel = 1 point par lettre du mot trouvé, converti ici
 * en palier de gain façon paytable de vidéo poker (choix maison, comme les
 * autres jeux du casino).
 *
 * Dictionnaire ET distribution des lettres mutualisés avec le Scrabble du
 * Casino Fanny : mots.txt (assets/scrabble/mots.txt, chargé par l'appelant
 * - voir games/lettres/main.js) sert de référence pour valider les mots,
 * et le sac de lettres reprend la distribution officielle des jetons du
 * Scrabble français (hors joker, qui n'a pas de sens pour former un mot
 * ici) - cf. src/games/scrabble/engine.js.
 *
 * Sources : https://en.wikipedia.org/wiki/Des_chiffres_et_des_lettres,
 * https://top-nsi.fr/projets_1ere/2/F-7/,
 * https://dcdl-toulouse.over-blog.com/2021/01/regles-du-jeu-en-quelques-mots.html */

export const DRAW_COUNT = 10;
export const MIN_VOWELS = 2;
export const ROUND_SECONDS = 45;
export const VOWEL_LETTERS = ['A', 'E', 'I', 'O', 'U', 'Y'];

// Distribution officielle des jetons du Scrabble français (hors les 2
// jokers, sans objet ici) - cf. TILE_DISTRIBUTION dans
// src/games/scrabble/engine.js. 45 voyelles + 55 consonnes = 100 lettres.
const VOWEL_BAG = [
  ['A', 9], ['E', 15], ['I', 8], ['O', 6], ['U', 6], ['Y', 1],
];
const CONSONANT_BAG = [
  ['B', 2], ['C', 2], ['D', 3], ['F', 2], ['G', 2], ['H', 2], ['J', 1],
  ['K', 1], ['L', 5], ['M', 3], ['N', 6], ['P', 2], ['Q', 1], ['R', 6],
  ['S', 6], ['T', 6], ['V', 2], ['W', 1], ['X', 1], ['Z', 1],
];

function expandBag(bag) {
  const out = [];
  bag.forEach(([letter, qty]) => { for (let i = 0; i < qty; i += 1) out.push(letter); });
  return out;
}

function shuffle(arr) {
  const a = [...arr];
  for (let i = a.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// Palier de gain : mult est le multiplicateur de la mise, selon la
// longueur du mot trouvé (score officiel = nombre de lettres).
export const TIERS = [
  { key: 'legendaire', name: 'Mot légendaire (10 lettres)', min: 10, mult: 25 },
  { key: 'exceptionnel', name: 'Mot exceptionnel (9 lettres)', min: 9, mult: 12 },
  { key: 'remarquable', name: 'Mot remarquable (8 lettres)', min: 8, mult: 6 },
  { key: 'beau', name: 'Beau mot (7 lettres)', min: 7, mult: 3 },
  { key: 'bon', name: 'Bon mot (6 lettres)', min: 6, mult: 2 },
  { key: 'correct', name: 'Mot correct (5 lettres)', min: 5, mult: 1 },
  { key: 'maigre', name: 'Mot maigre (3-4 lettres)', min: 3, mult: 0 },
  { key: 'nul', name: 'Trop court ou invalide', min: 0, mult: 0 },
];

export function tierForScore(score) {
  return TIERS.find((t) => score >= t.min);
}

/** Cherche, parmi `wordsArray`, le mot le plus long formable avec le
 * multi-ensemble `letters` (première trouvée à longueur maximale). */
export function findBestWord(letters, wordsArray) {
  const counts = {};
  letters.forEach((l) => { counts[l] = (counts[l] || 0) + 1; });
  let best = '';
  for (let i = 0; i < wordsArray.length; i += 1) {
    const w = wordsArray[i];
    if (w.length <= best.length || w.length > letters.length) continue;
    const c = { ...counts };
    let ok = true;
    for (let k = 0; k < w.length; k += 1) {
      const ch = w[k];
      if (!c[ch]) { ok = false; break; }
      c[ch] -= 1;
    }
    if (ok) best = w;
  }
  return best || null;
}

/* ------------------------------------------------------------------ */
/* État de la manche                                                    */
/* ------------------------------------------------------------------ */

export class LettresGame {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.wordsArray = null;
    this.wordSet = null;
    this.newSession();
  }

  /** À appeler une fois le dictionnaire chargé (fetch mots.txt côté UI). */
  setDictionary(wordsArray, wordSet) {
    this.wordsArray = wordsArray;
    this.wordSet = wordSet || new Set(wordsArray);
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.phase = 'betting'; // 'betting' | 'drawing' | 'playing' | 'result'
    this.letters = [];
    this.vowelBag = [];
    this.consonantBag = [];
    this.vowelsDrawn = 0;
    this.consonantsDrawn = 0;
    this.submittedWord = null;
    this.points = 0;
    this.multiplier = 0;
    this.payout = 0;
    this.bestWord = null;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  // Faut-il bloquer le choix "consonne" pour garantir le minimum
  // réglementaire de 2 voyelles avant la fin du tirage ?
  get mustDrawVowel() {
    const remaining = DRAW_COUNT - this.letters.length;
    const vowelsNeeded = MIN_VOWELS - this.vowelsDrawn;
    return vowelsNeeded >= remaining && vowelsNeeded > 0;
  }

  start(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) return { ok: false, reason: 'bad-bet' };

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;

    this.letters = [];
    this.vowelBag = shuffle(expandBag(VOWEL_BAG));
    this.consonantBag = shuffle(expandBag(CONSONANT_BAG));
    this.vowelsDrawn = 0;
    this.consonantsDrawn = 0;
    this.submittedWord = null;
    this.points = 0;
    this.multiplier = 0;
    this.payout = 0;
    this.bestWord = null;
    this.phase = 'drawing';
    return { ok: true };
  }

  drawLetter(kind) {
    if (this.phase !== 'drawing') return { ok: false, reason: 'wrong-phase' };
    if (this.letters.length >= DRAW_COUNT) return { ok: false, reason: 'complete' };
    if (kind === 'consonant' && this.mustDrawVowel) return { ok: false, reason: 'need-vowel' };

    const bag = kind === 'vowel' ? this.vowelBag : this.consonantBag;
    if (bag.length === 0) return { ok: false, reason: 'empty-bag' };

    const letter = bag.pop();
    this.letters.push(letter);
    if (kind === 'vowel') this.vowelsDrawn += 1; else this.consonantsDrawn += 1;
    if (this.letters.length >= DRAW_COUNT) this.phase = 'playing';
    return { ok: true, letter };
  }

  /** Le mot proposé (multi-ensemble) est-il formable avec les lettres tirées ? */
  canFormWord(word) {
    const w = (word || '').toUpperCase();
    if (!w) return false;
    const counts = {};
    this.letters.forEach((l) => { counts[l] = (counts[l] || 0) + 1; });
    for (let i = 0; i < w.length; i += 1) {
      const ch = w[i];
      if (!counts[ch]) return false;
      counts[ch] -= 1;
    }
    return true;
  }

  isDictionaryWord(word) {
    if (!this.wordSet) return false;
    return this.wordSet.has((word || '').toUpperCase());
  }

  submit(word) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const w = (word || '').toUpperCase().trim();
    const valid = w.length > 0 && this.canFormWord(w) && this.isDictionaryWord(w);
    this._finish(valid ? w : '');
    return { ok: true, valid };
  }

  timeUp() {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    this._finish('');
    return { ok: true };
  }

  _finish(word) {
    this.submittedWord = word;
    this.points = word.length;
    if (this.wordsArray) this.bestWord = findBestWord(this.letters, this.wordsArray);
    const tier = tierForScore(this.points);
    this.multiplier = tier.mult;
    this.payout = this.bet * this.multiplier;
    this.bankroll += this.payout;
    this.phase = 'result';
  }

  nextRound() {
    this.phase = 'betting';
    this.letters = [];
    this.vowelsDrawn = 0;
    this.consonantsDrawn = 0;
    this.submittedWord = null;
    this.points = 0;
    this.multiplier = 0;
    this.payout = 0;
    this.bestWord = null;
    this.bet = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      letters: [...this.letters],
      vowelsDrawn: this.vowelsDrawn,
      consonantsDrawn: this.consonantsDrawn,
      drawComplete: this.letters.length >= DRAW_COUNT,
      mustDrawVowel: this.phase === 'drawing' ? this.mustDrawVowel : false,
      submittedWord: this.submittedWord,
      points: this.points,
      multiplier: this.multiplier,
      payout: this.payout,
      bestWord: this.bestWord,
    };
  }
}
