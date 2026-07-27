import { Deck } from '../../cards/index.js';
import { rankHand, compareHands, HAND_CATEGORY_NAMES } from './handRank.js';

export const OUTFIT_STAGE_COUNT = 6; // 0 (tenue complète) .. 5 (lingerie, stade final)
export { HAND_CATEGORY_NAMES };

/**
 * Heuristique de tirage simple pour l'IA : conserve une main déjà faite
 * (brelan ou mieux), sinon garde ses paires, sinon cherche un tirage
 * couleur/quinte à 4 cartes, sinon ne garde que sa carte la plus haute.
 */
export function decideAIHolds(hand) {
  const { category } = rankHand(hand);
  const held = [false, false, false, false, false];

  if (['straight', 'flush', 'full-house', 'four-of-a-kind', 'straight-flush', 'royal-flush'].includes(category)) {
    return [true, true, true, true, true];
  }

  const valueOf = (card) => ({ A: 14, K: 13, Q: 12, J: 11 }[card.rank] || Number(card.rank));

  if (category === 'three-of-a-kind' || category === 'two-pair' || category === 'one-pair') {
    const counts = new Map();
    hand.forEach((card) => {
      const v = valueOf(card);
      counts.set(v, (counts.get(v) || 0) + 1);
    });
    hand.forEach((card, i) => {
      if (counts.get(valueOf(card)) >= 2) held[i] = true;
    });
    return held;
  }

  const suitCounts = new Map();
  hand.forEach((card) => suitCounts.set(card.suit, (suitCounts.get(card.suit) || 0) + 1));
  const [flushSuit, flushCount] = [...suitCounts.entries()].sort((a, b) => b[1] - a[1])[0];
  if (flushCount === 4) {
    hand.forEach((card, i) => { if (card.suit === flushSuit) held[i] = true; });
    return held;
  }

  const sortedByValueDesc = hand
    .map((card, i) => ({ i, v: valueOf(card) }))
    .sort((a, b) => b.v - a.v);
  held[sortedByValueDesc[0].i] = true;
  return held;
}

function outcomeMessage(outcome, stageAdvanced) {
  if (outcome === 'player-win') {
    return stageAdvanced
      ? "Vous gagnez ! L'adversaire change de tenue."
      : 'Vous gagnez ! (déjà à la tenue la plus légère)';
  }
  if (outcome === 'ai-win') return "L'IA gagne cette manche.";
  return 'Égalité : aucun changement.';
}

/**
 * Strip poker (5-card draw, joueur contre IA). Sans mise : l'enjeu est la
 * tenue de l'adversaire, qui progresse d'un stade (parmi 6, de la tenue
 * complète à la lingerie) à chaque manche perdue par l'IA. La progression
 * s'arrête au dernier stade existant, jamais au-delà.
 */
export class StripPoker {
  constructor() {
    this.newSession();
  }

  newSession() {
    this.outfitStage = 0;
    this.wins = 0;
    this.losses = 0;
    this.ties = 0;
    this.phase = 'pre-deal'; // 'pre-deal' | 'holding' | 'result'
    this.playerHand = [];
    this.aiHand = [];
    this.held = [false, false, false, false, false];
    this.result = null;
    this.message = '';
    this.playerRank = null;
    this.aiRank = null;
    this.deck = null;
  }

  deal() {
    if (this.phase !== 'pre-deal') return { ok: false, reason: 'wrong-phase' };
    this.deck = new Deck({ jokers: 0 });
    this.deck.shuffle();
    this.playerHand = this.deck.draw(5);
    this.aiHand = this.deck.draw(5);
    this.held = [false, false, false, false, false];
    this.result = null;
    this.playerRank = null;
    this.aiRank = null;
    this.message = '';
    this.phase = 'holding';
    return { ok: true };
  }

  toggleHold(index) {
    if (this.phase !== 'holding') return { ok: false, reason: 'wrong-phase' };
    if (index < 0 || index >= this.playerHand.length) return { ok: false, reason: 'bad-index' };
    this.held[index] = !this.held[index];
    return { ok: true };
  }

  drawAndShowdown() {
    if (this.phase !== 'holding') return { ok: false, reason: 'wrong-phase' };

    for (let i = 0; i < this.playerHand.length; i += 1) {
      if (!this.held[i]) this.playerHand[i] = this.deck.draw(1);
    }

    const aiHolds = decideAIHolds(this.aiHand);
    for (let i = 0; i < this.aiHand.length; i += 1) {
      if (!aiHolds[i]) this.aiHand[i] = this.deck.draw(1);
    }

    this.playerRank = rankHand(this.playerHand);
    this.aiRank = rankHand(this.aiHand);
    const cmp = compareHands(this.playerHand, this.aiHand);

    let stageAdvanced = false;
    if (cmp > 0) {
      this.result = 'player-win';
      this.wins += 1;
      if (this.outfitStage < OUTFIT_STAGE_COUNT - 1) {
        this.outfitStage += 1;
        stageAdvanced = true;
      }
    } else if (cmp < 0) {
      this.result = 'ai-win';
      this.losses += 1;
    } else {
      this.result = 'tie';
      this.ties += 1;
    }

    this.message = outcomeMessage(this.result, stageAdvanced);
    this.phase = 'result';
    return { ok: true };
  }

  nextRound() {
    if (this.phase !== 'result') return { ok: false, reason: 'wrong-phase' };
    this.phase = 'pre-deal';
    this.playerHand = [];
    this.aiHand = [];
    this.held = [false, false, false, false, false];
    this.result = null;
    this.message = '';
    return { ok: true };
  }

  get isFinalStage() {
    return this.outfitStage === OUTFIT_STAGE_COUNT - 1;
  }

  getState() {
    const revealed = this.phase === 'result';
    return {
      phase: this.phase,
      outfitStage: this.outfitStage,
      isFinalStage: this.isFinalStage,
      wins: this.wins,
      losses: this.losses,
      ties: this.ties,
      message: this.message,
      result: this.result,
      playerHand: this.playerHand.map((card, i) => ({ card, held: this.held[i] })),
      aiHand: this.aiHand.map((card) => ({ card, hidden: !revealed })),
      playerHandName: this.playerRank ? HAND_CATEGORY_NAMES[this.playerRank.category] : null,
      aiHandName: this.aiRank ? HAND_CATEGORY_NAMES[this.aiRank.category] : null,
    };
  }
}
