/* Générateur de lots de "Défis Scrabble" : réutilise le même moteur que le
 * mini-jeu du Casino Fanny (engine.js : classe Scrabble pour tirer une
 * grille de départ + chevalet, findBestMove pour calculer la solution de
 * Fanny) mais dessine tout au Canvas 2D plutôt qu'en DOM, pour pouvoir
 * exporter deux images JPEG par défi (le problème, puis la solution) et les
 * télécharger en lot - aucune dépendance externe (pas de html2canvas),
 * juste des rectangles/texte dessinés à la main dans le même style visuel
 * que style.css (couleurs reprises telles quelles).
 */
import { Scrabble, BOARD_SIZE, buildLetterIndex, findBestMove } from '../../src/games/scrabble/engine.js';

const WORDS_URL = new URL('../../assets/scrabble/mots.txt', import.meta.url);
const DEFINITIONS_URL = new URL('../../assets/scrabble/definitions.csv', import.meta.url);

const statusLineEl = document.getElementById('status-line');
const progressLineEl = document.getElementById('progress-line');
const btnPreview = document.getElementById('btn-preview');
const btnBatch = document.getElementById('btn-batch');
const batchCountEl = document.getElementById('batch-count');
const canvasProblemEl = document.getElementById('canvas-problem');
const canvasSolutionEl = document.getElementById('canvas-solution');

let wordsArray = [];
let seedWordsArray = [];
let wordSet = new Set();
let letterIndex = new Map();
const definitionsMap = new Map();
let defiCounter = 0;

/* Identique au parseur de main.js (voir son commentaire pour le détail du
 * format) : definitions.csv est produit par un script maison, pas un CSV
 * générique - découpage par lignes + indexOf/slice, pas d'automate. */
function loadDefinitions(text) {
  const n = text.length;
  let start = text.indexOf('\n') + 1;
  while (start > 0 && start < n) {
    let end = text.indexOf('\n', start);
    if (end === -1) end = n;
    let line = text.slice(start, end);
    start = end + 1;
    if (line.charCodeAt(line.length - 1) === 13) line = line.slice(0, -1);
    if (!line) continue;
    const comma = line.indexOf(',');
    if (comma <= 0) continue;
    const word = line.slice(0, comma);
    let def = line.slice(comma + 1);
    if (def.charCodeAt(0) === 34) {
      def = (def.charCodeAt(def.length - 1) === 34 ? def.slice(1, -1) : def.slice(1)).replace(/""/g, '"');
    }
    definitionsMap.set(word, def);
  }
}

/* ------------------------------------------------------------------ */
/* Rendu Canvas                                                         */
/* ------------------------------------------------------------------ */

const COLORS = {
  bg: '#1c130b',
  felt: '#1c4e28',
  feltLine: 'rgba(0, 0, 0, 0.35)',
  cellEmpty: 'rgba(255, 255, 255, 0.06)',
  cellCenter: 'rgba(255, 213, 79, 0.12)',
  bonusTW: 'rgba(196, 60, 48, 0.75)',
  bonusDW: 'rgba(214, 92, 130, 0.7)',
  bonusTL: 'rgba(46, 96, 168, 0.75)',
  bonusDL: 'rgba(78, 160, 186, 0.65)',
  bonusText: 'rgba(255, 255, 255, 0.85)',
  tileTop: '#e2c98f',
  tileBottom: '#cbaa65',
  tileBorder: 'rgba(120, 90, 40, 0.6)',
  tileLetter: '#241c13',
  solutionTop: '#fff0c0',
  solutionBottom: '#ffd54f',
  solutionBorder: '#8a5d2b',
  solutionLetter: '#241c13',
  gold: '#ffd54f',
  paper: '#f6ecd4',
  inkSoft: '#cabb9f',
};

const BONUS_FILL = { TW: COLORS.bonusTW, DW: COLORS.bonusDW, TL: COLORS.bonusTL, DL: COLORS.bonusDL };
const BONUS_LABEL = { TW: 'MT', DW: 'MD', TL: 'LT', DL: 'LD' };

