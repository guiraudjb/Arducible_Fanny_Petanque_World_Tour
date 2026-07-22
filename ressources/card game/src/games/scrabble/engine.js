/** Mini-jeu Scrabble "duplicate" du Casino Fanny : à chaque mise, une
 * grille 15x15 officielle (mêmes cases bonus que le vrai jeu) est tirée
 * déjà entamée par quelques mots (comme en duplicate/blitz : tout le
 * monde part de la même grille), et vous recevez un chevalet de 7
 * lettres fraîches. Il faut prolonger un mot existant en respectant les
 * vraies règles du Scrabble (alignement, pas de trou, tous les mots
 * croisés formés doivent être valides) avant la fin du temps imparti.
 * Score officiel (cases bonus uniquement sur les lettres nouvellement
 * posées, +50 si les 7 lettres du chevalet sont posées d'un coup) →
 * palier de gain façon paytable de vidéo poker. */

export const BOARD_SIZE = 15;
export const CENTER = 7;

// Disposition officielle du plateau Scrabble (identique quelle que soit
// la langue - seules les valeurs des lettres changent). '.'=rien,
// w=Mot triple, d=Mot double, l=Lettre double, t=Lettre triple,
// D=case centrale (mot double, avec étoile).
const BONUS_ROWS = [
  'w..l...w...l..w',
  '.d...t...t...d.',
  '..d...l.l...d..',
  'l..d...l...d..l',
  '....d.....d....',
  '.t...t...t...t.',
  '..l...l.l...l..',
  'w..l...D...l..w',
  '..l...l.l...l..',
  '.t...t...t...t.',
  '....d.....d....',
  'l..d...l...d..l',
  '..d...l.l...d..',
  '.d...t...t...d.',
  'w..l...w...l..w',
];
const BONUS_CODE = { '.': null, w: 'TW', d: 'DW', l: 'DL', t: 'TL', D: 'DW' };
export const BOARD_BONUS = BONUS_ROWS.map((row) => row.split('').map((ch) => BONUS_CODE[ch]));
export const BONUS_LABELS = { TW: 'MT', DW: 'MD', TL: 'LT', DL: 'LD' };

// [lettre, quantité dans le sac, valeur en points] - distribution standard
// du Scrabble français (102 jetons dont 2 jokers).
const TILE_DISTRIBUTION = [
  ['A', 9, 1], ['B', 2, 3], ['C', 2, 3], ['D', 3, 2], ['E', 15, 1],
  ['F', 2, 4], ['G', 2, 2], ['H', 2, 4], ['I', 8, 1], ['J', 1, 8],
  ['K', 1, 10], ['L', 5, 1], ['M', 3, 2], ['N', 6, 1], ['O', 6, 1],
  ['P', 2, 3], ['Q', 1, 8], ['R', 6, 1], ['S', 6, 1], ['T', 6, 1],
  ['U', 6, 1], ['V', 2, 4], ['W', 1, 10], ['X', 1, 10], ['Y', 1, 10],
  ['Z', 1, 10], ['*', 2, 0],
];

export const LETTER_VALUES = Object.fromEntries(TILE_DISTRIBUTION.map(([l, , v]) => [l, v]));

export const RACK_SIZE = 7;
export const BINGO_BONUS = 50;
export const ROUND_SECONDS = 90;
const GENERATION_TARGET_WORDS = 5;
const GENERATION_MAX_ATTEMPTS = 250;

// Paliers de gain (du meilleur au moins bon) : mult est le multiplicateur
// de la mise. Le premier palier dont le score atteint `min` l'emporte.
export const TIERS = [
  { key: 'legendaire', name: 'Mot légendaire', min: 70, mult: 20 },
  { key: 'exceptionnel', name: 'Mot exceptionnel', min: 45, mult: 10 },
  { key: 'remarquable', name: 'Mot remarquable', min: 30, mult: 5 },
  { key: 'beau', name: 'Beau mot', min: 20, mult: 3 },
  { key: 'bon', name: 'Bon mot', min: 12, mult: 2 },
  { key: 'correct', name: 'Mot correct', min: 6, mult: 1 },
  { key: 'maigre', name: 'Mot maigre', min: 1, mult: 0 },
  { key: 'invalide', name: 'Mot invalide', min: 0, mult: 0 },
];

