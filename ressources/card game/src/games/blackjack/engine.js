import { Deck } from '../../cards/index.js';

const DEALER_STAND_THRESHOLD = 17;
const BLACKJACK = 21;

function cardPoints(card) {
  if (card.rank === 'A') return 11;
  if (['K', 'Q', 'J'].includes(card.rank)) return 10;
  return Number(card.rank);
}

/** Calcule le meilleur total d'une main en gérant les As (11 ou 1). */
export function bestTotal(cards) {
  let total = 0;
  let aces = 0;
  for (const card of cards) {
    total += cardPoints(card);
    if (card.rank === 'A') aces += 1;
  }
  while (total > BLACKJACK && aces > 0) {
    total -= 10;
    aces -= 1;
  }
  return total;
}

export function isBlackjack(cards) {
  return cards.length === 2 && bestTotal(cards) === BLACKJACK;
}

const MESSAGES = {
  blackjack: (bet) => `Blackjack ! Vous gagnez ${Math.floor(bet * 1.5)} (payé 3:2).`,
  win: (bet) => `Gagné ! Vous remportez ${bet}.`,
  'dealer-bust': (bet) => `Le croupier dépasse 21. Vous remportez ${bet}.`,
  push: () => 'Égalité : la mise est remboursée.',
  lose: () => 'Perdu.',
  bust: () => 'Vous dépassez 21. Perdu.',
  'dealer-blackjack': () => 'Blackjack du croupier. Perdu.',
};

/**
 * Moteur de Blackjack (règles casino simplifiées, sans split) :
 * le croupier tire tant que son total est inférieur à 17 et reste sur tout 17.
 * Un blackjack naturel paie 3:2. Un paquet neuf (sans jokers) est rebattu à chaque manche.
 */
export class Blackjack {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.phase = 'betting'; // 'betting' | 'player-turn' | 'round-over'
    this.playerHand = [];
    this.dealerHand = [];
    this.message = '';
    this.result = null;
    this.deck = null;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  startRound(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) {
      return { ok: false, reason: 'bad-bet' };
    }

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;
    this.message = '';
    this.result = null;

    this.deck = new Deck({ jokers: 0 });
    this.deck.shuffle();
    this.playerHand = [this.deck.draw(1), this.deck.draw(1)];
    this.dealerHand = [this.deck.draw(1), this.deck.draw(1)];
    this.phase = 'player-turn';

    const playerBJ = isBlackjack(this.playerHand);
    const dealerBJ = isBlackjack(this.dealerHand);
    if (playerBJ || dealerBJ) {
      this.phase = 'round-over';
      if (playerBJ && dealerBJ) this._settle('push');
      else if (playerBJ) this._settle('blackjack');
      else this._settle('dealer-blackjack');
    }
    return { ok: true };
  }

  hit() {
    if (this.phase !== 'player-turn') return { ok: false, reason: 'wrong-phase' };
    this.playerHand.push(this.deck.draw(1));
    if (bestTotal(this.playerHand) > BLACKJACK) {
      this.phase = 'round-over';
      this._settle('bust');
    }
    return { ok: true };
  }

  stand() {
    if (this.phase !== 'player-turn') return { ok: false, reason: 'wrong-phase' };
    this._playDealerAndSettle();
    return { ok: true };
  }

  double() {
    if (this.phase !== 'player-turn') return { ok: false, reason: 'wrong-phase' };
    if (this.playerHand.length !== 2) return { ok: false, reason: 'too-late' };
    if (this.bet > this.bankroll) return { ok: false, reason: 'insufficient-funds' };

    this.bankroll -= this.bet;
    this.bet *= 2;
    this.playerHand.push(this.deck.draw(1));

    if (bestTotal(this.playerHand) > BLACKJACK) {
      this.phase = 'round-over';
      this._settle('bust');
    } else {
      this._playDealerAndSettle();
    }
    return { ok: true };
  }

  _playDealerAndSettle() {
    while (bestTotal(this.dealerHand) < DEALER_STAND_THRESHOLD) {
      this.dealerHand.push(this.deck.draw(1));
    }
    this.phase = 'round-over';

    const dealerTotal = bestTotal(this.dealerHand);
    const playerTotal = bestTotal(this.playerHand);
    if (dealerTotal > BLACKJACK) this._settle('dealer-bust');
    else if (playerTotal > dealerTotal) this._settle('win');
    else if (playerTotal < dealerTotal) this._settle('lose');
    else this._settle('push');
  }

  _settle(outcome) {
    this.result = outcome;
    if (outcome === 'blackjack') this.bankroll += this.bet + Math.floor(this.bet * 1.5);
    else if (outcome === 'win' || outcome === 'dealer-bust') this.bankroll += this.bet * 2;
    else if (outcome === 'push') this.bankroll += this.bet;
    // 'lose' / 'bust' / 'dealer-blackjack' : la mise déjà débitée est perdue.
    this.message = MESSAGES[outcome](this.bet);
  }

  /** Repasse en phase de mise pour la manche suivante (conserve le bankroll). */
  nextRound() {
    this.phase = 'betting';
    this.playerHand = [];
    this.dealerHand = [];
    this.bet = 0;
    this.message = '';
    this.result = null;
  }

  getState() {
    const dealerRevealed = this.phase !== 'player-turn';
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      message: this.message,
      result: this.result,
      playerHand: this.playerHand.map((card) => ({ card, hidden: false })),
      playerTotal: bestTotal(this.playerHand),
      dealerHand: this.dealerHand.map((card, i) => ({
        card,
        hidden: !dealerRevealed && i === 1,
      })),
      dealerTotal: dealerRevealed
        ? bestTotal(this.dealerHand)
        : (this.dealerHand.length ? bestTotal([this.dealerHand[0]]) : 0),
    };
  }
}