function roundRect(ctx, x, y, w, h, r) {
  ctx.beginPath();
  ctx.moveTo(x + r, y);
  ctx.arcTo(x + w, y, x + w, y + h, r);
  ctx.arcTo(x + w, y + h, x, y + h, r);
  ctx.arcTo(x, y + h, x, y, r);
  ctx.arcTo(x, y, x + w, y, r);
  ctx.closePath();
}

function drawTileGradient(ctx, x, y, size, top, bottom, border, letter, letterColor) {
  const grad = ctx.createLinearGradient(x, y, x, y + size);
  grad.addColorStop(0, top);
  grad.addColorStop(0.7, bottom);
  roundRect(ctx, x, y, size, size, size * 0.12);
  ctx.fillStyle = grad;
  ctx.fill();
  ctx.lineWidth = Math.max(1, size * 0.03);
  ctx.strokeStyle = border;
  ctx.stroke();
  if (letter) {
    ctx.fillStyle = letterColor;
    ctx.font = `700 ${Math.round(size * 0.52)}px Georgia, "Times New Roman", serif`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(letter, x + size / 2, y + size / 2 + size * 0.03);
  }
}

/** Dessine la grille 15x15 dans le rectangle [originX, originY, cellSize].
 * `ghostMap` (Map "row,col" -> letter) optionnelle : surligne en doré les
 * cases de la solution proposée par Fanny (image "solution" uniquement). */