export function tierForScore(score) {
  return TIERS.find((t) => score >= t.min);
}

/* ------------------------------------------------------------------ */
/* Sac de lettres                                                       */
/* ------------------------------------------------------------------ */

function buildBag() {
  const bag = [];
  for (const [letter, count, value] of TILE_DISTRIBUTION) {
    for (let i = 0; i < count; i += 1) bag.push({ letter, value });
  }
  return bag;
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

let nextTileId = 1;

function drawTiles(bag, count) {
  const tiles = [];
  for (let i = 0; i < count && bag.length > 0; i += 1) {
    const { letter, value } = bag.pop();
    tiles.push({
      id: nextTileId++,
      letter,
      value,
      isBlank: letter === '*',
      assignedLetter: null,
    });
  }
  return tiles;
}

function takeLettersFromBag(bag, letters) {
  for (const letter of letters) {
    const idx = bag.findIndex((t) => t.letter === letter);
    bag.splice(idx, 1);
  }
}

function bagHasLetters(bag, letters) {
  const need = {};
  for (const l of letters) need[l] = (need[l] || 0) + 1;
  const have = {};
  for (const t of bag) have[t.letter] = (have[t.letter] || 0) + 1;
  return Object.entries(need).every(([l, n]) => (have[l] || 0) >= n);
}

/* ------------------------------------------------------------------ */
/* Cœur des règles : résolution d'un coup (posé de lettres)             */
/* ------------------------------------------------------------------ */

function makeEmptyBoardCells() {
  return Array.from({ length: BOARD_SIZE }, () =>
    Array.from({ length: BOARD_SIZE }, () => ({ letter: null, value: null })));
}

function runCells(read, row, col, axis) {
  const cells = [];
  if (axis === 'row') {
    let c0 = col; while (read(row, c0 - 1)) c0 -= 1;
    let c1 = col; while (read(row, c1 + 1)) c1 += 1;
    for (let c = c0; c <= c1; c += 1) cells.push({ ...read(row, c), row, col: c });
  } else {
    let r0 = row; while (read(r0 - 1, col)) r0 -= 1;
    let r1 = row; while (read(r1 + 1, col)) r1 += 1;
    for (let r = r0; r <= r1; r += 1) cells.push({ ...read(r, col), row: r, col });
  }
  return cells;
}

/**
 * Résout un coup : placements = lettres NOUVELLEMENT posées uniquement
 * (jamais une case déjà occupée - une lettre déjà sur la grille est lue
 * via getCell, pas re-posée). Renvoie les mots formés (principal +
 * éventuels mots croisés), chacun avec le détail des cases pour le
 * calcul du score. `requireConnection` doit rester true pour un coup du
 * joueur (la grille n'est jamais vide dans ce mini-jeu) ; on ne le passe
 * à false que pour poser le tout premier mot de la génération de grille.
 */
export function resolveMove({ getCell, placements, requireConnection = true }) {
  if (!placements || placements.length === 0) return { ok: false, reason: 'empty' };
  for (const p of placements) {
    if (p.row < 0 || p.row >= BOARD_SIZE || p.col < 0 || p.col >= BOARD_SIZE) {
      return { ok: false, reason: 'out-of-bounds' };
    }
    if (getCell(p.row, p.col)) return { ok: false, reason: 'occupied' };
  }
  const cellKeys = new Set(placements.map((p) => `${p.row},${p.col}`));
  if (cellKeys.size !== placements.length) return { ok: false, reason: 'duplicate-cell' };

  const rows = new Set(placements.map((p) => p.row));
  const cols = new Set(placements.map((p) => p.col));
  let axis = null;
  if (placements.length > 1) {
    if (rows.size === 1) axis = 'row';
    else if (cols.size === 1) axis = 'col';
    else return { ok: false, reason: 'not-collinear' };
  }

  const placementMap = new Map(placements.map((p) => [`${p.row},${p.col}`, p]));
  function read(r, c) {
    if (r < 0 || r >= BOARD_SIZE || c < 0 || c >= BOARD_SIZE) return null;
    const key = `${r},${c}`;
    if (placementMap.has(key)) {
      const p = placementMap.get(key);
      return { letter: p.letter, value: p.value, isNew: true, bonus: BOARD_BONUS[r][c] };
    }
    const existing = getCell(r, c);
    return existing ? { letter: existing.letter, value: existing.value, isNew: false, bonus: BOARD_BONUS[r][c] } : null;
  }

  // Pas de trou entre les lettres posées (les cases intermédiaires
  // doivent être comblées, soit par une nouvelle lettre, soit par une
  // lettre déjà présente sur la grille).
  if (axis === 'row') {
    const row = [...rows][0];
    const colsSorted = placements.map((p) => p.col).sort((a, b) => a - b);
    for (let c = colsSorted[0]; c <= colsSorted[colsSorted.length - 1]; c += 1) {
      if (!read(row, c)) return { ok: false, reason: 'gap' };
    }
  } else if (axis === 'col') {
    const col = [...cols][0];
    const rowsSorted = placements.map((p) => p.row).sort((a, b) => a - b);
    for (let r = rowsSorted[0]; r <= rowsSorted[rowsSorted.length - 1]; r += 1) {
      if (!read(r, col)) return { ok: false, reason: 'gap' };
    }
  }

  const words = [];
  function collect(row, col, runAxis) {
    const cells = runCells(read, row, col, runAxis);
    if (cells.length >= 2) words.push({ cells, text: cells.map((c) => c.letter).join('') });
  }

  if (placements.length === 1) {
    const p = placements[0];
    collect(p.row, p.col, 'row');
    collect(p.row, p.col, 'col');
  } else if (axis === 'row') {
    collect(placements[0].row, placements[0].col, 'row');
    for (const p of placements) collect(p.row, p.col, 'col');
  } else {
    collect(placements[0].row, placements[0].col, 'col');
    for (const p of placements) collect(p.row, p.col, 'row');
  }

  if (words.length === 0) return { ok: false, reason: 'not-connected' };

  const touchesExisting = words.some((w) => w.cells.some((c) => !c.isNew));
  if (requireConnection && !touchesExisting) return { ok: false, reason: 'not-connected' };

  return { ok: true, words };
}

export function scoreWords(words) {
  let total = 0;
  for (const { cells } of words) {
    let letterSum = 0;
    let wordMult = 1;
    for (const cell of cells) {
      let v = cell.value;
      if (cell.isNew) {
        if (cell.bonus === 'DL') v *= 2;
        else if (cell.bonus === 'TL') v *= 3;
        else if (cell.bonus === 'DW') wordMult *= 2;
        else if (cell.bonus === 'TW') wordMult *= 3;
      }
      letterSum += v;
    }
    total += letterSum * wordMult;
  }
  return total;
}

/* ------------------------------------------------------------------ */
/* Génération de la grille pré-remplie                                  */
/* ------------------------------------------------------------------ */

function randomWordCoveringCenter(wordsArray, bag) {
  const candidates = shuffle(wordsArray.filter((w) => w.length >= 4 && w.length <= 8));
  for (const word of candidates) {
    const startCol = CENTER - Math.floor(word.length / 2);
    if (startCol < 0 || startCol + word.length > BOARD_SIZE) continue;
    if (CENTER < startCol || CENTER >= startCol + word.length) continue;
    if (!bagHasLetters(bag, word.split(''))) continue;
    return { word, startCol };
  }
  return null;
}

function computeOverlapPlacement(word, anchorRow, anchorCol, anchorIndex, axis, getCell) {
  const placements = [];
  for (let j = 0; j < word.length; j += 1) {
    const row = axis === 'col' ? anchorRow - anchorIndex + j : anchorRow;
    const col = axis === 'row' ? anchorCol - anchorIndex + j : anchorCol;
    if (row < 0 || row >= BOARD_SIZE || col < 0 || col >= BOARD_SIZE) return null;
    const existing = getCell(row, col);
    if (existing) {
      if (existing.letter !== word[j]) return null;
    } else {
      placements.push({ row, col, letter: word[j], value: LETTER_VALUES[word[j]] });
    }
  }
  if (placements.length === 0) return null;
  return placements;
}

/** Construit une grille de départ en réutilisant resolveMove pour
 * garantir que chaque mot ajouté (y compris les croisements
 * accidentels) est légal - la génération suit exactement les mêmes
 * règles qu'un coup joué. `bag` est mutée (les lettres utilisées sont
 * retirées, comme si la grille avait été jouée avant que le joueur ne
 * tire son propre chevalet). */
function generateSeedBoard(bag, wordsArray) {
  const cells = makeEmptyBoardCells();
  const getCell = (r, c) => (cells[r][c].letter ? cells[r][c] : null);

  const first = randomWordCoveringCenter(wordsArray, bag);
  let placedWords = 0;
  if (first) {
    const placements = first.word.split('').map((letter, i) => ({
      row: CENTER, col: first.startCol + i, letter, value: LETTER_VALUES[letter],
    }));
    const resolved = resolveMove({ getCell, placements, requireConnection: false });
    if (resolved.ok) {
      for (const p of placements) cells[p.row][p.col] = { letter: p.letter, value: p.value };
      takeLettersFromBag(bag, placements.map((p) => p.letter));
      placedWords += 1;
    }
  }

  let attempts = 0;
  while (placedWords < GENERATION_TARGET_WORDS && attempts < GENERATION_MAX_ATTEMPTS) {
    attempts += 1;
    const filled = [];
    for (let r = 0; r < BOARD_SIZE; r += 1) {
      for (let c = 0; c < BOARD_SIZE; c += 1) {
        if (cells[r][c].letter) filled.push({ row: r, col: c, letter: cells[r][c].letter });
      }
    }
    if (filled.length === 0) break;
    const anchor = filled[Math.floor(Math.random() * filled.length)];
    const axis = Math.random() < 0.5 ? 'row' : 'col';

    const withLetter = wordsArray.filter((w) => w.length >= 2 && w.length <= 9 && w.includes(anchor.letter));
    if (withLetter.length === 0) continue;
    const word = withLetter[Math.floor(Math.random() * withLetter.length)];
    const indices = [];
    for (let i = 0; i < word.length; i += 1) if (word[i] === anchor.letter) indices.push(i);
    const anchorIndex = indices[Math.floor(Math.random() * indices.length)];

    const placements = computeOverlapPlacement(word, anchor.row, anchor.col, anchorIndex, axis, getCell);
    if (!placements) continue;
    if (!bagHasLetters(bag, placements.map((p) => p.letter))) continue;

    const resolved = resolveMove({ getCell, placements, requireConnection: true });
    if (!resolved.ok) continue;
    if (!resolved.words.every((w) => wordsArray.includes(w.text))) continue;

    for (const p of placements) cells[p.row][p.col] = { letter: p.letter, value: p.value };
    takeLettersFromBag(bag, placements.map((p) => p.letter));
    placedWords += 1;
  }

  return cells;
}

/* ------------------------------------------------------------------ */
/* Classe principale                                                    */
/* ------------------------------------------------------------------ */

export class Scrabble {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.phase = 'betting'; // 'betting' | 'playing' | 'result'
    this.board = makeEmptyBoardCells();
    this.rack = [];
    this.pending = []; // { row, col, tile }
    this.result = null;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  /** @param {string[]} wordsArray - dictionnaire (mots valides, majuscules sans accent) */
  startRound(bet, wordsArray) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) return { ok: false, reason: 'bad-bet' };
    if (!wordsArray || wordsArray.length === 0) return { ok: false, reason: 'no-dictionary' };

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;

    const bag = shuffle(buildBag());
    this.board = generateSeedBoard(bag, wordsArray);
    this.rack = drawTiles(bag, RACK_SIZE);
    this.pending = [];
    this.result = null;
    this.phase = 'playing';
    return { ok: true };
  }

  placeTileFromRack(rackIndex, row, col) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const tile = this.rack[rackIndex];
    if (!tile) return { ok: false, reason: 'bad-index' };
    if (tile.isBlank && !tile.assignedLetter) return { ok: false, reason: 'blank-unassigned' };
    if (this.board[row][col].letter) return { ok: false, reason: 'occupied' };
    if (this.pending.some((p) => p.row === row && p.col === col)) return { ok: false, reason: 'occupied' };
    this.rack.splice(rackIndex, 1);
    this.pending.push({ row, col, tile });
    return { ok: true };
  }

  returnPendingAt(row, col) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const idx = this.pending.findIndex((p) => p.row === row && p.col === col);
    if (idx === -1) return { ok: false, reason: 'not-found' };
    const [entry] = this.pending.splice(idx, 1);
    entry.tile.assignedLetter = null;
    this.rack.push(entry.tile);
    return { ok: true };
  }

  assignBlank(rackIndex, letter) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    const tile = this.rack[rackIndex];
    if (!tile || !tile.isBlank) return { ok: false, reason: 'not-blank' };
    if (!/^[A-Z]$/.test(letter)) return { ok: false, reason: 'bad-letter' };
    tile.assignedLetter = letter;
    return { ok: true };
  }

  shuffleRack() {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    shuffle(this.rack);
    return { ok: true };
  }

  clearPending() {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };
    while (this.pending.length > 0) this.returnPendingAt(this.pending[0].row, this.pending[0].col);
    return { ok: true };
  }

  /** @param {Set<string>} wordSet - mots valides (majuscules, sans accent) */
  submitMove(wordSet) {
    if (this.phase !== 'playing') return { ok: false, reason: 'wrong-phase' };

    const placements = this.pending.map((p) => ({
      row: p.row,
      col: p.col,
      letter: p.tile.isBlank ? p.tile.assignedLetter : p.tile.letter,
      value: p.tile.value,
    }));
    const getCell = (r, c) => (this.board[r][c].letter ? this.board[r][c] : null);
    const resolved = resolveMove({ getCell, placements, requireConnection: true });

    let valid = false;
    let words = [];
    let invalidWord = null;
    let rawScore = 0;
    if (resolved.ok) {
      const bad = resolved.words.find((w) => !wordSet.has(w.text));
      if (bad) {
        invalidWord = bad.text;
      } else {
        valid = true;
        words = resolved.words.map((w) => w.text);
        rawScore = scoreWords(resolved.words);
      }
    } else {
      invalidWord = resolved.reason;
    }

    const bingo = this.pending.length === RACK_SIZE;
    const score = valid ? rawScore + (bingo ? BINGO_BONUS : 0) : 0;
    const tier = tierForScore(score);
    const payout = valid ? this.bet * tier.mult : 0;

    if (valid) {
      for (const p of placements) this.board[p.row][p.col] = { letter: p.letter, value: p.value };
    }

    this.bankroll += payout;
    this.result = {
      valid, words, invalidWord, score, bingo, tier, payout,
      placedCells: placements.map(({ row, col }) => ({ row, col })),
    };
    this.phase = 'result';
    return { ok: true };
  }

  nextRound() {
    this.phase = 'betting';
    this.board = makeEmptyBoardCells();
    this.rack = [];
    this.pending = [];
    this.result = null;
    this.bet = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      board: this.board.map((rowCells, r) => rowCells.map((cell, c) => ({
        row: r,
        col: c,
        letter: cell.letter,
        bonus: BOARD_BONUS[r][c],
        isCenter: r === CENTER && c === CENTER,
      }))),
      rack: this.rack.map((t) => ({ ...t, display: t.isBlank ? (t.assignedLetter || '') : t.letter })),
      pending: this.pending.map((p) => ({
        row: p.row,
        col: p.col,
        value: p.tile.value,
        isBlank: p.tile.isBlank,
        display: p.tile.isBlank ? (p.tile.assignedLetter || '') : p.tile.letter,
      })),
      result: this.result,
    };
  }
}
