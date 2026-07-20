import { SUITS, RANKS, JOKER_COLORS } from './constants.js';
import { Card } from './Card.js';

/**
 * Paquet générique de 54 cartes (52 standard + 2 jokers).
 * Indépendant de toute règle de jeu particulière.
 */
export class Deck {
  /**
   * @param {{jokers?: number}} [options] - Nombre de jokers à inclure (0, 1 ou 2). Défaut: 2.
   */
  constructor({ jokers = 2 } = {}) {
    this.jokers = jokers;
    this.cards = [];
    this._discard = [];
    this.reset();
  }

  /** Reconstruit un paquet complet et trié (52 + jokers), retire la défausse. */
  reset() {
    this.cards = [];
    for (const suit of Object.values(SUITS)) {
      for (const rank of RANKS) {
        this.cards.push(new Card(rank, suit));
      }
    }
    for (let i = 0; i < this.jokers; i += 1) {
      this.cards.push(Card.joker(i === 0 ? JOKER_COLORS.RED : JOKER_COLORS.BLACK));
    }
    this._discard = [];
    return this;
  }

  /** Mélange le paquet en place (Fisher-Yates). */
  shuffle() {
    for (let i = this.cards.length - 1; i > 0; i -= 1) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.cards[i], this.cards[j]] = [this.cards[j], this.cards[i]];
    }
    return this;
  }

  /** Nombre de cartes restantes à piocher. */
  get remaining() {
    return this.cards.length;
  }

  /**
   * Pioche une ou plusieurs cartes du dessus du paquet.
   * @param {number} count
   * @returns {Card|Card[]} une Card si count === 1, sinon un tableau.
   */
  draw(count = 1) {
    if (count > this.cards.length) {
      throw new Error(`Impossible de piocher ${count} carte(s), il n'en reste que ${this.cards.length}.`);
    }
    const drawn = this.cards.splice(0, count);
    return count === 1 ? drawn[0] : drawn;
  }

  /**
   * Distribue des cartes en plusieurs mains, à tour de rôle (comme une vraie distribution).
   * @param {number} numHands
   * @param {number} cardsPerHand
   * @returns {Card[][]} un tableau de mains
   */
  deal(numHands, cardsPerHand) {
    const total = numHands * cardsPerHand;
    if (total > this.cards.length) {
      throw new Error(`Impossible de distribuer ${total} cartes, il n'en reste que ${this.cards.length}.`);
    }
    const hands = Array.from({ length: numHands }, () => []);
    for (let round = 0; round < cardsPerHand; round += 1) {
      for (let hand = 0; hand < numHands; hand += 1) {
        hands[hand].push(this.draw(1));
      }
    }
    return hands;
  }

  /** Envoie des cartes à la défausse. */
  discard(cards) {
    const list = Array.isArray(cards) ? cards : [cards];
    this._discard.push(...list);
    return this;
  }

  get discardPile() {
    return this._discard;
  }

  /** Remet la défausse dans le paquet (sans mélanger). */
  reclaimDiscard() {
    this.cards.push(...this._discard);
    this._discard = [];
    return this;
  }
}
