// Roulette européenne (simple zéro, 37 cases : 0 à 36). Une seule mise
// active par lancer (comme la mise unique de Blackjack/Poker) - pas de
// tapis multi-mises simultanées, pour rester cohérent avec le reste du
// Casino et ne pas complexifier l'interface au-delà du nécessaire.

export const RED_NUMBERS = new Set([
  1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36,
]);

export function numberColor(n) {
  if (n === 0) return 'green';
  return RED_NUMBERS.has(n) ? 'red' : 'black';
}

/** Cotes (gain en plus de la mise rendue) par type de mise, format "X:1". */
export const ODDS = {
  straight: 35,
  red: 1,
  black: 1,
  even: 1,
  odd: 1,
  low: 1,
  high: 1,
  dozen1: 2,
  dozen2: 2,
  dozen3: 2,
};

export const BET_LABELS = {
  straight: 'Numéro plein',
  red: 'Rouge',
  black: 'Noir',
  even: 'Pair',
  odd: 'Impair',
  low: 'Manque (1-18)',
  high: 'Passe (19-36)',
  dozen1: '1ʳᵉ douzaine (1-12)',
  dozen2: '2ᵉ douzaine (13-24)',
  dozen3: '3ᵉ douzaine (25-36)',
};

/** Le zéro fait perdre toutes les mises extérieures (règle simplifiée,
 * sans "mise en prison" ni partage) - seul un numéro plein sur 0 gagne. */
export function isWinningBet(bet, winningNumber) {
  if (bet.kind === 'straight') return bet.number === winningNumber;
  if (winningNumber === 0) return false;

  switch (bet.kind) {
    case 'red': return numberColor(winningNumber) === 'red';
    case 'black': return numberColor(winningNumber) === 'black';
    case 'even': return winningNumber % 2 === 0;
    case 'odd': return winningNumber % 2 === 1;
    case 'low': return winningNumber >= 1 && winningNumber <= 18;
    case 'high': return winningNumber >= 19 && winningNumber <= 36;
    case 'dozen1': return winningNumber >= 1 && winningNumber <= 12;
    case 'dozen2': return winningNumber >= 13 && winningNumber <= 24;
    case 'dozen3': return winningNumber >= 25 && winningNumber <= 36;
    default: return false;
  }
}

/** Catégorise un gain pour le choix de la réplique de la croupière. */
export function winTier(kind, won) {
  if (!won) return 'none';
  if (kind === 'straight') return 'jackpot';
  if (kind === 'dozen1' || kind === 'dozen2' || kind === 'dozen3') return 'big';
  return 'small';
}

export class Roulette {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = null; // { kind, number?, amount }
    this.lastBet = null;
    this.phase = 'betting'; // 'betting' | 'result'
    this.winningNumber = null;
    this.won = false;
    this.payout = 0;
    this.history = [];
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  spin(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    const amount = bet && bet.amount;
    if (!bet || !bet.kind) return { ok: false, reason: 'no-bet-type' };
    if (bet.kind === 'straight' && !Number.isInteger(bet.number)) {
      return { ok: false, reason: 'no-number' };
    }
    if (!Number.isFinite(amount) || amount <= 0 || amount > this.bankroll) {
      return { ok: false, reason: 'bad-bet' };
    }

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= amount;

    this.winningNumber = Math.floor(Math.random() * 37);
    this.won = isWinningBet(bet, this.winningNumber);
    this.payout = this.won ? amount * (ODDS[bet.kind] + 1) : 0;
    this.bankroll += this.payout;

    this.history.unshift(this.winningNumber);
    this.history = this.history.slice(0, 8);

    this.phase = 'result';
    return { ok: true };
  }

  nextSpin() {
    this.phase = 'betting';
    this.winningNumber = null;
    this.won = false;
    this.payout = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      winningNumber: this.winningNumber,
      winningColor: this.winningNumber !== null ? numberColor(this.winningNumber) : null,
      won: this.won,
      payout: this.payout,
      winTier: this.phase === 'result' ? winTier(this.bet.kind, this.won) : 'none',
      history: this.history,
    };
  }
}
