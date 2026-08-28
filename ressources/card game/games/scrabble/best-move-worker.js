/* Web Worker (module) : calcule le meilleur coup possible d'une grille de
 * départ PENDANT que le joueur réfléchit (les 90 s de la manche), pour que
 * l'écran de résultat l'affiche sans attente.
 *
 * findBestMove balaie le dictionnaire complet (~10-15 s, synchrone) : hors
 * du thread principal, ça ne gèle rien. Ses entrées (seedBoard + chevalet
 * d'origine) sont figées dès startRound, donc le calcul est entièrement
 * parallélisable. Orchestré par games/scrabble/main.js (repli synchrone via
 * Scrabble.computeBestMove si les module workers ne sont pas disponibles).
 *
 * Messages :
 *   <- { id, seedBoard, rack }   (une manche)
 *   -> { id, best }              (best = retour de findBestMove, ou null)
 */
import { findBestMove, buildLetterIndex } from '../../src/games/scrabble/engine.js';

const WORDS_URL = new URL('../../assets/scrabble/mots.txt', import.meta.url);

let ready = null;
let letterIndex = null;
let wordSet = null;

/** Charge le dictionnaire et construit l'index une seule fois. Lancé dès la
 * création du worker pour être prêt bien avant la fin de la première manche. */
function init() {
  if (!ready) {
    ready = fetch(WORDS_URL)
      .then((r) => r.text())
      .then((text) => {
        const words = text.split('\n').filter(Boolean);
        wordSet = new Set(words);
        letterIndex = buildLetterIndex(words);
      });
  }
  return ready;
}
init();

self.onmessage = async (e) => {
  const { id, seedBoard, rack } = e.data;
  try {
    await init();
    const best = findBestMove({ boardCells: seedBoard, rack, letterIndex, wordSet });
    self.postMessage({ id, best });
  } catch (err) {
    self.postMessage({ id, best: null, error: String(err) });
  }
};
