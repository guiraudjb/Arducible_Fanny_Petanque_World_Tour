import { SUITS, SUIT_SYMBOLS, SUIT_COLORS, RANKS, JOKER_COLORS } from './constants.js';

/**
 * Représente une carte à jouer, standard ou joker.
 */
export class Card {
  /**
   * @param {string} rank - Un élément de RANKS ('A'..'K'), ignoré si isJoker.
   * @param {string} suit - Un élément de SUITS, ignoré si isJoker.
   * @param {{isJoker?: boolean, jokerColor?: string}} [options]
   */
  constructor(rank, suit, { isJoker = false, jokerColor = JOKER_COLORS.BLACK } = {}) {
    if (isJoker) {
      this.isJoker = true;
      this.rank = null;
      this.suit = null;
      this.jokerColor = jokerColor;
    } else {
      if (!RANKS.includes(rank)) {
        throw new Error(`Rang invalide: ${rank}`);
      }
      if (!Object.values(SUITS).includes(suit)) {
        throw new Error(`Couleur (suit) invalide: ${suit}`);
      }
      this.isJoker = false;
      this.rank = rank;
      this.suit = suit;
      this.jokerColor = null;
    }
  }

  static joker(color = JOKER_COLORS.BLACK) {
    return new Card(null, null, { isJoker: true, jokerColor: color });
  }

  /** Couleur d'affichage ('red' | 'black') */
  get color() {
    return this.isJoker ? this.jokerColor : SUIT_COLORS[this.suit];
  }

  /** Symbole de la couleur (♥ ♦ ♣ ♠), vide pour un joker */
  get suitSymbol() {
    return this.isJoker ? '' : SUIT_SYMBOLS[this.suit];
  }

  /**
   * Valeur numérique de la carte pour les calculs de jeu.
   * @param {{aceHigh?: boolean, jokerValue?: number}} [options]
   */
  value({ aceHigh = false, jokerValue = 0 } = {}) {
    if (this.isJoker) return jokerValue;
    const index = RANKS.indexOf(this.rank); // 0 = 'A'
    if (this.rank === 'A') return aceHigh ? 14 : 1;
    return index + 1; // '2'..'10' => 2..10, 'J'=>11, 'Q'=>12, 'K'=>13
  }

  /**
   * Nom de fichier sprite conventionnel: "{rank}-{suit}.png" ou "joker-{color}.png".
   * Le thème visuel (contenu des images) est libre ; seule cette convention
   * de nommage doit être respectée dans le dossier de sprites.
   */
  get spriteFile() {
    if (this.isJoker) {
      return `joker-${this.jokerColor}.png`;
    }
    return `${this.rank}-${this.suit}.png`;
  }

  equals(other) {
    if (!(other instanceof Card)) return false;
    if (this.isJoker || other.isJoker) {
      return this.isJoker === other.isJoker && this.jokerColor === other.jokerColor;
    }
    return this.rank === other.rank && this.suit === other.suit;
  }

  toString() {
    if (this.isJoker) {
      return `Joker (${this.jokerColor})`;
    }
    return `${this.rank}${this.suitSymbol}`;
  }
}
