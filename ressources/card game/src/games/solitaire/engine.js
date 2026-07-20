import { Deck, RANKS, SUITS } from '../../cards/index.js';

const TABLEAU_COLUMNS = 7;
const FOUNDATION_SUITS = Object.values(SUITS);

function rankIndex(card) {
  return RANKS.indexOf(card.rank);
}

function oppositeColor(a, b) {
  return a.color !== b.color;
}

/**
 * Moteur du Klondike (solitaire classique), indépendant du rendu.
 * Utilise un paquet standard de 52 cartes (sans jokers).
 */
export class Solitaire {
  constructor({ drawCount = 1 } = {}) {
    this.drawCount = drawCount;
    this.newGame();
  }

  newGame() {
    const deck = new Deck({ jokers: 0 });
    deck.shuffle();

    this.tableau = [];
    for (let col = 0; col < TABLEAU_COLUMNS; col += 1) {
      const pile = [];
      for (let row = 0; row <= col; row += 1) {
        const card = deck.draw(1);
        pile.push({ card, faceUp: row === col });
      }
      this.tableau.push(pile);
    }

    this.stock = [...deck.cards];
    this.waste = [];
    this.foundations = {};
    for (const suit of FOUNDATION_SUITS) {
      this.foundations[suit] = [];
    }
    this.moves = 0;
  }

  get isStockEmpty() {
    return this.stock.length === 0;
  }

  /** Pioche (ou recycle la défausse si le talon est vide). */
  drawFromStock() {
    if (this.stock.length === 0) {
      if (this.waste.length === 0) return { ok: false, reason: 'empty' };
      this.stock = this.waste.slice().reverse();
      this.waste = [];
      return { ok: true, recycled: true };
    }
    const count = Math.min(this.drawCount, this.stock.length);
    const drawn = this.stock.splice(this.stock.length - count, count);
    this.waste.push(...drawn);
    this.moves += 1;
    return { ok: true };
  }

  /**
   * Vérifie que pile[cardIndex..fin] forme une séquence face visible
   * valide (rangs décroissants, couleurs alternées) et renvoie cette
   * séquence, ou null si le déplacement n'est pas autorisé.
   */
  getMovableSequence(pileIndex, cardIndex) {
    const pile = this.tableau[pileIndex];
    if (!pile || cardIndex < 0 || cardIndex >= pile.length) return null;
    const seq = pile.slice(cardIndex);
    if (!seq.every((entry) => entry.faceUp)) return null;
    for (let i = 0; i < seq.length - 1; i += 1) {
      const current = seq[i].card;
      const next = seq[i + 1].card;
      if (rankIndex(current) !== rankIndex(next) + 1 || !oppositeColor(current, next)) {
        return null;
      }
    }
    return seq;
  }

  canStackOnTableau(card, targetTopCard) {
    if (!targetTopCard) return card.rank === 'K';
    return rankIndex(targetTopCard) === rankIndex(card) + 1 && oppositeColor(targetTopCard, card);
  }

  canStackOnFoundation(card, foundationPile) {
    if (foundationPile.length === 0) return card.rank === 'A';
    const top = foundationPile[foundationPile.length - 1];
    return top.suit === card.suit && rankIndex(top) + 1 === rankIndex(card);
  }

  _flipNewTop(pileIndex) {
    const pile = this.tableau[pileIndex];
    if (pile.length > 0) {
      pile[pile.length - 1].faceUp = true;
    }
  }

  moveTableauToTableau(fromPile, cardIndex, toPile) {
    if (fromPile === toPile) return { ok: false, reason: 'same-pile' };
    const seq = this.getMovableSequence(fromPile, cardIndex);
    if (!seq) return { ok: false, reason: 'invalid-sequence' };

    const target = this.tableau[toPile];
    const targetTop = target.length ? target[target.length - 1].card : null;
    if (!this.canStackOnTableau(seq[0].card, targetTop)) {
      return { ok: false, reason: 'illegal-move' };
    }

    this.tableau[fromPile].splice(cardIndex);
    target.push(...seq);
    this._flipNewTop(fromPile);
    this.moves += 1;
    return { ok: true };
  }

  moveTableauToFoundation(pileIndex) {
    const pile = this.tableau[pileIndex];
    if (!pile || pile.length === 0) return { ok: false, reason: 'empty' };
    const top = pile[pile.length - 1];
    if (!top.faceUp) return { ok: false, reason: 'face-down' };
    const foundation = this.foundations[top.card.suit];
    if (!this.canStackOnFoundation(top.card, foundation)) {
      return { ok: false, reason: 'illegal-move' };
    }
    pile.pop();
    foundation.push(top.card);
    this._flipNewTop(pileIndex);
    this.moves += 1;
    return { ok: true };
  }

  moveWasteToFoundation() {
    if (this.waste.length === 0) return { ok: false, reason: 'empty' };
    const card = this.waste[this.waste.length - 1];
    const foundation = this.foundations[card.suit];
    if (!this.canStackOnFoundation(card, foundation)) {
      return { ok: false, reason: 'illegal-move' };
    }
    this.waste.pop();
    foundation.push(card);
    this.moves += 1;
    return { ok: true };
  }

  moveWasteToTableau(toPile) {
    if (this.waste.length === 0) return { ok: false, reason: 'empty' };
    const card = this.waste[this.waste.length - 1];
    const target = this.tableau[toPile];
    const targetTop = target.length ? target[target.length - 1].card : null;
    if (!this.canStackOnTableau(card, targetTop)) {
      return { ok: false, reason: 'illegal-move' };
    }
    this.waste.pop();
    target.push({ card, faceUp: true });
    this.moves += 1;
    return { ok: true };
  }

  get isWon() {
    return FOUNDATION_SUITS.every((suit) => this.foundations[suit].length === RANKS.length);
  }

  getState() {
    return {
      moves: this.moves,
      stockCount: this.stock.length,
      wasteTop: this.waste.length ? this.waste[this.waste.length - 1] : null,
      foundations: FOUNDATION_SUITS.map((suit) => ({
        suit,
        topCard: this.foundations[suit].length
          ? this.foundations[suit][this.foundations[suit].length - 1]
          : null,
        count: this.foundations[suit].length,
      })),
      tableau: this.tableau.map((pile) => pile.map((entry) => ({ card: entry.card, faceUp: entry.faceUp }))),
      isWon: this.isWon,
    };
  }
}