function drawBoard(ctx, board, originX, originY, cellSize, ghostMap) {
  const gap = Math.max(1, cellSize * 0.02);
  roundRect(ctx, originX - 4, originY - 4, cellSize * BOARD_SIZE + 8, cellSize * BOARD_SIZE + 8, 8);
  ctx.fillStyle = COLORS.feltLine;
  ctx.fill();

  for (let r = 0; r < BOARD_SIZE; r += 1) {
    for (let c = 0; c < BOARD_SIZE; c += 1) {
      const cell = board[r][c];
      const x = originX + c * cellSize + gap;
      const y = originY + r * cellSize + gap;
      const size = cellSize - gap * 2;
      const key = `${r},${c}`;
      const ghostLetter = ghostMap && ghostMap.get(key);

      if (cell.letter) {
        drawTileGradient(ctx, x, y, size, COLORS.tileTop, COLORS.tileBottom, COLORS.tileBorder, cell.letter, COLORS.tileLetter);
      } else if (ghostLetter) {
        drawTileGradient(ctx, x, y, size, COLORS.solutionTop, COLORS.solutionBottom, COLORS.gold, ghostLetter, COLORS.solutionLetter);
      } else {
        roundRect(ctx, x, y, size, size, size * 0.08);
        if (cell.bonus) {
          ctx.fillStyle = BONUS_FILL[cell.bonus];
        } else if (cell.isCenter) {
          ctx.fillStyle = COLORS.cellCenter;
        } else {
          ctx.fillStyle = COLORS.cellEmpty;
        }
        ctx.fill();
        if (cell.bonus) {
          ctx.fillStyle = BONUS_LABEL_COLOR(cell.bonus);
          ctx.font = `700 ${Math.round(size * 0.28)}px system-ui, sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText(BONUS_LABEL[cell.bonus], x + size / 2, y + size / 2);
        } else if (cell.isCenter) {
          ctx.fillStyle = 'rgba(255, 213, 79, 0.7)';
          ctx.font = `${Math.round(size * 0.55)}px system-ui, sans-serif`;
          ctx.textAlign = 'center';
          ctx.textBaseline = 'middle';
          ctx.fillText('★', x + size / 2, y + size / 2);
        }
      }
    }
  }
}
function BONUS_LABEL_COLOR() { return COLORS.bonusText; }

function drawRack(ctx, rack, centerX, y, tileSize) {
  const gap = tileSize * 0.14;
  const totalW = rack.length * tileSize + (rack.length - 1) * gap;
  let x = centerX - totalW / 2;
  for (const tile of rack) {
    const letter = tile.isBlank ? (tile.assignedLetter || '★') : tile.letter;
    drawTileGradient(ctx, x, y, tileSize, COLORS.tileTop, COLORS.tileBottom, COLORS.tileBorder, letter, tile.isBlank ? '#8a5d2b' : COLORS.tileLetter);
    ctx.fillStyle = 'rgba(36, 28, 19, 0.6)';
    ctx.font = `700 ${Math.round(tileSize * 0.2)}px system-ui, sans-serif`;
    ctx.textAlign = 'right';
    ctx.textBaseline = 'alphabetic';
    ctx.fillText(String(tile.value), x + tileSize - tileSize * 0.08, y + tileSize - tileSize * 0.06);
    x += tileSize + gap;
  }
}

function wrapText(ctx, text, maxWidth) {
  const words = text.split(' ');
  const lines = [];
  let current = '';
  for (const word of words) {
    const candidate = current ? `${current} ${word}` : word;
    if (ctx.measureText(candidate).width <= maxWidth) {
      current = candidate;
    } else {
      if (current) lines.push(current);
      current = word;
    }
  }
  if (current) lines.push(current);
  return lines;
}

/* Reconstruit tous les mots (2 lettres ou plus) présents sur la grille en
 * balayant chaque case remplie et en étendant à gauche/droite puis
 * haut/bas - dédoublonné, ordre alphabétique. Fonctionne aussi bien sur
 * game.board (avec .value) que sur state.board (sans), seul .letter est lu. */
function collectBoardWords(board) {
  const letterAt = (r, c) => (board[r] && board[r][c] ? board[r][c].letter : null);
  const found = new Set();
  for (let r = 0; r < board.length; r += 1) {
    for (let c = 0; c < board[r].length; c += 1) {
      if (!letterAt(r, c)) continue;
      if (!letterAt(r, c - 1)) {
        let text = ''; let cc = c;
        while (letterAt(r, cc)) { text += letterAt(r, cc); cc += 1; }
        if (text.length >= 2) found.add(text);
      }
      if (!letterAt(r - 1, c)) {
        let text = ''; let rr = r;
        while (letterAt(rr, c)) { text += letterAt(rr, c); rr += 1; }
        if (text.length >= 2) found.add(text);
      }
    }
  }
  return [...found].sort();
}

/* Empile un titre + une liste "MOT — définition." (mots wrappés) à partir
 * de y, en s'arrêtant proprement (ligne "… encore N mot(s)") si le contenu
 * dépasserait `maxY` - nécessaire maintenant que le canvas est en taille
 * FIXE (format "story" plein écran smartphone, cf. CANVAS_H) plutôt que
 * dimensionné dynamiquement au contenu. */
const MAX_WORDS_SHOWN = 8;

function drawWordList(ctx, title, words, x, y, maxWidth, maxY) {
  ctx.textAlign = 'left';
  ctx.fillStyle = COLORS.gold;
  ctx.font = '700 26px Georgia, "Times New Roman", serif';
  ctx.fillText(title, x, y);
  y += 34;
  ctx.fillStyle = COLORS.paper;
  const shown = words.slice(0, MAX_WORDS_SHOWN);
  for (let i = 0; i < shown.length; i += 1) {
    const word = shown[i];
    const definition = definitionsMap.get(word);
    const text = definition ? `${word} — ${definition}` : `${word} — définition non disponible.`;
    ctx.font = '400 22px system-ui, sans-serif';
    const wrapped = wrapText(ctx, text, maxWidth).slice(0, 3);
    for (const line of wrapped) {
      if (y + 30 > maxY) {
        const remaining = words.length - i;
        if (remaining > 0) {
          ctx.fillStyle = COLORS.inkSoft;
          ctx.font = 'italic 20px system-ui, sans-serif';
          ctx.fillText(`… et ${remaining} mot(s) de plus`, x, y + 28);
        }
        ctx.textAlign = 'center';
        return;
      }
      y += 30;
      ctx.fillText(line, x, y);
    }
  }
  ctx.textAlign = 'center';
}

// Format "story" (Instagram/TikTok/Snapchat) : plein écran smartphone,
// portrait 9:16, HD. Taille FIXE (pas dépendante du contenu) - le felt de
// fond remplit tout le cadre quelle que soit la longueur des définitions ;
// drawWordList s'arrête proprement (voir maxY) plutôt que de déborder.
const CANVAS_W = 1080;
const CANVAS_H = 1920;

const HEADER_H = 170;
const RACK_GAP_TOP = 30;
const RACK_GAP_BOTTOM = 50;
const FOOTER_H = 60;

/** Compose une image complète (fond + en-tête + grille + chevalet + liste
 * de mots/définitions) sur `canvas`, en 1080x1920 fixe. `mode` = 'problem'
 * (mots déjà sur la grille de départ) ou 'solution' (le/les meilleur(s)
 * coup(s) de Fanny, mis en évidence sur la grille + listés avec leur
 * définition - TOUS les coups à égalité au meilleur score, pas seulement
 * le premier trouvé). */
function renderChallenge(canvas, { board, rack, defiNumber, mode, bestMoves, boardWords }) {
  canvas.width = CANVAS_W;
  canvas.height = CANVAS_H;
  const ctx = canvas.getContext('2d');
  const W = CANVAS_W;
  const H = CANVAS_H;
  const maxY = H - FOOTER_H - 10;

  ctx.fillStyle = COLORS.bg;
  ctx.fillRect(0, 0, W, H);
  ctx.fillStyle = COLORS.felt;
  ctx.fillRect(0, 150, W, H - 150);

  ctx.textAlign = 'center';
  ctx.fillStyle = COLORS.inkSoft;
  ctx.font = '600 24px system-ui, sans-serif';
  ctx.fillText('FANNY PÉTANQUE WORLD TOUR', W / 2, 46);
  ctx.fillStyle = COLORS.gold;
  ctx.font = '700 44px Georgia, "Times New Roman", serif';
  ctx.fillText(`DÉFI SCRABBLE #${defiNumber}`, W / 2, 96);
  ctx.fillStyle = COLORS.paper;
  ctx.font = '400 22px system-ui, sans-serif';
  ctx.fillText(
    mode === 'problem' ? 'Sept lettres, une grille déjà entamée. À vous de jouer !' : 'La solution de Fanny 👇',
    W / 2, 130,
  );

  const boardSize = W - 100;
  const cellSize = boardSize / BOARD_SIZE;
  const tileSize = Math.min(cellSize * 1.15, 70);
  const boardX = (W - boardSize) / 2;
  const boardY = HEADER_H;

  let ghostMap = null;
  if (mode === 'solution' && bestMoves.length) {
    // Toutes les cases à égalité au meilleur score partagent en général la
    // même lettre d'ancrage (même case de départ) mais peuvent diverger
    // ensuite : on superpose les placements de TOUS les coups à égalité
    // (une case gagnée par un coup et écrasée par un autre montre alors le
    // dernier - rare en pratique, les coups à égalité partagent la plupart
    // de leurs cases).
    ghostMap = new Map();
    for (const m of bestMoves) for (const p of m.placements) ghostMap.set(`${p.row},${p.col}`, p.letter);
  }
  drawBoard(ctx, board, boardX, boardY, cellSize, ghostMap);

  const rackY = boardY + boardSize + RACK_GAP_TOP;
  drawRack(ctx, rack, W / 2, rackY, tileSize);

  let y = rackY + tileSize + RACK_GAP_BOTTOM;
  if (mode === 'solution') {
    if (bestMoves.length) {
      const bingoTag = bestMoves[0].bingo ? '  —  SCRABBLE !' : '';
      const wordsLine = bestMoves.map((m) => m.word).join(', ');
      ctx.fillStyle = COLORS.gold;
      ctx.font = '700 30px Georgia, "Times New Roman", serif';
      const scoreLines = wrapText(ctx, `${wordsLine} (${bestMoves[0].score} pts)${bingoTag}`, W - 120);
      for (const line of scoreLines) { y += 36; ctx.fillText(line, W / 2, y); }
      y += 36;
      drawWordList(ctx, 'Définition(s) du top', bestMoves.map((m) => m.word), 60, y, W - 120, maxY);
    } else {
      ctx.fillStyle = COLORS.inkSoft;
      ctx.font = 'italic 22px system-ui, sans-serif';
      ctx.fillText('Aucun coup meilleur trouvé pour cette grille (rare).', W / 2, y + 20);
    }
  } else {
    drawWordList(ctx, 'Mots déjà sur la grille', boardWords, 60, y, W - 120, maxY);
  }

  ctx.fillStyle = 'rgba(202, 187, 159, 0.6)';
  ctx.font = '400 16px system-ui, sans-serif';
  ctx.textAlign = 'center';
  ctx.fillText('guiraudjb.github.io/Arducible_Fanny_Petanque_World_Tour', W / 2, H - 20);
}

/* ------------------------------------------------------------------ */
/* Génération d'un défi (grille + chevalet + meilleur coup)             */
/* ------------------------------------------------------------------ */

function generateChallenge() {
  const game = new Scrabble({ startingBankroll: 500 });
  // La mise ne sert à rien ici (aucune manche n'est réellement jouée),
  // juste besoin d'un board+rack tirés au sort par startRound.
  const result = game.startRound(10, wordsArray, seedWordsArray);
  if (!result.ok) return null;
  const state = game.getState();
  // Important : findBestMove a besoin de cell.value (valeur en points de
  // chaque lettre déjà posée) pour scorer les mots croisés existants -
  // state.board (issu de getState()) ne l'expose PAS (juste letter/bonus/
  // isCenter, suffisant pour l'affichage du jeu). game.board (l'état
  // interne réel, identique à game.seedBoard tant qu'aucun coup n'a été
  // joué) le conserve : sans ça, scoreWords additionne des `undefined` et
  // le score final devient NaN (affiché comme "null"/"-1" une fois passé
  // par JSON/gabarit).
  const best = findBestMove({ boardCells: game.board, rack: state.rack, letterIndex, wordSet });
  // TOUS les coups à égalité au meilleur score (pas seulement moves[0]) -
  // demande explicite : la solution de Fanny doit toujours montrer le/les
  // top, comme le fait le jeu lui-même ("3 meilleurs coups à X pts : ...").
  const bestMoves = best
    ? best.moves.map((m) => ({ word: m.word, score: best.score, bingo: m.bingo, placements: m.placements }))
    : [];
  const boardWords = collectBoardWords(game.board);
  return { board: state.board, rack: state.rack, bestMoves, boardWords };
}

/* ------------------------------------------------------------------ */
/* Export JPEG + téléchargement                                        */
/* ------------------------------------------------------------------ */

function canvasToJpegBlob(canvas) {
  return new Promise((resolve) => canvas.toBlob(resolve, 'image/jpeg', 0.92));
}

function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 4000);
}

function pad2(n) { return String(n).padStart(2, '0'); }

/* ------------------------------------------------------------------ */
/* Actions boutons                                                      */
/* ------------------------------------------------------------------ */

function previewOne() {
  const challenge = generateChallenge();
  if (!challenge) { statusLineEl.textContent = 'Impossible de générer une grille (dictionnaire non prêt ?).'; return; }
  defiCounter += 1;
  renderChallenge(canvasProblemEl, { ...challenge, defiNumber: defiCounter, mode: 'problem' });
  renderChallenge(canvasSolutionEl, { ...challenge, defiNumber: defiCounter, mode: 'solution' });
  statusLineEl.textContent = challenge.bestMoves.length
    ? `Défi #${defiCounter} — solution : ${challenge.bestMoves.map((m) => m.word).join(', ')} (${challenge.bestMoves[0].score} pts)`
    : `Défi #${defiCounter} — aucun coup meilleur trouvé (rare).`;
}

/* Chrome bloque les téléchargements automatiques multiples déclenchés par
 * script après le premier (garde-fou anti-spam) : sans intervention de
 * l'utilisateur à chaque fichier, un lot de N défis (2N fichiers) ne
 * passerait pas. La File System Access API (showDirectoryPicker) contourne
 * ça proprement : une SEULE autorisation ("choisir un dossier"), puis
 * écriture directe des fichiers dedans, sans repasser par le mécanisme de
 * téléchargement du navigateur. Repli sur <a download> + délais (marche
 * pour un petit lot, ou navigateurs sans cette API) si indisponible/refusée. */
async function pickOutputDirectory() {
  if (!('showDirectoryPicker' in window)) return null;
  try {
    return await window.showDirectoryPicker({ id: 'defi-scrabble-batch', mode: 'readwrite' });
  } catch (err) {
    if (err && err.name === 'AbortError') return undefined; // l'utilisateur a annulé
    return null;
  }
}

async function writeFileInDir(dirHandle, filename, blob) {
  const fileHandle = await dirHandle.getFileHandle(filename, { create: true });
  const writable = await fileHandle.createWritable();
  await writable.write(blob);
  await writable.close();
}

async function downloadBatch() {
  const n = Math.max(1, Math.min(200, Number(batchCountEl.value) || 1));
  btnBatch.disabled = true;
  btnPreview.disabled = true;

  const dirHandle = await pickOutputDirectory();
  if (dirHandle === undefined) { // annulé par l'utilisateur
    btnBatch.disabled = false;
    btnPreview.disabled = false;
    progressLineEl.textContent = '';
    return;
  }
  progressLineEl.textContent = dirHandle
    ? `Écriture dans "${dirHandle.name}"…`
    : 'Ce navigateur ne permet pas de choisir un dossier : téléchargement classique (autorisez les téléchargements multiples si demandé).';

  for (let i = 1; i <= n; i += 1) {
    const challenge = generateChallenge();
    if (!challenge) { i -= 1; continue; }
    defiCounter += 1;
    const num = defiCounter;
    // Dessine directement dans les canvas visibles (aperçu du lot en cours)
    // et exporte depuis ceux-ci - inutile de dessiner deux fois.
    renderChallenge(canvasProblemEl, { ...challenge, defiNumber: num, mode: 'problem' });
    renderChallenge(canvasSolutionEl, { ...challenge, defiNumber: num, mode: 'solution' });

    const [blobA, blobB] = await Promise.all([canvasToJpegBlob(canvasProblemEl), canvasToJpegBlob(canvasSolutionEl)]);
    const nameA = `defi-scrabble-${pad2(num)}-probleme.jpg`;
    const nameB = `defi-scrabble-${pad2(num)}-solution.jpg`;
    if (dirHandle) {
      await writeFileInDir(dirHandle, nameA, blobA);
      await writeFileInDir(dirHandle, nameB, blobB);
    } else {
      downloadBlob(blobA, nameA);
      // Délai entre les deux téléchargements d'un même défi, et entre deux
      // défis, pour rester sous la limite anti-spam de Chrome (repli sans
      // dossier choisi uniquement).
      await new Promise((r) => setTimeout(r, 250));
      downloadBlob(blobB, nameB);
      await new Promise((r) => setTimeout(r, 350));
    }
    progressLineEl.textContent = `${dirHandle ? 'Écrit' : 'Téléchargé'} ${i} / ${n}…`;
  }

  progressLineEl.textContent = `Terminé : ${n} défis ${dirHandle ? 'écrits dans ' + dirHandle.name : 'téléchargés'} (${n * 2} images).`;
  btnBatch.disabled = false;
  btnPreview.disabled = false;
}

btnPreview.addEventListener('click', previewOne);
btnBatch.addEventListener('click', downloadBatch);
btnPreview.disabled = true;
btnBatch.disabled = true;

Promise.all([
  fetch(WORDS_URL).then((r) => r.text()),
  fetch(DEFINITIONS_URL).then((r) => r.text()),
]).then(([wordsText, definitionsText]) => {
  wordsArray = wordsText.split('\n').filter(Boolean);
  wordSet = new Set(wordsArray);
  loadDefinitions(definitionsText);
  seedWordsArray = definitionsMap.size > 0
    ? wordsArray.filter((w) => definitionsMap.has(w))
    : wordsArray;
  statusLineEl.textContent = 'Construction de l’index du dictionnaire…';
  // Différé (setTimeout 0) pour laisser le statut ci-dessus s'afficher avant
  // le calcul synchrone (~1s sur ~645k mots).
  setTimeout(() => {
    letterIndex = buildLetterIndex(wordsArray);
    btnPreview.disabled = false;
    btnBatch.disabled = false;
    statusLineEl.textContent = '';
    previewOne();
  }, 30);
}).catch((err) => {
  statusLineEl.textContent = `Impossible de charger le dictionnaire (${err}).`;
});
